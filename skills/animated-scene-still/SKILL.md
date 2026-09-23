---
name: animated-scene-still
description: Write JSON image prompts for one composed 3D animated scene still or video opening frame, using character, environment, and prop references. Use for DreamWorks-inspired or broadly Pixar-style AI animation scenes; do not use for reference sheets, claymation, or real-world photographs.
---

# Animated Scene Still

Write **one valid JSON image prompt** for a single composed frame in a stylized 3D animated world. The frame may become the opening image of an AI video clip. Return the JSON in one `json` code block unless the user asks for another format. This skill writes prompts; generate the image only when requested. Use [references/json-blueprint.md](references/json-blueprint.md) as a structure, removing fields that do not apply.

## Composition and format

- Produce **one image**, not a character sheet, environment plate, prop grid, collage, or sequence. Match the intended video's aspect ratio. Use **9:16 for a short-form vertical video** when no other format is specified; otherwise follow the supplied project ratio or the user's explicit choice. Do not copy the landscape ratio of reference sheets into the final shot.
- Start with an observable story moment. Place every subject and prop in one coherent location, specifying foreground, middle ground, background, subject scale, contact points, gaze, and useful open space. Make the still suitable as a first frame: show the starting pose and object state before the clip's main action, not an unrelated beauty shot.
- Specify viewpoint by height, distance, angle, field of view, and crop. Frame the subjects clearly while preserving the environment's established geometry. A camera, phone, or tripod is never a scene object unless explicitly requested.

## Visual direction

- Default to the user's preferred **DreamWorks-inspired feature-animation CG** when the request says Pixar-style, DreamWorks-style, or simply AI animation without another medium. Describe the look through expressive sculpted faces, appealing silhouettes and proportions, shaped hair and fabric, rich but controlled saturation, layered set detail, plausible material response, and readable depth. Do not rely on a studio name alone in the final image prompt.
- Use light motivated by the set: a window, overcast sky, room fixture, streetlight, or another specified source. Keep its direction, shadow pattern, and colour consistent with the environment reference. Golden hour, amber haze, orange rim light, and sunset warmth appear only when requested or present in a controlling reference.
- Preserve the chosen 3D world across shots. Avoid slipping into live-action skin, clay fingerprints, flat illustration, anime line work, plastic-looking generic CG, or studio-lit product photography unless the user changes the visual direction.

## Reference and continuity control

- Give each provided image a clear role: character identity and costume, environment layout, prop geometry and markings, or shot composition. Preserve only the features that role controls. A photoreal source image may define a person's identity or an object's design without dictating the animated rendering style.
- Reuse the approved character's face shape, hair, body proportions, wardrobe, and accessories; the environment's landmarks, entrances, furniture, and light direction; and each prop's shape, scale, colour, logos, and state. Keep left/right relations and character-to-prop size consistent. Do not silently redesign established assets.
- If a needed reference does not exist, describe a restrained design in the prompt or use the corresponding character, environment, or prop reference skill when a reusable asset is needed. Do not require a sheet for incidental objects.
- For a scoped change, state what changes and what stays locked. When continuing from an approved still, preserve its composition and design unless the user requests a new shot.

## Text in the image

- No captions, subtitles, title cards, lower thirds, graphic text overlays, or watermarks by default.
- On signs, packaging, screens, and clothing, include readable text only when its exact wording is supplied or explicitly designed for this project. Quote the text exactly, name its placement and approximate size, and keep it legible. Do not request blurry substitute lettering or invented claims. If essential wording is missing, ask for it; if incidental, leave the surface free of readable text.
- For text that must be exact, inspect the generated result before treating it as approved. If the image model distorts it, use a text or compositing pass rather than claiming prompting alone guaranteed accurate lettering.

## Final check

Confirm one composed image at the intended video ratio; DreamWorks-inspired CG by default; reference identity and location geometry match; the pose works as a video first frame; light has one coherent logic without automatic golden hour; no physical recording gear or extra subjects appear; and every visible word is intentional and readable.
