#!/usr/bin/env python3
"""Adds the inserts to one hook project (edit/hook-N.fcproj: talking head on V1/A1, tightened, punch-ins kept), in the
reference video's style: box stills under the doctor's face on V2, full-screen CGI/product clips on V3, video only.
Each hook gets its own hook lines plus the shared body. No picture or clip shows twice in one video (checked).
Anchors are in talking-head source seconds (words/*.words.json) and are mapped through the hook's V1 cuts.
Usage: build_inserts.py N [--replace]   (--replace clears the old inserts on V2/V3 after a backup)"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
HOOK = int(sys.argv[1])
PROJ = EDIT / f"hook-{HOOK}.fcproj"
TPS = 254016000000
BOX_W, BOX_H, BOX_CX, BOX_CY = 720, 500, 540, 1490   # box under the face, over the mic and chest
BOX_MAX = 4.5                                          # longest a box still holds before the doctor shows clean

# TEMPLATE: copy to video-N/edit/build_inserts.py and fill in WORDS, FULL, HOOKS and BODY (Aleo video-3's is the worked
# example: upwork-max/video-3/edit/build_inserts.py). Read every line of the words file before writing anchors.
WORDS = EDIT / "words/<Master>_TalkingHead_Full_9x16_isolated_1.1x.words.json"   # transcribe.py on the master file
B = "assets/inserts/box/box-{}.jpg"
WEB = "assets/inserts/web/{}"
CH = "assets/inserts/charts/{}.png"
SC = "scenes/scene-{0}/scene-{0}-v1.jpg"          # pass the approved version's path when it isn't v1
RV = "assets/screens/reviews/review{}.png"
SC2 = "scenes/scene-{0}/scene-{0}{1}/scene-{0}{1}-v1.jpg"
PAIR = "assets/inserts/pairs/pair-{}.jpg"   # two stills side by side (made below from scene-Na and scene-Nb)
FULL = {}   # shot -> its versioned 1080p final, e.g. {"202": "clips/clip-202/final/clip-202-v1-1080p.mp4"}

# (source seconds | word | (word, after_sec), media) — "full:<shot>" is a full-screen clip, None shows the face clean.
# Every insert shows what its words say, and starts on them. Write the line it covers as a comment.
HOOKS = {
    1: [(0.16, SC.format(302)),                  # "cellulite as long as you can remember"
        (("worse", 2), PAIR.format(325))],       # "looks worse every year": thigh at 30 | at 48
}
BODY = [
    (41.1, CH.format("collagen-decline")),       # "only gets worse with age"
    (43.3, "full:202"),                          # "skin that's too thin to hide the dimples"
    (57.3, None),                                # the face alone for a beat
]
ANCHORS = HOOKS[HOOK] + BODY
shown = [m for _, m in ANCHORS if m]
if len(shown) != len(set(shown)):
    sys.exit(f"repeats in hook-{HOOK}: {sorted({m for m in shown if shown.count(m) > 1})}")


DIAGRAM_PAIRS = set()   # pair numbers whose halves are drawings on white (cropped to the drawing)


def make_pair(n):
    """scene-Na | scene-Nb side by side, the same height, a thin white gap: one box image."""
    out = ROOT / PAIR.format(n)
    if not out.exists():
        a, b = (Image.open(ROOT / SC2.format(n, k)).convert("RGB") for k in "ab")
        if n in DIAGRAM_PAIRS:   # drawings on white: crop to the drawing plus a margin so both halves fill their side
            a, b = (ImageOps.expand(im.crop(ImageOps.invert(im.convert("L")).point(lambda x: 255 if x > 12 else 0).getbbox()),
                                    30, "white") for im in (a, b))
        h = 900
        a, b = (im.resize((round(im.width * h / im.height), h), Image.LANCZOS) for im in (a, b))
        gap = 12
        img = Image.new("RGB", (a.width + gap + b.width, h), "white")
        img.paste(a, (0, 0)); img.paste(b, (a.width + gap, 0))
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out, quality=92)


for _, m in ANCHORS:
    if m and m.startswith("assets/inserts/pairs/"):
        make_pair(m.split("-")[-1].split(".")[0])


def cli(cmds):
    script = EDIT / ".fc-run.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    script.unlink()
    return [r.get("result") for r in res]


def inspect(what):
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "inspect", what], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


words = json.loads(WORDS.read_text())


def src_time(a):
    if isinstance(a, (int, float)):
        return a
    word, after = a if isinstance(a, tuple) else (a, 0)
    return next(w["start"] for w in words if w["start"] >= after and w["word"].lower().strip(",.?!") == word)


seq = inspect("sequence")
v = seq["video"]
old = [c["clip"] for t in v[1:] for c in t["items"]]
if old and "--replace" not in sys.argv:
    sys.exit("V2/V3 already hold clips: pass --replace to clear them (a backup is kept)")
if old:
    import shutil, datetime
    bk = EDIT / f"backup-{datetime.date.today():%Y%m%d}-norepeat"
    bk.mkdir(exist_ok=True)
    if not (bk / PROJ.name).exists():   # keep the first backup: the edit before any rebuild
        shutil.copy2(PROJ, bk / PROJ.name)
    cli([{"id": "edit.clear", "params": {"clips": old}}, {"id": "file.save", "params": {}}])
cuts = sorted(((c["start"], c["sourceIn"], c["sourceOut"]) for c in v[0]["items"]))
seq_end = max(c["end"] for c in v[0]["items"]) / TPS


def tl(src):
    t = round(src * TPS)
    for start, sin, sout in cuts:
        if sin <= t < sout:
            return (start + t - sin) / TPS
        if sin > t:
            return start / TPS   # inside a cut pause: the next kept piece
    return seq_end


anchors = sorted((tl(src_time(a)), m) for a, m in ANCHORS)
paths = sorted({str(ROOT / (FULL[m[5:]] if m.startswith("full:") else m)) for _, m in anchors if m})
for p in paths:
    if not Path(p).exists():
        sys.exit(f"missing {p}")
items = dict(zip(paths, cli([{"id": "file.import", "params": {"paths": paths}}, {"id": "file.save", "params": {}}])[0]["items"]))

place, fx, plan = [], [], []
for i, (t, m) in enumerate(anchors):
    if not m:
        continue
    nxt = anchors[i + 1][0] if i + 1 < len(anchors) else seq_end
    full = m.startswith("full:")
    path = str(ROOT / (FULL[m[5:]] if full else m))
    dur = min(nxt, t + (4.0 if full else BOX_MAX), seq_end) - t
    if dur < 0.4:
        print(f"skip {m} at {t:.2f}s: only {dur:.2f}s")
        continue
    place.append({"id": "timeline.place", "params": {"item": items[path], "track": "V3" if full else "V2", "seconds": round(t, 3),
                                                     "duration": round(dur * TPS), "insert": False, "video": True, "audio": False}})
    plan.append((t, dur, m, full, path))

clips = [r["clips"][0] for r in cli(place + [{"id": "file.save", "params": {}}])[:-1]]
for clip, (t, dur, m, full, path) in zip(clips, plan):
    if full:
        continue
    w, h = Image.open(path).size
    s = min(BOX_W / w, BOX_H / h) * 100
    fx += [{"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale", "value": round(s, 2)}},
           {"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "position", "value": [BOX_CX, BOX_CY]}}]
cli(fx + [{"id": "file.save", "params": {}}])
for t, dur, m, full, _ in plan:
    print(f"{t:7.2f}  {dur:4.1f}s  {'FULL' if full else 'box '}  {m}")
print(f"{len(plan)} inserts, sequence {seq_end:.1f}s → {PROJ}")
