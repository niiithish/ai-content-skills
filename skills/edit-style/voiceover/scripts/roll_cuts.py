#!/usr/bin/env python3
"""Rolls every V1 cut that fc_captions.py plan reports off the voice onto it (user, 2026-11-02: "fix it on all"):
a cut a few frames before or after its phrase's first word, or one near a phrase start, moves to that word. A rolling
edit, so nothing else on the timeline moves. Where a clip has no media left past that edge it is slipped first, and a
clip sped up to play whole (4a) is slowed a little to reach the cut instead. Run plan first; rerun plan and build after. Run only while FilmCraft does
not have the project open (it writes the file headless)."""
import re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_hooks23 import EDIT, FPS, TPS, inspect, run

FC = Path.home() / ".claude/skills/captions-filmcraft/scripts/fc_captions.py"
CAP = EDIT.parent / "captions"


def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + float(s)


def fix(stem):
    proj = EDIT / f"{stem}.fcproj"
    out = subprocess.run([str(FC), "plan", str(proj), "--script", str(CAP / f"{stem}.script.txt"), "--max-words", "4"],
                         capture_output=True, text=True).stdout
    moves = []
    for l in out.splitlines():
        if m := re.match(r"NOTE cut at (\S+) is .*?\((?:nearest: .* at )?(\d+:[\d.]+)\)", l):
            moves.append((round(secs(m[1]) * FPS), round(secs(m[2]) * FPS)))
    v1 = sorted(inspect(proj)["video"][0]["items"], key=lambda c: c["startFrame"])
    cmds = []
    for cut, to in moves:
        left = next(c for c in v1 if c["endFrame"] == cut)
        right = next(c for c in v1 if c["startFrame"] == cut)
        d = to - cut
        if d > 0 and left["speed"] != 1:  # whole clip sped into its slot: shorten the next one, slow this one to meet it
            cmds += [{"id": "timeline.trim", "params": {"clip": right["clip"], "edge": "in", "mode": "regular", "deltaFrames": d}},
                     {"id": "clip.speedDuration", "params": {"clips": [left["clip"]], "ripple": False, "speed": round(
                         100 * (left["sourceOut"] - left["sourceIn"]) / TPS / ((to - left["startFrame"] + 0.5) / FPS), 2)}}]
        else:
            if d < 0 and right["sourceIn"] < -d * TPS // FPS:  # no media before the right clip's head: slip it later
                cmds.append({"id": "timeline.slip", "params": {"clip": right["clip"], "deltaFrames": -d}})
            if d > 0 and left["sourceIn"] >= d * TPS // FPS:  # slip the left clip earlier so it has d frames past its out
                cmds.append({"id": "timeline.slip", "params": {"clip": left["clip"], "deltaFrames": -d}})
            cmds.append({"id": "timeline.roll", "params": {"left": left["clip"], "right": right["clip"], "deltaFrames": d}})
        print(f"  {stem}: cut {cut / FPS:6.2f} -> {to / FPS:6.2f} s ({to - cut:+d} f)  {left['name']} | {right['name']}")
    if cmds:
        run(proj, cmds + [{"id": "file.save", "params": {}}])


if __name__ == "__main__":
    for stem in sys.argv[1:]:
        fix(stem)
