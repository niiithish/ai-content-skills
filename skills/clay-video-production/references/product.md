# Clay product sheet

Layout and views: `video-production/references/sheets/product-sheet.md`. It is written for photoreal; what changes for clay:

The client wants their real product in the clay world, as clay. Never describe it from scratch: logos and labels get redrawn wrong.

- Run `make.py sheet ... --ref <client's product photo>` with a `prop_reference_sheet` prompt whose `reference_fidelity` says: preserve the exact silhouette, proportions, cap, label layout, logo, colours and every word; translate only the material.
- **Make the clay unmistakable** (v1 of the Mysa bottle read as a real plastic bottle and was rejected): "a hand-rolled lump of matte white modelling clay shaped into the bottle form", soft rounded edges, walls slightly bulging and uneven, deep thumbprints and fingerprint whorls everywhere, tool strokes, a faint seam, a separate hand-pressed clay cap with uneven tool-cut ribs, zero specular shine.
- **Print painted on the front face only**, never a wraparound sticker label: "hand-painted onto the clay on the FRONT FACE ONLY, within the front third of the circumference". The side view shows plain clay with no text. Quote every word on the pack.
- Softgels or other contents stay their real material (glossy translucent orange-red resin) as a contrast to the clay.
- State scale against the hero ("the bottle stands about as tall as Penny's shoulder").

Example: [sheets/product-clay-bottle.md](sheets/product-clay-bottle.md) (the real photo is `product-clay-bottle-ref.jpg`).

Every later still with the product passes this sheet as an ingredient, and the user checks the product against it.
