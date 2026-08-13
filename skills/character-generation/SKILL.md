---
name: character-generation
description: Write image prompts for photorealistic three-panel character reference sheets — headless full-body front, full-body back, and a large 3/4 close portrait — on a neutral dark-grey studio background. Outputs prompt text only and never generates the image. Use whenever a person must appear in AI images or video, including an AI model, virtual model, spokesmodel, brand model, creator, influencer, UGC creator, presenter, talent, avatar, persona, or any human character, for a product ad, jewellery or fashion shoot, campaign, or video clip. Also use to design or remix a character, or to lock a consistent face, hair, wardrobe, and accessories across shots. Trigger on "I want an AI model", "give me a model for my brand", "creator for this ad", "character for a jewelry ad", or a bare mention of a model, girl, guy, or person who needs generating.
---

# Character Generation

Write one image-generation prompt for a wide landscape character reference sheet: wardrobe (front + back) + face identity for downstream image and video work.

**Output is prompt text only.** Put the finished prompt in a code block and stop. Do not generate, render, preview, or offer to generate the image.

## Composition (always)

Exactly **three panels** left → right on one wide landscape sheet (~16:9), thin clean vertical dividers. Never two-panel. Never put a face on a full-body panel.

| Panel | ~Width | Content |
|---|---|---|
| **1 — Front body** | ~28–32% | Full-body **front**, standing, head **fully removed**. Natural body under clothes (shoulders, arms, hands, legs, feet). Empty neck opening — no head, face, hair, neck stump, mannequin, or floating features. Outfit + footwear fully visible, uncropped. |
| **2 — Back body** | ~28–32% | Full-body **back**, same outfit and pose language. **No face.** Back-of-head / hair from behind is allowed so silhouette and hair length read; no profile or three-quarter face. Outfit + footwear fully visible, uncropped. |
| **3 — Portrait** | ~36–44% | Large shoulder-up identity in slight **3/4 head turn** (not dead-on frontal) unless the user asks front-facing. Same upper outfit as body panels. No hands or arms in frame. |

**Why this layout (do not weaken):** On wide full-body figures the face is small and soft — models copy that bad face into wides. Headless bodies leave **only** the large portrait as the face source.

**Smile / teeth (when needed):** If the character will smile in video or the user asks for a smile, also write a **second prompt** that is the same sheet with only the portrait expression changed to a natural smile (same face, mouth, and teeth locked). Do not invent teeth on a single neutral sheet and hope video invents a matching smile later. Default single sheet = neutral closed mouth unless the user specifies a smiling character.

Shared: seamless **neutral dark-grey / charcoal** studio backdrop, soft frontal or side studio light (~5500K), photoreal reference photography — boring sheet on purpose (no cinema grade, film grain, or heavy look).

## Workflow

1. Identity: face structure, hair, eyes, age range, expression. Specificity from bone structure and hair — not moles or other discrete marks. Portrait default slight **3/4**. Ethnicity unspecified → default white American; state skin/hair/eye concretely, not as a nationality label. Reference image always wins.
2. Purpose check: if they model a product, keep product zones bare (jewellery → bare ears/neck/wrists/fingers).
3. One canonical outfit: every garment, layer, color, material, opacity/weight, fit, graphic, accessory, footwear — identical across all panels (upper match on portrait; full match front/back).
4. Load [references/prompt-blueprint.md](references/prompt-blueprint.md) and write sections in that order.
5. If a smile will be needed later and the user did not already lock one, note that a second smile-portrait sheet should be generated; write it when asked or when the brief clearly requires smiling performance.
6. Final check (below). Return only the prompt unless the user asks for explanation.

Infer restrained defaults. Ask only when a missing choice would change identity.

## Hard rules

**Identity**
- Supplied reference = identity source. Preserve face, hair, age, and any discrete marks actually on the reference. No beautify/age/gender redesign unless requested.
- **Face only on panel 3.** Panel 1: no head at all. Panel 2: no face (rear hair OK).
- **No moles** (or beauty marks, scars, freckle clusters, tattoos, piercings) unless the user or reference has them — with exact placement.
- **Natural bare skin is wanted.** No-makeup look: visible pores, natural oil/shine, fine lines, subtle uneven tone, light texture variation — real human face, not beauty-filter smooth or airbrushed. Eyes need a small catch-light so the face reads alive in later video.
- Default identity (when unspecified): white American; concrete visible features only.
- **Portrait angle:** default slight 3/4 head turn (not frontal passport shot).

**Body panels**
- Real body volume and limbs (not a flat lay, not a hollow ghost-mannequin void). Hands relaxed at sides unless the user specifies a pose.
- Head removed on the **front** panel completely — clean empty collar/neck opening, no cut-off face residue.
- Back panel: same wardrobe and body; no readable face.
- Full length neck-opening-to-footwear (front) / head-or-hair-to-footwear (back), generous margins, no crop.

**Outfit**
- One outfit, identical across panels (front/back full; portrait matches upper: neckline, layers, colors, materials, graphics, asymmetries).
- Every fabric: name weight and **opaque** (especially light/thin tops). Frontal or side light — no backlight through fabric. Exclusions must name show-through (nipples, underwear outline, translucent stretch).
- No sheer/mesh/lingerie-style fabrics; get delicacy from cut and drape with lining stated.
- Product-modelling character: **no jewellery**. Lock bare ears/neck/wrists/fingers. Otherwise at most one or two small pieces that serve the character.
- Quote required logos/text exactly; do not invent branding.

**Minors**
- Character sheet is the wrong asset for a minor. Skip the sheet; put a text description in the video prompt. Do not upload real photos of minors as references. If asked for a young-girl sheet, warn that image models often refuse before generating.

## Prompt sections (order)

1. `PANEL 1 — FRONT BODY, head removed`
2. `PANEL 2 — BACK BODY, no face`
3. `PANEL 3 — PORTRAIT (large head)`
4. `IDENTITY + WARDROBE LOCKS`
5. `LAYOUT`
6. `BACKGROUND + LIGHT`
7. `CAMERA + FRAMING`
8. `STYLE + DETAIL`
9. `EXCLUSIONS`

## Final check

- Three panels only; left→right: headless front, back (no face), large 3/4 portrait
- No face on either body panel; front head fully gone
- Portrait: shoulder-up slight 3/4 (unless front requested), no hands/arms; face matches reference if any; catch-light in eyes
- No moles/beauty marks unless requested or on reference; natural no-makeup skin; upper outfit matches body panels
- Fabrics opaque + weight named; light frontal/side; show-through in exclusions
- Product model: bare of jewellery, locked
- Same dark-grey backdrop all panels; no props, scenery, labels, or extra people; sheet stays boring (no cinema grade)
