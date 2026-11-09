#!/usr/bin/env python3
"""Speech to text with word timestamps, fully local. Parakeet TDT 0.6B v3 on the Intel GPU, CPU fallbacks.

  transcribe.py MEDIA [MEDIA ...] [--srt] [--out-dir DIR] [--verify] [--engine NAME]

Takes any audio or video file and writes next to it (or in --out-dir):
  <stem>.txt         the transcript
  <stem>.words.json  [{"word", "start", "end"}] in seconds
  <stem>.srt         with --srt: subtitles split at sentence punctuation

Other skills import it: `from transcribe import words` -> [(word, start, end), ...].
It runs under any python3: every engine is its own process (parakeet.cpp binary, or the venv for ONNX/whisper).

Engines, tried in order until one gives a sane result:
  parakeet-gpu   parakeet.cpp + Vulkan on the Arc GPU        (~70x real time)
  parakeet-cpu   the same binary and model on the CPU         (~10x real time, same output format)
  parakeet-onnx  onnx-asr, an independent Parakeet runtime    (venv, CPU)
  whisper        faster-whisper small.en, a different model   (venv, CPU, last resort)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

RATE = 16000
PCPP = Path.home() / ".local/share/parakeet-cpp"            # parakeet.cpp Vulkan build, see SKILL.md
PCPP_MODEL = PCPP / "model/tdt-0.6b-v3-f16.gguf"
VK_DEVICE = os.environ.get("TRANSCRIBE_VK_DEVICE", "Vulkan0")
VENV_PY = Path.home() / ".local/share/transcribe-venv/bin/python"   # has onnx-asr and faster-whisper
PARAKEET_ONNX = "nemo-parakeet-tdt-0.6b-v3"
LOCAL_MODELS = Path.home() / ".local/share/voxtype/models"
WHISPER_MODELS = ("medium.en", "small.en")   # the first one already downloaded is used; small.en is fetched if none is
CHUNK = 30         # seconds per ONNX pass, cut at the quietest moment in the last SEARCH seconds
SEARCH = 5
LAST_WORD = 0.08   # ONNX: length given to the final word, which has no next word to end it
VERIFY_TOL = 0.15  # --verify: a word start may differ by one 80 ms Parakeet step between GPU and CPU, not two


def to_wav(path, d):
    """Any media file -> 16 kHz mono WAV in directory d; returns (wav, seconds)."""
    wav = Path(d) / "a.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vn", "-ar", str(RATE), "-ac", "1",
                    "-c:a", "pcm_s16le", str(wav)], check=True)
    with wave.open(str(wav)) as w:
        return wav, w.getnframes() / RATE


def duration(path):
    with tempfile.TemporaryDirectory() as d:
        return to_wav(path, d)[1]


def sane(ws, seconds):
    """Cheap check on any engine's result: ordered, inside the file, not an absurd word rate."""
    if not ws:
        return True    # silence is a valid answer (but see words(): only trusted on short files)
    starts = [w[1] for w in ws]
    return (all(a <= b for a, b in zip(starts, starts[1:])) and starts[0] >= 0 and ws[-1][1] <= seconds + 0.5
            and len(ws) / max(seconds, 1) <= 8)


# ---------- parakeet.cpp (GPU and CPU) ----------

def parakeet_cpp(path, device):
    """(words, device_that_ran) from parakeet-cli. One short-lived process: the model loads (~1 s), runs, and the
    GPU is released when it exits. A crash ends only that process; a hang is killed by the timeout.
    parakeet.cpp silently uses the CPU when the named GPU is missing, so the device is read back from its log."""
    cli = PCPP / "bin/parakeet-cli"
    if not (cli.exists() and PCPP_MODEL.exists()):
        raise RuntimeError(f"parakeet.cpp not installed in {PCPP}")
    with tempfile.TemporaryDirectory() as d:
        wav, seconds = to_wav(path, d)
        env = {**os.environ, "LD_LIBRARY_PATH": f"{PCPP / 'lib'}:" + os.environ.get("LD_LIBRARY_PATH", ""),
               "PARAKEET_DEVICE": device}
        # GPU measured ~70x real time and CPU ~10x; the timeouts leave 10-30x headroom, so only a real hang hits them
        limit = 60 + (seconds / 2 if device != "cpu" else seconds)
        r = subprocess.run([str(cli), "transcribe", "--model", str(PCPP_MODEL), "--input", str(wav), "--timestamps"],
                           capture_output=True, text=True, env=env, timeout=limit)
    if r.returncode:
        raise RuntimeError(f"parakeet-cli exit {r.returncode}: {r.stderr.strip()[-200:]}")
    m = re.search(r"using device: (\S+)", r.stderr)
    ran = m.group(1) if m else "cpu"
    ws = [(m.group(3), float(m.group(1)), float(m.group(2)))
          for m in (re.match(r"([\d.]+)-([\d.]+)\s+(.+?)\s+\([\d.]+\)\s*$", l) for l in r.stdout.splitlines()) if m]
    return ws, ran


# ---------- engines that need the venv (run as a subprocess, so any caller's python works) ----------

def _venv(flag, path, seconds):
    py = str(VENV_PY if VENV_PY.exists() else sys.executable)
    r = subprocess.run([py, __file__, flag, str(path)], capture_output=True, text=True, timeout=300 + 3 * seconds)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[-300:] or f"exit {r.returncode}")
    return [tuple(w) for w in json.loads(r.stdout)]


def whisper_file(path):
    """faster-whisper words for a file, in the venv. fc_captions.py uses it as the second opinion on timing."""
    return _venv("--whisper-words", path, duration(path))


def _load_audio(path):
    import numpy as np
    with tempfile.TemporaryDirectory() as d:
        wav, _ = to_wav(path, d)
        with wave.open(str(wav)) as w:
            pcm = w.readframes(w.getnframes())
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768


def _chunks(audio):
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


def _onnx_words(path):
    # full precision on purpose: int8 was no faster on the CPU and misheard swears on the test voiceover
    import onnx_asr
    d = LOCAL_MODELS / "parakeet-tdt-0.6b-v3"
    model = onnx_asr.load_model(PARAKEET_ONNX, str(d) if (d / "vocab.txt").exists() else None).with_timestamps()
    out = []
    for offset, piece in _chunks(_load_audio(path)):
        r = model.recognize(piece, sample_rate=RATE)
        for tok, ts in zip(r.tokens, r.timestamps):
            if tok.startswith(" ") or not out:
                out.append([tok.strip(), offset + ts])
            else:
                out[-1][0] += tok
    return [(w, round(s, 3), round(out[i + 1][1] if i + 1 < len(out) else s + LAST_WORD, 3))
            for i, (w, s) in enumerate(out) if w]


def _whisper_words(path):
    from faster_whisper import WhisperModel
    model = None
    for name in WHISPER_MODELS:   # cached models first: the hub check can hang for minutes on a bad network
        try:
            model = WhisperModel(name, device="cpu", compute_type="int8", local_files_only=True)
            break
        except Exception:
            pass
    model = model or WhisperModel(WHISPER_MODELS[-1], device="cpu", compute_type="int8")
    # decoded samples, not the path: faster-whisper 1.2.1's own decoder breaks on newer PyAV (metadata_errors)
    segs, _ = model.transcribe(_load_audio(path), language="en", word_timestamps=True)
    return [(w.word.strip(), round(w.start, 3), round(w.end, 3)) for s in segs for w in s.words if w.word.strip()]


# ---------- the chain ----------

def _norm(ws):
    return [re.sub(r"[^a-z0-9]", "", w.lower()) for w, _, _ in ws]


def _agree(a, b):
    """Same words and every start within VERIFY_TOL."""
    return _norm(a) == _norm(b) and all(abs(x[1] - y[1]) <= VERIFY_TOL for x, y in zip(a, b))


ENGINES = ["parakeet-gpu", "parakeet-cpu", "parakeet-onnx", "whisper"]
LABELS = {"parakeet-gpu": "Parakeet (GPU, parakeet.cpp Vulkan)", "parakeet-cpu": "Parakeet (CPU, parakeet.cpp)",
          "parakeet-onnx": "Parakeet (CPU, ONNX)", "whisper": "faster-whisper"}


def _run(name, path, seconds):
    """(words, label) from one engine, or an exception."""
    if name in ("parakeet-gpu", "parakeet-cpu"):
        ws, ran = parakeet_cpp(path, VK_DEVICE if name == "parakeet-gpu" else "cpu")
        if name == "parakeet-gpu" and not ran.lower().startswith("vulkan"):
            raise RuntimeError(f"GPU {VK_DEVICE} not found by parakeet.cpp (it ran on {ran})")
        return ws, LABELS[name]
    return _venv("--onnx-words" if name == "parakeet-onnx" else "--whisper-words", path, seconds), LABELS[name]


def words(path, engine="auto", verify=None):
    """[(word, start, end), ...] for any audio or video file. Word text keeps its punctuation.

    Engines run in ENGINES order; a crash, hang, missing install or a result that fails sane() moves on to the
    next one. Zero words in a file over 3 s is also passed on, so silence is confirmed, never trusted.
    Naming an engine starts the chain there. verify=True (or TRANSCRIBE_VERIFY=1) re-runs a GPU result on the
    CPU and keeps the CPU words unless both agree on every word and every start (within one step)."""
    if verify is None:
        verify = os.environ.get("TRANSCRIBE_VERIFY", "0") == "1"
    seconds = duration(path)
    order = ENGINES[ENGINES.index(engine):] if engine in ENGINES else ENGINES
    for i, name in enumerate(order):
        try:
            ws, label = _run(name, path, seconds)
            if not sane(ws, seconds):
                raise RuntimeError("result failed the sanity check")
            if not ws and seconds > 3:
                raise RuntimeError("no words in a file longer than 3 s; letting the next engine confirm")
            if verify and name == "parakeet-gpu":
                try:
                    cpu, cpu_label = _run("parakeet-cpu", path, seconds)
                except Exception as e:   # no CPU check possible: the ONNX engine gives the result instead
                    raise RuntimeError(f"--verify: the CPU check failed ({e})")
                if _agree(ws, cpu):
                    label += ", verified on CPU"
                else:
                    print("--verify: GPU and CPU differ; keeping the CPU result", file=sys.stderr)
                    ws, label = cpu, cpu_label + " (GPU disagreed)"
            print(f"transcribed {Path(path).name} with {label}", file=sys.stderr)
            return ws
        except Exception as e:
            nxt = f"; trying {LABELS[order[i + 1]]}" if i + 1 < len(order) else ""
            print(f"{LABELS[name]} failed ({e.__class__.__name__}: {e}){nxt}", file=sys.stderr)
    sys.exit("no speech-to-text engine worked; see the messages above and transcribe/SKILL.md (setup)")


# ---------- output ----------

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
    ap.add_argument("media", type=Path, nargs="*")
    ap.add_argument("--onnx-words", metavar="FILE", help=argparse.SUPPRESS)
    ap.add_argument("--whisper-words", metavar="FILE", help=argparse.SUPPRESS)
    ap.add_argument("--srt", action="store_true", help="also write <stem>.srt")
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--engine", choices=["auto", *ENGINES], default="auto", help="start the chain at this engine")
    ap.add_argument("--verify", action="store_true",
                    help="re-run a GPU result on the CPU and keep the CPU words unless both agree (use for captions)")
    a = ap.parse_args()
    if a.onnx_words:
        return print(json.dumps(_onnx_words(a.onnx_words)))
    if a.whisper_words:
        return print(json.dumps(_whisper_words(a.whisper_words)))
    if not a.media:
        ap.error("give at least one media file")
    for m in a.media:
        t = time.time()
        ws = words(m, a.engine, True if a.verify else None)
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
