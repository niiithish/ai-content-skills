#!/usr/bin/env python3
"""Swap insert stills on V2 for clips in place: same start and length, nothing else moves (the user's edit stays).
Usage: swap_insert_clips.py hook-1.fcproj [...] [--map OLD_NAME=NEW_PATH ...] (--map replaces the default list)"""
import json, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
TPS = 254016000000
SWAP = {"scene-220-v1.jpg": R / "clips/clip-220/clip-220-v1.mp4",
        "scene-221-v1.jpg": R.parent / "assets/clips/b-roll/problem-cellulite/backs-of-thighs-grey-shorts-hallway_v4-204.mp4",
        "scene-209-v2.jpg": R / "clips/clip-209/clip-209-v4.mp4"}

def cli(proj, cmds):
    f = proj.with_suffix(".cmds.jsonl"); f.write_text("\n".join(json.dumps(c) for c in cmds) + "\n")
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink(); rs = [json.loads(l) for l in out.stdout.splitlines() if l.strip()]
    bad = [r for r in rs if not r.get("ok")]
    if bad or not rs: sys.exit(f"{proj.name}: {bad or out.stderr}")
    return [r.get("result") for r in rs]

def seq(proj):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"],
                                     capture_output=True, text=True).stdout)

def probe(p):
    w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.split(",")
    return int(w), int(h)

maps = [a for a in sys.argv[1:] if "=" in a]
if maps:
    SWAP = {o: Path(n).resolve() for o, n in (m.split("=", 1) for m in maps)}
for a in [a for a in sys.argv[1:] if a.endswith(".fcproj")]:
    proj = Path(a).resolve(); s = seq(proj)
    def others(s):
        return sorted((t, c["name"], c["start"], c["end"]) for t, tr in enumerate(s["video"]) for c in tr["items"]
                      if c["name"] not in SWAP and Path(c["name"]).name not in {p.name for p in SWAP.values()})
    before = others(s)
    hit = [c for c in s["video"][1]["items"] if c["name"] in SWAP]
    paths = sorted({str(SWAP[c["name"]]) for c in hit})
    items = dict(zip(paths, cli(proj, [{"id": "file.import", "params": {"paths": paths}}, {"id": "file.save", "params": {}}])[0]["items"]))
    fps = s.get("fps") or 24
    cmds = [{"id": "edit.clear", "params": {"clips": [c["clip"] for c in hit]}}]
    for c in hit:
        cmds.append({"id": "timeline.place", "params": {"item": items[str(SWAP[c["name"]])], "track": "V2",
                     "time": c["start"], "duration": c["end"] - c["start"], "insert": False, "video": True, "audio": False}})
    res = cli(proj, cmds + [{"id": "file.save", "params": {}}])
    fx = []
    for c, r in zip(hit, res[1:-1]):
        w, h = probe(SWAP[c["name"]]); sc = round(max(1080 / w, 1920 / h) * 100, 2)
        if abs(sc - 100) > 0.3:
            fx.append({"id": "effects.setParam", "params": {"clip": r["clips"][0], "effect": "motion", "param": "scale", "value": sc}})
    cli(proj, fx + [{"id": "file.save", "params": {}}])
    s2 = seq(proj); after = others(s2)
    new = {c["name"]: (c["start"], c["end"]) for c in s2["video"][1]["items"]}
    for c in hit:
        nm = SWAP[c["name"]].name
        print(f"{proj.name}: {c['name']} -> {nm} {c['start']/TPS:.2f}-{c['end']/TPS:.2f}s",
              "same slot" if new.get(nm) == (c["start"], c["end"]) else f"MOVED {new.get(nm)}")
    print(f"{proj.name}: other clips unchanged: {before == after}")
