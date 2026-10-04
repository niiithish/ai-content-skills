#!/usr/bin/env python3
"""Speech to text with word timestamps: NVIDIA Parakeet (onnx-asr) by default, faster-whisper as fallback.

  transcribe.py MEDIA [MEDIA ...] [--srt] [--out-dir DIR] [--engine parakeet|whisper]

Takes any audio or video file and writes next to it (or in --out-dir):
  <stem>.txt         the transcript
  <stem>.words.json  [{"word", "start", "end"}] in seconds
  <stem>.srt         with --srt: subtitles split at sentence punctuation

Other skills import it: `from transcribe import words` -> [(word, start, end), ...].

Parakeet (parakeet-tdt-0.6b-v3) is fast on a CPU and writes muted words as they sound
("f"), where whisper makes words up or drops them. Install: pip install "onnx-asr[cpu,hub]".
The model is read from ~/.local/share/voxtype/models/ when present, otherwise downloaded once.
faster-whisper (small.en) is used only when onnx-asr can't be imported or the model can't load.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

PARAKEET = "nemo-parakeet-tdt-0.6b-v3"
LOCAL_MODELS = Path.home() / ".local/share/voxtype/models"
WHISPER_MODEL = "small.en"
RATE = 16000
CHUNK = 300        # seconds per Parakeet pass; longer files are cut at the quietest moment near each boundary
SEARCH = 20        # seconds before each boundary searched for that quiet moment
LAST_WORD = 0.08   # length given to the final word, which has no next word to end it


def load_audio(path):
    """Any media file -> float32 mono 16 kHz samples."""
    import numpy as np
    with tempfile.TemporaryDirectory() as d:
        wav = Path(d) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vn", "-ar", str(RATE), "-ac", "1",
                        "-c:a", "pcm_s16le", str(wav)], check=True)
        with wave.open(str(wav)) as w:
            pcm = w.readframes(w.getnframes())
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768


def chunks(audio):
    """(offset_seconds, samples) pieces of at most CHUNK seconds, cut where it's quietest."""
    import numpy as np
    out, start, n = [], 0, len(audio)
    while n - start > CHUNK * RATE:
        lo, hi = start + (CHUNK - SEARCH) * RATE, start + CHUNK * RATE
        frame = RATE // 10
        energy = [np.abs(audio[i:i + frame]).mean() for i in range(lo, hi, frame)]
        cut = lo + int(np.argmin(energy)) * frame + frame // 2
        out.append((start / RATE, audio[start:cut]))
        start = cut
    out.append((start / RATE, audio[start:]))
    return out


def parakeet_model():
    # full precision: int8 was no faster on a CPU and misheard swears (muted and not) on the test voiceover
    import onnx_asr
    d = LOCAL_MODELS / "parakeet-tdt-0.6b-v3"
    return onnx_asr.load_model(PARAKEET, str(d) if (d / "vocab.txt").exists() else None).with_timestamps()


def parakeet_words(audio):
    model = parakeet_model()
    out = []
    for offset, piece in chunks(audio):
        r = model.recognize(piece, sample_rate=RATE)
        for tok, ts in zip(r.tokens, r.timestamps):
            if tok.startswith(" ") or not out:
                out.append([tok.strip(), offset + ts])
            else:
                out[-1][0] += tok
    return [(w, round(s, 3), round(out[i + 1][1] if i + 1 < len(out) else s + LAST_WORD, 3))
            for i, (w, s) in enumerate(out) if w]


def whisper_words(audio):
    from faster_whisper import WhisperModel
    try:    # the cached model first: the hub check can hang for minutes on a bad network
        model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8", local_files_only=True)
    except Exception:
        model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(audio, language="en", word_timestamps=True)
    return [(w.word.strip(), round(w.start, 3), round(w.end, 3)) for s in segs for w in s.words if w.word.strip()]


def words(path, engine="parakeet"):
    """[(word, start, end), ...] for any audio or video file. Word text keeps its punctuation."""
    audio = load_audio(path)
    if engine == "parakeet":
        try:
            return parakeet_words(audio)
        except Exception as e:  # ImportError, or a model that won't load
            print(f"Parakeet unavailable ({e.__class__.__name__}: {e}); falling back to faster-whisper {WHISPER_MODEL}",
                  file=sys.stderr)
    try:
        return whisper_words(audio)
    except ImportError:
        sys.exit('pip install "onnx-asr[cpu,hub]" (Parakeet speech-to-text), or faster-whisper as a fallback')


def stamp(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def srt(ws):
    cues, cur = [], []
    for w in ws:
        cur.append(w)
        if re.search(r"[.!?]$", w[0]):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return "\n".join(f"{i}\n{stamp(c[0][1])} --> {stamp(c[-1][2])}\n{' '.join(w[0] for w in c)}\n"
                     for i, c in enumerate(cues, 1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media", type=Path, nargs="+")
    ap.add_argument("--srt", action="store_true", help="also write <stem>.srt")
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--engine", choices=["parakeet", "whisper"], default="parakeet")
    a = ap.parse_args()
    for m in a.media:
        t = time.time()
        ws = words(m, a.engine)
        d = a.out_dir or m.parent
        d.mkdir(parents=True, exist_ok=True)
        base = d / m.stem
        Path(f"{base}.txt").write_text(" ".join(w for w, _, _ in ws) + "\n")
        Path(f"{base}.words.json").write_text(
            json.dumps([{"word": w, "start": s, "end": e} for w, s, e in ws], indent=0))
        if a.srt:
            Path(f"{base}.srt").write_text(srt(ws))
        print(f"{m.name}: {len(ws)} words in {time.time() - t:.1f}s -> {base}.txt, .words.json{', .srt' if a.srt else ''}")


if __name__ == "__main__":
    main()
