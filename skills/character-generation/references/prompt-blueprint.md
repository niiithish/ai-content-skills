# Character Reference Prompt Blueprint

Replace every bracketed instruction with concrete details and remove irrelevant clauses. Do not leave placeholders in the final prompt.

```text
SUBJECT (RIGHT panel — large head)
[Use @image_1 / the supplied character reference as the identity source, if applicable.] Create a large shoulder-and-above portrait of [character description]. Preserve [facial structure, skin tone, eyes, nose, lips, eyebrows, hairline, hairstyle, facial hair, age, and distinctive marks]. [Expression and gaze]. [Head and neck accessories with exact left/right placement]. The character wears the exact same upper outfit shown in the left panel: [matching neckline, collar, layers, colors, material, graphic placement, and visible jewelry]. Hands and arms are not in frame; keep a clean head-and-shoulders crop.

LEFT panel — OUTFIT ONLY, ghost-mannequin
Show the complete outfit as naturally worn by a fully invisible person: [describe upper garments in layering order, cut, fit, color, material, texture, seams, closures, graphics, and wear]. [Describe belt, bag, waist accessories, clips, or charms]. [Describe bottoms, fit, construction, length, and hem behavior]. [Describe socks and footwear, including material, color, sole, and how the hem meets the shoes]. [Describe naturally positioned wearable accessories]. The clothing has convincing three-dimensional worn volume, drape, folds, openings, and contact between layers, but there is no person and no visible support. No head, face, hair, neck, skin, shoulders, chest, torso, arms, hands, fingers, legs, ankles, feet, anatomy, mannequin, mannequin surface, hanger, stand, or wire frame. Do not present the clothing as a flat lay. Keep the entire outfit and footwear visible and uncropped.

IDENTITY + WARDROBE LOCKS
Both panels define one canonical character and one canonical outfit. The portrait identity remains [identity locks]. The upper outfit in the right panel is identical to the left panel in garment design, neckline, collar, layering, fit, colors, materials, wear, graphics, and accessory placement. Preserve [exact asymmetry and exact quoted text]. No mirrored details, substitutions, alternate styling, color drift, or wardrobe redesign.

LAYOUT
Wide 16:9 landscape character-reference sheet with two clearly separated panels and a thin clean vertical divider. LEFT occupies roughly 42% of the canvas and shows the complete outfit in a full-length straight-on view with generous margins. RIGHT occupies roughly 58% and shows the much larger shoulder-and-above identity portrait. Keep both panels balanced, uncluttered, and easy to use as AI image and video references. No labels or decorative border.

BACKGROUND + LIGHT
One continuous seamless neutral dark-grey studio backdrop across both panels. Broad soft neutral studio lighting, balanced exposure, natural skin tones, restrained highlights, gentle dimensional shadows, and approximately 5500K neutral white balance. No environmental setting or horizon clutter.

CAMERA + FRAMING
Straight, eye-level reference photography with normal-lens perspective and rectilinear geometry. The left outfit is centered, fully visible from its empty neck opening through the soles, with no crop. The right portrait faces the camera and is framed from the shoulders upward, with the hair and shoulders comfortably inside the panel. Deep enough focus for the face, garments, accessories, and footwear to remain sharp. No wide-angle distortion, dramatic perspective, or tilted camera.

STYLE + DETAIL
Clean photorealistic studio character-reference sheet. Render natural pores, hair strands, and facial details without beauty-filter smoothing. Render fabric weave, stitching, fading, print integration, hardware, jewelry, leather, suede, rubber, and garment wear accurately under soft studio light. Keep the result polished but physically believable.

EXCLUSIONS
No visible body or body part in the left panel; no mannequin, support, hanger, stand, or flat lay. No hands or arms in the right portrait. No extra people, alternate faces, duplicate garments, spare shoes, unrelated props, environmental staging, labels, captions, watermarks, decorative graphics, identity drift, wardrobe drift, mirrored asymmetry, cropped outfit, harsh shadows, shallow-focus blur, or motion blur.
```

## Reference-image adaptation

For an identity reference, add:

```text
Use @image_1 as the sole identity source. Match the visible face and hair faithfully without beautifying or redesigning the person. Infer only details that are not visible and keep those inferences conservative.
```

For an outfit reference, add:

```text
Use @image_2 as the wardrobe source. Preserve its recognizable garments, layering, fit, colors, materials, graphics, wear, footwear, and accessory placement. Reconstruct the outfit on a fully invisible body in the left panel and show the same upper outfit on the character in the right panel.
```

For a requested edit, add:

```text
Change only [requested feature]. Keep the character's remaining identity features and every unrelated wardrobe detail unchanged in both panels.
```
