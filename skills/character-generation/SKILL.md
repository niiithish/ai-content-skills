---
name: character-generation
description: Create detailed, model-ready image prompts for photorealistic two-panel character reference sheets on a neutral dark-grey studio background. Use when the user wants to design, generate, visualize, or remix a human character for AI images or video; establish a consistent face, hairstyle, clothing, footwear, and accessories; or turn a written concept or reference image into a landscape sheet with an invisible-body full outfit on the left and a matching shoulder-up identity portrait on the right.
---

# Character Generation

Create one standalone image-generation prompt for a landscape character reference sheet. Optimize it as an identity-and-wardrobe reference for later image generation, photo remixing, and AI video work.

## Related Skills

| Need | Use |
|---|---|
| A product or object reference sheet | **prop-generation** |
| A location reference or a shot keyframe | **environment-generation** |
| The video prompt that consumes this sheet | **video-generation** |
| The script and cut list that decide which assets are needed | **script-generation** |

This skill produces an identity reference on a neutral studio background, never a finished shot. When the user needs the character standing in a location, generate this sheet first, then use it as the identity reference for a keyframe or video prompt.

Wardrobe defined here becomes the wardrobe for every downstream clip, so keep it plain and repeatable unless the concept demands otherwise. Anything the character must never wear — for example bare ears when a necklace is the product — belongs in the locks.

## Core Composition

Always create exactly two clearly separated panels:

- **Left — outfit only:** Show the complete outfit from neck opening to footwear as if naturally worn by an invisible person. Include no head, face, neck, skin, hair, torso, arms, hands, fingers, legs, ankles, or other body parts. Show no mannequin, mannequin surface, support, hanger, stand, or wire frame. Preserve realistic garment volume, layering, drape, folds, closures, and contact between clothing pieces. Keep all clothing and footwear fully visible and uncropped.
- **Right — character identity:** Show a large shoulder-and-above portrait of the character, facing the camera unless the user requests another angle. Include the upper portion of the same outfit from the left panel so the neckline, collar, material, colors, and layers match exactly. Keep hands and arms outside the frame.

The left panel explains the complete wardrobe without introducing a body for the downstream model to copy or reinterpret. The right panel establishes the character's identity and how the outfit looks when worn.

## Workflow

1. Identify the character's identity, age range, presentation, physical features, hairstyle, expression, and distinctive details. When ethnicity is unspecified, apply the default below.
2. Check what the character is for. If she will model a product, decide what must stay bare so the product reads cleanly later.
3. Define one canonical outfit: every garment, layer, color, material, opacity, fit, graphic, accessory, and item of footwear.
4. Decide which accessories belong with the outfit display and which belong in the head-and-shoulders portrait. Do not duplicate an item inconsistently.
5. Read [references/prompt-blueprint.md](references/prompt-blueprint.md) and follow its section order.
6. Write the final prompt and check that the two panels describe one character and one unchanged outfit.

Do not ask follow-up questions when a coherent choice can be inferred. Make restrained, specific decisions that fit the user's concept. Ask only when a missing detail would substantially change the requested identity.

## Lock Character Identity

When a character reference image is supplied, treat it as the identity source.

- Preserve recognizable facial structure, skin tone, eye shape and color, nose, lips, eyebrows, hairline, hairstyle, facial hair, age, and distinctive marks.
- Use the platform reference token, such as `@image_1`, when available; otherwise say `the supplied character reference`.
- Do not beautify, age-shift, gender-shift, or redesign the person unless requested.
- If the user requests a change, name that change and explicitly preserve every unrelated identity feature.
- If several references show the same person, reconcile them into one identity. Prioritize the user-designated primary image when references conflict.

When no reference is supplied, define a visually specific but plausible identity. State visible features directly instead of relying on vague labels.

### Default identity when unspecified

When the user does not state ethnicity, nationality, or appearance, default to a white American character. State the visible features concretely — skin tone, hair colour and texture, eye colour — rather than writing a nationality label, which image models interpret inconsistently.

This is only a default. Any user-specified ethnicity, nationality, or feature set overrides it completely, and a supplied reference image always wins.

## Generation-Safety Constraints

These prevent silent rejections downstream. A character sheet that generates cleanly can still produce an unusable sheet, or block the video generation that consumes it.

### Wardrobe must be opaque

Never write sheer, transparent, translucent, mesh, see-through, or lingerie-style garments, and never leave a fabric's opacity unstated. Video generation models flag this material regardless of intent, and the flag lands on the clip rather than on the sheet.

Describe every garment as opaque by material and weight: "opaque ribbed cotton", "heavy matte jersey", "lined woven fabric". When a concept calls for a delicate or dressy look, get it through cut, drape, and colour rather than transparency, and state the lining explicitly. Keep coverage ordinary and practical unless the user asks otherwise, and put opacity in the locks so it survives regeneration.

### Minors

Image models are asymmetric here, and the asymmetry is worth stating plainly to the user rather than letting them hit it blind: prompts for young boys generally generate, while equivalent prompts for young girls are frequently refused. When a user asks for a young girl character sheet, tell them the refusal is likely before spending a generation on it.

Video generation adds a second constraint that runs the other way. Uploading a real photograph of a minor as a reference is typically blocked outright, but describing a child in the prompt text is usually allowed — the model then invents a synthetic child, which is the safer path anyway. So for any clip involving a minor, describe the child in words and skip the reference image.

Practical consequence: a character sheet is the wrong asset for a minor. Skip the sheet and carry the description into the video prompt as text.

## Lock the Outfit Across Panels

Define the complete outfit once, then preserve it exactly in both panels.

- Specify garment type, cut, fit, length, layering order, color, material, finish, seams, closures, pockets, wear, graphics, and accessories.
- Use exact left/right placement for asymmetric graphics, jewelry, clips, straps, charms, damage, or styling.
- Make the right portrait show the same neckline, collar, upper garment, layers, fabric, graphic placement, and head/neck accessories as the left outfit display.
- Keep required words or logos in quotation marks with exact spelling and capitalization. Do not invent branding or small text.
- Keep footwear, belts, bags, jewelry, and other requested styling items with the outfit. Floating wearable accessories are acceptable only when positioned naturally as worn and when no body parts or mannequin become visible.
- State the opacity and weight of every fabric. See the wardrobe rule under Generation-Safety Constraints.
- Do not let the left panel become a flat lay. Garments must hold realistic worn volume on a fully invisible body.

### Jewellery is a deliberate decision

Do not add jewellery by reflex. Decide it, and default to restraint.

**When the character will model a jewellery product, give her none at all.** Bare ears, bare neck, bare wrists, bare fingers. The product gets added later by the video or shot prompt, and anything already on the sheet competes with it, changes how it reads, or shows up in a clip where it does not belong. Put the bare state in the locks explicitly — "ears bare, neck bare, no rings or bracelets" — because models add earrings unprompted.

For every other character, one or two small restrained pieces are fine when they serve the character. Ask whether the piece says something about who she is; if not, leave it off.

This applies to the product category, not just the exact item: a character modelling earrings still gets a bare neck, since necklaces will be composited or shot later.

## Write the Prompt

Return only the finished prompt unless the user asks for an explanation or alternatives. Use natural language and concrete visual descriptions rather than keyword stuffing.

Write sections in this exact order:

1. `SUBJECT (RIGHT panel — large head)` — establish identity, facial details, expression, hair, head/neck accessories, and the matching visible upper outfit; explicitly exclude hands and arms.
2. `LEFT panel — OUTFIT ONLY, ghost-mannequin` — describe the complete outfit and explicitly prohibit every visible body part and mannequin structure.
3. `IDENTITY + WARDROBE LOCKS` — state that both panels represent one unchanged character concept and one identical outfit.
4. `LAYOUT` — define a wide landscape two-panel composition, full outfit on the left, larger shoulder-up portrait on the right, and a clean vertical divide.
5. `BACKGROUND + LIGHT` — define one seamless neutral dark-grey studio backdrop and soft neutral lighting shared across both panels.
6. `CAMERA + FRAMING` — define straight, undistorted reference photography with the outfit fully visible and the portrait cleanly cropped.
7. `STYLE + DETAIL` — define photorealism, natural skin, accurate fabric behavior, and sharp identity-critical detail.
8. `EXCLUSIONS` — prevent anatomy in the left panel, hands in the right panel, duplicate clothing, unrelated props, environmental staging, and identity or wardrobe drift.

## Visual Standard

Default to:

- a wide 16:9 landscape sheet with two panels and a thin clean vertical divider;
- roughly 40–45% of the width for the full outfit and 55–60% for the larger portrait;
- a seamless neutral charcoal or dark-grey studio background shared by both panels;
- broad, soft, even studio lighting at a neutral white balance with restrained shadows;
- a straight-on full-outfit view on the left and an eye-level shoulder-up portrait on the right;
- photorealistic reference photography, sharp focus, realistic skin, and clearly readable fabric weave, construction, and wear;
- calm neutral expression and direct gaze unless the user specifies otherwise;
- opaque, practical, fully covering garments;
- no jewellery on a product-modelling character, and restraint otherwise;
- a white American identity when the user has not specified one;
- no decorative design, scene, furniture, typography, labels, or props beyond requested wearable items.

Adapt styling, age, expression, pose, or rendering medium when requested, but retain the two-panel outfit-and-identity structure unless the user explicitly asks to change it.

## Final Check

Before returning the prompt, verify:

- the left panel contains a complete outfit but absolutely no visible anatomy or mannequin;
- the outfit is dimensional and naturally worn, not a flat lay or pile of clothing;
- the right panel is shoulder-and-above, with no hands or arms in frame;
- the face follows the supplied reference when one exists;
- the upper outfit in the portrait exactly matches the left panel;
- colors, materials, graphics, layers, jewelry, and asymmetrical details remain consistent;
- the outfit and footwear are uncropped and readable;
- every fabric is stated opaque, with nothing sheer, mesh, or see-through;
- a product-modelling character carries no jewellery, and the bare state is in the locks;
- both panels use the same neutral dark-grey background and compatible studio lighting;
- the divider and panel hierarchy are clear;
- no extra people, duplicate garments, unrelated objects, scenery, or text have appeared.
