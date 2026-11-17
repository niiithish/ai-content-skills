#!/usr/bin/env python3
"""Loom 3 item 1 (0:12): the cutout no longer shows over her own full shot.
A copy of her V1 shot (clip 71, 259-296) goes on V2, and the light leak runs
from it into clip-207 over the 8 frames before the cut (align end), so at 296
the insert is fully up and the cutout appears with it. Usage: FC_HEADLESS=1 leak_296.py PROJECT"""
import json, subprocess, sys
F = 10584000000; P = sys.argv[1]
def cli(*a, inp=None):
    r = subprocess.run(["filmcraft-cli", "--compact", "--project", P, *a], input=inp, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr + r.stdout)
    return r.stdout
def run(cmds):
    out = cli("run", "-", inp="".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    res = [json.loads(l) for l in out.splitlines() if l.startswith("{")]
    if not all(r.get("ok") for r in res): sys.exit(f"failed {cmds}: {res}")
    return res
seq = lambda: json.loads(cli("inspect", "sequence"))
s = seq(); v1 = s["video"][0]; v2 = s["video"][1]
src = next(c for c in v1["items"] if c["startFrame"] == 259 and c["endFrame"] == 296)
ins = next(c for c in v2["items"] if c["startFrame"] == 296)
leak = [x for x in v2["transitions"] if x["to"] == ins["clip"] and x["effect"] == "light_leak"]
run([{"id": "sequence.removeTransition", "params": {"transitions": [x["id"] for x in leak]}},
     {"id": "timeline.move", "params": {"moves": [{"clip": src["clip"], "track": v2["id"], "time": {"frame": 259}}],
                                        "copy": True, "insert": False, "linked": False}}])
s = seq(); v2 = s["video"][1]
cp = next(c for c in v2["items"] if c["startFrame"] == 259 and c["endFrame"] == 296)
p = leak[0]["params"]
run([{"id": "sequence.applyVideoTransition", "params": {"clip": cp["clip"], "edge": "out", "effect": "light_leak",
      "frames": 8, "align": "end", "params": {"amount": 75.0, "color": p["color"]["Color"], "seed": 1.0}}}])
s = seq()
for c in s["video"][1]["items"]:
    if 250 <= c["startFrame"] <= 300: print(c["clip"], c["startFrame"], c["endFrame"], c["name"])
for x in s["video"][1]["transitions"]:
    if abs(x["start"] / F - 292) < 10: print(x)
