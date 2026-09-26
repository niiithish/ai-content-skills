---
name: video-breakdown
description: >
  Decode a reference video into a remake bible. Gemini 3.1 Pro watches the video
  (the user pastes our prompt into gemini.google.com) and returns a v3 JSON: the
  video's pattern and hook, one scene per hard cut with camera moves, start and
  end states, how the picture builds on the spoken words, overlay captions and a
  timestamped transcript. The agent then checks it against contact sheets of the
  real frames. Use when the user wants a video breakdown, decode, shot list, cut
  list, scene changes, remake bible, "what happens in this video", when a client
  sends a reference or inspiration video with a brief, or on /video-breakdown.
  Triggers: decode this video, detailed breakdown, the cuts, scene changes,
  shot-by-shot, beat-by-beat, analyze this clip/ad/reel, recreate this ad.
---

# Video breakdown (Gemini remake bible + contact sheets)

Most agent models can't take video as input; they only see still frames. Gemini 3.1 Pro watches the whole video with its sound, so it writes the breakdown, and you check it against real frames. `<skill-dir>` is the folder holding this file.

## 1. Get the JSON

If there is no v3 JSON yet, tell the user this, then **stop and wait**. Don't invent a breakdown in the meantime.

1. Open https://gemini.google.com/app and set the model to **Gemini 3.1 Pro** (not Flash).
2. Attach the video.
3. Paste the prompt in [references/gemini-prompt.md](references/gemini-prompt.md) word for word. Give the user the file path, or print it in one `text` block they can copy.
4. Save Gemini's reply as `<video name>.breakdown.json` next to the video, or attach it here.

A JSON is usable only if it has `"schema_version": 3`, a `pattern` object and `scenes` that cover 0.0 to `duration_sec` with no gaps, and every scene has `camera`, `build`, `still` and `timeline`. Anything else (an older schema, missing keys, one-line scenes): name what's missing and ask the user to rerun Gemini with the prompt. A JSON someone saved earlier in `brief/` gets the same check before you rely on it.

## 2. Check it against the frames

Gemini can miss or invent things, and the plan depends on getting the pattern right. Look at the video yourself, cheaply:

```bash
bash "<skill-dir>/scripts/contact-sheets.sh" "/abs/path/to/video.mp4" /tmp/video-breakdown-$$
```

It samples at 2 fps, labels each frame with its time and puts 12 frames (6 s) on each sheet. Stdout gives `OUT=`, `MANIFEST=` and one row per sheet: `sheet_path  start_sec  end_sec  count  label`. Read every sheet in time order: never open the frames one by one, and don't spawn a subagent to look.

Check the JSON's cuts, settings, characters and `build` against the sheets. Where they disagree, trust the frames for what's visible and Gemini for the sound, motion between frames and the words. Pull a full-size frame (`ffmpeg -ss T -i video -frames:v 1 out.jpg`) only when a sheet cell is unclear: product text, a cut you can't place.

If the user doesn't want to use Gemini, write the breakdown from the sheets plus a local transcript (`ffmpeg -i video -ar 16000 -ac 1 -c:a pcm_s16le /tmp/a.wav && voxtype transcribe /tmp/a.wav`), and say it's weaker on motion and timing.

## 3. Write it up

Lead with what a remake needs first:

- **Pattern:** the repeating formula, the hook, why it works, each character's world. This is what planning copies.
- **Form, length, size and premise.**
- **Transcript**, phrase by phrase.
- **Each scene in time order**, as written in the JSON (don't paraphrase or pad): shot, times, purpose; camera (framing, angle, move); set; characters; elements; build; timeline with its words; still; overlay captions (or none).
- **Checked against the frames:** what you confirmed, what you corrected, and anything neither source settles.

Save the write-up as `<video name>.breakdown.md` next to the JSON when the video belongs to a project, so planning reads it instead of redoing it.
