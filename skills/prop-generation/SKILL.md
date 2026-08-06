---
name: prop-generation
description: Write detailed, model-ready image prompts for consistent multi-view prop and product reference sheets on a neutral grey studio background, choosing a tight set of 3-4 views that explain the object for video and ad workflows. Outputs prompt text only and never generates the image itself. Use whenever a physical product or object must appear in AI images or video — jewellery, apparel, footwear, cosmetics, packaging, gadgets, toys, appliances, tools, vehicles, furniture, or any other non-character item — including for a product ad, campaign, or video clip. Also use to design or remix a product, turn a concept or reference photo into front, side, rear, three-quarter, or detail views, or lock a product's exact appearance across shots. Trigger on "prompt for my product", "reference sheet for this necklace", or an uploaded product photo that needs consistent views.
---

# Prop Generation

Write one image-generation prompt for a multi-view prop/product reference sheet for downstream image and video identity.

**Output is prompt text only.** Put the finished prompt in a code block and stop. Do not generate, render, preview, or offer to generate the image.

## Defaults

- **3 views** by default, **4 max** (unless the user asks for more)
- Layout: 3 → one horizontal row; 4 → 2×2 grid
- Seamless **neutral medium-to-dark grey** studio background
- Soft product lighting, subtle contact shadows, orthographic / near-orthographic, deep focus
- **No orientation labels, captions, view names, or overlaid text** — only text that exists on the prop
- One prop only: no people, hands, environment, or extra objects

## Workflow

1. Identify the hero prop and how it will appear on camera.
2. Define one canonical design: shape, proportions, colors, materials, construction, markings, wear, asymmetries.
3. Pick the smallest 3–4 view set that covers surfaces the ad/video will show (see view rules).
4. Load [references/prompt-blueprints.md](references/prompt-blueprints.md) and fill the matching blueprint.
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
- Exact left/right for asymmetries; preserve through rotation.
- Consistent scale and camera height; each panel centered, no overlap or crop.
- Reference image: preserve silhouette, palette, materials, branding, wear unless asked to change. Scoped remix: name the change, lock everything else.
- Quote on-prop text/logos exactly; do not invent branding.
- For ad work: this sheet is the product identity source. A worn/in-use still and a **visually distinct** alternative (different form, not just worse condition) are separate assets when the script needs them.

## Prompt sections (order)

1. `PROP REFERENCE SHEET` — object, view count, layout, purpose
2. `CANONICAL PROP DESIGN`
3. `VIEWS` — each panel orientation and why
4. `LAYOUT` — grid, scale, margins, no labels
5. `BACKGROUND + LIGHT` — grey studio, soft light, contact shadows
6. `CAMERA + OPTICS` — orthographic, normal lens, deep focus
7. `MATERIAL + DETAIL`
8. `CONSISTENCY LOCKS` + exclusions

## Final check

- One prop identity in every panel; 3–4 views only
- Every view earns its place for on-camera surfaces or identity
- Neutral grey background; orthographic/near-orthographic; sharp; uncropped
- Materials, markings, wear agree across views
- No labels; only on-prop text; no people or environment
