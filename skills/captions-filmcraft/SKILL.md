---
name: captions-filmcraft
description: "Put captions into a FilmCraft project as editable text clips, each one starting on the exact frame its phrase is spoken and on the frame of every picture cut, then export the deliverable from FilmCraft. Caption blocks are whole script phrases of at most 4 words, back to back with no gaps, in the captions skill's one-line templates (4 sentence-case Montserrat, 2 ALL CAPS TikTok Sans). Timing comes from the project's own voiceover track: Parakeet and faster-whisper word times calibrated against the waveform, never one engine alone. Use when the user edits in FilmCraft and wants captions, subtitles or supers on a .fcproj, wants caption timing fixed in one, or a client complains captions are late or don't change with the picture. For burning captions into an exported video file instead, use captions."
---

# Captions in FilmCraft

The user edits and exports in FilmCraft, so captions go into the project as text clips they can see, nudge and export themselves, not burned into a render. Tool: `scripts/fc_captions.py` (needs `filmcraft-cli`, ffmpeg, numpy, `onnx-asr` and `faster-whisper`; it imports the `transcribe` skill's Parakeet helper, so install that skill alongside, and the fonts come from the `captions` skill's `fonts/`).

## The rules (a client's review, now the standard for every video)

1. **Picture, caption and voice change on the same frame.** Every cut on V1 starts a caption, and every caption starts on the frame its first word is heard: never a few frames late, never before the cut.
2. **Blocks are whole script phrases, at most 4 words.** Three words when that reads well, four only where the phrase needs it ("dimples that barely show," / "even in bathroom light.", not "dimples that barely" / "show, even"). Never split a name, a number and its unit, or "65% off".
3. **Back to back.** Each caption stays up until the next starts; the last runs to the end of the sequence. No blank frames in pauses.

## Why the timing works this way

ElevenLabs Scribe alone was 0.16 s (4 frames) late on part of a voiceover, and the client saw it. Engines disagree by a few frames, and each one drifts. So `plan`:
- After a pause (at least 0.1 s of silence), starts the caption on the frame where the voice comes back (ffmpeg silencedetect). This is exact.
- Mid-sentence, takes Parakeet's word start plus Parakeet's measured lead on this recording (about 0.08 s), averages it with faster-whisper when the two agree within 0.3 s, and moves it to the end of a real pause just before it. A silent frame is below -40 dB and 25 dB under the speech around it, so a quiet read isn't mistaken for silence. Expect about ±1 frame.
- Snaps the nearest caption onto every cut within 6 frames, and reports a cut that is more than 2 frames off its voice (the cut is wrong then, not the caption) or has no phrase starting near it.

## Process

1. Quote what the brief or the user says about captions in one line, and the template (default 4, the house look on Max's Aleo videos). Make sure FilmCraft is closed: the app keeps its own copy of the project and would overwrite the change (or ask the user to save and close it).
2. Voiceover and word times, per project (about 40 s for a 45 s ad):

   ```bash
   <skill-dir>/scripts/fc_captions.py words video-N/edit/hook-1.fcproj        # --vo A2 if the voice isn't on A1
   ```

   It deletes every other audio track in memory, exports the voice as `captions/<stem>.vo.wav` and never saves the project.
3. Blocks. Put the voiceover script for this edit (each hook has its own first lines) in a text file, then:

   ```bash
   <skill-dir>/scripts/fc_captions.py plan video-N/edit/hook-1.fcproj --script video-N/captions/hook-1.script.txt
   ```

   The first run writes `captions/<stem>.blocks.txt` (one caption per line, split at punctuation and into phrases of at most 4 words) and stops. **Read every line** against rule 2 and fix the file by hand: the split is a draft ("she made the backs" should be "Here's how she made" / "the backs"). Run `plan` again. It prints every caption with its start, length and source (`onset`, `words`, `pause`, `+cut`) and a `NOTE` for each cut that is off its voice, has no phrase near it, or a block over 4 words. Fix the blocks, or tell the user which cut to move and by how many frames. Brand words the engines mishear go in `--fixes` (`alio | aleo`, one per line); they only help the matching, never the text on screen.
4. Build:

   ```bash
   <skill-dir>/scripts/fc_captions.py build video-N/edit/hook-1.fcproj -t 4
   ```

   It writes the text clips to the top video track when that track holds only text (replacing the old captions), or to a new track on top. It saves to a temp file and checks that no other track changed and that every caption sits on its planned frames. Only then does it copy the original to `edit/backup-<date>-captions/` and write the new project, with the project's name kept (FilmCraft renames a project to the file it was saved as). Use `--track V3` to choose the track. End cards and other overlays stay on their own tracks, untouched.
5. Check: `fc_captions.py check PROJECT` renders the frame before and the first frame of about 8 captions (mid-sentence ones and two cuts) into `captions/<stem>.check.png`. Look at it: each pair must flip caption, and at a cut flip picture, between its two frames. Send it to the user, and tell them to look in FilmCraft before exporting.
6. Export only when the user says so: `fc_captions.py export PROJECT -o video-N/deliverables/<Brand>_<Concept>_<Variant>_<Ratio>.mp4` (the `filmcraft` skill's Meta settings: H.264 high, 6 Mb/s VBR 1-pass, AAC 192k, about 45 MB a minute; written to `.tmp.mp4` and renamed when done). Don't also burn captions with the `captions` skill: they are already in the picture.

## Templates

| # | Look |
|---|---|
| 4 | Sentence-case white Montserrat ExtraBold 68, 3 px black outline, soft shadow (blur 7, 4 px down, 75%), centred, baseline y 1420 |
| 2 | Same, ALL CAPS TikTok Sans ExtraBold 68 |

They match the `captions` skill's templates of the same number, inside the Meta/TikTok safe box (bottom y 1500 on 1080×1920). A missing font is installed from the `captions` skill's `fonts/` into `~/.local/share/fonts`. Boxed (1), karaoke (3) and extruded (5) captions need the `captions` skill.

## Rules

- Work files (`<stem>.vo.wav`, `.pk.json`, `.fw.json`, `.blocks.txt`, `.captions.json`, `.check.png`) go in `video-N/captions/`, never a session scratchpad.
- Never `build` while FilmCraft has the project open, and never save a project from the FilmCraft MCP without reloading it from disk first: its copy goes stale the moment the user edits.
- When the user moves cuts or changes the voiceover, run `words` (voice changed) or `plan` (cuts changed) and then `build` again; `build` refuses a plan made before the edit changed.
- Never write caption copy the script doesn't have.
