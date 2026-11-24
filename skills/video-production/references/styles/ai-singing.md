# Style Module: AI Singing / Story Song Ad (`--style ai-singing`)

A sung video sales letter (1–5 min) over 3D Pixar-style animation (combine with `pixar-3d.md` for visual direction and sheets). The generated song is the absolute timing spine — never cut, trim, or speed up the body of the song.

## 1. Lyrics & Song Script

1. **Real song craft, never plain prose:** Rhymed couplets (4–10 words per line, one visual beat = 2–4 s), steady meter, one refrain that returns 2–4 times and flips meaning at the payoff.
2. **Product & before/after arc:** Lock the hero's **before** (visible problem/dullness) and **after** (visible transformation) sheets upfront in `PROJECT_STATE.json` so the visual story matches the product logic.
3. **Validate with `song.py`:**
   ```bash
   python3 <skill-dir>/scripts/song.py lyrics video-N/song/lyrics-v1.md --video video-N
   ```
   Fix any lines flagged too long or too short, and save the clean lead lines to `video-N/voiceover/script.md`.

## 2. Suno Generation (Default) — Copy-Ready Formatting Lock

Always give the user **two separate, clean fenced copy boxes** (and save to `video-N/song/suno/style.txt` and `lyrics.txt`) so they can paste straight into Suno Create → Advanced (paid plan required for ads):

- **Box 1 — Style prompt ONLY** (short, positive keywords only; **NEVER put `[Verse]`, `[Chorus]`, or section-by-section structure inside the Style box**):
  ```text
  short commercial jingle, [GENRE], [BPM] BPM, [VOCAL: gender, age, tone], clear diction, brand name sung clearly, vocals start at 00:00, no build-up, memorable hook, tight ending
  ```
  *Proven alternatives:* `"theatrical pop-rock, Broadway storytelling, 104 BPM, expressive mature female vocal, conversational talk-singing verses, powerhouse belted choruses, driving piano, strings, punchy drums, vocals at 00:00"`. Never name real artists.
- **Box 2 — Lyrics ONLY** (plain `[Verse]`, `[Chorus]`, `[Outro]`, `[End]` tags only — strip `{music cues}` and `(backing answers)`; put the brand name on its own line, spelled phonetically if Suno mispronounces it).

## 3. Intro-Trim & Vocal-Onset Sync (`vocals` + `transcribe`)

Suno often adds a 1–5 s instrumental intro before the first sung word, and instruments mask ASR word timestamps.

1. Save the chosen take to `video-N/voiceover/recording.wav`.
2. **Split vocals first** using `vocals` (MelBand RoFormer via `transcribe` skill) so timing and captions run on the isolated voice stem alone.
3. **Check exact vocal onset:** If there is an instrumental intro before the first lyric, either trim the intro head cleanly OR plan dedicated silent establishing/beat-synced shots for those opening seconds — **never have a character start lip-syncing at `0.0 s` while only instruments are playing.**
4. Time every lyric line with `video-plan` (`plan.py voiceover video-N`). Flag any line ASR can't find so the user can check if the singer dropped or mangled it.
5. **Capability-aware audio fast-path:** If your runtime supports native audio input (e.g., Gemini / Antigravity), listen directly to the Suno `.mp3` and separated `vocals.wav` to verify the intro swell, exact vocal onset, held notes, and musical phrasing when matching visuals to beats — still relying on `vocals` → `transcribe` for exact timestamps. Text-only agents rely on `vocals` + `transcribe` + `pauses.py`.

## 4. Visual Planning & Production

- **Mix singing & silent B-roll:** About 30–40% of runtime is on-camera lip-sync (`SUNG`: hook, refrains, climax); the remaining 60–70% is silent 3D B-roll (`pixar-3d.md`) cutting every 2–4 s. Every second of the song (including instrumental breaks and the 2–5 s end-card tail) needs picture.
- **B-roll clips:** Generate in direct 1080p via `make.py clips` (muted under the song in the edit).
- **Lip-sync shots (outside Flow):** Flow cannot take an audio track. Generate each sung shot's approved still first, then cut gapless audio slices:
  ```bash
  python3 <skill-dir>/scripts/song.py slice video-N 1-2 14 38-39
  ```
  (`--all` slices the entire song into ≤10 s consecutive chunks.) Hand off each still + character sheet + slice to an audio-driven lip-sync model (`MiniMax H3 Max`, `Seedance 2.0`, Sync Labs, or HeyGen via `elevenlabs-creative`).

## 5. Edit & Captions Handoff

- Full uncut song on A1; every video clip muted above it (`filmcraft-edit`). Never run `filmcraft-pacing` silence removal on a song ad.
- Captions (`captions-filmcraft`) always time from the vocal stem (`vocals` → `transcribe`) and use the lyric sheet's exact lead lines (especially across dragged/held notes).
