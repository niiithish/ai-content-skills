---
name: animated-video-production
description: Plan and prompt stylized 3D animated videos, including reference assets, composed scene stills, and image-to-video clips. Use when the user asks for DreamWorks-style, Pixar-style, or feature-animation-like AI content; default to expressive DreamWorks-inspired CG rather than a photographic or clay look.
---

# Animated Video Production

Build a consistent 3D animated world from a concept, script beat, or shot list. Write production-ready prompts and a small continuity plan. Generate media only when the user asks for generation, using the requested tool; for still generation without a tool choice, prefer the built-in image generator. Use Google Flow only when explicitly requested.

## Visual direction

- Treat “Pixar-style” as a broad request for 3D animation. Unless the user specifies another look, use the user's preferred DreamWorks-inspired feature-animation CG direction across all assets and clips.
- Convey that direction through visible choices: appealing sculpted character shapes, expressive faces and readable silhouettes, richly coloured environments, slightly saturated but controlled palettes, layered surfaces, coherent material response, and purposeful light and shadow. Describe the actual design in each prompt instead of relying on a studio name as the sole style instruction.
- Light the world from plausible sources in the location. Do not default to golden hour, orange rim light, amber haze, or sunset warmth. Use those only when the user or a controlling reference requests them.
- Keep characters, costumes, props, architecture, palette, and light direction consistent from reference sheets through scene stills and clips. Do not silently turn the look photographic, clay, flat illustration, or generic glossy CGI.

## Asset-to-clip workflow

Create only the assets the shot needs. When relevant, establish character identity, environment geometry, and prop design before composing the scene still. A composed scene still is one shot frame with the characters and objects in place; it is distinct from an empty environment reference.

- Use `character-generation`, `environment-generation`, and `prop-generation` for their reference-sheet structure. Their reference sheets stay **one landscape image each**. For this workflow, adapt their photographic rendering instructions to the animated CG direction above while preserving the single-image layout, views, panel separators, and consistency locks. A reference photo controls identity or design, not the artwork style unless the user says it does.
- Compose one scene still per planned clip or materially different shot. Specify aspect ratio from the user's project or request; do not inherit the 9:16 default of `photoreal-still-prompt`, which is for real-world photographs. Preserve the reference identities, proportions, wardrobe, prop markings, location layout, and light direction.
- Use the approved scene still as the opening frame for each video prompt. For another clip, restate the relevant continuity locks or use the approved last frame. Write one prompt per generation, with clear first-frame placement, action, duration, and end state.
- When the user asks only for a prompt or plan, output prompts or the plan. Do not render media or claim that an asset exists.

## Clip motion and framing

- Default to a **fixed viewpoint and unchanged crop** based on the scene still. Describe a steady, locked composition in positive terms. Do not insert zooms, pushes, pans, tracks, handheld sway, reframing, or cuts unless the user requests them or supplies them in a controlling reference.
- Do not write “no zoom” or similar negative camera-movement instructions into the generated prompt. State the desired fixed framing once. If the user requests a move, give it a clear direction, timing, and endpoint.
- Describe framing as a viewpoint, field of view, and subject placement. Do not describe a camera, phone, or tripod as a physical object in the scene. If the user mentions filming equipment to explain the viewpoint, translate that into framing and stability; include visible equipment only when the user explicitly wants it on screen.
- Give the animated subjects specific, physically coherent motion. Keep the environment, object scale, screen direction, and scene lighting stable throughout the clip.

## Sound and visible text — apply to every animated clip

- **Audio:** use only sounds that would be heard at the depicted place: room tone, weather, footsteps, fabric movement, objects being handled, doors, water, traffic, or other sounds caused by the scene. Match timing and distance to the visible action. No music, score, or soundtrack by default. Add dialogue, narration, or voiceover only when the user requests it.
- **Captions:** no subtitles, captions, title cards, lower thirds, or text overlays by default. Add them only when the user asks for them and provides the wording or approves copy.
- **In-world text:** preserve exact supplied spelling, typography hierarchy, logo, and placement on signs, labels, packaging, or screens. Ask for missing wording when readability matters. If wording is unknown and nonessential, keep that surface free of readable text rather than inventing blurry or garbled letters. Do not invent product claims or branding.
- Carry these sound and text rules into the clip prompt itself, not just production notes. Describe the positive audio bed and the approved visible text; include concise exclusions for music, captions, or invented writing when the target generator needs them.

## Final check

Before returning, confirm that the request routes to the animated CG workflow; the same design language reaches assets, scene stills, and clips; reference sheets remain one landscape image each; the clip starts from the approved still; framing stays fixed unless requested otherwise; no filming gear appears by accident; sound is scene-native with no music; captions are absent; and any visible wording is exact and readable.
