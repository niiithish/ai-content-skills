# Clay reference sheets

Sheets fix identity for every still. Make them with `make.py sheet`, save the prompt to the asset's `prompts/` folder, and show the user each sheet before any still uses it. Approved examples with their exact prompts are in [sheets/](sheets/).

## Characters

Follow `character-generation`: one 16:9 landscape image, three panels (headless front body, back body, large 3/4 portrait), thin `#d1d1d2` separators, `#504f50` backdrop, neutral studio light. What changes for clay:

- **Objective:** "a three-panel studio reference sheet of [name], a hand-sculpted stop-motion plasticine [animal/person] puppet".
- **Material, described physically:** matte plasticine with visible fingerprints, thumb-pressed edges, small tool marks and slight asymmetry; costume sculpted from clay (pressed cable-knit texture, pressed dots, rolled trim); accessories as clay or beads (a short pearl string).
- **The face (the identity):** big matte white clay disc eyes with glossy black bead pupils and a tiny catch-light, heavy sculpted lids (with a few short lashes for a woman), a sculpted beak or long nose, rolled-clay brows, dabs of blush. Strong, readable shapes; this is what stops the model making a toy.
- **Age** in the face for older characters: heavy lids, laugh-line creases at the eye corners.
- **Scale:** against another character ("Walt is half a head taller and rounder than Penny").
- **Negatives:** "Pingu-style simple flat penguins with tiny dot eyes", "smooth glossy 3D CGI render", "plastic toy sheen, vinyl figure", "real feathers, realistic birds" (or "real fur"), "2D cartoon, outlines".

Example: [sheets/character-penguin-penny.md](sheets/character-penguin-penny.md).

## Creatures (the "inside" world's helpers)

A recurring creature type gets one three-panel sheet of ONE creature (front, back, large three-quarter close-up), even when scenes show several of them; the stills then say how many and that they are identical copies of the sheet ("two Layer Makers, both exactly the creature from the sheet"). Give it a size against a story object (a softgel, a jar) and a job it does with a clay tool (rolling pins, trowels). Example: [sheets/character-creature-layer-maker.md](sheets/character-creature-layer-maker.md).

## The product

The client wants their real product in the clay world, as clay. Never describe it from scratch: logos and labels get redrawn wrong.

- Run `make.py sheet ... --ref <client's product photo>` with a `prop_reference_sheet` prompt whose `reference_fidelity` says: preserve the exact silhouette, proportions, cap, label layout, logo, colours and every word; translate only the material.
- **Make the clay unmistakable** (v1 of the Mysa bottle read as a real plastic bottle and was rejected): "a hand-rolled lump of matte white modelling clay shaped into the bottle form", soft rounded edges, walls slightly bulging and uneven, deep thumbprints and fingerprint whorls everywhere, tool strokes, a faint seam, a separate hand-pressed clay cap with uneven tool-cut ribs, zero specular shine.
- **Print painted on the front face only**, never a wraparound sticker label: "hand-painted onto the clay on the FRONT FACE ONLY, within the front third of the circumference". The side view shows plain clay with no text. Quote every word on the pack.
- Softgels or other contents stay their real material (glossy translucent orange-red resin) as a contrast to the clay.
- State scale against the hero ("the bottle stands about as tall as Penny's shoulder").

Example: [sheets/product-clay-bottle.md](sheets/product-clay-bottle.md) (the real photo is `product-clay-bottle-ref.jpg`).

Every later still with the product passes this sheet as an ingredient, and the user checks the product against it.

## No environment sheets

Clay projects skip them. The first still in each place is written in full (set, light, palette) and, once approved, becomes that place's **look still** for every later shot there. A new shot in the same place passes the look still and asks for the change: a new camera, new poses (see `scene-still.md`).
