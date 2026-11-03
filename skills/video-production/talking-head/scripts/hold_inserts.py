#!/usr/bin/env python3
"""Holds every insert until the next one comes in (client Loom 3, 2026-10-25: an overlay that disappears while she is
still talking "isn't clean"). Each V2 still or V3 clip whose end leaves a gap before the next insert is trimmed out to
that next insert's start. A V3 clip can't play past its media: it is held as far as its media goes, and the rest of
the gap is reported. The last insert is left as it is. Usage: hold_inserts.py edit/hook-N.fcproj [--dry]"""
import json, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1]).resolve()
DRY = "--dry" in sys.argv


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


def run(cmds):
    script = PROJ.parent / ".fc-hold.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
    script.unlink()
    return all(json.loads(l).get("ok") for l in out.stdout.splitlines() if l.startswith("{")) and not out.returncode


s = fc("inspect", "sequence")
ins = sorted((c for t in (1, 2) for c in s["video"][t]["items"]), key=lambda c: c["startFrame"])
for a, b in zip(ins, ins[1:]):
    gap = b["startFrame"] - a["endFrame"]
    if gap <= 0:
        continue
    print(f"  hold {a['name'][:34]:34} {a['endFrame'] / 24:7.2f}s +{gap / 24:.2f}s")
    if DRY:
        continue
    held = gap
    while held and not run([{"id": "timeline.trim", "params": {"clip": a["clip"], "edge": "out", "mode": "regular", "deltaFrames": held}}]):
        held = held * 3 // 4 if held > 4 else held - 1
    if held < gap:
        print(f"       only +{held / 24:.2f}s (end of its media), {(gap - held) / 24:.2f}s still open")
