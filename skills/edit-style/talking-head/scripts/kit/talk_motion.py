#!/usr/bin/env python3
"""Zoom on the talking-only stretches (V1 with no insert over it), filmcraft-pacing calm style (user 2026-10-29:
"hard cut zoom in at few words, and slow zoom in and then hard cut back to same 100% scale").
Each stretch opens at 100% with a slow push (client Loom 7: no hard punch the moment an insert cuts back to her, no
sideways drift, so every move is a centred scale). Inside a stretch, every V1 cut and, in long runs, a caption start
about every 1.5–2.5 s is a mark; at each mark the scale steps hard between 100% and the punch (110%), and each segment
slow-pushes on (+3%). Every step lands on a caption start or V1 cut (Loom 7). Only V1 scale keyframes change; inserts,
captions and timing stay. Rerun-safe: deletes the V1 scale keyframes first. Usage: talk_motion.py hook-1.fcproj [...] [--dry]"""
import datetime, json, re, shutil, subprocess, sys
from pathlib import Path

TPS, FPS = 254016000000, 24
F = TPS // FPS
PUNCH, PUSH = 110.0, 3.0           # punch-in scale, slow push gained over a segment
MIN_SEG, LONG_SEG = 30, 60         # frames: shortest segment after a mark; split segments longer than this
EDGE = 18                          # no mark this close to a stretch's start or end


def seq(proj):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


def has_text(c):
    return any(e["effect"] == "graphic_text" for e in c["effects"])


def plan(s):
    v = s["video"]
    v1 = sorted(v[0]["items"], key=lambda c: c["startFrame"])
    end = v1[-1]["endFrame"]
    capt = next(t for t in reversed(v) if any(has_text(c) for c in t["items"]))
    caps = sorted({c["startFrame"] for c in capt["items"]})
    cover = [False] * end
    for t in v[1:]:
        if t is capt or not any(not has_text(c) for c in t["items"]):
            continue
        for c in t["items"]:
            if has_text(c) or c["endFrame"] - c["startFrame"] > 400 and c["startFrame"] < 5:   # skip overlays
                continue
            for f in range(c["startFrame"], min(c["endFrame"], end)):
                cover[f] = True
        break                                       # V2 inserts only; V4 holds the title emoji
    cuts = {c["startFrame"] for c in v1[1:]}
    runs, f = [], 0
    while f < end:
        if cover[f]:
            f += 1; continue
        g = f
        while g < end and not cover[g]:
            g += 1
        runs.append((f, g)); f = g
    segs = []                                       # (start, end, scale at start)
    for a, b in runs:
        marks = sorted(m for m in cuts if a < m < b)
        bounds = [a] + marks + [b]
        out = [bounds[0]]
        for x, y in zip(bounds, bounds[1:]):        # split long pieces at caption starts
            last = x
            for c in caps:
                if last + LONG_SEG <= y and c - last >= MIN_SEG and y - c >= MIN_SEG and c - a >= EDGE and b - c >= EDGE and c - last >= 36:
                    out.append(c); last = c
            out.append(y)
        out = sorted(set(out))
        for i, (x, y) in enumerate(zip(out, out[1:])):
            segs.append((x, y, 100.0 if i % 2 == 0 else PUNCH))
    return v1, segs


dry = "--dry" in sys.argv
for a in [a for a in sys.argv[1:] if a.endswith(".fcproj")]:
    proj = Path(a).resolve(); s = seq(proj)
    v1, segs = plan(s)
    cmds = []
    ids = {c["clip"] for c in v1}                  # clear old zooms: delete each V1 scale keyframe (media times from the file)
    for it in json.load(open(proj))["project"]["items"].values():
        for tr in (it.get("kind") or {}).get("Sequence", {}).get("video_tracks", [])[:1] if isinstance(it.get("kind"), dict) else []:
            for c in tr["items"]:
                if c["id"] in ids:
                    sc = c["effects"][0]["params"]["scale"]
                    cmds += [{"id": "effects.deleteKeyframe", "params": {"clip": c["id"], "effect": "motion", "param": "scale", "mediaTime": k["time"]}}
                             for k in sc.get("keyframes") or []]
    cmds += [{"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "scale", "value": 100.0}} for c in v1]
    for x, y, v0 in segs:
        clip = next(c for c in v1 if c["startFrame"] <= x < c["endFrame"])
        if y > clip["endFrame"]:
            sys.exit(f"{proj.name}: segment {x}-{y} runs past its V1 clip")
        for f, val in ((x, v0), (y - 1, v0 + PUSH * (y - x) / 72)):     # +3% per 3 s
            cmds.append({"id": "effects.setParam", "params": {"clip": clip["clip"], "effect": "motion", "param": "scale",
                                                              "value": round(val, 2), "keyframe": True, "time": f * F}})
    print(f"{proj.name}: " + ", ".join(f"{x}-{y} {v0:.0f}%" for x, y, v0 in segs))
    if dry:
        continue
    bk = proj.parent / f"backup-{datetime.date.today()}-talkmotion"; bk.mkdir(exist_ok=True)
    if not (bk / proj.name).exists():
        shutil.copy2(proj, bk / proj.name)
    f = proj.with_suffix(".motion.jsonl"); f.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink()
    rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs):
        sys.exit(f"{proj.name}: {[r for r in rs if not r.get('ok')] or out.stderr[-1500:]}")
