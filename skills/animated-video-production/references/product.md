# Animated product sheet

Layout and views: `video-production/references/sheets/product-sheet.md`. It is written for photoreal; this is what changes in 3D feature animation. The layout stays: one landscape image, the same cells, butted edge to edge with no divider lines.

- **The client's product stays the real product.** Make the sheet from its real photos with `make.py sheet ... --ref`; the label is never redrawn and every prompt that shows it quotes the label text exactly.
- **Render** the prop as feature-animation CG: slightly simplified, appealing shapes, clear readable colour, soft 3D shading, and materials that still read (glossy metal, wax paper, cardboard). Replace the `studio photograph` wording with this.
- **Scale:** state its size against a character ("about the length of the cat's body") so scenes keep it consistent.
- **Product mascots** (a real product with a face and limbs): image models redraw logos and labels wrong. Edit the client's real product photo with `make.py sheet ... --ref`, adding only the face, arms and legs and keeping the label, logo, colours and shape exactly; quote the label text. When the user already likes a take, edit that exact file, one take at a time.
