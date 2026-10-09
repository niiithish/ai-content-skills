#!/usr/bin/env python3
"""Burn captions into finished 9:16 edits in one of the named templates (see `captions.py templates`).

  captions.py templates                                   list the templates
  captions.py words   EDIT                                speech-to-text word times -> captions/<stem>.words.json
  captions.py plan    EDIT -t N [--script S] [--labels L] [--title TEXT] [--fixes F]
                                                          captions with times -> captions/<stem>.plan.json
  captions.py preview EDIT [--at T ...]                   real frames with captions -> captions/<stem>.preview.png
  captions.py render  EDIT [EDIT ...] -o OUT.mp4 [OUT.mp4 ...]
                                                          captioned videos, one at a time, on the GPU when there is one
  captions.py sample  -t N -o OUT.png                     the template on a plain background

Words on screen come from the voiceover script when --script is given (speech-to-text only times them); without
one they come from the transcript, with spoken forms fixed (fixes.txt next to this script, plus --fixes).
The labels file has one "LABEL | first words of the line it starts on" per line.
Work files go in <video>/captions/ (the nearest folder above EDIT with PLAN.md, AGENTS.md or project.conf), never a scratchpad.
Every template keeps its text inside the Meta/TikTok caption safe box: x 40-1050, y 220-1500 on 1080x1920.
"""
import argparse, difflib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "fonts"
W, H = 1080, 1920
SAFE = (40, 220, 1050, 1500)

# Templates. "box": merged white box, up to 2 lines. "line": one line of 1-3 words, no box.
TEMPLATES = {
    "1": dict(name="Boxed (Mysa video-3)", kind="box", font="TikTokSans-SemiBold.ttf", size=54,
              about="#111 TikTok Sans SemiBold 54 on one merged white box, up to 2 lines (~36 chars), bottom at y 1480"),
    "2": dict(name="Bold caps (Mysa video-6)", kind="line", font="TikTokSans-ExtraBold.ttf", size=68, caps=True, punct=True,
              stroke=3, shadow=(0, 4, 7, 190), y=1420, anchor="ms", maxwords=3, target=13, maxchars=24, highlight=None,
              about="ALL CAPS white TikTok Sans ExtraBold 68, 3 px black outline, soft shadow, one line of <=3 words, baseline y 1420"),
    "3": dict(name="Karaoke (Mysa video-10)", kind="line", font="Montserrat-ExtraBold.ttf", size=43, caps=True, punct=False,
              stroke=6, shadow=(3, 3, 0, 128), y=1440, anchor="mm", maxwords=3, target=12, maxchars=18, highlight=(200, 255, 0),
              about="ALL CAPS white Montserrat ExtraBold, 6 px outline, hard shadow, the spoken word lime #C8FF00, <=3 words, centre y 1440, no punctuation"),
    "4": dict(name="Sentence case (Mysa video-7)", kind="line", font="Montserrat-ExtraBold.ttf", size=68, caps=False, punct=True,
              stroke=3, shadow=(0, 4, 7, 190), y=1420, anchor="ms", maxwords=3, target=13, maxchars=24, highlight=None,
              about="Sentence-case white Montserrat ExtraBold 68, 3 px black outline, soft shadow, one line of <=3 words, baseline y 1420"),
}
MAXPX = 900                                          # widest line; the safe box is 1010 wide
GAP = 0.45                                           # a pause this long always ends a caption
WEAK = {"a", "an", "the", "to", "of", "my", "with", "for", "that", "in", "your", "on", "and", "from", "be", "do", "is", "i", "or", "but", "so", "it"}

# template 1 (box) constants: locked over seven rounds on Mysa video-3
PITCH, PADX, R, SS = 74, 20, 18, 4                   # pitch ~1.95x cap height; supersample for smooth corners
BOTTOM, LABEL_TOP, LABEL_SECS = 1480, 245, 3.0
TARGET, MAXLEN, SHORT = 36, 50, 16                   # chars per caption: aim, hard max, orphan threshold
CAP = ((255, 255, 255), (17, 17, 17))
LABEL = ((0xEA, 0x40, 0x40), (255, 255, 255))
TITLE = dict(font="Montserrat-ExtraBold.ttf", size=50, fill=(232, 28, 36), padx=30, pady=20, radius=14)

_fonts = {}


def font(name, size):
    if (name, size) not in _fonts:
        _fonts[name, size] = ImageFont.truetype(str(FONTS / name), size)
    return _fonts[name, size]


BOXFONT = font("TikTokSans-SemiBold.ttf", 54)
CAPH = -BOXFONT.getbbox("H", anchor="ls")[1]
_d = ImageDraw.Draw(Image.new("L", (1, 1)))


def sh(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def probe(edit):
    """width, height, fps, duration of the video stream (not the container: a looped input can make that longer)."""
    info = json.loads(sh("ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,duration"
                         ":format=duration", "-of", "json", str(edit)))
    st = next(s for s in info["streams"] if s["codec_type"] == "video")
    num, den = st["r_frame_rate"].split("/")
    dur = float(st.get("duration") or info["format"]["duration"])
    return int(st["width"]), int(st["height"]), float(num) / float(den), dur


def audio_codec(edit):
    return sh("ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(edit)).strip()


def work_dir(edit):
    for d in [edit.parent, *edit.parent.parents]:
        if any((d / f).is_file() for f in ("PLAN.md", "AGENTS.md", "project.conf")):
            out = d / "captions"
            break
    else:
        out = edit.parent / "captions"
    out.mkdir(parents=True, exist_ok=True)
    return out


def paths(edit):
    d = work_dir(edit)
    return {k: d / f"{edit.stem}.{k}" for k in ("words.json", "plan.json", "preview.png")} | {"frames": d / f"{edit.stem}-frames"}


def template(t):
    """A template number, or a JSON file {"base": "2", ...overrides} for a project-only variant."""
    if t in TEMPLATES:
        return dict(TEMPLATES[t], id=t)
    p = Path(t)
    if p.is_file():
        o = json.loads(p.read_text())
        return dict(TEMPLATES[str(o.pop("base", "2"))], **o, id=str(p))
    sys.exit(f"unknown template {t!r}: use 1-4 or a JSON file")


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


def load_heard(p):
    return [(x["word"], x["start"], x["end"]) if isinstance(x, dict) else tuple(x) for x in json.loads(p.read_text())
            if (x["word"] if isinstance(x, dict) else x[0]).strip()]


# ---------- plan ----------

def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def curly(w):
    w = re.sub(r'([?!])",$', r'\1"', w)    # 'asking "does that hurt?",' reads without the comma
    w = re.sub(r'^"', "“", w)
    w = w.replace('"', "”")
    return w.replace("'", "’")


def load_fixes(extra):
    """'spoken words | written form' per line, longest first. Applied only to transcript words (no --script)."""
    fx = []
    for f in [HERE / "fixes.txt"] + ([Path(extra)] if extra else []):
        for line in f.read_text().splitlines():
            if "|" in line and not line.lstrip().startswith("#"):
                k, v = (x.strip() for x in line.split("|", 1))
                fx.append((k.lower().split(), v))
    return sorted(fx, key=lambda x: -len(x[0]))


def apply_fixes(heard, fixes):
    out, i = [], 0
    while i < len(heard):
        for ks, v in fixes:
            seg = [re.sub(r"[^\w'$%-]", "", x[0]).lower() for x in heard[i:i + len(ks)]]
            if seg == ks:
                tail = re.sub(r"^.*?([.,?!;:]*)$", r"\1", heard[i + len(ks) - 1][0])
                out.append((v + tail, heard[i][1], heard[i + len(ks) - 1][2])); i += len(ks); break
        else:
            out.append(heard[i]); i += 1
    return out


def box_chunks(words):
    """Template 1. Per sentence, split into captions by DP: ~TARGET chars each, max MAXLEN, prefer breaks at commas."""
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


def line_chunks(words, shown, ends, st):
    """One-line templates. Per segment (script line, sentence or pause), DP to ~target chars, <= maxwords and
    MAXPX, preferring breaks at punctuation and never ending on a weak word."""
    out, s = [], 0
    for e in ends:
        best = {s: (0, None)}
        for j in range(s + 1, e + 1):
            cands = []
            for i in range(s, j):
                if i not in best:
                    continue
                txt = " ".join(shown[i:j])
                if (j - i > st["maxwords"] or len(txt) > st["maxchars"] or text_px(txt, st) > MAXPX) and j - i > 1:
                    continue
                c = (len(txt) - st["target"]) ** 2 / 10
                if j < e and not re.search(r'[,;:?!.—]["”]?$', words[j - 1]):
                    c += 25
                if j - i == 1 and e - s > 1 and not re.search(r'[?!]["”]?$', words[i]):
                    c += 35
                if j < e and norm(words[j - 1]) in WEAK:
                    c += 25
                cands.append((best[i][0] + c, i))
            if cands:
                best[j] = min(cands)
        j, parts = e, []
        while j > s:
            i = best[j][1]; parts.append(list(range(i, j))); j = i
        out += parts[::-1]
        s = e
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


def show(w, st):
    """How a word appears on screen in this template."""
    if not st.get("punct", True):
        w = re.sub(r"[.,;:!?\"“”]", "", w)
    w = curly(w)
    return w.upper() if st.get("caps") else w


def cmd_plan(a):
    p = paths(a.edit)
    st = template(a.template)
    if not p["words.json"].is_file():
        sys.exit(f"no {p['words.json']}: run `captions.py words {a.edit}` first")
    heard = load_heard(p["words.json"])
    line_ends = []
    if a.script:
        lines = [l.strip() for l in Path(a.script).read_text().splitlines() if l.strip() and not l.lstrip().startswith("#")]
        words = []
        for l in lines:
            words += l.split(); line_ends.append(len(words))
        start, end, missing = align(words, heard)
    else:
        heard = apply_fixes(heard, load_fixes(a.fixes))
        words = [w[0] for w in heard]
        start, end, missing = [w[1] for w in heard], [w[2] for w in heard], 0
    dur = probe(a.edit)[3]
    if st["kind"] == "box":
        cs = box_chunks(words)
    else:
        shown = [show(w, st) for w in words]
        ends = set(line_ends) | {len(words)}
        ends |= {i + 1 for i, w in enumerate(words) if re.search(r'[.!?]["”]?$', w)}
        ends |= {i + 1 for i in range(len(words) - 1) if start[i + 1] - end[i] > GAP}
        cs = line_chunks(words, shown, sorted(ends), st)
    caps = []
    for n, c in enumerate(cs):
        t0 = start[c[0]]
        t1 = start[cs[n + 1][0]] if n + 1 < len(cs) else min(dur, end[c[-1]] + 0.8)
        if n + 1 < len(cs) and t1 - end[c[-1]] > 0.6:     # a long pause: clear shortly after the speech
            t1 = end[c[-1]] + 0.35
        if st["kind"] == "box":
            caps.append([round(t0, 3), round(t1, 3), [' '.join(curly(w) for w in ln.split()) for ln in two_lines([words[j] for j in c])]])
        else:
            caps.append([round(t0, 3), round(t1, 3), [" ".join(shown[j] for j in c)], [round(start[j], 3) for j in c]])
    labels = []
    for line in (Path(a.labels).read_text().splitlines() if a.labels else []):
        if "|" not in line:
            continue
        label, key = (x.strip() for x in line.split("|", 1))
        k = [norm(x) for x in key.split()]
        hit = next((i for i in range(len(words) - len(k) + 1) if [norm(x) for x in words[i:i + len(k)]] == k), None)
        if hit is None:
            sys.exit(f"label {label!r}: {key!r} is not in the words")
        labels.append([round(start[hit], 3), round(min(dur, start[hit] + LABEL_SECS), 3), label])
    title = None
    if a.title:
        until = a.title_until
        if until is None:   # until the hook's first sentence is said
            until = next((end[i] for i, w in enumerate(words) if re.search(r'[.!?]["”]?$', w)), end[-1]) + 0.3
        title = [0.0, round(until, 3), a.title, a.title_y]
    plan = {"edit": str(a.edit), "duration": dur, "template": st["id"], "style": st, "captions": caps, "labels": labels, "title": title}
    p["plan.json"].write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    for c in caps:
        print(f"{c[0]:6.2f}-{c[1]:6.2f}  " + " / ".join(c[2]))
    for t0, t1, label in labels:
        print(f"{t0:6.2f}-{t1:6.2f}  [{label}]")
    if title:
        print(f"  0.00-{title[1]:6.2f}  title: {title[2]}")
    wide = [c[2] for c in caps if st["kind"] == "line" and text_px(c[2][0], st) > MAXPX]
    if wide:
        print(f"note: {len(wide)} single words wider than {MAXPX}px are shrunk to fit the safe box: {wide[:3]}")
    src = f"{len(words)} script words, {missing} not heard (timed by interpolation)" if a.script else f"{len(words)} transcript words"
    print(f"template {st['id']} ({st['name']}), {src} -> {p['plan.json']}")


# ---------- drawing ----------

def text_px(txt, st):
    return _d.textlength(txt, font=font(st["font"], st["size"])) + 2 * st["stroke"]


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
        half = round((d.textlength(ln, font=BOXFONT) / 2 + PADX) * SS)
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
        ld.text((W / 2, y0 + k * PITCH + (PITCH + CAPH) / 2), ln, font=BOXFONT, fill=fg + (255,), anchor="ms")
    return Image.alpha_composite(im, layer)


def draw_line(im, text, st, active=None):
    """One line, white with a black outline and a shadow; word `active` in the highlight colour."""
    size = st["size"]
    if text_px(text, st) > MAXPX:            # one long word: shrink rather than leave the safe box
        size = int(size * MAXPX / text_px(text, st))
    f, sw = font(st["font"], size), st["stroke"]
    x0 = W / 2 - _d.textlength(text, font=f) / 2
    pos = dict(xy=(x0, st["y"]), anchor="l" + st["anchor"][1])
    dx, dy, blur, alpha = st["shadow"]
    sh_ = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh_).text((x0 + dx, st["y"] + dy), text, font=f, fill=alpha, anchor=pos["anchor"], stroke_width=sw, stroke_fill=alpha)
    if blur:
        sh_ = sh_.filter(ImageFilter.GaussianBlur(blur))
    im.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), sh_)
    d = ImageDraw.Draw(im)
    d.text(text=text, font=f, fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=(0, 0, 0, 255), **pos)
    if active is not None and st.get("highlight"):
        ws = text.split(" ")
        x = x0 + (_d.textlength(" ".join(ws[:active]) + " ", font=f) if active else 0)
        d.text((x, st["y"]), ws[active], font=f, fill=tuple(st["highlight"]) + (255,), anchor=pos["anchor"])
    return im


def draw_title(im, text, y):
    f = font(TITLE["font"], TITLE["size"])
    l, t, r, b = f.getbbox(text)
    w, h = r - l + 2 * TITLE["padx"], b - t + 2 * TITLE["pady"]
    x0, y0 = (W - w) // 2, int(y - h / 2)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x0, y0, x0 + w - 1, y0 + h - 1], TITLE["radius"], fill=TITLE["fill"] + (255,))
    d.text((x0 + TITLE["padx"] - l, y0 + TITLE["pady"] - t), text, font=f, fill="white")
    return im


def state(plan, t):
    """Everything on screen at time t (hashable, so equal states share one overlay PNG)."""
    cap = next((c for c in plan["captions"] if c[0] <= t < c[1]), None)
    k = None
    if cap and len(cap) > 3 and plan["style"].get("highlight"):
        k = max(i for i, s in enumerate(cap[3]) if s <= t or i == 0)
    lab = active(plan["labels"], t)
    ti = plan.get("title")
    return (tuple(cap[2]) if cap else None, k, lab, ti[2] if ti and ti[0] <= t < ti[1] else None)


def overlay(plan, s):
    cap, k, lab, title = s
    st = plan["style"]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if title:
        im = draw_title(im, title, plan["title"][3])
    if cap:
        im = draw_box(im, list(cap), CAP) if st["kind"] == "box" else draw_line(im, cap[0], st, k)
    if lab:
        im = draw_box(im, [lab], LABEL, top=LABEL_TOP)
    return im


def load_plan(edit):
    p = paths(edit)["plan.json"]
    if not p.is_file():
        sys.exit(f"no {p}: run `captions.py plan {edit} -t N` first")
    plan = json.loads(p.read_text())
    plan.setdefault("style", TEMPLATES["1"]); plan.setdefault("title", None)
    return plan


def active(items, t):
    return next((x[2] for x in items if x[0] <= t < x[1]), None)


# ---------- preview ----------

def cmd_preview(a):
    plan = load_plan(a.edit)
    ts = a.at
    if not ts:   # a label (or the title) with a caption, then a caption mid-way
        c = plan["captions"]
        first = next((l[0] + 0.5 for l in plan["labels"] if active(c, l[0] + 0.5)), c[0][0] + 0.2)
        mid = c[len(c) // 2]
        ts = [first, mid[3][-1] + 0.05 if len(mid) > 3 else mid[0] + 0.2]
    shots = []
    for t in ts:
        frame = Path(tempfile.mkstemp(suffix=".png")[1])
        sh("ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(a.edit), "-frames:v", "1", "-vf", f"scale={W}:{H}", str(frame))
        im = Image.open(frame).convert("RGBA")
        frame.unlink()
        shots.append(Image.alpha_composite(im, overlay(plan, state(plan, t))).convert("RGB"))
        print(f"{t:.2f}s  {state(plan, t)}")
    sheet = Image.new("RGB", (W // 2 * len(shots), H // 2), "white")
    for i, s in enumerate(shots):
        sheet.paste(s.resize((W // 2, H // 2), Image.LANCZOS), (i * W // 2, 0))
    out = Path(a.output) if a.output else paths(a.edit)["preview.png"]
    (shots[0] if len(shots) == 1 else sheet).save(out)
    print(f"-> {out}")


def cmd_sample(a):
    st = template(a.template)
    plan = {"style": st, "labels": [], "title": None,
            "captions": [[0, 1, ["Wiping stings every time,", "and you brace to sit down"]]] if st["kind"] == "box"
            else [[0, 1, [" ".join(show(w, st) for w in a.text.split())], [0, 0.1, 0.2][:len(a.text.split())]]]}
    im = Image.new("RGBA", (W, H))
    g = ImageDraw.Draw(im)
    for y in range(H):   # a plain mid-tone gradient so white and black both read
        v = int(70 + 80 * y / H)
        g.line([(0, y), (W, y)], fill=(v, v + 10, v + 25, 255))
    im = Image.alpha_composite(im, overlay(plan, state(plan, 0.15)))
    ImageDraw.Draw(im).rectangle(SAFE, outline=(255, 80, 80, 255), width=3)
    im.convert("RGB").crop((0, 900, W, 1600)).save(a.output)
    print(f"-> {a.output}")


# ---------- render ----------

def encode(inputs, fc, tail):
    """Intel Quick Sync, then VA-API, then x264 veryfast. QSV is ~8x faster than x264 slow here at SSIM 0.99."""
    tries = [["-init_hw_device", "qsv=hw", "-filter_hw_device", "hw", *inputs, "-filter_complex",
              fc + ",format=nv12,hwupload=extra_hw_frames=64[v]", "-c:v", "h264_qsv", "-global_quality", "20", "-preset", "slow"]]
    if os.path.exists("/dev/dri/renderD128"):
        tries.append(["-vaapi_device", "/dev/dri/renderD128", *inputs, "-filter_complex", fc + ",format=nv12,hwupload[v]",
                      "-c:v", "h264_vaapi", "-qp", "20"])
    tries.append([*inputs, "-filter_complex", fc + "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p"])
    for i, t in enumerate(tries):
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", *t, *tail], capture_output=True, text=True)
        if r.returncode == 0:
            return t[t.index("-c:v") + 1]
        if i == len(tries) - 1:
            sys.exit(r.stderr)


def render_one(edit, out):
    plan = load_plan(edit)
    w, h, fps, dur = probe(edit)
    if abs(w / h - W / H) > 0.01:
        sys.exit(f"{edit} is {w}x{h}; the caption layout is for 9:16")
    frames = paths(edit)["frames"]
    frames.mkdir(exist_ok=True)
    for old in frames.glob("*.png"):
        old.unlink()
    fr = lambda t: round(t * fps)
    times = [x for c in plan["captions"] for x in c[:2] + (c[3] if len(c) > 3 and plan["style"].get("highlight") else [])]
    times += [x for l in plan["labels"] for x in l[:2]] + (plan["title"][:2] if plan["title"] else [])
    end = fr(dur)
    cuts = sorted({0, end} | {min(end, max(0, fr(x))) for x in times})
    lst, cache, key = [], {}, None
    for f0, f1 in zip(cuts, cuts[1:]):
        key = state(plan, (f0 + 0.5) / fps)
        if key not in cache:
            p = frames / f"f{len(cache):04d}.png"
            overlay(plan, key).save(p, compress_level=1)
            cache[key] = p
        lst.append(f"file '{cache[key]}'\nduration {(f1 - f0) / fps:.6f}")
    lst.append(f"file '{cache[key]}'")
    listfile = frames / "list.txt"
    listfile.write_text("\n".join(lst) + "\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + ".tmp" + out.suffix)
    scale = "" if (w, h) == (W, H) else f",scale={w}:{h}"
    fc = f"[1:v]fps={fps}{scale},format=rgba[c];[0:v][c]overlay=0:0:eof_action=pass"
    inputs = ["-i", str(edit), "-f", "concat", "-safe", "0", "-i", str(listfile)]
    ac = audio_codec(edit)   # a Resolve .mov carries PCM, which an mp4 can't hold
    aud = ["-c:a", "copy"] if ac in ("aac", "mp3") else ["-c:a", "aac", "-b:a", "192k"]
    tail = ["-map", "[v]", "-map", "0:a?", "-t", f"{dur:.3f}", *aud, "-movflags", "+faststart", str(tmp)]
    enc = encode(inputs, fc, tail)
    tmp.replace(out)
    print(f"-> {out}  ({enc})", flush=True)


def cmd_render(a):
    outs = [Path(o) for o in a.output]
    if len(outs) != len(a.edit):
        sys.exit("give one -o per edit, in the same order")
    for e, o in zip(a.edit, outs):   # one at a time: each encode already fills the GPU/CPU
        render_one(e.resolve(), o)


def cmd_templates(a):
    for k, t in TEMPLATES.items():
        print(f"template-{k}  {t['name']}: {t['about']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("templates")
    s = sub.add_parser("words"); s.add_argument("edit", type=Path); s.add_argument("--engine", choices=["auto", "elevenlabs", "parakeet", "whisper"], default="auto")
    s = sub.add_parser("plan"); s.add_argument("edit", type=Path); s.add_argument("-t", "--template", default="1")
    s.add_argument("--script"); s.add_argument("--labels"); s.add_argument("--fixes", help="extra 'spoken | written' lines (brand names)")
    s.add_argument("--title", help="hook title box, red, from 0 s to the end of the first sentence")
    s.add_argument("--title-until", type=float); s.add_argument("--title-y", type=int, default=960, help="title centre (default 960, a split-screen seam)")
    s = sub.add_parser("preview"); s.add_argument("edit", type=Path); s.add_argument("--at", type=float, nargs="+"); s.add_argument("-o", "--output")
    s = sub.add_parser("render"); s.add_argument("edit", type=Path, nargs="+"); s.add_argument("-o", "--output", nargs="+", required=True)
    s = sub.add_parser("sample"); s.add_argument("-t", "--template", required=True); s.add_argument("-o", "--output", required=True)
    s.add_argument("--text", default="Wiping still stings")
    a = ap.parse_args()
    if a.cmd in ("words", "plan", "preview"):
        a.edit = a.edit.resolve()
    {"templates": cmd_templates, "words": cmd_words, "plan": cmd_plan, "preview": cmd_preview, "render": cmd_render,
     "sample": cmd_sample}[a.cmd](a)


if __name__ == "__main__":
    main()
