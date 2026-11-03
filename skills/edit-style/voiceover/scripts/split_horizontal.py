#!/usr/bin/env python3
"""Turns the 9d/9e split in edit/hook-1-v2.fcproj from side by side into top and bottom (user, 2026-11-02): each clip loses
25% top and bottom instead of left and right, 9d moves to the top half, 9e to the bottom. Run only while FilmCraft does not
have the project open (it writes the file headless)."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_hook1_v2 import cli, seq

Y = {"9d": 480, "9e": 1440}


def split():
    found = {}
    for t in seq()["video"]:
        for c in t["items"]:
            for s in Y:
                if f"clip-{s}-" in json.dumps(c):
                    found[s] = c["clip"]
    if set(found) != set(Y):
        sys.exit(f"9d/9e not both on the timeline: {found}")
    cmds = []
    for s, c in found.items():
        cmds += [{"id": "effects.setParam", "params": {"clip": c, "effect": "crop", "param": p, "value": v}}
                 for p, v in (("left", 0), ("right", 0), ("top", 25), ("bottom", 25))]
        cmds.append({"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "position", "value": [540, Y[s]]}})
    cli(cmds + [{"id": "file.save", "params": {}}])
    print("9d top, 9e bottom: crop top/bottom 25%")


if __name__ == "__main__":
    split()
