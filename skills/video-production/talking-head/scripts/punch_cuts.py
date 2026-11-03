#!/usr/bin/env python3
"""Gives every talking-head jump cut a zoom change (client Loom, 2026-10-24: "hit a cut, and then upscale it for the jump
cut ... then it looks clean"): next to each cut, one side is at 100% and the other punched in to 108% on her face, the
pacing skill's calm punch-in. Clips with keyframed motion are left alone. Run after heal_cuts.py.
Usage: punch_cuts.py edit/hook-N.fcproj"""
import json, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1]).resolve()
LO, HI = 100.0, 108.0
s = json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "inspect", "sequence"],
                              capture_output=True, text=True, check=True).stdout)
W, H = s["settings"]["width"], s["settings"]["height"]
FY = round(0.4 * H)          # her face, as pace.py motion places it


def motion(c):
    p = next(e for e in c["effects"] if e["effect"] == "motion")["params"]
    return float(p["scale"]["value"].split("(")[1].rstrip(")")), bool(p["scale"]["keyframes"] or p["position"]["keyframes"])


cmds, prev = [], None
for c in sorted(s["video"][0]["items"], key=lambda c: c["startFrame"]):
    sc, keyed = motion(c)
    if not keyed and prev == sc:
        sc = HI if sc == LO else LO
        cmds += [{"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "position",
                                                        "value": [W / 2, round(FY - (FY - H / 2) * sc / 100)]}},
                 {"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "scale", "value": sc}}]
    prev = None if keyed else sc
print(f"{len(cmds) // 2} clips re-zoomed")
script = PROJ.parent / ".fc-punch.jsonl"
script.write_text("".join(json.dumps(x) + "\n" for x in cmds + [{"id": "file.save", "params": {}}]))
out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
script.unlink()
bad = [r for r in (json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")) if not r.get("ok")]
sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}" if bad or out.returncode else 0)
