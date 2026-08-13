# Character prompt blueprint

Replace every bracketed instruction with concrete detail. Drop irrelevant clauses. No placeholders in the final prompt.

```text
PANEL 1 — FRONT BODY, head removed
Full-body front view of [character body type / build / approximate height cues], standing straight, arms relaxed at the sides. The head is completely removed: empty neck opening at the collar only — no head, face, hair, neck, mannequin, stump, or floating features. Natural body under the clothes: shoulders, arms, hands, torso volume, legs, ankles, feet. Wearing [upper garments in layering order — cut, fit, color, material, seams, closures, graphics, wear]. [Belt, bag, waist accessories]. [Bottoms — fit, length, hem]. [Socks and footwear]. [Wearable accessories positioned as worn]. Convincing worn volume and drape. Entire outfit and footwear visible and uncropped. Not a flat lay.

PANEL 2 — BACK BODY, no face
Full-body back view of the same person and the exact same outfit, standing straight. No face visible — no profile, no three-quarter face. [Back-of-head and hair from behind only if hair is part of the silhouette: length, color, style as seen from rear.] Same garments, materials, fit, graphics, footwear, and accessories as panel 1, correctly shown from behind (seams, vents, back pockets, hem, sole shape). Full length uncropped.

PANEL 3 — PORTRAIT (large head)
[Use @image_1 / the supplied character reference as the identity source, if applicable.] Large shoulder-and-above portrait of [character description] in a slight 3/4 head turn — face angled a little off camera, not a dead-on frontal passport angle [unless the user asked front-facing]. Preserve [facial structure, skin tone, eyes, nose, lips, eyebrows, hairline, hairstyle, facial hair, age]. Natural no-makeup skin: visible pores, natural oil and shine, fine lines, subtle uneven tone and light texture variation — a real bare face, not beauty-filter smooth or airbrushed. Small catch-light in each eye. No moles, beauty marks, scars, freckle clusters, tattoos, or piercings [unless the user requested one or the reference shows one, in which case state it with exact placement]. [Expression and gaze — default relaxed neutral, mouth closed, no smile unless the user wants a smiling character; if smiling, lock this character’s own mouth shape and teeth]. [Head and neck accessories with exact left/right placement]. Exact same upper outfit as the body panels: [matching neckline, collar, layers, colors, material, graphic placement, and visible jewelry]. Hands and arms not in frame; clean head-and-shoulders crop.

IDENTITY + WARDROBE LOCKS
All three panels define one canonical character and one canonical outfit. Facial identity exists only in panel 3 and remains [identity locks]. Panel 1 has no head; panel 2 has no face. Upper outfit on the portrait matches the body panels in garment design, neckline, collar, layering, fit, colors, materials, wear, graphics, and accessory placement. Front and back body panels are the same wardrobe. Every garment stays fully opaque: [fabric, weight, density], solid uniform [colour] with no skin tone or body shape visible through fabric. Preserve [asymmetry and exact quoted text]. [Product-modelling: ears bare, neck bare, wrists and fingers bare, no jewellery.] No substitutions, color drift, or wardrobe redesign.

LAYOUT
Wide 16:9 landscape character-reference sheet, three panels left to right, thin clean vertical dividers. Panel 1 ~30% headless front full body. Panel 2 ~30% back full body. Panel 3 ~40% larger shoulder-up portrait. Generous margins on body panels so feet and shoulders are not cropped. No labels or decorative border.

BACKGROUND + LIGHT
One seamless neutral dark-grey studio backdrop across all panels. Broad soft neutral studio light from front and slightly to the side, balanced exposure, natural skin tones, restrained highlights, gentle shadows, ~5500K. Light from the camera side so garments stay solid — no backlight or rim light through fabric. No environment, horizon, or cinematic grade.

CAMERA + FRAMING
Straight eye-level reference photography, normal-lens, rectilinear. Panels 1–2: centered full-length standing figures, headless front / no-face back, no crop of footwear. Panel 3: shoulders upward, slight 3/4 head turn (not frontal unless requested), hair and shoulders inside frame. Deep enough focus for face, garments, and footwear. No wide-angle distortion or tilt.

STYLE + DETAIL
Clean photorealistic studio character-reference sheet — intentionally plain. Natural no-makeup skin (pores, shine, fine lines, subtle unevenness), hair strands, fabric weave, stitching, hardware, and wear under soft studio light. Believable, not retouched. No film grain, no cinema look, no heavy color grade.

EXCLUSIONS
No head or face on panel 1. No face on panel 2. No two-panel or four-panel layout. No hands or arms in the portrait panel. No sheer, transparent, translucent, mesh, or see-through fabric. Nothing shows through clothing: no visible nipples, areolae, breast or underwear outline, no translucent stretch, no wet clinging fabric. No moles, beauty marks, scars, freckle clusters, tattoos, or piercings unless requested or on the reference. No beauty-filter / airbrushed skin. No extra people, alternate faces, duplicate garments, unrelated props, scenery, labels, watermarks, identity or wardrobe drift, mirrored asymmetry, cropped outfit or feet, harsh shadows, shallow blur, motion blur, or cinematic grading on the sheet.
```

## Reference adaptations

**Identity reference**

```text
Use @image_1 as the sole identity source for panel 3. Match the visible face and hair faithfully without beautifying or redesigning. Infer only non-visible details, and keep those conservative. Body panels stay headless (front) / no-face (back).
```

**Outfit reference**

```text
Use @image_2 as the wardrobe source. Preserve garments, layering, fit, colors, materials, graphics, wear, footwear, and accessory placement. Show the full outfit on the headless front body and the no-face back body; same upper outfit on the portrait.
```

**Scoped edit**

```text
Change only [requested feature]. Keep remaining identity features and every unrelated wardrobe detail unchanged in all three panels.
```

**Smile variant (second sheet when needed)**

```text
Same three-panel sheet as the locked character. Change only panel 3 expression to a natural smile for this character: [smile description]. If teeth show, lock [this character’s tooth shape, size, alignment, color] — same mouth, not a different person. Panels 1–2 and all wardrobe/identity locks unchanged.
```
