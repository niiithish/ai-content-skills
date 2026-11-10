#!/usr/bin/env python3
"""video-23 hook 1: builds edit/hook-1.fcproj, export-ready (user 2026-11-09: "use these 2 [ElevenLabs mp3s] and then
build the project like export ready").

- A1: the ElevenLabs voices (edit/media/voice/{guest,host}-talking-11labs.mp3), one clip per script line, lines back to
  back in script order. Each line's range comes from edit/<speaker>-talking.cuts.json, whose pieces match the mp3s 1:1.
- V1: the talking finals (video only), one piece per cuts.json piece, so every squeezed pause is a real jump cut, and
  also cut at every shot start. Each piece pushes slowly (1.5 %/s); jump cuts inside a shot alternate base and base x1.08.
- V2: inserts (stills pushed 2 %/s, screens, two screen recordings) and the listener half of the split shots
  (both halves cropped to the middle 50 % of the frame: top 10 %, bottom 40 %).
- Shots start on the first word they show (PLAN.md). With captions/hook-1.captions.json present (fc_captions.py plan),
  each shot start moves onto its first caption's planned start frame (rule: pictures change only on caption starts).
- Writes captions/hook-1.blocks.txt (template 1: <=3 words, a shot start always starts a block) unless it exists.
Usage: build_hook1.py [--replace]"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
PROJ = EDIT / "hook-1.fcproj"
CAP = ROOT / "captions"
TPS, FPS = 254016000000, 24
GAIN_DB = 4.0
PUSH = 0.08                       # inserts push 8 %/s (max +25 %), like the reference (user: ours "super boring" at 2 %/s)
HOST_LINES = {"2", "12", "18"}
SPEED = 1.1                       # user 2026-11-09: "increase the speed of the entire thing by 10%"
VOICE = {"guest": EDIT / "media/voice/guest-talking-11labs-110.mp3", "host": EDIT / "media/voice/host-talking-11labs-110.mp3"}
WORDS = {k: EDIT / f"media/voice/{k}-talking-11labs.words.json" for k in VOICE}   # 1.0x times, divided by SPEED
RANGES = {k: dict(v, path=str(EDIT / f"media/talk-110/clip-{k}-110.mp4")) for k, v in json.load(open(EDIT / "ranges.json")).items()}
LISTEN = {"jess": ROOT / "clips/clip-listen-jess/final/clip-listen-jess-v2-1080p.mp4",
          "nora": ROOT / "clips/clip-listen-nora/final/clip-listen-nora-v2-1080p.mp4"}
SC = lambda n, v: ROOT / f"scenes/scene-{n}/scene-{n}-{v}.jpg"
SCR = lambda f: EDIT / "media/screens" / f

# (line, first words as spoken in the ElevenLabs transcript, what is on screen)
#   ("talk", scale)                      speaker full frame
#   ("ins", path)                        insert on V2
#   ("split", listener, sourceIn s, speaker_on_top)
SHOTS = [
    ("1", "i mean", ("talk", 100)),
    ("1", "third", ("ins", SCR("201-focus.png"))),
    ("1", "actually does", ("talk", 112)),
    ("1", "it just", ("split", "jess", 0.0, True)),
    ("2", "a third", ("talk", 100)),
    ("3", "so think", ("talk", 100)),
    ("3", "is regular", ("ins", SC("202", "v1"))),
    ("3", "it gets", ("talk", 120)),
    ("4", "it dries", ("ins", SC("203", "v2"))),
    ("4", "it can", ("ins", SC("204", "v1"))),
    ("4", "and it", ("talk", 100)),
    ("5", "then you", ("talk", 100)),
    ("5", "which is", ("ins", SCR("205-focus.png"))),
    ("6", "so they", ("talk", 100)),
    ("6", "but they", ("talk", 112)),
    ("7", "then theres", ("ins", SCR("206-focus.png"))),
    ("7", "now the", ("talk", 100)),
    ("8", "so its", ("ins", SC("207", "v1"))),
    ("8", "and theres", ("talk", 100)),
    ("8", "like misa", ("ins", SC("208", "v1"))),
    ("8", "for example", ("ins", SC("209", "v1"))),
    ("8", "and theyre", ("ins", SC("210", "v1"))),
    ("9", "and it", ("split", "jess", 1.9, True)),
    ("9", "a new", ("ins", SC("211", "v2"))),
    ("9", "and each", ("talk", 100)),
    ("10", "so with", ("ins", SC("212", "v2"))),
    ("10", "and a", ("ins", SCR("study-focus.png"))),
    ("10", "found healthier", ("talk", 100)),
    ("11", "and there", ("talk", 100)),
    ("11", "nothing is", ("ins", SC("213", "v2"))),
    ("11", "it is", ("talk", 120)),
    ("12", "okay so", ("talk", 130)),
    ("12", "like actually", ("split", "nora", 0.0, False)),
    ("13", "yeah exactly", ("talk", 100)),
    ("13", "two soft", ("ins", SC("214", "v1"))),
    ("13", "no weird", ("talk", 112)),
    ("14", "because now", ("ins", SC("215", "v2"))),
    ("14", "thats easy", ("ins", SC("216a", "v2"))),
    ("14", "to take", ("ins", SC("216b", "v1"))),
    ("14", "without really", ("talk", 100)),
    ("15", "and the", ("talk", 100)),
    ("15", "thats always", ("talk", 112)),
    ("16", "like women", ("talk", 100)),
    ("16", "and then", ("split", "jess", 4.1, True)),
    ("16", "so they", ("talk", 120)),
    ("17", "but this", ("ins", SC("217a", "v1"))),
    ("17", "generation", ("ins", SC("217b", "v1"))),
    ("17", "its basically", ("ins", SC("217c", "v1"))),
    ("17", "the reasons", ("talk", 100)),
    ("18", "okay so", ("talk", 100)),
    ("18", "you said", ("talk", 112)),
    ("19", "okay you", ("talk", 100)),
    ("19", "at", ("ins", SCR("218-type-url.mp4"))),
    ("19", "honestly i", ("ins", SCR("219-pdp-scroll.mp4"))),
    ("19", "actually recommend", ("talk", 120)),
    ("20", "and they", ("talk", 100)),
]
SCRIPT = [l for l in (ROOT / "voiceover/script.md").read_text().splitlines() if l.strip() and not l.startswith("#")]
SCRIPT = [l.replace("third-generation", "third generation") for l in SCRIPT]   # captions: no hyphen, like the reference

norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())


def lines():
    """Ordered [(line id, speaker, mp3 in s, mp3 out s, pieces[(src_in, src_out, mp3 at)], words)]."""
    out = {}
    for spk in ("guest", "host"):
        cuts = json.load(open(EDIT / f"{spk}-talking.cuts.json"))
        words = [dict(w, start=w["start"] / SPEED, end=w["end"] / SPEED) for w in json.load(open(WORDS[spk]))]
        for cid in dict.fromkeys(p[0] for p in cuts):
            if cid.startswith("h"):
                continue
            ps = [(p[1] / SPEED, p[2] / SPEED, p[3] / SPEED) for p in cuts if p[0] == cid]
            a, b = ps[0][2], ps[-1][2] + ps[-1][1] - ps[-1][0]
            ws = [w for w in words if a - 0.1 <= w["start"] < b - 0.1]
            out[cid] = (cid, spk, a, b, ps, ws)
    return [out[str(i)] for i in range(1, 21)]


def find_words(words, key, frm):
    """Index of the first word at or after frm where the joined normalized words start with the key."""
    k = norm(key)
    nw = [norm(w) for w in words]
    for i in range(frm, len(nw)):
        if "".join(nw[i:i + 6]).startswith(k) or "".join(nw[i:i + 6]).replace("mysa", "misa").startswith(k):
            return i
    sys.exit(f"words '{key}' not found after {frm}: {' '.join(nw)}")


def chunk(words):
    """<=3 words a block, no 1-word leftover when avoidable."""
    n = len(words)
    if n <= 3:
        return [words]
    sizes = [3] * (n // 3) + ([n % 3] if n % 3 else [])
    if sizes[-1] == 1:
        sizes[-2:] = [2, 2]
    out, i = [], 0
    for s in sizes:
        out.append(words[i:i + s]); i += s
    return out


def blocks_for(line_text, starts):
    """Split a script line into caption blocks: at each shot start (word index into the line), then at , . ? :"""
    words = line_text.split()
    cuts = sorted(set(starts) | {0})
    out = []
    for a, b in zip(cuts, cuts[1:] + [len(words)]):
        seg, cur = words[a:b], []
        for w in seg:
            cur.append(w)
            if re.search(r"[,.?:]$", w):
                out += chunk(cur); cur = []
        if cur:
            out += chunk(cur)
    return [" ".join(b) for b in out]


def probe_dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


def cli(proj, cmds, save_as=None):
    script = EDIT / ".fc-run.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    args = ["filmcraft-cli", "--compact"] + (["--project", str(proj)] if not save_as else []) + ["run", str(script)]
    args += ["--save-as", str(save_as)] if save_as else ["--save"]
    out = subprocess.run(args, capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    script.unlink()
    return [r.get("result") for r in res]


def main():
    if PROJ.exists() and "--replace" not in sys.argv:
        sys.exit(f"{PROJ.name} exists: pass --replace")
    L = lines()
    # timeline start of each line (frames); mp3 ranges are on the 1/24 grid
    T, t = {}, 0
    for cid, spk, a, b, ps, ws in L:
        T[cid] = t
        t += round((b - a) * FPS)
    end = t
    byline = {l[0]: l for l in L}
    joins = set(T.values())
    edges = sorted({T[cid] + round((at - a) * FPS) + d for cid, spk, a, b, ps, ws in L
                    for d in (0, ) for src_in, src_out, at in ps} |
                   {T[cid] + round((at - a) * FPS) + round((src_out - src_in) * FPS) for cid, spk, a, b, ps, ws in L
                    for src_in, src_out, at in ps})
    # shot starts from the words
    starts, wpos, word_idx = [], {}, []
    for cid, key, what in SHOTS:
        _, spk, a, b, ps, ws = byline[cid]
        i = find_words([w["word"] for w in ws], key, wpos.get(cid, 0))
        wpos[cid] = i + 1
        f = T[cid] if i == 0 else T[cid] + round((ws[i]["start"] - a) * FPS)   # a line's first shot starts on the join
        starts.append(f)
        word_idx.append((cid, i))
    # caption blocks (template 1): shot starts force block starts; word index in Parakeet == script word index? map by count
    blocks_file = CAP / "hook-1.blocks.txt"
    CAP.mkdir(exist_ok=True)
    all_blocks, shot_w, off = [], [], 0      # shot_w: each shot's first word, counted over the whole script
    for n, text in enumerate(SCRIPT, 1):
        sw = text.split()
        idx = []
        for c, key, _ in SHOTS:
            if c == str(n):
                idx.append(find_words(sw, key, idx[-1] + 1 if idx else 0))
        all_blocks += blocks_for(text, idx)
        shot_w += [off + j for j in idx]
        off += len(sw)
    if not blocks_file.exists():             # a draft; edit it by hand, a shot start must stay a block start
        blocks_file.write_text("\n".join(all_blocks) + "\n")
        print(f"wrote {blocks_file.name}: {len(all_blocks)} blocks")
    bstart, acc = [], 0
    for b_ in [l for l in blocks_file.read_text().splitlines() if l.strip()]:
        bstart.append(acc); acc += len(b_.replace(" / ", " ").split())
    assert acc == off, (acc, off)
    missing = [SHOTS[k][1] for k, g in enumerate(shot_w) if g not in bstart]
    assert not missing, f"shot starts not at a block start: {missing}"
    first_block = [bstart.index(g) for g in shot_w]
    capj = CAP / "hook-1.captions.json"
    if capj.exists() and first_block:
        caps = json.load(open(capj))["blocks"]
        snapped = []
        for k, (f, bi) in enumerate(zip(starts, first_block)):
            c = caps[bi]
            cf = c["start"]
            if f in joins:                     # a line's first shot stays on the line join (the caption snaps to the cut)
                snapped.append(f); continue
            near = [e for e in edges if abs(e - cf) <= 6]
            if near:                           # a jump cut next to the caption: use the cut, never a sliver of V1
                cf = min(near, key=lambda e: abs(e - cf))
            if abs(cf - f) > 8:
                print(f"  NOTE shot {k} {SHOTS[k][1]!r}: word frame {f}, caption {bi} '{c.get('text')}' at {cf}")
            snapped.append(cf)
        starts = snapped
        starts[0] = 0
        print("shot starts snapped to caption starts")
    assert starts == sorted(starts) and len(set(starts)) == len(starts), starts
    bounds = list(zip(starts, starts[1:] + [end]))
    for (s, e), sh in zip(bounds, SHOTS):
        assert e - s >= 8, (sh, e - s)

    # --- project
    pics = sorted({str(w[1]) for _, _, w in SHOTS if w[0] == "ins"})
    talk = sorted({RANGES[cid]["path"] for cid in byline})
    paths = [str(VOICE["guest"]), str(VOICE["host"])] + talk + [str(p) for p in LISTEN.values()] + pics
    for p in paths:
        assert Path(p).exists(), p
    if PROJ.exists():
        PROJ.unlink()
    r = cli(None, [{"id": "file.newProject", "params": {"name": "hook-1"}},
                   {"id": "file.import", "params": {"paths": paths}},
                   {"id": "file.newSequence", "params": {"name": "hook-1", "width": 1080, "height": 1920, "fps": FPS,
                                                         "video": 2, "audio": 1}}], save_as=PROJ)
    items = dict(zip(paths, r[1]["items"]))
    place, meta = [], []
    # A1
    for cid, spk, a, b, ps, ws in L:
        place.append({"id": "timeline.place", "params": {"item": items[str(VOICE[spk])], "track": "V1", "audioTrack": "A1",
                                                         "frame": T[cid], "sourceIn": round(a * FPS) * TPS // FPS,
                                                         "duration": round((b - a) * FPS) * TPS // FPS, "insert": False,
                                                         "video": False, "audio": True}})
        meta.append(("audio",))
    # V1: talking pieces cut at shot starts
    shot_of = lambda f: max(k for k, s in enumerate(starts) if s <= f)
    last_shot, alt = None, False
    for cid, spk, a, b, ps, ws in L:
        for src_in, src_out, at in ps:
            f0 = T[cid] + round((at - a) * FPS)
            f1 = T[cid] + round((at + src_out - src_in - a) * FPS)   # rounded ends, so pieces never overlap
            sin = round(src_in * FPS)
            cuts_here = [s for s in starts if f0 < s < f1]
            for x, y in zip([f0] + cuts_here, cuts_here + [f1]):
                k = shot_of(x)
                kind = SHOTS[k][2]
                if k != last_shot:
                    alt = False
                else:
                    alt = not alt
                last_shot = k
                place.append({"id": "timeline.place", "params": {"item": items[RANGES[cid]["path"]], "track": "V1",
                                                                 "frame": x, "sourceIn": (sin + x - f0) * TPS // FPS,
                                                                 "duration": (y - x) * TPS // FPS, "insert": False,
                                                                 "video": True, "audio": False}})
                meta.append(("v1", k, kind, x, y, alt))
    # V2: inserts and listener halves
    for k, ((s, e), (cid, key, what)) in enumerate(zip(bounds, SHOTS)):
        if what[0] == "ins":
            p = what[1]
            d = e - s
            if p.suffix == ".mp4":
                md = int(probe_dur(p) * FPS)
                assert md >= d * 0.5, (p.name, d, md)
            place.append({"id": "timeline.place", "params": {"item": items[str(p)], "track": "V2", "frame": s,
                                                             "duration": min(d, md if p.suffix == ".mp4" else d) * TPS // FPS,
                                                             "insert": False, "video": True, "audio": False}})
            meta.append(("ins", p, s, e, (md if p.suffix == ".mp4" else None)))
        elif what[0] == "split":
            _, who, src, top = what
            d = e - s
            avail = int(7.9 * FPS)
            sin = min(round(src * FPS), avail - d)
            assert sin >= 0, (key, d)
            place.append({"id": "timeline.place", "params": {"item": items[str(LISTEN[who])], "track": "V2", "frame": s,
                                                             "sourceIn": sin * TPS // FPS, "duration": d * TPS // FPS,
                                                             "insert": False, "video": True, "audio": False}})
            meta.append(("listen", not top))       # listener goes in the other half
    res = cli(PROJ, place)
    fx = []
    gain_clips = []

    def half(clip, on_top):
        fx.extend([{"id": "effects.apply", "params": {"clips": [clip], "effect": "crop"}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": 3, "param": "top", "value": 10}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": 3, "param": "bottom", "value": 40}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "position",
                                                         "value": [540, 768 if on_top else 1728]}}])

    for r_, m in zip(res, meta):
        clip = r_["clips"][0]
        if m[0] == "audio":
            gain_clips += r_["clips"]
        elif m[0] == "v1":
            _, k, kind, x, y, alt = m
            if kind[0] == "split":
                half(clip, kind[3])
                continue
            base = kind[1] if kind[0] == "talk" else 100
            s0 = base * (1.08 if alt else 1.0)
            s1 = s0 * (1 + 0.015 * (y - x) / FPS)
            fx += [{"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale",
                                                         "value": round(v, 2), "keyframe": True, "time": f * TPS // FPS}}
                   for v, f in ((s0, x), (s1, y - 1))]
        elif m[0] == "ins":
            _, p, s, e, md = m
            if p.suffix == ".mp4":
                if md < e - s:
                    fx.append({"id": "clip.speedDuration", "params": {"clips": [clip], "speed": round(100 * md / (e - s), 1),
                                                                     "ripple": False}})
                continue                          # 1080x1920 screen recordings: full frame as they are
            if p.suffix == ".png":                # 1080x1920 screens
                sc = 104.0
            else:                                 # 768x1376 stills: fill
                sc = max(1080 / 768, 1920 / 1376) * 100 * 1.05
            fx += [{"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale",
                                                         "value": round(v, 2), "keyframe": True, "time": f * TPS // FPS}}
                   for v, f in ((sc, s), (sc * (1 + min(PUSH * (e - s) / FPS, 0.25)), e - 1))]
        elif m[0] == "listen":
            half(clip, m[1])
    fx.append({"id": "clip.audioGain", "params": {"clips": gain_clips, "mode": "set", "db": GAIN_DB}})
    cli(PROJ, fx)
    for k, ((s, e), (cid, key, what)) in enumerate(zip(bounds, SHOTS)):
        lab = what[1].name if what[0] == "ins" else (f"split {what[1]}" if what[0] == "split" else f"talk {what[1]}%")
        print(f"{k:2d} line {cid:>2} {s / FPS:6.2f}s {(e - s) / FPS:4.2f}s  {key!r:22} {lab}")
    print(f"{PROJ.name}: {len(L)} lines, {end / FPS:.2f} s")


if __name__ == "__main__":
    main()
