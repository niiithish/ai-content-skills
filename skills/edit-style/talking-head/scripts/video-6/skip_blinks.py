#!/usr/bin/env python3
"""Start cutout pieces after a blink that falls on a picture change (user 2026-11-17 check of Max's Loom 6 item 3: at 1:43
her eyes were shut on the cut). Each piece skips its first K source frames (the blink) and plays a little slower,
(L-K)/L, so it still ends on its own frame in sync. Timeline positions unchanged.
Usage: skip_blinks.py PROJECT clip:K [clip:K ...]"""
import json, subprocess, sys
P = sys.argv[1]; F = 10584000000; CLI = ["filmcraft-cli", "--compact", "--project", P]
seq = lambda: json.loads(subprocess.run(CLI + ["inspect", "sequence"], capture_output=True, text=True, check=True).stdout)
for a in sys.argv[2:]:
    cid, k = map(int, a.split(":"))
    c = next(c for c in seq()["video"][2]["items"] if c["clip"] == cid); L = c["endFrame"] - c["startFrame"]
    cmds = [{"id": "clip.speedDuration", "params": {"clips": [cid], "speed": round((L - k) / L * 100 * c["speed"], 4), "ripple": False}},
            {"id": "timeline.slip", "params": {"clip": cid, "delta": k * F}}, {"id": "file.save", "params": {}}]
    o = subprocess.run(CLI + ["run", "-"], input="".join(json.dumps(x) + "\n" for x in cmds), capture_output=True, text=True)
    if '"ok":false' in o.stdout: sys.exit(o.stdout)
    n = next(x for x in seq()["video"][2]["items"] if x["clip"] == cid)
    d = c["endFrame"] - n["endFrame"]  # speedDuration changes the length; put the end back
    if d:
        subprocess.run(CLI + ["run", "-"], input=json.dumps({"id": "timeline.trim", "params": {"clip": cid, "edge": "out", "mode": "regular", "delta": d * F, "linked": False}}) + "\n" + json.dumps({"id": "file.save", "params": {}}) + "\n", capture_output=True, text=True, check=True)
        n = next(x for x in seq()["video"][2]["items"] if x["clip"] == cid)
    assert (n["startFrame"], n["endFrame"]) == (c["startFrame"], c["endFrame"]) and abs(n["sourceOut"] - c["sourceOut"]) < F / 2 and abs(n["sourceIn"] - c["sourceIn"] - k * F) < F / 2, (c, n)
    print(f"{cid} {c['startFrame']}-{c['endFrame']}: skips {k} f, speed {n['speed']:.3f}")
