# Prop JSON prompt blueprint

Use this structure to write a valid JSON image prompt. Replace bracketed values with concrete details, omit irrelevant optional fields, and return only the completed object in a `json` code block. Two jewellery views use a 1×2 row; three views use a horizontal row; four use a 2×2 grid. Include only surfaces needed to establish the object and support the intended shots.

```json
{
  "prompt_type": "multiview_prop_reference_sheet",
  "objective": "Generate exactly one composite studio reference image showing [three or four] views of the exact same [prop] for consistent downstream image and video shots.",
  "canonical_prop_design": {
    "identity": "[One object, defining silhouette, proportions, dimensions or scale cues].",
    "construction": "[Components, joins, closures, controls, and exact placement].",
    "color_and_materials": "[Each surface's color, material, finish, and wear].",
    "markings_and_asymmetry": "[Exact left/right asymmetry, markings, and only supplied text or logos; otherwise none]."
  },
  "canvas_and_layout": {
    "output_image_count": 1,
    "aspect_ratio": "16:9 landscape",
    "composite_rule": "All views occupy cells on this single image canvas; do not create separate images or files for individual views.",
    "view_count": 3,
    "grid": "One horizontal row of three equal cells, with thin solid #d1d1d2 separators between cells.",
    "framing": "For full-object views, keep the same visual scale and camera height; center each view with balanced margins and no crop or overlap. A selected detail closeup may be magnified.",
    "labels": "No orientation labels, view names, captions, or overlaid text; only text physically on the prop."
  },
  "views": [
    {
      "position": "left",
      "orientation": "[Strict camera axis for the first view, such as true front or full lateral side].",
      "visible_surfaces_and_details": "[Direction the object's front points; visible and hidden surfaces; identity-critical components and markings]."
    },
    {
      "position": "center",
      "orientation": "[Different camera axis, such as strict side or direct overhead].",
      "visible_surfaces_and_details": "[Different silhouette and visible surfaces, plus how they connect to the first view]."
    },
    {
      "position": "right",
      "orientation": "[Third distinct camera axis, such as straight rear or direct top, or a justified detail closeup].",
      "visible_surfaces_and_details": "[Previously unseen parts and surfaces; state what must not be visible from this angle]."
    }
  ],
  "background_and_lighting": {
    "background": "Uniform solid #504f50 studio background in every cell, with no environment or horizon.",
    "light": "Broad soft neutral product lighting, balanced exposure, controlled material highlights, and subtle contact shadows under upright views."
  },
  "camera_and_optics": "Orthographic or near-orthographic front, side, rear, top, or bottom views; controlled normal-lens perspective only for a selected three-quarter view. Rectilinear geometry, no tilt, deep sharp focus in every panel.",
  "material_detail": "[Weave, grain, seams, fasteners, ports, controls, tread, print, engraving, reflections, and wear, consistent between views].",
  "consistency_locks": [
    "Exactly one 16:9 landscape output image contains all views in cells separated by #d1d1d2 lines.",
    "All panels show one physical object with identical proportions, components, colors, materials, markings, condition, and attachments.",
    "Left/right asymmetries rotate correctly; no mirrored or invented surfaces.",
    "Each view has a visibly distinct silhouette or a justified detail crop; no repeated near-identical angle.",
    "Any on-prop text or logo appears exactly as supplied and nowhere else."
  ],
  "negative_prompt": [
    "alternate product variants, duplicated or missing parts, mirrored asymmetry, repeated near-identical angles",
    "separate images for each view, portrait canvas, cropped edges, inconsistent scale, overlapping views, exploded parts",
    "people, hands, unrelated props, lifestyle environment",
    "orientation labels, captions, invented text or logos, watermarks",
    "dramatic shadows, shallow focus, motion blur, wide-angle distortion"
  ],
  "final_generation_instruction": "Generate exactly one 16:9 landscape studio photograph containing a [three/four]-view studio reference sheet of the same [prop] in [ordered orientations]. Preserve [defining features] through rotation, keep the full object uncropped in each panel at consistent scale, using a uniform #504f50 background, thin #d1d1d2 cell separators, soft product light, and no labels or unrelated objects."
}
```

For four views, set `view_count` to `4`, change `grid` to `2×2 with one vertical and one horizontal thin solid #d1d1d2 separator`, and give the four `views` positions `top-left`, `top-right`, `bottom-left`, and `bottom-right`. The fourth view must resolve a surface needed on camera or a small identity feature unreadable at full scale. Choose views based on the object: a shoe may need lateral, medial, top, and three-quarter; a compact device may need front, side, and rear; a vehicle may need front, side, rear, and three-quarter. Keep handedness locked. Do not add an underside unless it matters to the shot.

## Jewellery loop and clasp: two views

When asked for two views, or when a necklace or bracelet is defined by its complete loop and front clasp, adapt the object above to `view_count: 2`, `grid: "1×2 row with thin solid #d1d1d2 separator"`, and two `views` only:

- **Left:** near-orthographic top-down full closed oval loop, entire circumference visible and uncropped. Beads or pearls continue across the top or nape arc; no chain-only gap, open horseshoe, or worn-on-neck V. Put the front clasp and drop, if any, at 6 o'clock.
- **Right:** near-orthographic magnified closeup of the *same* 6 o'clock hardware, with a few beads and spacers on each side. It is a detail of the left view, not a second piece. Show exactly how it opens and closes.

In `canonical_prop_design`, specify strand rhythm, bead or pearl shape and luster, metal, clasp ownership, and left/right attachment. For a ring-and-T-bar clasp, lock the ring wire and T-bar to the same gauge; the T-bar passes through the ring and is only slightly longer than its outer diameter. The viewer-left strand's jump ring connects through the receiver ring; the viewer-right strand owns the T-bar and does not also attach to the receiver. A drop, if present, hangs from the bottom of the receiver. Adapt these mechanics if the supplied product uses a different clasp. Lock the full loop, hardware, and handedness in `consistency_locks` and exclude hidden rear clasps, duplicate pendants, and missing nape beads. Keep the one-image 16:9 landscape canvas, #504f50 background, #d1d1d2 separator, light, label, and no-wearer rules from the main blueprint.

## Reference and scoped edits

For a supplied image, insert `reference_fidelity` after `objective` with the exact image handle, visible silhouette, proportions, palette, materials, branding, and wear to preserve; infer unseen surfaces conservatively. For a scoped remix, add `requested_changes` and lock all unrelated design features in `consistency_locks`. Quote on-prop text exactly; do not invent branding.

Before returning the JSON, compare every view's camera axis and silhouette, then read the full object once for stray object names or components copied from another example (for example, a shoe prompt mentioning a mug). Keep `objective`, `canonical_prop_design`, `canvas_and_layout`, `views`, `negative_prompt`, and `final_generation_instruction` about the same prop.
