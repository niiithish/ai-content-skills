# JSON blueprint for a photoreal still

Use this as a structure, not a form to fill mechanically. Replace bracketed strings with concrete shot details and remove fields that do not apply. In particular, omit `reference_fidelity` when there is no supplied reference and omit `product_identity` when no product is visible. The shown 9:16 portrait canvas is the default; change `aspect_ratio`, `orientation`, framing, and the final instruction when the user requests a different format. Return one parseable JSON object with a compact `final_generation_instruction` that agrees with the other fields.

```json
{
  "prompt_type": "real_world_still",
  "objective": "Generate one believable photograph of [specific subject and moment] in [specific place], with [the most important visual lock].",
  "reference_fidelity": {
    "sources": [
      {
        "image": "[@image_1 or supplied reference handle]",
        "use_for": "[Product identity, person identity, pose, location, or camera/light; one clear job per image].",
        "preserve": ["[Visible details that must stay exact]."],
        "do_not_copy": ["[Unwanted background, styling, UI, or unrelated objects]."]
      }
    ],
    "requested_changes": ["[Only changes the user actually asked for]."]
  },
  "canvas": {
    "output_image_count": 1,
    "aspect_ratio": "9:16",
    "orientation": "portrait",
    "framing": "[Close, medium, or wide; what is visible and where the crop falls].",
    "composition": "[Hero position, scale, foreground, middle ground, background, and negative space].",
    "edge_details": "[Useful left, right, top, and bottom anchors; omit if not needed]."
  },
  "scene": {
    "place": "[Specific plausible room or location, with enough context to read as real].",
    "moment": "[Ordinary action or still instant; state what has already happened].",
    "support_surfaces": "[Exact table, counter, sink ledge, floor, or hand that physically supports each object].",
    "materials_and_condition": "[Actual surface and furnishing materials, age, wear, and restrained lived-in detail].",
    "background": "[Only visible architecture and objects that establish the place]."
  },
  "subjects": [
    {
      "role": "[Hero person, product, or action].",
      "appearance": "[Identity or object construction relevant to this shot; preserve supplied references].",
      "position_and_scale": "[Where it sits in the frame and how large it appears].",
      "pose_or_state": "[Visible pose, hand contact, expression, or object state].",
      "wardrobe_if_visible": "[Specific garments, fit, fabric, and natural folds; omit for no-person still life]."
    }
  ],
  "product_identity": {
    "source": "[Supplied product reference or explicitly fictional design].",
    "package": "[Container shape, size, material, cap or dispenser, color, finish, and orientation].",
    "brand_system": "[Proper-name wordmark, product line, category descriptor, restrained color and typography hierarchy].",
    "exact_visible_text": ["[Only exact short text given by the user/reference or deliberately chosen for a fictional package]."],
    "label_placement": "[Where the brand, product name, category, and size sit on the package].",
    "incidental_products": "[A few varied plausible background packages if relevant; no invented readable gibberish]."
  },
  "camera": {
    "capture_style": "[Phone snapshot, handheld camera, or deliberate still camera, as justified by the brief].",
    "height_distance_angle": "[Physically plausible camera height, distance, and direction].",
    "perspective_and_focus": "[Plausible lens character, focus target, and background sharpness]."
  },
  "lighting": {
    "primary_source": "[Actual window, ceiling light, lamp, flash, or sun and its position].",
    "direction_and_falloff": "[How light crosses the scene and where exposure decreases].",
    "shadows_and_reflections": "[Specific shadows and material responses caused by that source].",
    "color_balance": "[Neutral or mixed room light as warranted; avoid automatic gold studio fill]."
  },
  "capture_details": {
    "processing": "[Natural phone HDR, modest camera processing, or requested look; no automatic beauty filter].",
    "physical_cues": ["[One or two scene-specific cues such as a water meniscus, cloth fold, or slight fingerprint]."],
    "overall": "[Scene-specific scale, surface texture, tonal falloff, focus behavior, and incidental wear visible in the frame]."
  },
  "negative_prompt": [
    "[Contradictions or predictable visual mistakes specific to this shot].",
    "generic blank packages, category-only labels, invented brand claims, illegible text pretending to be a hero label",
    "unrequested rustic wood, amber-tinted fill, seamless studio sweep, perfect prop symmetry",
    "CGI, illustration, anime, Pixar-like styling, extra objects, captions, watermarks, UI overlays"
  ],
  "final_generation_instruction": "Generate one 9:16 portrait photograph of [subject and moment] in [place]. Lock [product/person identity], [camera/crop], [support surface], and [light direction]. Preserve [critical supplied reference details], apply only [requested changes], and avoid [main observed failure modes]."
}
```

## Product packaging when no reference is supplied

A prominent bathroom product needs a believable retail design, not an anonymous white cylinder. The following is an **illustration, not a default brand to reuse**:

- Fictional brand wordmark: `Sorelle` in small deep-green sans-serif type.
- Product line: `Night Form` in larger type; descriptor: `Scalp Renewal Serum`; size: `30 mL` at the base. These are three levels of label hierarchy, not one generic `Hair Serum` sticker.
- Container: low cylindrical smoky-amber glass bottle, cream paper label with a deep-green band, ribbed dark-green dropper cap, slight liquid line and real glass reflections.
- In a bathroom still, name the physical support: for example, a stone sink counter beside a faucet. Use one directional window and the bathroom's actual overhead fixture as restrained mixed light. Keep background toiletries varied and secondary.

When a supplied product image exists, its brand, copy, shape, palette, and cap replace this entire invented example. Do not invent medical or performance claims. If exact lettering is essential to the final asset, retain the reference or plan a separate label-compositing pass after generation; JSON prompting alone cannot guarantee perfect small text.
