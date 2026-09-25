---
name: prop-generation
description: >-
  Write detailed JSON image prompts for consistent multi-view prop and product reference
  sheets on a #504f50 studio background, choosing a tight set of views that explain the
  object for video and ad workflows (jewellery often 2-view loop + clasp; otherwise 3-4).
  Outputs prompt text only and never generates the image itself. Use whenever a physical
  product or object must appear in AI images or video — jewellery, apparel, footwear,
  cosmetics, packaging, gadgets, toys, appliances, tools, vehicles, furniture, or any
  other non-character item — including for a product ad, campaign, or video clip. Also use
  to design or remix a product, turn a concept or reference photo into front, side, rear,
  three-quarter, or detail views, or lock a product's exact appearance across shots.
  Trigger on "prompt for my product", "reference sheet for this necklace", or an uploaded
  product photo that needs consistent views. Has an animated mode for stylized 3D
  projects.
---

# Prop Generation

Write one image-generation prompt for a multi-view prop/product reference sheet for downstream image and video identity.

**Output is a JSON image prompt only.** Return one valid JSON object in a `json` code block and stop. Do not generate, render, preview, or offer to generate the image.

Use the structured JSON style in [references/prompt-blueprints.md](references/prompt-blueprints.md). Emit parseable JSON with double-quoted keys and strings; no comments, markdown inside the object, trailing commas, or unresolved placeholders. Omit irrelevant fields instead of filling them with guesses. Keep `final_generation_instruction` consistent with the structured fields.

## Animated mode

Use this mode when the project is stylized 3D animation (the `animated-video-production` skill, or a request for Pixar-, DreamWorks- or feature-animation-style characters, places or props). The layout rules below still apply: one landscape image, the same panels and separators. What changes:

- **Render** the prop as feature-animation CG: slightly simplified, appealing shapes, clear readable colour, soft 3D shading, and materials that still read (glossy metal, wax paper, cardboard). Replace the `studio photograph` wording with this.
- **Scale:** state its size against a character ("about the length of the cat's body") so scenes keep it consistent.
- **Where the prompt goes:** in an animated project, save the prompt to the asset's `prompts/` folder. It may then be generated with the `flow` skill; the prompt-only rule above covers standalone requests.

## Defaults

- **3 views** by default, **4 max** (unless the user asks for more)
- **Jewellery exception:** when the user asks for 2 views, or a necklace/bracelet is defined by its silhouette plus clasp, use **2 views** (full loop left, clasp closeup right). Do not pad to 3.
- **One output image**, always a 16:9 landscape composite sheet; each view occupies one cell on the same canvas, never a separate image or file. Layout: 2 → 1×2 row; 3 → 1×3 row; 4 → 2×2 grid. Use thin solid `#d1d1d2` separators between cells (one vertical and one horizontal for a 2×2 grid).
- Seamless **`#504f50`** studio background in every cell
- Soft product lighting, subtle contact shadows, orthographic / near-orthographic, deep focus
- In the JSON image prompt, show the intended photographic look through material response, lens geometry, contact shadows, sharpness, and exposure rather than using `realistic`, `photorealistic`, or `cinematic` as a style label. Default to neutral studio light; no amber glow or sunset-style rim light unless requested.
- **No orientation labels, captions, view names, or overlaid text** — only text that exists on the prop
- One prop only: no people, hands, environment, or extra objects

## Workflow

1. Identify the hero prop and how it will appear on camera.
2. Define one canonical design: shape, proportions, colors, materials, construction, markings, wear, asymmetries.
3. Pick the smallest view set that covers surfaces the ad/video will show (see view rules). Use the jewellery 2-view exception when applicable.
4. Load [references/prompt-blueprints.md](references/prompt-blueprints.md) and fill its JSON structure.
5. Final check. Return only the prompt unless the user asks for explanation.

Infer restrained design choices. Ask only when a missing choice would change the prop's identity.

## View selection

Choose from geometry and on-camera needs — not a fixed category template.

| Include | When |
|---|---|
| Front + side + rear (or ¾) | Default 3-view set |
| Both sides | Lateral faces differ and the shot shows it |
| Top | Controls, openings, or layout the audience sees |
| Bottom | Only if the underside is the subject (e.g. shoe outsole) |
| Three-quarter | Connects orthographic surfaces; supporting, not beauty hero |
| Detail | Feature unreadable at full-object scale, within the 4-view cap |

Skip surfaces the audience never sees (blender underside, plain appliance base). Prefer fewer views when unsure.

## Hard rules

- All panels = **one physical object**. Same design, proportions, colors, materials, markings, wear, component placement.
- Each panel must show a **clearly different camera axis or a justified detail crop**. Specify the strict orientation, the direction the front or toe points, which surfaces are visible, and which are hidden. Do not let three-quarter approximations replace side, top, or rear views.
- Exact left/right for asymmetries; preserve through rotation.
- Consistent scale and camera height; each panel centered, no overlap or crop.
- Reference image: preserve silhouette, palette, materials, branding, wear unless asked to change. Scoped remix: name the change, lock everything else.
- Quote on-prop text/logos exactly. With no supplied branding, a product gets a plausible fictional brand (wordmark, product name, short descriptor) written out in the prompt, never a blank or unbranded package.
- For ad work: this sheet is the product identity source. A worn/in-use still and a **visually distinct** alternative (different form, not just worse condition) are separate assets when the script needs them.

## JSON fields (order)

1. `prompt_type`, `objective`, and `reference_fidelity` when a reference exists
2. `canonical_prop_design`, `canvas_and_layout`, and ordered `views`
3. `background_and_lighting`, `camera_and_optics`, `material_detail`
4. `consistency_locks`, `negative_prompt`, `final_generation_instruction`

## Final check

- One 16:9 landscape output image containing every view in separate cells; 2 views for jewellery loop + clasp when appropriate, otherwise 3–4; `#d1d1d2` separators
- Every view earns its place for on-camera surfaces or identity
- `#504f50` background in every cell; orthographic/near-orthographic; sharp; uncropped
- Materials, markings, wear agree across views
- Distinct silhouettes and visible surfaces prove the chosen orientations; no repeated near-identical views. Check the JSON for leftover object names or parts copied from a different blueprint example.
- No labels; only on-prop text; no people or environment
