---
name: ugc-ad-remake
description: Run a still-first talking-head remake of a winning TikTok/Reels UGC ad with a new product and talent. Use when the user wants to clone, copy, remake, or recreate a winning ad, start a new UGC project from a reference video, swap a different model/product into an existing talking-head structure, write Gemini Omni 720p "she says" clips, or continue a product-swap still + locked-frame clip workflow. Trigger on clone this ad, remake this TikTok, copy this UGC, different model different product, talking-head review, Gemini Omni, yappy, silent hold, product swap, same frame, zip-hold, or name the clips. Do not use for silent cinematic b-roll, claymation, three-panel character sheets, multi-view prop sheets, environment plates, or writing a brand-new silent voiceover script from scratch.
---

# UGC Ad Remake

Remake a winning talking-head UGC ad with a **new talent** and **new product**, keeping the original's structure, camera grammar, and spoken cadence.

Write **prompt text only**. Put the finished prompt in a code block and stop. Do not generate images/video unless the user asks. Do not dump a whole production package on "note the goal" or "don't do anything."

This skill overrides **script-generation** and **video-generation** for talking-head remakes: on-camera speech is allowed, the camera stays locked to the still, and the room does not change every cut.

## Working style

- Short. Prompt-only. One next step.
- Still first, then the clip. Never write a talking clip before an approved still exists.
- User uploads images as **identity refs**, not start frames, unless they say start-frame.
- Match the winning ad's *structure* (beats, angles, hand jobs, zip/open/hold). Change talent, product, colorway, brand, and nouns that the new still cannot support.
- Fast yappy UGC. Line once, then silent hold. Never time the line to fill 4s/6s.
- Default engine: **Gemini Omni, 720p, 9:16, 24fps**. 4s or 6s only.

## Session start

If they only name the goal, note it and wait.

When work starts, use or create a project folder:

```text
product-images/     listing stills + SOURCE.txt
images/             approved 9:16 stills + README.txt
clips/              clip-01-slug.mp4 + CLIP_INDEX.txt
scripts/            working spoken script
final/              stitched export later
```

Read those files before inventing a second woman, color, logo, or room.

If they give a winning ad (video, screenshots, or transcript):

1. Break it into spoken beats + camera/hand jobs. Load [references/beat-map.md](references/beat-map.md).
2. Lock talent + product. Character/prop sheets via those skills when asked.
3. Pull only the chosen listing variant into `product-images/`.
4. Rebuild stills one by one from winning-ad screenshots + our product.
5. Write one Omni clip per approved still.
6. Transcribe and rename when they say the pass is done.

## Route

| They ask | Do |
|---|---|
| Character / smile sheet | **character-generation** |
| Product turnaround | **prop-generation** |
| Room plate | **environment-generation** |
| Listing images | Download chosen variant only |
| New still / product swap | Load [references/still-prompts.md](references/still-prompts.md) |
| "she says" / Omni clip | Still first, then [references/clip-prompts.md](references/clip-prompts.md) |
| Last still/clip is wrong | Patch one lock. [references/failure-locks.md](references/failure-locks.md) |
| Transcribe / name clips | **voxtype-transcribe** → `clip-01-slug.mp4` + `CLIP_INDEX.txt` |

## Split attached images

| Source | Keep |
|---|---|
| Winning-ad / pose still | Person, face, expression, pose, **hand contact points**, crop, camera height, lighting, room, table, wardrobe |
| Our product / prop sheet | Silhouette, color, material, openings, logo text + metal color, the open/closed state they asked for |

Never mix them. The old product must not leak. The grey studio must not replace the room.

## Clip locks

Locked frame = the approved still. No zoom, pan, extra walls, or lighting change.

Speech: quote the line, fast yappy, no pauses, no extra words, then mouth closed until the clip ends. Name the locked voice (age, gender, American-English ethnicity). Never write "throughout 4 seconds" or "finish by 2.5s".

Hands stay on the still's contact points. One small move only if asked (zip, press, point). Zip: start state, pull direction, end state, travels once. Turn: degrees (side → front is 90, not a spin).

Hard cut only when they name the phrase and the second still.

If a 4s take clips the line, bump to 6s and keep it yappy. If zip + talk + turn fail, split the clip.

Rewrite unused script nouns to match the still. Do not keep two clips that speak the same line unless they want the hard-cut version.

## Output

One prompt in a fenced code block. If the still is missing, say that in one sentence and give the still prompt only.
