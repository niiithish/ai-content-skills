#!/usr/bin/env python3
"""Captions as text clips inside a FilmCraft project, each one starting on the frame its phrase is spoken.

  fc_captions.py words  PROJECT [--vo A1]            the voiceover track as WAV, then word times from Parakeet and
                                                    faster-whisper -> captions/<stem>.vo.wav, .pk.json, .fw.json
  fc_captions.py plan   PROJECT [--script S] [--fixes F]
                                                    caption blocks with start frames -> captions/<stem>.captions.json
  fc_captions.py build  PROJECT [-t 4] [--track V3] text clips into the project (backup, temp save, verify, copy in)
  fc_captions.py check  PROJECT [--n 8]             frames just before and on caption starts -> captions/<stem>.check.png
  fc_captions.py export PROJECT -o OUT.mp4          H.264 at the delivery settings, from FilmCraft itself

Blocks are one caption per line in captions/<stem>.blocks.txt. `plan --script` writes a first split there (whole
phrases, at most 4 words); read and fix it, then run plan again. Timing never comes from one engine alone:
  - after a pause, a caption starts on the frame where the voice rises out of silence (ffmpeg silencedetect);
  - mid-sentence, at Parakeet's word start plus its measured lead on this recording, averaged with faster-whisper,
    and moved to the end of a real pause (< -40 dB) just before it;
  - every picture cut (V1) starts a caption on that exact frame; a cut more than 2 frames off its voice is reported.
Captions run back to back, no gaps. Work files go in <video>/captions/ (the nearest folder above the project with
PLAN.md, AGENTS.md or project.conf).
"""
import argparse, datetime, difflib, json, os, re, shutil, statistics, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TPS = 254016000000                                   # FilmCraft ticks per second
SAFE_Y = 1500                                        # Meta/TikTok caption safe box bottom on 1080x1920
MAXWORDS = 4
MAX_W = 860  # px: widest caption line on 1080, so 110 px stays clear each side (Max video-2: wide lines ran off the frame)

# One-line templates from the captions skill, as FilmCraft text. Fonts must be installed for fontconfig.
SHADOW = {"shadow": True, "shadow_angle": 90, "shadow_distance": 4, "shadow_blur": 7, "shadow_opacity": 75,
          "shadow_color": "#000000"}
STYLES = {
    "4": dict(about="Sentence-case white Montserrat ExtraBold 68, 3 px black outline, soft shadow, baseline y 1420",
              font="Montserrat", fontStyle="ExtraBold", size=68, caps=False, file="Montserrat-ExtraBold.ttf",
              props={"align": "center", "fill_color": "#ffffff", "stroke": True, "stroke_width": 3,
                     "stroke_color": "#000000", **SHADOW, "position": [540, 1420]}),
    "2": dict(about="ALL CAPS white TikTok Sans ExtraBold 68, 3 px black outline, soft shadow, baseline y 1420",
              font="TikTok Sans", fontStyle="ExtraBold", size=68, caps=True, file="TikTokSans-ExtraBold.ttf",
              props={"align": "center", "fill_color": "#ffffff", "stroke": True, "stroke_width": 3,
                     "stroke_color": "#000000", **SHADOW, "position": [540, 1420]}),
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


def cuts_of(s):
    return sorted({i["startFrame"] for i in s["video"][0]["items"]} - {0})


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
    audio = T.load_audio(str(P["vo.wav"]))
    pk = T.parakeet_words(audio)
    json.dump(pk, open(P["pk.json"], "w"))
    print(f"Parakeet: {len(pk)} words -> {P['pk.json']}")
    from faster_whisper import WhisperModel
    for name in ("medium.en", "small.en"):
        try:
            m = WhisperModel(name, device="cpu", compute_type="int8", local_files_only=True)
            break
        except Exception:
            m = None
    m = m or WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(str(P["vo.wav"]), language="en", word_timestamps=True)
    fw = [(w.word.strip(), w.start, w.end) for sg in segs for w in sg.words if w.word.strip()]
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


def silent(x, fr, fps):
    """Below -40 dB and 25 dB under the loudest speech within half a second (quiet reads stay speech)."""
    peak = max(frame_db(x, k, fps) for k in range(fr - round(fps / 2), fr + round(fps / 2) + 1))
    return frame_db(x, fr, fps) < min(-40, peak - 25)


def silence_ends(path, least=0.1):
    """Where the voice comes back after a pause of at least `least` s (shorter gaps are stop consonants)."""
    err = subprocess.run(["ffmpeg", "-i", str(path), "-af", "silencedetect=n=-40dB:d=0.06", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [float(e) for e, d in re.findall(r"silence_end: ([0-9.]+) \| silence_duration: ([0-9.]+)", err)
            if float(d) >= least]


def align(block_toks, asr):
    """Index into asr for every block token (None where unmatched)."""
    sm = difflib.SequenceMatcher(None, [t for t, _ in block_toks], [t for t, _ in asr], autojunk=False)
    m = [None] * len(block_toks)
    for bi, ai, n in sm.get_matching_blocks():
        for k in range(n):
            m[bi + k] = ai + k
    return m


def starts(blocks, asr, fx):
    """ASR start time of each block's first spoken word, or None."""
    toks, first = [], []
    for b in blocks:
        first.append(len(toks))
        toks += [(norm(w, fx), 0) for w in b.split() if norm(w, fx)]
    m = align(toks, asr)
    out = []
    for bi, ti in enumerate(first):
        end = first[bi + 1] if bi + 1 < len(first) else len(toks)
        if m[ti] is not None:
            out.append(asr[m[ti]][1]); continue
        prev = next((m[k] for k in range(ti - 1, -1, -1) if m[k] is not None), None)
        nxt = next((m[k] for k in range(ti + 1, end) if m[k] is not None), None)
        guess = prev + 1 if prev is not None else None
        if guess is not None and guess < len(asr) and (nxt is None or guess <= nxt):
            out.append(asr[guess][1])
        elif nxt is not None:
            out.append(asr[nxt][1])
        else:
            out.append(None)
    return out, sum(x is None for x in m), len(m)


def cmd_plan(a):
    P = paths(a.project)
    for k in ("vo.wav", "pk.json", "fw.json"):
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
    fw = asr_tokens(json.load(open(P["fw.json"])), fx)
    ps, miss, total = starts(blocks, pk, fx)
    fs, _, _ = starts(blocks, fw, fx)
    ons = silence_ends(P["vo.wav"])
    x = pcm16k(P["vo.wav"])
    # Parakeet's lead on this recording: where a word follows silence, how far before the voice it marks it
    lead = [min(c) for c in ([o - t for o in silence_ends(P['vo.wav'], 0.06) if -0.05 <= o - t <= 0.25] for _, t in pk) if c]
    off = statistics.median(lead) if len(lead) >= 5 else 0.08
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
            deep = [k for k in range(fr - 2, fr + 1) if silent(x, k, fps)]
            if len(deep) == 3:  # inside a pause: the caption starts where the voice comes back
                while fr < max(deep) + 8 and silent(x, fr, fps):
                    fr += 1
                src = "pause"
            elif deep:          # just after a short pause before the word
                fr, src = max(deep) + 1, "pause"
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
    for r0, r1 in zip(rows, rows[1:]):
        if r1[1] <= r0[1]:
            die(f"{r1[0]!r} starts at or before {r0[0]!r} ({r1[1]} <= {r0[1]}): check blocks.txt order")
    out = [{"text": t, "start": f, "end": rows[k + 1][1] if k + 1 < len(rows) else end, "src": src}
           for k, (t, f, src) in enumerate(rows)]
    long = [r["text"] for r in out if len(r["text"].split()) > MAXWORDS]
    json.dump({"project": str(Path(a.project).resolve()), "fps": fps, "cuts": cuts, "end": end, "lead": off,
               "blocks": out}, open(P["captions.json"], "w"), ensure_ascii=False, indent=1)
    for r in out:
        print(f"  {tc(r['start'], fps)}  {r['end'] - r['start']:4d}f  {r['text']:30s} {r['src']}")
    print(f"{len(out)} captions, Parakeet lead {off:.3f} s, {miss}/{total} script words not heard -> {P['captions.json']}")
    for n in notes + [f"over {MAXWORDS} words: {t!r}" for t in long]:
        print("NOTE", n)


def tc(fr, fps):
    s = fr / fps
    return f"{int(s // 60)}:{s % 60:05.2f}"


# ---------- build ----------

def fit_size(st, text):
    """The template size, or smaller so the line (outline included) fits MAX_W."""
    path = subprocess.run(["fc-match", "-f", "%{file}", f"{st['font']}:style={st['fontStyle']}"],
                          capture_output=True, text=True).stdout.strip()
    w = int(subprocess.run(["magick", "-font", path, "-pointsize", str(st["size"]), f"label:{text}",
                            "-format", "%w", "info:"], capture_output=True, text=True).stdout or 0)
    w += 2 * st["props"].get("stroke_width", 0)
    return st["size"] if w <= MAX_W else int(st["size"] * MAX_W / w)


def ensure_font(st):
    if subprocess.run(["fc-list", f"{st['font']}:style={st['fontStyle']}"], capture_output=True, text=True).stdout.strip():
        return
    src = HERE.parent.parent / "captions" / "fonts" / st["file"]
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
    if app_running():
        die("FilmCraft is open: save and close it first (the app would keep its own copy and overwrite this)")
    plan = json.load(open(P["captions.json"]))
    s = seq(project)
    if cuts_of(s) != plan["cuts"] or s["durationFrames"] != plan["end"]:
        die("the edit changed since plan: run plan again")
    st = dict(STYLES[a.template])
    ensure_font(st)
    T = tpf(s)
    nv = len(s["video"])
    if a.track:
        v = int(a.track.lstrip("Vv")) - 1
        add = v >= nv
    else:  # the top video track when it holds only text clips (or nothing), else a new one on top
        top = s["video"][-1]["items"]
        v, add = (nv - 1, False) if nv > 1 and all(is_text(i) for i in top) else (nv, True)
    if not add and any(not is_text(i) for i in s["video"][v]["items"]):
        die(f"V{v + 1} holds clips that aren't text: pass --track for an empty or captions-only track")
    old = [] if add else [i["clip"] for i in s["video"][v]["items"]]
    cmds = []
    if add:
        cmds.append({"id": "sequence.addTracks", "params": {"video": 1}})
    if old:
        cmds.append({"id": "edit.clear", "params": {"clips": old}})
    for b in plan["blocks"]:
        text = b["text"].upper() if st["caps"] else b["text"]
        cmds.append({"id": "graphics.newText", "params": {
            "text": text, "position": st["props"]["position"], "size": fit_size(st, text), "font": st["font"],
            "fontStyle": st["fontStyle"], "seconds": (b["end"] - b["start"]) / plan["fps"], "track": v,
            "time": b["start"] * T}})
        cmds.append({"id": "graphics.set", "params": {"props": st["props"]}})
    tmp = project.with_name(f".{project.stem}.captions-tmp.fcproj")
    cmds.append({"id": "file.save", "params": {"path": str(tmp)}})
    cli(project, cmds)
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
    print(f"V{v + 1}: {len(want)} captions (template {a.template}), {len(old)} old ones replaced; backup {dst}")


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
    p = sub.add_parser("plan"); p.add_argument("project"); p.add_argument("--script"); p.add_argument("--fixes")
    b = sub.add_parser("build"); b.add_argument("project"); b.add_argument("-t", "--template", default="4", choices=STYLES)
    b.add_argument("--track")
    c = sub.add_parser("check"); c.add_argument("project"); c.add_argument("--n", type=int, default=8)
    e = sub.add_parser("export"); e.add_argument("project"); e.add_argument("-o", "--out", required=True)
    e.add_argument("--kbps", type=int, help="video bitrate (default 6000, ~45 MB a minute at 1080x1920; 4000 ~32 MB)")
    a = ap.parse_args()
    {"words": cmd_words, "plan": cmd_plan, "build": cmd_build, "check": cmd_check, "export": cmd_export}[a.cmd](a)


if __name__ == "__main__":
    main()
