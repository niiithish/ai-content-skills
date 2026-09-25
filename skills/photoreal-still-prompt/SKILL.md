---
name: photoreal-still-prompt
description: Write JSON prompts for one photorealistic real-world still, defaulting to 9:16 portrait unless the user requests another aspect ratio. Use for lifestyle scenes, UGC frames, product-in-context photos, ad images, video start frames, reference reconstructions, and scoped edits when the user wants an image prompt. Outputs prompt text only. Do not use for multi-panel character, prop, or environment reference sheets, or for anime, Pixar, illustration, CGI, or other stylized imagery.
---

# Photoreal Still Prompt

Write a **valid JSON image prompt** for one believable real-world photograph. This skill produces the prompt, not the image; image rendering uses a separately requested tool or workflow. Return the completed JSON object in one `json` code block unless the user asks for another format. No markdown or comments inside the object, unresolved placeholders, or fields filled with `n/a`.

Use [references/json-blueprint.md](references/json-blueprint.md) for the JSON structure and the product-packaging example. Adapt its fields to the actual shot; omit people, wardrobe, product, or reference fields when irrelevant. Keep the nested detail relevant to this shot; do not inherit a sample face, pose, beauty treatment, or aspect ratio.

## Scope and framing

- This is a **single final image**, not a reference sheet, collage, or multi-angle grid. **Default to 9:16 portrait** whenever the user does not specify an aspect ratio. An explicit user ratio or orientation overrides this default; align crop and camera framing with that choice. Do not inherit a conflicting ratio from a reference image or sample prompt.
- State what the camera would actually see: height, distance, angle, crop edges, subject scale, foreground/background relationship, and plausible lens or phone perspective. Avoid mutually incompatible optics.
- In the generated JSON, do not use `realistic`, `photorealistic`, or `cinematic` as a style shortcut. Specify the cues that create the requested look: camera height and handling, focus and exposure, skin/fabric/material texture, light source, falloff, shadows, and scene-appropriate imperfections. If the user says “cinematic,” translate it into those concrete choices rather than repeating the adjective.
- Anchor objects to real supporting surfaces and positions. Name whether an item sits on a table, counter, shelf, floor, sink ledge, or in a hand; show enough geometry to prove it. A requested kitchen table must not become a floating wall shelf.

## Reference control

- Give each supplied reference one explicit job: person identity, product/packaging identity, location, pose/crop, or lighting/camera. State what to preserve and what **not** to copy from it. Keep requested changes scoped.
- If exact product branding matters, use the supplied product image or exact text as authority. Preserve package silhouette, cap, palette, wordmark, label hierarchy, and readable supplied copy. Do not replace it with a blank package, a category-only label such as `Hair Serum`, invented claims, or random lettering.
- If no brand or package reference is supplied and a product must be prominent, design a plausible **fictional** retail identity: an intentional container, material, cap, proper-name wordmark, product-line name, short category descriptor, size, and restrained label hierarchy. Specify the short text exactly; leave fine print indistinct rather than requesting gibberish. If the user needs an exact existing brand and has not provided it, ask for the product reference or exact label copy.
- Background products should read as ordinary retail objects, not a row of identical blank white bottles. They carry plausible fictional brands too. Describe only the few whose design matters; their short text is readable where in focus, soft where not.

## Real-world look

- Build the shot from a credible place and moment. Choose materials and furniture for that scene instead of defaulting to rustic wood, aged tables, beige linen, or decorative props. Wood is fine when the brief or reference calls for it; it is not a universal realism shortcut.
- Use light with a physical source, direction, falloff, and shadows. For a casual home or phone image, allow uneven mixed indoor/daylight exposure and ordinary reflections. If time of day is unspecified, choose ordinary neutral daylight or the location's practical fixtures. Do not add amber sunset light, orange rim light, warm haze, or a gold-tinted fill by default. Use those only when the user or reference calls for them. Avoid symmetrical studio lighting, blown windows, and pristine product staging unless requested.
- Wardrobe, when present, needs a specific garment type, fit, fabric weight, wear, and natural folds. Avoid generic fashion styling, implausible cling or shine, and perfect AI-looking fabric. Keep a supplied outfit unchanged unless asked to edit it.
- Use a few relevant imperfections that follow the scene (fingerprints on glass, garment creases, water meniscus, slight household clutter), not a stock list of dust, grain, and mess. Make the product and scene physically plausible before adding micro-detail.

## Final check

- One real-world photo; 9:16 portrait by default or the user's explicit aspect and crop; no panel sheet or illustrated look. If the prompt is used to render an image, verify the final file's dimensions before calling it compliant.
- Camera angle, subject scale, support surface, light source, and shadow direction agree.
- Hero product has a credible package and brand treatment; exact supplied identity wins. No blank generic label or `Hair Serum`-only text.
- No default rustic wood, over-warm studio glow, generic wardrobe, or irrelevant styling carried from examples.
- Every JSON field describes the same shot. `negative_prompt` targets concrete failure modes and does not contradict the positive description. `final_generation_instruction` summarizes the same locked details without adding new ones.
