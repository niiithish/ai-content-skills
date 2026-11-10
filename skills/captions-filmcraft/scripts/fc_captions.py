#!/usr/bin/env python3
"""Captions as text clips inside a FilmCraft project, each one starting on the frame its phrase is spoken.

  fc_captions.py words  PROJECT [--vo A1] [--fast]    the voiceover track as WAV, then word times from Parakeet and
                                                    faster-whisper (Parakeet only with --fast) -> captions/<stem>.vo.wav, .pk.json, .fw.json
  fc_captions.py plan   PROJECT [--script S] [--fixes F] [--hide 0.4]
                                                    caption blocks with start and end frames -> captions/<stem>.captions.json
  fc_captions.py build  PROJECT [-t 4] [--track V3] text clips into the project (backup, temp save, verify, copy in)
  fc_captions.py check  PROJECT [--n 8]             frames just before and on caption starts -> captions/<stem>.check.png
  fc_captions.py export PROJECT -o OUT.mp4          H.264 at the delivery settings, from FilmCraft itself

Blocks are one caption per line in captions/<stem>.blocks.txt. `plan --script` writes a first split there (whole
phrases, at most 4 words); read and fix it, then run plan again. Timing never comes from one engine alone:
  - after a pause, a caption starts on the frame where the voice rises out of silence (the transcribe skill's
    pauses.py: a threshold set from this recording's own noise floor and speech level, since AI clips carry room
    tone above a fixed -40 dB);
  - mid-sentence, at Parakeet's word start plus its measured lead on this recording, averaged with faster-whisper
    (unless words ran with --fast), and moved to the end of a real pause or to the loudness dip just before it;
  - a sentence's last word, where Parakeet runs late, on the last rise out of a dip before Parakeet's start;
  - every picture cut (V1) starts a caption on that exact frame; a cut more than 2 frames off its voice is reported.
  - then every caption is checked against the waveform: one shown over silence, late on its voice or left up over a
    pause is fixed, and anything unclear is printed as a NOTE.
Captions run back to back through short pauses. Where the voice stops for --hide seconds or more (default 0.4),
the caption ends 2 frames after the last word and the screen is clear until the voice comes back.
Work files go in <video>/captions/ (the nearest folder above the project with PLAN.md, AGENTS.md or project.conf).
"""
import argparse, datetime, difflib, json, math, os, re, shutil, statistics, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _d in (HERE.parent.parent / "transcribe" / "scripts", HERE.parent.parent / "filmcraft" / "scripts",
           Path.home() / ".claude/skills/transcribe/scripts", Path.home() / ".claude/skills/filmcraft/scripts"):
    sys.path.insert(0, str(_d))
TAIL = 2  # frames a caption stays up after the last word before a pause
EARLY_POP = 3  # frames a one/two-word pop caption leads its voice (matched to the raw-Parakeet demo, 2026-11-07)
MIN_POP = 5  # frames: the shortest a pop caption gets from the lead (template 7 merges anything shorter)
MIN_GAP = 2  # a mid-phrase caption's start is never snapped closer than this to the caption before it
TPS = 254016000000                                   # FilmCraft ticks per second
SAFE_Y = 1500                                        # Meta/TikTok caption safe box bottom on 1080x1920
MAXWORDS = 4
MAX_W = 860  # px: widest caption line on 1080, so 110 px stays clear each side (Max video-2: wide lines ran off the frame)

# One-line caption templates, as FilmCraft text. Fonts must be installed for fontconfig.
SHADOW = {"shadow": True, "shadow_angle": 90, "shadow_distance": 4, "shadow_blur": 7, "shadow_opacity": 75,
          "shadow_color": "#000000"}
STYLES = {
    # TikTok auto-caption look on a podcast clip (Mysa video-23 reference DCT#28, 2026-11-09). Measured on the
    # reference at 720x1280 and scaled x1.5: ALL CAPS white TikTok Sans SemiBold (stem 6.08 px at 720 = SemiBold),
    # cap height 49.5 px (size 70), no punctuation, on a solid black box per line, radius 10, 103.5 px tall, box
    # 499 px wide for "SO IT'S NANO" (magick width + 22 px a side). One line: box centre y 1413 (baseline 1438).
    # Over ~800 px of text ("THE SECOND GENERATION") it wraps greedily, filling line 1 first: baselines 1396 and
    # 1479, the two boxes overlap ~21 px, the block stays centred on 1413. 1-3 words a page, chunked by count, back
    # to back (plan --max-words 3). In split two-shots the reference moves captions onto the seam (centre y 959).
    "1": dict(about="ALL CAPS white TikTok Sans SemiBold 70 on a solid black rounded box per line, centred y 1413, "
                    "no punctuation, 1-3 words a page (plan --max-words 3), wraps over 900 px into two balanced lines, never one short word alone",
              font="TikTok Sans 24pt", fontStyle="SemiBold", size=70, caps=True, bare=True, file="TikTokSans-SemiBold.ttf",
              lines=[1396, 1479], single=1438, wrap_px=900, boxes=dict(pad=[22, 6], radius=10, color="#000000"),
              props={"align": "center", "fill_color": "#ffffff", "stroke": False, "shadow": False,
                     "background": False, "position": [540, 1438]}),
    "4": dict(about="Sentence-case white Montserrat ExtraBold 68, 3 px black outline, soft shadow, baseline y 1420",
              font="Montserrat", fontStyle="ExtraBold", size=68, caps=False, file="Montserrat-ExtraBold.ttf",
              props={"align": "center", "fill_color": "#ffffff", "stroke": True, "stroke_width": 3,
                     "stroke_color": "#000000", **SHADOW, "position": [540, 1420]}),
    "2": dict(about="ALL CAPS white TikTok Sans ExtraBold 68, 3 px black outline, soft shadow, baseline y 1420",
              font="TikTok Sans", fontStyle="ExtraBold", size=68, caps=True, file="TikTokSans-ExtraBold.ttf",
              props={"align": "center", "fill_color": "#ffffff", "stroke": True, "stroke_width": 3,
                     "stroke_color": "#000000", **SHADOW, "position": [540, 1420]}),
    # TikTok native-caption look (user's reference frame, Mysa video-14, 2026-10-23), measured at 1080x1920:
    # "I was 47." 210 px wide, cap height 35 px (size 50), baseline y ~1408, thin dark outline + soft dark glow.
    # Raised to 64 for the 45+ women audience (user, 2026-10-23).
    "3": dict(about="Sentence-case white TikTok Sans SemiBold 64, 2 px black outline, soft glow, baseline y 1408",
              font="TikTok Sans 24pt", fontStyle="SemiBold", size=64, caps=False, file="TikTokSans-SemiBold.ttf",
              props={"align": "center", "fill_color": "#ffffff", "stroke": True, "stroke_width": 2,
                     "stroke_color": "#000000", "shadow": True, "shadow_angle": 90, "shadow_distance": 0,
                     "shadow_blur": 9, "shadow_opacity": 90, "shadow_color": "#000000", "position": [540, 1409]}),
    # Storybook-explainer look (Alaria video-4 reference ad): small, 1-2 words, just below mid-frame.
    # Measured on the reference at 1080x1920: text ~210 px wide for "center of", baseline y ~1113, thin dark outline.
    "5": dict(about="Sentence-case white TikTok Sans SemiBold 50, 2 px black outline, soft shadow, baseline y 1113, "
                    "1-2 words a caption (plan --max-words 2)",
              font="TikTok Sans 24pt", fontStyle="SemiBold", size=50, caps=False, file="TikTokSans-SemiBold.ttf",
              props={"align": "center", "fill_color": "#ffffff", "stroke": True, "stroke_width": 2,
                     "stroke_color": "#000000", "shadow": True, "shadow_angle": 90, "shadow_distance": 0,
                     "shadow_blur": 9, "shadow_opacity": 90, "shadow_color": "#000000", "position": [540, 1116]}),
    # Doctor-explainer look (Aleo video-3 reference ad, 2026-10-24): black text on white rounded boxes, two lines,
    # just above the box insert. Measured on the reference at 1080x1920: size 58 ("practitioner with a background"
    # 810 px wide), baselines 74 apart, each line's box 17 px wider than its text on each side and about 89 px tall
    # (7 px past the font's ascent and descent), radius 16. The boxes are shape layers behind both text layers, so
    # they merge into one shape and never cover a letter; the text's own background padded both ways alike and came
    # out 103 px tall ("too big, the gap is wider", user 2026-10-24).
    # A block's line break is " / " in blocks.txt ("1 to 2 weeks / as the biofilm breaks down"); without one, build
    # splits a block of 3+ words in two at the most even break.
    "6": dict(about="Sentence-case black TikTok Sans SemiBold 58 on white rounded boxes merged behind both lines, "
                    "baselines y 1098 and 1173 (plan --max-words 7, ' / ' marks the line break)",
              font="TikTok Sans 24pt", fontStyle="SemiBold", size=58, caps=False, file="TikTokSans-SemiBold.ttf",
              lines=[1098, 1173], boxes=dict(pad=[17, 7], radius=16, color="#ffffff"),
              props={"align": "center", "fill_color": "#000000", "stroke": False, "shadow": False,
                     "background": False, "position": [540, 1136]}),
    # Word-by-word podcast-clip look (Aleo video-4 reference ad, 2026-10-27). Measured on the reference at 720x1280,
    # scaled to 1080x1920: cap height 60 px ("VERY" 233 px wide), baseline y 1306, a thin black outline and a hard
    # black drop shadow down-right with no blur. One word a caption, two when a short word leads ("OR YOUR",
    # "THE BODY", "IT ISN'T"), the same spot on every shot. Blocks written by hand in blocks.txt (plan --max-words 3).
    "7": dict(about="ALL CAPS white Montserrat ExtraBold 85, 3 px black outline, hard shadow down-right, baseline "
                    "y 1306, no punctuation, 1-2 words a caption (plan --max-words 3)",
              font="Montserrat", fontStyle="ExtraBold", size=85, caps=True, bare=True, file="Montserrat-ExtraBold.ttf",
              props={"align": "center", "fill_color": "#ffffff", "stroke": True, "stroke_width": 3,
                     "stroke_color": "#000000", "shadow": True, "shadow_angle": 45, "shadow_distance": 6,
                     "shadow_blur": 0, "shadow_opacity": 100, "shadow_color": "#000000", "position": [540, 1306]}),
    # Doctor-explainer with TikTok-native italic captions (Mysa video-17 reference ad, 2026-10-30). Measured on the
    # reference at 720x1280, scaled to 1080x1920: "STARTING TO SHIFT" 585 px wide, cap height 42 px, baseline y 1377
    # (on the doctor's chest), slanted, thin black outline and a soft dark shadow, no punctuation. The hook line is
    # lowercase ("what dies off", "in your gut"), everything after it ALL CAPS: build --caps-from <first cut, s>.
    "8": dict(about="ALL CAPS white TikTok Sans SemiBold 62 slanted, 2 px black outline, soft shadow, baseline "
                    "y 1377, no punctuation; lowercase before --caps-from",
              font="TikTok Sans 24pt", fontStyle="SemiBold", size=62, caps=True, bare=True, file="TikTokSans-SemiBold.ttf",
              props={"align": "center", "fill_color": "#ffffff", "faux_italic": True, "stroke": True,
                     "stroke_width": 2, "stroke_color": "#000000", "shadow": True, "shadow_angle": 90,
                     "shadow_distance": 2, "shadow_blur": 8, "shadow_opacity": 85, "shadow_color": "#000000",
                     "position": [540, 1377]}),
    # Claymation explainer, karaoke by line (Mysa video-18 reference ad DCT#22, 2026-11-02). Measured on the reference
    # at 720x1280, scaled to 1080x1920: two lines centred about 70% down, baselines y 1346 and 1415, "gut lining
    # while" 354 px wide in the bold weight (size 43, raised to 46); all lowercase, no outline, a soft dark shadow.
    # Captions come in pairs, one phrase a line: the phrase being spoken is Montserrat Bold white, its partner line
    # Montserrat Light white at 80% opacity. Each caption is one clip with both lines, so the bold moves down to the
    # second line on that phrase's first word. A pair breaks where the captions clear in a pause.
    "9": dict(about="Pairs of lowercase lines, the spoken one white Montserrat Bold 46, the other Montserrat Light at "
                    "80% opacity, baselines y 1346 and 1415, soft shadow (plan --max-words 4)",
              font="Montserrat", fontStyle="Bold", size=46, caps=False, lower=True, file="Montserrat-Bold.ttf",
              pair=dict(lines=[1346, 1415], fontStyle="Light", file="Montserrat-Light.ttf", opacity=80),
              props={"align": "center", "fill_color": "#ffffff", "stroke": False, "shadow": True,
                     "shadow_angle": 90, "shadow_distance": 2, "shadow_blur": 8, "shadow_opacity": 70,
                     "shadow_color": "#000000", "position": [540, 1415]}),
}
# Meta-ready, same as the filmcraft skill's fc.py export: 2 min ~ 90 MB, ~2.4x faster than 40 Mb/s 2-pass max quality
EXPORT = {"bitrateKbps": 6000, "maxBitrateKbps": 9000, "bitrateMode": "vbr1Pass", "gpuRendering": "auto",
          "h264Profile": "high", "audio": {"bitrate_kbps": 192, "bits": 16, "channels": 2, "codec": "aac",
                                           "flac_level": 5, "float": False, "sample_rate": 48000}}

# Phrase splitting: never end a block on these, and prefer to start one on the second set.
WEAK_END = {"a", "an", "the", "to", "of", "my", "her", "his", "your", "their", "our", "with", "for", "that", "in",
            "on", "and", "from", "or", "but", "so", "is", "was", "she", "he", "i", "it", "got", "get"}
STARTERS = {"and", "but", "or", "so", "then", "while", "with", "for", "in", "of", "past", "to", "because", "when",
            "even", "until", "after", "before", "without", "like", "than", "that", "who", "which"}
NUM = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                  "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
NUM.update({w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())})


def die(msg):
    sys.exit(f"fc_captions: {msg}")


# ---------- FilmCraft ----------

def cli(project, cmds):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(json.dumps(c, ensure_ascii=False) for c in cmds) + "\n")
    out = subprocess.run(["filmcraft-cli", "--project", str(project), "run", f.name], capture_output=True, text=True)
    os.unlink(f.name)
    lines = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [l for l in lines if not l.get("ok")]
    if out.returncode or bad or len(lines) != len(cmds):
        die(f"filmcraft-cli run failed: rc={out.returncode} {bad[:2]} {out.stderr[-400:]}")
    return lines


def seq(project):
    out = subprocess.run(["filmcraft-cli", "--project", str(project), "inspect", "sequence"], capture_output=True, text=True)
    if out.returncode:
        die(f"inspect failed: {out.stderr[-300:]}")
    return json.loads(out.stdout)


def fps_of(s):
    r = s["settings"]["frame_rate"]
    return r["num"] / r["den"]


def tpf(s):
    r = s["settings"]["frame_rate"]
    return TPS * r["den"] // r["num"]


def is_text(item):
    return any(e["effect"] == "graphic_text" for e in item.get("effects", []))


def caption_track(s, plan):
    """Index of the text-only track (above V1) holding most of the plan's caption texts, or None."""
    want = {t.strip().lower() for b in plan["blocks"] for t in (b["text"], b["text"].split(" / ")[0])}
    best, score = None, 0
    for v, tr in enumerate(s["video"][1:], 1):
        items = tr["items"]
        if not items or not all(is_text(i) for i in items):
            continue
        hit = sum(i.get("name", "").strip().lower() in want for i in items)
        if hit >= max(3, len(items) // 2) and hit > score:
            best, score = v, hit
    top = len(s["video"]) - 1   # re-blocked captions match no old name; the top text-only track is still the captions
    if best is None and top > 0 and s["video"][top]["items"] and all(is_text(i) for i in s["video"][top]["items"]):
        best = top
    return best


def zoom_of(c):
    m = next((e["params"].get("scale") for e in c.get("effects", []) if e["effect"] == "motion"), None)
    return str(m["value"]) if m and not m.get("keyframes") else None


def cuts_of(s):
    """V1 cuts the viewer sees. A join where the same media runs on (a razor around a sped-up pause) is not one,
    unless the zoom changes there: a master with its jump cuts baked in is razored at each one and zoomed 100/108%
    (calvin video-15, 2026-10-26), and those are cuts the viewer sees."""
    v1 = sorted(s["video"][0]["items"], key=lambda c: c["startFrame"])
    half = v1[0]["duration"] // max(1, v1[0]["durationFrames"]) // 2 if v1 else 0
    return sorted(b["startFrame"] for a, b in zip(v1, v1[1:])
                  if b["item"] != a["item"] or abs(b["sourceIn"] - a["sourceOut"]) > half or zoom_of(a) != zoom_of(b))


def app_running():
    ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True).stdout.splitlines()
    return any(re.match(r"^/opt/filmcraft/bin/filmcraft( |$)", l) for l in ps)


# ---------- files ----------

def workdir(project):
    p = Path(project).resolve()
    for d in p.parents:
        if any((d / n).exists() for n in ("PLAN.md", "AGENTS.md", "project.conf")):
            out = d / "captions"
            break
    else:
        out = p.parent / "captions"
    out.mkdir(exist_ok=True)
    return out


def paths(project):
    w, stem = workdir(project), Path(project).stem
    return {k: w / f"{stem}.{k}" for k in ("vo.wav", "pk.json", "fw.json", "blocks.txt", "captions.json", "check.png")}


# ---------- words ----------

def cmd_words(a):
    P = paths(a.project)
    import fc
    fc.save_live(a.project)  # the export below reads the saved file
    s = seq(a.project)
    n = len(s["audio"])
    keep = int(a.vo.lstrip("Aa"))
    # delete every other audio track (highest first so the names don't shift), export, never save
    cmds = [{"id": "sequence.deleteTrack", "params": {"track": f"A{k}"}} for k in range(n, 0, -1) if k != keep]
    cmds.append({"id": "file.exportMedia", "params": {"path": str(P["vo.wav"]), "format": "wav", "wait": True}})
    cli(a.project, cmds)
    print(f"voiceover ({a.vo}) -> {P['vo.wav']}")
    sys.path.insert(0, str(HERE.parent.parent / "transcribe" / "scripts"))
    sys.path.insert(0, str(Path.home() / ".claude/skills/transcribe/scripts"))
    import transcribe as T
    pk = T.words(str(P["vo.wav"]), verify=True)   # Vulkan GPU, re-checked on the CPU; CPU engines if it fails
    json.dump(pk, open(P["pk.json"], "w"))
    print(f"Parakeet: {len(pk)} words -> {P['pk.json']}")
    if a.fast:   # whisper stays on by default: without it 6 of 27 one-word captions moved 3-7 frames off (2026-11-07)
        P["fw.json"].unlink(missing_ok=True)  # a stale one from an older voiceover must not be averaged in
        return
    try:
        fw = T.whisper_file(str(P["vo.wav"]))   # medium.en if downloaded, else small.en; runs in the transcribe venv
    except Exception as e:   # the second opinion is optional: carry on with Parakeet alone, as --fast does
        print(f"faster-whisper failed ({e}); continuing with Parakeet only", file=sys.stderr)
        P["fw.json"].unlink(missing_ok=True)
        return
    json.dump(fw, open(P["fw.json"], "w"))
    print(f"faster-whisper: {len(fw)} words -> {P['fw.json']}")


# ---------- text ----------

def load_fixes(path):
    fx = {}
    for line in open(path) if path else []:
        if "|" in line and not line.lstrip().startswith("#"):
            k, v = (x.strip().lower() for x in line.split("|", 1))
            fx[re.sub(r"[^a-z0-9]", "", k)] = re.sub(r"[^a-z0-9]", "", v)
    return fx


def norm(w, fx={}):
    x = re.sub(r"[^a-z0-9]", "", w.lower())
    return fx.get(x, x)


def asr_tokens(words, fx):
    """ASR words -> (normalised token, start), with spelled-out numbers joined into digits."""
    out, i = [], 0
    while i < len(words):
        w, s = words[i][0], words[i][1]
        parts = [p for p in re.split(r"[-\s]", w.lower()) if p]
        if parts and all(re.sub(r"[^a-z]", "", p) in NUM for p in parts):
            v = sum(NUM[re.sub(r"[^a-z]", "", p)] for p in parts)
            if v >= 20 and v % 10 == 0 and i + 1 < len(words) and re.sub(r"[^a-z]", "", words[i + 1][0].lower()) in NUM \
                    and NUM[re.sub(r"[^a-z]", "", words[i + 1][0].lower())] < 10:
                v += NUM[re.sub(r"[^a-z]", "", words[i + 1][0].lower())]; i += 1
            out.append((str(v), s))
        elif norm(w, fx) not in ("", "percent"):
            out.append((norm(w, fx), s))
        i += 1
    return out


def split_phrases(text):
    """Script -> blocks: break at punctuation, then cut long clauses into whole phrases of at most 4 words."""
    blocks, clauses = [], []
    for clause in re.findall(r"[^,.!?;:—–]+[,.!?;:—–]*", text.replace("\n", " ")):
        words = clause.split()
        if words and clauses and len(clauses[-1]) == 1 and not re.search(r"[.!?]$", clauses[-1][0]):
            clauses[-1] += words          # "Then," joins the clause after it
        elif words:
            clauses.append(words)
    for words in clauses:
        n = len(words)
        best = [0.0] + [1e9] * n
        back = [0] * (n + 1)
        for j in range(1, n + 1):
            for k in range(max(0, j - MAXWORDS), j):
                ln = j - k
                cost = best[k] + abs(ln - 3) * 0.6 + (3 if ln == 1 else 0)
                if j < n and norm(words[j - 1]) in WEAK_END:
                    cost += 4
                if j < n and norm(words[j]) not in STARTERS:
                    cost += 2
                if cost < best[j]:
                    best[j], back[j] = cost, k
        cut, j = [], n
        while j:
            cut.append((back[j], j)); j = back[j]
        blocks += [" ".join(words[k:j]) for k, j in reversed(cut)]
    return blocks


# ---------- timing ----------

def pcm16k(path):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def frame_db(x, fr, fps):
    import numpy as np
    a, b = int(fr / fps * 16000), int((fr + 1) / fps * 16000)
    seg = x[a:b]
    return float(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)) if len(seg) else -120.0


def closure_onsets(x, t0, t1):
    """Times in [t0, t1) where the voice comes out of a near-silence of 10-30 ms (a stop consonant's closure, the
    gap between two words): on 10 ms steps, at least 10 dB under the 50 ms before and 15 dB under the 20 ms after.
    A 33 ms video frame blurs these: "trick" showed only a 2 dB rise at frame 318-319, but -64 dB at 10.63 s."""
    import numpy as np
    def db(i):
        seg = x[i * 160:i * 160 + 320]
        return float(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)) if len(seg) else -120.0
    out = []
    for i in range(max(5, int(t0 * 100) - 1), int(t1 * 100) - 1):
        v = db(i)
        if max(db(i + 1), db(i + 2)) - v >= 15 and max(db(j) for j in range(i - 5, i)) - v >= 10:
            out.append((i + 1) / 100)
    return out


_QUIET = {}


def silent(x, fr, fps):
    """Below this recording's quiet level (between its noise floor and its speech) and 20 dB under the loudest
    speech within half a second, so a quiet read stays speech."""
    from pauses import loudness, threshold
    if id(x) not in _QUIET:
        _QUIET[id(x)] = threshold(loudness(x))[0]
    peak = max(frame_db(x, k, fps) for k in range(fr - round(fps / 2), fr + round(fps / 2) + 1))
    return frame_db(x, fr, fps) < min(_QUIET[id(x)], peak - 20)


def dip(x, fr, fps, floor=None):
    """The frame after the quietest moment in the 5 frames before `fr` (and 1 after), when the voice rises at least
    6 dB out of it: where a word starts between two others. Checked on Max video-2 against waveform onsets: exact on
    6 of 8, 1 frame early on the rest, where Parakeet's start alone ran 2-3 frames late.
    `floor`: the earliest frame the dip may be on. With one- or two-word captions the words are ~7 frames apart,
    and an unbounded search found the previous caption's dip, put both on one frame and the second got spread late."""
    lo = fr - 5 if floor is None else max(fr - 5, floor - 1)   # the start is the frame after the quiet one
    if lo > fr + 1:
        return None
    v, k = min((frame_db(x, j, fps), j) for j in range(lo, fr + 2))
    rise = max(frame_db(x, j, fps) for j in range(k + 1, fr + 3))
    return k + 1 if rise - v >= 6 else None


def voice_pauses(path, least=0.1):
    """(speech end, onset) of every pause of at least `least` s (shorter gaps are stop consonants)."""
    from pauses import load, find_pauses
    return find_pauses(load(path), least)


def silence_ends(path, least=0.1):
    """Where the voice comes back after a pause of at least `least` s."""
    return [e for _, e in voice_pauses(path, least)]


def voice_end(x):
    """Seconds where the last word ends (the last loud moment)."""
    from pauses import loudness, threshold, HOP
    db = loudness(x)
    loud = [i for i, v in enumerate(db) if v >= threshold(db)[0]]
    return (loud[-1] + 1) * HOP if loud else len(x) / 16000


def align(block_toks, asr):
    """Index into asr for every block token (None where unmatched)."""
    sm = difflib.SequenceMatcher(None, [t for t, _ in block_toks], [t for t, _ in asr], autojunk=False)
    m = [None] * len(block_toks)
    for bi, ai, n in sm.get_matching_blocks():
        for k in range(n):
            m[bi + k] = ai + k
    return m


GUESSED = []  # (block, how) for every block whose first word was not heard as its own word


def letter_starts(toks, asr):
    """Start time of every script token, by matching letters with the word gaps taken out, so "sea buckthorn" finds
    the heard "seabuckthorn" and "trymysa" finds "try mysa". A token starting inside a heard word gets that word's
    start plus its share of the letters before it (None when its letters were not heard at all)."""
    sc, sown = [], []
    for i, (t, _) in enumerate(toks):
        sc += t; sown += [i] * len(t)
    ac, at = [], []
    for k, (t, st) in enumerate(asr):
        nxt = asr[k + 1][1] if k + 1 < len(asr) else st + 0.08 * len(t)
        for c, ch in enumerate(t):
            ac.append(ch); at.append(st + (nxt - st) * c / max(len(t), 1) if c else st)
    first = {}
    for i, ch in enumerate(sown):
        first.setdefault(ch, i)
    m = [None] * len(sc)
    for si, ai, n in difflib.SequenceMatcher(None, sc, ac, autojunk=False).get_matching_blocks():
        for k in range(n):
            m[si + k] = ai + k
    out = []
    for i in range(len(toks)):
        f = first.get(i)
        hit = next((m[f + k] for k in range(min(3, len(toks[i][0]))) if f is not None and m[f + k] is not None), None)
        out.append(at[hit] if hit is not None else None)
    return out


def starts(blocks, asr, fx):
    """ASR start time of each block's first spoken word, or None. A first word that was not heard as its own word
    is found by its letters (letter_starts); only if that fails too is it guessed, and every such block is listed in
    GUESSED so plan can print it (video-23: "sea buckthorn" heard as one word got a 2-frame caption)."""
    toks, first = [], []
    for b in blocks:
        first.append(len(toks))
        toks += [(norm(w, fx), 0) for w in b.split() if norm(w, fx)]
    m = align(toks, asr)
    lt = None
    out = []
    for bi, ti in enumerate(first):
        end = first[bi + 1] if bi + 1 < len(first) else len(toks)
        if m[ti] is not None:
            out.append(asr[m[ti]][1]); continue
        lt = lt or letter_starts(toks, asr)
        prev_t = next((out[k] for k in range(bi - 1, -1, -1) if out[k] is not None), None)
        nxt = next((m[k] for k in range(ti + 1, end) if m[k] is not None), None)
        cand = lt[ti]
        if cand is not None and (prev_t is None or cand > prev_t) and (nxt is None or cand <= asr[nxt][1]):
            out.append(cand); GUESSED.append((blocks[bi], "by letters")); continue
        prev = next((m[k] for k in range(ti - 1, -1, -1) if m[k] is not None), None)
        guess = prev + 1 if prev is not None else None
        if guess is not None and guess < len(asr) and (nxt is None or guess <= nxt):
            out.append(asr[guess][1])
        elif nxt is not None:
            out.append(asr[nxt][1])
        else:
            out.append(None)
        GUESSED.append((blocks[bi], "GUESSED"))
    return out, sum(x is None for x in m), len(m)


def brief_check(blocks, brief, project):
    """Caption words the client's brief spells another way: a hyphen it doesn't use (or drops), or a word it never
    uses at all. Captions show the client's words, spelled the client's way."""
    if not brief:
        root = Path(project).resolve().parent
        root = root.parent if root.name == "edit" else root
        cands = sorted((root / "brief").glob("*.txt")) + sorted((root / "brief").glob("*.md"))
        if not cands:
            return []
        brief = cands[0]
    text = Path(brief).read_text(errors="ignore").lower().replace("\u2019", "'")
    words = set(re.findall(r"[a-z0-9']+(?:-[a-z0-9']+)*", text))
    flat = set(re.findall(r"[a-z0-9']+", text))
    out, seen = [], set()
    for b in blocks:
        for w in re.findall(r"[a-z0-9']+(?:-[a-z0-9']+)*", b.lower().replace("\u2019", "'")):
            if w in words or w in seen:
                continue
            seen.add(w)
            parts = w.split("-")
            if len(parts) > 1 and all(p in flat for p in parts):
                out.append(f"{w!r}: the brief writes it without the hyphen ({' '.join(parts)})")
            elif any(x.replace("-", "") == w for x in words if "-" in x):
                out.append(f"{w!r}: the brief hyphenates it ({next(x for x in words if x.replace('-', '') == w)})")
            elif w.strip("'") not in flat and not w.isdigit():
                out.append(f"{w!r} is not in the brief ({Path(brief).name})")
    return out


def cmd_plan(a):
    global MAXWORDS
    MAXWORDS = a.max_words
    P = paths(a.project)
    for k in ("vo.wav", "pk.json"):
        if not P[k].exists():
            die(f"{P[k]} missing: run `fc_captions.py words {a.project}` first")
    if not P["blocks.txt"].exists():
        if not a.script:
            die(f"no {P['blocks.txt']}: pass --script (the voiceover script of this edit) to write a first split")
        text = Path(a.script).read_text()
        P["blocks.txt"].write_text("\n".join(split_phrases(text)) + "\n")
        print(f"wrote {P['blocks.txt']}: read it, join or split phrases that read badly, then run plan again")
    blocks = [l.strip() for l in P["blocks.txt"].read_text().splitlines() if l.strip()]
    fx = load_fixes(a.fixes)
    s = seq(a.project)
    fps, end, cuts = fps_of(s), s["durationFrames"], cuts_of(s)
    pk = asr_tokens(json.load(open(P["pk.json"])), fx)
    ps, miss, total = starts(blocks, pk, fx)
    heard = list(GUESSED)
    if P["fw.json"].exists():
        fs, _, _ = starts(blocks, asr_tokens(json.load(open(P["fw.json"])), fx), fx)
    else:
        fs = [None] * len(blocks)
    ons = silence_ends(P["vo.wav"])
    x = pcm16k(P["vo.wav"])
    # Parakeet's lead on this recording: where a word follows silence, how far before the voice it marks it
    short = silence_ends(P['vo.wav'], 0.06)   # once: it reads the whole recording
    lead = [min(c) for c in ([o - t for o in short if -0.05 <= o - t <= 0.25] for _, t in pk) if c]
    off = statistics.median(lead) if len(lead) >= 5 else 0.08
    real_stops = [s0 for s0, _ in voice_pauses(P['vo.wav'], 0.15)]   # pauses, not stop consonants
    rows = []
    for i, (b, p, f) in enumerate(zip(blocks, ps, fs)):
        if p is None and f is None:
            die(f"can't place {b!r}: none of its words were heard. Check blocks.txt against the voiceover")
        est = p + off if p is not None else f
        if p is not None and f is not None and abs(f - (p + off)) < 0.3:
            est = (p + off + f) / 2
        near = [o for o in ons if abs(o - est) <= 0.13]
        if i == 0 and est < 0.5:
            fr, src = 0, "start"
        elif near:
            fr, src = int(min(near, key=lambda o: abs(o - est)) * fps), "onset"
        else:
            fr, src = round(est * fps), "words"
            # never snap back onto the caption before, nor onto the word before this one (which may be the last
            # word of a two-word caption, "can look" / "away."): its start plus the lead is where its own dip is
            floor = rows[-1][1] + MIN_GAP if rows else None
            j = next((k for k, (_, t) in enumerate(pk) if t == p), None) if p is not None else None
            if floor is not None and j:
                floor = max(floor, round((pk[j - 1][1] + off) * fps) + 1)
            deep = [k for k in range(fr - 2, fr + 1) if silent(x, k, fps) and (floor is None or k >= floor - 1)]
            if len(deep) == 3:  # inside a pause: the caption starts where the voice comes back
                while fr < max(deep) + 8 and silent(x, fr, fps):
                    fr += 1
                src = "pause"
            elif deep:          # just after a short pause before the word
                fr, src = max(deep) + 1, "pause"
            else:               # mid-phrase: the word starts where the voice rises out of the dip before it
                d = dip(x, fr, fps, floor)
                if d is not None:
                    fr, src = d, "dip"
            # overshot: under 5 frames of voice left before a real pause means the word was already over (Parakeet
            # late on a sentence's last word, plus the lead, landed on its final consonant or in the silence after).
            # "trick." landed on the "k" after the 2-frame "ck" closure, 10 frames late (user, 2026-11-07).
            # Parakeet is late on these words, so search back from its own start for the last clear rise out of a dip
            # (trick: 319, time: 365 out of the "t" closure; both match the waveform and the user's mark).
            stop_at = next((s0 * fps for s0 in real_stops if s0 * fps > fr - 1), None)
            if p is not None and (all(silent(x, k, fps) for k in range(fr, fr + 3))
                                  or (stop_at is not None and stop_at - fr < 5)):
                # Parakeet was late here, so its previous word is no floor either ("a" kept "time." 7 frames late):
                # only the caption before. Look back up to 12 frames (0.4 s), never onto the overshoot itself.
                raw = round(p * fps)
                lo = max(raw - 12, rows[-1][1] + MIN_GAP if rows else 0)
                back = closure_onsets(x, lo / fps, (raw - 1) / fps)
                if back:
                    fr, src = max(round(back[-1] * fps), lo), "back-dip"
                else:
                    fr, src = max(raw, floor or 0), "words-raw"
        rows.append([b, fr, src])
    notes = []
    for c in cuts:
        j = min(range(len(rows)), key=lambda j: abs(rows[j][1] - c))
        d = c - rows[j][1]
        if abs(d) > 6:
            notes.append(f"cut at {tc(c, fps)} is not on a phrase start (nearest: {rows[j][0]!r} at {tc(rows[j][1], fps)}): "
                         "move the cut to a phrase start, or split a block there")
            continue
        if abs(d) > 2:
            notes.append(f"cut at {tc(c, fps)} is {abs(d)} frames {'after' if d > 0 else 'before'} the voice of "
                         f"{rows[j][0]!r} ({tc(rows[j][1], fps)}): move the cut onto the voice")
        rows[j][1], rows[j][2] = c, rows[j][2] + "+cut"
    # Fast or sung lines: the engines miss words, or a cut snap lands two blocks on one frame. Spread those blocks
    # evenly up to the next block that starts later, and list them, rather than stopping on the first one.
    i = 1
    while i < len(rows):
        if rows[i][1] <= rows[i - 1][1]:
            j = i
            while j < len(rows) and rows[j][1] <= rows[i - 1][1]:
                j += 1
            lo, hi = rows[i - 1][1], rows[j][1] if j < len(rows) else end
            for k in range(i, j):
                rows[k][1], rows[k][2] = lo + round((hi - lo) * (k - i + 1) / (j - i + 1)), "spread"
                notes.append(f"{rows[k][0]!r} had no clear start (fast words): spread to {tc(rows[k][1], fps)}, check it")
            i = j
        i += 1
    # pop styles: show each mid-phrase caption a few frames before its voice (on the voice it reads late).
    # Never on a caption snapped to a cut (picture and caption change together) and never out of order.
    early = a.early if a.early is not None else (EARLY_POP if MAXWORDS <= 3 else 0)
    if early:
        prev = -1
        for r in rows:
            if r[2] in LEADING:   # mid-phrase only: after a pause the voice
                # onset is visible on the waveform and a caption before it shows over silence (user, 2026-11-07)
                # never shorten the caption before below MIN_POP: "and" (on the voice after a pause) got 2 frames
                # when "suddenly" led into it, a flash nobody can read (2026-11-07)
                r[1] = max(r[1] - early, min(prev + MIN_POP, r[1]), 0)
            prev = r[1]
    # a caption leaves the screen in a real pause: 2 frames after the voice stops, back when it starts again
    gaps = [(s0, e0) for s0, e0 in voice_pauses(P["vo.wav"], a.hide)] if a.hide else []
    out = []
    for k, (t, f, src) in enumerate(rows):
        nxt = rows[k + 1][1] if k + 1 < len(rows) else end
        stop = [math.ceil(s0 * fps) + TAIL for s0, e0 in gaps if f < s0 * fps and e0 * fps <= nxt + 1 + early]
        if k + 1 == len(rows):  # after the last word: the end card speaks for itself
            stop += [math.ceil(s0 * fps) + TAIL for s0, e0 in gaps if s0 * fps > f] + \
                    [math.ceil(voice_end(x) * fps) + TAIL]
        # clear in the pause even when the voice stopped under half a second in: hold the half second, then clear
        # (it used to skip the pause then, leaving the caption over the silence until the next one)
        e = min([nxt] + [max(s, f + round(fps / 2)) for s in stop if s < nxt])
        out.append({"text": t, "start": f, "end": e, "src": src})
    # check every caption against the waveform; fix the clear misses (start onto its voice, end in the pause), then
    # check again and report whatever is left for a human
    _, fixes = audit(x, out, fps, early, a.hide, real_stops, with_fixes=True, onsets=ons)
    for line in apply_fixes(out, fixes, fps):
        print("waveform check fixed:", line)
    notes += audit(x, out, fps, early, a.hide, real_stops, onsets=ons)
    long = [r["text"] for r in out if len(r["text"].replace(" / ", " ").split()) > MAXWORDS]
    json.dump({"project": str(Path(a.project).resolve()), "fps": fps, "cuts": cuts, "end": end, "lead": off,
               "blocks": out}, open(P["captions.json"], "w"), ensure_ascii=False, indent=1)
    for r in out:
        print(f"  {tc(r['start'], fps)}  {r['end'] - r['start']:4d}f  {r['text']:30s} {r['src']}")
    clear = sum(1 for k, r in enumerate(out) if r["end"] < (out[k + 1]["start"] if k + 1 < len(out) else end))
    print(f"{len(out)} captions, {clear} end before a pause, Parakeet lead {off:.3f} s, {miss}/{total} script words "
          f"not heard -> {P['captions.json']}")
    for n in notes + [f"over {MAXWORDS} words: {t!r}" for t in long]:
        print("NOTE", n)
    for n in brief_check(blocks, a.brief, a.project):
        print("BRIEF", n)
    for b, how in heard:
        print(f"CHECK {b!r}: its first word was not heard as its own word, start found {how}"
              + (" (look at this caption's frame before the build)" if how == "GUESSED" else ""))


def apply_fixes(out, fixes, fps):
    """Move each start onto its voice / end into its pause as audit() asks, keeping order and back-to-back runs."""
    done = []
    for k, what, val in fixes:
        r = out[k]
        if what == "end":
            done.append(f"{r['text']!r} now ends {tc(val, fps)} (was {tc(r['end'], fps)})")
            r["end"] = val
            continue
        lo = out[k - 1]["start"] + MIN_GAP if k else 0
        hi = min(out[k + 1]["start"] - MIN_GAP if k + 1 < len(out) else r["end"] - 1, r["end"] - MIN_GAP)
        val = min(max(val, lo), hi)
        if val == r["start"]:
            continue
        if k and (out[k - 1]["end"] == r["start"] or out[k - 1]["end"] > val):
            out[k - 1]["end"] = val   # back to back stays back to back
        done.append(f"{r['text']!r} now starts {tc(val, fps)} (was {tc(r['start'], fps)})")
        r["start"], r["src"] = val, r["src"] + "+fixed"
    return done


LEADING = ("dip", "words", "words-raw", "back-dip", "spread")   # sources that get the --early lead


def audit(x, out, fps, early, hide, stops=(), with_fixes=False, onsets=()):
    """Every caption against the waveform, for the misses users have caught (2026-11-07): a start over the silence
    before its voice (AND IT, PUT IT), a start after its word has clearly begun (TRICK on its final "k", 10 frames
    late), a caption left up over a pause (AWAY). `stops`: where real pauses (>= 0.15 s) begin, in seconds.
    Returns NOTE lines; none means every caption sits on its voice. Tested against the flagged versions."""
    quiet = lambda j: all(silent(x, i, fps) for i in (j, j - 1, j - 2))   # 3 frames: a pause, not a stop consonant
    # a voice coming out of a pause shows on the frame it starts in, as plan places it (4.93 s -> frame 147, not 148)
    on_frame = lambda v: next((int(o * fps) for o in onsets if abs(o * fps - v) <= 1.5), v)
    notes, fixes = [], []
    for k, r in enumerate(out):
        f, e, t = r["start"], r["end"], r["text"]
        prev = out[k - 1]["start"] if k else -99
        if "cut" not in r["src"] and r["src"] not in ("start", "pinned"):   # by rule, or placed by hand
            v = next((j for j in range(f, f + 15) if not silent(x, j, fps)), None)
            if v is not None:
                lead = 0 if quiet(v - 1) else early   # out of a pause: on the voice; mid-phrase: up to --early before
                if v - f > lead + 1:
                    notes.append(f"{t!r} at {tc(f, fps)} shows {v - f} frames before its voice (allowed {lead})")
                    fixes.append((k, "start", on_frame(v) - lead))
            q = next((j for j in range(f - 1, f - 9, -1) if quiet(j)), None)
            stop = next((s0 * fps for s0 in stops if s0 * fps > f - 1), None)
            if q is not None and f - (q + 1) > 1 and prev < q + 1 - 6:
                notes.append(f"{t!r} at {tc(f, fps)} starts {f - q - 1} frames after the voice came back: late")
                fixes.append((k, "start", on_frame(q + 1)))
            elif stop is not None and stop - f < 5 and (v is None or v < stop) and e <= stop + TAIL + round(fps / 2):
                # only when the caption ends in that pause: a short first word before a break ("not / from cream") is fine
                notes.append(f"{t!r} at {tc(f, fps)} has only {max(0, round(stop - f))} frames of voice before the "
                             f"pause: it starts on the end of its word, late")
            elif q is None:
                lead = early if r["src"] in LEADING else 0
                late = [c for c in closure_onsets(x, (f - 6) / fps, (f - lead - 2) / fps) if c * fps > prev + 2]
                if late and not closure_onsets(x, (f - lead - 2) / fps, (f + 3) / fps):
                    notes.append(f"{t!r} at {tc(f, fps)}: the voice rises out of a gap {round(f - late[-1] * fps)} "
                                 f"frames before it: maybe late")
        run = 0
        while run < e - f and silent(x, e - 1 - run, fps):
            run += 1
        after = 0   # the silence must be a real pause (--hide): short ones are run through by rule
        while after < round(fps * 2) and silent(x, e + after, fps):
            after += 1
        if run > TAIL + 1 and e - f > round(fps / 2) and hide and (run + after) / fps >= hide:
            notes.append(f"{t!r} stays up {run} frames over silence before {tc(e, fps)}")
            fixes.append((k, "end", max(e - run + TAIL, f + round(fps / 2))))
    return (notes, fixes) if with_fixes else notes


def tc(fr, fps):
    s = fr / fps
    return f"{int(s // 60)}:{s % 60:05.2f}"


# ---------- build ----------

def text_width(st, text, size):
    path = subprocess.run(["fc-match", "-f", "%{file}", f"{st['font']}:style={st['fontStyle']}"],
                          capture_output=True, text=True).stdout.strip()
    return int(subprocess.run(["magick", "-font", path, "-pointsize", str(size), f"label:{text}",
                               "-format", "%w", "info:"], capture_output=True, text=True).stdout or 0)


def fit_size(st, text):
    """The template size, or smaller so the line (outline included) fits MAX_W."""
    w = text_width(st, text, st["size"]) + 2 * st["props"].get("stroke_width", 0)
    return st["size"] if w <= MAX_W else int(st["size"] * MAX_W / w)


def box_cmds(st, clip, ls, size, pos):
    """Template 6: a white rounded box behind each line, as shape layers at the back of the clip. FilmCraft's text
    sits on its baseline with the font's ascent (= size) above and 0.3 x size below."""
    bx, out, n = st["boxes"], [], len(ls)
    for k, (t, (x, y)) in enumerate(zip(ls, pos)):
        w, top, bot = text_width(st, t, size), y - size, y + 0.3 * size
        out += [{"id": "graphics.newShape", "params": {
                    "shape": "rectangle", "clip": clip, "position": [x, (top + bot) / 2],
                    "size": [w + 2 * bx["pad"][0], bot - top + 2 * bx["pad"][1]]}},
                {"id": "graphics.set", "params": {"clip": clip, "layer": n + k, "props": {
                    "fill_color": bx["color"], "corner_radius": bx["radius"], "stroke": False}}},
                {"id": "graphics.arrangeLayer", "params": {"clip": clip, "layer": n + k, "to": "back"}}]
    return out


ONE_LINE = 26  # characters that sit on one line at size 58 (user, 2026-10-24: "is / thinner skin." looked ugly)


def two_lines(text, one=False):
    """A block as the lines template 6 shows: split at " / ", else at the most even break (after a comma if one).
    one: always one line (build --one-line; Aleo video-5 user, 2026-10-29), shrunk by fit_size if it is too wide."""
    flat = text.replace(" / ", " ")
    if one or len(flat) <= ONE_LINE:  # fits on one line: never a one- or two-word line over another
        return [flat]
    if " / " in text:
        return [t.strip() for t in text.split(" / ")]
    w = text.split()
    if len(w) < 3:
        return [text]
    def cost(k):
        a, b = " ".join(w[:k]), " ".join(w[k:])
        return abs(len(a) - len(b)) - (8 if a.endswith(",") else 0) + (6 if norm(w[k - 1]) in WEAK_END else 0)
    k = min(range(1, len(w)), key=cost)
    return [" ".join(w[:k]), " ".join(w[k:])]


def greedy_lines(st, text):
    """Template 1: one line while the text is at most wrap_px wide, else two balanced lines (the narrowest widest
    line), never one short word alone on a line ("A THIRD-GENERATION / FIX" read badly, user 2026-11-09).
    Best is blocks that fit one line: `build` prints every block that wraps."""
    flat = text.replace(" / ", " ")
    if " / " in text:
        return [t.strip() for t in text.split(" / ")]
    if text_width(st, flat, st["size"]) <= st["wrap_px"]:
        return [flat]
    w = flat.split()
    opts = [(" ".join(w[:k]), " ".join(w[k:])) for k in range(1, len(w))]
    ok = [o for o in opts if not any(len(x) <= 4 and " " not in x for x in o)] or opts
    best = min(ok, key=lambda o: max(text_width(st, x, st["size"]) for x in o))
    print(f"  wraps: {best[0]} / {best[1]}")
    return list(best)


KEEP_CASE = {"mysa", "himalayan", "co2", "co2-extracted", "i"}  # template 9 lowercases everything but these


def lower_text(text):
    return " ".join(w if re.sub(r"[^\w-]", "", w).lower() in KEEP_CASE else w.lower() for w in text.split())


def pairs(blocks):
    """Template 9: (partner index, row) of each block. Blocks pair two by two, the first on the top row; a pair breaks
    where the captions clear and at a sentence end, so a pair never runs into the next sentence."""
    mate, i = {}, 0
    while i < len(blocks):
        if (i + 1 < len(blocks) and blocks[i]["end"] == blocks[i + 1]["start"]
                and not blocks[i]["text"].rstrip().endswith((".", "?", "!"))):
            mate[i], mate[i + 1] = (i + 1, 0), (i, 1)
            i += 2
        else:
            mate[i] = (None, 0)
            i += 1
    return mate


def ensure_font(st):
    if subprocess.run(["fc-list", f"{st['font']}:style={st['fontStyle']}"], capture_output=True, text=True).stdout.strip():
        return
    src = HERE.parent / "fonts" / st["file"]
    if not src.exists():
        die(f"font {st['font']} {st['fontStyle']} isn't installed and {src} is missing")
    dst = Path.home() / ".local/share/fonts" / st["file"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    subprocess.run(["fc-cache", "-f", str(dst.parent)], capture_output=True)
    print(f"installed {dst.name} for FilmCraft")


def signature(s, skip_v):
    keep = lambda it: (it["startFrame"], it["durationFrames"], it["name"], it.get("sourceIn"))
    return ([[keep(i) for i in t["items"]] for k, t in enumerate(s["video"]) if k != skip_v],
            [[keep(i) for i in t["items"]] for t in s["audio"]])


def cmd_build(a):
    P = paths(a.project)
    project = Path(a.project).resolve()
    import fc
    live = fc.save_live(project)  # the user's open copy is saved first; the app reloads the result at the end
    plan = json.load(open(P["captions.json"]))
    s = seq(project)
    if cuts_of(s) != plan["cuts"] or s["durationFrames"] != plan["end"]:
        die("the edit changed since plan: run plan again")
    st = dict(STYLES[a.template])
    ensure_font(st)
    if st.get("pair"):
        ensure_font(dict(st, fontStyle=st["pair"]["fontStyle"], file=st["pair"]["file"]))
    T = tpf(s)
    nv = len(s["video"])
    if a.track:
        v = int(a.track.lstrip("Vv")) - 1
        add = v >= nv
    else:  # the track whose text clips are these captions (an older build), else a new one on top. Never just the
        # top text track: on Max video-2 that held the "X" / "LINK BELOW" overlays, and a build replaced them.
        v = caption_track(s, plan)
        v, add = (nv, True) if v is None else (v, False)
    if not add and any(not is_text(i) for i in s["video"][v]["items"]):
        die(f"V{v + 1} holds clips that aren't text: pass --track for an empty or captions-only track")
    old = [] if add else [i["clip"] for i in s["video"][v]["items"]]
    cmds = []
    if add:
        cmds.append({"id": "sequence.addTracks", "params": {"video": 1}})
    if old:
        cmds.append({"id": "edit.clear", "params": {"clips": old}})
    lines, second = [], []  # template 6: line 1 is the clip, line 2 a second layer added once its clip id is known
    mate = pairs(plan["blocks"]) if st.get("pair") else {}
    for n, b in enumerate(plan["blocks"]):
        before = a.caps_from is not None and b["start"] < a.caps_from * plan["fps"] - 0.5
        text = b["text"].lower() if before else b["text"].upper() if st["caps"] else b["text"]
        if st.get("pair"):  # its own line bold; the partner phrase dimmed on the other line
            pr = st["pair"]
            m, row = mate[n]
            text = lower_text(text.replace(" / ", " "))
            size = st["size"]
            if m is not None:
                size = min(fit_size(st, text), fit_size(st, lower_text(plan["blocks"][m]["text"].replace(" / ", " "))))
            pos = [[540, pr["lines"][row if m is not None else 1]]]
            cmds.append({"id": "graphics.newText", "params": {
                "text": text, "position": pos[0], "size": size, "font": st["font"], "fontStyle": st["fontStyle"],
                "seconds": (b["end"] - b["start"]) / plan["fps"], "track": v, "time": b["start"] * T}})
            cmds.append({"id": "graphics.set", "params": {"props": dict(st["props"], position=pos[0])}})
            if m is not None:
                lines.append((len(cmds) - 2, [text, lower_text(plan["blocks"][m]["text"].replace(" / ", " "))],
                              size, pos + [[540, pr["lines"][1 - row]]]))
            continue
        if st.get("bare"):  # the reference shows no commas, full stops or word hyphens
            text = re.sub(r"[,.!?;:]+(?=\s|$)", "", text)
            # "third-generation" -> "third generation" (video-23 user: the reference writes THIRD GENERATION);
            # a hyphen before a digit stays (omega-7)
            text = re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z])", " ", text)
        ls = (greedy_lines(st, text) if st.get("wrap_px") else two_lines(text, a.one_line)) if st.get("lines") else [text]
        size = min(fit_size(st, t) for t in ls)
        ys = st["lines"] if len(ls) == 2 else [st.get("single") or (st["lines"][-1] if st.get("lines") else st["props"]["position"][1])]
        pos = [[st["props"]["position"][0], y] for y in ys]
        cmds.append({"id": "graphics.newText", "params": {
            "text": ls[0], "position": pos[0], "size": size, "font": st["font"],
            "fontStyle": st["fontStyle"], "seconds": (b["end"] - b["start"]) / plan["fps"], "track": v,
            "time": b["start"] * T}})
        cmds.append({"id": "graphics.set", "params": {"props": dict(st["props"], position=pos[0])}})
        lines.append((len(cmds) - 2, ls, size, pos))
    tmp = project.with_name(f".{project.stem}.captions-tmp.fcproj")
    cmds.append({"id": "file.save", "params": {"path": str(tmp)}})
    res = cli(project, cmds)
    for i, ls, size, pos in lines:
        clip = res[i]["result"]["clip"]
        if len(ls) == 2 and st.get("pair"):
            second += [{"id": "graphics.newText", "params": {"text": ls[1], "position": pos[1], "size": size,
                                                              "font": st["font"], "fontStyle": st["pair"]["fontStyle"], "clip": clip}},
                       {"id": "graphics.set", "params": {"clip": clip, "layer": 1, "props": dict(
                           st["props"], position=pos[1], opacity=st["pair"]["opacity"])}}]
        elif len(ls) == 2:
            second += [{"id": "graphics.newText", "params": {"text": ls[1], "position": pos[1], "size": size,
                                                              "font": st["font"], "fontStyle": st["fontStyle"], "clip": clip}},
                       {"id": "graphics.set", "params": {"clip": clip, "layer": 1, "props": dict(st["props"], position=pos[1])}}]
        if st.get("boxes"):   # after the text: each box goes to the back, so text is always on top
            second += box_cmds(st, clip, ls, size, pos)
    if second:
        cli(tmp, second + [{"id": "file.save", "params": {}}])
    # verify the temp save before it replaces anything
    t = seq(tmp)
    got = [(i["startFrame"], i["startFrame"] + i["durationFrames"]) for i in t["video"][v]["items"]]
    want = [(b["start"], b["end"]) for b in plan["blocks"]]
    errs = []
    if signature(t, v) != signature(s, v if not add else -1):
        errs.append("other tracks changed")
    if got != want:
        errs.append(f"caption frames differ from the plan: {[(g, w) for g, w in zip(got, want) if g != w][:3]}")
    if errs:
        tmp.unlink(missing_ok=True)
        die("; ".join(errs) + " (project left as it was)")
    orig, new = json.load(open(project)), json.load(open(tmp))
    new["project"]["name"], new["project"]["root"]["name"] = orig["project"]["name"], orig["project"]["root"]["name"]
    bk = project.parent / f"backup-{datetime.date.today()}-captions"
    bk.mkdir(exist_ok=True)
    dst = bk / project.name
    k = 2
    while dst.exists():
        dst = bk / f"{project.stem}-{k}{project.suffix}"; k += 1
    shutil.copy2(project, dst)
    project.write_text(json.dumps(new, separators=(",", ":"), ensure_ascii=False))
    tmp.unlink()
    if live:
        fc.reload_live(project)
    print(f"V{v + 1}: {len(want)} captions (template {a.template}), {len(old)} old ones replaced; backup {dst}"
          + ("; the open app reloaded it" if live else ""))


# ---------- check, export ----------

def cmd_check(a):
    P = paths(a.project)
    plan = json.load(open(P["captions.json"]))
    fps, bl = plan["fps"], plan["blocks"][1:]
    pick = [b for b in bl if "cut" not in b["src"]]
    step = max(1, len(pick) // a.n)
    pick = (pick[::step] + [b for b in bl if "cut" in b["src"]][:2])[:a.n + 2]
    with tempfile.TemporaryDirectory() as d:
        rows = []
        for i, b in enumerate(pick):
            pair = []
            for fr in (b["start"] - 1, b["start"]):
                out = f"{d}/{i}-{fr}.png"
                subprocess.run(["filmcraft-cli", "--project", a.project, "render", "--seconds", str((fr + 0.5) / fps),
                                "--out", out, "--scale", "0.25"], capture_output=True)
                pair.append(out)
            rows.append(pair)
            print(f"row {i + 1}: frame {b['start'] - 1} | {b['start']}  {b['text']!r} ({b['src']})")
        cols = [x for p in rows for x in p]
        per = 4
        grid = [cols[k:k + per] for k in range(0, len(cols), per)]
        while len(grid[-1]) < per:
            grid[-1].append(grid[-1][-1])
        lines = []
        for k, g in enumerate(grid):
            o = f"{d}/row{k}.png"
            subprocess.run(["ffmpeg", "-v", "quiet", "-y", *sum((["-i", x] for x in g), []), "-filter_complex",
                            f"hstack=inputs={per}", o])
            lines.append(o)
        args = sum((["-i", x] for x in lines), [])
        flt = f"vstack=inputs={len(lines)}" if len(lines) > 1 else "null"
        subprocess.run(["ffmpeg", "-v", "quiet", "-y", *args, "-filter_complex", flt, str(P["check.png"])])
    print(f"-> {P['check.png']} (pairs left to right: the frame before a caption starts, then its first frame)")


def cmd_export(a):
    """The filmcraft skill's export: saves the open copy first, burns caption tracks, checks the file."""
    fcpy = next((d / "fc.py" for d in (HERE.parent.parent / "filmcraft" / "scripts",
                                        Path.home() / ".claude/skills/filmcraft/scripts") if (d / "fc.py").exists()), None)
    if fcpy:
        sys.exit(subprocess.run([sys.executable, str(fcpy), "export", a.project, "-o", a.out]
                                + (["--kbps", str(a.kbps)] if a.kbps else [])).returncode)
    if app_running():
        die("FilmCraft is open: close it first so the export reads the saved project")
    out = Path(a.out).resolve()
    tmp = out.with_name(out.stem + ".tmp" + out.suffix)
    settings = dict(EXPORT)
    if a.kbps:  # video at this average rate, peaks at 1.5x
        settings.update(bitrateKbps=a.kbps, maxBitrateKbps=int(a.kbps * 1.5))
    r = cli(a.project, [{"id": "file.exportMedia", "params": {"path": str(tmp), "format": "h264",
                                                               "settings": settings, "wait": True}}])
    tmp.replace(out)
    print(f"-> {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("words"); w.add_argument("project"); w.add_argument("--vo", default="A1")
    w.add_argument("--fast", action="store_true",
                   help="Parakeet only (about 25 s instead of 80 s for 95 s of voice; mid-phrase starts can run 2-7 frames off)")
    p = sub.add_parser("plan"); p.add_argument("project"); p.add_argument("--script"); p.add_argument("--fixes")
    p.add_argument("--brief", help="the client's brief or script: flag caption words spelled differently there "
                   "(video-23: our 'third-generation' where the brief says 'third generation'). Default: brief/*.txt|md")
    p.add_argument("--max-words", type=int, default=MAXWORDS, help="most words a caption (template 5: 2, template 6: 7)")
    p.add_argument("--early", type=int, help=f"show captions this many frames before their voice (default {EARLY_POP} "
                   "with --max-words 3 or fewer, the one- and two-word pop templates 5 and 7; else 0)")
    p.add_argument("--hide", type=float, default=0.4,
                   help="clear the screen in voice pauses at least this long, s (0: captions back to back)")
    b = sub.add_parser("build"); b.add_argument("project"); b.add_argument("-t", "--template", default="4", choices=STYLES)
    b.add_argument("--track")
    b.add_argument("--caps-from", type=float, help="template 8: captions before this time (s) are lowercase")
    b.add_argument("--one-line", action="store_true", help="template 6: every caption on one line (blocks must fit 860 px)")
    c = sub.add_parser("check"); c.add_argument("project"); c.add_argument("--n", type=int, default=8)
    e = sub.add_parser("export"); e.add_argument("project"); e.add_argument("-o", "--out", required=True)
    e.add_argument("--kbps", type=int, help="video bitrate (default 6000, ~45 MB a minute at 1080x1920; 4000 ~32 MB)")
    a = ap.parse_args()
    {"words": cmd_words, "plan": cmd_plan, "build": cmd_build, "check": cmd_check, "export": cmd_export}[a.cmd](a)


if __name__ == "__main__":
    main()
