---
name: transcribe
description: Local speech-to-text with word timestamps for any audio or video file using Parakeet TDT 0.6B v3 on Intel GPU (Vulkan) with CPU and faster-whisper fallbacks, plus local vocal separation (`vocals`, MelBand RoFormer on XPU) for sung ads. Writes .txt, .words.json, and optional .srt. Use for transcripts, word timestamps, voiceover timing, song vocal splitting, pause detection, or finding bleeps/mutes. Not for cloud ASR (forbidden) or TTS generation (use cartesia-tts).
compatibility: Requires python3, ffmpeg, and local parakeet-cpp / transcribe-venv / separate-xpu-venv installs.
metadata:
  author: ai-content-skills
  version: "2.0"
---

# Transcribe (Local ASR & Vocal Separation)

All transcription runs **100% locally** via `transcribe` (`~/.local/bin/transcribe` → `scripts/transcribe.py`). Never use cloud ASR.

## Run `transcribe`

```bash
transcribe FILE [--srt] [--out-dir DIR] [--verify] [--engine NAME] [--vocals]
```

Writes next to `FILE` (or into `--out-dir`):
- `<stem>.txt` — plain transcript
- `<stem>.words.json` — `[{"word", "start", "end"}]` in seconds
- `<stem>.srt` (with `--srt`) — sentence-split subtitles

### Engine Fallback Chain (`auto`)

1. **`parakeet-gpu`**: Parakeet TDT 0.6B v3 on Intel Arc GPU via `parakeet.cpp` + Vulkan (`$PARAKEET_DIR`, default `$HOME/.local/share/parakeet-cpp`: `bin/parakeet-cli`, `lib/`, `model/tdt-0.6b-v3-f16.gguf`). ~70× real time.
2. **`parakeet-cpu`**: Same `parakeet.cpp` binary/model on CPU (~10× real time).
3. **`parakeet-onnx`**: `onnx-asr` in `$HOME/.local/share/transcribe-venv` (reads `$HOME/.local/share/voxtype/models/parakeet-tdt-0.6b-v3` if present, full precision).
4. **`whisper`**: `faster-whisper` (`medium.en` or `small.en`, decoded samples passed directly) in `transcribe-venv` as last resort.

Every engine runs in an isolated subprocess and releases the GPU on exit. Crashes, hangs (killed at 10–30× expected duration), empty results on >3 s files, or sanity-check failures automatically fall through to the next engine.

### Reliability & Verification

- **`--verify`** (or `TRANSCRIBE_VERIFY=1`): cross-checks a GPU result against CPU; if any word differs or shifts >0.15 s, keeps CPU. Always use `--verify` for captions (`fc_captions.py` enables it automatically).
- `TRANSCRIBE_VK_DEVICE` selects the Vulkan device (default `Vulkan0`).
- **Mutes/bleeps**: Parakeet writes a muted word as its first sound; use `scripts/pauses.py` to detect real gaps.
- Always eyeball brand names, proper nouns, and numbers before relying on raw ASR output.

## Songs: Split Vocals First (`vocals`)

For sung ads / AI singing tracks, always time from the **vocal stem**, never the mixed track (music fills line gaps and breaks waveform snapping):

```bash
vocals SONG [--music] [--out-dir DIR]   # -> SONG.vocals.wav (+ optional SONG.music.wav)
transcribe SONG --vocals                # splits (or reuses fresh stem), then transcribes stem
```

- Uses `vocals_mel_band_roformer.ckpt` in `$HOME/.local/share/separate-models/` via `$HOME/.local/share/separate-xpu-venv` (`python-audio-separator` on Intel XPU, CPU fallback).
- Preserves exact sample count and zero offset (`vocals + music` sums back to the original); use the stem for timing only, never put it in the final mix.
- Quick visual check: `python3 <skill-dir>/scripts/caption_preview.py SONG.vocals.words.json SONG.mp3 --voice SONG.vocals.wav -o check.mp4`.

## Pause Detection (`pauses.py`)

ASR gives word starts, not exact speech ends. Use waveform pause detection for cuts and caption ends:

```bash
python3 <skill-dir>/scripts/pauses.py voice.wav [--least 0.15]
```

Uses an adaptive threshold (40% between 8th-percentile noise floor and 90th-percentile speech level) rather than fixed `-40 dB`.

## Python Helper API (for other skills)

```python
from transcribe import words
ws = words("voiceover/recording.wav")          # [(word, start, end), ...]
ws = words("vo.wav", verify=True)              # caption-grade
ws = words("song.wav", vocals=True)            # auto vocal-split + transcribe

from vocals import vocals
stem = vocals("song.wav")                      # Path to reused/generated vocal stem

from pauses import load, find_pauses
gaps = find_pauses(load("vo.wav"))             # [(speech_end, onset), ...]
```

## Environment Notes

- `PARAKEET_DIR`: overrides `$HOME/.local/share/parakeet-cpp`.
- `transcribe-venv`: Python 3.12 with `onnx-asr[hub]`, plain `onnxruntime` (never install `onnxruntime-openvino` alongside it), and `faster-whisper`.
- `separate-xpu-venv`: Python 3.12 with `torch` XPU + `audio-separator`.
