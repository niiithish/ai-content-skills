---
name: character-generation
description: Write JSON image prompts for three-panel character reference sheets — headless full-body front, full-body back, and a large 3/4 close portrait — on a #504f50 studio background. Photoreal by default, with an animated mode for stylized 3D characters and animals. Outputs prompt text only. Use whenever a person or recurring character must appear in AI images or video and needs a consistent face, hair, wardrobe and accessories across shots: an AI model, spokesmodel, brand model, creator, influencer, UGC creator, presenter, avatar, persona, or an animated character. Also use to design or remix a character. Trigger on "I want an AI model", "give me a model for my brand", "creator for this ad", "character sheet", or "character for a jewelry ad".
---

# Character Generation

Write one image-generation prompt for a wide landscape character reference sheet: wardrobe (front + back) + face identity for downstream image and video work.

**Output is a JSON image prompt only.** Return one valid JSON object in a `json` code block and stop. Do not generate, render, preview, or offer to generate the image. A required smile variant is a second, separate JSON object in its own `json` code block.

Use the structured JSON style in [references/prompt-blueprint.md](references/prompt-blueprint.md). Emit parseable JSON with double-quoted keys and strings; no comments, markdown inside the object, trailing commas, or unresolved placeholders. Omit irrelevant fields instead of filling them with guesses. Keep `final_generation_instruction` consistent with the structured fields.

## Animated mode

Use this mode when the project is stylized 3D animation (the `animated-video-production` skill, or a request for Pixar-, DreamWorks- or feature-animation-style characters, places or props). The layout rules below still apply: one landscape image, the same panels and separators. What changes:

- **Render** the character as sculpted, slightly stylized feature-animation CG: appealing proportions, large expressive eyes with catch-lights, shaped hair or groomed fur, simplified skin with soft subsurface shading. Replace the photoreal skin rules (pores, oil, fine lines) and `studio photograph` wording with this. Keep the studio sheet neutral and evenly lit.
- **Animals and creatures** use the same three panels: headless front body, back body, and a large 3/4 head portrait. Describe fur colour, pattern and markings concretely, since they are the identity.
- **A group** of near-identical characters (a litter of kittens, a squad) can be one lineup sheet of complete characters instead of three panels. Say so in the prompt, and in every scene prompt that uses it.
- **Scale:** state the character's size against a familiar reference ("a small young cat, back at an adult's shin"). Scene prompts reuse it.
- **Where the prompt goes:** in an animated project, save the prompt to the asset's `prompts/` folder. It may then be generated with the `flow` skill; the prompt-only rule above covers standalone requests.

## Composition (always)

Exactly **one output image**: a single 16:9 landscape sheet containing three panels left → right, separated by thin solid `#d1d1d2` vertical lines. Never render or request three separate images, files, canvases, or sequential outputs for the three views. No portrait-orientation canvas. Never two-panel. Never put a face on a full-body panel.

| Panel | ~Width | Content |
|---|---|---|
| **1 — Front body** | ~28–32% | Full-body **front**, standing, head **fully removed**. Natural body under clothes (shoulders, arms, hands, legs, feet). The garment collar is the topmost visible edge: show `#504f50` background directly above and inside the opening, with no exposed neck skin, chin, cut stump, mannequin, or floating features. Outfit + footwear fully visible, uncropped. |
| **2 — Back body** | ~28–32% | Full-body **back**, same outfit and pose language. **No face.** Back-of-head / hair from behind is allowed so silhouette and hair length read; no profile or three-quarter face. Outfit + footwear fully visible, uncropped. |
| **3 — Portrait** | ~36–44% | Large shoulder-up identity in a visible **3/4 head turn** unless the user asks front-facing: rotate roughly 25–35° from camera, keep both eyes visible, and make one cheek and ear more visible. Same upper outfit as body panels. No hands or arms in frame. |

**Why this layout (do not weaken):** On wide full-body figures the face is small and soft — models copy that bad face into wides. Headless bodies leave **only** the large portrait as the face source.

**Smile / teeth (when needed):** If the character will smile in video or the user asks for a smile, also write a **second prompt** that is the same sheet with only the portrait expression changed to a natural smile (same face, mouth, and teeth locked). Do not invent teeth on a single neutral sheet and hope video invents a matching smile later. Default single sheet = neutral closed mouth unless the user specifies a smiling character.

Shared: seamless **`#504f50`** studio backdrop in every panel, soft frontal or side studio light (~5500K), photoreal reference photography — boring sheet on purpose (no cinema grade, film grain, or heavy look).

In the JSON image prompt, describe the visible cues—skin texture, hair strands, fabric weave, neutral light, and camera framing—instead of using `realistic`, `photorealistic`, or `cinematic` as a style label. Keep amber sunset glow and warm rim light out of the default studio setup.

## Workflow

1. Identity: face structure, hair, eyes, age range, expression. Specificity from bone structure and hair — not moles or other discrete marks. Portrait default slight **3/4**. Ethnicity unspecified → default white American; state skin/hair/eye concretely, not as a nationality label. Reference image always wins.
2. Purpose check: if they model a product, keep product zones bare (jewellery → bare ears/neck/wrists/fingers).
3. One canonical outfit: every garment, layer, color, material, opacity/weight, fit, graphic, accessory, footwear — identical across all panels (upper match on portrait; full match front/back).
4. Load [references/prompt-blueprint.md](references/prompt-blueprint.md) and fill the JSON object with the locked details.
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
- **Portrait angle:** default visible 3/4 turn, roughly 25–35° from camera, with asymmetric cheek and ear visibility and both eyes readable (not frontal passport symmetry).

**Body panels**
- Real body volume and limbs (not a flat lay, not a hollow ghost-mannequin void). Hands relaxed at sides unless the user specifies a pose.
- Head removed on the **front** panel completely — collar is the highest visible edge, with background directly above and inside it; no exposed neck skin or cut-off face residue.
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

## JSON fields (order)

1. `prompt_type`, `objective`, and `reference_fidelity` when references exist
2. `canvas` and `panels` in left-to-right order
3. `identity`, `wardrobe`, and `consistency_locks`
4. `background_and_lighting`, `camera_and_style`, `negative_prompt`
5. `final_generation_instruction`

## Final check

- One 16:9 landscape output image containing exactly three panels; left→right: headless front, back (no face), large 3/4 portrait; `#d1d1d2` separators
- No face on either body panel; front head and neck fully gone, with no skin above the collar
- Portrait: shoulder-up visible 25–35° 3/4 turn (unless front requested), one cheek/ear more visible, both eyes readable, no hands/arms; face matches reference if any; catch-light in eyes
- No moles/beauty marks unless requested or on reference; natural no-makeup skin; upper outfit matches body panels
- Fabrics opaque + weight named; light frontal/side; show-through in exclusions
- Product model: bare of jewellery, locked
- Same `#504f50` backdrop all panels; no props, scenery, labels, or extra people; sheet stays boring (no cinema grade)
