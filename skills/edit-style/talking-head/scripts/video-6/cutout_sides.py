#!/usr/bin/env python3
"""video-6 (2026-11-14, user: "the cutout of that Korean woman is not the same in all places in the ref ... in few
places it's hidden, few places it changes place ... can you copy it"). The inspo keeps her cutout bottom-right on most
inserts, moves it bottom-left (same size, not mirrored) where the shot's subject sits on the right, and hides it on
product hero / line-up shots and the offer (as on its name cards). Here, per V2 insert (by its index on V2): LEFT moves
the V3 cutout over that insert to the left spot, HIDE removes it. The V3 cutout is razored on the insert's edges
(each a caption start or V1 cut, so no picture changes mid-caption). Headless when the app is closed, live otherwise.
Usage: cutout_sides.py [PROJECT]"""
import json, os, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / "hook-1.fcproj")
F = 254016000000 // 24
RIGHT = [991, 1423]          # build_hook1_full.py KEY: her face at x ~960, the inspo's right spot
LEFT = [301, 1423]           # inspo's left spot: face at x ~270 (measured on its 0:03 / 3:25 frames)
# V2 insert indices (inspect sequence order). Ours: picked from each insert's frame where her right-hand spot hides
# the subject (a person, legs, hands or a bottle on the right), in short runs like the inspo.
LEFT_IDX = [4, 5, 10, 20, 26, 33, 34, 36, 46, 47, 50, 58, 59, 65, 78, 80, 81, 90, 92, 93]
HIDE_IDX = [72, 98, 99]      # bottle hero "Now the one exception", CTA "Link is below", offer "Up to 65% off"

tok = Path("~/.config/filmcraft/control-token").expanduser().read_text().strip()
live = subprocess.run(["python3", os.path.expanduser("~/.claude/skills/filmcraft/scripts/fc.py"), "status"],
                      capture_output=True, text=True).stdout
LIVE = "bridge 127.0.0.1:9876: up" in live
os.environ["FILMCRAFT_CONTROL_TOKEN"] = tok
CLI = ["filmcraft-cli"] + (["--bridge", "127.0.0.1:9876"] if LIVE else ["--project", str(PROJ)]) + ["--compact"]


def seq():
    return json.loads(subprocess.run(CLI + ["inspect", "sequence"], capture_output=True, text=True, check=True).stdout)


def run(cmds):
    out = subprocess.run(CLI + ["run", "-"], capture_output=True, text=True,
                         input="".join(json.dumps(c) + "\n" for c in cmds))
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {[r for r in res if not r.get('ok')][:3]} {out.stderr[-1500:]}")


sp = lambda c: (c["startFrame"], c["startFrame"] + c["durationFrames"])
s = seq()
v2 = s["video"][1]["items"]
spans = {i: sp(v2[i]) for i in LEFT_IDX + HIDE_IDX}
for i, (a, b) in spans.items():
    print(f"{'LEFT' if i in LEFT_IDX else 'HIDE'} {i:3d} {a}-{b} {v2[i]['name']}")
# 1. razor V3 on every chosen insert's edges
cuts = sorted({x for a, b in spans.values() for x in (a, b)})
razor = [{"id": "timeline.razor", "params": {"time": x * F, "track": "V3"}}
         for x in cuts if any(sp(c)[0] < x < sp(c)[1] for c in s["video"][2]["items"])]
if razor:
    run(razor + [{"id": "file.save", "params": {}}])
s = seq()
v3 = s["video"][2]["items"]
inside = lambda c, a, b: a <= sp(c)[0] and sp(c)[1] <= b
left = [c for c in v3 for i in LEFT_IDX if inside(c, *spans[i])]
hide = [c for c in v3 for i in HIDE_IDX if inside(c, *spans[i])]
cmds = [{"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "position", "value": LEFT}}
        for c in left]
if hide:
    cmds.append({"id": "timeline.delete", "params": {"clips": [c["clip"] for c in hide], "ripple": False}})
cmds.append({"id": "file.save", "params": {}})
run(cmds)
print(f"cutout: {len(left)} pieces moved left, {len(hide)} hidden ({'live' if LIVE else 'headless'})")
