#!/usr/bin/env python3
"""Cuts the pause inside one caption down to about 0.2 s and splits that caption onto the cut (user, 2026-10-25: cut the
pause before "thinner skin" too, "with its own caption on the cut"). The caption that starts with FIRST is rebuilt in
template 6 as two captions: TEXT1 up to the cut, TEXT2 from it. The cut keeps 0.16 s after the voice and 0.04 s before
it comes back; every later clip moves left, and a clip running through the pause plays on without a jump.
Then run punch_cuts.py and fc_inserts.py check --render.
Usage: split_pause.py edit/hook-N.fcproj FIRST TEXT1 TEXT2 [--master PATH]"""
import json, math, subprocess, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path.home() / ".claude/skills/captions-filmcraft/scripts"))
import fc_captions as fcc

TPS, FPS = 254016000000, 24
KEEP_AFTER, KEEP_BEFORE, DB = 0.16, 0.04, -45
def master(proj):
    """--master PATH, or the sped-up isolated master in deliverables/ (the file V1 cuts)."""
    if "--master" in sys.argv:
        return Path(sys.argv[sys.argv.index("--master") + 1]).resolve()
    return max((proj.parent.parent / "deliverables").glob("*_isolated_1.1x.mp4"), key=lambda p: p.stat().st_mtime)


PROJ = Path(sys.argv[1]).resolve()
FIRST, TEXT1, TEXT2 = sys.argv[2:5]
SRC = master(PROJ)
PCM = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                   capture_output=True, check=True).stdout, np.int16).astype(float)


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


def run(cmds):
    script = PROJ.parent / ".fc-split.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
    script.unlink()
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {out.stdout[-1500:]}{out.stderr[-1500:]}")
    return [r.get("result") for r in res]


def voiced(s, f):
    """Voice in the half frame at timeline frame f (a float), read from the source under A1."""
    c = next(c for c in s["audio"][0]["items"] if c["startFrame"] <= f < c["endFrame"])
    t = c["sourceIn"] / TPS + (f - c["startFrame"]) / FPS
    x = PCM[int(t * 16000):int((t + 1 / 48) * 16000)]
    return 20 * np.log10(np.sqrt((x ** 2).mean()) / 32768 + 1e-9) > DB


s = fc("inspect", "sequence")
v = s["video"]
cap = [c for c in v[-1]["items"] if c["name"].startswith(FIRST)]
if len(cap) != 1:
    sys.exit(f"{PROJ.stem}: {len(cap)} captions start with {FIRST!r}")
cap = cap[0]
c0, c1 = cap["startFrame"], cap["endFrame"]
# the longest pause inside the caption
best, run_start = (0, 0, 0), None
for h in range(c0 * 2, c1 * 2 + 1):
    on = h == c1 * 2 or voiced(s, h / 2)
    if not on and run_start is None:
        run_start = h
    elif on and run_start is not None:
        best = max(best, (h - run_start, run_start / 2, h / 2))
        run_start = None
_, a, b = best
A, B = math.ceil(a + KEEP_AFTER * FPS), math.floor(b - KEEP_BEFORE * FPS)
n = B - A
if n < 2:
    sys.exit(f"{PROJ.stem}: no pause to cut in {FIRST!r} ({(b - a) / FPS:.2f}s)")
print(f"{PROJ.stem}: pause {a / FPS:.2f}-{b / FPS:.2f}s ({(b - a) / FPS:.2f}s), cut {n} frames at {A / FPS:.2f}s")

run([{"id": "edit.clear", "params": {"clips": [cap["clip"]]}}]
    + [{"id": "timeline.razor", "params": {"time": f * TPS // FPS, "track": t[0]["id"]}} for f in (A, B) for t in (v, s["audio"])])
s = fc("inspect", "sequence")
v = s["video"]
held, cmds = [], []
for t in v[1:]:
    for c in t["items"]:
        if c["startFrame"] < A < c["endFrame"]:
            held.append((c, c["endFrame"] - n))
            cmds.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": A - c["endFrame"]}})
        elif A <= c["startFrame"] < B:
            cmds.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "in", "mode": "regular", "deltaFrames": B - c["startFrame"]}})
run(cmds + [{"id": "edit.rippleDelete", "params": {"clips": [c["clip"] for t in (v[0], s["audio"][0]) for c in t["items"] if c["startFrame"] == A]}}])
run([{"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": end - A}} for c, end in held])

# the two captions, built as fc_captions.py build makes template 6
st = dict(fcc.STYLES["6"])
track = len(fc("inspect", "sequence")["video"]) - 1
blocks = [(TEXT1, c0, A), (TEXT2, A, c1 - n)]
made = []
for text, f0, f1 in blocks:
    ls = fcc.two_lines(text)
    size = min(fcc.fit_size(st, t) for t in ls)
    ys = st["lines"] if len(ls) == 2 else [st["lines"][-1]]
    pos = [[st["props"]["position"][0], y] for y in ys]
    r = run([{"id": "graphics.newText", "params": {"text": ls[0], "position": pos[0], "size": size, "font": st["font"],
                                                    "fontStyle": st["fontStyle"], "seconds": (f1 - f0) / FPS, "track": track,
                                                    "time": f0 * TPS // FPS}},
             {"id": "graphics.set", "params": {"props": dict(st["props"], position=pos[0])}}])
    clip = r[0]["clip"]
    second = []
    if len(ls) == 2:
        second += [{"id": "graphics.newText", "params": {"text": ls[1], "position": pos[1], "size": size,
                                                          "font": st["font"], "fontStyle": st["fontStyle"], "clip": clip}},
                   {"id": "graphics.set", "params": {"clip": clip, "layer": 1, "props": dict(st["props"], position=pos[1])}}]
    run(second + fcc.box_cmds(st, clip, ls, size, pos))
    made.append((clip, f0, f1, " / ".join(ls)))
got = {c["clip"]: (c["startFrame"], c["endFrame"]) for c in fc("inspect", "sequence")["video"][-1]["items"]}
for clip, f0, f1, t in made:
    print(f"  {f0 / FPS:7.2f}-{f1 / FPS:6.2f}s  {t}" + ("" if got.get(clip) == (f0, f1) else f"  WRONG: {got.get(clip)}"))
