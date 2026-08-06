# Environment prompt blueprints

Use the matching blueprint. Replace every bracketed instruction. No placeholders in the final prompt.

## Interior

```text
ENVIRONMENT REFERENCE — [LOCATION NAME]

Create a wide 3/4-angle establishing image of [room/interior and purpose]. Reused as a stable location reference for downstream AI image and video generation.

SPATIAL DESIGN
[Room shape and scale, two adjoining visible walls, floor, ceiling, openings, windows, level changes, circulation paths, fixed architectural landmarks. Name one clear staging anchor (sofa, lamp, counter, doorway). Place features relationally; keep the plan plausible.]

CAMERA + COMPOSITION
Camera [near a corner / diagonally across the room] at [eye level / slightly elevated], looking toward [principal wall or far corner]. Reveal two adjoining walls receding in different directions, broad floor, enough ceiling for volume, and clear foreground / midground / background depth. Wide landscape, moderately wide 24–35 mm rectilinear character, upright verticals, natural perspective — no fisheye or stretched corners. Genuine diagonal 3/4 establishing view that gives depth for downstream camera angles — not a flat frontal head-on plate, centered one-point, top-down, panorama, or dollhouse cutaway.

FURNISHINGS + SET DRESSING
[Major furniture and fixtures first, then coherent lived-in detail. Keep doors, pathways, and boundaries visible. Exact locations for identity-critical objects.]

MATERIALS + CONDITION
[Architecture and main surfaces, colors, textures, age, cleanliness, wear, light response.]

LIGHT + ATMOSPHERE
[Time of day and one primary light logic: main source, direction, softness, color balance, shadow direction. No second competing sun. Do not hide the layout.]

RENDERING + LOCKS
Photorealistic [or requested style], deep readable focus, crisp architectural detail, realistic scale, 16:9. One coherent unoccupied location. Preserve room shape, wall relationships, openings, furniture placement, pathways, staging anchor, and light direction. No people unless requested; no duplicated furniture, blocked doors, floating objects, impossible reflections, warped walls, bent verticals, extra windows or rooms, malformed architecture, invented logos, brand names, or visible text.
```

## Large-scale / exterior

```text
ENVIRONMENT REFERENCE — [LOCATION NAME]

Create a wide 3/4-angle establishing image of [stadium / arena / street / courtyard / landscape / exterior]. Stable spatial and visual reference for downstream AI image and video generation.

SPATIAL DESIGN
[Footprint, terrain or ground plane, enclosing or adjacent structures, elevations, boundaries, access routes, entrances, primary focal landmark / staging anchor. Clear foreground, middle-ground, and background zones.]

CAMERA + COMPOSITION
Camera [diagonal position] at [human eye level / slightly elevated], looking obliquely toward [far focal point]. Strong foreground plane, lateral and forward depth, far boundary, at least one adjoining or receding side. Entrances, routes, field or site boundaries, and major landmarks readable. Wide landscape 16:9, moderately wide rectilinear lens, upright architecture, natural scale falloff, deep focus. Genuine diagonal 3/4 establishing view with readable depth — not a flat frontal façade plate, centered one-point, aerial top-down, fisheye, or extreme panorama.

LANDMARKS + SITE DETAILS
[Stands, buildings, roads, paths, gates, landscaping, equipment, signs — placed relationally to the staging anchor. Smaller detail without obscuring circulation or geometry.]

MATERIALS + CONDITION
[Construction materials, ground, vegetation, age, maintenance, wear, weather effects, palette.]

LIGHT + ATMOSPHERE
[Season, weather, time of day, one primary sun or artificial direction, one shadow direction, visibility, atmospheric depth. Geometry stays clear. No two suns.]

RENDERING + LOCKS
Photorealistic [or requested style], realistic architecture and scale, crisp spatial detail, deep focus, 16:9. Preserve one coherent site plan, boundaries, landmarks, entrances, routes, materials, season, weather, and light direction. Default no people/crowd; if included, secondary only. No duplicated landmarks, impossible roads or stairs, blocked entrances, floating structures, warped architecture, contradictory shadows, accidental extra buildings, invented branding, or visible text.
```

## Reference adaptations

```text
Use [@image_1 / the supplied reference image] as the identity source. Preserve architecture, layout, proportions, openings, landmarks, furniture or site features, materials, palette, condition, weather, and lighting. If the reference is frontal or head-on, expand it into a spatially informative diagonal 3/4 establishing view while remaining faithful to visible geometry — do not keep a flat frontal plate. Infer unseen areas conservatively; do not redesign, beautify, relocate, or add major structures unless requested.
```

Scoped remix:

```text
Change only [requested feature]. Keep footprint, architecture, wall or site relationships, openings, pathways, landmarks, remaining furnishings, materials, and condition unchanged.
```

## Compact style

When the user wants a short prompt, compress the same information into one dense paragraph. Never drop the 3/4-view requirement, spatial relationships, lighting, exclusions, or 16:9.
