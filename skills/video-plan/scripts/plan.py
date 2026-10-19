#!/usr/bin/env python3
"""Plan a short video from a client brief: folders, voiceover timing, and PLAN.pdf from PLAN.md.

  plan.py init CLIENT_DIR [video-N]            brief/, video-N/PLAN.md, video-N/voiceover/ (never overwrites)
  plan.py voiceover VIDEO_DIR [--voices WORD]  time each line of VIDEO_DIR/voiceover/script.md:
                                               the real voiceover/recording.* if present (transcribe skill),
                                               otherwise a Cartesia scratch read; writes
                                               voiceover/timing.md
  plan.py voiceover VIDEO_DIR --on-camera      lines spoken inside the clips (Flow makes the voice): time each
                                               from its word count, no Cartesia; writes voiceover/timing.md
  plan.py pdf VIDEO_DIR                        PLAN.pdf from PLAN.md (rerun after every edit); first rewrites
                                               the summary line under the title (shots, length, average and
                                               longest shot) and flags gaps, overlaps and shots over 10 s

Settings come from VIDEO_DIR/project.conf when it exists (CARTESIA_VOICE, CARTESIA_SPEED,
CARTESIA_MODEL, CARTESIA_API_KEY). The key falls back to $CARTESIA_API_KEY, then
~/.config/cartesia/api_key.
"""
import argparse
import difflib
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CLIP_LENGTHS = (4, 6, 8, 10)
HEADROOM = 1.0  # seconds of picture past a line's slot; a clip that is too long only gets trimmed
TIME = re.compile(r"^([\d.]+)\s*[–-]\s*([\d.]+)\s*s$")  # a shot's Time cell: "12.6 – 14.4 s"
ON_CAMERA_WPS = 3.2  # words per second Flow speaks a line asked for "at a brisk, natural pace" (Mysa video 2, measured: 3.0-3.3)
ON_CAMERA_HEADROOM = 0.5  # the clip ends this soon after the last word; the character holds the pose
LINE_GAP = 0.4  # pause between lines in the scratch read
CARTESIA = "https://api.cartesia.ai"
CARTESIA_VERSION = "2026-08-14"
BROWSERS = ["chromium", "google-chrome-stable", "google-chrome", "chrome", "brave"]


def die(msg):
    sys.exit(f"error: {msg}")


def conf(video):
    c = {"CARTESIA_API_KEY": "", "CARTESIA_MODEL": "sonic-3.6", "CARTESIA_VOICE": "a33f7a4c-100f-41cf-a1fd-5822e8fc253f",
         "CARTESIA_SPEED": "1.0"}
    p = video / "project.conf"
    if p.is_file():
        for line in p.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                k, v = line.split("=", 1)
                if v.strip():
                    c[k.strip()] = v.strip().strip("\"'")
    key_file = Path.home() / ".config" / "cartesia" / "api_key"
    c["CARTESIA_API_KEY"] = (c["CARTESIA_API_KEY"] or os.environ.get("CARTESIA_API_KEY", "")
                             or (key_file.read_text().strip() if key_file.is_file() else ""))
    return c


def ffprobe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


# ---------- init ----------

def cmd_init(args):
    root = Path(args.client).expanduser().resolve()
    video = root / args.video
    for d in (root / "brief", video / "voiceover"):
        d.mkdir(parents=True, exist_ok=True)
    plan = video / "PLAN.md"
    if not plan.exists():
        shutil.copy(SKILL / "templates" / "PLAN.md", plan)
        print(f"created {plan.relative_to(root)}")
    script = video / "voiceover" / "script.md"
    if not script.exists():
        script.write_text("# Voiceover script: one spoken line per row, in story order, worded exactly as the client wrote it\n")
        print(f"created {script.relative_to(root)}")
    print(f"\nClient: {root}\nVideo:  {video}")


# ---------- voiceover timing ----------

def real_voiceover(video):
    return next((p for ext in ("wav", "mp3", "m4a", "aac") for p in [video / "voiceover" / f"recording.{ext}"] if p.is_file()), None)


def script_lines(video):
    p = video / "voiceover" / "script.md"
    if not p.is_file():
        die(f"write the voiceover script to {p} first: one spoken line per row, in story order")
    lines = []
    for raw in p.read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(re.sub(r"^(\d+[.)]|[-*])\s+", "", s).strip().strip('"“”'))
    if not lines:
        die(f"{p} has no lines")
    return lines


def cartesia(c, path, body=None):
    if not c["CARTESIA_API_KEY"]:
        die("no Cartesia key: save it once to ~/.config/cartesia/api_key (chmod 600), or put the real voiceover at voiceover/recording.wav")
    req = urllib.request.Request(CARTESIA + path, data=json.dumps(body).encode() if body else None, headers={
        "Cartesia-Version": CARTESIA_VERSION, "Authorization": f"Bearer {c['CARTESIA_API_KEY']}",
        "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        die(f"Cartesia {e.code}: {e.read().decode(errors='replace')[:300]}")


def scratch_read(c, video, lines):
    """One Cartesia read per line (cached by text, voice and speed), joined into voiceover/scratch.wav."""
    rate, width = 44100, 2  # raw 16-bit mono PCM: Cartesia's streamed WAV header has no real length
    folder = video / "voiceover" / "lines"
    folder.mkdir(parents=True, exist_ok=True)
    pcm = []
    for i, text in enumerate(lines, 1):
        key = hashlib.sha1("|".join([text, c["CARTESIA_MODEL"], c["CARTESIA_VOICE"], c["CARTESIA_SPEED"]]).encode()).hexdigest()[:8]
        f = folder / f"{i:02d}-{key}.pcm"
        if not f.is_file():
            print(f"reading line {i}: {text}")
            f.write_bytes(cartesia(c, "/tts/bytes", {
                "model_id": c["CARTESIA_MODEL"], "transcript": text, "language": "en",
                "voice": {"mode": "id", "id": c["CARTESIA_VOICE"]},
                "output_format": {"container": "raw", "encoding": "pcm_s16le", "sample_rate": rate},
                "generation_config": {"speed": float(c["CARTESIA_SPEED"])}}))
        pcm.append(f)
    for old in folder.iterdir():
        old in pcm or old.unlink()
    dest = video / "voiceover" / "scratch.wav"
    gap = b"\0" * (int(LINE_GAP * rate) * width)
    timings, t = [], 0.0
    with wave.open(str(dest), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(width)
        out.setframerate(rate)
        for i, f in enumerate(pcm):
            data = f.read_bytes()
            d = len(data) / (rate * width)
            out.writeframes(data + (gap if i < len(pcm) - 1 else b""))
            timings.append((t, t + d))
            t += d + LINE_GAP
    return dest, timings


def heard_times(audio, lines):
    """Start and end of each script line in the real voiceover, from speech-to-text word timestamps (transcribe skill)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "transcribe" / "scripts"))
    try:
        from transcribe import words
    except ImportError:
        die("needs the transcribe skill next to this one (skills/transcribe), used to time the real voiceover")
    print(f"transcribing {audio.name} ...")
    norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower())
    heard = [(norm(w), s, e) for w, s, e in words(audio) if norm(w)]
    script = [(i, norm(w)) for i, line in enumerate(lines) for w in line.split() if norm(w)]
    matched = {}
    sm = difflib.SequenceMatcher(None, [s[1] for s in script], [h[0] for h in heard], autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            matched[a + k] = heard[b + k][1:]
    timings = []
    for i in range(len(lines)):
        ts = [matched[k] for k, (li, _) in enumerate(script) if li == i and k in matched]
        timings.append((min(s for s, _ in ts), max(e for _, e in ts)) if ts else None)
    return timings


def clip_for(seconds):
    return next((n for n in CLIP_LENGTHS if n >= seconds + HEADROOM), None)


def on_camera_timing(video, lines):
    """Lines spoken by characters inside the clip: Flow makes the voice, so time each line from its word count."""
    rows = ["| Line | Words | Length | Clips | Text |", "|---|---|---|---|---|"]
    total = sum(len(t.split()) for t in lines) / ON_CAMERA_WPS
    for i, text in enumerate(lines, 1):
        words = len(text.split())
        length = words / ON_CAMERA_WPS
        clip = next((n for n in CLIP_LENGTHS if n >= length + ON_CAMERA_HEADROOM), None)
        if clip:
            clips = f"{clip} s"
        else:  # the fewest clips of up to 10 s, each holding whole sentences
            n = -(-(length + ON_CAMERA_HEADROOM) // 10)
            clips = f"split into {int(n)} × 10 s at a sentence break"
        rows.append(f"| {i} | {words} | {length:.1f} s | {clips} | {text} |")
    body = (f"# Line timing (spoken on camera)\n\nSource: word count. Length {total:.1f} s of speech.\n\nFlow generates the voice inside each clip, so each line is timed from "
            f"its word count at {ON_CAMERA_WPS:g} words a second, a brisk delivery. Clips is the shortest Flow length that "
            f"holds the line plus {ON_CAMERA_HEADROOM:g} s; a longer line gets the fewest 10 s clips, split only at a sentence break, "
            f"chained so it plays as one shot.\n\n" + "\n".join(rows) + "\n")
    (video / "voiceover" / "timing.md").write_text(body)
    print(body + f"\n{video / 'voiceover' / 'timing.md'}")


def cmd_voiceover(args):
    video = Path(args.video).expanduser().resolve()
    c = conf(video)
    if args.on_camera:
        return on_camera_timing(video, script_lines(video))
    if args.voices is not None:
        q = urllib.parse.urlencode({"limit": 100, **({"q": args.voices} if args.voices else {})})
        for v in json.loads(cartesia(c, f"/voices?{q}"))["data"]:
            if v.get("language") == "en":
                print(f"{v['id']}  {v['name']:<14} {(v.get('description') or '')[:80]}")
        return
    lines = script_lines(video)
    audio = real_voiceover(video)
    if audio:
        timings, source = heard_times(audio, lines), f"{audio.name} (the real voiceover, timed with speech-to-text)"
    else:
        audio, timings = scratch_read(c, video, lines)
        source = f"{audio.name} (Cartesia scratch read, voice {c['CARTESIA_VOICE']}, speed {c['CARTESIA_SPEED']})"
    total = ffprobe_duration(audio)
    starts = [tm[0] for tm in timings if tm]
    rows = ["| Line | In | Out | Slot | Clip | Text |", "|---|---|---|---|---|---|"]
    for i, (text, tm) in enumerate(zip(lines, timings), 1):
        if tm is None:
            rows.append(f"| {i} | ? | ? | ? | ? | {text} (not found in the audio: check the script matches the recording) |")
            continue
        start, end = tm
        slot = next((s for s in starts if s > start), total) - start  # until the next line starts
        clip = clip_for(slot)
        rows.append(f"| {i} | {start:.1f} | {end:.1f} | {slot:.1f} s | {f'{clip} s' if clip else 'split'} | {text} |")
    body = (f"# Voiceover timing\n\nSource: `{source}`. Length {total:.1f} s.\n\n"
            f"Slot runs from the line's start to the next line's start (the last one to the end of the audio): the picture "
            f"under that line must cover it. Clip is the shortest Flow length that holds the slot plus {HEADROOM:.0f} s. "
            f"A line marked split needs two or more shots whose lengths add up to at least the slot plus {HEADROOM:.0f} s. "
            f"In and Out are the caption in/out times.\n\n" + "\n".join(rows) + "\n")
    (video / "voiceover" / "timing.md").write_text(body)
    print(body + f"\n{video / 'voiceover' / 'timing.md'}")


# ---------- PLAN.pdf ----------

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def md_to_html(md, base):
    """The Markdown PLAN.md uses: headings, paragraphs, lists, tables, bold, italics, code, images."""
    out, lines, i = [], [l for l in md.splitlines() if not l.strip().startswith("<!--")], 0
    cell = lambda row: [c.strip() for c in row.strip().strip("|").split("|")]
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif m := re.match(r"^(#{1,4})\s+(.*)", line):
            n = len(m[1])
            out.append(f"<h{n}>{inline(m[2])}</h{n}>")
            i += 1
        elif line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = cell(line)
            i += 2
            body = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                body.append(cell(lines[i]))
                i += 1
            cls = " ".join(re.sub(r"[^a-z]+", "-", h.lower()).strip("-") for h in head)
            out.append(f'<table class="{cls}"><thead><tr>' + "".join(f"<th>{inline(h)}</th>" for h in head) + "</tr></thead><tbody>")
            for r in body:
                cells = []
                for c in r:
                    img = re.fullmatch(r"!\[[^\]]*\]\(([^)]+)\)", c)
                    if img and (base / img[1]).is_file():
                        cells.append(f'<td><img src="{(base / img[1]).resolve().as_uri()}"></td>')
                    else:
                        cells.append(f"<td>{inline(c)}</td>")
                out.append("<tr>" + "".join(cells) + "</tr>")
            out.append("</tbody></table>")
        elif re.match(r"^\s*([-*]|\d+\.)\s+", line):
            tag = "ol" if re.match(r"^\s*\d+\.", line) else "ul"
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))
                i += 1
            box = lambda x: re.sub(r"^\[([ xX])\]\s*", lambda m: "☑ " if m[1] != " " else "☐ ", x)
            cls = ' class="checks"' if all(re.match(r"^\[[ xX]\]", x) for x in items) else ""
            out.append(f"<{tag}{cls}>" + "".join(f"<li>{inline(box(x))}</li>" for x in items) + f"</{tag}>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\s*\||\s*([-*]|\d+\.)\s)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 14mm; }
body { font: 10pt Arial, sans-serif; color: #000; background: #fff; }
h1 { font-size: 14pt; margin: 0 0 4px; } p { margin: 0 0 6px; } code { font-size: 9pt; }
table { border-collapse: collapse; width: 100%; margin-top: 8px; }
th, td { border: 1px solid #000; padding: 5px 6px; vertical-align: top; text-align: left; }
th { font-weight: bold; } tr { page-break-inside: avoid; }
table.what-we-show td:nth-child(1) { width: 7%; }
table.what-we-show td:nth-child(2) { width: 14%; white-space: nowrap; }
table.what-we-show td:nth-child(3) { width: 32%; }
"""


def shots(md):
    """[(shot, start, end)] from the shot table's Time column."""
    out = []
    for l in md.splitlines():
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if l.lstrip().startswith("|") and len(c) > 1 and (m := TIME.match(c[1])):
            out.append((c[0], float(m[1]), float(m[2])))
    return out


def summary(md, video):
    """Rewrite the line under the title and print what to check in the shot timings."""
    rows = shots(md)
    if not rows:
        return md
    end = rows[-1][2]
    longest = max(rows, key=lambda r: r[2] - r[1])
    audio = real_voiceover(video) or next((p for p in [video / "voiceover" / "scratch.wav"] if p.is_file()), None)
    timed = f"timed to `voiceover/{audio.name}`" if audio else "not timed to a voiceover yet"
    line = (f"{len(rows)} shots, {end:.1f} s, {timed}. New shot every {end / len(rows):.1f} s on average; "
            f"longest {longest[2] - longest[1]:.1f} s (shot {longest[0]}).")
    for (a, _, e), (b, s, _) in zip(rows, rows[1:]):
        if abs(s - e) > 0.05:
            print(f"  check: shot {a} ends at {e:.1f} s but shot {b} starts at {s:.1f} s")
    for n, s, e in rows:
        if e - s > 10:
            print(f"  check shot {n}: {e - s:.1f} s is longer than a 10 s clip; split it")
        elif e - s < 1.2:
            print(f"  check shot {n}: {e - s:.1f} s")
    if audio and end + 0.05 < ffprobe_duration(audio):
        print(f"  check: the shots end at {end:.1f} s, before the voiceover ({ffprobe_duration(audio):.1f} s)")
    m = re.search(r"^# .*\n\n", md, re.M)
    if not m:
        return md
    rest = md[m.end():]
    if not rest.startswith(("**", "|")):  # replace the old summary line, else insert one
        rest = rest.split("\n", 1)[1].lstrip("\n") if "\n" in rest else ""
    return md[:m.end()] + line + "\n\n" + rest


def cmd_pdf(args):
    video = Path(args.video).expanduser().resolve()
    plan = video / "PLAN.md"
    if not plan.is_file():
        die(f"no {plan}")
    browser = next((b for b in BROWSERS if shutil.which(b)), None)
    if not browser:
        die("needs Chromium or Chrome to print the PDF")
    md = plan.read_text()
    new = summary(md, video)
    if new != md:
        plan.write_text(md := new)
    doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{md_to_html(md, video)}</body></html>"
    dest = video / "PLAN.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "plan.html"
        page.write_text(doc)
        r = subprocess.run([browser, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                            f"--user-data-dir={tmp}/profile", f"--print-to-pdf={dest}", page.as_uri()],
                           capture_output=True, text=True, timeout=120)
    if not dest.is_file() or dest.stat().st_mtime < plan.stat().st_mtime:
        die(f"PDF not written: {r.stderr.strip()[-400:]}")
    print(dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("client")
    p.add_argument("video", nargs="?", default="video-1")
    p = sub.add_parser("voiceover")
    p.add_argument("video")
    p.add_argument("--on-camera", action="store_true", help="lines spoken inside the clips: time them from word count, no Cartesia")
    p.add_argument("--voices", nargs="?", const="", metavar="WORD", help="list Cartesia English voices, optionally matching WORD")
    p = sub.add_parser("pdf")
    p.add_argument("video")
    args = ap.parse_args()
    {"init": cmd_init, "voiceover": cmd_voiceover, "pdf": cmd_pdf}[args.cmd](args)


if __name__ == "__main__":
    main()
