---
name: environment-generation
description: Write detailed JSON image prompts for spatially clear wide 3/4-view environment references used in AI image generation, photo remixing, and AI video. Outputs prompt text only and never generates the image itself. Use whenever a scene needs a place — a location, setting, backdrop, background, set, room, or venue — for an AI image, product ad, or video clip, including a bedroom, bathroom, kitchen, living room, office, shop, gym, cafe, warehouse, stadium, street, poolside, courtyard, garden, landscape, or fantasy and sci-fi environment. Also use to establish or remix a location from a concept or reference photo, or to keep one place consistent across several shots. Trigger on "where should this be shot", "background for this clip", or a cut list naming places that need references. Has an animated mode for stylized 3D projects.
---

# Environment Generation

Write one image-generation prompt for a coherent environment reference: depth, boundaries, openings, landmarks, and object placement clear enough for a downstream video model.

**Output is a JSON image prompt only.** Return one valid JSON object in a `json` code block and stop. Do not generate, render, preview, or offer to generate the image.

Use the structured JSON style in [references/prompt-blueprints.md](references/prompt-blueprints.md). Emit parseable JSON with double-quoted keys and strings; no comments, markdown inside the object, trailing commas, or unresolved placeholders. Omit irrelevant fields instead of filling them with guesses. Keep `final_generation_instruction` consistent with the structured fields.

## Animated mode

Use this mode when the project is stylized 3D animation (the `animated-video-production` skill, or a request for Pixar-, DreamWorks- or feature-animation-style characters, places or props). The defaults below still apply: one 16:9 landscape establishing plate. What changes:

- **Render** the place as feature-animation CG: sculpted, slightly stylized architecture and props, rich but controlled colour, layered set dressing, soft 3D shading. Replace the photoreal and `photograph` wording with this.
- **Light** with the location's real source at the time of day the story needs, and state its brightness. No golden hour unless the brief asks for it. This light becomes the reference for every still shot there.
- **View:** 3/4 stays the default. When the shot list frames the place head-on (a building facade seen straight on), make the sheet head-on too, so stills and sheet agree.
- **Empty of characters,** but include the fixed props the story uses (a bench, the bins, a box and quilt) at their story positions.
- **Where the prompt goes:** in an animated project, save the prompt to the asset's `prompts/` folder. It may then be generated with the `flow` skill; the prompt-only rule above covers standalone requests.

## Defaults

- **Exactly one 16:9 landscape output image**, even when the final video is vertical — a single establishing plate, not a portrait canvas or separate angle images
- **True 3/4 view** (mandatory) — never a flat frontal "pretty plate"
- **One light logic** — one primary source direction and one shadow direction (never two suns)
- In the JSON image prompt, specify materials, spatial scale, perspective, focus, source direction, exposure, and shadow behavior rather than using `realistic`, `photorealistic`, or `cinematic` as a style label. Daytime defaults to ordinary neutral daylight, not an amber sunset or gold-tinted atmosphere, unless the user or reference asks for it.
- Photorealistic, deep readable focus, rectilinear 24–35 mm character, upright verticals
- Unoccupied by default; people only if requested or essential for scale

## Workflow

1. Environment type, mood/function, era, style, required details.
2. Spatial plan first: footprint, boundaries, zones, openings, circulation, fixed landmarks, and at least one **staging anchor**.
3. Diagonal 3/4 camera that reveals the most useful geometry (not head-on).
4. Load [references/prompt-blueprints.md](references/prompt-blueprints.md) (interior or exterior) and fill its JSON structure.
5. Furnishings and atmosphere without hiding the plan; lock one light direction.
6. Final check. Return only the prompt unless the user asks for explanation.

Infer coherent locations. Ask only when a missing decision would fundamentally change the place.

## 3/4 view — not frontal

A frontal head-on plate looks like a nice photo but fails as a video location: it reads as **flat wallpaper**, and past its edges the model invents new surroundings every generation. A **3/4 diagonal** gives the model depth to place subjects and covers almost a full circle of usable angles.

**Interior:** camera near a corner / diagonally across the room, aimed toward a visible far inside corner placed clearly off-center (about one-third or two-thirds across the image). Two adjoining walls occupy meaningful width and their wall-floor seams run diagonally in different directions toward that corner. Show broad floor and enough ceiling for volume. Natural corner — not a dollhouse cutaway. Eye-level or slightly elevated. Avoid a broad far wall square to the camera even if side walls are visible.

**Exterior / stadium / landscape:** strong foreground, lateral depth, far boundary or focal structure, at least one adjoining side. Entrances, routes, and landmarks stay readable.

**Avoid:** flat head-on façades, centered one-point symmetry, fisheye, extreme ultra-wide stretch, aerial top-down. If multiple views are requested, keep a 3/4 establishing hero that other angles agree with. For action sets that need both sides, still lead with 3/4; add a second reverse/back plate only when the user asks for multi-angle coverage.

## Spatial rules

- Shell first: scale, shape, walls/ground, ceiling/sky, doors, windows, level changes, routes
- **Staging anchor** — leave one clear fixed landmark (column, lamp, sofa, counter, tree, doorway) and place features relative to it. Staging like "hero at the lamp, facing the door" works; "hero in the room" is a lottery downstream
- Landmarks placed relationally ("doorway beyond the sofa on the right")
- Foreground / midground / background zones; open pathways; no blocked doors or floating objects
- **One light logic:** one primary source and one shadow direction; state time of day and where light enters
- Materials, season, time of day, and set dressing tell one story
- Reference image: preserve architecture, layout, landmarks, materials, lighting unless asked to change. Infer unseen areas conservatively. Expand a frontal reference into a true 3/4 when needed. Scoped remix: name the change, lock the rest.

## JSON fields (order)

1. `prompt_type`, `objective`, and `reference_fidelity` when a reference exists
2. `canvas_and_camera`, `environment`, `spatial_design`
3. `set_dressing`, `materials_and_condition`, `lighting_and_atmosphere`
4. `rendering_and_consistency_locks`, `negative_prompt`, `final_generation_instruction`

In-world text is welcome; overlays are not. Anything that carries print in real life (a newspaper, a sign, a book cover, packaging, a label, a shop front) gets short, readable, plausible text written into the prompt in quotes: a headline, a brand name, a product line. Invent fictional brands; use a real one only when the user supplies it. Keep each surface to a few words and leave fine print soft. Never captions, subtitles, watermarks, app UI or on-screen graphics.

## Final check

- Unmistakable **3/4 diagonal** — for an interior, the far corner is off-center and two wall-floor seams angle toward it from different sides; not frontal wallpaper or top-down
- At least one clear staging anchor; landmarks relational and plausible
- Adjacent surfaces and depth explain the space beyond the immediate camera view
- One light source logic (no contradictory dual suns)
- Foreground does not hide essential geometry
- Exactly one wide 16:9 image stated in the prompt; rectilinear, level, sharp
