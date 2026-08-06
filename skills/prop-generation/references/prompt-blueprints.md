# Prop prompt blueprints

Use the multi-view blueprint. Replace every bracketed instruction. No placeholders in the final prompt. Cap at 3–4 views.

## Multi-view sheet (3–4 views)

```text
PROP REFERENCE SHEET — [PROP NAME] ([COUNT] views)

Create a production-ready [COUNT]-view studio reference sheet of one [prop]. Show the exact same physical object in every panel so downstream AI image and video models do not invent unseen surfaces.

CANONICAL PROP DESIGN
[Silhouette, proportions, construction, components, colors, materials, finish, markings, condition, exact left/right asymmetry. Define one unchanged object before rotations.]

VIEWS
[GRID POSITION] — [ORIENTATION]: [Camera orientation, visible surface, identity-critical details.]
[Repeat once per view. 3 by default, at most 4. Only surfaces the video/ad will show.]

LAYOUT
Wide landscape canvas in a [1x3 / 2x2] arrangement. Logical inspection sequence. Same visual scale across panels, centered in clear areas, balanced margins, no overlap, no cropping. Long/tall orientations may use their cell fully without a hero panel dominating. No labels, view names, captions, or overlaid text — only text physically on the prop.

BACKGROUND + LIGHT
One continuous seamless neutral medium-to-dark grey studio background. Broad soft neutral product lighting, balanced exposure, controlled highlights, subtle contact shadow under each upright view. No environment or horizon.

CAMERA + OPTICS
Locked orthographic or near-orthographic for front, side, rear, top, bottom. Controlled normal-lens perspective only for a selected three-quarter. Straight rectilinear geometry, no tilt, no wide-angle distortion, deep sharp focus every panel.

MATERIAL + DETAIL
[How each main material responds to light. Seams, fasteners, controls, tread, texture, wear — consistent.]

CONSISTENCY LOCKS
All [COUNT] panels show the same single prop: identical dimensions, silhouette, components, colors, materials, markings, asymmetry, condition, attachments. Rotated views must agree structurally. No alternate variants, mirrored asymmetry, duplicated or missing parts, people, hands, unrelated props, exploded parts, environment, dramatic shadows, shallow focus, motion blur, cropped edges, orientation labels, or captions. [Exact text/logo locks — only text on the prop.]
```

### Grids

- 3 views → 1×3 row
- 4 views → 2×2

### Surface coverage

Add a view only when the shot needs that surface and it resolves a real unknown:

- opposite side — lateral asymmetry the shot reveals
- top — controls/openings the audience sees
- rear — heel, ports, back construction the shot shows
- three-quarter — connects width/depth
- detail — small identity feature that will not read full-object
- bottom — only if underside is the subject

Stop at 3 unless a 4th earns its place.

## View order shortcuts

Fill the multi-view blueprint with these panel sets when they fit:

| Prop type | Suggested views |
|---|---|
| Compact product (remote, tool, boxed item) | front · strict side · back (1×3) |
| Shoe | lateral · medial · top/laces · front ¾ (2×2); outsole only if it is the subject |
| Appliance / blender | front · side · front ¾; top only if controls matter — never underside |
| Vehicle | front · full side · rear · front ¾ (2×2) |
| Chair / furniture | front · side · rear; ¾ as 4th only if needed |
| Robot / gadget with top controls | front · side · back · top when top appears on camera |

Handedness (left/right shoe, etc.) stays locked across every panel.

## Reference adaptations

```text
Use [@image_1 / the supplied reference image] as the identity source. Preserve silhouette, proportions, components, palette, materials, markings, and wear in every view. Infer unseen surfaces conservatively. Do not redesign, beautify, or add features unless requested.
```

Scoped edit:

```text
Change only [requested feature]. Keep silhouette, proportions, remaining components, colors, materials, markings, and condition unchanged across every view.
```
