#!/usr/bin/env python3
"""Write a build.py spec from a video folder's PLAN.md shot table.

Each shot N goes at its plan time, trimmed to its slot, from the newest clip-N-v*-1080p (else clip-N-v*) in
clips/resolve-prores/ (convert first with to-prores.sh). Hard cuts.

Usage:
  plan-spec.py VIDEO_DIR --timeline NAME [--vo FILE] [--music FILE] [--render-name NAME] > spec.json
"""
import argparse
import glob
import json
import os
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument("video_dir")
ap.add_argument("--timeline", required=True)
ap.add_argument("--vo")
ap.add_argument("--music")
ap.add_argument("--fps", type=float, default=24)
ap.add_argument("--render-name")
a = ap.parse_args()
v = os.path.abspath(a.video_dir)

shots = []
for line in open(os.path.join(v, "PLAN.md")):
    m = re.match(r"\|\s*(\d+)\s*\|\s*([\d.]+)\s*[–-]\s*([\d.]+)\s*s", line)
    if m:
        shots.append((int(m[1]), float(m[2]), float(m[3])))
if not shots:
    sys.exit("no shot table (| N | a – b s | ...) in PLAN.md")

ver = lambda p: int(re.search(r"-v(\d+)", p)[1]) if re.search(r"-v(\d+)", p) else 0
video, missing = [], []
for n, t0, t1 in shots:
    found = sorted(glob.glob(f"{v}/clips/resolve-prores/clip-{n}-v*-1080p.mov"), key=ver) \
        or sorted(glob.glob(f"{v}/clips/resolve-prores/clip-{n}-v*.mov"), key=ver)
    if not found:
        missing.append(n)
        continue
    video.append({"file": found[-1], "at": t0, "dur": round(t1 - t0, 4)})
if missing:
    sys.exit(f"no ProRes for shots {missing}: run to-prores.sh on clips/all first")

audio = []
if a.vo:
    audio.append({"file": os.path.abspath(a.vo), "at": 0, "track": 1})
if a.music:
    audio.append({"file": os.path.abspath(a.music), "at": 0, "track": 2 if a.vo else 1, "dur": "timeline"})
spec = {"timeline": a.timeline, "width": 1080, "height": 1920, "fps": a.fps, "video": video, "audio": audio}
if a.render_name:
    spec["render"] = {"dir": f"{v}/deliverables/raw", "name": a.render_name}
json.dump(spec, sys.stdout, indent=1)
print()
