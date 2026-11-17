#!/usr/bin/env python3
"""List visible cutout cuts (new V2 picture, or her cutout appearing) where her head jump inside the
green-screen file lands 1-2 frames AFTER the cut (Loom 8, 0:50). Usage: find_late_jumps.py PROJECT"""
import json, subprocess, sys
import numpy as np
P = sys.argv[1]; F = 10584000000; THR = 9.0
m = np.load("assets/cutout/drhan-greenscreen-hook1-body-1.242x-24p.mp4.motion.npy")
s = json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", P, "inspect", "sequence"], capture_output=True, text=True).stdout)
v2s = {c["startFrame"] for c in s["video"][1]["items"]}
ends = {c["endFrame"] for c in s["video"][2]["items"]}
for c in sorted([c for c in s["video"][2]["items"] if "hook1-body" in c["name"]], key=lambda c: c["startFrame"]):
    e = c["startFrame"]
    if not (e in v2s or e not in ends) or c["endFrame"] - e < 4: continue
    for k in (0, 1):
        i = int(round(c["sourceIn"] / F + k * c["speed"]))
        if m[i] > THR: print(f"{P}: cut {e} ({e//24//60}:{e//24%60:02d}:{e%24:02d}) clip {c['clip']}: jump {k+1} f late (motion {m[i]:.1f})"); break
