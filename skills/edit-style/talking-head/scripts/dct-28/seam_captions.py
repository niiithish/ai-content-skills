#!/usr/bin/env python3
"""Moves every caption that starts inside a split shot (a listener clip on V2, name starting with --listener, default
'clip-listen') up onto the seam: motion position y 960 -> 506 (box centre 1413 -> 959 with template 1).
A caption build resets positions, so rerun this after every build.
Usage: seam_captions.py edit/hook-N.fcproj [--y 506] [--listener clip-listen]   (through fc.py run: live when the app
has the project open, else the file)"""
import json, subprocess, sys
from pathlib import Path


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


P = Path(sys.argv[1]).resolve()
Y, LISTEN = int(arg("--y", 506)), arg("--listener", "clip-listen")
d = json.load(open(P))


def find_seq(o):
    if isinstance(o, dict):
        if "video_tracks" in o:
            return o
        for v in o.values():
            r = find_seq(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_seq(v)
            if r:
                return r


vt = find_seq(d["project"])["video_tracks"]
splits = [(c["start"], c["start"] + c["duration"]) for t in vt[1:-1] for c in t["items"] if c["name"].startswith(LISTEN)]
caps = vt[-1]["items"]
ids = [c["id"] for c in caps if any(a <= c["start"] < b for a, b in splits)]
cmds = [{"id": "effects.setParam", "params": {"clip": i, "effect": "motion", "param": "position", "value": [540, Y]}}
        for i in ids]
f = P.parent / ".seam.jsonl"
f.write_text("".join(json.dumps(c) + "\n" for c in cmds))
# fc.py run goes through the live bridge when the app has the project open, else edits the file
r = subprocess.run([sys.executable, str(Path.home() / ".claude/skills/filmcraft/scripts/fc.py"), "run", str(P), str(f)],
                   capture_output=True, text=True)
f.unlink()
if r.returncode:
    sys.exit(f"failed: {r.stdout[-800:]} {r.stderr[-800:]}")
print(f"{len(ids)} captions in {len(splits)} split shots moved to y {Y}")
