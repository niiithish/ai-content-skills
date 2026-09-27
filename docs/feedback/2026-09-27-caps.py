import json, re, sys, difflib, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

P = '/home/nithish/Work/upwork/upwork-calvin/video-3'
S = os.path.dirname(os.path.abspath(__file__))
FONT = f'{P}/font/TikTok_Sans/static/TikTokSans_24pt-SemiBold.ttf'
FONTB = f'{P}/font/TikTok_Sans/static/TikTokSans_28pt-Bold.ttf'
W, H, FPS = 1080, 1920, 30

HOOKS = {
 1: "Here's what your vaginal tissue goes through when you start taking real sea buckthorn oil for eight weeks.",
 2: "Here's what your vagina goes through when you start feeding your vaginal tissue real omega-7 for eight weeks.",
 3: "Here's what your vaginal tissue goes through when you take two real sea buckthorn softgels a day for eight weeks.",
}
body = [l.strip() for l in open(f'{P}/voiceover/script.md') if l.strip() and not l.startswith('#')][1:]

# supers: (label, first words of the script where the section starts)
SUPERS = [("HOURS", "Hours after"), ("DAYS 4–6", "And within four"), ("WEEK 3", "By week three"),
          ("WEEK 6", "By week six"), ("WEEK 8", "And by week eight")]

def norm(t):
    t = t.lower().replace('omega-7', 'omega7').replace('softgels', 'softgels')
    return re.sub(r"[^a-z0-9]", "", t)

def chunks(words):
    """Per sentence, split into captions by DP: ~36 chars each, max 50, prefer breaks at commas."""
    L = lambda i, j: len(' '.join(words[i:j]))
    sents, st = [], 0
    for i, w in enumerate(words):
        if re.search(r'[.!]$', w) or (w.endswith('?') and not w.endswith('?"')):
            sents.append((st, i + 1)); st = i + 1
    if st < len(words): sents.append((st, len(words)))
    out = []
    for s, e in sents:
        best = {s: (0, None)}
        for j in range(s + 1, e + 1):
            cands = []
            for i in range(s, j):
                if i not in best: continue
                n = L(i, j)
                if n > 50: continue
                c = (n - 36) ** 2 / 12
                if j < e and not re.search(r'[,;]["\u201d]?$', words[j - 1]): c += 20
                if n < 16 and not (i == s and j == e): c += 60
                cands.append((best[i][0] + c, i))
            if cands: best[j] = min(cands)
        j, parts = e, []
        while j > s:
            i = best[j][1]; parts.append(list(range(i, j))); j = i
        out += parts[::-1]
    return out

def two_lines(ws):
    txt = ' '.join(ws)
    if len(txt) <= 16 or len(ws) < 3:
        return [txt]
    best = min(range(1, len(ws)), key=lambda k: max(len(' '.join(ws[:k])), len(' '.join(ws[k:]))) * 10
               + (len(' '.join(ws[:k])) < len(' '.join(ws[k:]))))
    return [' '.join(ws[:best]), ' '.join(ws[best:])]

font = ImageFont.truetype(FONT, 54)
fontb = ImageFont.truetype(FONTB, 96)

# cap height; each line box pads cap top and baseline equally (matches the TikTok refs)
CAPH = -font.getbbox('H', anchor='ls')[1]
SS = 4  # supersample for smooth corners

def _corner(m, cx, cy, dx, dy, r, convex):
    """Round one corner of the union mask. (dx, dy) points into the empty quadrant."""
    if r < 1: return
    p = Image.new('L', (r, r), 0 if convex else 255)
    if convex:
        px, py = (0 if dx > 0 else r), (0 if dy > 0 else r)
        ox, oy = (cx - r if dx > 0 else cx), (cy - r if dy > 0 else cy)
        ImageDraw.Draw(p).ellipse((px - r, py - r, px + r, py + r), fill=255)
    else:
        px, py = (r if dx > 0 else 0), (r if dy > 0 else 0)
        ox, oy = (cx if dx > 0 else cx - r), (cy if dy > 0 else cy - r)
        ImageDraw.Draw(p).ellipse((px - r, py - r, px + r, py + r), fill=0)
    m.paste(p, (ox, oy))

def render_caption(lines, path, top=None, bottom=1480, bg=(255, 255, 255), fg=(17, 17, 17)):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lh, padx, R = 74, 20, 18   # pitch ~1.95x cap height
    y0 = top if top is not None else bottom - lh * len(lines)
    # one merged shape: stacked line boxes, convex corners rounded, concave joins filleted
    m = Image.new('L', (W * SS, H * SS), 0); md = ImageDraw.Draw(m)
    xs = []
    for k, ln in enumerate(lines):
        half = round((d.textlength(ln, font=font) / 2 + padx) * SS)
        xs.append((W * SS // 2 - half, W * SS // 2 + half))
    ys = [(y0 + k * lh) * SS for k in range(len(lines) + 1)]
    for k, (xa, xb) in enumerate(xs):
        md.rectangle((xa, ys[k], xb - 1, ys[k + 1] - 1), fill=255)
    r = R * SS
    n = len(xs)
    for s in (1, -1):  # right side, then left side (mirrored)
        edge = lambda k: xs[k][1] if s > 0 else xs[k][0]
        _corner(m, edge(0), ys[0], s, -1, r, True)
        _corner(m, edge(n - 1), ys[n], s, 1, r, True)
        for k in range(n - 1):
            a_, b_ = edge(k), edge(k + 1)
            dd = abs(a_ - b_)
            rr = min(r, dd // 2)
            if rr < SS: continue
            if (a_ - b_) * s > 0:   # upper line sticks out
                _corner(m, a_, ys[k + 1], s, 1, rr, True)
                _corner(m, b_, ys[k + 1], s, 1, rr, False)
            else:                   # lower line sticks out
                _corner(m, b_, ys[k + 1], s, -1, rr, True)
                _corner(m, a_, ys[k + 1], s, -1, rr, False)
    m = m.resize((W, H), Image.LANCZOS)
    im.paste(Image.new('RGBA', (W, H), bg + (255,)), (0, 0), m)
    d = ImageDraw.Draw(im)
    for k, ln in enumerate(lines):
        d.text((W / 2, y0 + k * lh + (lh + CAPH) / 2), ln, font=font, fill=fg + (255,), anchor='ms')
    im.save(path)

def render_super(label, path):
    render_caption([label], path, top=245, bg=(0xEA, 0x40, 0x40), fg=(255, 255, 255))

def build(h):
    words = (HOOKS[h] + ' ' + ' '.join(body)).split()
    wt = json.load(open(f'{S}/w{h}.json'))
    # expand whisper tokens that are split ("soft gels", "omega -7") by aligning on normalized char streams
    sn = [norm(w) for w in words]
    tn = [norm(w[0]) for w in wt]
    # char-level alignment
    sc, sidx = [], []
    for i, t in enumerate(sn):
        for ch in t: sc.append(ch); sidx.append(i)
    tc, tidx = [], []
    for i, t in enumerate(tn):
        for ch in t: tc.append(ch); tidx.append(i)
    sm = difflib.SequenceMatcher(None, sc, tc, autojunk=False)
    start = [None] * len(words); endt = [None] * len(words)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            si, ti = sidx[a + k], tidx[b + k]
            if start[si] is None: start[si] = wt[ti][1]
            endt[si] = wt[ti][2]
    # interpolate gaps
    for arr in (start, endt):
        for i in range(len(arr)):
            if arr[i] is None:
                j = i
                while j < len(arr) and arr[j] is None: j += 1
                a = arr[i - 1] if i else 0.0
                b = arr[j] if j < len(arr) else a + 0.3
                for k in range(i, j): arr[k] = a + (b - a) * (k - i + 1) / (j - i + 1)
    miss = sum(1 for i in range(len(words)) if start[i] is None)
    cs = chunks(words)
    dur = float(os.popen(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{P}/my-edits/hook-{h}.mp4"').read())
    ev = []
    for n, c in enumerate(cs):
        t0 = start[c[0]]
        t1 = start[cs[n + 1][0]] if n + 1 < len(cs) else min(dur, endt[c[-1]] + 0.8)
        if n + 1 < len(cs) and t1 - endt[c[-1]] > 0.6:  # long pause: clear shortly after speech
            t1 = endt[c[-1]] + 0.35
        ev.append((t0, t1, [x.replace('?",', '?\u201d').replace('"', '\u201c').replace("'", '\u2019') for x in two_lines([words[j] for j in c])]))
    sup = []
    joined = [w.lower() for w in words]
    for label, key in SUPERS:
        k = key.lower().split()
        for i in range(len(words) - len(k)):
            if [re.sub(r'[^a-z]', '', x) for x in joined[i:i + len(k)]] == k:
                sup.append((start[i], start[i] + 3.0, label)); break
    return ev, sup, dur

if __name__ == '__main__':
    h = int(sys.argv[1])
    ev, sup, dur = build(h)
    json.dump({'captions': ev, 'supers': sup, 'dur': dur}, open(f'{S}/ev{h}.json', 'w'), indent=1)
    for e in ev: print(f'{e[0]:6.2f}-{e[1]:6.2f}  ' + ' / '.join(e[2]))
    print(sup)

def track(h):
    """Composite caption+super PNG per interval and a concat list."""
    ev, sup, dur = build(h)
    d = f'{S}/trk{h}'; os.makedirs(d, exist_ok=True)
    evs = [(a, b, ('c', l)) for a, b, l in ev] + [(a, b, ('s', l)) for a, b, l in sup]
    fr = lambda t: round(t * FPS)
    cuts = sorted({0, fr(dur)} | {fr(a) for a, b, _ in evs} | {fr(b) for a, b, _ in evs})
    cuts = [c for c in cuts if 0 <= c <= fr(dur)]
    lst, cache = [], {}
    for i in range(len(cuts) - 1):
        f0, f1 = cuts[i], cuts[i + 1]
        act = [x for a, b, x in evs if fr(a) <= f0 and fr(b) >= f1]
        key = json.dumps(act)
        if key not in cache:
            p = f'{d}/f{len(cache):04d}.png'
            im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            for kind, v in act:
                render_caption(v, f'{d}/tmp.png') if kind == 'c' else render_super(v, f'{d}/tmp.png')
                im = Image.alpha_composite(im, Image.open(f'{d}/tmp.png'))
            im.save(p); cache[key] = p
        lst.append(f"file '{cache[key]}'\nduration {(f1 - f0) / FPS:.6f}")
    lst.append(f"file '{cache[key]}'")
    open(f'{d}/list.txt', 'w').write('\n'.join(lst) + '\n')
    return d, dur
