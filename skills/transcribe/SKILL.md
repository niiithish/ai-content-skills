---
name: transcribe
description: >
  Speech to text with word timestamps for any audio or video file. Fully local: Parakeet
  on the Intel GPU first, then Parakeet on the CPU (two runtimes), then faster-whisper.
  Writes a transcript, a words.json and optionally an SRT. Use when the user wants a
  transcript, speech-to-text, word timestamps, subtitles from audio, "what does he say",
  to time a voiceover, or to find swears, bleeps or mutes. For a song (sung ad, AI singing
  ad), it first splits the vocals from the music (`vocals`, MelBand RoFormer on the Arc GPU)
  so the caption timing comes from the voice alone. The captions, video-plan and song-ad
  scripts use its helper.
---

# Transcribe

Parakeet (local, Intel GPU with CPU fallback) is the speech-to-text for every skill here. Nothing leaves the machine.

## Run it

Easiest, from any shell or any LLM tool: `transcribe FILE [--srt] [--out-dir DIR] [--verify]` (`~/.local/bin/transcribe`, which runs the script below in the venv at `~/.local/share/transcribe-venv`).

**Engines, in order** (`auto` moves on to the next when one fails, and prints why):
1. `parakeet-gpu`: **Parakeet TDT 0.6B v3 on the Intel Arc GPU** through parakeet.cpp + Vulkan (`~/.local/share/parakeet-cpp/`: `bin/parakeet-cli`, `lib/`, `model/tdt-0.6b-v3-f16.gguf`; source and build in `~/Work/tries/parakeet-cpp/`). 1 min in ~1.5 s, 3 min in ~2.6 s, 30 min in ~26 s.
2. `parakeet-cpu`: the same binary and model on the CPU (3 min in ~18 s). Same output, so a GPU-only problem is covered without changing anything else.
3. `parakeet-onnx`: Parakeet through onnx-asr, a separate runtime, in case parakeet.cpp itself breaks.
4. `whisper`: faster-whisper (medium.en if downloaded, else small.en). A different model with looser timing, last resort.

Every engine runs as its own process (engines 3 and 4 in the venv), so callers can use any `python3`, and a crash in one engine can't take the caller down.

**Load and unload:** each call loads the model (about 1 s), runs, and exits, which releases the GPU. Nothing stays resident.

**Reliability, because a bad caption ruins a video:**
- A crash, a hang (killed after a timeout of 10-30x the expected time) or a missing install moves on to the next engine.
- Every result must pass a sanity check (ordered, inside the file, plausible word rate). Zero words in a file over 3 s is passed on to the next engine, so silence is confirmed, never trusted.
- parakeet.cpp quietly uses the CPU when the named GPU isn't found. The script reads back which device actually ran and labels the result honestly.
- `--verify` (or `TRANSCRIBE_VERIFY=1`) re-runs a GPU result on the CPU. If any word differs, or any word start differs by more than 0.15 s (one 80 ms step is normal), it keeps the CPU result. `fc_captions.py` always does this. It costs about 1 s of CPU per 10 s of audio.
- Tested: GPU, CPU, ONNX and whisper on the same file (the three Parakeet engines gave identical words); wrong GPU name, engine abort, out-of-order output, empty output, missing install, a hang and a GPU/CPU timing disagreement each fell back to a correct result. All test audio was one synthetic voice, so keep `--verify` on for real speakers.
- **Other models tested for word timing (2026-11-07), none better, so nothing was switched:** Qwen3-ForcedAligner-0.6B (aligns the script), faster-whisper small.en / medium.en / large-v3-turbo, against waveform onsets on a 3-min real voiceover. Where the script matched the recording, all were within ~110 ms of each other in scatter (Parakeet 45% of starts within 2 frames, Qwen 40%, small.en 44%), and Qwen's timestamps are 80 ms steps like Parakeet's. Qwen broke where the read differed from the script (up to 3.8 s off) and gave several fast repeated words ("all of it, all of it") the same time. Bigger Whisper models were not more accurate. No ASR is frame-accurate: the caption planner's waveform snapping (onsets, dips) is what makes captions land. Bench: `~/Work/tries/asr-bench/` (`bench.py`, `score.py`).
- Songs: see "Songs" below; transcribe the vocal stem, not the mix.
- Rebuilding parakeet.cpp: see `~/Work/tries/parakeet-cpp/` (cmake and Vulkan headers were installed locally, no sudo).

For each file it writes, next to the file or in `--out-dir`:

- `<stem>.txt`: the transcript;
- `<stem>.words.json`: `[{"word", "start", "end"}]` in seconds, punctuation kept on the word;
- `<stem>.srt` with `--srt`: one cue per sentence.

It prints which engine ran, the word count and the elapsed time. Any format ffmpeg reads works.

- **Muted or bleeped words** are not marked: Parakeet writes a mute as its first sound ("f", "fers"). Use `pauses.py` to find them.
- Read the result before you rely on it: names, brand names and numbers are where any engine slips.

## Setup notes

- **Venv** `~/.local/share/transcribe-venv` (Python 3.12, uv): `onnx-asr[hub]`, plain `onnxruntime` (CPU), `faster-whisper`. Don't add `onnxruntime-openvino` next to `onnxruntime`: they overwrite each other's files, and OpenVINO on this Arc GPU aborted on variable-length audio anyway.
- ONNX engine: the model is read from `~/.local/share/voxtype/models/parakeet-tdt-0.6b-v3` when present. Full precision on purpose: int8 got swears wrong. Files over 30 s are cut at the quietest moment near each boundary.
- faster-whisper is given decoded samples, not a path: 1.2.1's own decoder breaks on the installed PyAV.
- Naming an engine starts the chain there: `--engine parakeet-gpu|parakeet-cpu|parakeet-onnx|whisper`. `TRANSCRIBE_VK_DEVICE` picks the Vulkan device (default `Vulkan0`).

## From other scripts

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "transcribe" / "scripts"))
from transcribe import words
words("voiceover/recording.wav")                # [(word, start, end), ...]
words("vo.wav", verify=True)                    # for captions
```

`fc_captions.py`, `plan.py voiceover` and `song-ad` (through `plan.py`) get their heard words this way, then align the script to them, so the wording on screen still comes from the script.

## Songs: split the vocals first

For any sung track (song ads, AI singing animated ads), time from the **vocal stem**, never the mix:

```bash
vocals SONG [--music] [--out-dir DIR]          # -> SONG.vocals.wav (+ SONG.music.wav); ~1 min for a 4 min song
transcribe SONG --vocals                       # splits (or reuses a fresh stem), then transcribes the stem
```

```python
from vocals import vocals;  vocals("song.wav")          # Path of the stem, reused while newer than the song
words("song.wav", vocals=True)
```

- **What it fixes (measured on a 4:12 Suno-style song ad, 2026-11-20):** Parakeet's word starts were the same on the mix and the stem (median 0 s difference). The problem is the waveform: in the mix the music fills the gaps between sung lines, so `pauses.py` found only 10 of 37 real line gaps and caption starts/ends had nothing to snap to; on the stem every gap is true silence (-80 to -90 dB) and all 37 were found. Parakeet alone was 3+ frames off on 25 of those 37 line starts (median 0.16 s early, worst 2 s), and it doesn't measure where a held note ends. So the stem's job is the waveform checks: line onsets and voice ends, held notes included.
- **The stem keeps the song's timeline exactly:** same sample count, 0 offset, and vocals + music sum back to the song (-73 dB residual). Times from the stem are the song's times. It is for timing only: never put it in the edit.
- **Timeline edits are handled by where the audio comes from:** `fc_captions.py words` exports the song from the edited FilmCraft timeline (trimmed, moved or re-timed as it is) and splits that export, so the stem always matches the edit, not the original file.
- **Check by eye:** `scripts/caption_preview.py SONG.vocals.words.json SONG.mp3 --voice SONG.vocals.wav -o check.mp4` renders a black 1080x1920 video with white captions over the original song and a timecode, snapped to the stem's onsets and voice ends.
- **Model and runtime:** `vocals_mel_band_roformer.ckpt` (Kimberley Jensen, vocals SDR 12.6, the top vocal model in audio-separator's list; Demucs htdemucs_ft 10.8), 913 MB in `~/.local/share/separate-models/`, through python-audio-separator 0.48 in `~/.local/share/separate-xpu-venv` (Python 3.12, torch 2.15.0+xpu, ~3 GB with Intel's oneAPI runtime). audio-separator only knows CUDA/MPS/DirectML, so `vocals.py` sets the device to `xpu` itself; on the Arc B570 a 4:12 song took 59 s. If the GPU fails it falls back to the CPU and says so (the CPU took over 10 min at the model's default overlap 8; `vocals.py` uses overlap 2). Each run is its own process, so the GPU is released when it ends.
- Lyrics on screen still come from the lyric sheet: the stem fixes timing, and words the singer slurs ("con" / "calm") stay misheard either way.

## Pauses: where the voice actually stops

ASR can't say where a word ends: Parakeet gives word starts only, and Whisper's ends drift. For cuts and caption ends, use the waveform:

```bash
<skill-dir>/scripts/pauses.py voice.wav [--least 0.15]      # speech end, onset and length of every pause
```

```python
from pauses import load, find_pauses
find_pauses(load("vo.wav"))        # [(speech_end, onset), ...] in seconds
```

The quiet threshold comes from each recording: 40% of the way from its noise floor (8th percentile) to its speech level (90th). A fixed -40 dB (ffmpeg silencedetect) found none of the pauses in Max video-2, whose AI clips carry room tone above it. Silero VAD holds on too long to see 0.2–0.5 s pauses. Pauses under 0.15 s are stop consonants, not pauses. `filmcraft-pacing` and `captions-filmcraft` use it.
