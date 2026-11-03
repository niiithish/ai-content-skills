#!/usr/bin/env python3
"""Puts a hook's one-take talking clip in place of its two-clip opening (user, 2026-10-25: hooks 2 and 3 "said in 1
shot", the clip's own audio kept). Everything before the body (--body: the master second the body starts, 32.25 on
Aleo) on V1/A1 goes; the take, trimmed --gap seconds after its last word (default 0.7, capped at the take's end: 0.2 s ran straight into the body,
"no gap at all", and 0.37 s was still "too tight"), goes in at 0 and the body closes up behind it. The take's audio is set to the body's loudness (EBU R128,
measured on both; Flow's raw voice was 3 dB louder than the isolated master). The hook's captions and box stills
keep their order and move to the frames their first words are spoken in the take (word times from its transcript).
Then run punch_cuts.py and fc_inserts.py check --render.
Usage: one_take_hook.py edit/hook-N.fcproj TAKE-1080p.mp4 TAKE.words.json --body SECONDS [--gap 0.7] [--master PATH]
TAKE.words.json comes from the transcribe skill (check it first: every word once)."""
import datetime, json, math, re, shutil, subprocess, sys
from pathlib import Path

TPS, FPS = 254016000000, 24
BODY_SRC = float(sys.argv[sys.argv.index("--body") + 1])
KEEP_AFTER = float(sys.argv[sys.argv.index("--gap") + 1]) if "--gap" in sys.argv else 0.7
PROJ, TAKE, WORDS = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), json.load(open(sys.argv[3]))
BLOCKS = [l.strip() for l in open(PROJ.parent.parent / "captions" / f"{PROJ.stem}.blocks.txt") if l.strip()]


def master(proj):
    """--master PATH, or the sped-up isolated master in deliverables/ (the file V1 cuts)."""
    if "--master" in sys.argv:
        return Path(sys.argv[sys.argv.index("--master") + 1]).resolve()
    return max((proj.parent.parent / "deliverables").glob("*_isolated_1.1x.mp4"), key=lambda p: p.stat().st_mtime)


def lufs(path, start=0, dur=30):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(start), "-t", str(dur), "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


def run(cmds):
    script = PROJ.parent / ".fc-onetake.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
    script.unlink()
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {out.stdout[-1500:]}{out.stderr[-1500:]}")


s = fc("inspect", "sequence")
v, a1 = s["video"], s["audio"][0]
H = next(c["startFrame"] for c in v[0]["items"] if abs(c["sourceIn"] / TPS - BODY_SRC) < 0.05)
caps = sorted((c for c in v[-1]["items"] if c["startFrame"] < H), key=lambda c: c["startFrame"])
boxes = sorted((c for c in v[1]["items"] if c["startFrame"] < H), key=lambda c: c["startFrame"])
if any(c["startFrame"] < H < c["endFrame"] for t in v[1:] for c in t["items"]) or any(c["startFrame"] < H for t in v[2:-1] for c in t["items"]):
    sys.exit("a clip other than the hook's box stills and captions runs over the hook")

# each hook caption starts on its first word in the take
starts, i = [], 0
for b in BLOCKS[:len(caps)]:
    starts.append(0 if i == 0 else round(WORDS[i]["start"] * FPS))
    i += len(re.findall(r"\S+", b))
if i != len(WORDS):
    sys.exit(f"the hook's captions hold {i} words, the take {len(WORDS)}")
TAKE_LEN = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(TAKE)],
                                capture_output=True, text=True, check=True).stdout)
L = min(math.ceil((WORDS[-1]["end"] + KEEP_AFTER) * FPS), math.floor(TAKE_LEN * FPS))
new = {c["clip"]: (f0, f1) for c, f0, f1 in zip(caps, starts, starts[1:] + [L])}
cap_of = {c["startFrame"]: k for k, c in enumerate(caps)}
box_starts = [starts[cap_of[b["startFrame"]]] for b in boxes]
new.update({b["clip"]: (f0, f1) for b, f0, f1 in zip(boxes, box_starts, box_starts[1:] + [L])})
for c in caps:
    print(f"  {new[c['clip']][0] / FPS:5.2f}-{new[c['clip']][1] / FPS:5.2f}s  {c['name']}")

bk = PROJ.parent / f"backup-{datetime.date.today()}-onetake"
bk.mkdir(exist_ok=True)
shutil.copy(PROJ, bk / PROJ.name)
gain = round(lufs(master(PROJ), BODY_SRC) - lufs(TAKE), 1)
moved = caps + boxes
run([{"id": "edit.clear", "params": {"clips": [c["clip"] for t in (v[0], a1) for c in t["items"] if c["startFrame"] < H]}}]
    + [{"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": c["startFrame"] + 1 - c["endFrame"]}} for c in moved])
run([{"id": "timeline.move", "params": {"moves": [{"clip": c["clip"], "track": t["id"], "time": new[c["clip"]][0] * TPS // FPS}
                                                  for t in (v[1], v[-1]) for c in t["items"] if c["clip"] in new], "insert": False}}]
    + [{"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": new[c["clip"]][1] - new[c["clip"]][0] - 1}} for c in moved])
run([{"id": "file.import", "params": {"paths": [str(TAKE)]}}])
item = next(c["item"] for c in fc("inspect", "project")["root"]["children"] if c["name"] == TAKE.name)
run([{"id": "timeline.place", "params": {"item": item, "track": "V1", "audioTrack": "A1", "frame": 0, "insert": False, "duration": L * TPS // FPS}},
     {"id": "sequence.closeGap", "params": {"track": "V1", "time": L * TPS // FPS}}])
take_a = next(c["clip"] for c in fc("inspect", "sequence")["audio"][0]["items"] if c["startFrame"] == 0)
run([{"id": "clip.audioGain", "params": {"clips": [take_a], "mode": "set", "db": gain}}])

s = fc("inspect", "sequence")
v = s["video"]
got = {c["clip"]: (c["startFrame"], c["endFrame"]) for t in v for c in t["items"]}
body = next(c for c in v[0]["items"] if abs(c["sourceIn"] / TPS - BODY_SRC) < 0.05)
bad = [k for k, f in new.items() if got.get(k) != f]
nxt = [min((c for c in t["items"] if c["startFrame"] >= L), key=lambda c: c["startFrame"])["startFrame"] for t in (v[1], v[-1])]
print(f"{PROJ.stem}: hook {H / FPS:.2f}s -> {L / FPS:.2f}s one take; body at {body['startFrame'] / FPS:.2f}s, "
      f"next box/caption at {nxt[0] / FPS:.2f}/{nxt[1] / FPS:.2f}s, take audio {gain:+.1f} dB" + (f"  WRONG: {bad}" if bad or body["startFrame"] != L or nxt != [L, L] else ""))
