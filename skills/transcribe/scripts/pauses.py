#!/usr/bin/env python3
"""Where a voice actually pauses, from the waveform: exact speech ends and onsets for cuts and captions.

ASR word times can't do this: Parakeet gives word starts only (each word "ends" where the next starts), and
Whisper's ends drift. A fixed threshold like ffmpeg's silencedetect -40 dB can't either: AI video clips carry room
tone that sits above it, so it found none of the 0.3-0.6 s pauses in Max video-2. The threshold here is set from
the recording itself, between its noise floor and its speech level.

  pauses.py AUDIO [--least 0.15]      prints each pause: start, end, length (seconds)

From other scripts:
  from pauses import load, find_pauses
  x = load("vo.wav")                  # mono float32 at 16 kHz
  find_pauses(x)                      # [(speech_end, onset), ...]
"""
import argparse, subprocess, sys
import numpy as np

SR = 16000
HOP = 0.01  # s per loudness step


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def loudness(x):
    """dB per 10 ms step (20 ms windows), lightly smoothed so a single loud click doesn't break a pause."""
    w, h = int(0.02 * SR), int(HOP * SR)
    n = max(1, (len(x) - w) // h + 1)
    idx = np.arange(w)[None, :] + h * np.arange(n)[:, None]
    db = 10 * np.log10(np.mean(x[np.minimum(idx, len(x) - 1)] ** 2, axis=1) + 1e-10)
    k = 3  # 70 ms running median
    pad = np.pad(db, k, mode="edge")
    return np.median(np.lib.stride_tricks.sliding_window_view(pad, 2 * k + 1), axis=1)


def threshold(db):
    floor, speech = np.percentile(db, 8), np.percentile(db, 90)
    return floor + 0.4 * (speech - floor), floor, speech


def find_pauses(x, least=0.15):
    """(speech_end, onset) in seconds for every quiet stretch of at least `least` s between speech.
    Stop consonants (the closure in "it can") last under about 0.12 s, so the default skips them."""
    db = loudness(x)
    thr, _, _ = threshold(db)
    q = db < thr
    out, i, n = [], 0, len(q)
    while i < n:
        if q[i]:
            j = i
            while j < n and q[j]:
                j += 1
            if i > 0 and j < n and (j - i) * HOP >= least:
                out.append((round(i * HOP, 3), round(j * HOP, 3)))
            i = j
        else:
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--least", type=float, default=0.15)
    a = ap.parse_args()
    x = load(a.audio)
    thr, floor, speech = threshold(loudness(x))
    ps = find_pauses(x, a.least)
    print(f"noise floor {floor:.1f} dB, speech {speech:.1f} dB, quiet below {thr:.1f} dB")
    for s, e in ps:
        print(f"{s:8.2f} {e:8.2f}  {e - s:.2f}")
    print(f"{len(ps)} pauses >= {a.least} s, {sum(e - s for s, e in ps):.1f} s of {len(x) / SR:.1f} s")


if __name__ == "__main__":
    sys.exit(main())
