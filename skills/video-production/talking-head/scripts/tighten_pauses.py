#!/usr/bin/env python3
"""Cuts the pauses of 0.35 s or more that are left in the talking head down to about 0.2 s (user, 2026-10-25: "the
silence is a bit long"), and puts back the caption on words spoken after a pause (the caption for "...your mom is
thinner skin." ended in the pause, so "thinner skin" had none).
A pause is cut only where a new caption starts at a clause or sentence, so the jump cut follows the client's rule, and
only where both talking-head shots stay 1.8 s or longer, unless a full-screen V3 clip hides the cut. The cut keeps
0.16 s after the voice and 0.04 s before it comes back. Every later clip on every track moves left; a clip running
through the pause ends where it did, minus the cut, so a CGI clip plays on without a jump. The caption after the pause
starts on the cut, the one before ends on it. Pauses inside a clause stay (the client healed "is | thinner").
--force "WORDS" also cuts the pause before the caption starting with WORDS when it would leave a shot under 1.8 s (user,
2026-10-25: "Your skin looks firmer, | the dimples"). Then run punch_cuts.py and check --render, not snap (it ignores
clip speed). Usage: tighten_pauses.py edit/hook-N.fcproj [--dry] [--force "WORDS"]... [--master PATH]"""
import json, math, subprocess, sys
from pathlib import Path
import numpy as np

TPS, FPS = 254016000000, 24
MIN_PAUSE, KEEP_AFTER, KEEP_BEFORE, MIN_SHOT, DB = 0.35, 0.16, 0.04, 1.8, -45
def master(proj):
    """--master PATH, or the sped-up isolated master in deliverables/ (the file V1 cuts)."""
    if "--master" in sys.argv:
        return Path(sys.argv[sys.argv.index("--master") + 1]).resolve()
    return max((proj.parent.parent / "deliverables").glob("*_isolated_1.1x.mp4"), key=lambda p: p.stat().st_mtime)


PROJ = Path(sys.argv[1]).resolve()
DRY = "--dry" in sys.argv
FORCE = [sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == "--force"]
SRC = master(PROJ)
PCM = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                   capture_output=True, check=True).stdout, np.int16).astype(float)


BLOCKS = [l.strip() for l in open(PROJ.parent.parent / "captions" / f"{PROJ.stem}.blocks.txt") if l.strip()]


def norm(x):
    return x.replace("’", "'").lower()


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


def run(cmds):
    script = PROJ.parent / ".fc-pauses.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
    script.unlink()
    if out.returncode or not all(json.loads(l).get("ok") for l in out.stdout.splitlines() if l.startswith("{")):
        sys.exit(f"FilmCraft failed: {out.stdout[-1500:]}{out.stderr[-1500:]}")


def voice_map(s):
    """Voice on or off for every half frame of the timeline, read from the source under each A1 clip."""
    end = s["audio"][0]["items"][-1]["endFrame"]
    on = np.zeros(end * 2, bool)
    for c in s["audio"][0]["items"]:
        for h in range(c["startFrame"] * 2, c["endFrame"] * 2):
            t = c["sourceIn"] / TPS + (h / 2 - c["startFrame"]) / FPS
            x = PCM[int(t * 16000):int((t + 1 / 48) * 16000)]
            on[h] = len(x) and 20 * np.log10(np.sqrt((x ** 2).mean()) / 32768 + 1e-9) > DB
    return on


def runs(m):
    i, out = 0, []
    while i < len(m):
        j = i
        while j < len(m) and m[j] == m[i]:
            j += 1
        out.append((bool(m[i]), i / 2, j / 2))
        i = j
    return out


def move_caption(c, start, end, track):
    return [{"id": "timeline.move", "params": {"moves": [{"clip": c["clip"], "track": track, "time": start * TPS // FPS}], "insert": False}},
            {"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": end - (start + c["endFrame"] - c["startFrame"])}}]


s = fc("inspect", "sequence")
v = s["video"]
caps = sorted(v[-1]["items"], key=lambda c: c["startFrame"])
pauses = [(a, b) for on, a, b in runs(voice_map(s)) if not on and a > 0 and (b - a) / FPS >= MIN_PAUSE]
todo = []
for a, b in pauses:
    A, B = math.ceil(a + KEEP_AFTER * FPS), math.floor(b - KEEP_BEFORE * FPS)
    nxt = min(caps, key=lambda c: abs(c["startFrame"] - b))
    prev = max((c for c in caps if c["startFrame"] < nxt["startFrame"]), key=lambda c: c["startFrame"])
    shot = next(c for c in v[0]["items"] if c["startFrame"] <= A < c["endFrame"])
    hidden = any(c["startFrame"] <= A - 1 and A + 1 < c["endFrame"] for c in v[2]["items"])
    full = next((l for l in BLOCKS if norm(l).startswith(norm(prev["name"]))), prev["name"])   # a clip is named by its first line
    clause = full[-1] in ",.:;?!" or nxt["name"].lower().startswith(("and ", "but ", "because "))
    why = ("no caption starts after it" if abs(nxt["startFrame"] - b) > 3 else
           "inside a clause" if not clause else
           "a shot would be under 1.8 s" if not hidden and not any(nxt["name"].startswith(w) for w in FORCE) and min(A - shot["startFrame"], shot["endFrame"] - B) < MIN_SHOT * FPS else
           "too short to cut" if B - A < 2 else "")
    print(f"  {a / FPS:7.2f}s {(b - a) / FPS:.2f}s  …{prev['name'][-22:]:22} | {nxt['name'][:22]:22}  "
          f"{'skip: ' + why if why else f'cut {(B - A) / FPS:.2f}s' + (' (under V3)' if hidden else '')}")
    if not why:
        todo.append((A, B))

for A, B in ([] if DRY else reversed(todo)):    # last first, so the earlier frames stay put
    s = fc("inspect", "sequence")
    v, n = s["video"], B - A
    run([{"id": "timeline.razor", "params": {"time": f * TPS // FPS, "track": t[0]["id"]}} for f in (A, B) for t in (v, s["audio"])])
    s = fc("inspect", "sequence")
    v = s["video"]
    held, cmds = [], []
    for t in v[1:]:
        for c in t["items"]:
            if c["startFrame"] < A < c["endFrame"]:      # runs into the pause: ends at A for now
                if t is not v[-1]:
                    held.append((c, c["endFrame"] - n))
                cmds.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": A - c["endFrame"]}})
            elif A <= c["startFrame"] < B:               # starts in the pause: loses its head
                cmds.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "in", "mode": "regular", "deltaFrames": B - c["startFrame"]}})
    run(cmds + [{"id": "edit.rippleDelete", "params": {"clips": [c["clip"] for t in (v[0], s["audio"][0]) for c in t["items"] if c["startFrame"] == A]}}])
    s = fc("inspect", "sequence")
    v = s["video"]
    cmds = [{"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": end - A}}
            for c, end in held]
    caps = sorted(v[-1]["items"], key=lambda c: c["startFrame"])
    nxt = min(caps, key=lambda c: abs(c["startFrame"] - A))
    cmds += move_caption(nxt, A, nxt["endFrame"], v[-1]["id"])
    prev = max((c for c in caps if c["startFrame"] < nxt["startFrame"]), key=lambda c: c["startFrame"])
    if prev["endFrame"] != A:
        cmds.append({"id": "timeline.trim", "params": {"clip": prev["clip"], "edge": "out", "mode": "regular", "deltaFrames": A - prev["endFrame"]}})
    run(cmds)

# Words spoken after a caption already ended: that caption stays up until the next one.
s = fc("inspect", "sequence")
caps = sorted(s["video"][-1]["items"], key=lambda c: c["startFrame"])
on = voice_map(s)
cmds = []
for a, b in zip(caps, caps[1:]):
    if b["startFrame"] > a["endFrame"] and on[a["endFrame"] * 2:b["startFrame"] * 2].sum() >= 6:
        print(f"  {a['endFrame'] / FPS:7.2f}s  voice with no caption: '{a['name']}' now runs to {b['startFrame'] / FPS:.2f}s")
        cmds.append({"id": "timeline.trim", "params": {"clip": a["clip"], "edge": "out", "mode": "regular", "deltaFrames": b["startFrame"] - a["endFrame"]}})
if cmds and not DRY:
    run(cmds)
print(f"{PROJ.stem}: {len(todo)} pauses cut, {sum(B - A for A, B in todo) / FPS:.2f}s shorter")
