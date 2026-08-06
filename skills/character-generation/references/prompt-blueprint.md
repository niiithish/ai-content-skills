# Character prompt blueprint

Replace every bracketed instruction with concrete detail. Drop irrelevant clauses. No placeholders in the final prompt.

```text
SUBJECT (RIGHT panel — large head)
[Use @image_1 / the supplied character reference as the identity source, if applicable.] Create a large shoulder-and-above portrait of [character description] in a slight 3/4 head turn — face angled a little off camera, not a dead-on frontal passport angle [unless the user asked front-facing]. Preserve [facial structure, skin tone, eyes, nose, lips, eyebrows, hairline, hairstyle, facial hair, age]. Natural no-makeup skin: visible pores, natural oil and shine, fine lines, subtle uneven tone and light texture variation — a real bare face, not beauty-filter smooth or airbrushed. Small catch-light in each eye. No moles, beauty marks, scars, freckle clusters, tattoos, or piercings [unless the user requested one or the reference shows one, in which case state it with exact placement]. [Expression and gaze]. [Head and neck accessories with exact left/right placement]. The character wears the exact same upper outfit shown in the left panel: [matching neckline, collar, layers, colors, material, graphic placement, and visible jewelry]. Hands and arms are not in frame; keep a clean head-and-shoulders crop.

LEFT panel — OUTFIT ONLY, ghost-mannequin
Show the complete outfit as naturally worn by a fully invisible person: [upper garments in layering order — cut, fit, color, material, seams, closures, graphics, wear]. [Belt, bag, waist accessories]. [Bottoms — fit, length, hem]. [Socks and footwear]. [Wearable accessories positioned as worn]. Convincing three-dimensional worn volume, drape, and layer contact — no person and no support. No head, face, hair, neck, skin, shoulders, chest, torso, arms, hands, fingers, legs, ankles, feet, anatomy, mannequin, hanger, stand, or wire frame. Not a flat lay. Entire outfit and footwear visible and uncropped.

IDENTITY + WARDROBE LOCKS
Both panels define one canonical character and one canonical outfit. The portrait identity remains [identity locks]. The upper outfit in the right panel is identical to the left in garment design, neckline, collar, layering, fit, colors, materials, wear, graphics, and accessory placement. Every garment stays fully opaque: [fabric, weight, density], solid uniform [colour] with no skin tone or body shape visible through it. Preserve [asymmetry and exact quoted text]. [Product-modelling: ears bare, neck bare, wrists and fingers bare, no jewellery.] No substitutions, color drift, or wardrobe redesign.

LAYOUT
Wide 16:9 landscape character-reference sheet, two panels, thin clean vertical divider. LEFT ~42% full-length straight-on outfit with generous margins. RIGHT ~58% larger shoulder-up portrait. No labels or decorative border.

BACKGROUND + LIGHT
One seamless neutral dark-grey studio backdrop across both panels. Broad soft neutral studio light from front and slightly to the side, balanced exposure, natural skin tones, restrained highlights, gentle shadows, ~5500K. Light from the camera side so garments stay solid — no backlight or rim light through fabric. No environment or horizon.

CAMERA + FRAMING
Straight eye-level reference photography, normal-lens, rectilinear. Left: centered full-length straight-on outfit from empty neck opening through soles, no crop. Right: shoulders upward, slight 3/4 head turn (not frontal unless requested), hair and shoulders inside frame. Deep enough focus for face, garments, and footwear. No wide-angle distortion or tilt.

STYLE + DETAIL
Clean photorealistic studio character-reference sheet. Natural no-makeup skin (pores, shine, fine lines, subtle unevenness), hair strands, fabric weave, stitching, hardware, and wear under soft studio light. Believable, not retouched.

EXCLUSIONS
No body or mannequin in the left panel; no flat lay. No hands or arms in the right portrait. No sheer, transparent, translucent, mesh, or see-through fabric. Nothing shows through clothing: no visible nipples, areolae, breast or underwear outline, no translucent stretch, no wet clinging fabric. No moles, beauty marks, scars, freckle clusters, tattoos, or piercings unless requested or on the reference. No beauty-filter / airbrushed skin. No extra people, alternate faces, duplicate garments, unrelated props, scenery, labels, watermarks, identity or wardrobe drift, mirrored asymmetry, cropped outfit, harsh shadows, shallow blur, or motion blur.
```

## Reference adaptations

**Identity reference**

```text
Use @image_1 as the sole identity source. Match the visible face and hair faithfully without beautifying or redesigning. Infer only non-visible details, and keep those conservative.
```

**Outfit reference**

```text
Use @image_2 as the wardrobe source. Preserve garments, layering, fit, colors, materials, graphics, wear, footwear, and accessory placement. Reconstruct on a fully invisible body in the left panel; same upper outfit on the character in the right panel.
```

**Scoped edit**

```text
Change only [requested feature]. Keep remaining identity features and every unrelated wardrobe detail unchanged in both panels.
```
