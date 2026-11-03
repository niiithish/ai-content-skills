#!/usr/bin/env python3
"""Client Loom 10 (2026-10-31, brief/max_loom10.mp4), on hooks 1–3, in place (nothing moves in time):
- 0:20 the 🤯 must look like the iPhone one: the title's emoji PNG on V4 becomes the client's picture with its
  background removed (assets/emoji/exploding-head-iphone.png, from brief/max_att0.jpg), at the old one's height.
- 2:30 copy the winning ad's layout: the hook title sits up top so her body shows (box centre y TITLE_Y, measured
  on the ad at 0:00, 20% down), every caption after it low, where his screenshot has it (brief/max_att1.png,
  box centre 71% down = y CAPTION_Y). The emoji moves with the title.
Usage: loom10_layout.py hook-1.fcproj [...]"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path

TITLE_Y, CAPTION_Y = 380.0, 1360.0
EMOJI = Path(__file__).resolve().parents[1] / "assets/emoji/exploding-head-iphone.png"


def cli(proj, cmds):
    f = proj.with_suffix(".loom10.jsonl"); f.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink(); rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs):
        sys.exit(f"{proj.name}: {[r for r in rs if not r.get('ok')] or out.stderr[-1500:]}")


def tracks(proj):
    for it in json.load(open(proj))["project"]["items"].values():
        k = it.get("kind")
        if isinstance(k, dict) and "Sequence" in k:
            return k["Sequence"]["video_tracks"]


def p(c, effect, name):
    v = next(e for e in c["effects"] if e.get("effect") == effect)["params"][name]["value"]
    return next(iter(v.values()))


def ffsize(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return [int(x) for x in r.stdout.strip().split(",")[:2]]


for a in [a for a in sys.argv[1:] if a.endswith(".fcproj")]:
    proj = Path(a).resolve()
    bk = proj.parent / f"backup-{datetime.date.today()}-loom10"; bk.mkdir(exist_ok=True)
    if not (bk / proj.name).exists():
        shutil.copy2(proj, bk / proj.name)
    v = tracks(proj)
    caps = next(t["items"] for t in v if any(e.get("effect") == "graphic_text" for c in t["items"] for e in c["effects"]))
    title = min(caps, key=lambda c: c["start"])
    cmds, shift = [], 0.0
    for c in caps:
        my, ay, sy = p(c, "motion", "position")["y"], p(c, "motion", "anchor")["y"], p(c, "graphic_shape", "position")["y"]
        centre = sy + my - ay                      # where the box centre sits on screen now
        new = (TITLE_Y if c is title else CAPTION_Y) - centre + my
        if c is title:
            shift = new - my
        cmds.append({"id": "effects.setParam", "params": {"clip": c["id"], "effect": "motion", "param": "position",
                                                          "value": [p(c, "motion", "position")["x"], round(new, 1)]}})
    # the emoji: new picture, same height on screen, moved with the title
    emo = [c for t in v for c in t["items"] if "exploding-head" in c["name"]]
    for c in emo:
        pos, sc = p(c, "motion", "position"), p(c, "motion", "scale")
        cmds.append({"id": "effects.setParam", "params": {"clip": c["id"], "effect": "motion", "param": "position",
                                                          "value": [pos["x"], round(pos["y"] + shift, 1)]}})
    cli(proj, cmds)
    old_h = 184
    for c in emo:
        if c["name"] != EMOJI.name:
            sc = p(c, "motion", "scale")
            cli(proj, [{"id": "media.replaceFootage", "params": {"item": c["item"], "path": str(EMOJI)}},
                       {"id": "clip.rename", "params": {"clip": c["id"], "name": EMOJI.name}},
                       {"id": "effects.setParam", "params": {"clip": c["id"], "effect": "motion", "param": "scale",
                                                             "value": round(sc * old_h / ffsize(EMOJI)[1], 2)}}])
    print(f"{proj.name}: title to y {TITLE_Y:.0f} (shift {shift:+.0f}), {len(caps) - 1} captions to y {CAPTION_Y:.0f}, emoji {len(emo)} swapped")
