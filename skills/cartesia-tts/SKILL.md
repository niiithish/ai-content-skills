---
name: cartesia-tts
description: Generate text-to-speech voiceovers and voice samples with Cartesia (Sonic 3.6) via the `cartesia` CLI, outputting a WAV plus exact word timestamps (OUT.words.json) and per-line timing. Use for any TTS, voiceover, scratch read, voice audition, or before video-plan so shots are timed from a real read. Not for speech-to-text transcription (use transcribe) or ElevenLabs Voice Isolator (use elevenlabs-creative).
compatibility: Requires python3, ffmpeg, cartesia CLI, and CARTESIA_API_KEY (or ~/.config/cartesia/api_key).
metadata:
  author: ai-content-skills
  version: "2.0"
---

# Cartesia TTS

All TTS voiceovers run through `cartesia` (`~/.local/bin/cartesia` → `scripts/cartesia.py`), using model alias `sonic-3.6` (pin with `--model sonic-3.6-2026-08-27` when re-reads must match exactly).

**API Key:** read from `~/.config/cartesia/api_key` (chmod `600`, folder `700`) or `$CARTESIA_API_KEY`. Never print, commit, or pass it on a command line.

## Fast One-Prompt Onboarding (No 4-Turn Ping-Pong)

- **If the project already locked a voice** (`voiceover/recording.voice.json` or approved `PLAN.md`): reuse that voice, speed, and emotion directly without re-asking.
- **For a new voiceover**: first pull 3–5 fitting candidates and save their previews (`cartesia voices ... --previews voiceover/voices`), then ask **everything in one single concise message**:
  1. **Tool**: Cartesia (default) or another (ElevenLabs / client's own recording)?
  2. **Voice**: list the 3–5 candidates with your **#1 recommended pick** + full path to `voiceover/voices/` (user can also paste any Cartesia voice ID or `--mine` clone).
  3. **Speed & Emotion**: recommend speed (`1.0` or `1.1` if ad runs at 1.1x) and emotion (`neutral`, `calm`, `content`, `sad`, `angry`, `scared` — default `neutral`).

Wait for that one reply. Only run `audition` if the user asks to hear candidates on their own script first; otherwise generate the full read immediately.

## Commands

```bash
# Search voices and save MP3 previews
cartesia voices warm narrator --gender feminine --limit 10 --previews voiceover/voices
cartesia voices --mine

# Optional: audition first 2 lines of script in candidate voices
cartesia audition --script voiceover/script.md --voices ID1,ID2,ID3 --out voiceover/audition

# Full script read (writes .wav, .words.json, .lines.json, .voice.json)
cartesia say --script voiceover/script.md --voice ID --speed 1.0 --out voiceover/recording.wav

# Single-line quick test
cartesia say "One line to test." --voice ID --out /tmp/test.wav

# Reference lists
cartesia emotions
cartesia models
```

Inline SSML-style tags supported mid-script: `<emotion value="sad"/>`, `<speed ratio="0.9"/>`, `<volume ratio="1.2"/>`, `[laughter]`.

## Outputs of `cartesia say`

- `recording.wav`: 44.1 kHz mono, lines joined with `--gap` silence (default `0.4` s).
- `recording.words.json`: exact Cartesia word timestamps `[{"word", "start", "end"}]` (compatible with `transcribe` and `plan.py voiceover` — no ASR needed).
- `recording.lines.json`: per-line start/end times.
- `recording.voice.json`: voice ID, model, speed, and emotion used (cite in `PLAN.md`).
- `recording.lines/`: per-line cache so editing one line only regenerates that line.

## Integration with `video-plan`

Write `voiceover/script.md` (one spoken line per row), confirm the single onboarding prompt, and render to `voiceover/recording.wav`. Then `plan.py voiceover <video-folder>` reads `recording.words.json` directly to time the shot table.
