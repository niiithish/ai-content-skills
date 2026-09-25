#!/usr/bin/env python3
"""One tool for an animated video project: Flow batches, review sheets, picks, rough cut, handoff.

Run from anywhere; it works on the video folder that contains this scripts/ folder.

  make.py status                       every shot: newest still, clip, final
  make.py stills [shots] [--dry-run]   generate stills in scenes/stills-batch.json
  make.py clips  [shots] [--dry-run]   generate 360p drafts in clips/clips-batch.json
  make.py finals [shots] [--into DIR] [--no-draft] [--dry-run]
                                       native 720p + 1080p upsample of each clip
  make.py pick 1a b [--clip]           keep variant b as the shot's version
  make.py review stills|clips|finals [shots]
                                       contact sheets in review/ (one image per page)
  make.py animatic                     edit/animatic.mp4: clips where they exist,
                                       stills elsewhere, over edit/voiceover.* if present
  make.py handoff                      edit/clips/01-....mp4 in story order for the editor
  make.py sync                         refresh scenes/all and clips/all

Shots are ids like 1a or 10b. Story order is the job order in scenes/stills-batch.json.

A manifest job may carry "variants": 2-4. Each variant is its own job with its own seed,
saved as scene-1a-v1-a.jpg, -b, ... until `pick` copies one to scene-1a-v1.jpg. Jobs whose
output already exists are skipped, so any command can be rerun after an interruption.

Settings come from ../project.conf (PRO_ACCOUNT, CONCURRENCY, RPM); PRO_ACCOUNT falls back
to $FLOW_PRO_ACCOUNT. Finals need it: Flow's 1080p upsample is free only on a paid account.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

VIDEO = Path(__file__).resolve().parent.parent
KINDS = {
    "stills": {"folder": "scenes", "stem": "scene", "manifest": "stills-batch.json", "ext": ".jpg"},
    "clips": {"folder": "clips", "stem": "clip", "manifest": "clips-batch.json", "ext": ".mp4"},
}
LETTERS = "abcd"
BASE_SEED = 12345
JOB_ID = re.compile(r"^(scene|clip)-(\d+[a-z]+)-v(\d+)$")
FONTS = [
    "/usr/share/fonts/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]
FONT = next((f for f in FONTS if Path(f).is_file()), None)


def die(msg):
    sys.exit(f"error: {msg}")


def conf():
    c = {"PRO_ACCOUNT": "", "CONCURRENCY": "3", "RPM": "6"}
    p = VIDEO / "project.conf"
    if p.is_file():
        for line in p.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                k, v = line.split("=", 1)
                c[k.strip()] = v.strip().strip("\"'")
    c["PRO_ACCOUNT"] = c["PRO_ACCOUNT"] or os.environ.get("FLOW_PRO_ACCOUNT", "")
    return c


# ---------- manifests ----------

def manifest_path(kind):
    return VIDEO / KINDS[kind]["folder"] / KINDS[kind]["manifest"]


def load_jobs(kind):
    path = manifest_path(kind)
    if not path.is_file():
        return []
    data = json.loads(path.read_text())
    jobs = data["jobs"] if isinstance(data, dict) else data
    for j in jobs:
        if not JOB_ID.match(j.get("id", "")):
            die(f"{path.name}: job id {j.get('id')!r} must look like scene-1a-v1 or clip-1a-v1")
        for key in ("prompt_file", "output"):
            j[key] = str((path.parent / j[key]).resolve())
        j["ingredient"] = [str((path.parent / p).resolve()) for p in j.get("ingredient", [])]
    return jobs


def shot(job):
    return JOB_ID.match(job["id"])[2]


def version(job):
    return int(JOB_ID.match(job["id"])[3])


def select(jobs, shots):
    if not shots:
        return jobs
    want = [s.lower() for s in shots]
    unknown = set(want) - {shot(j) for j in jobs}
    if unknown:
        die("no job for: " + ", ".join(sorted(unknown)))
    return [j for j in jobs if shot(j) in want]


def story_order():
    """Shot ids in story order: stills manifest first, then any clip-only shots."""
    order = []
    for kind in ("stills", "clips"):
        for j in load_jobs(kind):
            if shot(j) not in order:
                order.append(shot(j))
    return order


def variant_paths(out):
    return [out.with_name(f"{out.stem}-{x}{out.suffix}") for x in LETTERS]


def expand(jobs):
    """One flow job per variant; a shot that was already picked is not regenerated."""
    run = []
    for j in jobs:
        j = dict(j)
        n = int(j.pop("variants", 1))
        out = Path(j["output"])
        if n <= 1 or out.is_file():
            run.append(j)
            continue
        base = int(j.get("seed", BASE_SEED))
        for i, path in enumerate(variant_paths(out)[:n]):
            run.append({**j, "id": f"{j['id']}-{LETTERS[i]}", "output": str(path), "seed": base + 1000 * i})
    return run


def check_inputs(jobs):
    missing = sorted({p for j in jobs for p in [j["prompt_file"], *j["ingredient"]] if not Path(p).is_file()})
    if missing:
        die("missing files:\n  " + "\n  ".join(missing))


def run_batch(jobs, name, dry):
    c = conf()
    folder = VIDEO / ("scenes" if name == "stills" else "clips")
    run_file = folder / f".run-{name}.json"
    run_file.write_text(json.dumps({"jobs": jobs}, indent=2))
    logs = folder / ".logs"
    logs.mkdir(exist_ok=True)
    log = logs / f"{name}-{datetime.now():%Y%m%d-%H%M%S}.log"
    print(f"{len(jobs)} jobs · log {log}")
    cmd = ["flow", "batch", str(run_file), "--concurrency", c["CONCURRENCY"], "--rpm", c["RPM"], "--continue-on-error"]
    if dry:
        cmd.append("--dry-run")
    with open(log, "w") as fh:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            line = f"[{datetime.now():%H:%M:%S}] {line.rstrip()}"
            print(line, flush=True)
            fh.write(line + "\n")
        proc.wait()
    return proc.returncode


def report(paths):
    print("\nOn disk:")
    for p in paths:
        print(("  ok      " if Path(p).is_file() else "  MISSING ") + str(Path(p).relative_to(VIDEO)))


# ---------- all/ folders ----------

def sync(quiet=False):
    for kind, k in KINDS.items():
        root = VIDEO / k["folder"]
        if not manifest_path(kind).is_file():
            continue
        name = re.compile(rf"^{k['stem']}-(\d+[a-z]+)-v(\d+)(-1080p)?\{k['ext']}$")
        wanted = {shot(j) for j in load_jobs(kind)}
        all_dir = root / "all"
        all_dir.mkdir(exist_ok=True)
        latest = {}
        paths = list(root.glob(f"{k['stem']}-*/{k['stem']}-*/*")) + list(root.glob(f"{k['stem']}-*/{k['stem']}-*/final/*-1080p.mp4"))
        for p in paths:
            m = name.match(p.name)
            if not m or m[1] not in wanted:
                continue
            v = int(m[2])
            if m[1] not in latest or v > latest[m[1]][0]:
                latest[m[1]] = (v, [p])
            elif v == latest[m[1]][0]:
                latest[m[1]][1].append(p)
        keep = set()
        for _, files in latest.values():
            finals = [p for p in files if p.name.endswith("-1080p.mp4")]
            for p in finals or files:  # once a final exists, all/ holds only the final
                dest = all_dir / p.name
                keep.add(dest.name)
                if not dest.exists() or dest.stat().st_size != p.stat().st_size:
                    shutil.copy2(p, dest)
                    quiet or print(f"added   {k['folder']}/all/{dest.name}")
        for old in all_dir.iterdir():
            if name.match(old.name) and old.name not in keep:
                old.unlink()
                quiet or print(f"removed {k['folder']}/all/{old.name}")
        quiet or print(f"{k['folder']}/all: {len(latest)} shots")


def newest_in_all(kind, s):
    k = KINDS[kind]
    files = sorted((VIDEO / k["folder"] / "all").glob(f"{k['stem']}-{s}-v*{k['ext']}"))
    files = [f for f in files if re.match(rf"^{k['stem']}-{s}-v\d+(-1080p)?\{k['ext']}$", f.name)]
    finals = [f for f in files if f.name.endswith("-1080p.mp4")]
    return (finals or files or [None])[-1]


# ---------- commands ----------

def cmd_generate(kind, args):
    jobs = select(load_jobs(kind), args.shots)
    if not jobs:
        die(f"{manifest_path(kind).relative_to(VIDEO)} has no jobs")
    check_inputs(jobs)
    run = expand(jobs)
    run_batch(run, kind, args.dry_run)
    report([j["output"] for j in run])
    pending = [shot(j) for j in jobs if not Path(j["output"]).is_file() and any(p.is_file() for p in variant_paths(Path(j["output"])))]
    if pending:
        print(f"\nVariants waiting for a pick: {', '.join(pending)}  (make.py review {kind}, then make.py pick SHOT LETTER)")
    sync()


def cmd_finals(args):
    c = conf()
    finals = []
    for j in select(load_jobs("clips"), args.shots):
        draft = Path(j["output"])
        if not draft.is_file() and not args.no_draft:
            die(f"no draft for {j['id']}: {draft.relative_to(VIDEO)} (pick a variant, or pass --no-draft)")
        finals.append({
            "id": j["id"] + "-final", "kind": "video", "prompt_file": j["prompt_file"],
            "aspect": j.get("aspect", "9:16"), "duration": j.get("duration", 4),
            "resolution": "720p", "upsample": "1080p", "ingredient": j["ingredient"],
            "timeout": 1500, "no_rotate": True,
            "output": str(draft.parent / "final" / draft.name),
            **({"seed": j["seed"]} if "seed" in j else {}),
        })
    check_inputs(finals)
    print(f"{len(finals)} finals")
    previous = None
    if not args.dry_run:
        if not c["PRO_ACCOUNT"]:
            die("set PRO_ACCOUNT in project.conf (the paid Flow account that upsamples to 1080p for free)")
        try:
            previous = json.loads(subprocess.run(["flow", "accounts"], capture_output=True, text=True).stdout).get("active")
        except (ValueError, AttributeError):
            previous = None
        subprocess.run(["flow", "account", "use", c["PRO_ACCOUNT"]], check=True, stdout=subprocess.DEVNULL)
        print(f"Using {c['PRO_ACCOUNT']} for the 1080p upsample")
    try:
        run_batch(finals, "finals", args.dry_run)
    finally:
        if previous and previous != c["PRO_ACCOUNT"]:
            subprocess.run(["flow", "account", "use", previous], stdout=subprocess.DEVNULL)
            print(f"Active account restored to {previous}")
    hd = [Path(f["output"]).with_name(Path(f["output"]).stem + "-1080p.mp4") for f in finals]
    report(hd)
    sync()
    if args.into:
        dest = VIDEO / "clips" / args.into
        dest.mkdir(parents=True, exist_ok=True)
        for p in hd:
            if p.is_file():
                shutil.copy2(p, dest / p.name)
                print(f"copied  {p.name} -> clips/{args.into}/")
    print("\nFinals are new generations: run `make.py review finals` and compare them with the drafts.")


def cmd_pick(args):
    kind = "clips" if args.clip else "stills"
    jobs = [j for j in load_jobs(kind) if shot(j) == args.shot.lower()]
    if not jobs:
        die(f"no {kind} job for {args.shot}")
    out = Path(jobs[-1]["output"])
    src = out.with_name(f"{out.stem}-{args.letter.lower()}{out.suffix}")
    if not src.is_file():
        die(f"no variant {src.relative_to(VIDEO)}")
    shutil.copy2(src, out)
    print(f"{src.name} -> {out.name}")
    sync()


def ffprobe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def frame(video, t, dest):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(dest)],
                   check=True)
    return dest


def montage(tiles, cols, size, dest):
    """tiles: [(label, path)]; one labelled contact sheet."""
    cmd = ["magick", "montage", "-background", "#111114", "-fill", "#f4f4f5", "-pointsize", "22"]
    if FONT:
        cmd += ["-font", FONT]
    for label, path in tiles:
        cmd += ["-label", label, str(path)]
    cmd += ["-tile", f"{cols}x", "-geometry", f"{size}+10+10", str(dest)]
    subprocess.run(cmd, check=True)
    return dest


def cmd_review(args):
    kind = args.kind
    base = "clips" if kind == "finals" else kind
    jobs = select(load_jobs(base), args.shots)
    if not jobs:
        die("nothing to review")
    out_dir = VIDEO / "review"
    out_dir.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".frames-", dir=out_dir))
    stamp = f"{datetime.now():%Y%m%d-%H%M%S}"
    rows, missing = [], []  # each row: list of (label, path)
    for j in jobs:
        s, v = shot(j), version(j)
        out = Path(j["output"])
        if kind == "finals":
            hd = out.parent / "final" / f"{out.stem}-1080p.mp4"
            if not hd.is_file():
                missing.append(f"{s} v{v} final")
                continue
            row = []
            if out.is_file():
                row.append((f"{s} v{v} draft", frame(out, ffprobe_duration(out) / 2, tmp / f"{s}-d.jpg")))
            d = ffprobe_duration(hd)
            for name, t in (("start", 0.3), ("mid", d / 2), ("end", d - 0.3)):
                row.append((f"{s} final {name}", frame(hd, t, tmp / f"{s}-f-{name}.jpg")))
            rows.append(row)
            continue
        candidates = [(f"{s} v{v}", out)] if out.is_file() else [
            (f"{s} v{v} {p.stem[-1]}", p) for p in variant_paths(out) if p.is_file()]
        if not candidates:
            missing.append(f"{s} v{v}")
        for label, path in candidates:
            if kind == "stills":
                rows.append([(label, path)])
            else:
                d = ffprobe_duration(path)
                n = label.replace(" ", "-")
                rows.append([(f"{label} {name}", frame(path, t, tmp / f"{n}-{name}.jpg"))
                             for name, t in (("start", 0.3), ("mid", d / 2), ("end", max(d - 0.3, 0)))])
    sheets = []
    if kind == "stills":
        tiles = [t for row in rows for t in row]
        for i in range(0, len(tiles), 10):
            sheets.append(montage(tiles[i:i + 10], 5, "300x533", out_dir / f"stills-{stamp}-{i // 10 + 1}.jpg"))
    else:
        cols = 4 if kind == "finals" else 3
        for i in range(0, len(rows), 4):
            tiles = []
            for row in rows[i:i + 4]:
                if kind == "finals" and len(row) == 3:  # no draft on disk: pad so columns line up
                    blank = tmp / "blank.jpg"
                    if not blank.is_file():
                        subprocess.run(["magick", "-size", "240x427", "xc:#111114", str(blank)], check=True)
                    row = [("no draft", blank)] + row
                tiles += row
            sheets.append(montage(tiles, cols, "240x427", out_dir / f"{kind}-{stamp}-{i // 4 + 1}.jpg"))
    shutil.rmtree(tmp, ignore_errors=True)
    for p in sheets:
        print(p)
    if missing:
        print("not generated yet: " + ", ".join(missing))


def encode_segment(src, seconds, label, dest, still):
    vf = "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p"
    if FONT:
        vf += f",drawtext=fontfile='{FONT}':text='{label}':x=16:y=16:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=8"
    inp = ["-loop", "1", "-t", f"{seconds}", "-i", str(src)] if still else ["-i", str(src)]
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inp, "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", str(dest)],
                   check=True)


def cmd_animatic(args):
    clip_len = {shot(j): j.get("duration", 4) for j in load_jobs("clips")}
    edit = VIDEO / "edit"
    edit.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".animatic-", dir=edit))
    segs, total, lines = [], 0.0, []
    for s in story_order():
        clip, still = newest_in_all("clips", s), newest_in_all("stills", s)
        if clip:
            dur = ffprobe_duration(clip)
            src, is_still, what = clip, False, clip.name
        elif still:
            dur = float(clip_len.get(s, 4))
            src, is_still, what = still, True, still.name
        else:
            lines.append(f"  {s:>4}  (nothing yet, skipped)")
            continue
        seg = tmp / f"{len(segs):03d}.mp4"
        encode_segment(src, dur, s, seg, is_still)
        segs.append(seg)
        lines.append(f"  {s:>4}  {total:6.1f}s  {dur:4.1f}s  {what}")
        total += dur
    if not segs:
        die("no stills or clips yet")
    (tmp / "list.txt").write_text("".join(f"file '{p}'\n" for p in segs))
    vo = next((p for ext in ("wav", "mp3", "m4a", "aac") for p in [edit / f"voiceover.{ext}"] if p.is_file()), None)
    dest = edit / "animatic.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt")]
    cmd += ["-i", str(vo), "-map", "0:v", "-map", "1:a", "-c:a", "aac"] if vo else []
    subprocess.run(cmd + ["-c:v", "copy", str(dest)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n".join(lines))
    print(f"\n{dest}\npicture {total:.1f}s" + (f" · voiceover {ffprobe_duration(vo):.1f}s ({vo.name})" if vo else " · no edit/voiceover.* yet"))


def cmd_handoff(args):
    dest = VIDEO / "edit" / "clips"
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("[0-9][0-9]-*.mp4"):
        old.unlink()
    lines = []
    for s in story_order():
        clip = newest_in_all("clips", s)
        if not clip:
            lines.append(f"--  {s}: no clip")
            continue
        n = len([l for l in lines if not l.startswith("--")]) + 1
        name = f"{n:02d}-{clip.name}"
        shutil.copy2(clip, dest / name)
        lines.append(f"{name}  {ffprobe_duration(clip):.1f}s" + ("" if clip.name.endswith("-1080p.mp4") else "  (draft, no 1080p yet)"))
    (dest / "ORDER.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n{dest}")


def cmd_status(args):
    sync(quiet=True)
    stills = {shot(j): j for j in load_jobs("stills")}
    clips = {shot(j): j for j in load_jobs("clips")}
    print(f"{'shot':>5}  {'still':<22}{'clip':<22}final")
    for s in story_order():
        cells = []
        for jobs in (stills, clips):
            j = jobs.get(s)
            if not j:
                cells.append("-")
                continue
            out = Path(j["output"])
            if out.is_file():
                cells.append(f"v{version(j)}")
            elif any(p.is_file() for p in variant_paths(out)):
                cells.append(f"v{version(j)} pick {''.join(p.stem[-1] for p in variant_paths(out) if p.is_file())}")
            else:
                cells.append(f"v{version(j)} to make")
        j = clips.get(s)
        hd = j and Path(j["output"]).parent / "final" / f"{Path(j['output']).stem}-1080p.mp4"
        cells.append("1080p" if hd and hd.is_file() else "-")
        print(f"{s:>5}  {cells[0]:<22}{cells[1]:<22}{cells[2]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("stills", "clips"):
        p = sub.add_parser(name)
        p.add_argument("shots", nargs="*")
        p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("finals")
    p.add_argument("shots", nargs="*")
    p.add_argument("--into")
    p.add_argument("--no-draft", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("pick")
    p.add_argument("shot")
    p.add_argument("letter", choices=list(LETTERS))
    p.add_argument("--clip", action="store_true")
    p = sub.add_parser("review")
    p.add_argument("kind", choices=["stills", "clips", "finals"])
    p.add_argument("shots", nargs="*")
    for name in ("animatic", "handoff", "sync", "status"):
        sub.add_parser(name)
    args = ap.parse_args()
    {
        "stills": lambda: cmd_generate("stills", args),
        "clips": lambda: cmd_generate("clips", args),
        "finals": lambda: cmd_finals(args),
        "pick": lambda: cmd_pick(args),
        "review": lambda: cmd_review(args),
        "animatic": lambda: cmd_animatic(args),
        "handoff": lambda: cmd_handoff(args),
        "sync": lambda: sync(),
        "status": lambda: cmd_status(args),
    }[args.cmd]()


if __name__ == "__main__":
    main()
