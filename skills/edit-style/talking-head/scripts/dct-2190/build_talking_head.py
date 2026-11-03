#!/usr/bin/env python3
"""DCT-2190: builds edit/talking-head.fcproj (user 2026-11-02: "replace the clips audio with these [ElevenLabs mp3s],
increase the speed of her talking by 12%, set it up in FilmCraft, name it talking head, remove gaps, have all the
audio including hook-1, 2, 3").

1. New copies, originals untouched: each 1080p talking final's picture + its ElevenLabs voice (audio/elevenlabs/clip-N.mp3)
   -> edit/talking-media/clip-N-voice-1.12x.mp4, sped up 1.12x (setpts/atempo, pitch kept), h264_vaapi.
2. Gaps: the silence before and after each line is cut to LEAD/TAIL, and every pause inside a line of MIN_PAUSE or more
   is cut down to KEEP_AFTER + KEEP_BEFORE (found from the waveform). Each kept stretch is its own V1/A1 clip.
3. One sequence, back to back: hook 1, hook 2, hook 3, then body 4-19 (each hook gets HOOK_TAIL after it).
Usage: build_talking_head.py [--replace]"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
TM = EDIT / "talking-media"
VOICE = ROOT / "audio" / "elevenlabs"
PROJ = EDIT / "talking-head.fcproj"
TPS, FPS = 254016000000, 24
SPEED = 1.12
SHOTS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16a", "16b", "17", "18", "19"]
HOOKS = {"1", "2", "3"}
LEAD, TAIL, HOOK_TAIL = 0.06, 0.19, 0.37      # silence kept before/after each line (user 2026-11-02: at least 0.25 s voice to voice between clips); after each hook
MIN_PAUSE, KEEP_AFTER, KEEP_BEFORE = 0.35, 0.16, 0.04   # pauses >= MIN_PAUSE inside a line shrink to 0.2 s
TARGET_LUFS = -16.0   # user 2026-11-03: every clip the same loudness (voices ranged -21.6 to -30.9 LUFS)


def loudness(f):
    """Integrated loudness (LUFS, EBU R128) of a file's audio."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(err.split("Summary:")[1].split("I:")[1].split()[0])


def final(shot):
    d = ROOT / "clips" / (f"clip-{shot[:-1]}/clip-{shot}" if shot[-1].isalpha() else f"clip-{shot}") / "final"
    return max(d.glob(f"clip-{shot}-v*-1080p.mp4"), key=lambda p: int(p.name.split("-v")[1].split("-")[0]))


def make(shot):
    """New copy: the final's picture + the ElevenLabs voice, 1.12x, voice at TARGET_LUFS (second pass corrects what the
    peak limiter took off)."""
    out = TM / f"clip-{shot}-voice-{SPEED}x.mp4"
    if out.exists():
        return out
    TM.mkdir(parents=True, exist_ok=True)
    gain = TARGET_LUFS - loudness(VOICE / f"clip-{shot}.mp3")
    for _ in range(3):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-vaapi_device", "/dev/dri/renderD128",
                        "-i", str(final(shot)), "-i", str(VOICE / f"clip-{shot}.mp3"), "-filter_complex",
                        f"[0:v]setpts=PTS/{SPEED},fps={FPS},format=nv12,hwupload[v];[1:a]atempo={SPEED},volume={gain:.2f}dB,alimiter=limit=0.84:level=disabled[a]",
                        "-map", "[v]", "-map", "[a]", "-shortest", "-c:v", "h264_vaapi", "-qp", "18", "-profile:v", "high",
                        "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(out)], check=True)
        off = TARGET_LUFS - loudness(out)
        if abs(off) <= 0.2:
            break
        gain += off
    return out


def words(p):
    out = EDIT / "words" / f"{p.stem}.words.json"
    if not out.exists():
        subprocess.run([sys.executable, str(Path.home() / ".claude/skills/transcribe/scripts/transcribe.py"), "--engine",
                        "parakeet", "--out-dir", str(out.parent), str(p)], check=True, capture_output=True)
    return out


def segments(p, tail, short=0.0):
    """Kept stretches (start, end) in seconds: speech with head/tail and inner pauses trimmed. short: silence the clip
    before ran out of (its voice ran to its file end), taken from this clip's own lead-in instead. Also returns the
    silence actually kept after the voice."""
    a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                     capture_output=True, check=True).stdout, np.int16) / 32768
    db = np.array([20 * np.log10(np.sqrt((a[i:i + 160] ** 2).mean()) + 1e-9) for i in range(0, len(a) - 160, 160)])
    lo, hi = np.percentile(db, 8), np.percentile(db, 90)
    on = db > lo + 0.4 * (hi - lo)
    dur = len(a) / 16000
    # only between the first and last spoken word (Parakeet times), so breaths and clicks outside the line are dropped
    ws = json.load(open(words(p)))
    w0, w1 = int(max(0, ws[0]["start"] - 0.15) * 100), int((ws[-1]["end"] + 0.25) * 100)
    on[:w0] = False; on[w1:] = False
    idx = np.where(on)[0]
    s0, s1 = idx[0] / 100, (idx[-1] + 1) / 100
    # runs of silence inside the speech
    segs, start, i = [], max(0.0, s0 - LEAD - short), idx[0]
    while i <= idx[-1]:
        if not on[i]:
            j = i
            while j <= idx[-1] and not on[j]:
                j += 1
            if (j - i) / 100 >= MIN_PAUSE:
                segs.append((start, i / 100 + KEEP_AFTER))
                start = j / 100 - KEEP_BEFORE
            i = j
        else:
            i += 1
    segs.append((start, min(dur, s1 + tail)))
    return segs, segs[-1][1] - s1


def cli(cmds, save_as=None):
    script = EDIT / ".fc-run.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    args = ["filmcraft-cli", "--compact"] + (["--project", str(PROJ)] if not save_as else []) + ["run", str(script)]
    if save_as:
        args += ["--save-as", str(save_as)]
    out = subprocess.run(args, capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    script.unlink()
    return [r.get("result") for r in res]


def main():
    if PROJ.exists():
        if "--replace" not in sys.argv:
            sys.exit(f"{PROJ.name} exists: pass --replace")
        PROJ.unlink()
    media = {s: make(s) for s in SHOTS}
    pieces, t, report, short = [], 0, [], 0.0
    for s in SHOTS:
        want = HOOK_TAIL if s in HOOKS else TAIL
        segs, kept = segments(media[s], want, short)
        short = max(0.0, TAIL - kept)   # at least TAIL + LEAD voice to voice at every join
        start = t
        for a, b in segs:
            fa, fb = round(a * FPS), round(b * FPS)
            pieces.append((s, fa, fb - fa, t))
            t += fb - fa
        report.append(f"clip {s:>3}: {start / FPS:6.2f}s  {len(segs)} piece(s), {(t - start) / FPS:.2f}s")
    paths = [str(media[s]) for s in SHOTS]
    r = cli([{"id": "file.newProject", "params": {"name": "talking-head"}},
             {"id": "file.import", "params": {"paths": paths}},
             {"id": "file.newSequence", "params": {"name": "talking-head", "width": 1080, "height": 1920, "fps": FPS,
                                                   "video": 1, "audio": 1}}], save_as=PROJ)
    items = dict(zip(SHOTS, r[1]["items"]))
    cli([{"id": "timeline.place", "params": {"item": items[s], "track": "V1", "audioTrack": "A1", "frame": at,
                                             "sourceIn": sin * TPS // FPS, "duration": d * TPS // FPS, "insert": False}}
         for s, sin, d, at in pieces] + [{"id": "file.save", "params": {}}])
    print("\n".join(report))
    print(f"{PROJ.name}: {len(pieces)} clips on V1/A1, {t / FPS:.1f} s")


main()
