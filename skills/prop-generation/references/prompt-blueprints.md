# Prompt Blueprints

Use the flexible blueprint for a 3- or 4-view sheet. The three- and four-view blueprints below are the standard shortcuts. Keep every sheet to 3-4 views. Replace every bracketed instruction with concrete details and omit irrelevant clauses. Do not leave placeholders in the final prompt.

## Dynamic multi-view sheet (3-4 views)

Use whenever a surface-coverage audit helps you decide between 3 and 4 views.

```text
PROP REFERENCE SHEET — [PROP NAME] ([COUNT] views)

Create a production-ready [COUNT]-view studio reference sheet of one [prop]. Show the exact same physical object in every panel so downstream AI image and video models do not need to invent unseen surfaces.

CANONICAL PROP DESIGN
[Describe silhouette, proportions, construction, components, colors, materials, finish, markings, condition, and exact left/right asymmetry. Define one unchanged object before describing rotations.]

VIEWS
[GRID POSITION] — [ORIENTATION]: [State camera orientation, visible surface and identity-critical details.]
[Repeat once per selected view. Use 3 views by default and at most 4. Only include a surface the downstream video or ad will actually show.]

LAYOUT
Wide landscape canvas in a [1x3 / 2x2] arrangement. Place the views in a logical inspection sequence. Keep the object at the same visual scale across panels, centered within clear individual areas with balanced margins, no overlap, and no cropping. Let long or tall orientations use their cells efficiently without changing object identity or making one hero panel dominate. No labels, view names, captions, or any overlaid text; the only text allowed is text physically on the prop.

BACKGROUND + LIGHT
One continuous seamless neutral medium-to-dark grey studio background across the full sheet. Broad soft neutral product lighting, balanced exposure, controlled highlights, and a subtle physically appropriate contact shadow beneath each upright view. No environment or horizon clutter.

CAMERA + OPTICS
Use locked orthographic or near-orthographic technical framing for front, side, rear, top, and bottom views. Use a controlled normal-lens perspective only for a selected three-quarter view. Straight rectilinear geometry, no perspective tilt, no wide-angle distortion, and deep sharp focus in every panel.

MATERIAL + DETAIL
[Describe the optical behavior of each main material and render seams, fasteners, controls, tread, texture, wear, and manufacturing details consistently.]

CONSISTENCY LOCKS
All [COUNT] panels show the same single prop with identical dimensions, silhouette, component placement, colors, materials, markings, asymmetry, condition, and attachments. Every rotated view must agree structurally with all others. No alternate variants, mirrored asymmetry, duplicated or missing components, people, hands, characters, unrelated props, exploded parts, environmental staging, dramatic shadows, shallow focus, motion blur, cropped edges, orientation labels, view names, or captions. [Exact text/logo locks — only text physically on the prop.]
```

### Grid selection

- 3 views: 1x3 horizontal row.
- 4 views: 2x2.

### Surface-coverage audit

Start with the orientations that reveal the prop's defining silhouette. Within the 3-4 view cap, add a view only when the shot will actually show that surface and it resolves a real unknown:

- opposite side for lateral/medial asymmetry the shot reveals;
- top for controls, openings, or surface layout the audience sees;
- rear for heel, closures, ports, or back construction the shot shows;
- controlled three-quarter for connecting width, depth, and layered forms;
- detail for a small identity-critical feature that cannot read in full-object views.

Skip the underside by default; include a bottom view only when the underside is the actual subject (for example, a shoe outsole). Stop at 3 views unless a 4th earns its place. Never exceed 4 views unless the user explicitly asks. Do not add panels merely to fill a grid.

## Three-view horizontal sheet

Use for compact products and objects whose exterior is explained by front, side, and back.

```text
PROP REFERENCE SHEET — [PROP NAME] (3 views)

Create a clean three-view studio reference sheet of one [prop]. Show the exact same physical object in every view for downstream AI image and video reference use.

CANONICAL PROP DESIGN
[Describe silhouette and proportions first. Then define construction, components, controls, openings, colors, materials, finish, exact markings, and condition. Lock any left/right asymmetry.]

VIEWS
Left — FRONT VIEW: dead-on front face, [front-specific visible details].
Center — SIDE VIEW: strict [left/right] side profile, edge-on and level, clearly showing true depth, thickness, raised parts, and [side-specific details].
Right — BACK VIEW: dead-on rear face, [rear-specific visible details].

LAYOUT
Wide landscape canvas. Arrange the three views left to right on one horizontal baseline, evenly spaced and at equal scale. Center each view in its own area with generous equal margins. No overlap and no cropping. No labels, view names, captions, or overlaid text; only text physically on the prop may appear. The design is identical in all three views.

BACKGROUND + LIGHT
One continuous seamless neutral medium-to-dark grey studio background. Broad soft neutral product lighting, balanced exposure, controlled highlights, and a subtle contact shadow directly beneath each view. No environment or horizon clutter.

CAMERA + OPTICS
Eye-level, locked, orthographic or near-orthographic camera for every view. Normal-lens character, straight rectilinear edges, no perspective tilt, no foreshortening, no wide-angle distortion. Deep depth of field; every view is razor-sharp.

MATERIAL + DETAIL
[Describe the optical behavior of each main material: matte, satin, glossy, translucent, brushed, woven, painted, weathered, etc.] Render seams, fasteners, controls, texture, wear, and manufacturing details cleanly and plausibly.

CONSISTENCY LOCKS
One prop only. All three views show the exact same model, silhouette, dimensions, component placement, colors, materials, markings, and condition. Preserve [critical features]. No people, hands, characters, stands, packaging, unrelated accessories, extra objects, exploded parts, environmental staging, dramatic shadows, motion blur, cropped edges, orientation labels, view names, or captions. [Exact text/logo locks — only text physically on the prop.]
```

## Four-view 2x2 turnaround

Use for vehicles, machinery, furniture, or asymmetrical props whose top or a fourth angle the shot will actually show. Skip the fourth view (drop to three) when it does not appear on camera.

```text
PROP REFERENCE SHEET — [PROP NAME] (4 views)

Create a production-ready 2x2 turnaround sheet of one [prop]. Show the exact same physical object in all four panels for downstream AI image and video reference use.

CANONICAL PROP DESIGN
[Describe the overall silhouette, proportions, construction, major components, colors, materials, finish, markings, wear, and distinctive features. Define left/right placement for asymmetrical parts.]

VIEWS
Top-left — FRONT VIEW: straight-on and centered, [front-specific geometry and details].
Top-right — SIDE VIEW: full strict [left/right] broadside profile, [side-specific geometry and details].
Bottom-left — REAR VIEW: straight-on and centered, [rear-specific geometry and details].
Bottom-right — [TOP / THREE-QUARTER / DETAIL] VIEW: true orthographic or controlled view showing [top controls, roof equipment, a connecting three-quarter form, or an identity-critical detail the shot will show]. Avoid an underside view unless the bottom is the actual subject.

LAYOUT
Wide landscape 2x2 grid with clean, equal panel divisions. Keep the prop at a consistent readable scale while allowing a long side view to use its panel efficiently. Center each view with generous margins; no overlap and no cropping. No labels, view names, captions, or overlaid text; only text physically on the prop may appear. Every panel depicts one unchanged design.

BACKGROUND + LIGHT
The same seamless neutral medium-to-dark grey studio background in all four panels. Broad soft neutral studio light, balanced exposure, restrained highlights, and soft contact shadows where physically appropriate. No environment, atmosphere, or scenery.

CAMERA + OPTICS
Locked orthographic or near-orthographic technical framing. Normal-lens character, rectilinear geometry, no perspective tilt, no foreshortening, and no wide-angle distortion. Deep focus and sharp detail throughout.

MATERIAL + DETAIL
[Describe how paint, polymer, glass, rubber, metal, fabric, wood, or weathering should read under studio light.] Show plausible seams, joints, fasteners, tread, controls, and mechanical relationships.

CONSISTENCY LOCKS
All four panels show the same single prop with identical proportions, wheelbase or footprint, components, colors, materials, markings, asymmetry, wear, and attachments. The chosen top/detail view must agree structurally with the other three views. No people, hands, characters, unrelated props, alternate variants, duplicated components, exploded view, environment, dramatic perspective, shallow focus, motion blur, cropped edges, orientation labels, view names, or captions. [Exact text/logo locks — only text physically on the prop.]
```

## Reference-image adaptation

Add these ideas when the user provides an image:

```text
Use [@image_1 / the supplied reference image] as the identity source for the prop. Preserve its recognizable silhouette, proportions, component placement, color palette, materials, markings, and wear in every view. Infer unseen surfaces conservatively from the visible construction and design language. Do not redesign, beautify, simplify, or add features unless explicitly requested.
```

For an explicit change, use a scoped edit lock:

```text
Change only [requested feature]. Keep the prop's silhouette, proportions, camera-independent geometry, remaining components, colors, materials, markings, and condition unchanged across every view.
```

## Selection examples

- TV remote: front, strict side, back in one row.
- TV remote: front, strict side, back in one row.
- Running shoe: 4-view 2x2 grid showing lateral side, medial side, top-down/laces, and front three-quarter. Add a bottom/outsole view only if the outsole is the ad's subject. Define a single left or right shoe and keep that handedness unchanged.
- Toy robot: front, side, back; use four views only if the top controls actually appear on camera.
- Car or truck: front, full side, rear, and a front three-quarter in a 2x2 grid. Skip the undercarriage unless it is the subject.
- Blender or appliance: front, side, and a front three-quarter; add a top view only if the controls or jar opening matter. Never include an underside view.
- Chair: front, side, rear; add a three-quarter construction view as the fourth only when needed.
- Hand tool: working face/front, strict side, back/opposite face; add a detail as the fourth only when the mechanism matters.
- Boxed product: front, side, back; quote all required package text exactly and avoid inventing small print.
