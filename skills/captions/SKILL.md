---
name: captions
description: Burn captions and section labels into a finished 9:16 edit in one locked style (TikTok Sans SemiBold, black on a merged white box at the bottom of the Meta/TikTok safe area, red label boxes at the top). The wording comes from the voiceover script and the timing from faster-whisper word timestamps. It shows one preview frame before any render and writes <Brand>_<Concept>_<Variant>_<Ratio>.mp4 deliverables. Use when the user asks for captions, subtitles or supers on their edit, or on any video they've cut. Not for captions inside generated stills or clips (those never carry text).
---

# Captions

The user edits the video; we burn captions into their finished edit. The style below took seven rounds with the user to lock (Mysa video 3). Use it as is, and change it only when the user asks.

Tool: `scripts/captions.py` (Python 3 with Pillow and faster-whisper, plus ffmpeg), with the font bundled in `fonts/` (TikTok Sans, OFL).

## Locked style

Layout on a 1080×1920 canvas, scaled to the edit. The Meta/TikTok caption safe box is x 40–1050, y 220–1500.

- **Captions:**
  - `#111` text, TikTok Sans SemiBold 54 px, on white;
  - the block's bottom edge at y 1480, the bottom of the safe box (never the centre of the frame);
  - at most 2 lines, and nearly every caption is 2 full lines (about 36 characters, 50 at most, breaking at commas where possible, with no short orphans);
  - curly quotes and apostrophes.
- **The box:** one merged shape around all lines (never a box per line, which leaves a notch), with rounded outer corners (R 18) and rounded fillets where lines of different widths step. Line pitch is 74 px (about 1.95× cap height), and each line is centred on its cap height, so the space above the capitals equals the space below the baseline.
- **Section labels** (HOURS, DAYS 4–6, WEEK 3…): the same box shape at the top (y 245), white text on `#EA4040`, on screen for 3 s from the start of their line. Never a big centred super or a white box.
- **Words** come from the voiceover script, not from whisper: whisper only times them. The audio is copied untouched.

## Process

1. Find what the brief says about captions and quote it to the user in one line. Get the edit (the user's file, e.g. `video-N/my-edits/hook-1.mp4`) and the script text as voiced in that edit (the hook variant plus the body). Save it as a text file in `video-N/captions/`.
2. Time the words (a few minutes a file on CPU):

   ```bash
   <skill-dir>/scripts/captions.py words video-N/my-edits/hook-1.mp4
   ```

3. Plan the captions. `labels.txt` holds one `LABEL | first words of its line` per line:

   ```bash
   <skill-dir>/scripts/captions.py plan video-N/my-edits/hook-1.mp4 --script video-N/captions/hook-1.txt --labels video-N/captions/labels.txt
   ```

   It prints every caption with its times, and how many script words whisper didn't hear. Read it: breaks in the right places, nothing missing. If many words weren't heard, the script doesn't match the edit; ask for the right one.
4. **Preview first.** `captions.py preview EDIT` composites one real frame with a caption and a label (or `--at 12.5` for a chosen moment) into `captions/<stem>.preview.png`. Show it to the user, and render nothing until they say yes.
5. Render each edit into `video-N/deliverables/`, named `<Brand>_<Concept>_<Variant>_<Ratio>.mp4`:

   ```bash
   <skill-dir>/scripts/captions.py render video-N/my-edits/hook-1.mp4 -o video-N/deliverables/Mysa_Dose-to-Done_Hook1-Control_9x16.mp4
   ```

   It writes `<name>.tmp.mp4` and renames it only when ffmpeg finishes, so a stopped render never leaves a broken deliverable. Run several edits in the background, one render each.
6. Check one frame of each deliverable at a caption with a label, then report the files in a line each.

## Rules

- All work files (`<stem>.words.json`, `<stem>.plan.json`, frames, preview) go in `video-N/captions/`, which the tool finds from the `PLAN.md` above the edit. Never keep them in a session scratchpad: it is wiped between sessions.
- If the user wants a style change, change it in the plan or with the tool's constants for that project only. Add it to the project's `AGENTS.md` Decisions, and here only if the user says it's the new default.
- Never write new caption copy or full subtitles the brief didn't ask for.
