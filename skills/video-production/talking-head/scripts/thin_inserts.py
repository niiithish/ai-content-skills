#!/usr/bin/env python3
"""Brings the box-still pace down to the reference video's (user, 2026-10-24: "you have spammed the scene inserts
too much"). Measured on the reference: a new insert every 3.4 s, most held 2-5 s, the doctor clean about 20% of the
time. Ours had one every 2.6 s, 15-18 of them under 1.5 s, the doctor clean 11-14%.
Drops the box stills (V2) with the shortest on-screen time until the hook has at most one insert per PACE seconds.
A dropped still leaves the doctor clean while the hook is under CLEAN, else the still before it (when it touches)
holds on instead. Full-screen clips (V3) always stay. Every edge stays on a caption start or cut, so
fc_inserts.py check still passes. Usage: thin_inserts.py edit/hook-N.fcproj [--dry]"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path

PACE, CLEAN = 3.4, 0.20
PROJ = Path(sys.argv[1]).resolve()
DRY = "--dry" in sys.argv


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


v = fc("inspect", "sequence")["video"]
end = max(c["endFrame"] for c in v[0]["items"])
v2 = sorted(v[1]["items"], key=lambda c: c["startFrame"])
v3 = v[2]["items"]
fps = 24


def visible(c):   # frames of a V2 still not hidden by a V3 clip
    return sum(1 for f in range(c["startFrame"], min(c["endFrame"], end))
               if not any(x["startFrame"] <= f < x["endFrame"] for x in v3))


def clean_frames(stills):
    cov = [False] * end
    for c in list(stills) + v3:
        for f in range(c["startFrame"], min(c["endFrame"], end)):
            cov[f] = True
    return cov.count(False)


keep = {c["clip"]: dict(c, E=c["endFrame"]) for c in v2 if visible(c) > 0}
target = int(end / fps / PACE) - len(v3)
drops, holds = [], []
while len(keep) > target:
    c = min(keep.values(), key=lambda c: visible(dict(c, endFrame=c["E"])))
    del keep[c["clip"]]
    prev = next((p for p in keep.values() if p["E"] == c["startFrame"]), None)
    if prev and clean_frames([dict(k, endFrame=k["E"]) for k in keep.values()]) / end > CLEAN:
        prev["E"] = c["E"]
        holds.append((prev, c))
    drops.append(c)
hidden = [c for c in v2 if visible(c) == 0]
for c in sorted(drops, key=lambda c: c["startFrame"]):
    print(f"  drop {c['name'][:34]:34} {c['startFrame'] / fps:7.2f}-{c['endFrame'] / fps:6.2f}s")
for p, c in holds:
    print(f"  hold {p['name'][:34]:34} on to {c['endFrame'] / fps:7.2f}s")
stills = [dict(k, endFrame=k["E"]) for k in keep.values()]
print(f"{len(v2) - len(hidden)} box stills -> {len(stills)}, + {len(v3)} full-screen: one insert every "
      f"{end / fps / (len(stills) + len(v3)):.1f}s, doctor clean {100 * clean_frames(stills) / end:.0f}%")
if DRY:
    sys.exit()
bk = PROJ.parent / f"backup-{datetime.date.today()}-thin"
bk.mkdir(exist_ok=True)
if not (bk / PROJ.name).exists():
    shutil.copy2(PROJ, bk / PROJ.name)
cmds = [{"id": "edit.clear", "params": {"clips": [c["clip"] for c in drops]}}]
cmds += [{"id": "timeline.trim", "params": {"clip": k["clip"], "edge": "out", "mode": "regular",
                                            "deltaFrames": k["E"] - k["endFrame"]}} for k in keep.values() if k["E"] != k["endFrame"]]
script = PROJ.parent / ".fc-thin.jsonl"
script.write_text("".join(json.dumps(x) + "\n" for x in cmds + [{"id": "file.save", "params": {}}]))
out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
script.unlink()
bad = [r for r in (json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")) if not r.get("ok")]
sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}" if bad or out.returncode else 0)
