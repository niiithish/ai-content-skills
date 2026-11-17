#!/usr/bin/env python3
"""video-6 (2026-11-13, user: "at the starting where we switch from the talking head normal to the clip and
transparent talking head b roll there is a push in blur kind of transition which i want to copy"): the inspo's first
switch (2.1 s) smears her plain shot for about 3 frames and lands the insert + cutout blurred for 2 (30 fps).
Copy (user, same day: "it should happen between two clips, not the end of clip 1"): a copy of her shot (from the caption start
before) goes on V2 right before the insert, so V2 has a real cut there, and FilmCraft zoom_blur runs 8 frames centred on it (her
shot blurs out, the insert blurs in); the V3 cutout gets 2 frames of zoom_blur in. Earlier transitions there are
removed first (the first version blurred V1 only, and the insert came in sharp after it).
Run after build_hook1_full.py and talk_motion.py. Usage: push_blur.py [PROJECT]"""
import json, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / "hook-1.fcproj")
TPS, FPS = 254016000000, 24
F = TPS // FPS


def seq():
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


def run(cmds):
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", "-"], capture_output=True, text=True,
                         input="".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {res} {out.stderr[-1500:]}")


s = seq()
at = min(c["startFrame"] for c in s["video"][1]["items"] if c["name"] != s["video"][0]["items"][0]["name"])
old = [t["id"] for k in (0, 1, 2) for t in s["video"][k]["transitions"]
       if t["effect"] == "zoom_blur" and abs(t["start"] / F - at) < 10]
if old:
    run([{"id": "sequence.removeTransition", "params": {"transitions": old}}])
    s = seq()
v2 = s["video"][1]["items"]
pad = [c for c in v2 if c["startFrame"] + c["durationFrames"] == at and c["name"].startswith("clip-") and "voice" in c["name"]]
if not pad:
    # the copy starts on a caption start (fc_inserts check counts it as a picture change), at least 8 frames back
    caps = json.load(open(PROJ.parent.parent / "captions" / f"{PROJ.stem}.captions.json"))["blocks"]
    a = max(c["start"] for c in caps if c["start"] <= at - 8)
    her = [c for c in s["video"][0]["items"] if c["startFrame"] <= a < c["startFrame"] + c["durationFrames"]][0]
    assert her["startFrame"] + her["durationFrames"] >= at, "her shot cuts between the caption start and the switch"
    run([{"id": "timeline.place", "params": {"item": her["item"], "track": "V2", "frame": a,
                                             "sourceIn": her["sourceIn"] + (a - her["startFrame"]) * F,
                                             "duration": (at - a) * F, "insert": False, "video": True, "audio": False}}])
    s = seq()
    pad = [c for c in s["video"][1]["items"] if c["startFrame"] + c["durationFrames"] == at]
ins = [c for c in s["video"][2]["items"] if c["startFrame"] == at]
assert len(pad) == 1 and len(ins) == 1, (pad, ins)
run([{"id": "sequence.applyVideoTransition", "params": {"clip": pad[0]["clip"], "effect": "zoom_blur", "frames": 8,
                                                         "edge": "out", "align": "center"}},
     {"id": "sequence.applyVideoTransition", "params": {"clip": ins[0]["clip"], "effect": "zoom_blur", "frames": 2,
                                                         "edge": "in", "align": "start"}}])
print(f"push-in blur centred on frame {at} ({at / FPS:.2f} s): her copy on V2 -> insert, 8 f; cutout 2 f in")
