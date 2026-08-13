# Clip prompts

Load this after an approved still exists, for a remake clip with product in hands. Simple talking-head with no product and no winning ad is **simple-talking-head**, not this file.

Output one prompt in a code block.

## Engine

Gemini Omni. 720p. 9:16. 24fps. 4s or 6s only.

| Line | Duration |
|---|---|
| about 8 words or fewer | 4s |
| Longer, or last 4s take clipped | 6s |

If they ask 8s, write 6s and split the leftover.

References are identity refs, not start frames, unless they say start-frame.

## Speech

On-camera. One take. Fast yappy UGC. American English matching the locked talent.

```
She says, once, at a fast yappy UGC pace, with no pauses:
"[line]"
As soon as the last word is out, her mouth closes. She holds the same pose in silence for the rest of the clip.
```

Never write throughout 4 seconds, finish by 2.5s, or speak slowly enough to fill the clip.

Leftover time = silent hold. No new gesture, no second pass of the line, no extra words.

## Locked frame

First frame = the still. Camera never moves. Room, table, crop, and lighting stay.

Hands stay on the still's contact points. Add one small move only if asked:

| Move | Write |
|---|---|
| Zip open | Start pinched/almost closed, pull direction, those zips open. Slider travels once. |
| Zip close | Start ajar, pull direction, teeth fully meshed. Do not zip an already closed zipper. |
| Press sides | Palms stay and squeeze a little. |
| Point / touch | Fingers move inside already-open compartments. |
| 90-degree turn | Start face, end face, about 90 degrees. Not 180, not a spin. |

Hard cut only when they name the phrase and the second still.

## Prompt skeleton

```
Gemini Omni, 720p, 9:16, 24fps, [4s/6s].

REFERENCES
@image1 is the locked starting still. Match the person, product, room, crop, and hands. Identity reference, not a start-frame upload.

FIRST FRAME
Exactly @image1.

CAMERA
Locked. No zoom, pan, tilt, or cut [unless a hard cut is specified].

ACTION
[one continuous oner / or one named hard cut]
[the single hand move, or hands stay]

SPEECH
[locked voice], American English, fast yappy UGC, no pauses.
She says once:
"[line]"
Then mouth closed, silent hold to the end.

AUDIO
Only her voice, then room tone.

LOCKS
same person, same product, same logo, same room and light, hands stay, no extra words
```

## After generation

Use voxtype-transcribe. Rename `clip-01-slug.mp4` in spoken order. Write the exact transcript under each file in `clips/CLIP_INDEX.txt`.
