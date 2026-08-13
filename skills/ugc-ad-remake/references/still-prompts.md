# Still prompts

Load this when the user needs a new 9:16 scene still: winning-ad pose + our product. Output one prompt in a code block.

Character / prop / environment sheets stay landscape and belong to those skills. Scene stills are 9:16.

## Image roles

- `@image1` = winning-ad / pose / woman / room / hands / lighting
- `@image2` = our product (hero photo, open product, or prop sheet)
- `@image3` only for a geometry helper (zip mark, 90-degree turn plate)

If `@image2` is a 3-view sheet, name the panel to copy.

## Always lock

1. Same person as `@image1` unless they asked for a new talent in this still: face, hair, expression, wardrobe, nails.
2. Same room, table, wall crop, and lighting as `@image1`. No grey studio. No wall above a table-only overhead.
3. Same camera: height, tilt, distance, 9:16 crop, how much body is visible.
4. Same hands: contact points, which fingers pinch or rest.
5. Our product from `@image2` only: color, material, openings, stitch/shape, exact logo + metal color when that face is visible.
6. Product state they asked for. Do not open extra panels.

## Common stills

| Still | Frame | Hands | Product |
|---|---|---|---|
| Present closed | Waist-up, product on table or at chest | Palms on both sides or table-edge rest | Front face to camera, closed, logo readable |
| Handle / lift | Waist-up, product off table | One hand through handles or gripping the body | Closed, hanging as in `@image1` |
| Zip pinch | Tight on product + lower face | Dominant hand on the marked pull | Almost closed, 1-2 cm gap, not fully shut |
| Open toward camera | Waist-up, product lifted | One hand on handle, other under the hanging flap | Only the asked compartment open; contents stay |
| Overhead packed | Top-down table only | Fingers at the same rims as `@image1` | Only the asked openings; no extra flaps |
| Feature close-up | Torso + open feature | Pointing or holding the rim | Match our product's real pockets / brushes / bottles |

## Overhead

If `@image1` is top-down:

- camera looks down at the table
- no standing body, no extra wall
- hands enter from the same sides
- indoor table light, not product-studio brightness

## Prompt skeleton

```
9:16 photoreal UGC still. Remix @image1 and @image2.

KEEP FROM @image1
[person, pose, hands, crop, room, table, lighting]

REPLACE ONLY THE PRODUCT WITH @image2
[color, material, openings, logo, open/closed state]

HANDS
[exact contact points]

CAMERA
locked 9:16, same height and tilt as @image1

LOCKS
same person, same room, same light, our product only, no extra furniture, no old logo
```
