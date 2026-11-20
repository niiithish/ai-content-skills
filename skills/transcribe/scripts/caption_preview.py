#!/usr/bin/env python3
"""A quick check video for word timing: black 1080x1920, white captions, the given audio, a timecode in the corner.

  caption_preview.py WORDS.json AUDIO -o OUT.mp4 [--words 3] [--gap 0.4] [--voice VOCALS.wav]

WORDS.json is transcribe's <stem>.words.json. AUDIO is what you hear: for a song, the original mix (not the vocal
stem), so you judge the captions against the real track. Captions are up to --words words, a new one after a pause
of --gap s or a sentence end; each stays up until the next starts, or 0.3 s past its last word before a pause.
--voice (a song's vocal stem, from vocals.py) snaps to the waveform: a caption after a gap starts where the voice
comes back, and one before a gap ends 2 frames after the voice stops (held notes included). Without it the times
are Parakeet's alone, which on a song were 3+ frames off on 25 of 37 line starts.
Not a deliverable: real captions go into FilmCraft with captions-filmcraft.
"""
import argparse, json, re, subprocess, tempfile
from pathlib import Path


def ass_time(t):
    cs = int(round(max(t, 0) * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def groups(ws, n, gap):
    out, cur = [], []
    for i, w in enumerate(ws):
        if cur and (len(cur) >= n or w["start"] - cur[-1]["end"] >= gap):
            out.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.!?,]$", w["word"]):
            out.append(cur); cur = []
    return out + ([cur] if cur else [])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words", type=Path); ap.add_argument("audio", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--words", type=int, default=3, dest="n"); ap.add_argument("--gap", type=float, default=0.4)
    ap.add_argument("--voice", type=Path, help="vocal stem: snap starts and ends to where the voice really starts and stops")
    a = ap.parse_args()
    ap_voice = a.voice
    ws = json.loads(a.words.read_text())
    gaps = []
    if ap_voice:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from pauses import load, find_pauses
        gaps = [(e, o) for e, o in find_pauses(load(str(ap_voice))) if o - e >= 0.15]
    gs = groups(ws, a.n, a.gap)
    starts = [g[0]["start"] for g in gs]
    if gaps:   # the first word after a gap starts where the voice comes back (Parakeet runs early there)
        for k, t in enumerate(starts):
            near = [o for e, o in gaps if e - 0.1 <= t <= o + 0.25 and (k == 0 or o > starts[k - 1] + 0.1)]
            if near:
                starts[k] = near[0]
    lines = []
    for k, g in enumerate(gs):
        start = starts[k]
        nxt = starts[k + 1] if k + 1 < len(gs) else None
        end = g[-1]["end"] + 0.3
        if gaps:   # end 2 frames after the voice stops before the next gap, however long the note is held
            stop = next((e for e, o in gaps if e >= g[-1]["start"] and (nxt is None or o <= nxt + 0.25)), None)
            end = stop + 2 / 30 if stop is not None and (nxt is None or nxt - stop >= a.gap) else (nxt or end)
        elif nxt is not None and nxt - g[-1]["end"] < a.gap:
            end = nxt                      # back to back while the voice runs
        end = min(end, nxt) if nxt is not None else end
        text = " ".join(w["word"] for w in g).replace("{", "(").replace("}", ")")
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,{text}")
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat ExtraBold,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n"
    with tempfile.TemporaryDirectory() as d:
        sub = Path(d) / "c.ass"   # the ass filter: ffmpeg 9's subtitles filter dropped the first caption
        sub.write_text(ass)
        vf = (f"ass={sub}:fontsdir={Path.home() / '.local/share/fonts'},"
              "drawtext=text='%{pts\\:hms}':x=40:y=60:fontsize=40:fontcolor=gray")
        a.out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=1080x1920:r=30",
                        "-i", str(a.audio), "-vf", vf, "-map", "0:v", "-map", "1:a", "-shortest",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", str(a.out)], check=True)
    print(f"{len(gs)} captions -> {a.out}")


if __name__ == "__main__":
    main()
