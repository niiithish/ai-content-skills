#!/usr/bin/env python3
"""Split a song into its sung vocals and its music, locally, so speech-to-text hears only the voice.

  vocals.py SONG [SONG ...] [--out-dir DIR] [--music] [--device auto|xpu|cpu] [--overlap N] [--model FILE] [--force]

Writes next to each file (or in --out-dir):
  <stem>.vocals.wav   the voice alone, same length and same timeline as SONG (sample-accurate), 44.1 kHz stereo
  <stem>.music.wav    with --music: everything else

Why: in a sung track the music covers the ends of held words, so Parakeet hears words late, short or not at
all, and the waveform checks (pauses.py, caption onsets) see the beat instead of the voice. On the vocal stem
both work as on a voiceover. Never put the stem in the edit: it is for timing only.

Model: MelBand RoFormer vocals by Kimberley Jensen (vocals_mel_band_roformer.ckpt, vocals SDR 12.6, the best in
audio-separator's list in 2026-11; Demucs htdemucs_ft is 10.8). Runs through python-audio-separator in the venv
~/.local/share/separate-xpu-venv on the Intel Arc GPU (PyTorch XPU), falling back to the CPU when the GPU fails.
audio-separator itself only knows CUDA/MPS/DirectML, so the device is set here after it starts.

Other scripts: `from vocals import vocals; vocals("song.wav")` -> Path of the vocal stem (cached: a stem newer
than its song is reused).
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time, wave
from pathlib import Path

VENV_PY = Path.home() / ".local/share/separate-xpu-venv/bin/python"
MODELS = Path.home() / ".local/share/separate-models"
MODEL = "vocals_mel_band_roformer.ckpt"
OVERLAP = 2   # chunks overlapping each other; the model's own 8 is 4x slower for a gain no caption can see


def _seconds(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def vocals(path, out_dir=None, music=False, device="auto", overlap=OVERLAP, model=MODEL, force=False):
    """Path of <stem>.vocals.wav for any audio or video file. Runs the separation in the venv as its own process."""
    path = Path(path).resolve()
    d = Path(out_dir) if out_dir else path.parent
    d.mkdir(parents=True, exist_ok=True)
    voc, mus = d / f"{path.stem}.vocals.wav", d / f"{path.stem}.music.wav"
    fresh = lambda p: p.exists() and p.stat().st_mtime >= path.stat().st_mtime
    if not force and fresh(voc) and (fresh(mus) or not music):
        print(f"vocals: reusing {voc.name}", file=sys.stderr)
        return voc
    if not VENV_PY.exists():
        sys.exit(f"vocals: no separation venv at {VENV_PY}; see transcribe/SKILL.md (Songs)")
    order = ["xpu", "cpu"] if device == "auto" else [device]
    seconds = _seconds(path)
    for dev in order:
        t = time.time()
        # GPU ~? the timeout only catches a hang: the CPU took over 10 min for 4 min of song at overlap 8
        limit = 300 + seconds * (3 if dev == "xpu" else 12)
        r = subprocess.run([str(VENV_PY), "-I", __file__, "--_inner", str(path), str(voc), str(mus) if music else "",
                            dev, str(overlap), model], capture_output=True, text=True, timeout=limit)
        if r.returncode == 0 and voc.exists():
            print(f"vocals: {path.name} -> {voc.name}{' + ' + mus.name if music else ''} on {r.stdout.strip()} "
                  f"in {time.time() - t:.0f} s", file=sys.stderr)
            return voc
        print(f"vocals: {dev} failed: {(r.stderr or '').strip()[-400:]}", file=sys.stderr)
    sys.exit("vocals: separation failed on every device")


def _inner(src, voc, mus, dev, overlap, model):
    """Runs inside the venv: separate, then write stems trimmed/padded to the song's exact length."""
    import numpy as np, soundfile as sf, torch
    from audio_separator.separator import Separator
    if dev == "xpu" and not (hasattr(torch, "xpu") and torch.xpu.is_available()):
        raise SystemExit("no XPU device visible to PyTorch")
    with tempfile.TemporaryDirectory() as tmp:
        sep = Separator(model_file_dir=str(MODELS), output_dir=tmp, output_format="WAV", log_level=30,
                        output_single_stem=None if mus else "Vocals",
                        mdxc_params={"segment_size": 256, "override_model_segment_size": False, "batch_size": None,
                                     "overlap": int(overlap), "pitch_shift": 0})
        sep.torch_device = torch.device(dev)
        sep.load_model(model_filename=model)
        sep.model_instance.torch_device = torch.device(dev)
        outs = [Path(tmp) / Path(o).name for o in sep.separate(src)]
        n_src = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                            "csv=p=0", src], capture_output=True, text=True).stdout) * 44100)
        for o in outs:
            name = o.name.lower()
            dest = voc if "(vocals)" in name else mus if mus and ("(other)" in name or "(instrumental)" in name) else None
            if not dest:
                continue
            x, sr = sf.read(str(o), always_2d=True)
            if sr == 44100 and abs(len(x) - n_src) < 4410:   # keep the timeline exact: same sample count as the song
                x = x[:n_src] if len(x) >= n_src else np.pad(x, ((0, n_src - len(x)), (0, 0)))
            sf.write(dest, x, sr, subtype="PCM_16")
    print(torch.xpu.get_device_name(0) + " (XPU)" if dev == "xpu" else "CPU")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--_inner":
        a = sys.argv[2:]
        return _inner(a[0], a[1], a[2] or None, a[3], a[4], a[5])
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media", type=Path, nargs="+")
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--music", action="store_true", help="also write <stem>.music.wav")
    ap.add_argument("--device", choices=["auto", "xpu", "cpu"], default="auto")
    ap.add_argument("--overlap", type=int, default=OVERLAP, help=f"chunk overlap (default {OVERLAP}; model default 8, slower)")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--force", action="store_true", help="separate again even if a fresh stem exists")
    a = ap.parse_args()
    for m in a.media:
        print(vocals(m, a.out_dir, a.music, a.device, a.overlap, a.model, a.force))


if __name__ == "__main__":
    main()
