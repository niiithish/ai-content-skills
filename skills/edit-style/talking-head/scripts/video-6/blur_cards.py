#!/usr/bin/env python3
"""video-6 (2026-11-14, user: "this fast whoosh sound effect transitions, instead of that can we have that blur push in
for all?"): the 7 whoosh pushes (6 name cards + "Aleo has eucalyptus") become the push-in blur of the first insert
(push_blur.py): FilmCraft zoom_blur, 8 frames centred on the V2 cut. Live through the bridge (FC_HEADLESS=1: file).
  - V2: push removed; zoom_blur 8 f centred on the cut. The 3-frame her-copy before 571 grows 2 frames at its head
    (566, over her own V1 shot, so nothing changes on screen) so the blur has 4 frames before the cut.
  - V4 cards: start back on the cut (they started 3 f early to push in with the picture) and blur in over 4 frames.
  - V3 cutout: the slide-out keyframes come off (static at her spot); she blurs out over the last 4 frames before a card.
    At 4346, where she runs on, V3 gets the same 8 f centred blur as V2.
  - The 7 captions that end 3 f before the cut now end 4 f before it, as the blur starts (user's earlier rule).
  - SFX (ours: "instead of that" read as the sound too): each Fast Woosh 03 becomes the first insert's Cartoon Swipe,
    -2 dB, 5 frames before the cut.
Nothing else moves."""
import json, os, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / "hook-1.fcproj")
TPS, FPS = 254016000000, 24
F = TPS // FPS
CUTS = (571, 1069, 1551, 2103, 2701, 3150, 4346)
HEADLESS = bool(os.environ.get("FC_HEADLESS"))
if HEADLESS:
    CLI = ["filmcraft-cli", "--compact", "--project", str(PROJ)]
else:
    os.environ["FILMCRAFT_CONTROL_TOKEN"] = Path("~/.config/filmcraft/control-token").expanduser().read_text().strip()
    CLI = ["filmcraft-cli", "--bridge", "127.0.0.1:9876", "--compact"]


def seq():
    return json.loads(subprocess.run(CLI + ["inspect", "sequence"], capture_output=True, text=True, check=True).stdout)


def run(cmds):
    cmds = cmds + [{"id": "file.save", "params": {}}]
    out = subprocess.run(CLI + ["run", "-"], input="".join(json.dumps(c) + "\n" for c in cmds), capture_output=True,
                         text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {[r for r in res if not r.get('ok')]} {out.stderr[-1500:]}")
    return res[:-1]


s = seq()
V2, V3, V4, V5 = (s["video"][k] for k in (1, 2, 3, 4))
SFX = s["audio"][3]
before = {(k, c["clip"]): (c["startFrame"], c["endFrame"]) for k in ("video", "audio") for t in s[k] for c in t["items"]}

# 1) drop the pushes
push = [t["id"] for tr in (V2, V3, V4) for t in tr["transitions"] if t["effect"] == "push"]
assert len(push) == 14, len(push)
cmds = [{"id": "sequence.removeTransition", "params": {"transitions": push}}]

# 2) clip edges
pad = next(c for c in V2["items"] if c["endFrame"] == 571 and c["durationFrames"] == 3)
assert not any(c["startFrame"] < 568 and c["endFrame"] > 564 for c in V2["items"] if c is not pad)
cmds.append({"id": "timeline.trim", "params": {"clip": pad["clip"], "edge": "in", "mode": "regular", "deltaFrames": -2,
                                               "linked": False}})
cards = [c for c in V4["items"] if c["startFrame"] + 3 in CUTS]
assert len(cards) == 6, cards
cmds += [{"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "in", "mode": "regular", "deltaFrames": 3,
                                            "linked": False}} for c in cards]
caps = [c for c in V5["items"] if c["endFrame"] + 3 in CUTS]
assert len(caps) == 7, [c["name"] for c in caps]
cmds += [{"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": -1,
                                            "linked": False}} for c in caps]
# cutout: static again
outs = [c for c in V3["items"] if c["endFrame"] in CUTS[1:6]]
assert len(outs) == 5
for c in outs:
    cmds += [{"id": "effects.toggleAnimation", "params": {"clip": c["clip"], "effect": "motion", "param": "position"}},
             {"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "position",
                                                   "value": [991.0, 1423.0]}}]
run(cmds)

# 3) blurs
s = seq()
V2, V3, V4 = (s["video"][k] for k in (1, 2, 3))
cmds = []
for at in CUTS:
    o = next(c for c in V2["items"] if c["endFrame"] == at)
    cmds.append({"id": "sequence.applyVideoTransition", "params": {"clip": o["clip"], "effect": "zoom_blur", "frames": 8,
                                                                   "edge": "out", "align": "center"}})
for c in V4["items"]:
    if c["startFrame"] in CUTS:
        cmds.append({"id": "sequence.applyVideoTransition", "params": {"clip": c["clip"], "effect": "zoom_blur",
                                                                       "frames": 4, "edge": "in", "align": "start"}})
for c in V3["items"]:
    if c["endFrame"] in CUTS[1:6]:
        cmds.append({"id": "sequence.applyVideoTransition", "params": {"clip": c["clip"], "effect": "zoom_blur",
                                                                       "frames": 4, "edge": "out", "align": "end"}})
    if c["endFrame"] == 4346:
        cmds.append({"id": "sequence.applyVideoTransition", "params": {"clip": c["clip"], "effect": "zoom_blur",
                                                                       "frames": 8, "edge": "out", "align": "center"}})
run(cmds)

# 4) SFX: whoosh -> swipe
woosh = [c for c in SFX["items"] if c["name"] == "Fast Woosh 03.mp3"]
swipe = next(c for c in SFX["items"] if c["name"] == "Cartoon Swipe.mp3")
assert len(woosh) == 7
run([{"id": "timeline.delete", "params": {"clips": [c["clip"] for c in woosh], "ripple": False}}])
res = run([{"id": "timeline.place", "params": {"item": swipe["item"], "track": SFX["id"], "frame": at - 5,
                                               "insert": False, "video": False, "audio": True}} for at in CUTS])
run([{"id": "clip.audioGain", "params": {"clips": [(r.get("result") or r)["clips"][0] for r in res], "mode": "set",
                                         "db": -2.0}}])

# 5) nothing else moved
s = seq()
after = {(k, c["clip"]): (c["startFrame"], c["endFrame"]) for k in ("video", "audio") for t in s[k] for c in t["items"]}
changed = {k: (before.get(k), after.get(k)) for k in set(before) | set(after) if before.get(k) != after.get(k)}
expect = {("video", pad["clip"])} | {("video", c["clip"]) for c in cards + caps} | {("audio", c["clip"]) for c in woosh}
other = {k: v for k, v in changed.items() if k not in expect and not (k[0] == "audio" and v[0] is None)}
print(f"{len(CUTS)} push-in blurs; {len(changed)} clip changes; unexpected: {other or 'none'}; {s['durationFrames']} f")
