# Environment JSON prompt blueprints

Use the interior or exterior structure to write a valid JSON image prompt. Replace bracketed values with concrete spatial details; omit irrelevant optional fields. Return only the completed object in a `json` code block. Relationships between landmarks matter more than decorative detail.

## Interior

```json
{
  "prompt_type": "environment_reference",
  "objective": "Generate one spatially clear three-quarter establishing reference of [interior and purpose] for consistent downstream image and video shots.",
  "canvas_and_camera": {
    "output_image_count": 1,
    "aspect_ratio": "16:9 landscape",
    "composition_rule": "One establishing image on one canvas; no portrait crop or separate angle images.",
    "camera_position": "[Near a room corner, aiming diagonally toward a visible far inside corner placed about one-third or two-thirds across the image].",
    "view": "True two-point three-quarter angle: two adjoining walls occupy meaningful width, their wall-floor seams run diagonally toward the off-center corner from different directions, and broad floor, ceiling, foreground, middle-ground, and background remain visible. No broad far wall square to the camera.",
    "optics": "Eye-level or slightly elevated, rectilinear 24–35 mm character, level camera, upright verticals, deep readable focus."
  },
  "environment": {
    "type_and_style": "[Room type, era, purpose, style, mood, palette].",
    "scale_and_shell": "[Footprint, proportions, visible walls, floor, ceiling, level changes, fixed architecture].",
    "openings": "[Doors and windows with exact wall positions and what they lead to or reveal]."
  },
  "spatial_design": {
    "staging_anchor": "[One fixed recognizable landmark and its location].",
    "zones": "[Foreground, middle-ground, and background with relational placement].",
    "circulation": "[Clear paths between entrances, anchor, and activity areas; unblocked doors].",
    "landmark_relationships": ["[Place each identity-critical fixture relative to the anchor and openings]."]
  },
  "set_dressing": "[Major furnishings first, then restrained objects; exact locations for recurring items without hiding the shell].",
  "materials_and_condition": "[Surface materials, colors, texture, age, maintenance, wear, and light response].",
  "lighting_and_atmosphere": {
    "time_of_day": "[Time].",
    "primary_source_and_direction": "[One source and where it enters].",
    "shadow_direction": "[Consistent direction and softness].",
    "atmosphere": "[Visibility and color balance without obscuring geometry]."
  },
  "rendering_and_consistency_locks": [
    "Natural material texture, accurate room scale, crisp spatial detail, and one coherent unoccupied room unless people are requested.",
    "Preserve room shape, adjoining-wall relationships, openings, pathways, anchor, furniture placement, and light direction across later views."
  ],
  "negative_prompt": [
    "flat frontal or centered one-point view, corner centered or hidden, broad far wall square to camera", "dollhouse cutaway, top-down view, fisheye, extreme wide-angle stretch",
    "blocked doors or paths, floating objects, impossible reflections", "duplicated furniture, invented rooms or windows, warped walls, bent verticals",
    "contradictory light or shadows, extra people, garbled or misspelled lettering"
  ],
  "final_generation_instruction": "Generate exactly one 16:9 landscape photograph of a three-quarter interior reference of [place]. Place the visible inside corner off-center and show two adjoining walls with floor seams angling toward it from different directions. Show [anchor], [openings], and [furnishings] with clear circulation, one light direction, level rectilinear geometry, and deep focus."
}
```

## Exterior, venue, or landscape

```json
{
  "prompt_type": "environment_reference",
  "objective": "Generate one spatially clear three-quarter establishing reference of [exterior, venue, or landscape] for consistent downstream image and video shots.",
  "canvas_and_camera": {
    "output_image_count": 1,
    "aspect_ratio": "16:9 landscape",
    "composition_rule": "One establishing image on one canvas; no portrait crop or separate angle images.",
    "camera_position": "[Human eye-level or slightly elevated diagonal vantage looking obliquely across the site].",
    "view": "True three-quarter angle with strong foreground plane, lateral and forward depth, at least one receding side, and a readable far boundary.",
    "optics": "Moderately wide rectilinear lens, upright architecture, natural scale falloff, deep focus."
  },
  "environment": {
    "type_and_style": "[Site type, purpose, era, mood, palette].",
    "footprint_and_boundaries": "[Terrain, ground plane, elevations, adjacent structures, site limits].",
    "access": "[Entrances, gates, roads, paths, stairs, and their positions]."
  },
  "spatial_design": {
    "staging_anchor": "[One fixed landmark and its position].",
    "zones": "[Foreground, middle-ground, and background].",
    "routes": "[Clear movement paths; entrances and boundaries remain visible].",
    "landmark_relationships": ["[Place structures, vegetation, or equipment relative to the anchor and access routes]."]
  },
  "set_dressing": "[Essential site detail, signage, or vegetation without concealing geometry].",
  "materials_and_condition": "[Construction and ground materials, vegetation, age, maintenance, wear, palette].",
  "lighting_and_atmosphere": {
    "season_and_weather": "[Season and weather].",
    "time_of_day": "[Time].",
    "primary_source_and_direction": "[One sun or artificial source direction].",
    "shadow_direction": "[One consistent shadow direction].",
    "visibility": "[Atmospheric depth while preserving readable routes and boundaries]."
  },
  "rendering_and_consistency_locks": [
    "Accurate architecture and human scale, crisp spatial detail, and no crowd unless requested.",
    "Preserve one coherent footprint, boundaries, anchor, entrances, routes, materials, weather, and light direction across later views."
  ],
  "negative_prompt": [
    "flat frontal facade, centered one-point view, aerial top-down, fisheye, extreme panorama",
    "blocked entrances, impossible roads or stairs, floating structures", "duplicated landmarks, accidental extra buildings, warped architecture",
    "two suns, contradictory shadows, garbled or misspelled lettering"
  ],
  "final_generation_instruction": "Generate exactly one 16:9 landscape photograph of a three-quarter establishing reference of [site]. Show [anchor], [boundaries], and [entrances/routes] in clear relation, with readable foreground and far depth, one light direction, and level rectilinear geometry."
}
```

## Reference and scoped edits

When an image is supplied, insert `reference_fidelity` after `objective` with the exact image handle, architecture, layout, openings, landmarks, materials, condition, and lighting to preserve; infer unseen geometry conservatively. Expand a frontal reference into a spatially informative three-quarter view while respecting visible geometry. For a scoped remix, add `requested_changes` and preserve unrelated spatial locks.

For a requested short prompt, shorten field values while keeping valid JSON, three-quarter view, spatial relationships, light logic, exclusions, and 16:9.
