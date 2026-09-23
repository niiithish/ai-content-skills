# Character JSON prompt blueprint

Write a valid JSON image prompt using this structure. Replace all bracketed values with concrete details, remove irrelevant optional fields, and output the completed object in one `json` code block. Add enough detail to lock identity and wardrobe; avoid inventing measurements or marks absent from the brief.

```json
{
  "prompt_type": "character_reference_sheet",
  "objective": "Generate exactly one composite landscape image containing a three-panel studio reference sheet of [one adult character] with one canonical outfit and the face visible only in the portrait panel.",
  "canvas": {
    "output_image_count": 1,
    "aspect_ratio": "16:9 landscape",
    "composite_rule": "All three views share one image canvas; do not create separate images or files for individual panels.",
    "layout": "Three panels left to right with thin solid #d1d1d2 vertical separators: headless front body about 30%, no-face back body about 30%, shoulder-up portrait about 40%.",
    "framing": "Full outfit and footwear uncropped in body panels; portrait hair and shoulders inside frame with no hands or arms.",
    "labels": "No captions, panel names, decorative border, or watermark."
  },
  "panels": [
    {
      "position": "left",
      "view": "full-body front",
      "subject": "[Build and stance], with natural body volume and arms relaxed. Head and neck completely absent. The garment collar is the topmost visible edge, with #504f50 background directly above and inside its opening; no skin above the collar, chin, stump, mannequin, or floating features.",
      "wardrobe_visible": "[Upper layers, bottoms, footwear, and accessories with cut, fit, color, material, weight, opacity, and placement]."
    },
    {
      "position": "center",
      "view": "full-body back",
      "subject": "Same body and outfit from behind. No readable face or profile. [Rear hair silhouette if needed].",
      "wardrobe_visible": "[Rear seams, closures, graphics, hems, footwear, and accessories, consistent with the front]."
    },
    {
      "position": "right",
      "view": "large shoulder-up portrait, visible three-quarter head turn",
      "subject": "[Adult age range, skin tone, facial structure, eyes, brows, nose, lips, hairline, hairstyle, gaze, expression]. Head turned about 25–35 degrees from the camera, with both eyes readable and one cheek and ear more visible; not a symmetrical frontal portrait. Natural no-makeup skin with pores, slight shine, fine lines, and uneven tone; small eye catch-lights. No hands or arms.",
      "wardrobe_visible": "[Exact same upper outfit, neckline, layering, colors, graphics, and accessories as body panels]."
    }
  ],
  "identity": {
    "source": "[Character description or supplied identity reference].",
    "distinctive_features": "[Only requested or reference-visible marks, piercings, tattoos, or asymmetries with exact placement; otherwise none].",
    "expression": "[Neutral closed mouth by default or the requested expression]."
  },
  "wardrobe": {
    "canonical_outfit": "[Every garment in layer order; fabric and weight; fully opaque construction; fit, color, wear, footwear, and accessories].",
    "text_and_logos": "[Exact supplied text or logos; otherwise none].",
    "product_modeling_zones": "[For a product model, bare ears, neck, wrists, and fingers with no jewelry; otherwise limited requested accessories]."
  },
  "background_and_lighting": {
    "background": "Uniform solid #504f50 studio backdrop in every panel.",
    "light": "Broad soft neutral frontal or slight side light, approximately 5500K; balanced exposure, gentle shadows, and no backlight through garments."
  },
  "camera_and_style": {
    "camera": "Eye-level, normal-lens, rectilinear studio reference photography; centered full-length bodies and a large shoulder-up portrait; deep readable focus.",
    "detail": "Visible skin pores and tonal variation, separate hair strands, fabric weave, stitching, hardware, and natural drape; no beauty-filter smoothing or heavy color grade."
  },
  "consistency_locks": [
    "Exactly one 16:9 landscape output image contains all three panels, with #d1d1d2 dividers; panel 3 is the only face source.",
    "All panels show one person and one unchanged outfit.",
    "Front and back construction, footwear, colors, materials, graphics, and left/right asymmetries agree through rotation.",
    "The portrait upper outfit and accessories exactly match the body views.",
    "All fabrics are fully opaque with no skin tone or underwear visible through them."
  ],
  "negative_prompt": [
    "head, exposed neck skin, chin, or neck stump above front-panel collar", "readable face or profile on back body panel", "frontal symmetrical portrait, hands or arms in portrait panel",
    "separate images for each view, portrait canvas, extra panels or people", "cropped outfit or footwear", "mannequin or hollow flat-lay body",
    "sheer, mesh, translucent, or see-through clothing", "visible nipples or underwear outline",
    "unrequested marks, jewelry, text, or logos", "wardrobe or identity drift", "airbrushed skin, heavy color grading, labels, watermarks"
  ],
  "final_generation_instruction": "Generate exactly one 16:9 landscape studio photograph containing a three-panel character sheet: front body with no head or exposed neck above its collar, no-face full-body back, and large shoulder-up portrait visibly turned 25–35 degrees with one cheek and ear more visible. Keep [identity and outfit] consistent against a uniform #504f50 studio backdrop with thin #d1d1d2 panel separators and soft neutral light, natural detail, fully opaque clothing, and no scenery or labels."
}
```

## Reference and edits

When an image is supplied, add `reference_fidelity` after `objective` with exact image handles (for example `@image_1`), visible identity and wardrobe details to preserve, and an instruction to infer unseen details conservatively. Preserve face, hair, age, marks, and outfit unless changed by request. For a scoped change, add `requested_changes` and state what stays locked.

If a smile sheet is explicitly required, output a second complete JSON object for a second single-sheet image. Copy the first object's layout, body panels, identity, wardrobe, and locks. Change only the portrait expression and corresponding `objective` and `final_generation_instruction`. If teeth show, describe this character's tooth shape, size, alignment, and color.
