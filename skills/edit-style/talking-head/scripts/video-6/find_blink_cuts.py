#!/usr/bin/env python3
"""List visible cutout cuts (V2 picture change, or her cutout appearing) whose first 2 frames show her eyes shut
(eye-band darkness under 70 % of the local median). Usage: find_blink_cuts.py PROJECT"""
import json, subprocess, sys
import numpy as np
P = sys.argv[1]; F = 10584000000
m = np.load("/tmp/claude-1000/-home-nithish-Work-upwork-upwork-max-video-6/f6d267e6-ab73-42a3-b3b3-691cc9d5082a/scratchpad/loomcheck/eye.npy")
s = json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", P, "inspect", "sequence"], capture_output=True, text=True).stdout)
v2s = {c["startFrame"] for c in s["video"][1]["items"]}
v3 = sorted([c for c in s["video"][2]["items"] if "hook1-body" in c["name"]], key=lambda c: c["startFrame"])
ends = {c["endFrame"] for c in s["video"][2]["items"]}
def src(c, f): return int(round(c["sourceIn"] / F + (f - c["startFrame"]) * c["speed"]))
bad = []
for c in v3:
    e = c["startFrame"]
    if not (e in v2s or e not in ends): continue
    for f in (e, e + 1):
        if f >= c["endFrame"]: continue
        i = src(c, f); med = np.median(m[max(0, i - 12): i + 12])
        if m[i] < 0.7 * med: bad.append((e, f, round(float(m[i] / med), 2))); break
print(P, len(bad), "blink cuts:", bad)
