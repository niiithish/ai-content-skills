#!/usr/bin/env python3
"""video-6 (2026-11-15, client Looms 1-2): swap V2 inserts in their slots. For each (start, end, file, from_s):
every V2 clip lying inside [start, end) is deleted and the new file is placed there, video only, from from_s,
scaled to fill 1080x1920. A split slot (start inside an existing clip) razors V2 first. Nothing else moves.
Usage: FC_HEADLESS=1 swap_inserts.py PROJECT start end file from_s [start end file from_s ...]"""
import json, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1])
F = 254016000000 // 24
CLI = ["filmcraft-cli", "--compact", "--project", str(PROJ)]
args = sys.argv[2:]
slots = [(int(args[i]), int(args[i + 1]), Path(args[i + 2]).resolve(), float(args[i + 3])) for i in range(0, len(args), 4)]


def seq():
    return json.loads(subprocess.run(CLI + ["inspect", "sequence"], capture_output=True, text=True, check=True).stdout)


def run(cmds, save=True):
    cmds = cmds + ([{"id": "file.save", "params": {}}] if save else [])
    out = subprocess.run(CLI + ["run", "-"], input="".join(json.dumps(c) + "\n" for c in cmds), capture_output=True,
                         text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {[r for r in res if not r.get('ok')]} {out.stderr[-1500:]}")
    return [r.get("result", r) for r in (res[:-1] if save else res)]


def size(p):
    w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip().split(",")[:2]
    return int(w), int(h)


s = seq()
before = {(k, c["clip"]): (c["startFrame"], c["endFrame"]) for k in ("video", "audio") for t in s[k] for c in t["items"]}
for a, b, p, src in slots:
    s = seq()
    V2 = s["video"][1]
    cuts = [x for x in (a, b) if any(c["startFrame"] < x < c["endFrame"] for c in V2["items"])]
    if cuts:
        run([{"id": "timeline.razor", "params": {"time": x * F, "track": V2["id"]}} for x in cuts])
        s = seq()
        V2 = s["video"][1]
    old = [c for c in V2["items"] if a <= c["startFrame"] and c["endFrame"] <= b]
    assert old and min(c["startFrame"] for c in old) == a and max(c["endFrame"] for c in old) == b, (a, b, old)
    item = run([{"id": "file.import", "params": {"paths": [str(p)]}}])[0]["items"][0]
    run([{"id": "timeline.delete", "params": {"clips": [c["clip"] for c in old], "ripple": False}},
         {"id": "timeline.place", "params": {"item": item, "track": V2["id"], "frame": a, "sourceIn": {"seconds": src},
                                             "duration": (b - a) * F, "insert": False, "video": True,
                                             "audio": False}}])
    s = seq()
    new = next(c for c in s["video"][1]["items"] if c["startFrame"] == a)
    w, h = size(p)
    sc = max(1080 / w, 1920 / h) * 100
    if abs(sc - 100) > 0.3:
        run([{"id": "effects.setParam", "params": {"clip": new["clip"], "effect": "motion", "param": "scale",
                                                    "value": round(sc, 2)}}])
    print(f"{a}-{b}: {[c['name'] for c in old]} -> {p.name} from {src} s (scale {sc:.0f})")
s = seq()
after = {(k, c["clip"]): (c["startFrame"], c["endFrame"]) for k in ("video", "audio") for t in s[k] for c in t["items"]}
moved = [k for k in before if k in after and before[k] != after[k]]
print("moved clips:", moved or "none", f"; {s['durationFrames']} f")
