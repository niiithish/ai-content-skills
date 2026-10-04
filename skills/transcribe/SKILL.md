---
name: transcribe
description: Speech to text with word timestamps for any audio or video file, on the CPU. NVIDIA Parakeet (parakeet-tdt-0.6b-v3 via onnx-asr) is the default; faster-whisper is only a fallback. Writes a transcript, a words.json and optionally an SRT. Use when the user wants a transcript, speech-to-text, word timestamps, subtitles from audio, "what does he say", to time a voiceover, or to find swears, bleeps or mutes. The captions, video-plan and song-ad scripts use its helper.
---

# Transcribe

Parakeet is the speech-to-text for every skill here. On a 145 s voiceover on CPU it took 4 s to load and 19 s to transcribe, and it wrote muted swears as they sound ("f"). Whisper small.en took longer and made swears up where the audio was muted; medium.en took 82 s and dropped them. Use whisper only when Parakeet can't run.

## Run it

```bash
<skill-dir>/scripts/transcribe.py path/to/file.mp4 [more files] [--srt] [--out-dir DIR]
```

For each file it writes, next to the file or in `--out-dir`:

- `<stem>.txt`: the transcript;
- `<stem>.words.json`: `[{"word", "start", "end"}]` in seconds, punctuation kept on the word;
- `<stem>.srt` with `--srt`: one cue per sentence.

It prints the word count and the elapsed time. Any format ffmpeg reads works: it converts to 16 kHz mono first. Files longer than 5 minutes are transcribed in pieces cut at the quietest moment near each boundary.

Read the result before you rely on it: names, brand names and numbers are where it slips. A muted or bleeped word shows up as its first sound ("f", "f'", "fers"), so search for short fragments to find mutes.

## Setup

- `pip install "onnx-asr[cpu,hub]"` (and ffmpeg). The model is read from `~/.local/share/voxtype/models/parakeet-tdt-0.6b-v3` when it's there, otherwise downloaded once from Hugging Face.
- Full precision on purpose: the int8 model was no faster on this CPU and got swears wrong on the test voiceover.
- When onnx-asr can't be imported or the model won't load, it says so and falls back to faster-whisper `small.en` (`pip install faster-whisper`). `--engine whisper` forces it.

## From other scripts

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "transcribe" / "scripts"))
from transcribe import words
words("voiceover/recording.wav")   # [(word, start, end), ...]
```

`captions.py words`, `plan.py voiceover` and `song-ad` (through `plan.py`) get their heard words this way, then align the script to them, so the wording on screen still comes from the script.
