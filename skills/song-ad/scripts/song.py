#!/usr/bin/env python3
"""Helpers for a sung ad: check the lyric sheet, and cut gapless song slices for the lip-sync shots.

  song.py lyrics LYRICS.md [--video VIDEO_DIR]   count sung words, estimate the song length, flag lines
                                                 too long or too short for one shot; with --video, write the
                                                 sung lines to VIDEO_DIR/voiceover/script.md for plan.py
  song.py slice VIDEO_DIR 1-2 7 15-16 [--all]    cut the song (voiceover/recording.*) into slices for those
                                                 lyric lines, from voiceover/timing.md; --all slices the
                                                 whole song into consecutive batches of up to 10 s

Lyric sheet format: [Section] tags, {music cues} and (backing answers) are not lead lines; [Spoken] and
other tags on their own line are skipped. Every other non-empty line is one sung (or spoken) lead line.
Slices share their boundaries (the midpoint of the silence between lines), so consecutive slices play
back to back with no gap and no overlap; the first slice starts at 0 s and the last runs to the end.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

WORDS_PER_SECOND = 2.5  # sung delivery (Starpop's measure); spoken VO runs about 2.8-3.2
LINE_MIN, LINE_MAX = 4, 10  # words per lead line: one line is one shot of about 2-4 s
MAX_SLICE = 10.0  # longest clip the lip-sync models take in one generation (MiniMax H3 Max, Seedance 2.0)


def die(msg):
    sys.exit(f"error: {msg}")


def lead_lines(text):
    lines = []
    in_fence = False
    for raw in text.splitlines():
        s = raw.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if not s or s.startswith("#") or s.startswith("|") or s.startswith("**"):
            continue
        s = re.sub(r"\[[^\]]*\]", "", s)  # [Section] / [Spoken] tags
        s = re.sub(r"\{[^}]*\}", "", s)   # {music cues}
        s = re.sub(r"\([^)]*\)", "", s)   # (backing answers)
        s = re.sub(r"\s+", " ", s).strip(" -—")
        if re.search(r"[A-Za-z]", s):
            lines.append(s)
    return lines


def cmd_lyrics(args):
    p = Path(args.lyrics)
    text = p.read_text()
    if "```" in text:  # a script file: the lyrics live in the first fenced block
        m = re.search(r"```[^\n]*\n(.*?)```", text, re.S)
        text = m.group(1) if m else text
    lines = lead_lines(text)
    if not lines:
        die(f"no lyric lines found in {p}")
    words = sum(len(l.split()) for l in lines)
    secs = words / WORDS_PER_SECOND
    print(f"{len(lines)} lead lines · {words} words · about {int(secs // 60)}:{int(secs % 60):02d} of vocals "
          f"at {WORDS_PER_SECOND} words/s (instrumental breaks and held notes add more)")
    flagged = [(i, l) for i, l in enumerate(lines, 1) if not LINE_MIN <= len(l.split()) <= LINE_MAX]
    for i, l in flagged:
        n = len(l.split())
        print(f"  line {i}: {n} words ({'pair it with the next line' if n < LINE_MIN else 'split it'}): {l}")
    if not flagged:
        print(f"  every line is {LINE_MIN}-{LINE_MAX} words")
    if args.video:
        out = Path(args.video) / "voiceover" / "script.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("# Sung lead lines, in song order (written by song.py lyrics; edit the lyric sheet, not this)\n\n"
                       + "\n".join(lines) + "\n")
        print(f"wrote {out}")


def recording(video):
    for ext in ("wav", "mp3", "m4a", "aac"):  # the same takes plan.py voiceover times
        f = video / "voiceover" / f"recording.{ext}"
        if f.is_file():
            return f
    die(f"put the chosen song take at {video}/voiceover/recording.wav first")


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def timing(video):
    p = video / "voiceover" / "timing.md"
    if not p.is_file():
        die(f"run video-plan's plan.py voiceover {video} first (it writes {p})")
    rows = {}
    for line in p.read_text().splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|", line)
        if m:
            rows[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    if not rows:
        die(f"no timed lines in {p}")
    return rows


def boundaries(rows, total):
    """Cut point before each line: the middle of the silence after the previous line. Line 1 starts at 0."""
    n = max(rows)
    b = {1: 0.0}
    for i in range(2, n + 1):
        prev = next((rows[k] for k in range(i - 1, 0, -1) if k in rows), None)
        if i in rows and prev:
            b[i] = (prev[1] + rows[i][0]) / 2
        elif i in rows:
            b[i] = rows[i][0]
    b[n + 1] = total
    return b, n


def cut(src, start, end, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
                    "-ac", "2", "-ar", "44100", str(out)], check=True)


def cmd_slice(args):
    video = Path(args.video).expanduser().resolve()
    src = recording(video)
    rows = timing(video)
    total = duration(src)
    b, n = boundaries(rows, total)
    out_dir = video / "voiceover" / "slices"
    out_dir.mkdir(exist_ok=True)
    groups = []
    if args.all:  # consecutive batches of whole lines, each as long as fits in MAX_SLICE
        cuts = sorted(b)  # a line whisper didn't find has no cut point: it rides inside its neighbour's slice
        k = 0
        while k < len(cuts) - 1:
            m = k + 1
            while m + 1 < len(cuts) and b[cuts[m + 1]] - b[cuts[k]] <= MAX_SLICE:
                m += 1
            groups.append((cuts[k], cuts[m] - 1))
            k = m
    else:
        for spec in args.lines:
            a, _, z = spec.partition("-")
            groups.append((int(a), int(z or a)))
    report = ["| Slice | Lines | In | Out | Length |", "|---|---|---|---|---|"]
    for a, z in groups:
        if a not in b or (z + 1) not in b:
            print(f"lines {a}-{z}: a line next to this range wasn't found in the audio (see timing.md); fix the script or cut by hand")
            continue
        start, end = b[a], b[z + 1]
        name = f"lines-{a}" + (f"-{z}" if z != a else "") + ".wav"
        cut(src, start, end, out_dir / name)
        flag = "  over 10 s: split the shot" if end - start > MAX_SLICE else ""
        report.append(f"| {name} | {a}-{z} | {start:.2f} | {end:.2f} | {end - start:.2f} s{flag} |")
    body = f"# Song slices\n\nFrom `{src.name}` ({total:.1f} s). Consecutive slices share their cut points: no gaps.\n\n" + "\n".join(report) + "\n"
    (out_dir / "slices.md").write_text(body)
    print(body)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lyrics")
    p.add_argument("lyrics")
    p.add_argument("--video")
    p.set_defaults(fn=cmd_lyrics)
    p = sub.add_parser("slice")
    p.add_argument("video")
    p.add_argument("lines", nargs="*", help="lyric line numbers or ranges, e.g. 1-2 7 15-16")
    p.add_argument("--all", action="store_true", help="slice the whole song into gapless batches of up to 10 s")
    p.set_defaults(fn=cmd_slice)
    args = ap.parse_args()
    if args.cmd == "slice" and not args.all and not args.lines:
        ap.error("name the lines to slice, or pass --all")
    args.fn(args)


if __name__ == "__main__":
    main()
