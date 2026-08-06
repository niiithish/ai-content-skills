---
name: character-generation
description: Write image prompts for photorealistic two-panel character reference sheets — an invisible-body outfit on the left, a matching shoulder-up identity portrait on the right — on a neutral dark-grey studio background. Outputs prompt text only and never generates the image. Use whenever a person must appear in AI images or video, including an AI model, virtual model, spokesmodel, brand model, creator, influencer, UGC creator, presenter, talent, avatar, persona, or any human character, for a product ad, jewellery or fashion shoot, campaign, or video clip. Also use to design or remix a character, or to lock a consistent face, hair, wardrobe, and accessories across shots. Trigger on "I want an AI model", "give me a model for my brand", "creator for this ad", "character for a jewelry ad", or a bare mention of a model, girl, guy, or person who needs generating.
---

# Character Generation

Write one image-generation prompt for a landscape character reference sheet: identity + wardrobe for downstream image and video work.

**Output is prompt text only.** Put the finished prompt in a code block and stop. Do not generate, render, preview, or offer to generate the image.

## Composition (always)

Exactly two panels on a wide 16:9 landscape sheet with a thin vertical divider:

| Panel | Content |
|---|---|
| **Left (~40–45%)** | Full outfit neck-to-footwear on an **invisible body**. No head, skin, limbs, mannequin, hanger, or stand. Realistic worn volume — not a flat lay. Fully visible, uncropped. |
| **Right (~55–60%)** | Large shoulder-up identity portrait in a slight **3/4 head turn** (not dead-on frontal) unless the user asks front-facing. Same upper outfit as left. No hands or arms in frame. |

Shared: seamless **neutral dark-grey / charcoal** studio backdrop, soft frontal or side studio light (~5500K), photoreal reference photography.

## Workflow

1. Identity: face structure, hair, eyes, age range, expression. Specificity from bone structure and hair — not moles or other discrete marks. Portrait default: slight **3/4** (face turned a little), not straight-on — models read identity better and the sheet stays more usable for video. Ethnicity unspecified → default white American; state skin/hair/eye concretely, not as a nationality label. Reference image always wins.
2. Purpose check: if she models a product, keep product zones bare (jewellery → bare ears/neck/wrists/fingers).
3. One canonical outfit: every garment, layer, color, material, opacity/weight, fit, graphic, accessory, footwear.
4. Load [references/prompt-blueprint.md](references/prompt-blueprint.md) and write sections in that order.
5. Final check (below). Return only the prompt unless the user asks for explanation.

Infer restrained defaults. Ask only when a missing choice would change identity.

## Hard rules

**Identity**
- Supplied reference = identity source. Preserve face, hair, age, and any discrete marks actually on the reference. No beautify/age/gender redesign unless requested.
- **No moles** (or beauty marks, scars, freckle clusters, tattoos, piercings) unless the user or reference has them — with exact placement. These become continuity liabilities.
- **Natural bare skin is wanted.** No-makeup look: visible pores, natural oil/shine, fine lines, subtle uneven tone, light texture variation — real human face, not beauty-filter smooth or airbrushed. Small normal skin variation is fine; discrete invented marks are not. Eyes need a small catch-light so the face reads alive in later video.
- Default identity (when unspecified): white American; concrete visible features only.
- **Portrait angle:** default slight 3/4 head turn (not frontal passport shot). Keep the left outfit panel straight-on full-length so wardrobe reads cleanly.

**Outfit**
- One outfit, identical upper detail in both panels (neckline, layers, colors, materials, graphics, asymmetries).
- Every fabric: name weight and **opaque** (especially light/thin tops). Frontal or side light — no backlight through fabric. Exclusions must name show-through (nipples, underwear outline, translucent stretch).
- No sheer/mesh/lingerie-style fabrics; get delicacy from cut and drape with lining stated.
- Product-modelling character: **no jewellery**. Lock bare ears/neck/wrists/fingers. Otherwise at most one or two small pieces that serve the character.
- Quote required logos/text exactly; do not invent branding.

**Minors**
- Character sheet is the wrong asset for a minor. Skip the sheet; put a text description in the video prompt. Do not upload real photos of minors as references. If asked for a young-girl sheet, warn that image models often refuse before generating.

## Prompt sections (order)

1. `SUBJECT (RIGHT panel — large head)`
2. `LEFT panel — OUTFIT ONLY, ghost-mannequin`
3. `IDENTITY + WARDROBE LOCKS`
4. `LAYOUT`
5. `BACKGROUND + LIGHT`
6. `CAMERA + FRAMING`
7. `STYLE + DETAIL`
8. `EXCLUSIONS`

## Final check

- Left: full outfit, zero anatomy/mannequin, worn volume not flat lay
- Right: shoulder-up slight 3/4 (unless front requested), no hands/arms; face matches reference if any; catch-light in eyes
- No moles/beauty marks (unless requested or on reference); natural no-makeup skin texture kept; upper outfit matches left exactly
- Fabrics opaque + weight named; light frontal/side; show-through in exclusions
- Product model: bare of jewellery, locked
- Same dark-grey backdrop both panels; no props, scenery, labels, or extra people
