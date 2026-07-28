---
name: environment-generation
description: Create detailed, model-ready image prompts for spatially clear 3/4-view environments used as references in AI image generation, photo remixing, and AI video. Use when the user wants to design, generate, visualize, establish, or remix an interior or exterior location such as a bedroom, kitchen, living room, office, shop, warehouse, stadium, arena, street, courtyard, garden, landscape, or fantasy/sci-fi environment from a written concept or reference image.
---

# Environment Generation

Create one standalone image-generation prompt for a coherent environment reference image. Optimize the image to establish the location clearly enough that a downstream AI video model can understand its depth, boundaries, adjoining surfaces, entrances, landmarks, and object placement.

## Related Skills

| Need | Use |
|---|---|
| A human character reference | **character-generation** |
| A product or object reference sheet | **prop-generation** |
| The video prompt that consumes this reference | **video-generation** |
| The script and cut list that decide which locations are needed | **script-generation** |

## Workflow

1. Identify the environment, intended mood or function, era, rendering style, and required details.
2. Define one coherent spatial plan before adding decoration: footprint, boundaries, main zones, openings, circulation paths, and fixed landmarks.
3. Choose a diagonal camera position that creates a genuine 3/4 view and reveals the most useful spatial information.
4. Read [references/prompt-blueprints.md](references/prompt-blueprints.md) and adapt the relevant blueprint.
5. Add furnishings, set dressing, materials, lighting, condition, and atmosphere without obscuring the spatial plan.
6. Check that every named feature can coexist in one frame and that the prompt contains no spatial contradictions.

Do not ask follow-up questions when a coherent environment can be inferred. Make restrained, specific choices and state them directly. Ask only when a missing decision would fundamentally change the location.

## Choose the Output Type First

Two different images get requested from this skill. Decide which one the user needs before writing, because the composition and aspect ratio differ.

- **Establishing sheet (default, always wide).** A wide 16:9 landscape 3/4 view whose job is to explain the whole space to a downstream model. Follow the 3/4-view rules below. **Keep this wide even when the final video is vertical.** A wide frame carries more usable spatial information — two adjoining walls, floor depth, opening positions, landmark relationships — and that is exactly what a video model needs in order to place a subject and hold the geometry steady. Cropping the location reference to vertical throws that information away and buys nothing.
- **Shot-ready keyframe.** A single frame that will open or seed a specific clip, matched to the delivery aspect ratio and composed as the actual shot rather than a survey of the room. State the ratio in the prompt and again in the locks; a landscape reference will drag a vertical generation back to landscape.

**Default to the establishing sheet.** Produce a keyframe only when the user asks for a shot, an opening or first frame, a keyframe, or a specific clip. A vertical delivery platform on its own is not a reason to narrow the environment sheet — vertical projects still want a wide location reference plus separate keyframes for the cuts that need one.

When a project needs both, write the wide establishing sheet first, then derive keyframes that agree with its layout.

## Require a True 3/4 View

This section governs the establishing sheet. A shot-ready keyframe uses the framing the shot calls for instead.

Make the main image a wide landscape 3/4-angle establishing view. This is mandatory for the reference workflow, including when another angle might look more dramatic.

- Place the camera diagonally across the environment rather than square to one wall or façade.
- For an interior, reveal two adjoining walls receding in different directions, a broad area of floor, and enough ceiling to clarify the room volume. Show the corner relationship naturally; do not create a dollhouse cutaway or remove walls unless requested.
- For an exterior, stadium, arena, courtyard, or landscape, reveal a strong foreground plane, lateral depth, a far boundary or focal structure, and at least one adjoining side or receding spatial edge.
- Keep entrances, exits, windows, corridors, stairs, field boundaries, and major landmarks readable. Avoid blocking them with foreground objects.
- Use eye-level or slightly elevated camera height by default. Use a moderately wide rectilinear lens, usually the visual character of 24–35 mm full-frame, wide enough to explain the space but not so wide that it bends walls or stretches corners.
- Keep verticals upright, geometry plausible, and near/far scale relationships natural. Avoid fisheye distortion, extreme ultra-wide stretching, aerial top-down views, centered one-point symmetry, or flat head-on compositions.
- If the user requests multiple images or views, retain a 3/4 establishing frame as the hero view and make the other angles agree with its spatial plan.

## Build One Stable Environment

Treat the prompt as a location specification, not a loose collection of décor.

- Establish the shell first: approximate scale, room or site shape, wall/ground boundaries, ceiling or sky condition, doors and openings, windows, level changes, and circulation routes.
- Place every fixed landmark relationally: for example, the screen is centered on the long wall, the doorway is beyond the sofa on the right, or the player tunnel opens beneath the left-side stands.
- Divide large locations into legible foreground, middle-ground, and background zones. Preserve open pathways and negative space.
- Keep architecture, furniture scale, object placement, materials, weathering, season, and time of day internally consistent.
- Use set dressing to communicate function and history, but group small objects into readable clusters rather than distributing clutter randomly.
- Include only objects that support the location. Prevent duplicate furniture, impossible overlaps, blocked doors, floating objects, contradictory windows, extra rooms, and malformed architecture.
- Default to an unoccupied environment so people do not become part of the location identity. Include people or crowds only when requested or essential for scale; keep incidental figures secondary and non-identifying.

## Use References and Remix Requests

Treat supplied images as evidence for the location's identity. Preserve recognizable architecture, layout, proportions, landmark placement, materials, colors, furnishings, wear, weather, and lighting unless the user requests a change. Use the platform reference token, such as `@image_1`, when available; otherwise say `the supplied reference image`.

Infer unseen areas conservatively from visible geometry and design language. Do not silently expand the location, move doors or windows, redesign architecture, or combine incompatible spaces. For a remix, name the requested change and explicitly lock the layout and all unaffected features.

## Write the Prompt

Return only the finished prompt unless the user asks for explanation or alternatives. Use cohesive natural language or concise titled sections; match the density and direct style of the user's examples. Do not expose placeholders or planning notes.

Include these elements in a logical order:

1. Environment type, purpose, era/style, and overall visual identity.
2. Mandatory wide 3/4-angle establishing composition and camera placement.
3. Spatial shell, adjacent surfaces, openings, zones, pathways, and fixed landmarks.
4. Furniture, props, vegetation, signage, surface condition, and lived-in details.
5. Lighting sources, time of day, weather or atmosphere, and material response.
6. Rendering style, rectilinear optics, depth of field, detail level, and aspect ratio.
7. Spatial consistency locks and exclusions.

Default to photorealistic 16:9 for an establishing sheet. For a shot-ready keyframe, use the delivery ratio the user named and state it in the prompt. Keep the whole environment sharp enough to read; avoid portrait-like shallow focus. Use visible text or logos only when supplied or essential, quote exact required wording, and do not invent branding. When text is not needed, explicitly exclude logos, brand names, and visible writing.

## Final Check

Before returning the prompt, verify:

- the frame is unmistakably a 3/4 view rather than a head-on or top-down shot;
- adjacent surfaces and depth cues explain the environment beyond the immediate camera view;
- the layout, openings, pathways, and landmark positions are unambiguous and physically plausible;
- foreground objects do not hide essential spatial information;
- décor, materials, condition, season, weather, and lighting tell one coherent story;
- no duplicated fixtures, impossible geometry, malformed architecture, or accidental extra spaces are encouraged;
- the framing is rectilinear, level, sharp, and suitable as an AI image/video location reference;
- the aspect ratio matches the output type — 16:9 for an establishing sheet, the stated delivery ratio for a keyframe — and appears in the prompt text.
