"""Builds edit/host-talking.fcproj (Jess: lines 2, 12, 18) and edit/guest-talking.fcproj (Nora: every other line, then
hooks 2 and 3), each the speaker's talking finals back to back on V1/A1, cut to the speech ranges in edit/ranges.json
(silence over 0.3 s squeezed, bad words cut). Frames at 24 fps. Refuses to overwrite an existing project."""
import json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent; EDIT = ROOT / "edit"
R = json.loads((EDIT / "ranges.json").read_text())
HOST = ["2", "12", "18"]
GUEST = [c for c in R if c not in HOST and not c.startswith("h")] + ["h2", "h3"]
FPS = 24

def cli(cmds, project=None, save_as=None):
    s = EDIT / ".fc-run.jsonl"; s.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    args = ["filmcraft-cli", "--compact"] + (["--project", str(project)] if project else []) + ["run", str(s)]
    if save_as: args += ["--save-as", str(save_as)]
    out = subprocess.run(args, capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode: sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    s.unlink(); return [r.get("result") for r in res]

for name, clips in [("host-talking", HOST), ("guest-talking", GUEST)]:
    proj = EDIT / f"{name}.fcproj"
    if proj.exists(): sys.exit(f"{proj.name} exists; move it away first")
    paths = [R[c]["path"] for c in clips]
    r = cli([{"id": "file.newProject", "params": {"name": name}},
             {"id": "file.import", "params": {"paths": paths}},
             {"id": "file.newSequence", "params": {"name": name, "width": 1080, "height": 1920, "fps": FPS, "video": 1, "audio": 1}}],
            save_as=proj)
    items = r[1]["items"]; cmds = []; cur = 0; log = []
    for c, item in zip(clips, items):
        for a, b in R[c]["keep"]:
            i0, i1 = round(a * FPS), round(b * FPS)
            cmds.append({"id": "timeline.place", "params": {"item": item, "track": "V1", "audioTrack": "A1", "frame": cur,
                         "insert": False, "sourceIn": {"frame": i0}, "duration": {"frame": i1 - i0}}})
            log.append([c, i0 / FPS, i1 / FPS, cur / FPS]); cur += i1 - i0
    cmds.append({"id": "file.save", "params": {}})
    cli(cmds, project=proj)
    (EDIT / f"{name}.cuts.json").write_text(json.dumps(log, indent=1))
    print(f"{proj.name}: {len(clips)} clips, {len(log)} pieces, {cur / FPS:.2f} s")
