---
name: video-breakdown
description: >
  Decode a reference video into a remake bible. Gemini 3.1 Pro watches the video
  (the agent runs gemini.google.com in its built-in browser when it has one, or
  the user pastes our prompt there) and returns a v3 JSON: the
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

## 0. Prep (always, before or while Gemini runs)

Gemini's JSON alone is too coarse: on one 80 s ad it gave 8 "scenes" for ~40 real cuts, the wrong resolution and `[cite]` junk. So always build the ground truth first, in one command (about 15 s for 80 s of video):

```bash
bash "<skill-dir>/scripts/prep.sh" /abs/path/to/reference.mp4
```

It writes next to the video: the word-timed transcript (`.txt`, `.words.json`, `.srt`, via the `transcribe` skill), `cuts.txt` (hard cuts, scene score > 0.3), 2 fps contact sheets in `sheets/`, and `specs.txt` (size, fps, length, words, wpm, shot count). Keep the files with the project, not in a scratchpad.

## 1. Get the JSON

If there is no v3 JSON yet, get one from Gemini. Don't invent a breakdown in the meantime.

**With a built-in browser** (Claude or ChatGPT app browser tools; the user is signed in to Google there), run Gemini yourself:

1. Open https://gemini.google.com/app in the browser pane. If it asks for sign-in, stop and ask the user to sign in there. Never type credentials yourself.
2. Open the mode picker and choose **Pro** (Gemini 3.1 Pro). Never run it on Flash.
3. Attach the video:
   - a YouTube link: put the link on the first line of the message;
   - a local file: the browser tools can't pick files from disk. Ask for this one step: "Drag `<abs path>` into the Gemini box in the browser pane." Wait until the video chip shows in the input box.
4. Put the full text of [references/gemini-prompt.md](references/gemini-prompt.md) in the input box, word for word, with a `type` action (read the file first), and send it.
5. Wait for the reply to finish (the stop button goes away; long videos take a few minutes), then read it with `get_page_text` or the reply's copy button. Save the JSON object as `<video name>.breakdown.json` next to the video.
6. If Gemini refuses, cuts off or returns something other than one JSON object, send "Return the complete JSON object only." once in the same chat. If that fails too, fall back to the steps below.

**Without a browser**, hand it to the user, then **stop and wait**:

1. Open https://gemini.google.com/app and set the model to **Gemini 3.1 Pro** (not Flash).
2. Attach the video.
3. Paste the prompt in [references/gemini-prompt.md](references/gemini-prompt.md) word for word. Give the user the file path, or print it in one `text` block they can copy.
4. Save Gemini's reply as `<video name>.breakdown.json` next to the video, or attach it here.

A JSON is usable only if it has `"schema_version": 3`, a `pattern` object and `scenes` that cover 0.0 to `duration_sec` with no gaps, and every scene has `camera`, `build`, `still` and `timeline`. Anything else (an older schema, missing keys, one-line scenes): name what's missing and rerun Gemini with the prompt (yourself when you have a browser, otherwise ask the user). A JSON someone saved earlier in `brief/` gets the same check before you rely on it.

## 2. Check it against the frames

Gemini can miss or invent things, and the plan depends on getting the pattern right. Look at the video yourself, cheaply:

```bash
bash "<skill-dir>/scripts/contact-sheets.sh" "/abs/path/to/video.mp4" /tmp/video-breakdown-$$
```

It samples at 2 fps, labels each frame with its time and puts 12 frames (6 s) on each sheet. Stdout gives `OUT=`, `MANIFEST=` and one row per sheet: `sheet_path  start_sec  end_sec  count  label`. Read every sheet in time order: never open the frames one by one, and don't spawn a subagent to look.

(`prep.sh` already made them in `sheets/`.) Check the JSON's cuts, settings, characters and `build` against the sheets and `cuts.txt`: the shot list needs one row per real cut, not per Gemini scene. Where they disagree, trust the frames for what's visible and Gemini for the sound, motion between frames and the words. Pull a full-size frame (`ffmpeg -ss T -i video -frames:v 1 out.jpg`) only when a sheet cell is unclear: product text, a cut you can't place.

If the user doesn't want to use Gemini, write the breakdown from the prep files alone, and say it's weaker on motion between frames.

## 3. Write it up

Save it as `<video name>.breakdown.md` next to the video, in this order (the user approved this layout on Mysa video-9):

1. **Specs** table: size, fps, length, words and wpm, shot count and average shot, look, audio (VO, music, SFX), captions in one line. From `specs.txt`, corrected by eye.
2. **Pattern:** the formula, the timeline engine (what moves the story forward), mirrored beats, the visual euphemism system (how it shows what it can't show), the hook, why it works. This is what planning copies.
3. **Style bible + recurring cast:** medium/look, light, palette, each character's look and world.
4. **Captions:** font family and weight, case, colour, outline/shadow/box, words per page, position (y as % of height), word highlight, titles or labels. Then name the **nearest captions template** (`captions` skill: 1 boxed two-line, 2 bold caps one-liner, 3 karaoke one-liner with a hook title, 4 sentence-case one-liner) and what differs, so the edit can say "template-3" instead of describing it.
5. **Transcript**, word-timed (from the `.srt`).
6. **Shot list, one row per cut** from `cuts.txt` and the sheets: `# | time | shot | camera | build | VO words`. Whip pans and dissolves get their own rows.
7. **Checked against the frames:** what you confirmed, what you corrected in Gemini's JSON, and anything neither source settles.

## 4. When the user wants a remake

- Write our voiceover to the same formula and length: word count within ~5% of the reference.
- Map every reference beat to ours in a table (reference time and words → our line → our shot).
- Cite where each product claim comes from (brief, product page); never invent numbers.
- Split-screen shots are never generated as one split frame: plan each side as its own still and clip (subject centred, action inside the middle half of the width) and build the split, seam and labels in the edit.
- A known toy or brand look is fine to match, but describe it generically in prompts ("glossy plastic toy-brick minifigure") and use original characters and invented competitor brands.
