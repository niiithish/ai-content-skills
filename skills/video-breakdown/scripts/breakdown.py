#!/usr/bin/env python3
"""Local reference-video breakdown: cuts, recurring shots, layouts, captions, words.

  breakdown.py analyze VIDEO [--out DIR] [--no-ocr]
      Finds every cut (hard + soft), groups shots that come back (same camera /
      same setup), OCRs on-screen text, lines
      every shot and cut up with the word-timed transcript, and writes shot
      sheets + a cluster sheet to look at. Writes DIR/labels.json to fill in.

  breakdown.py report DIR
      After labels.json is filled: shot table, rhythm stats (share of runtime,
      insert cadence, cut-on-word timing, by section), timeline.png.

  breakdown.py map DIR SCRIPT.txt [--vo OUR.words.json]
      Aligns the reference words to our script (or our real voiceover) and
      writes the reference visual pattern onto our words: which shot type goes
      on which of our phrases, and when.

Only needs ffmpeg, numpy, Pillow (and tesseract for OCR).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import statistics as st
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = ["/usr/share/fonts/noto/NotoSans-Regular.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
BOLD_PATHS = ["/usr/share/fonts/noto/NotoSans-Bold.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"]

# Shot types the agent picks from in labels.json (free text is allowed too).
TYPES = {
    "talking-head": "#4f7cff",   # one speaker on camera, any framing
    "two-shot":     "#7aa2ff",   # both speakers in one frame
    "split":        "#a78bfa",   # horizontal / vertical split of speakers
    "broll":        "#22c55e",   # live-action / photoreal clip
    "still":        "#84cc16",   # photo or image, usually with a push
    "cgi":          "#f97316",   # 3D / animation / inside-the-body / diagram motion
    "product":      "#ef4444",   # packshot, product in hand, unboxing
    "text":         "#eab308",   # text card, screenshot, review, UI
    "compare":      "#ec4899",   # before/after: side-by-side split or wipe between two pictures
    "story":        "#06b6d4",   # story/song ads: the cast acting a scene (the spine, like a speaker)
    "transition":   "#475569",   # black frame, flash, whip blur bridging two shots (not an insert)
    "other":        "#94a3b8",
}


def font(size, bold=False):
    for p in (BOLD_PATHS if bold else []) + FONT_PATHS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def tc(t):
    m, s = divmod(max(t, 0), 60)
    return f"{int(m)}:{s:04.1f}"


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_frames:format=duration",
                          "-of", "json", str(video)], capture_output=True, text=True, check=True)
    j = json.loads(out.stdout)
    s = j["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(d), float(j["format"]["duration"])


def decode_small(video, w, h):
    cmd = ["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={w}:{h}:flags=area",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def hist(frames):
    q = (frames // 32).astype(np.int32)              # 8 levels a channel
    idx = q[..., 0] * 64 + q[..., 1] * 8 + q[..., 2]
    out = np.zeros((len(frames), 512), np.float32)
    for i, f in enumerate(idx.reshape(len(frames), -1)):
        out[i] = np.bincount(f, minlength=512)
    return out / out.sum(1, keepdims=True)


# ---------------------------------------------------------------- cut detection
def find_cuts(F, fps):
    f = F.astype(np.float32) / 255.0
    n = len(f)
    d = np.zeros(n, np.float32)
    d[1:] = np.abs(f[1:] - f[:-1]).mean(axis=(1, 2, 3))
    H = hist(F)
    hd = np.zeros(n, np.float32)
    hd[1:] = 0.5 * np.abs(H[1:] - H[:-1]).sum(1)

    cuts = []          # (frame, kind, strength)
    W = 12
    for i in range(1, n):
        lo, hi = max(1, i - W), min(n, i + W + 1)
        ctx = np.concatenate([d[lo:i], d[i + 1:hi]])
        local = float(np.median(ctx)) if len(ctx) else 0.0
        peak = d[i] >= d[max(1, i - 2):min(n, i + 3)].max()
        hard = (d[i] > max(0.055, 3.5 * local + 0.02)) or (hd[i] > 0.45 and d[i] > 0.035)
        if hard and peak:
            if cuts and i - cuts[-1][0] < 2:      # one cut per frame pair
                continue
            cuts.append((i, "hard", round(float(d[i]), 3)))

    # Soft transitions (dissolves, whips, fast pushes into a new picture): a big
    # change across ~0.4 s with no single hard jump.
    k = max(3, int(round(fps * 0.2)))
    span = np.zeros(n, np.float32)
    span[k:n - k] = np.abs(f[2 * k:] - f[:n - 2 * k]).mean(axis=(1, 2, 3))
    hard_at = np.array([c[0] for c in cuts]) if cuts else np.array([-999])
    for i in range(k, n - k):
        if span[i] < 0.11 or span[i] < span[max(0, i - k):i + k + 1].max():
            continue
        if np.abs(hard_at - i).min() <= 2 * k:
            continue
        # the picture before and after must be different scenes, not just motion
        if 0.5 * np.abs(H[i + k] - H[i - k]).sum() < 0.25:
            continue
        cuts.append((i, "soft", round(float(span[i]), 3)))
    cuts.sort()
    return cuts, d


def shot_layout_vec(F, a, b):
    idx = [a + int((b - a) * p) for p in (0.25, 0.5, 0.75)]
    idx = [min(max(i, a), b - 1) for i in idx]
    small = F[idx].astype(np.float32).mean(0)
    img = Image.fromarray(small.astype(np.uint8)).resize((12, 21), Image.BILINEAR)
    v = np.asarray(img, np.float32).ravel()
    v = (v - v.mean()) / (v.std() + 1e-6)
    return v, hist(F[idx]).mean(0)


def cluster(shots, F):
    feats = [shot_layout_vec(F, s["f0"], s["f1"]) for s in shots]
    reps, labels = [], []
    for v, h in feats:
        best, bd = None, 9.0
        for ci, (rv, rh) in enumerate(reps):
            dist = 0.5 * (1 - float(np.dot(v, rv)) / len(v)) + 0.5 * 0.5 * float(np.abs(h - rh).sum())
            if dist < bd:
                best, bd = ci, dist
        if best is not None and bd < 0.22:
            labels.append(best)
        else:
            reps.append((v, h))
            labels.append(len(reps) - 1)
    return labels


# ---------------------------------------------------------------- words
def load_words(video, out):
    for cand in (out / "words.json", video.with_suffix(".words.json")):
        if cand.exists() and cand.stat().st_size > 2:
            w = json.loads(cand.read_text())
            if cand != out / "words.json":
                shutil.copy(cand, out / "words.json")
            return w
    exe = shutil.which("transcribe") or str(Path.home() / ".local/bin/transcribe")
    tmp = out / "_tr"
    tmp.mkdir(exist_ok=True)
    print("transcribing (local Parakeet)…", file=sys.stderr)
    subprocess.run([exe, str(video), "--srt", "--out-dir", str(tmp)], check=True,
                   stdout=subprocess.DEVNULL)
    stem = video.stem
    for ext in ("words.json", "txt", "srt"):
        p = tmp / f"{stem}.{ext}"
        if p.exists():
            shutil.move(p, out / ("transcript." + ext if ext != "words.json" else "words.json"))
    shutil.rmtree(tmp, ignore_errors=True)
    return json.loads((out / "words.json").read_text())


def words_in(words, t0, t1):
    return [w for w in words if t0 <= (w["start"] + w["end"]) / 2 < t1]


def cut_word_relation(words, t):
    """Where a cut lands against the voice: on a word start, mid-word, or in a pause."""
    for w in words:
        if w["start"] - 0.001 <= t <= w["end"]:
            off = t - w["start"]
            # ASR word starts are ~80 ms steps and run a little early: within 0.2 s is "on the word"
            return ("on-word" if off <= 0.2 else "mid-word"), round(off, 2), w["word"]
    nxt = next((w for w in words if w["start"] > t), None)
    prv = next((w for w in reversed(words) if w["end"] < t), None)
    if nxt and nxt["start"] - t <= 0.15:
        return "on-word", round(t - nxt["start"], 2), nxt["word"]
    if prv is None and nxt is None:
        return "no-voice", None, ""
    since = t - (prv["end"] if prv else 0)
    return ("word-end" if prv and since <= 0.15 else "in-pause"), round(since, 2), (nxt or prv)["word"]


# ---------------------------------------------------------------- frames + OCR
def grab_frames(video, frame_ids, outdir, width=540):
    """Stream the video once and keep only the frames we need (no select-filter limits)."""
    outdir.mkdir(parents=True, exist_ok=True)
    vw, vh, _, _ = probe(video)
    h = int(round(width * vh / vw / 2)) * 2
    need = set(frame_ids)
    last = max(need)
    size = width * h * 3
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={width}:{h}",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    mapping, i = {}, 0
    while i <= last:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        if i in need:
            dest = outdir / f"f{i:05d}.jpg"
            Image.frombuffer("RGB", (width, h), buf).save(dest, quality=88)
            mapping[i] = dest
        i += 1
    proc.kill()
    proc.wait()
    for fid in need - mapping.keys():          # past the end: reuse the last frame we have
        mapping[fid] = mapping[max(k for k in mapping if k <= fid)] if any(k <= fid for k in mapping) else None
    return mapping


def ocr(path):
    if not shutil.which("tesseract"):
        return ""
    img = Image.open(path).convert("L")
    w, h = img.size
    img = img.resize((w * 2 // 1, h * 2 // 1)) if w < 900 else img
    tmp = Path(str(path) + ".ocr.png")
    img.save(tmp)
    r = subprocess.run(["tesseract", str(tmp), "-", "--psm", "11"], capture_output=True, text=True,
                       env={**os.environ, "OMP_THREAD_LIMIT": "1"})  # one thread each; run many at once
    tmp.unlink(missing_ok=True)
    txt = " ".join(t for t in re.split(r"\s+", r.stdout) if re.search(r"[A-Za-z0-9]{2,}", t))
    return txt.strip()[:160]


# ---------------------------------------------------------------- sheets
def wrap(text, fnt, width, draw, max_lines):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][:-1] + "…"
    return lines


def shot_sheets(shots, frames, out, vw, vh, per=12, cols=4):
    tw = 170 if vh > vw else 260                      # thumb width
    th = int(tw * vh / vw)
    cell_w, pad = tw * 3 + 8, 14
    f_small, f_lab = font(17), font(19, bold=True)
    head_h, text_h = 30, 96
    cell_h = head_h + th + text_h
    sheets = []
    for si in range(0, len(shots), per):
        group = shots[si:si + per]
        rows = (len(group) + cols - 1) // cols
        W = cols * (cell_w + pad) + pad
        H = rows * (cell_h + pad) + pad + 40
        sheet = Image.new("RGB", (W, H), "#0e0e10")
        dr = ImageDraw.Draw(sheet)
        dr.text((pad, 10), f"shots {group[0]['id']}–{group[-1]['id']}   {tc(group[0]['start'])}–{tc(group[-1]['end'])}"
                "   (start · middle · end frame of each shot)", fill="#f4f4f5", font=f_lab)
        for k, s in enumerate(group):
            x = pad + (k % cols) * (cell_w + pad)
            y = 40 + pad + (k // cols) * (cell_h + pad)
            flags = []
            if s.get("cut_in") == "soft":
                flags.append("SOFT")
            if s.get("split"):
                flags.append(f"SPLIT@{int(s['split'] * 100)}%")
            if s.get("same_as_prev"):
                flags.append("JUMP")
            head = f"#{s['id']}  {tc(s['start'])}  {s['dur']:.1f}s  {s['cluster']}  {s['motion']}  {' '.join(flags)}"
            dr.rectangle([x, y, x + cell_w, y + cell_h], fill="#18181b")
            dr.text((x + 6, y + 5), head, fill="#fde68a" if flags else "#f4f4f5", font=f_small)
            for j, fid in enumerate(s["thumbs"]):
                im = Image.open(frames[fid]).convert("RGB").resize((tw, th))
                sheet.paste(im, (x + j * (tw + 4), y + head_h))
            words = " ".join(w["word"] for w in s["words"]) or "—"
            for li, line in enumerate(wrap(words, f_small, cell_w - 12, dr, 4)):
                dr.text((x + 6, y + head_h + th + 4 + li * 22), line, fill="#a1a1aa", font=f_small)
        p = out / "sheets" / f"shots_{si // per + 1:02d}.jpg"
        p.parent.mkdir(exist_ok=True)
        sheet.save(p, quality=85)
        sheets.append(p)
    return sheets


def cluster_sheet(shots, frames, out, vw, vh, max_examples=6):
    by = {}
    for s in shots:
        by.setdefault(s["cluster"], []).append(s)
    order = sorted(by, key=lambda c: (-len(by[c]), int(c[1:])))
    tw = 120 if vh > vw else 200
    th = int(tw * vh / vw)
    f_lab = font(18, bold=True)
    row_h = th + 34
    W = 260 + max_examples * (tw + 6) + 20
    sheets, per_sheet = [], 8
    for pi in range(0, len(order), per_sheet):
        part = order[pi:pi + per_sheet]
        img = Image.new("RGB", (W, len(part) * (row_h + 10) + 20), "#0e0e10")
        dr = ImageDraw.Draw(img)
        for r, c in enumerate(part):
            mem = by[c]
            y = 10 + r * (row_h + 10)
            tot = sum(m["dur"] for m in mem)
            dr.text((10, y + 4), f"{c}", fill="#fde68a", font=font(26, bold=True))
            dr.text((10, y + 40), f"{len(mem)} shots · {tot:.1f}s", fill="#f4f4f5", font=f_lab)
            dr.text((10, y + 64), "#" + ",".join(str(m["id"]) for m in mem[:14]) + ("…" if len(mem) > 14 else ""),
                    fill="#a1a1aa", font=font(14))
            step = max(1, len(mem) // max_examples)
            for j, m in enumerate(mem[::step][:max_examples]):
                im = Image.open(frames[m["thumbs"][1]]).convert("RGB").resize((tw, th))
                img.paste(im, (260 + j * (tw + 6), y))
        p = out / "sheets" / f"clusters_{pi // per_sheet + 1:02d}.jpg"
        img.save(p, quality=85)
        sheets.append(p)
    return sheets


# ---------------------------------------------------------------- analyze
def analyze(args):
    video = Path(args.video).resolve()
    out = Path(args.out).resolve() if args.out else video.parent / f"{video.stem}.breakdown"
    out.mkdir(parents=True, exist_ok=True)
    vw, vh, fps, dur = probe(video)
    sw = 64
    sh = int(round(sw * vh / vw / 2)) * 2
    print(f"{vw}x{vh} {fps:.3g}fps {dur:.1f}s — decoding…", file=sys.stderr)

    with ThreadPoolExecutor(1) as ex:
        words_job = ex.submit(load_words, video, out)
        F = decode_small(video, sw, sh)
        cuts, d = find_cuts(F, fps)
        words = words_job.result()

    n = len(F)
    bounds = [0] + [c[0] for c in cuts] + [n]
    kinds = ["start"] + [c[1] for c in cuts]
    shots = []
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        if b <= a:
            continue
        inner = d[a + 1:b]
        mot = float(np.mean(inner)) if len(inner) else 0.0
        shots.append(dict(id=len(shots) + 1, f0=a, f1=b, start=round(a / fps, 3), end=round(b / fps, 3),
                          dur=round((b - a) / fps, 3), cut_in=kinds[i], motion_score=round(mot, 4),
                          motion="static" if mot < 0.006 else "moving" if mot < 0.025 else "busy"))
    labels = cluster(shots, F)
    counts = {}
    for l in labels:
        counts[l] = counts.get(l, 0) + 1
    # name clusters by first appearance
    names, nxt = {}, 1
    for l in labels:
        if l not in names:
            names[l] = f"c{nxt}"
            nxt += 1
    for s, l in zip(shots, labels):
        s["cluster"] = names[l]
        s["recurring"] = counts[l] > 1
        a, b = s["f0"], s["f1"]
        s["thumbs"] = [a + min(1, b - a - 1), (a + b) // 2, max(a, b - 2)]
        s["words"] = words_in(words, s["start"], s["end"])
    for i in range(1, len(shots)):
        shots[i]["same_as_prev"] = shots[i]["cluster"] == shots[i - 1]["cluster"]
        rel, off, w = cut_word_relation(words, shots[i]["start"])
        shots[i]["cut_vs_voice"] = dict(kind=rel, offset=off, word=w)

    print(f"{len(shots)} shots, {len(names)} groups — grabbing frames…", file=sys.stderr)
    frames = grab_frames(video, [f for s in shots for f in s["thumbs"]], out / "frames")
    if not args.no_ocr and shutil.which("tesseract"):
        with ThreadPoolExecutor(os.cpu_count() or 8) as ex:
            texts = list(ex.map(lambda s: ocr(frames[s["thumbs"][1]]), shots))
        for s, t in zip(shots, texts):
            s["ocr"] = t
    ss = shot_sheets(shots, frames, out, vw, vh)
    cs = cluster_sheet(shots, frames, out, vw, vh)

    meta = dict(video=str(video), width=vw, height=vh, fps=round(fps, 3), duration=round(dur, 3),
                words=len(words), wpm=round(len(words) / dur * 60) if dur else 0, shots=len(shots),
                hard_cuts=sum(1 for c in cuts if c[1] == "hard"), soft_cuts=sum(1 for c in cuts if c[1] == "soft"),
                groups=len(names))
    (out / "shots.json").write_text(json.dumps(dict(meta=meta, shots=shots), indent=1))
    lab = out / "labels.json"
    if not lab.exists():
        by = {}
        for s in shots:
            by.setdefault(s["cluster"], []).append(s["id"])
        lab.write_text(json.dumps({
            "_help": "Give every group a type (" + ", ".join(TYPES) + ") and a short label "
                     "(who/what, framing). Override single shots under 'shots'. 'merge' joins shots "
                     "the detector split by mistake (e.g. [12, 13]); 'drop_cuts' removes false cuts by the "
                     "id of the shot they start. 'sections' names the beats: [[start_sec, 'Hook'], …].",
            "groups": {c: {"type": "", "label": "", "shots": ids} for c, ids in by.items()},
            "shots": {}, "drop_cuts": [], "sections": [],
        }, indent=1))
    print(json.dumps(meta))
    print(f"OUT={out}")
    for p in cs:
        print(f"GROUP_SHEET {p}")
    for p in ss:
        print(f"SHOT_SHEET {p}")


# ---------------------------------------------------------------- report
def load_labeled(out):
    data = json.loads((out / "shots.json").read_text())
    lab = json.loads((out / "labels.json").read_text())
    shots = data["shots"]
    drop = set(int(x) for x in lab.get("drop_cuts", []))
    merged = []
    for s in shots:
        if merged and s["id"] in drop:
            p = merged[-1]
            p["end"] = s["end"]
            p["dur"] = round(p["end"] - p["start"], 3)
            p["words"] += s["words"]
            p["merged"] = p.get("merged", [p["id"]]) + [s["id"]]
            continue
        merged.append(dict(s))
    over = {}
    for k, v in lab.get("shots", {}).items():          # keys "12" or ranges "12-30"
        a, _, b = str(k).partition("-")
        for i in range(int(a), int(b or a) + 1):
            over[str(i)] = {**over.get(str(i), {}), **v}
    for s in merged:
        g = lab["groups"].get(s["cluster"], {})
        o = over.get(str(s["id"]), {})
        s["type"] = (o.get("type") or g.get("type") or "other").strip()
        s["label"] = (o.get("label") or g.get("label") or "").strip()
        s["note"] = o.get("note", "")
    secs = sorted(lab.get("sections", []), key=lambda x: x[0])
    for s in merged:
        name = ""
        for t, nm in secs:
            if s["start"] + 0.01 >= t:
                name = nm
        s["section"] = name
    return data["meta"], merged, secs


def is_speaker(t):
    return t in ("talking-head", "two-shot", "split", "story")


def report(args):
    out = Path(args.dir).resolve()
    meta, shots, secs = load_labeled(out)
    unl = [s["id"] for s in shots if s["type"] == "other" and not s["label"]]
    dur = meta["duration"]
    L = []
    L.append(f"# Rhythm map · {Path(meta['video']).name}\n")
    L.append(f"{meta['width']}x{meta['height']}, {meta['fps']} fps, {dur:.1f} s · {meta['words']} words "
             f"(~{meta['wpm']} wpm) · **{len(shots)} shots**, average {dur / len(shots):.2f} s\n")

    # share by type
    L.append("## What is on screen, by type\n")
    L.append("| Type | Shots | Time | Share | Avg shot | Median |")
    L.append("|---|---:|---:|---:|---:|---:|")
    by = {}
    for s in shots:
        by.setdefault(s["type"], []).append(s["dur"])
    for t, ds in sorted(by.items(), key=lambda kv: -sum(kv[1])):
        L.append(f"| {t} | {len(ds)} | {sum(ds):.1f} s | {sum(ds) / dur * 100:.0f}% | {st.mean(ds):.2f} s | {st.median(ds):.2f} s |")

    # insert cadence
    ins = [s for s in shots if not is_speaker(s["type"]) and s["type"] != "transition"]
    spk = [s for s in shots if is_speaker(s["type"])]
    L.append("\n## Insert cadence\n")
    if ins:
        # runs of consecutive inserts = one "insert block" between speaker shots
        blocks, cur = [], []
        for s in shots:
            if s["type"] == "transition":
                continue
            if is_speaker(s["type"]):
                if cur:
                    blocks.append(cur)
                    cur = []
            else:
                cur.append(s)
        if cur:
            blocks.append(cur)
        starts = [b[0]["start"] for b in blocks]
        gaps = [b - a for a, b in zip(starts, starts[1:])]
        L.append(f"- **{len(blocks)} insert blocks** ({len(ins)} insert shots) over {dur:.0f} s: "
                 f"one every **{dur / len(blocks):.1f} s** on average"
                 + (f", gap median {st.median(gaps):.1f} s (min {min(gaps):.1f}, max {max(gaps):.1f})." if gaps else "."))
        bl = [sum(x["dur"] for x in b) for b in blocks]
        L.append(f"- Block length: median {st.median(bl):.1f} s, {st.mean([len(b) for b in blocks]):.1f} shots a block.")
        if spk:
            sd = [s["dur"] for s in spk]
            L.append(f"- Spine shots (speaker or story): median {st.median(sd):.1f} s, longest {max(sd):.1f} s "
                     f"(#{max(spk, key=lambda s: s['dur'])['id']}).")
        first = ins[0]
        L.append(f"- First insert at {tc(first['start'])} (#{first['id']}, {first['type']}).")
    else:
        L.append("- No inserts: the speaker carries the whole video.")

    wps = [len(s["words"]) for s in shots if s["type"] != "transition"]
    if wps:
        L.append(f"- Words a shot (pace): median {st.median(wps):.0f}, "
                 f"{sum(1 for w in wps if w <= 3) / len(wps) * 100:.0f}% of shots carry 3 words or fewer, "
                 f"{sum(1 for w in wps if w == 0) / len(wps) * 100:.0f}% carry none.")

    # cut timing against the voice
    rel = [s.get("cut_vs_voice") for s in shots[1:] if s.get("cut_vs_voice")]
    if rel:
        kinds = {}
        for r in rel:
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
        L.append("\n## Cuts against the voice\n")
        L.append("- " + ", ".join(f"{k}: {v} ({v / len(rel) * 100:.0f}%)" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])))
        ins_rel = [s["cut_vs_voice"]["kind"] for s in shots[1:] if not is_speaker(s["type"]) and s.get("cut_vs_voice")]
        if ins_rel:
            ow = ins_rel.count("on-word")
            L.append(f"- Into an insert: {ow}/{len(ins_rel)} land on a word start.")

    # by section
    if secs:
        L.append("\n## By section\n")
        L.append("| Section | Time | Shots | Avg shot | Speaker share | Inserts (types) |")
        L.append("|---|---|---:|---:|---:|---|")
        names = [nm for _, nm in secs]
        for i, (t0, nm) in enumerate(secs):
            t1 = secs[i + 1][0] if i + 1 < len(secs) else dur
            ss = [s for s in shots if s["section"] == nm]
            if not ss:
                continue
            sp = sum(s["dur"] for s in ss if is_speaker(s["type"]))
            tl = sum(s["dur"] for s in ss)
            ty = {}
            for s in ss:
                if not is_speaker(s["type"]):
                    ty[s["type"]] = ty.get(s["type"], 0) + 1
            L.append(f"| {nm} | {tc(t0)}–{tc(t1)} | {len(ss)} | {tl / len(ss):.1f} s | {sp / tl * 100:.0f}% | "
                     + (", ".join(f"{k} {v}" for k, v in ty.items()) or "—") + " |")

    # shot table
    L.append("\n## Shot list\n")
    L.append("| # | Time | Dur | Type | What | Cut in | VO words |")
    L.append("|---:|---|---:|---|---|---|---|")
    for s in shots:
        cv = s.get("cut_vs_voice") or {}
        cut = s.get("cut_in", "")
        if cv:
            cut += f", {cv['kind']}"
        if s.get("split"):
            cut += f", split {int(s['split'] * 100)}%"
        words = " ".join(w["word"] for w in s["words"])
        what = s["label"] + (f" — {s['note']}" if s["note"] else "")
        if s.get("ocr") and s["type"] == "text":
            what += f" · text: “{s['ocr'][:60]}”"
        L.append(f"| {s['id']} | {tc(s['start'])} | {s['dur']:.1f} | {s['type']} | {what} | {cut} | {words} |")
    (out / "rhythm.md").write_text("\n".join(L) + "\n")
    timeline_png(shots, dur, out / "timeline.png", secs)
    (out / "shots.labeled.json").write_text(json.dumps(dict(meta=meta, shots=shots), indent=1))
    print(f"wrote {out / 'rhythm.md'}\nwrote {out / 'timeline.png'}")
    if unl:
        print(f"WARNING unlabeled shots (typed 'other'): {unl[:40]}")


def timeline_png(shots, dur, path, secs, per_row=30.0):
    rows = int(np.ceil(dur / per_row))
    W, left, bar_h, row_h = 1800, 70, 54, 120
    px = (W - left - 20) / per_row
    img = Image.new("RGB", (W, 70 + rows * row_h + 60), "#0e0e10")
    dr = ImageDraw.Draw(img)
    dr.text((left, 16), "Timeline · colour = shot type · thin dividers = cuts", fill="#f4f4f5", font=font(22, bold=True))
    f_s = font(14)
    for r in range(rows):
        y = 70 + r * row_h
        t0 = r * per_row
        dr.text((8, y + 18), tc(t0), fill="#a1a1aa", font=f_s)
        for s in shots:
            a, b = max(s["start"], t0), min(s["end"], t0 + per_row)
            if b <= a:
                continue
            x0, x1 = left + (a - t0) * px, left + (b - t0) * px
            dr.rectangle([x0, y, x1, y + bar_h], fill=TYPES.get(s["type"], "#94a3b8"), outline="#0e0e10")
            if x1 - x0 > 26 and s["start"] >= t0:
                dr.text((x0 + 3, y + 3), str(s["id"]), fill="#0e0e10", font=f_s)
        for t, nm in secs:
            if t0 <= t < t0 + per_row:
                x = left + (t - t0) * px
                dr.line([x, y - 6, x, y + bar_h + 6], fill="#ffffff", width=3)
                dr.text((x + 4, y + bar_h + 8), nm, fill="#ffffff", font=font(15, bold=True))
        for k in range(0, int(per_row) + 1, 5):
            x = left + k * px
            dr.line([x, y + bar_h, x, y + bar_h + 4], fill="#52525b")
    x, y = left, 70 + rows * row_h + 10
    used = sorted({s["type"] for s in shots})
    for t in used:
        dr.rectangle([x, y, x + 22, y + 22], fill=TYPES.get(t, "#94a3b8"))
        dr.text((x + 28, y + 2), t, fill="#f4f4f5", font=font(16))
        x += 40 + dr.textlength(t, font=font(16))
    img.save(path)


# ---------------------------------------------------------------- map onto our script
def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def script_words(path, hook=1):
    """Spoken words of our script: one hook (HOOK n) + the body, without titles,
    beat headings or speaker tags. A words.json (our real VO) is used as is."""
    p = Path(path)
    if p.suffix == ".json":
        return [dict(word=w["word"], start=w["start"], end=w["end"]) for w in json.loads(p.read_text())]
    if p.suffix == ".pdf":
        text = subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True).stdout
    else:
        text = p.read_text()
    lines = [re.sub(r"\\([\\.\-!#*_()\[\]])", r"\1", l).replace("**", "") for l in text.splitlines()]
    label = re.compile(r"^\s*#*\s*(HOOK\s*(\d+)|Beats?\s*\d+|SCRIPT BODY|Body|CTA|Hooks?)\b", re.I)
    has_hooks = any(re.match(r"^\s*#*\s*HOOK\s*\d", l, re.I) for l in lines)
    keep = not has_hooks           # with hooks: skip the title block until a hook/body starts
    toks = []
    for line in lines:
        m = label.match(line)
        if m:
            keep = (int(m.group(2)) == hook) if m.group(2) else (keep if m.group(1).lower().startswith("hook") else True)
            # "Beat 3: I body oil." keeps the speech after the colon; an ALL-CAPS heading
            # ("BEAT 3 · FRAMEWORK + GENERATION 1: LUBE") is dropped whole.
            rest = line.split(":", 1)[1] if ":" in line and not line.strip().isupper() else ""
            if not (keep and rest.strip()):
                continue
            line = rest
        if not keep:
            continue
        if line.strip().isupper() and "·" in line:
            continue
        line = re.sub(r"^\s*(HOST|GUEST|[A-Z][A-Z .]{1,20})\s*:", " ", line)    # speaker tags
        toks += [dict(word=w) for w in line.split() if re.search(r"\w", w)]
    return toks


def map_cmd(args):
    out = Path(args.dir).resolve()
    meta, shots, secs = load_labeled(out)
    ours = script_words(args.vo or args.script, args.hook)
    ref_words = []
    for s in shots:
        for w in s["words"]:
            ref_words.append((s["id"], w))
    A = [norm(w["word"]) for _, w in ref_words]
    B = [norm(w["word"]) for w in ours]
    sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
    amap = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            amap[blk.a + k] = blk.b + k
    matched = len(amap) / max(1, len(A))
    # Anchors (ref word index -> our word index) from runs of >= 2 matching words, kept
    # monotone; every reference cut is then placed on our words by interpolating between
    # anchors, so each of our words lands in exactly one reference shot.
    anchors = [(-1, -1)]
    for blk in sm.get_matching_blocks():
        if blk.size >= 2 or (blk.size == 1 and len(A[blk.a]) > 3):
            for k in range(blk.size):
                if blk.b + k > anchors[-1][1]:
                    anchors.append((blk.a + k, blk.b + k))
    anchors.append((len(A), len(B)))
    ax = np.array([x for x, _ in anchors], float)
    ay = np.array([y for _, y in anchors], float)

    def to_ours(i):
        return int(round(np.interp(i, ax, ay)))

    first, i = {}, 0
    for sid, _ in ref_words:
        first.setdefault(sid, i)
        i += 1
    rows = []
    for k, s in enumerate(shots):
        if s["id"] not in first:
            rows.append((s, None, None, "(no words: pause / music)"))
            continue
        b0 = to_ours(first[s["id"]]) if rows or k else 0
        nxt = next((first[t["id"]] for t in shots[k + 1:] if t["id"] in first), len(A))
        b1 = to_ours(nxt) - 1
        if b1 < b0:
            rows.append((s, None, None, "(no words of ours: drop or merge this shot)"))
            continue
        rows.append((s, b0, b1, " ".join(w["word"] for w in ours[b0:b1 + 1])))
    L = [f"# Reference pattern on our script\n",
         f"{matched * 100:.0f}% of the reference words found in ours. Each row is one reference shot: "
         "put the same kind of picture on our words.\n"]
    has_t = args.vo is not None
    L.append("| Ref # | Ref time | Type | Reference shot | Our words" + (" | Our time |" if has_t else " |"))
    L.append("|---:|---|---|---|---" + ("|---|" if has_t else "|"))
    for s, b0, b1, words in rows:
        t = ""
        if has_t and b0 is not None:
            t = f" {tc(ours[b0]['start'])}–{tc(ours[b1]['end'])} |"
        elif has_t:
            t = " |"
        L.append(f"| {s['id']} | {tc(s['start'])} ({s['dur']:.1f}s) | {s['type']} | {s['label']} | {words} |{t}")
    # words in ours that no reference shot covered (new lines)
    covered = set()
    for _, b0, b1, _ in rows:
        if b0 is not None:
            covered.update(range(b0, b1 + 1))
    gaps, cur = [], []
    for k, w in enumerate(ours):
        if k in covered:
            if cur:
                gaps.append(cur)
                cur = []
        else:
            cur.append(w["word"])
    if cur:
        gaps.append(cur)
    gaps = [g for g in gaps if len(g) >= 4]
    if gaps:
        L.append("\n## Our lines with no reference shot (new copy: pick the pattern from the nearest beat)\n")
        for g in gaps:
            L.append(f"- {' '.join(g)}")
    dest = out / ("pattern-on-vo.md" if has_t else "pattern-on-script.md")
    dest.write_text("\n".join(L) + "\n")
    print(f"matched {matched * 100:.0f}% of reference words\nwrote {dest}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze")
    a.add_argument("video")
    a.add_argument("--out")
    a.add_argument("--no-ocr", action="store_true")
    r = sub.add_parser("report")
    r.add_argument("dir")
    m = sub.add_parser("map")
    m.add_argument("dir")
    m.add_argument("script", help="our script (.txt/.md/.pdf) or our VO words.json")
    m.add_argument("--vo", help="our real voiceover words.json (gives real times)")
    m.add_argument("--hook", type=int, default=1, help="which HOOK n of the script to use (default 1)")
    args = ap.parse_args()
    {"analyze": analyze, "report": report, "map": map_cmd}[args.cmd](args)


if __name__ == "__main__":
    main()
