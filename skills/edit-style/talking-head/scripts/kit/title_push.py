#!/usr/bin/env python3
"""Push transition out of each hook's opening still onto her talking shot ("I'm 57."), as the reference does at 2.3 s
(user 2026-10-29: "after that first clip on top we add like a push transition to the clip she says I am 57").
FilmCraft's Push (Slide), from the east, 80% motion blur, 8 frames ending on the still's last frame, so the push lands
as the "I'm 57." caption starts. The still is on V2 over V1, so it can only end-align: the still slides out over her shot.
The title caption and its 🤯 (clips on the tracks above ending with the still) are trimmed to end as the push starts
(user 2026-10-29: "just before the start of the transition just hide the caption"; a push on them smears the text).
Replaces an existing transition there; rerun after make_hook.py and title_emoji.py. Usage: title_push.py hook-1.fcproj [...]"""
import json, subprocess, sys
from pathlib import Path

FRAMES, BLUR, FROM_EAST = 8, 80, 1


def cli(proj, cmds):
    f = proj.with_suffix(".push.jsonl"); f.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink(); rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs):
        sys.exit(f"{proj.name}: {rs or out.stderr[-1500:]}")


for a in [a for a in sys.argv[1:] if a.endswith(".fcproj")]:
    proj = Path(a).resolve()
    s = json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"],
                                  capture_output=True, text=True, check=True).stdout)
    v2 = s["video"][1]
    still = min(v2["items"], key=lambda c: c["startFrame"])
    if still["startFrame"] != 0:
        sys.exit(f"{proj.name}: no opening still on V2")
    end = still["endFrame"]
    over = [c for t in s["video"][2:] for c in t["items"] if c["endFrame"] == end and c["startFrame"] < end - FRAMES]
    old = [t["id"] for t in v2.get("transitions", []) if t.get("from") == end]
    cli(proj, ([{"id": "sequence.removeTransition", "params": {"transitions": old}}] if old else []) +
        [{"id": "sequence.applyVideoTransition", "params": {"clip": still["clip"], "effect": "push", "frames": FRAMES, "edge": "out",
                                                            "params": {"direction": FROM_EAST, "motion_blur": BLUR}}}] +
        [{"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": -FRAMES, "linked": False}} for c in over])
    print(f"{proj.name}: push out of {still['name']} frames {end - FRAMES}-{end}" + (f"; {', '.join(c['name'] for c in over)} end at {end - FRAMES}" if over else ""))
