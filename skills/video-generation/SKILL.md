---
name: video-generation
description: Write model-ready prompts for AI video generation engines such as Seedance, Veo, Kling, Sora, Runway, and Hailuo. Outputs prompt text only and never generates the video itself, and writes silent footage with no on-camera dialogue by default since generated lip-sync is unreliable. Use when the user wants a video prompt, a cinematic shot or scene, a clip built from a script beat or storyboard, b-roll or product footage, a multi-cut sequence inside one generation, or asks how to prompt an AI video model; also use when turning character, prop, or environment reference images into a clip. Trigger on phrases like "video prompt", "write a Seedance prompt", "make a clip where...", "build this shot", "generate this scene", "turn this script into clips".
---

# Video Generation

Turn a script beat, storyboard frame, or idea into **one standalone AI video prompt**. Block, light, and pace like a director.

**Output: one prompt per generation, in a code block.** Do not generate, render, preview, or offer to generate the video. The user runs generation on their platform.

## Core principle

The model reacts to what is **visible and measurable**, not mood words.

- "tense" → freezes, slowly closes fist, side light, half face in shadow
- "epic car shot" → low track alongside wet curve, spray off tyres, buffeting shake

Before returning: watch the prompt as a viewer — non-empty first frame, subject positions and gaze, light direction.

## Workflow

1. One continuous generation per prompt; name what turns in it.
2. Clip budget: most engines 5–10s. Longer beat → split into numbered generations.
3. Continuity anchors: who/what in frame, details that must survive the next gen.
4. Write blocks in order from [references/prompt-blocks.md](references/prompt-blocks.md).
5. Tag references (below).
6. Final check.

Ask only when blocking, light, timing, or first frame is truly ambiguous.

## Context isolation

Each generation is a blank slate. No scene numbers, script headings, "as above", "continues from", unused tags, or subjects not physically in this shot.

To chain: export last frame of approved clip → next gen's opening reference + restated locks. Continuity from frame + locks, never narration about prior shots.

## Reference tagging

`@tag` = appearance/identity. Text = what happens. Both required.

- Use user-specified tags, else load order: `@image1`, `@video1`, `@audio1`
- Keep tagged descriptions **short**: age, role/build, state, unique visible features, action-critical details → then `100% matches the reference`. Long appearance text fights the image.
- State identity-critical details in words even when visible (small text, logos, exact colours)
- Never `@tag` a subject absent from the shot

## Prompt block order

Drop blocks the shot does not need:

```
SCENE CONTEXT → ACTIVE REFERENCES → LOCATION MAP → FIRST FRAME / BLOCKING
→ FORMAT MODE → OPTICS → CAMERA → ACTION → PERFORMANCE → PHYSICS
→ LIGHTING → COLOR GRADE → WARDROBE → AUDIO → STYLE → OUTPUT SETTINGS
→ POSITIVE LOCKS
```

- **No style prefix.** Prompt opens on SCENE CONTEXT. Light → LIGHTING; acting/skin → PERFORMANCE; colour → COLOR GRADE or LOCATION. Technical format (res, grain, fps, aspect) is a short STYLE/OUTPUT suffix.
- **CAMERA third** among core layers (subject → action → camera → style → locks). End of prompt ignores FOV; front fights identity.
- Locks: short positive fixers next to what they protect. Say each important thing once.

Full block spec + example: [references/prompt-blocks.md](references/prompt-blocks.md).  
Shot sizes + FOV table: [references/optics.md](references/optics.md).  
Engine caps: [references/engine-notes.md](references/engine-notes.md).

## Cuts and timing

| Mode | Write as | Use when |
|---|---|---|
| Oner | continuous shot, camera does not cut on its own | single unbroken beat |
| Sequential cuts | `CUT 1 … CUT 2 …` | specific cuts, flexible timing |
| Timed multishot | `HARD CUT` at stated seconds | beats on a clock |
| Freestyle b-roll | no locked cuts | model finds angles |

When cuts are specified: *"cuts only at the specified points, the camera does not cut on its own."*

```
0.0s to 1.5s — [description]
1.5s HARD CUT
1.5s to 3.0s — [description]
```

Cut types: `HARD CUT`, `SMASH CUT`, `MATCH CUT`, `INSERT CUT`, `REVERSE CUT`, `WHIP CUT`. Fades only on request. Whip under 0.8s → hard cut, no blur. One speed mode per shot start to finish. Across internal cuts: same characters, geometry, screen direction, gaze, light, wardrobe, prop state.

## Directing rules

- **Blocking** — where each person/object is, hands, what sits between them
- **Acting** — muscle movement, not emotion labels; restraint by default
- **Pace** — confession needs air; action compresses; reveal holds a close-up
- **Camera** — every move motivated and concrete

## Hard rules

- **Positive phrasing only** — "stays upright, feet planted" not "does not fall"
- Speeds in **km/h**; atmosphere in **% or metres**; white balance in **Kelvin** (fixed in scene)
- Atmosphere builds in steps across a sequence (20% → 40% → 60%)
- Giant scale by human comparison; left/right from **camera**
- **FOV in degrees** from the optics anchor table — never mm, never arbitrary values
- Colour as material + light + role; background in foreground/mid/background layers
- Environment interaction physical (snow melts, wind moves fabric)
- No director names, signature-work refs, camera/lens model names
- No readable UI/captions/logos unless user supplies exact wording
- **English prompts only**

## Silent footage (default)

No on-camera speech, mouthing, or address to camera. Lip-sync is the fastest AI tell; silent clips also regenerate without re-recording audio.

- PERFORMANCE: "lips closed" / "mouth relaxed and closed"; repeat in POSITIVE LOCKS for tighter-than-medium
- Face still acts: blink, exhale, eyes to product, faint smile
- Hands and body carry the beat
- AUDIO ambient only (room tone, water, footsteps) — even on engines with native audio
- Voiceover never enters the video prompt

If user demands talking: write it, flag lip-sync risk, offer silent+VO.

## Ad / UGC overrides

Script first via **script-generation**; one video prompt per generation from the cut list.

- **Moderation** — do not stack water + swimwear + bathroom + intimacy. Plain wardrobe, practical framing, flat action description.
- **Clothing solid** — name fabric weight opaque in WARDROBE; key light frontal/side; lock "top stays solid, no underlying shape through it". Water/stretch need the lock even if the sheet was clean.
- **Minors** — describe in text, never upload a real child photo as reference.

## Final check

- Blocks ordered; opens SCENE CONTEXT; CAMERA third; technical style as suffix
- Tags short, only where subject is present
- Positive phrasing; km/h, %/m, Kelvin; FOV from table; "no drift mid-segment" if multishot
- Emotion as muscle; left/right from camera; first frame specified
- Within engine clip cap and aspect ratio; locks on what drifts
