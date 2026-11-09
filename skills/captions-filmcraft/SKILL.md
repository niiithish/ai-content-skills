---
name: captions-filmcraft
description: "Put captions into a FilmCraft project as editable text clips, each one starting on the exact frame its phrase is spoken and on the frame of every picture cut, then export the deliverable from FilmCraft. Caption blocks are whole script phrases of at most 4 words, back to back while the voice runs and cleared in real pauses, and every B-roll or box insert snapped so a new picture only ever appears on a caption start or a V1 cut (`fc_inserts.py`), in templates (4 sentence-case Montserrat, 2 ALL CAPS TikTok Sans, 3 small TikTok-native sentence case, 6 two-line black-on-white rounded boxes). Timing comes from the project's own voiceover track: Parakeet and faster-whisper word times calibrated against the waveform (`--fast` for Parakeet alone). Use when the user edits in FilmCraft and wants captions, subtitles or supers on a .fcproj, wants caption timing fixed in one, or a client complains captions are late, don't change with the picture, or that inserts change mid-caption and look messy."
---

# Captions in FilmCraft

**House style:** for any client edit, load `edit-style` (and its `talking-head-edit` or `voiceover-edit` sub-skill) first. It holds the approved principles and numbers this tool applies.

The user edits and exports in FilmCraft, so captions go into the project as text clips they can see, nudge and export themselves, not burned into a render. Tool: `scripts/fc_captions.py` (needs `filmcraft-cli`, ffmpeg, numpy, `onnx-asr` and `faster-whisper`; it imports the `transcribe` skill's Parakeet helper, so install that skill alongside, and the fonts come from the `captions` skill's `fonts/`).

## The rules (a client's review, now the standard for every video)

1. **Picture, caption and voice change on the same frame.** Every cut on V1 starts a caption, and every caption starts on the frame its first word is heard: never a few frames late, never before the cut.
2. **Blocks are whole script phrases, at most 4 words.** Three words when that reads well, four only where the phrase needs it ("dimples that barely show," / "even in bathroom light.", not "dimples that barely" / "show, even"). Never split a name, a number and its unit, or "65% off".
3. **Back to back while the voice runs, gone in silence.** Each caption stays up until the next starts, unless the voice pauses for 0.4 s or more first: then it ends 2 frames after the voice stops. The last ends 2 frames after the last word. A caption is never shorter than half a second. `--hide 0` puts them back to back everywhere.
4. **A new picture appears only on a caption start or a V1 cut.** Every B-roll clip, box still or full-screen insert starts and ends on the frame a caption starts or the main video cuts, never mid-caption, and no picture shows for under 8 frames. The Aleo video-3 client: "every time a new image comes to the screen its either when a new text starts or when the cut is happening of the main video. If you dont do this, it looks super messy" and called the misses "very rookie mistakes". Inserts placed on word times alone (start on the words they show) still landed 3–20 frames inside a caption on about a third of the changes.

## Why the timing works this way

A single ASR engine alone was 0.16 s (4 frames) late on part of a voiceover, and the client saw it. Engines disagree by a few frames, and each one drifts. So `plan`:
- After a pause, starts the caption on the frame where the voice comes back. Pauses come from the `transcribe` skill's `pauses.py`, with a threshold set from the recording (between its noise floor and its speech level). A fixed -40 dB found none of the pauses in Max video-2, whose AI clips carry room tone.
- Mid-sentence, takes Parakeet's word start plus Parakeet's measured lead on this recording (about 0.08 s), averages it with faster-whisper when the two agree within 0.3 s, and moves it to the end of a real pause just before it, or to the dip just before the voice rises 6 dB (source `dip`). Expect about ±1 frame.
- **Whisper stays on by default.** Rechecked 2026-11-07 on the one-word test: without it 6 of 27 captions moved 3–7 frames off the waveform and ONE started in the silence before its voice. Neither engine alone is more accurate (see the transcribe skill's model test), but they miss in different directions, so the average is closer. Tested on Max video-2 hook 1: Parakeet plus the dip matched the waveform on 71 of 74 onsets, but was still 2–5 frames late on about 14 mid-phrase captions, and late captions are what the client complained about. `words --fast` (Parakeet only, about 25 s instead of 80 s) is for drafts.
- With one- and two-word captions (templates 5 and 7) words are ~7 frames apart: the dip search never goes back past the previous word's start, and a start that lands in the silence after a word falls back to Parakeet's own start. Before this (2026-11-07 test), captions doubled up on one frame and got spread up to 9 frames late. On that synthetic voice the 0.08–0.12 s lead made some mid-phrase starts ~3 frames late; it was measured on real voices, so recheck it on the next real one-word edit.
- **Pop captions lead the voice by 3 frames** (`plan --early`, on by default with `--max-words 3` or fewer, i.e. templates 5 and 7; 0 for phrase captions). Placed exactly on the voice, one-word captions read as late next to a version that leads (user, 2026-11-07). The lead is for mid-phrase starts only (`dip`, `words`, `spread`): a caption after a pause (`onset`, `pause`) or on a cut stays exactly on the voice, else it shows in the silence before the word (user's waveform review, same day). A caption that ends in a pause clears 2 frames after the voice even when that makes it shorter than half a second, rather than staying over the silence. The lead never leaves the caption before it under 5 frames (a 2-frame "AND" flashed).
- **A sentence's last word: Parakeet is often 5–10 frames late** ("trick." 0.17 s, "time." 0.3 s on the 2026-11-07 test), so the lead put the start on the word's final consonant (after a 2-frame stop closure, which is not a pause) or in the silence after it. A start with under 5 frames of voice left before a real pause (0.15 s or more) is redone from the waveform: the last 10–30 ms near-silence (a stop closure or word gap, on 10 ms steps; 33 ms frames blur it) up to 0.4 s before Parakeet's start, never before the caption before (source `back-dip`). The user marked TRICK's start on the waveform and it matched to the frame.
- **Checks every caption against the waveform and fixes the clear misses** (`audit` in `plan`, 2026-11-07), the three a user has caught: a start over the silence before its voice (moved onto the voice; out of a pause no lead is allowed), a start after the voice came back from a pause or on its word's last consonant (moved onto the voice, or reported), a caption up over a pause of `--hide` or more (ended 2 frames after the voice). It prints `waveform check fixed:` for each change and a `NOTE` for anything left (`maybe late`: look at it). Captions placed by hand (`pinned`), on a cut, or at frame 0 are left alone. Tested: it found and fixed all 5 misses on the one-word test (the result matched the hand-tuned plan frame for frame), 0 false alarms on the fixed plan, and on Calvin video-19 (112 phrase captions, real voice) fixed 5 that were 2–6 frames off and left 1 note.
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
6. Inserts (rule 4), whenever the project has B-roll or insert tracks between V1 and the captions, after every caption build and every insert change:

   ```bash
   <skill-dir>/scripts/fc_inserts.py split PROJECT     # split captions where an insert changes mid-caption, at the nearest word
   <skill-dir>/scripts/fc_captions.py plan PROJECT ... && <skill-dir>/scripts/fc_captions.py build PROJECT -t N
   <skill-dir>/scripts/fc_inserts.py snap PROJECT      # every insert edge onto the nearest caption start or V1 cut
   <skill-dir>/scripts/fc_inserts.py check PROJECT --render
   ```

   Split first, or snap has to move a picture up to 2–3 s off its words to reach a caption start. `split` prefers a comma, full stop or the line break, never leaves "the", "your" or "of" at the end of a half, and keeps the old blocks as `<stem>.blocks.pre-split.txt`. `snap` only trims and moves (motion keyframes stay), never lets two pictures share a mark or a movie play past its media, backs up to `edit/backup-<date>-snap/`, and lists any insert left under 8 frames (split a caption there or drop it). `check` must end with 0 mid-caption, 0 short, 0 near misses and, with `--render`, 0 frames not switching: never export before it does. Rerun anything that repositions captions afterwards (a build resets hand-moved caption positions).
7. Export only when the user says so: `fc_captions.py export PROJECT -o video-N/deliverables/<Brand>_<Concept>_<Variant>_<Ratio>.mp4` (the `filmcraft` skill's Meta settings: H.264 high, 6 Mb/s VBR 1-pass, AAC 192k, about 45 MB a minute; written to `.tmp.mp4` and renamed when done). Don't also burn captions with the `captions` skill: they are already in the picture.

## Templates

| # | Look |
|---|---|
| 4 | Sentence-case white Montserrat ExtraBold 68, 3 px black outline, soft shadow (blur 7, 4 px down, 75%), centred, baseline y 1420 |
| 2 | Same, ALL CAPS TikTok Sans ExtraBold 68 |
| 3 | TikTok's own caption look: sentence-case white TikTok Sans SemiBold 64, 2 px black outline, soft dark glow (blur 9, no offset, 90%), centred, baseline y 1408. Matched to a TikTok reference frame at 50, raised to 64 for a 45+ audience |
| 5 | Storybook explainer: white TikTok Sans SemiBold 50, thin outline, 1–2 words, baseline y 1116 (`plan --max-words 2`) |
| 7 | Word-by-word podcast clip (Aleo video-4 reference): ALL CAPS white Montserrat ExtraBold 85, 3 px black outline, hard black shadow down-right (6 px, no blur), no punctuation, baseline y 1306, the same spot on every shot. One word a caption, two when a short word leads ("OR YOUR", "THE BODY"); write `blocks.txt` by hand that way and merge any block under 5 frames into its neighbour, then `plan --max-words 3` |
| 6 | Doctor explainer (Aleo video-3 reference): sentence-case black TikTok Sans SemiBold 58 on a tight white rounded box behind each line, drawn as a shape layer sized to the line's measured width (17 px side and 7 px top/bottom padding, radius 16, measured on the reference; the two boxes meet behind the text). FilmCraft's own text background was too big and left a wide gap, which the user rejected, two lines with baselines y 1098 and 1173, leaving a small gap above a box insert (box top about y 1225). Blocks are up to 7 words (`plan --max-words 7`); ` / ` in `blocks.txt` marks the line break, else `build` splits at the most even break. Each caption is one text clip with a text layer and a box layer per line. `build --one-line` keeps every caption on one line; write blocks of about 2–4 words, at most 24 characters (a 30+ character line read as too wide, Aleo video-5 user 2026-10-29) |

All stay inside the Meta/TikTok safe box (bottom y 1500 on 1080×1920); previews are in `templates/`. A missing font is installed from `fonts/` into `~/.local/share/fonts`.

## Rules

- Work files (`<stem>.vo.wav`, `.pk.json`, `.fw.json`, `.blocks.txt`, `.captions.json`, `.check.png`) go in `video-N/captions/`, never a session scratchpad.
- Never save a project from a headless FilmCraft engine while the app has it open; `build` goes through the bridge for that.
- After `filmcraft-pacing` tighten, run `words`, `plan` and `build` again: the cuts moved every word. When the user moves cuts or changes the voiceover, run `words` (voice changed) or `plan` (cuts changed) and then `build` again; `build` refuses a plan made before the edit changed.
- Never write caption copy the script doesn't have.
- Never place an insert by eye or by word time alone: it goes on a caption start or a cut (rule 4), and `fc_inserts.py check` passes before every export.
