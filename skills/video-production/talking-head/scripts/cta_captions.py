#!/usr/bin/env python3
"""Moves the captions over one full-screen clip (the product-in-hand CTA) to the top of the frame, clear of the
product's label (Aleo video-3, user 2026-10-24). Rerun after every captions build.
Usage: cta_captions.py edit/hook-N.fcproj --clip clip-232
Every layer (both text lines and their template-6 boxes) moves up by the same amount: the bottom line's baseline
goes from y 1173 to 405, the top line's from 1098 to 330."""
import json, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1]).resolve()
CLIP = sys.argv[sys.argv.index("--clip") + 1]
DY = 405 - 1173


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


v = fc("inspect", "sequence")["video"]
cta = next(c for t in v[1:-1] for c in t["items"] if c["name"].startswith(CLIP))
cmds = []
for c in v[-1]["items"]:
    if c["endFrame"] <= cta["startFrame"] + 1:
        continue
    layers = fc("exec", "graphics.list", json.dumps({"clip": c["clip"]}))["layers"]
    if min(l["position"][1] for l in layers) < 900:
        continue   # already moved
    cmds += [{"id": "graphics.set", "params": {"clip": c["clip"], "layer": l["layer"],
                                               "props": {"position": [l["position"][0], l["position"][1] + DY]}}}
             for l in layers]
    print(f"{c['startFrame'] / 24:7.2f}s  {' / '.join(l['text'] for l in layers if l['kind'] == 'text')}")
script = PROJ.parent / ".fc-cta.jsonl"
script.write_text("".join(json.dumps(x) + "\n" for x in cmds + [{"id": "file.save", "params": {}}]))
out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
script.unlink()
bad = [r for r in (json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")) if not r.get("ok")]
sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}" if bad or out.returncode else 0)
