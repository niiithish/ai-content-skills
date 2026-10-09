---
name: captions
description: "Burn captions into finished 9:16 edits in a named template the user picks by number (\"use template-3\"): 1 boxed two-line (TikTok Sans on a white box), 2 bold ALL CAPS one-liner, 3 karaoke one-liner with the spoken word in lime plus an optional red hook title, 4 sentence-case Montserrat one-liner. All stay inside the Meta/TikTok safe box. Words come from the voiceover script (or the transcript with number/brand fixes), timing from ElevenLabs Scribe word timestamps (the transcribe skill). Shows preview frames before any render, renders one edit at a time on the Intel GPU (Quick Sync / VA-API, x264 fallback) and writes <Brand>_<Concept>_<Variant>_<Ratio>.mp4 deliverables. Use when the user asks for captions, subtitles, supers or a hook title on their edit. Not for captions inside generated stills or clips (those never carry text)."
---

# Captions

The user edits the video; we burn captions into their finished edit (usually Resolve exports in `video-N/deliverables/raw*/`). Tool: `scripts/captions.py` (Python 3 with Pillow, plus ffmpeg). Word times come from the `transcribe` skill's helper, so install it alongside. Fonts are bundled in `fonts/` (TikTok Sans and Montserrat, both OFL).

## Templates

The user names one ("template-3"); don't ask them to describe the style again. If they name none, ask which, showing `templates/all.png`. Each was locked with the user on a real Mysa ad.

| # | From | Look | Words per caption |
|---|---|---|---|
| 1 | video-3 | `#111` TikTok Sans SemiBold 54 on one merged white box with rounded corners and filleted steps; block bottom y 1480. Red `#EA4040` section labels at y 245 for 3 s. | 2 lines, ~36 chars (50 max), breaks at commas |
| 2 | video-6 | ALL CAPS white TikTok Sans ExtraBold 68, 3 px black outline, soft shadow (blur 7, dy 4); baseline y 1420; punctuation kept. | 1 line, ≤3 words, ~13 chars |
| 3 | video-10 | ALL CAPS white Montserrat ExtraBold, 6 px black outline, hard 50% shadow; **the word being spoken turns lime `#C8FF00`**; centre y 1440; no punctuation. Usually with a hook title (below). | 1 line, ≤3 words, ≤18 chars |
| 4 | video-7 | Sentence-case white Montserrat ExtraBold 68, 3 px outline, soft shadow; baseline y 1420; punctuation kept. | 1 line, ≤3 words, ~13 chars |

Samples: `templates/template-N.png` (the red frame is the safe box). `captions.py templates` prints the list.

Every template keeps text inside the **Meta/TikTok caption safe box, x 40–1050, y 220–1500** on 1080×1920: lines are capped at 900 px, and a single word wider than that is shrunk, never allowed past the edge.

**Options on any template:**
- `--title "How lube ruined my marriage!!"`: a hook title, white Montserrat ExtraBold 50 on a red `#E81C24` rounded box, centred on y 960 (the seam of a split-screen hook; `--title-y` to move it), from 0 s until the first sentence is said (+0.3 s; `--title-until` to set it). Use the same title on every hook unless told otherwise.
- `--labels labels.txt`: section labels (template 1's red boxes), one `LABEL | first words of its line` per line.
- A project-only variant: a JSON file `{"base": "2", "size": 60, "highlight": [255, 220, 0]}` passed as `-t file.json`. Keys: `font`, `size`, `caps`, `punct`, `stroke`, `shadow` `[dx, dy, blur, alpha]`, `y`, `anchor` (`ms` baseline, `mm` centre), `maxwords`, `target`, `maxchars`, `highlight` `[r, g, b]` or null. Record it in the project's `AGENTS.md`; add it here as template 5+ only when the user says so.

## Process

1. Quote what the brief or the user says about captions in one line, and the template number. Get the edits.
2. Word times, one per edit (seconds with ElevenLabs):

   ```bash
   <skill-dir>/scripts/captions.py words video-N/deliverables/raw/hook-1.mov
   ```

3. Plan. Words on screen come from the voiceover script when you have the one voiced in this edit (`--script`, one line per row); otherwise from the transcript, with spoken forms fixed by `scripts/fixes.txt` (numbers: "fifty-six" → 56, "nineteen ninety-nine" → $19.99) plus a project file for brand spellings (Scribe hears "Mysa" as "Maesa"/"Maisa"):

   ```bash
   printf 'maesa | Mysa\nmaisa | Mysa\n' > video-N/captions/fixes.txt
   <skill-dir>/scripts/captions.py plan EDIT -t 3 --fixes video-N/captions/fixes.txt --title "How lube ruined my marriage!!"
   ```

   It prints every caption with its times. Read it: brand and numbers right, breaks in sensible places, and with `--script`, few words "not heard" (many means the script doesn't match the edit).
4. **Preview first.** `captions.py preview EDIT` writes `captions/<stem>.preview.png`: real frames side by side, one with the title or a label and one mid-video (`--at 1.2 40.5` to choose). Send it to the user and render nothing until they say yes.
5. Render all edits in **one** command; they go one at a time (each encode already fills the GPU, so parallel runs only slow every one down):

   ```bash
   <skill-dir>/scripts/captions.py render raw/hook-1.mov raw/hook-2.mov raw/hook-3.mov \
     -o deliverables/Mysa_Lube-Myth_Hook1_9x16.mp4 deliverables/Mysa_Lube-Myth_Hook2_9x16.mp4 deliverables/Mysa_Lube-Myth_Hook3_9x16.mp4
   ```

   Run it in the background and report each file as it lands. Encoder order: Intel Quick Sync (`h264_qsv -global_quality 20`), then VA-API, then x264 veryfast; on the user's Iris Xe a 4-minute 1080×1920 hook takes about 1.5 min. Video length is the source's video stream, audio is copied if AAC, else encoded to AAC 192k (Resolve's PCM can't go in an mp4). Each file is written as `<name>.tmp.mp4` and renamed when done, so a stopped render never leaves a broken deliverable.
6. Check one frame of each deliverable and that video and audio durations match, then report the files in a line each.

## Rules

- All work files (`<stem>.words.json`, `<stem>.plan.json`, overlay frames, previews) go in `video-N/captions/` (found from the nearest `PLAN.md`, `AGENTS.md` or `project.conf` above the edit). Never keep them in a session scratchpad: it is wiped between sessions.
- A style change for one project goes in a template JSON there and its `AGENTS.md` Decisions, not in this skill, unless the user says it's the new default.
- Never write new caption copy or full subtitles the brief didn't ask for.
