---
name: video-generation
description: Write model-ready prompts for AI video generation engines such as Seedance, Veo, Kling, Sora, Runway, and Hailuo. Outputs prompt text only and never generates the video itself, and writes silent footage with no on-camera dialogue by default since generated lip-sync is unreliable. Use when the user wants a video prompt, a cinematic shot or scene, a clip built from a script beat or storyboard, b-roll or product footage, a multi-cut sequence inside one generation, or asks how to prompt an AI video model; also use when turning character, prop, or environment reference images into a clip. Trigger on phrases like "video prompt", "write a Seedance prompt", "make a clip where...", "build this shot", "generate this scene", "turn this script into clips".
---

# Video Generation

Turn a script beat, storyboard frame, or loose idea into one standalone AI video prompt. Block, light, and pace each shot like a director, not a copywriter.

**Output: one prompt per generation, in a code block, nothing else** unless the user asks for options or explanation.

**Do not generate the video.** No video or image tool calls, no rendering, no previews, no offering to generate. The user runs every generation themselves on their own platform, then pastes results back for review.

> Prompt-craft technique adapted from free Higgsfield Academy material. No authorship claimed.

## Core principle: write the visible

The model reacts to what can be seen and measured, never to mood words. Translate every abstraction into something observable.

- "tense scene" -> "he freezes, slowly closes his fist, light only from the side, half the face in shadow"
- "epic fast car shot" -> "low tracking shot alongside the car through a wet curve, spray off the tyres, hard buffeting camera shake"

Before returning a prompt, watch it in your head as a viewer. Is the first frame non-empty, is it clear where each subject is and where it looks, and where the light comes from.

## Workflow

1. **Find the beat.** One prompt covers one continuous generation. Name what turns in it.
2. **Check the clip budget.** Most engines cap a single generation at 5-10 seconds. If the beat needs more, split it into numbered generations and write one prompt each.
3. **Set continuity anchors.** Who and what is in frame, and which details must survive into the next generation.
4. **Write the blocks** in the order given in [references/prompt-blocks.md](references/prompt-blocks.md).
5. **Tag the references** using the rules below.
6. **Run the final check** at the bottom of this file.

Close gaps in conversation before writing when blocking, light, timing, or the first frame is genuinely ambiguous — the model fills any gap on its own, rarely the intended way. Do not ask about details that can be inferred.

## Context isolation

Each generation is a blank slate with no memory of the others. Every prompt is a sealed single-shot document.

Never carry in scene numbers, script headings, recaps of earlier shots, "as above" or "continues from" phrasing, unused tags, or people and props that are not physically in this shot.

To chain generations, export the last frame of the finished clip and hand it to the next generation as its opening reference. Continuity comes from that frame plus restated locks, never from narration about what happened before.

## Reference tagging

A reference image (`@tag`) sets appearance and identity. The text sets what happens. Both are required.

- Use the tags the user specifies. Otherwise name them by load order: `@image1 @image2`, `@video1`, `@audio1`.
- **Keep tagged descriptions short.** Long appearance text fights the reference image and degrades the likeness. Write: age, role or build, current state, unique visible features, action-critical details, and voice only if the character speaks. Then `100% matches the reference`.
- State identity-critical details in words even when they are visible in the reference — small text, logos, and exact colours get dropped otherwise.
- Never place an `@tag` in a shot where that subject is absent; the model will force it into frame.

## Prompt structure

Full block-by-block spec, style placement, and worked examples: [references/prompt-blocks.md](references/prompt-blocks.md).

Order, dropping any block the shot does not need:

```
SCENE CONTEXT -> ACTIVE REFERENCES -> LOCATION MAP -> FIRST FRAME / BLOCKING
-> FORMAT MODE -> OPTICS -> CAMERA -> ACTION -> PERFORMANCE -> PHYSICS
-> LIGHTING -> COLOR GRADE -> WARDROBE -> AUDIO -> STYLE -> OUTPUT SETTINGS
-> POSITIVE LOCKS
```

Two rules govern placement:

- **No style prefix.** Style is not one block. Light goes in LIGHTING, acting and skin realism in PERFORMANCE, colour in COLOR GRADE or folded into LOCATION. Only technical format — resolution, grain, fps, aspect ratio — sits as a short suffix in STYLE and OUTPUT SETTINGS. The prompt always opens on SCENE CONTEXT.
- **CAMERA sits third** among the core layers (subject -> action -> camera -> style -> locks). At the end its FOV gets ignored; at the front it fights identity.

A lock is a short positive fixer next to what it protects: `"the chain stays flush against the skin in every cut"`. Write densely where control matters and sparsely where it does not. Say each important thing once.

## Cuts and timing

Pick the least precision the shot actually needs.

| Mode | Write it as | Use when |
|---|---|---|
| Oner | "one continuous shot, the camera does not cut on its own" | single unbroken beat |
| Sequential cuts | `CUT 1 ... CUT 2 ...` | specific cuts, timing flexible |
| Timed multishot | explicit `HARD CUT` at stated seconds | beats must land on a clock |
| Freestyle b-roll | no cuts locked | let the model find angles |

Whenever cuts are specified, add: *"cuts only at the specified points, the camera does not cut on its own."*

```
0.0s to 1.5s — [description]
1.5s HARD CUT
1.5s to 3.0s — [description]
```

Cut types: `HARD CUT`, `SMASH CUT`, `MATCH CUT`, `INSERT CUT`, `REVERSE CUT`, `WHIP CUT`. Fades only on request. A whip under 0.8s renders as a hard cut with no blur. Hard cuts only between speed modes — one shot holds one speed start to finish.

Across internal cuts hold the same character set, geometry, screen direction, gaze, light, wardrobe, and prop state.

## Directing

**Blocking.** State where each person stands, sits, moves, what the hands do, what sits between them. "She sits across from him in the booth, knees touching under the table" beats "they sit and talk."

**Acting.** Emotion is muscle movement, never a label. "Her eyes drop to the table, jaw tightens, she swallows once before answering" beats "she looks sad." Restraint by default.

**Pace.** Read the dramatic structure. A confession needs air and held frames. Action compresses. A reveal lands on one held close-up.

**Camera.** Motivate every move and state it concretely: "low-angle 18 degree dolly-in, slow push from waist to chest as she realizes."

## Hard rules

- **Positive phrasing only.** State the target, never the prohibition. "stays upright, feet planted" beats "does not fall backward."
- **Speeds in km/h**, atmosphere in percent or metres (`fog density 40%`, `haze visible at 15 metres`), white balance in Kelvin, fixed within a scene.
- **Atmosphere builds in steps** across a sequence: 20% -> 40% -> 60%.
- **Giant scale by human comparison**: "as tall as four humans stacked head to toe."
- **Left and right are from the camera.**
- **FOV in degrees** from the anchor table, never millimetres, never arbitrary values.
- **Colour as material plus light plus role**, never a flat list: "crimson silk catching the cold spill from the corridor" beats "she wears red."
- **Background in layers** — foreground, midground, background stated separately.
- **Environment interaction stated physically**: snow melts on skin, wind moves fabric.
- **No director names, no signature-work references, no camera or lens model names.** Describe the look instead.
- **No readable UI text, captions, or logos** unless the user supplies exact wording. Composite graphics in the edit.
- **English prompts only.**

## No Talking On Camera

Default to silent footage in every prompt, ads and everything else. Characters do not speak, mouth words, or address the camera. Lip-sync on generated video still reads as wrong — mouth shapes drift out of step with audio, and the artifact is the single fastest way for a clip to look AI-made. Silent footage sidesteps it entirely, and it also lets any clip be regenerated later without re-recording audio.

What to write instead:

- **State the mouth.** A closed mouth needs saying, since a character framed on the face tends to drift into talking. Put "lips closed" or "mouth relaxed and closed" in PERFORMANCE, and repeat it in POSITIVE LOCKS for any shot tighter than a medium.
- **Give the face something else to do.** Silent does not mean blank. A slow blink, a small exhale, eyes moving to the product, a faint smile at the corner of the mouth — expression carries the beat where dialogue would have.
- **Give the hands and body the work.** Silent clips live on action. She touches the chain, turns her head, walks into frame, dries her hands. Blocking replaces speech.
- **Keep AUDIO ambient.** Room tone, water, footsteps, fabric. No voice line, even on engines with native audio, since a generated voice will not match the voiceover laid over it in the edit.

Voiceover gets recorded separately and placed in the edit, so the script's words never enter the video prompt.

When the user explicitly asks for a talking clip, write it — but say plainly that lip-sync is the weak point and that a silent take with voiceover over it is more reliable.

## Optics

Shot sizes, the FOV anchor table, and optical recipes for hidden-camera, broadcast, snake-cam and tele-compression looks: [references/optics.md](references/optics.md). Read it before writing the OPTICS block.

## Engine differences

Clip length caps, aspect ratio handling, reference-image support, audio behaviour, and per-engine quirks: [references/engine-notes.md](references/engine-notes.md). Read it when the user names an engine or when clip length and aspect ratio matter.

## Ad and UGC work

When the clip belongs to a short-form ad, the script comes first and the visuals serve it. Use **script-generation** for the script and cut list, then write one video prompt per generation from that cut list.

These rules override normal cinematic instinct in this context. Silent footage is covered above and applies here too.

- **Respect content moderation.** Water, swimwear, bathrooms, and intimacy stack into silent rejections. Keep wardrobe plain, framing tight and practical, expressions neutral, and describe the action flatly: "water running over her neck at the sink," not a shower scene. Avoid piling up suggestive adjectives.
- **Keep clothing solid.** The common failure is not a sheer garment being asked for; it is a plain opaque top rendering semi-transparently on its own, so the body reads through it. Name the fabric weight in WARDROBE ("heavyweight opaque ribbed cotton, nothing showing through"), keep the key light frontal or side rather than behind the subject in LIGHTING, and lock it in POSITIVE LOCKS: "the top stays solid uniform white with no underlying shape visible through it". Water and stretch amplify it, so a clip with water on the body needs the lock stated even when the sheet was clean.
- **Minors: describe, never upload.** A real photograph of a child as a reference image is typically blocked, while a text description usually generates and produces a synthetic child, which is the safer route. So for any clip involving a minor, write the description into the prompt and attach no reference image for that character.

## Final check

- Blocks in order, prompt opens on SCENE CONTEXT, CAMERA third, technical style as a suffix?
- Each style aspect in its home block, adapted to this scene rather than generic?
- Tags named per the rule, present only where the subject is, descriptions short?
- Everything positive, speeds in km/h, atmosphere in %/m, WB in Kelvin?
- FOV from the anchor table, per segment in a multishot, with "no drift mid-segment"?
- Emotion as muscle movement, left/right from camera, colour as material plus light?
- First frame non-empty and fully specified?
- Within the engine's clip length cap, correct aspect ratio?
- Locks restate the details most likely to drift?
