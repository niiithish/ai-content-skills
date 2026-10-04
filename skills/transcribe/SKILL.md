---
name: transcribe
description: Speech to text with word timestamps for any audio or video file. ElevenLabs Scribe v2 is the default; Parakeet (local, CPU) runs when there's no key or no network, and faster-whisper last. Writes a transcript, a words.json and optionally an SRT. Use when the user wants a transcript, speech-to-text, word timestamps, subtitles from audio, "what does he say", to time a voiceover, or to find swears, bleeps or mutes. The captions, video-plan and song-ad scripts use its helper.
---

# Transcribe

ElevenLabs Scribe v2 is the speech-to-text for every skill here. On a 145 s voiceover, scored against its script:

| Engine | Time | Wrong words |
|---|---|---|
| ElevenLabs Scribe v2 | 4.5 s | none (only US spellings and hyphens differ); the muted swears marked `[censored]` with their times |
| Parakeet (CPU) | 27 s | 3: "mint" for "mince", and the full swear at two muted spots |
| faster-whisper small.en | 77 s | twice as many; made swears up where the audio is muted |

## Run it

```bash
<skill-dir>/scripts/transcribe.py path/to/file.mp4 [more files] [--srt] [--out-dir DIR] [--engine auto|elevenlabs|parakeet|whisper]
```

For each file it writes, next to the file or in `--out-dir`:

- `<stem>.txt`: the transcript;
- `<stem>.words.json`: `[{"word", "start", "end"}]` in seconds, punctuation kept on the word;
- `<stem>.srt` with `--srt`: one cue per sentence.

It prints which engine ran, the word count and the elapsed time. Any format ffmpeg reads works.

- **Sound events** come through as bracketed words with their times: `[censored]` for a muted or bleeped word, `[laughter]`, `[hip hop music]`. Search for `[censored]` to find mutes. Parakeet writes a mute as its first sound ("f", "fers") instead.
- Read the result before you rely on it: names, brand names and numbers are where any engine slips.
- Scribe output can differ a little between runs; rerun one file rather than trusting a single odd word.

## Engines and setup

`auto` (the default) tries each in order and moves on, saying why, when one can't run:

1. **ElevenLabs Scribe v2**: the key comes from `$ELEVENLABS_API_KEY`, else `~/.config/elevenlabs/api_key`. The audio is uploaded to ElevenLabs as 16 kHz mono FLAC; it costs a few cents per hour of audio. Never print or commit the key.
2. **Parakeet** (`parakeet-tdt-0.6b-v3`, offline): `pip install "onnx-asr[cpu,hub]"`. The model is read from `~/.local/share/voxtype/models/parakeet-tdt-0.6b-v3` when it's there, otherwise downloaded once. Full precision on purpose: int8 was no faster and got swears wrong. Files over 5 minutes are cut at the quietest moment near each boundary.
3. **faster-whisper** `small.en`: `pip install faster-whisper`.

Naming an engine starts the chain there: `--engine parakeet` when the client's audio must not leave the machine.

## From other scripts

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "transcribe" / "scripts"))
from transcribe import words
words("voiceover/recording.wav")   # [(word, start, end), ...]
```

`captions.py words`, `plan.py voiceover` and `song-ad` (through `plan.py`) get their heard words this way, then align the script to them, so the wording on screen still comes from the script.
