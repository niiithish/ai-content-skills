#!/usr/bin/env python3
"""FilmCraft helper: edits go to the live app when it has the project open, exports run from the saved file.

  fc.py status [PROJECT]                     app running? bridge up? which project, unsaved changes
  fc.py run PROJECT CMDS.jsonl               engine commands, one {"id","params"} per line: live in the app
                                             (then saved) when it has PROJECT open, else on the file
  fc.py swap PROJECT OLD NEW.mp4             replace a clip's media (OLD = file name, shot like 6a, or item id);
                                             every timeline use keeps its place, length and trim
  fc.py relink PROJECT [--folder DIR]        relink missing media from video-N/clips (searched recursively)
  fc.py export PROJECT... (-o OUT | -d DIR)  Meta 9:16 H.264, one at a time, from the saved files
           [--kbps 6000] [--no-captions] [--start S --end E]
"""
import argparse, json, os, re, socket, subprocess, sys, tempfile, time
from pathlib import Path

CLI = "filmcraft-cli"
PORT = int(os.environ.get("FILMCRAFT_CONTROL_PORT", 9876))
BRIDGE = f"127.0.0.1:{PORT}"
AUDIO = {"bitrate_kbps": 192, "bits": 16, "channels": 2, "codec": "aac", "flac_level": 5, "float": False,
         "sample_rate": 48000}
# Measured 2026-10-18 on the Iris Xe laptop, 10 s of 1080x1920: these settings 13 s / 7.6 MB; the old
# 40 Mb/s 2-pass max-render-quality ones 31 s / 50 MB. GPU rendering is on (it is off by default).
META = {"bitrateMode": "vbr1Pass", "gpuRendering": "auto", "h264Profile": "high", "audio": AUDIO}


def die(msg):
    sys.exit(f"fc.py: {msg}")


def app_running():
    return subprocess.run(["pgrep", "-x", "filmcraft"], capture_output=True).returncode == 0


def bridge_project():
    """(path, dirty) of the project the live app has active, or None when the bridge doesn't answer."""
    try:
        socket.create_connection(("127.0.0.1", PORT), timeout=1).close()
    except OSError:
        return None
    # the app can be slow to answer while it loads a project; never fall back to the file then
    for _ in range(3):
        try:
            out = subprocess.run([CLI, "--bridge", BRIDGE, "--compact", "inspect", "project"],
                                 capture_output=True, text=True, timeout=20)
            break
        except subprocess.TimeoutExpired:
            time.sleep(3)
    else:
        die(f"FilmCraft's bridge on {BRIDGE} isn't answering (still loading, or a dialog is open). "
            "Ask the user to check the app, then retry.")
    if out.returncode:
        die(f"FilmCraft's bridge on {BRIDGE} refused: {out.stderr.strip()[-200:]}")
    d = json.loads(out.stdout)
    return d.get("path"), d.get("dirty")


def mode(project):
    """'live' when the app has PROJECT open, 'file' when it's safe to edit the file directly."""
    project = str(Path(project).resolve())
    b = bridge_project()
    if b and b[0] and str(Path(b[0]).resolve()) == project:
        return "live"
    if app_running() and not b:
        die("FilmCraft is open without its control port, so its copy of the project would overwrite ours. "
            "Ask the user to save and quit, then reopen it from the launcher (it starts with --control).")
    return "file"


def run_cmds(project, cmds, save=True):
    m = mode(project)
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(json.dumps(c, ensure_ascii=False) for c in cmds) + "\n")
    args = [CLI, "--bridge", BRIDGE] if m == "live" else [CLI, "--project", str(project)] + (["--save"] if save else [])
    out = subprocess.run(args + ["--compact", "run", f.name], capture_output=True, text=True)
    os.unlink(f.name)
    lines = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [l for l in lines if not l.get("ok", True)]
    if out.returncode or bad:
        die(f"{m} run failed: rc={out.returncode} {bad[:2]} {out.stderr[-400:]}")
    if m == "live" and save:
        subprocess.run([CLI, "--bridge", BRIDGE, "--compact", "exec", "file.save"], check=True, capture_output=True)
    print(f"[{m}] {len(cmds)} command(s) ok" + (", saved" if save else ""))
    return lines


def inspect(project, what):
    m = mode(project)
    args = [CLI, "--bridge", BRIDGE] if m == "live" else [CLI, "--project", str(project)]
    out = subprocess.run(args + ["--compact", "inspect", what], capture_output=True, text=True)
    if out.returncode:
        die(f"inspect failed: {out.stderr[-300:]}")
    return json.loads(out.stdout)


def media_items(node):
    """Project items (clips, audio, stills) under the bins: {item, name, type, ...}."""
    for c in node.get("children", []):
        if "item" in c:
            yield c
        yield from media_items(c)


def cmd_status(a):
    b = bridge_project()
    print(f"app running: {app_running()}  bridge {BRIDGE}: {'up' if b else 'down'}")
    if b:
        print(f"live project: {b[0]}  unsaved changes: {b[1]}")
    if a.project:
        print(f"{a.project}: edits go {mode(a.project)}")


def cmd_run(a):
    cmds = [json.loads(l) for l in Path(a.cmds).read_text().splitlines() if l.strip() and not l.lstrip().startswith("#")]
    for l in run_cmds(a.project, cmds):
        print(json.dumps(l)[:300])


def cmd_swap(a):
    new = Path(a.new).resolve()
    if not new.exists():
        die(f"{new} doesn't exist")
    items = list(media_items(inspect(a.project, "project")["root"]))
    if re.fullmatch(r"\d+[a-z]?", a.old):  # a shot: clip-6a-v2-1080p.mp4 for 6a
        hit = [i for i in items if re.match(rf"clip-{re.escape(a.old)}-v\d+", i.get("name", ""))]
        if not hit and a.old.isdigit():
            hit = [i for i in items if i["item"] == int(a.old)]
    else:
        hit = [i for i in items if i.get("name") == a.old]
    if len(hit) != 1:
        die(f"{a.old!r} matches {len(hit)} items: {[i.get('name') for i in hit][:6]}")
    it = hit[0]
    run_cmds(a.project, [{"id": "media.replaceFootage", "params": {"item": it["item"], "path": str(new)}},
                         {"id": "clip.rename", "params": {"item": it["item"], "name": new.name}}])
    print(f"{it.get('name')} -> {new}")


def cmd_relink(a):
    p = Path(a.project).resolve()
    folder = Path(a.folder) if a.folder else p.parent.parent / "clips"
    r = run_cmds(a.project, [{"id": "media.autoRelink", "params": {"folder": str(folder.resolve())}}])
    print(json.dumps(r[-1].get("result", r[-1]))[:1500])


def has_caption_tracks(project):
    """True when any sequence in the saved project has a caption track with something on it."""
    def walk(n):
        if isinstance(n, dict):
            if n.get("caption_tracks"):
                return True
            return any(walk(v) for v in n.values())
        return isinstance(n, list) and any(walk(v) for v in n)
    try:
        return walk(json.loads(Path(project).read_text()))
    except (OSError, ValueError):
        return True  # unreadable here: burn rather than silently drop captions


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height",
                          "-of", "json", str(path)], capture_output=True, text=True)
    return json.loads(out.stdout or "{}")


def cmd_export(a):
    if bool(a.out) == bool(a.dir):
        die("give -o OUT for one project or -d DIR for several")
    if a.out and len(a.projects) > 1:
        die("-o takes one project; use -d DIR")
    b = bridge_project()
    for proj in a.projects:
        p = Path(proj).resolve()
        if b and b[0] and Path(b[0]).resolve() == p and b[1]:
            subprocess.run([CLI, "--bridge", BRIDGE, "--compact", "exec", "file.save"], check=True, capture_output=True)
            print(f"saved the user's open project first: {p.name}")
        elif app_running() and not b:
            print("note: FilmCraft is open without its bridge; exporting the last SAVED version of each project")
        out = Path(a.out) if a.out else Path(a.dir) / (p.stem + ".mp4")
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".tmp.mp4")
        settings = dict(META, bitrateKbps=a.kbps, maxBitrateKbps=int(a.kbps * 1.5))
        burn = has_caption_tracks(p) and not a.no_captions  # FilmCraft's default leaves caption tracks out
        params = {"path": str(tmp), "format": "h264", "settings": settings, "wait": True, "burnCaptions": burn}
        if a.start is not None:
            params.update(range="custom", startSeconds=a.start, endSeconds=a.end)
        t0 = time.time()
        r = subprocess.run(["nice", "-n", "10", CLI, "--project", str(p), "--compact", "exec", "file.exportMedia",
                            json.dumps(params)], capture_output=True, text=True)
        if r.returncode:
            tmp.unlink(missing_ok=True)
            die(f"{p.name}: export failed: {r.stdout[-400:]} {r.stderr[-400:]}")
        tmp.replace(out)
        info = probe(out)
        codecs = sorted(s["codec_name"] for s in info.get("streams", []))
        v = next((s for s in info.get("streams", []) if s["codec_type"] == "video"), {})
        dur = float(info.get("format", {}).get("duration", 0))
        mb = out.stat().st_size / 1e6
        ok = codecs == ["aac", "h264"]
        print(f"{'OK ' if ok else 'BAD'} {out}  {mb:.1f} MB  {dur:.1f} s  {v.get('width')}x{v.get('height')}  "
              f"{'+'.join(codecs)}  captions track: {'burned' if burn else 'none'}  ({time.time() - t0:.0f} s to export)")
        if not ok:
            die("expected H.264 video + AAC audio")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("project", nargs="?")
    r = sub.add_parser("run"); r.add_argument("project"); r.add_argument("cmds")
    w = sub.add_parser("swap"); w.add_argument("project"); w.add_argument("old"); w.add_argument("new")
    l = sub.add_parser("relink"); l.add_argument("project"); l.add_argument("--folder")
    e = sub.add_parser("export"); e.add_argument("projects", nargs="+")
    e.add_argument("-o", "--out"); e.add_argument("-d", "--dir")
    e.add_argument("--kbps", type=int, default=6000, help="video bitrate: 6000 ~ 45 MB/min, 4000 ~ 32 MB/min")
    e.add_argument("--no-captions", action="store_true",
                   help="leave caption tracks out (they are burned in by default; text-clip captions are always in the picture)")
    e.add_argument("--start", type=float); e.add_argument("--end", type=float)
    a = ap.parse_args()
    {"status": cmd_status, "run": cmd_run, "swap": cmd_swap, "relink": cmd_relink, "export": cmd_export}[a.cmd](a)


if __name__ == "__main__":
    main()
