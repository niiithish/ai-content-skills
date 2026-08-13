---
name: video-breakdown
description: >
  Break down a local video into shots, cuts, scene changes, on-screen actions,
  and spoken lines using cheap 2fps contact sheets plus offline transcription.
  Use when the user wants a detailed video breakdown, shot list, cut list,
  scene changes, what someone is doing or saying, "what happens in this video",
  or runs /video-breakdown. Triggers: "detailed breakdown of the video",
  "her actions", "the cuts", "scene changes", "what she is saying", shot-by-shot,
  beat-by-beat, analyze this clip/ad/reel.
---

# Video breakdown (contact sheets + transcript)

Default method for any local video the user wants broken down. Optimize for **cost and speed**, not frame-by-frame viewing.

Do **not** open every extracted still one by one. Do **not** stitch the whole video into a single packed grid. Do **not** spawn a subagent just to look at a sheet.

Needs `ffmpeg`, `magick` (ImageMagick), and `python3`. Speech needs `voxtype` (or the **voxtype-transcribe** skill).

## Pipeline (run in parallel)

1. Confirm the file exists. `ffprobe` duration, fps, size, and whether there is an audio stream.
2. **At the same time:**
   - Build contact sheets with the script below.
   - Transcribe if there is audio. Do not use cloud STT unless the user asks.
3. Read **every contact sheet** (each sheet is one image). Then write the breakdown.
4. Pull a full-size still only when a sheet cell is ambiguous (wardrobe change, product text, a cut you cannot place). Usually 0–2 extra frames.

## Contact sheets

`<skill-dir>` is the folder that contains this `SKILL.md`. Run:

```bash
bash "<skill-dir>/scripts/contact-sheets.sh" "/abs/path/to/video.mp4" /tmp/video-breakdown-$$
```

Do not hardcode `~/.grok/skills`. Resolve the script from this skill's directory.

It samples at **2 fps**, labels each still with a timestamp, and stitches **12 stills (6 seconds) per image**, 4 across. Stdout includes `OUT=`, `MANIFEST=`, and a TSV: `sheet_path  start_sec  end_sec  count  label`.

- Short-form / ads / Reels / product clips: keep 2 fps and 6s chunks (the script default).
- Longer than ~3 minutes: still use the script. Read sheets in time order. Summarize repeating beats instead of narrating every half-second.

Read the sheets yourself, in order. Each sheet is the context for that 6-second window.

## What to extract from a sheet

- Hard cuts (wardrobe, location, bag/product state, camera jump).
- Continuous action vs a new shot.
- Hands, props, on-screen text you can actually read.
- Order: left → right, top → bottom, then the next sheet.

Do not invent motion that is not on the sheet. If a zip or set-down happens *between* cells, say the gap, do not describe the missing frames.

## Transcript

If **voxtype-transcribe** is installed, follow it.

Otherwise convert to 16 kHz mono WAV and run `voxtype transcribe` (it rejects any other format):

```bash
INPUT="/abs/path/to/video.mp4"
WAV="/tmp/voxtype-$(basename "${INPUT%.*}").wav"
ffmpeg -y -i "$INPUT" -acodec pcm_s16le -ar 16000 -ac 1 "$WAV"
voxtype transcribe "$WAV"
rm -f "$WAV"
```

Align lines to shots using the sheet timestamps and mouth/action changes — not by splitting audio unless a line is clearly wrong.

Proper names and product words may be wrong. Correct only when the picture makes it obvious (logo, packing into two wells, etc.) and note the correction.

No audio stream, or no `voxtype`: skip transcription and say so.

## Write-up

Lead with duration, format (e.g. vertical 1080×1920), and a one-line premise.

Then a **cut list** (shot number, timecode, length, what changed).

Then **shot-by-shot**:

- Time range
- Location / wardrobe if it changed
- What the person does (hands, face, product)
- What they say in that range, quoted

End with anything the sheets plus transcript cannot settle.

Do not dump the contact-sheet files on the user unless they ask. `/tmp` is fine.
