# Character sheet

The layout every style uses for a character reference sheet: wardrobe (front + back) and face identity for every later still and clip. It is written for photoreal, the default; the style skill's `references/characters.md` says what changes (render, material, scale).

Write one JSON object in the structure of [character-blueprint.md](character-blueprint.md). Emit parseable JSON with double-quoted keys and strings; no comments, markdown inside the object, trailing commas, or unresolved placeholders. Omit irrelevant fields instead of filling them with guesses. Keep `final_generation_instruction` consistent with the structured fields. A required smile variant is a second, separate JSON object.

**Where the prompt goes.** In a project, save it to the asset's `prompts/` folder and make the sheet with `make.py sheet` (`video-production`). For a one-off request outside a project, return the JSON in a `json` code block and stop; don't generate it unless asked.

## Outfit sheets

When a character wears more than one outfit in a video (night clothes, everyday, going out), each outfit gets its own sheet, and every outfit after the first is an **edit of the approved base sheet**, never a fresh prompt, so the face and body can't drift. Write it as plain edit text, not JSON: "Edit the reference character sheet: change only her outfit to …", then every garment, colour, fabric, fit and footwear, which accessories stay and which come off, and the hair if it changes. End with "Keep everything else exactly as in the reference sheet": the same three-panel layout, character, face, body, backdrop, light and render. Save it as `<name>-<outfit>-vN.md` next to the base (`hero-sleep-v1.md`) and generate it with the base sheet as the reference.

Extras (a waiter, other diners, passers-by) get no sheet at all: they are described in the shot that shows them.

## Composition (always)

Exactly **one output image**: a single 16:9 landscape sheet containing three panels left → right, butted edge to edge like separate photos placed side by side. No drawn divider, separator line, gap, gutter or border between panels: the only boundary is where one shot ends and the next begins (framing and scale change there). Never render or request three separate images, files, canvases, or sequential outputs for the three views. No portrait-orientation canvas. Never two-panel. Never put a face on a full-body panel.

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
4. Load [character-blueprint.md](character-blueprint.md) and fill the JSON object with the locked details.
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

- One 16:9 landscape output image containing exactly three panels; left→right: headless front, back (no face), large 3/4 portrait; panels butted edge to edge, no divider lines or gutters
- No face on either body panel; front head and neck fully gone, with no skin above the collar
- Portrait: shoulder-up visible 25–35° 3/4 turn (unless front requested), one cheek/ear more visible, both eyes readable, no hands/arms; face matches reference if any; catch-light in eyes
- No moles/beauty marks unless requested or on reference; natural no-makeup skin; upper outfit matches body panels
- Fabrics opaque + weight named; light frontal/side; show-through in exclusions
- Product model: bare of jewellery, locked
- Same `#504f50` backdrop all panels; no props, scenery, labels, or extra people; sheet stays boring (no cinema grade)
