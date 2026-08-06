---
name: environment-generation
description: Write detailed, model-ready image prompts for spatially clear wide 3/4-view environment references used in AI image generation, photo remixing, and AI video. Outputs prompt text only and never generates the image itself. Use whenever a scene needs a place — a location, setting, backdrop, background, set, room, or venue — for an AI image, product ad, or video clip, including a bedroom, bathroom, kitchen, living room, office, shop, gym, cafe, warehouse, stadium, street, poolside, courtyard, garden, landscape, or fantasy and sci-fi environment. Also use to establish or remix a location from a concept or reference photo, or to keep one place consistent across several shots. Trigger on "where should this be shot", "background for this clip", or a cut list naming places that need references.
---

# Environment Generation

Write one image-generation prompt for a coherent environment reference: depth, boundaries, openings, landmarks, and object placement clear enough for a downstream video model.

**Output is prompt text only.** Put the finished prompt in a code block and stop. Do not generate, render, preview, or offer to generate the image.

## Defaults

- **Wide 16:9 landscape** even when the final video is vertical — more spatial information for the model
- **True 3/4 view** (mandatory) — never a flat frontal "pretty plate"
- **One light logic** — one primary source direction and one shadow direction (never two suns)
- Photorealistic, deep readable focus, rectilinear 24–35 mm character, upright verticals
- Unoccupied by default; people only if requested or essential for scale

## Workflow

1. Environment type, mood/function, era, style, required details.
2. Spatial plan first: footprint, boundaries, zones, openings, circulation, fixed landmarks, and at least one **staging anchor**.
3. Diagonal 3/4 camera that reveals the most useful geometry (not head-on).
4. Load [references/prompt-blueprints.md](references/prompt-blueprints.md) (interior or exterior).
5. Furnishings and atmosphere without hiding the plan; lock one light direction.
6. Final check. Return only the prompt unless the user asks for explanation.

Infer coherent locations. Ask only when a missing decision would fundamentally change the place.

## 3/4 view — not frontal

A frontal head-on plate looks like a nice photo but fails as a video location: it reads as **flat wallpaper**, and past its edges the model invents new surroundings every generation. A **3/4 diagonal** gives the model depth to place subjects and covers almost a full circle of usable angles.

**Interior:** camera near a corner / diagonally across the room. Two adjoining walls receding in different directions, broad floor, enough ceiling for volume. Natural corner — not a dollhouse cutaway. Eye-level or slightly elevated.

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

## Prompt content order

1. Environment type, purpose, era/style, visual identity
2. Wide 3/4 composition and camera placement
3. Spatial shell, openings, zones, pathways, landmarks
4. Furnishings, props, vegetation, condition
5. Lighting, weather/atmosphere, material response
6. Rendering style, optics, 16:9, consistency locks and exclusions

Visible text/logos only when supplied or essential; otherwise exclude invented branding and writing.

## Final check

- Unmistakable **3/4 diagonal** — not frontal wallpaper, not top-down
- At least one clear staging anchor; landmarks relational and plausible
- Adjacent surfaces and depth explain the space beyond the immediate camera view
- One light source logic (no contradictory dual suns)
- Foreground does not hide essential geometry
- Wide 16:9 stated in the prompt; rectilinear, level, sharp
