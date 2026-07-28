# Environment Prompt Blueprints

Use the relevant blueprint as a structural guide. Replace every bracketed instruction with concrete details and omit irrelevant clauses. Do not leave placeholders in the final prompt.

Blueprints: interior environment · large-scale or exterior environment.

## Interior environment

```text
ENVIRONMENT REFERENCE — [LOCATION NAME]

Create a wide 3/4-angle establishing image of [room/interior and its purpose]. The image will be reused as a stable location reference for downstream AI image and video generation.

SPATIAL DESIGN
[Define approximate room shape and scale, two adjoining visible walls, floor, ceiling, openings, windows, level changes, circulation paths, and fixed architectural landmarks. Place features relationally and keep the plan physically plausible.]

CAMERA + COMPOSITION
Place the camera [near a corner/diagonally across the room] at [eye level/slightly elevated], looking toward [principal wall or far corner]. Clearly reveal two adjoining walls receding in different directions, a broad area of floor, enough ceiling to understand the volume, and the depth between foreground, middle ground, and background. Wide landscape composition, moderately wide 24–35 mm rectilinear lens character, upright verticals, natural perspective, no fisheye or stretched corners. This must read as a genuine 3/4 view, not a head-on shot, centered one-point view, top-down view, panorama, or dollhouse cutaway.

FURNISHINGS + SET DRESSING
[Place major furniture and fixtures first, then add coherent functional or lived-in details. Keep doors, pathways, and spatial boundaries visible. Define exact locations for identity-critical objects.]

MATERIALS + CONDITION
[Describe architecture and main surfaces, colors, textures, age, cleanliness, wear, and how materials respond to light.]

LIGHT + ATMOSPHERE
[Define time of day and motivated light sources: windows, practical lamps, ceiling fixtures, signs, fire, etc. Describe direction, softness, color balance, and atmosphere without hiding the layout.]

RENDERING + LOCKS
Photorealistic [or requested style], deep readable focus, crisp architectural detail, realistic scale and material response, 16:9. One coherent unoccupied location. Preserve the stated room shape, wall relationships, opening positions, furniture placement, and pathways. No people unless requested, no duplicated furniture, blocked doors, floating objects, impossible reflections, warped walls, bent verticals, extra windows or rooms, malformed architecture, invented logos, brand names, or visible text.
```

## Large-scale or exterior environment

```text
ENVIRONMENT REFERENCE — [LOCATION NAME]

Create a wide 3/4-angle establishing image of [stadium/arena/street/courtyard/landscape/exterior]. The image will serve as a stable spatial and visual reference for downstream AI image and video generation.

SPATIAL DESIGN
[Define the site's footprint, terrain or ground plane, enclosing or adjacent structures, elevations, boundaries, access routes, entrances, and primary focal landmark. Divide the location into clear foreground, middle-ground, and background zones.]

CAMERA + COMPOSITION
Place the camera [diagonal position] at [human eye level/slightly elevated], looking obliquely across the location toward [far focal point]. Reveal a strong foreground plane, lateral and forward depth, the far boundary, and at least one adjoining or receding side. Keep entrances, routes, field or site boundaries, and major landmarks readable. Use a wide landscape 16:9 frame with moderately wide rectilinear lens character, upright architecture, natural scale falloff, and deep focus. This must be a genuine 3/4 establishing view—not a flat head-on façade, centered one-point composition, aerial top-down plan, fisheye, or extreme panorama.

LANDMARKS + SITE DETAILS
[Place stands, buildings, roads, paths, gates, tunnels, seating, landscaping, equipment, signs, or other major features relationally. Add coherent smaller details without obscuring circulation or geometry.]

MATERIALS + CONDITION
[Describe construction materials, ground surfaces, vegetation, age, maintenance, wear, weather effects, and color palette.]

LIGHT + ATMOSPHERE
[Define season, weather, time of day, sun or artificial-light direction, shadows, visibility, and atmospheric depth. Keep the site's geometry clear.]

RENDERING + LOCKS
Photorealistic [or requested style], realistic architecture and scale, crisp spatial detail, deep readable focus, 16:9. Preserve one coherent site plan, boundary shape, landmark placement, entrances, routes, surface materials, season, and weather. Default to no people or crowd; include them only if requested and keep them secondary. No duplicated landmarks, impossible roads or stairs, blocked entrances, floating structures, warped architecture, contradictory shadows, accidental extra buildings, invented branding, or visible text.
```

## Reference-image adaptation

Add this when the user supplies a reference image:

```text
Use [@image_1 / the supplied reference image] as the identity source for the environment. Preserve its recognizable architecture, layout, proportions, openings, landmark placement, furniture or site features, materials, color palette, condition, weather, and lighting. Expand the view into a spatially informative 3/4 angle while remaining faithful to the visible geometry. Infer unseen areas conservatively; do not redesign, beautify, relocate, or add major structures unless explicitly requested.
```

For a scoped remix, add:

```text
Change only [requested feature]. Keep the established footprint, architecture, camera-readable wall or site relationships, openings, pathways, landmark placement, remaining furnishings, materials, and condition unchanged.
```

## Compact prompt style

When the user prefers a short prompt like the provided room example, compress the same information into one dense paragraph. Retain the environment identity, genuine 3/4 camera geometry, spatial plan, key furnishings or landmarks, material condition, lighting, rendering standard, exclusions, and aspect ratio. Never shorten away the 3/4-view requirement or spatial relationships.
