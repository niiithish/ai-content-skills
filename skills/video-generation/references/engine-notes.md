# Engine Notes

Contents: clip length caps · reference support · audio behaviour · what changes per engine · stitching longer videos.

Read this when the user names an engine, or whenever clip length and aspect ratio affect how a script gets split.

**Verify before relying on a number.** These platforms ship breaking changes often, and a wrapper (fal, Replicate, PixVerse, Artlist, Higgsfield) frequently exposes a shorter cap or fewer resolutions than the underlying model. When a limit decides how many generations a script needs, check the current docs for the exact surface the user is on rather than trusting this table.

## Caps and capabilities

| Engine | Clip length | Aspect | Native audio | References | Verified |
|---|---|---|---|---|---|
| Seedance 2.0 | 4-15s per generation | 16:9, 9:16 | no — ambient only, lay VO over | up to 9 images, 3 video, 3 audio; 12 files total | yes |
| Veo 3.1 | 4s, 6s or 8s; reference-image-to-video locks to 8s; 24 fps | 16:9 or 9:16 | yes — synchronized dialogue, SFX, ambience, music | images supported; reference mode is 8s only | yes |
| Kling 2.5 | up to 10s, usually a 5s or 10s selector | 16:9, 9:16, 1:1 | no | first and last frame | yes, but API surfaces vary by version |
| Hailuo 02 | ~10s on the model; some APIs expose only 6s | 16:9, 9:16 | no | first frame | no — check before use |
| Sora 2 | short generations, varies by tier | 16:9, 9:16 | yes | varies by surface | no — check before use |
| Runway Gen-4 | short generations, extendable | multiple, incl. 9:16 | limited | first frame, references | no — check before use |

Sources for the verified rows: Seedance from the [ByteDance Seed model page](https://seed.bytedance.com/en/seedance2_0); Veo from [Google Cloud's Veo 3.1 docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate) and the [Gemini API video guide](https://ai.google.dev/gemini-api/docs/veo); Kling from [OpenCreator's 2.5 Turbo page](https://opencreator.io/models/kling-2-5), with the caveat that [Kling's API changelog](https://kling.ai/document-api/updates/api) shows durations differing by version and platform. Third-party wrappers such as fal, Replicate, and PixVerse sometimes upscale to 1080p from a lower native resolution.

## What actually changes between engines

The block structure and the visible-detail discipline carry across all of them. Only these need adjusting:

- **Clip budget.** Drives how many generations a script becomes. Write the split before writing any prompt.
- **Aspect ratio.** State it explicitly in OUTPUT SETTINGS. Engines that default to 16:9 will hand back landscape for a vertical ad unless told otherwise. If a keyframe or reference image is landscape, the generation tends to follow it — regenerate the reference at the target ratio instead of fighting it in text.
- **Audio.** On an engine with native audio, describe ambience in AUDIO and still keep characters silent for ad work. On an engine without it, AUDIO is ambient-only and every voice line is laid in during the edit.
- **Reference count.** Seedance accepts a deep reference stack, so character plus product plus environment can all be tagged in one prompt. Frame-only engines need the identity baked into a keyframe image first.
- **Multishot reliability.** Internal HARD CUTs hold up well on Seedance. On engines built around a single continuous motion, prefer one cut per generation and assemble in the edit.

## Stitching past the cap

1. Split the script so no generation exceeds the engine's cap, and no single cut runs longer than the pacing calls for.
2. Generate each clip a little long, then trim to length in the edit.
3. Export the final frame of an approved clip and pass it as the opening reference for the next one.
4. Restate the continuity locks in every prompt. Wardrobe, product placement, hair side, and light direction drift first.
5. Keep a status table — prompt written, generated, approved — so regenerations do not lose their place.
