---
name: captions-filmcraft
description: "Put captions into a FilmCraft project as editable text clips, each one starting on the exact frame its phrase is spoken and on the frame of every picture cut, then export the deliverable from FilmCraft. Caption blocks are whole script phrases of at most 4 words, back to back while the voice runs and cleared in real pauses, in two one-line templates (4 sentence-case Montserrat, 2 ALL CAPS TikTok Sans). Timing comes from the project's own voiceover track: Parakeet and faster-whisper word times calibrated against the waveform (`--fast` for Parakeet alone). Use when the user edits in FilmCraft and wants captions, subtitles or supers on a .fcproj, wants caption timing fixed in one, or a client complains captions are late or don't change with the picture."
---

# Captions in FilmCraft

The user edits and exports in FilmCraft, so captions go into the project as text clips they can see, nudge and export themselves, not burned into a render. Tool: `scripts/fc_captions.py` (needs `filmcraft-cli`, ffmpeg, numpy, `onnx-asr` and `faster-whisper`; it imports the `transcribe` skill's Parakeet helper, so install that skill alongside, and the fonts come from the `captions` skill's `fonts/`).

## The rules (a client's review, now the standard for every video)

1. **Picture, caption and voice change on the same frame.** Every cut on V1 starts a caption, and every caption starts on the frame its first word is heard: never a few frames late, never before the cut.
2. **Blocks are whole script phrases, at most 4 words.** Three words when that reads well, four only where the phrase needs it ("dimples that barely show," / "even in bathroom light.", not "dimples that barely" / "show, even"). Never split a name, a number and its unit, or "65% off".
3. **Back to back while the voice runs, gone in silence.** Each caption stays up until the next starts, unless the voice pauses for 0.4 s or more first: then it ends 2 frames after the voice stops. The last ends 2 frames after the last word. A caption is never shorter than half a second. `--hide 0` puts them back to back everywhere.

## Why the timing works this way

ElevenLabs Scribe alone was 0.16 s (4 frames) late on part of a voiceover, and the client saw it. Engines disagree by a few frames, and each one drifts. So `plan`:
- After a pause, starts the caption on the frame where the voice comes back. Pauses come from the `transcribe` skill's `pauses.py`, with a threshold set from the recording (between its noise floor and its speech level). A fixed -40 dB found none of the pauses in Max video-2, whose AI clips carry room tone.
- Mid-sentence, takes Parakeet's word start plus Parakeet's measured lead on this recording (about 0.08 s), averages it with faster-whisper when the two agree within 0.3 s, and moves it to the end of a real pause just before it, or to the dip just before the voice rises 6 dB (source `dip`). Expect about ±1 frame.
- **Whisper stays on by default.** Tested on Max video-2 hook 1: Parakeet plus the dip matched the waveform on 71 of 74 onsets, but was still 2–5 frames late on about 14 mid-phrase captions, and late captions are what the client complained about. `words --fast` (Parakeet only, about 25 s instead of 80 s) is for drafts.
- Snaps the nearest caption onto every cut within 6 frames, and reports a cut that is more than 2 frames off its voice (the cut is wrong then, not the caption) or has no phrase starting near it.

## Process

1. Quote what the brief or the user says about captions in one line, and the template (default 4, the house look on Max's Aleo videos). FilmCraft may stay open: `words` and `build` save the user's open copy first (through the `filmcraft` skill's bridge), and `build` makes the app reload the project after writing it. If the app is open without its bridge, they stop: ask the user to save and quit, then reopen it from the launcher.
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

Both stay inside the Meta/TikTok safe box (bottom y 1500 on 1080×1920); previews are in `templates/`. A missing font is installed from `fonts/` into `~/.local/share/fonts`.

## Rules

- Work files (`<stem>.vo.wav`, `.pk.json`, `.fw.json`, `.blocks.txt`, `.captions.json`, `.check.png`) go in `video-N/captions/`, never a session scratchpad.
- Never save a project from a headless FilmCraft engine while the app has it open; `build` goes through the bridge for that.
- After `filmcraft-pacing` tighten, run `words`, `plan` and `build` again: the cuts moved every word. When the user moves cuts or changes the voiceover, run `words` (voice changed) or `plan` (cuts changed) and then `build` again; `build` refuses a plan made before the edit changed.
- Never write caption copy the script doesn't have.
