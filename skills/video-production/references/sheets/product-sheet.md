# Product sheet

The layout every style uses for a multi-view product or prop reference sheet. In a video, only the client's product gets one (`video-plan` step 7), made from its real photos with `make.py sheet ... --ref`, never from a description. It is written for photoreal; the style skill's `references/product.md` says what changes.

Write one JSON object in the structure of [product-blueprint.md](product-blueprint.md). Emit parseable JSON with double-quoted keys and strings; no comments, markdown inside the object, trailing commas, or unresolved placeholders. Omit irrelevant fields instead of filling them with guesses. Keep `final_generation_instruction` consistent with the structured fields.

**Where the prompt goes.** In a project, save it to the asset's `prompts/` folder and make the sheet with `make.py sheet` (`video-production`). For a one-off request outside a project, return the JSON in a `json` code block and stop; don't generate it unless asked.

## Defaults

- **3 views** by default, **4 max** (unless the user asks for more)
- **Jewellery exception:** when the user asks for 2 views, or a necklace/bracelet is defined by its silhouette plus clasp, use **2 views** (full loop left, clasp closeup right). Do not pad to 3.
- **One output image**, always a 16:9 landscape composite sheet; each view occupies one cell on the same canvas, never a separate image or file. Layout: 2 → 1×2 row; 3 → 1×3 row; 4 → 2×2 grid. Cells butt edge to edge like separate photos placed side by side: no drawn divider, separator line, gap, gutter or border. The only boundary is where one shot ends and the next begins.
- Seamless **`#504f50`** studio background in every cell
- Soft product lighting, subtle contact shadows, orthographic / near-orthographic, deep focus
- In the JSON image prompt, show the intended photographic look through material response, lens geometry, contact shadows, sharpness, and exposure rather than using `realistic`, `photorealistic`, or `cinematic` as a style label. Default to neutral studio light; no amber glow or sunset-style rim light unless requested.
- **No orientation labels, captions, view names, or overlaid text** — only text that exists on the prop
- One prop only: no people, hands, environment, or extra objects

## Workflow

1. Identify the hero prop and how it will appear on camera.
2. Define one canonical design: shape, proportions, colors, materials, construction, markings, wear, asymmetries.
3. Pick the smallest view set that covers surfaces the ad/video will show (see view rules). Use the jewellery 2-view exception when applicable.
4. Load [product-blueprint.md](product-blueprint.md) and fill its JSON structure.
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

- One 16:9 landscape output image containing every view in separate cells; 2 views for jewellery loop + clasp when appropriate, otherwise 3–4; cells butted edge to edge, no divider lines or gutters
- Every view earns its place for on-camera surfaces or identity
- `#504f50` background in every cell; orthographic/near-orthographic; sharp; uncropped
- Materials, markings, wear agree across views
- Distinct silhouettes and visible surfaces prove the chosen orientations; no repeated near-identical views. Check the JSON for leftover object names or parts copied from a different blueprint example.
- No labels; only on-prop text; no people or environment
