# Engine notes

Read when the user names an engine, or when clip length / aspect ratio drives script split.

**Verify before relying on a number.** Platforms and wrappers change often. When a limit decides generation count, check current docs for the surface the user is on.

## Caps and capabilities

| Engine | Clip length | Aspect | Native audio | References | Verified |
|---|---|---|---|---|---|
| Seedance 2.0 | 4–15s | 16:9, 9:16 | no — ambient only, VO in edit | up to 9 images, 3 video, 3 audio; 12 files total | yes |
| Veo 3.1 | 4s / 6s / 8s; ref-image mode locks 8s; 24 fps | 16:9 or 9:16 | yes | images; ref mode 8s only | yes |
| Kling 2.5 | up to 10s (often 5 or 10 selector) | 16:9, 9:16, 1:1 | no | first and last frame | yes — APIs vary |
| Hailuo 02 | ~10s model; some APIs 6s | 16:9, 9:16 | no | first frame | check before use |
| Sora 2 | short; tier-dependent | 16:9, 9:16 | yes | varies | check before use |
| Runway Gen-4 | short; extendable | multiple incl. 9:16 | limited | first frame, references | check before use |

Verified rows drawn from vendor docs at last update; wrappers (fal, Replicate, PixVerse, etc.) may expose shorter caps.

## What changes per engine

Block structure and visible-detail discipline stay the same. Adjust only:

- **Clip budget** — split before writing prompts
- **Aspect ratio** — state in OUTPUT SETTINGS. Wide reference sheets stay wide (content reference); **first-frame** images must match delivery ratio
- **Audio** — native-audio engines: ambient in AUDIO, characters still silent for ads. No-audio engines: all voice in edit
- **Reference count** — deep stacks (Seedance) vs frame-only engines (bake identity into keyframe first)
- **Multishot** — HARD CUTs reliable on Seedance; single-motion engines: one cut per gen, assemble in edit

## Stitching past the cap

1. Split so no generation exceeds the cap and no cut exceeds pacing.
2. Generate slightly long; trim in edit.
3. Last frame of approved clip → opening reference for the next.
4. Restate continuity locks every prompt (wardrobe, product, hair side, light direction drift first).
5. Keep a status table so regenerations do not lose place.
