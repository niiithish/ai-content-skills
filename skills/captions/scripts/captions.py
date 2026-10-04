#!/usr/bin/env python3
"""Burn the locked caption style into a finished 9:16 edit.

  captions.py words   EDIT                          Parakeet word times -> captions/<stem>.words.json
  captions.py plan    EDIT --script S [--labels L]  captions and labels with times -> captions/<stem>.plan.json
  captions.py preview EDIT [--at T]                 one real frame with a caption and a label -> captions/<stem>.preview.png
  captions.py render  EDIT -o OUT.mp4               the captioned video (temp file, then mv; audio copied)

The script file is the voiceover text (lines starting with # are skipped); the words on screen come from it,
not from the transcript. The labels file has one "LABEL | first words of the line it starts on" per line.
Work files go in <video>/captions/ (the folder holding PLAN.md above EDIT, else EDIT's folder), never a scratchpad.

Style (locked; change it only when the user asks): layout on a 1080x1920 canvas, scaled to the edit.
  captions: #111 TikTok Sans SemiBold 54 px on white, one merged box with rounded corners and filleted steps,
            at most 2 lines, block bottom at y 1480 (the bottom of the Meta/TikTok safe box, x 40-1050, y 220-1500)
  labels:   the same box, white on #EA4040, top at y 245, on screen 3 s from the start of their line
"""
import argparse, difflib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT = HERE.parent / "fonts" / "TikTokSans-SemiBold.ttf"
W, H = 1080, 1920
SIZE, PITCH, PADX, R, SS = 54, 74, 20, 18, 4       # pitch ~1.95x cap height; supersample for smooth corners
BOTTOM, LABEL_TOP, LABEL_SECS = 1480, 245, 3.0
TARGET, MAXLEN, SHORT = 36, 50, 16                 # chars per caption: aim, hard max, orphan threshold
CAP = ((255, 255, 255), (17, 17, 17))
LABEL = ((0xEA, 0x40, 0x40), (255, 255, 255))

font = ImageFont.truetype(str(FONT), SIZE)
CAPH = -font.getbbox("H", anchor="ls")[1]


def sh(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def probe(edit):
    info = json.loads(sh("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                         "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(edit)))
    st = info["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    return int(st["width"]), int(st["height"]), float(num) / float(den), float(info["format"]["duration"])


def work_dir(edit):
    for d in [edit.parent, *edit.parent.parents]:
        if (d / "PLAN.md").is_file():
            out = d / "captions"
            break
    else:
        out = edit.parent / "captions"
    out.mkdir(parents=True, exist_ok=True)
    return out


def paths(edit):
    d = work_dir(edit)
    return {k: d / f"{edit.stem}.{k}" for k in ("words.json", "plan.json", "preview.png")} | {"frames": d / f"{edit.stem}-frames"}


# ---------- words ----------

def cmd_words(a):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "transcribe" / "scripts"))
    try:
        from transcribe import words as transcribe_words
    except ImportError:
        sys.exit("needs the transcribe skill next to this one (skills/transcribe)")
    words = [list(w) for w in transcribe_words(a.edit, a.engine)]
    out = paths(a.edit)["words.json"]
    out.write_text(json.dumps(words))
    print(f"{len(words)} words -> {out}")


# ---------- plan ----------

def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def curly(w):
    w = re.sub(r'([?!])",$', r'\1"', w)    # 'asking "does that hurt?",' reads without the comma
    w = re.sub(r'^"', "“", w)
    w = w.replace('"', "”")
    return w.replace("'", "’")


def chunks(words):
    """Per sentence, split into captions by DP: ~TARGET chars each, max MAXLEN, prefer breaks at commas."""
    L = lambda i, j: len(" ".join(words[i:j]))
    sents, st = [], 0
    for i, w in enumerate(words):
        if re.search(r'[.!?]["”]?$', w):
            sents.append((st, i + 1)); st = i + 1
    if st < len(words):
        sents.append((st, len(words)))
    out = []
    for s, e in sents:
        best = {s: (0, None)}
        for j in range(s + 1, e + 1):
            cands = []
            for i in range(s, j):
                if i not in best:
                    continue
                n = L(i, j)
                if n > MAXLEN and j - i > 1:
                    continue
                c = (n - TARGET) ** 2 / 12
                if j < e and not re.search(r'[,;:—]["”]?$', words[j - 1]):
                    c += 20
                if n < SHORT and not (i == s and j == e):
                    c += 60
                cands.append((best[i][0] + c, i))
            if cands:
                best[j] = min(cands)
        j, parts = e, []
        while j > s:
            i = best[j][1]; parts.append(list(range(i, j))); j = i
        out += parts[::-1]
    return out


def two_lines(ws):
    txt = " ".join(ws)
    if len(txt) <= SHORT or len(ws) < 3:
        return [txt]
    k = min(range(1, len(ws)), key=lambda k: max(len(" ".join(ws[:k])), len(" ".join(ws[k:]))) * 10
            + (len(" ".join(ws[:k])) < len(" ".join(ws[k:]))))
    return [" ".join(ws[:k]), " ".join(ws[k:])]


def align(words, heard):
    """Script word -> (start, end) from the heard words, by char-level alignment; gaps interpolated."""
    sc, sidx, tc, tidx = [], [], [], []
    for i, t in enumerate(words):
        for ch in norm(t):
            sc.append(ch); sidx.append(i)
    for i, t in enumerate(heard):
        for ch in norm(t[0]):
            tc.append(ch); tidx.append(i)
    start, end = [None] * len(words), [None] * len(words)
    for a, b, n in difflib.SequenceMatcher(None, sc, tc, autojunk=False).get_matching_blocks():
        for k in range(n):
            si, ti = sidx[a + k], tidx[b + k]
            if start[si] is None:
                start[si] = heard[ti][1]
            end[si] = heard[ti][2]
    missing = sum(x is None for x in start)
    for arr in (start, end):
        for i in range(len(arr)):
            if arr[i] is None:
                j = i
                while j < len(arr) and arr[j] is None:
                    j += 1
                a = arr[i - 1] if i else 0.0
                b = arr[j] if j < len(arr) else a + 0.3
                for k in range(i, j):
                    arr[k] = a + (b - a) * (k - i + 1) / (j - i + 1)
    return start, end, missing


def cmd_plan(a):
    p = paths(a.edit)
    if not p["words.json"].is_file():
        sys.exit(f"no {p['words.json']}: run `captions.py words {a.edit}` first")
    heard = json.loads(p["words.json"].read_text())
    text = " ".join(l.strip() for l in Path(a.script).read_text().splitlines() if l.strip() and not l.lstrip().startswith("#"))
    words = text.split()
    start, end, missing = align(words, heard)
    dur = probe(a.edit)[3]
    cs = chunks(words)
    caps = []
    for n, c in enumerate(cs):
        t0 = start[c[0]]
        t1 = start[cs[n + 1][0]] if n + 1 < len(cs) else min(dur, end[c[-1]] + 0.8)
        if n + 1 < len(cs) and t1 - end[c[-1]] > 0.6:     # a long pause: clear shortly after the speech
            t1 = end[c[-1]] + 0.35
        caps.append([round(t0, 3), round(t1, 3), [' '.join(curly(w) for w in ln.split()) for ln in two_lines([words[j] for j in c])]])
    labels = []
    for line in (Path(a.labels).read_text().splitlines() if a.labels else []):
        if "|" not in line:
            continue
        label, key = (x.strip() for x in line.split("|", 1))
        k = [norm(x) for x in key.split()]
        hit = next((i for i in range(len(words) - len(k) + 1) if [norm(x) for x in words[i:i + len(k)]] == k), None)
        if hit is None:
            sys.exit(f"label {label!r}: {key!r} is not in the script")
        labels.append([round(start[hit], 3), round(min(dur, start[hit] + LABEL_SECS), 3), label])
    p["plan.json"].write_text(json.dumps({"edit": str(a.edit), "duration": dur, "captions": caps, "labels": labels}, indent=1, ensure_ascii=False))
    for t0, t1, lines in caps:
        print(f"{t0:6.2f}-{t1:6.2f}  " + " / ".join(lines))
    for t0, t1, label in labels:
        print(f"{t0:6.2f}-{t1:6.2f}  [{label}]")
    print(f"{len(words)} script words, {missing} not heard (timed by interpolation) -> {p['plan.json']}")


# ---------- drawing ----------

def _corner(m, cx, cy, dx, dy, r, convex):
    """Round one corner of the union mask; (dx, dy) points into the empty quadrant."""
    if r < 1:
        return
    p = Image.new("L", (r, r), 0 if convex else 255)
    if convex:
        px, py = (0 if dx > 0 else r), (0 if dy > 0 else r)
        ox, oy = (cx - r if dx > 0 else cx), (cy - r if dy > 0 else cy)
        ImageDraw.Draw(p).ellipse((px - r, py - r, px + r, py + r), fill=255)
    else:
        px, py = (r if dx > 0 else 0), (r if dy > 0 else 0)
        ox, oy = (cx if dx > 0 else cx - r), (cy if dy > 0 else cy - r)
        ImageDraw.Draw(p).ellipse((px - r, py - r, px + r, py + r), fill=0)
    m.paste(p, (ox, oy))


def draw_box(im, lines, colours, top=None, bottom=BOTTOM):
    """One merged shape: stacked line boxes, convex corners rounded, concave steps filleted."""
    bg, fg = colours
    d = ImageDraw.Draw(im)
    y0 = top if top is not None else bottom - PITCH * len(lines)
    m = Image.new("L", (W * SS, H * SS), 0)
    md = ImageDraw.Draw(m)
    xs = []
    for ln in lines:
        half = round((d.textlength(ln, font=font) / 2 + PADX) * SS)
        xs.append((W * SS // 2 - half, W * SS // 2 + half))
    ys = [(y0 + k * PITCH) * SS for k in range(len(lines) + 1)]
    for k, (xa, xb) in enumerate(xs):
        md.rectangle((xa, ys[k], xb - 1, ys[k + 1] - 1), fill=255)
    r, n = R * SS, len(xs)
    for s in (1, -1):
        edge = lambda k: xs[k][1] if s > 0 else xs[k][0]
        _corner(m, edge(0), ys[0], s, -1, r, True)
        _corner(m, edge(n - 1), ys[n], s, 1, r, True)
        for k in range(n - 1):
            a_, b_ = edge(k), edge(k + 1)
            rr = min(r, abs(a_ - b_) // 2)
            if rr < SS:
                continue
            if (a_ - b_) * s > 0:
                _corner(m, a_, ys[k + 1], s, 1, rr, True)
                _corner(m, b_, ys[k + 1], s, 1, rr, False)
            else:
                _corner(m, b_, ys[k + 1], s, -1, rr, True)
                _corner(m, a_, ys[k + 1], s, -1, rr, False)
    m = m.resize((W, H), Image.LANCZOS)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(Image.new("RGBA", (W, H), bg + (255,)), (0, 0), m)
    ld = ImageDraw.Draw(layer)
    for k, ln in enumerate(lines):
        ld.text((W / 2, y0 + k * PITCH + (PITCH + CAPH) / 2), ln, font=font, fill=fg + (255,), anchor="ms")
    return Image.alpha_composite(im, layer)


def overlay(caption=None, label=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if caption:
        im = draw_box(im, caption, CAP)
    if label:
        im = draw_box(im, [label], LABEL, top=LABEL_TOP)
    return im


def load_plan(edit):
    p = paths(edit)["plan.json"]
    if not p.is_file():
        sys.exit(f"no {p}: run `captions.py plan {edit} --script ...` first")
    return json.loads(p.read_text())


def active(items, t):
    return next((x[2] for x in items if x[0] <= t < x[1]), None)


# ---------- preview ----------

def cmd_preview(a):
    plan = load_plan(a.edit)
    t = a.at
    if t is None:   # the first moment a label and a caption are both up, else the first caption
        t = next((l[0] + 0.5 for l in plan["labels"] if active(plan["captions"], l[0] + 0.5)), plan["captions"][0][0] + 0.2)
    w, h, _, _ = probe(a.edit)
    frame = Path(tempfile.mkstemp(suffix=".png")[1])
    sh("ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(a.edit), "-frames:v", "1", "-vf", f"scale={W}:{H}", str(frame))
    im = Image.open(frame).convert("RGBA")
    frame.unlink()
    im = Image.alpha_composite(im, overlay(active(plan["captions"], t), active(plan["labels"], t)))
    out = Path(a.output) if a.output else paths(a.edit)["preview.png"]
    im.convert("RGB").save(out)
    print(f"{t:.2f}s -> {out}")


# ---------- render ----------

def cmd_render(a):
    plan = load_plan(a.edit)
    w, h, fps, dur = probe(a.edit)
    if abs(w / h - W / H) > 0.01:
        sys.exit(f"{a.edit} is {w}x{h}; the caption layout is for 9:16")
    frames = paths(a.edit)["frames"]
    frames.mkdir(exist_ok=True)
    for old in frames.glob("*.png"):
        old.unlink()
    fr = lambda t: round(t * fps)
    evs = [(c[0], c[1]) for c in plan["captions"]] + [(l[0], l[1]) for l in plan["labels"]]
    end = fr(dur)
    cuts = sorted({0, end} | {min(end, max(0, fr(x))) for e in evs for x in e})
    lst, cache, key = [], {}, None
    for f0, f1 in zip(cuts, cuts[1:]):
        t = (f0 + 0.5) / fps
        cap, lab = active(plan["captions"], t), active(plan["labels"], t)
        key = json.dumps([cap, lab])
        if key not in cache:
            p = frames / f"f{len(cache):04d}.png"
            overlay(cap, lab).save(p)
            cache[key] = p
        lst.append(f"file '{cache[key]}'\nduration {(f1 - f0) / fps:.6f}")
    lst.append(f"file '{cache[key]}'")
    listfile = frames / "list.txt"
    listfile.write_text("\n".join(lst) + "\n")
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + ".tmp" + out.suffix)
    scale = "" if (w, h) == (W, H) else f",scale={w}:{h}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a.edit), "-f", "concat", "-safe", "0", "-i", str(listfile),
                    "-filter_complex", f"[1:v]fps={fps}{scale},format=rgba[c];[0:v][c]overlay=0:0:eof_action=pass[v]",
                    "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "17", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "copy", str(tmp)], check=True)
    tmp.replace(out)
    print(f"-> {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("words"); s.add_argument("edit", type=Path); s.add_argument("--engine", choices=["parakeet", "whisper"], default="parakeet")
    s = sub.add_parser("plan"); s.add_argument("edit", type=Path); s.add_argument("--script", required=True); s.add_argument("--labels")
    s = sub.add_parser("preview"); s.add_argument("edit", type=Path); s.add_argument("--at", type=float); s.add_argument("-o", "--output")
    s = sub.add_parser("render"); s.add_argument("edit", type=Path); s.add_argument("-o", "--output", required=True)
    a = ap.parse_args()
    a.edit = a.edit.resolve()
    {"words": cmd_words, "plan": cmd_plan, "preview": cmd_preview, "render": cmd_render}[a.cmd](a)


if __name__ == "__main__":
    main()
