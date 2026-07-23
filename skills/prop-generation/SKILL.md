---
name: prop-generation
description: Create detailed, model-ready image prompts for consistent multi-view prop reference sheets on a neutral grey studio background, choosing a tight set of 3-4 views that explain the object for video and ad workflows. Use when the user wants to design, generate, visualize, or remix a product, object, footwear item, toy, appliance, tool, vehicle, weapon, furniture item, or other non-character prop; turn a written concept or reference image into front, side, rear, three-quarter, or detail views; or create an orthographic prop turnaround for AI image or video workflows.
---

# Prop Generation

Create one standalone image-generation prompt for a clean, consistent, multi-view prop reference sheet. Optimize the sheet for reuse as an identity reference in later image generation, photo remixing, and AI video work. Keep the sheet tight: use 3 views by default and 4 only when a fourth genuinely earns its place.

## Workflow

1. Identify the single hero prop and its intended use.
2. Extract or infer a canonical design before describing individual views: shape, proportions, colors, materials, construction, controls, markings, wear, and distinctive features.
3. Audit the prop's visible surfaces and identity-critical features, then select the smallest view set (3 by default, at most 4) that explains the surfaces a downstream video or ad will actually show.
4. Read [references/prompt-blueprints.md](references/prompt-blueprints.md) and use the matching dynamic layout blueprint.
5. Write the final prompt in the required section order.
6. Check every view against the canonical design and remove contradictions.

Do not ask follow-up questions when a sensible design can be inferred. Make restrained, coherent choices and state them directly in the prompt. Ask only when a missing choice would substantially change the prop's identity.

## Select Views (3-4 Max)

Choose views from the prop's geometry, asymmetry, and how the prop will be shown on camera—not from a fixed category template. Cap the sheet at 4 views and default to 3. A downstream video or ad rarely shows every surface, so only include a view of a surface the audience will actually see or that carries the prop's identity. Before choosing the count, list mentally which surfaces the shot needs and drop any view a viewer would never notice (for example, the underside of a blender, the bottom of an appliance, or a plain rear face).

- Use **3 views** by default: usually front, one strict side, and either the rear or a front three-quarter—whichever the prop's on-camera presentation needs.
- Use **4 views** only when one extra panel resolves a genuinely important, on-camera ambiguity, such as a differing second side or a top that shows controls or openings the audience will see.
- Choose **both sides** only when lateral/medial faces differ in a way the shot will reveal (controls, doors, graphics, wear, construction).
- Choose **top** only when controls, openings, or surface layout matter to the shot.
- Skip **bottom/undercarriage** views by default. Include one only when the underside is the actual subject (for example, a shoe outsole in a product shot). Do not add a bottom view for props whose underside never appears on camera, like a blender, kettle, or appliance base.
- Choose a **front or rear three-quarter** when an integrated 3D view helps connect the orthographic surfaces. Treat it as supporting geometry, not a dramatic beauty shot.
- Choose a **detail view** only for a feature that cannot read at full-object scale, and only within the 4-view cap. A detail does not replace a required orientation view.
- Honor an explicit view count or layout from the user, but never exceed 4 views unless the user directly asks for more.

Run a coverage check before writing: does the view set show the surfaces the downstream video or ad will actually put on screen, plus the prop's defining components and any asymmetry the shot reveals? Omit any orientation the audience will never see or that is genuinely redundant. When in doubt, prefer fewer views.

Use true front, strict side, true rear, top, and bottom views whenever they are selected. Keep three-quarter views controlled and natural. Avoid dramatic foreshortening, wide-angle distortion, or a collage of unrelated beauty shots.

## Choose a Readable Layout

Use a landscape canvas and select a grid that keeps every full-object view large enough to inspect:

- 3 views: one horizontal row.
- 4 views: 2x2 grid.

Arrange views in a logical rotation or inspection sequence. Give every panel its own clear area, use consistent object scale, and allow unusually long or tall orientations to use their cell efficiently. Do not enlarge a three-quarter hero view so much that it makes technical views secondary. Do not add orientation labels, captions, view names (such as "FRONT VIEW"), arrows, dimension lines, or any other overlaid text. The only text allowed is text that physically exists on the prop itself.

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
3. `VIEWS` — state the selected count (3-4) and define each panel's orientation and why the shot needs it.
4. `LAYOUT` — define the matching grid (1x3 or 2x2), panel positions, spacing, consistent scale, margins, and dividers. No labels.
5. `BACKGROUND + LIGHT` — specify a seamless neutral medium-to-dark grey studio background, soft neutral product lighting, subtle contact shadows, and no environment.
6. `CAMERA + OPTICS` — specify orthographic or near-orthographic framing, a normal lens character, rectilinear edges, deep focus, and no perspective distortion.
7. `MATERIAL + DETAIL` — explain how each surface responds to light and how fine details should render.
8. `CONSISTENCY LOCKS` — restate exact identity constraints and exclusions.

Include exact text, logos, symbols, or colors only when they physically exist on the prop or are essential. Put required text in quotation marks, preserve spelling and capitalization, and keep it identical across views. Do not invent branding. Never add orientation labels, view names, captions, or any other overlaid text to the sheet: the only text that may appear is text that is actually on the prop.

## Visual Standard

Default to:

- one isolated prop only, with no people, hands, characters, unrelated accessories, or environmental staging;
- a seamless neutral medium-to-dark grey background shared by all panels;
- broad, soft, even studio lighting with restrained highlights and soft contact shadows;
- photorealistic product/reference photography, sharp detail, deep depth of field, and accurate materials;
- a clean landscape composition with a 3-view row or 4-view 2x2 grid, no crop, no overlap, no decorative border, no overlaid text or labels, and generous margins;
- no motion blur, atmosphere, dramatic depth of field, or cinematic scene lighting.

Adapt the rendering style when requested, but retain the neutral reference-sheet composition and cross-view consistency unless the user explicitly changes them.

## Reference Images

Use reference images as visual evidence. Describe what is visible rather than making unsupported claims about exact dimensions or hidden construction. If only one angle is provided, infer unseen views conservatively and maintain the visible design language. Use the platform's reference token, such as `@image_1`, when one is available; otherwise say `the supplied reference image`.

If multiple images show the same prop, reconcile them into one canonical design. If they conflict materially, prioritize the image the user identifies as primary; otherwise preserve the clearest shared features and avoid silently combining incompatible variants.

## Final Check

Before returning the prompt, verify:

- one prop identity appears in every panel;
- the sheet uses 3-4 views, never more (unless the user explicitly asked for more);
- every included view shows a surface the downstream video or ad will actually put on camera or that carries the prop's identity;
- no view is included for a surface the audience will never see (for example, a blender or appliance underside);
- opposite sides appear only when they differ in a way the shot reveals;
- every panel remains large and sharp enough to be useful at the selected count;
- panel orientation and placement are unambiguous;
- the background is neutral grey and consistent;
- framing is orthographic or near-orthographic, sharp, and uncropped;
- materials, markings, and wear agree across views;
- the only text on the sheet is text physically present on the prop; there are no orientation labels, view names, or captions;
- exclusions prevent people, extra props, duplicate objects within panels, and environmental clutter.
