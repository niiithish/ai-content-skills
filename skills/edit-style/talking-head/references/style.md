# House style: the numbers

Every value here was set by the client or the user, and was approved in video-5 (2026-11-02) and DCT-2190 (2026-11-03). Use these values unless the video's `AGENTS.md` says otherwise. Units: 24 fps, 1080×1920; a frame is 10584000000 ticks; a second is 254016000000 ticks.

## Speaker track (V1/A1)

| What | Value | Where it came from |
|---|---|---|
| Speed | 1.1x (video-5), 1.12x (DCT-2190), `setpts=PTS/S, atempo=S` | user |
| Join, voice to voice | about 0.25 s; hook into body about 0.37 s | Loom 2/3: "no gap at all" at 0.2 s |
| Pause inside a line | 0.35 s or more is cut to about 0.2 s | "too much blank sound" |
| Hook opening | under 0.3 s of silence before the first word | user |
| Loudness | each talking source normalised to −16 LUFS, then A1 clip gain −4.9 dB, so the master lands at −21.1 LUFS. A swapped clip must match this. | user (voices ranged −21.6 to −30.9) |
| Shot she is seen in | she finishes the word before an insert covers her | Loom 11: "she doesn't even completely say it and she's already gone" |

Every clip join in a joined master is a jump cut, even when it is not a V1 cut. Cut V1 at every join, or find the joins as the join time ÷ speed. Each jump must sit under an insert or on a caption start.

## Pictures (V2 inserts)

- **Full screen**, scaled to fill 1080×1920. One about every 2–4 s; her face shows about a quarter of the time. In DCT-2190 there were about 40 per 90 s hook.
- **Start** on a caption start or a V1 cut, at the first frame of the words the picture shows. Never start mid-caption, and never show a picture for under 8 frames.
- **Hold** until the next picture or the next talking shot. Never leave a gap of her face for 1–3 frames (a flash).
- **No repeats** inside a hook.
- **Stills push** with motion scale from the first frame to the last at one rate: **2 % of the start scale per second** (Loom 11). A 2 s still goes 100 → 104%. The push never stops early (Loom 8), never starts late (Loom 11: "static, then 0.1 s, then it starts zooming"), and is always centred. See `loom11_fixes.py` step 2.
- **Clips** play at 100% speed unless the user asks (DCT-2190 squats ran at 150%). A clip with no motion can get an edit-made slow zoom or pan when the user asks (scene-207: a still with a zoom and a pan to the right).
- **Video stays video.** A clip is never swapped for a still.

## Talking-shot motion (V1 scale, `talk_motion.py`)

- Each stretch of her face opens at 100%, with a slow centred push of +3% per 3 s. There is never a punch on the frame an insert cuts back to her (Loom 7).
- Inside a stretch, the scale steps hard 100% ↔ 110% at each V1 cut. In runs longer than 60 frames it also steps on a caption start, at most every 36 frames, and never within 18 frames of the stretch's edges. Every segment keeps pushing.
- No position keyframes: no sideways drift (Loom 7 read it as "a jump cut to the top left").
- The script reruns safely (it deletes V1 scale keyframes first). Rerun it after any V1 or insert change.

## Captions (`captions-filmcraft` template 6)

| What | Value |
|---|---|
| Look | TikTok Sans SemiBold 58, black text, white rounded box |
| Lines | one line, `build -t 6 --one-line` |
| Length | video-5: 2–4 words, at most 24 characters. DCT-2190: a whole clause, 3–5 words, up to about 32 characters, no end punctuation. Follow the reference ad. |
| Position | every body caption box centred at **y 1360** (71% down, Loom 10). This is a motion position: `caption_layout.py` sets it after every build, because a build resets it. |
| Timing | starts on its first word. It may lead the voice by up to 3 frames, never more (Loom 11: "money-back guarantee" came up 14 frames early). Back to back while she talks; cleared in a real pause. |
| Words | verbatim from the brief; numbers as digits ("57", "40%", "60-day"). |
| Insert changes | a new caption starts on every picture change; split a block where a picture changes. |

The hook title is two lines, up top, never over her face:

- video-5: box centre about y 655, just under her chin.
- DCT-2190: scaled to 85%, box centre y 422, the reference's measured centre.

Always check the hook's first frame by eye.

## Audio

| Track | What |
|---|---|
| A1 | her voice |
| A2 | music: `assets/music/Frank Ocean - Pink + White(instrumental) [N9GXZD8y-bg].m4a`, from its start. Gain −27 dB (video-5, voice −22.2 LUFS) or −26 dB (DCT-2190, voice −21.1 LUFS), keeping the music about 18 dB under the voice. 1 s fade out at the end of the hook (`add_music.py`, safe to rerun). |
| A3 | sound effects, such as the click on each word of the DCT-2190 card (`edit-style/assets/switch-click-02.mp3`) |

## Overlays (above the captions)

- 🤯: `edit-style/assets/exploding-head-iphone.png` at scale 12, one space after the title's last word, inside its box. FilmCraft can't draw colour emoji.
- CTA arrows: `edit-style/assets/cta-arrows-red.png`, two red arrows bobbing as in the reference, over the CTA line (DCT-2190).

## Export

- `python3 ~/.claude/skills/filmcraft/scripts/fc.py export edit/hook-N.fcproj -o deliverables/<Brand>_<Short>_HookN_9x16.mp4`
- Run it in the background, one hook after another. Before exporting, move old exports to `deliverables/pre-<what>/`.
- Output: 1080×1920, 24 fps, H.264 + AAC, about 45 MB a minute (about 69 MB for 90 s).
- Afterwards, check each file with `ffprobe` (duration matches the timeline, has an audio stream) and look at a frame or two.
