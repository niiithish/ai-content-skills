---
name: prop-generation
description: Create detailed, model-ready image prompts for consistent multi-view prop reference sheets on a neutral grey studio background, dynamically choosing the number and type of views needed to explain the object. Use when the user wants to design, generate, visualize, or remix a product, object, footwear item, toy, appliance, tool, vehicle, weapon, furniture item, or other non-character prop; turn a written concept or reference image into front, lateral, medial, side, rear, top, bottom, detail, or three-quarter views; or create an orthographic prop turnaround for AI image or video workflows.
---

# Prop Generation

Create one standalone image-generation prompt for a clean, consistent, multi-view prop reference sheet. Optimize the sheet for reuse as an identity reference in later image generation, photo remixing, and AI video work.

## Workflow

1. Identify the single hero prop and its intended use.
2. Extract or infer a canonical design before describing individual views: shape, proportions, colors, materials, construction, controls, markings, wear, and distinctive features.
3. Audit the prop's visible surfaces and identity-critical features, then select the smallest view set that fully explains them without forcing a later model to guess.
4. Read [references/prompt-blueprints.md](references/prompt-blueprints.md) and use the matching dynamic layout blueprint.
5. Write the final prompt in the required section order.
6. Check every view against the canonical design and remove contradictions.

Do not ask follow-up questions when a sensible design can be inferred. Make restrained, coherent choices and state them directly in the prompt. Ask only when a missing choice would substantially change the prop's identity.

## Select Views Dynamically

Choose views from the prop's geometry, asymmetry, and downstream motion needs—not from a fixed category template. Do not force every object into three or four panels. Before choosing the count, list mentally which surfaces or features would remain ambiguous from the current set and add only the view that resolves each ambiguity.

- Use **3 views** when front, one strict side, and rear fully explain a simple object.
- Use **4 views** when the top, underside, three-quarter silhouette, or a second side resolves one additional important ambiguity.
- Use **5–6 views** for shape-rich, wearable, strongly asymmetric, or mechanically layered props whose opposite sides and hidden surfaces differ. Footwear normally needs 6 views: lateral side, medial side, top-down, front three-quarter, rear/heel, and bottom/outsole.
- Use **7–8 views** only when each extra panel reveals distinct identity-critical geometry, articulation, access, or attachment information. If more than 6 views would make panels too small to remain useful, create two explicitly linked sheets with the same canonical design rather than overcrowding one image.
- Choose **both sides** when lateral/medial faces, controls, doors, attachments, graphics, wear, or construction differ.
- Choose **top** when controls, openings, lacing, surface layout, roof equipment, seating, or plan shape matter.
- Choose **bottom/undercarriage** when tread, outsole, wheels, tracks, chassis, mounting points, mechanisms, or underside construction matter.
- Choose **front or rear three-quarter** when an integrated 3D view helps the model connect otherwise orthographic surfaces. Treat it as supporting geometry, not a dramatic beauty shot.
- Choose a **detail view** only for a feature that cannot read at full-object scale. A detail does not replace a required orientation view.
- Honor an explicit view count or layout from the user.

Run a coverage check before writing: can the view set reconstruct the prop's width, depth, height, both asymmetric sides, upper surface, contact/underside surface, and defining components? Omit orientations that are genuinely redundant; include those a downstream image or video model would otherwise have to invent.

Use true front, strict side, true rear, top, and bottom views whenever they are selected. Keep three-quarter views controlled and natural. Avoid dramatic foreshortening, wide-angle distortion, or a collage of unrelated beauty shots.

## Choose a Readable Layout

Use a landscape canvas and select a grid that keeps every full-object view large enough to inspect:

- 3 views: one horizontal row.
- 4 views: 2x2 grid.
- 5 views: balanced 3-over-2 or 2-over-3 grid, with equal visual scale and centered empty space in the shorter row.
- 6 views: 3x2 grid.
- 7–8 views: 4x2 grid only when adequate resolution is available; otherwise split into two matching sheets.

Arrange views in a logical rotation or inspection sequence. Give every panel its own clear area, use consistent object scale, and allow unusually long or tall orientations to use their cell efficiently. Do not enlarge a three-quarter hero view so much that it makes technical views secondary. Use no labels by default; if orientation could be confused, add only small plain labels.

## Preserve One Prop Across Every Panel

Treat all panels as views of one physical object, not variants.

- Repeat that the design, proportions, dimensions, colors, materials, markings, damage, attachments, and component placement remain identical in every view.
- Describe asymmetrical features with exact left/right placement and preserve that placement through rotation.
- Keep visual scale and camera height consistent. Center each view independently with balanced margins and no overlap or cropping.
- Show physically plausible geometry. Make front, side, rear, top, and bottom views agree about thickness, depth, wheelbase, handles, seams, doors, controls, and attachments.
- For a supplied reference image, preserve its recognizable silhouette, proportions, color palette, materials, branding, surface details, and wear unless the user requests a change.
- When editing or remixing a supplied prop, name what changes and explicitly lock everything else.

## Write the Prompt

Return only the finished prompt unless the user asks for explanation or alternatives. Use natural language and concrete visual descriptions rather than keyword stuffing.

Write sections in this order:

1. `PROP REFERENCE SHEET` — state the object, view count, layout, and reference-sheet purpose.
2. `CANONICAL PROP DESIGN` — fully define the one design shared by every view.
3. `VIEWS` — state the dynamically selected count and define each panel's orientation and the ambiguity it resolves.
4. `LAYOUT` — define the matching grid, panel positions, spacing, consistent scale, margins, dividers, and labels if needed.
5. `BACKGROUND + LIGHT` — specify a seamless neutral medium-to-dark grey studio background, soft neutral product lighting, subtle contact shadows, and no environment.
6. `CAMERA + OPTICS` — specify orthographic or near-orthographic framing, a normal lens character, rectilinear edges, deep focus, and no perspective distortion.
7. `MATERIAL + DETAIL` — explain how each surface responds to light and how fine details should render.
8. `CONSISTENCY LOCKS` — restate exact identity constraints and exclusions.

Include exact text, logos, symbols, or colors only when supplied or essential. Put required text in quotation marks, preserve spelling and capitalization, and keep it identical across views. Do not invent branding. Avoid labels by default because generated typography can introduce artifacts; if labels aid a technical sheet or the user requests them, use only simple labels such as `FRONT VIEW`.

## Visual Standard

Default to:

- one isolated prop only, with no people, hands, characters, unrelated accessories, or environmental staging;
- a seamless neutral medium-to-dark grey background shared by all panels;
- broad, soft, even studio lighting with restrained highlights and soft contact shadows;
- photorealistic product/reference photography, sharp detail, deep depth of field, and accurate materials;
- a clean landscape composition with a view-count-appropriate grid, no crop, no overlap, no decorative border, and generous margins;
- no motion blur, atmosphere, dramatic depth of field, or cinematic scene lighting.

Adapt the rendering style when requested, but retain the neutral reference-sheet composition and cross-view consistency unless the user explicitly changes them.

## Reference Images

Use reference images as visual evidence. Describe what is visible rather than making unsupported claims about exact dimensions or hidden construction. If only one angle is provided, infer unseen views conservatively and maintain the visible design language. Use the platform's reference token, such as `@image_1`, when one is available; otherwise say `the supplied reference image`.

If multiple images show the same prop, reconcile them into one canonical design. If they conflict materially, prioritize the image the user identifies as primary; otherwise preserve the clearest shared features and avoid silently combining incompatible variants.

## Final Check

Before returning the prompt, verify:

- one prop identity appears in every panel;
- the view count is justified by the prop rather than a fixed default;
- the chosen views reveal all identity-critical geometry and eliminate avoidable surface guessing;
- opposite sides are both present when they differ materially;
- the top and underside are present when they carry important construction, controls, tread, or attachments;
- every panel remains large and sharp enough to be useful at the selected count;
- panel orientation and placement are unambiguous;
- the background is neutral grey and consistent;
- framing is orthographic or near-orthographic, sharp, and uncropped;
- materials, markings, and wear agree across views;
- exact text is quoted and spelled consistently;
- exclusions prevent people, extra props, duplicate objects within panels, and environmental clutter.
