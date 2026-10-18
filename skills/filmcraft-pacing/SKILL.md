---
name: filmcraft-pacing
description: "Make a FilmCraft talking-head or voiceover edit more engaging, in place on the .fcproj: cut the dead air in the voice down to a natural breath (found from the waveform, not ASR), keep every other track in sync, add a punch-in at each visible jump cut, a slow push on long still shots and a slow push in/out on static B-roll, and report the numbers (pauses, shot lengths, still stretches, captions shown through silence, music level). Calm style for viewers over about 35 (Meta buyers), punchy for young creator style. Use when the user edits in FilmCraft and says an edit drags, has long gaps or silences, feels static or boring, needs zooms, punch-ins or more motion, or asks how engaging or well paced it is. Run it after the timeline is built and before captions. Not for building the timeline or exporting (filmcraft), captions (captions-filmcraft), or edits outside FilmCraft."
---

# Pacing in FilmCraft

Tool: `scripts/pace.py`. It needs the `filmcraft` skill (`fc.py`, so edits go live when the app has the project open) and the `transcribe` skill (`pauses.py`) installed alongside, plus numpy and ffmpeg (ffmpeg only reads the voice for analysis; the edit never leaves FilmCraft).

## The workflow

1. **Report** first, and quote the numbers to the user:

   ```bash
   <skill-dir>/scripts/pace.py report video-N/edit/hook-1.fcproj        # --vo A2 if the voice isn't on A1
   ```

   It prints the pauses and how much each style would cut, shot lengths and the longest stretch with nothing changing, B-roll without motion, talking clips that already move, captions left up through a pause of 0.4 s or more, and the music gain.
2. **Tighten:** `pace.py tighten PROJECT --style calm` (add `--dry` to see the cuts first). It razors V1 and the voice track at each pause, ripple-deletes the dead air and moves every other clip (B-roll, overlays, music) to the time it was cut to. Cuts land on existing seams when one is within 2 frames, so no 1-frame slivers.
3. **Motion:** `pace.py motion PROJECT --style calm` (`--face-y` if the face isn't at about 40% of the height).
4. **Captions after the cuts:** the timing moved, so run `captions-filmcraft` `words`, `plan`, `build`, `check` again.
5. **Report again** and tell the user the before/after numbers. Never export (filmcraft does that when the user says so).

Each step saves a copy to `edit/backup-<date>-pacing/` the first time that day. When the app has the project open, edits go live and are saved there (fc.py decides).

## What it changes, and why these numbers

| | calm | punchy |
|---|---|---|
| A pause after a word is cut to | 0.12 s | 0.08 s |
| A pause of 0.35 s or more (sentence end) is cut to | 0.20 s | 0.12 s |
| Punch-in at a visible jump cut | 108% | 115% |
| Slow push on a still stretch longer than | 4 s, to 106% | 2.5 s, to 110% |
| B-roll push in/out | 100↔106% | 100↔110% |

- **Pauses.** Editors cut pauses over about 0.3 s and keep 50–150 ms so speech still breathes. Cutting to zero sounds robotic, and older viewers notice. 40 ms of silence is always kept before the voice comes back, so first consonants aren't clipped.
- **Pauses come from the waveform.** Parakeet gives word starts only, and Whisper's word ends drift. A fixed -40 dB threshold found none of the 0.2–0.5 s pauses in Max video-2: AI clips carry room tone above it. `pauses.py` sets the threshold from each recording, between its noise floor and its speech level.
- **Something changes every 3–5 s.** A cut, a zoom step or B-roll. Punch-ins of 10–20% hide a jump cut; slow pushes of 5–10% keep a long shot alive. Calm uses the low end: viewers over 35 dislike over-editing.
- **Cover jump cuts with B-roll where you can** (the lesson of the reel the user shared): a jump cut in a talking head reads as an edit, a cut to B-roll reads as a story. When `report` shows visible jump cuts and there is B-roll to spare, put it over them before running `motion`, which then punches only the jump cuts still visible.
- **Captions shouldn't stay up in silence.** `captions-filmcraft` now clears the screen in pauses of 0.4 s or more.
- **Music** sits 6–12 dB under the voice. `report` prints the gain. Change it only when the user asks.

## Rules

- Never touches a clip that already has motion: scale or position keyframed, scale not 100, or position moved. The user's or a build script's zooms stay.
- Only the talking track (V1 + the voice) is cut. Never cut music or B-roll to fit; they move with the time.
- Run it on the edit the user approved, and after the user's own tweaks read `report` before changing anything. To undo, copy the backup back (close the project in the app first, or it saves over it).
- Never export, and never use ffmpeg to render, re-encode or join a FilmCraft edit.
