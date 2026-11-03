#!/usr/bin/env python3
"""Replaces one insert with new media in the same slot (same start and end frames): a box still on V2 (fitted to the
720x500 box under her face, as build_inserts.py does), or with --full a full-screen clip on V3. The old clip is removed.
Usage: replace_insert.py edit/hook-N.fcproj OLD_NAME_PREFIX NEW_PATH [--full]"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image

TPS = 254016000000
BOX_W, BOX_H, BOX_CX, BOX_CY = 720, 500, 540, 1490
PROJ, OLD, NEW = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve()
FULL = "--full" in sys.argv


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


def run(cmds):
    script = PROJ.parent / ".fc-replace.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
    script.unlink()
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {out.stdout[-1500:]}{out.stderr[-1500:]}")
    return [r.get("result") for r in res]


def walk(n):
    for c in n.get("children", []):
        yield c
        yield from walk(c)


s = fc("inspect", "sequence")
old = [c for t in (1, 2) for c in s["video"][t]["items"] if c["name"].startswith(OLD)]
if len(old) != 1:
    sys.exit(f"{PROJ.name}: {len(old)} clips named {OLD}*")
old = old[0]
item = next((c["item"] for c in walk(fc("inspect", "project")["root"]) if c["name"] == NEW.name), None)
if item is None:
    item = run([{"id": "file.import", "params": {"paths": [str(NEW)]}}])[0]["items"][0]
run([{"id": "edit.clear", "params": {"clips": [old["clip"]]}}])
clip = run([{"id": "timeline.place", "params": {"item": item, "track": "V3" if FULL else "V2", "seconds": old["startFrame"] / 24,
                                                "duration": (old["endFrame"] - old["startFrame"]) * TPS // 24,
                                                "insert": False, "video": True, "audio": False}}])[0]["clips"][0]
if not FULL:
    w, h = Image.open(NEW).size
    run([{"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale", "value": round(min(BOX_W / w, BOX_H / h) * 100, 2)}},
         {"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "position", "value": [BOX_CX, BOX_CY]}}])
print(f"{PROJ.stem}: {old['name']} -> {NEW.name} ({'V3' if FULL else 'V2'}) {old['startFrame'] / 24:.2f}-{old['endFrame'] / 24:.2f}s")
