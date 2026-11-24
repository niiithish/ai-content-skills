# product-clay-bottle (video-7 sheet, approved)

```json
{
  "prompt_type": "prop_reference_sheet",
  "objective": "Generate exactly one composite landscape image: a three-view reference sheet of the Mysa supplement bottle and its softgel as an obviously HAND-SCULPTED plasticine stop-motion prop, the kind an animator moulds by hand for a claymation set, not a real plastic bottle.",
  "reference_fidelity": {
    "reference": "@image_1 is the client's real product photo (assets/props/mysa-bottle/mysa-bottle-ref.png) and is the source of truth for the design.",
    "preserve": "Exact silhouette and proportions: a tall rounded-shoulder cylindrical bottle about 1.6 times as tall as it is wide, a wide white cap with fine vertical ribs about a quarter of the bottle's height, a short neck ring under the cap. White body. Label layout, logo shape, colours and every word in the same positions and order as the photo. Softgel: deep translucent orange-red oval.",
    "translate": "The material must change completely: no smooth moulded plastic anywhere. The bottle is a hand-rolled lump of matte white modelling clay shaped into the bottle form; the cap is a separate hand-pressed clay disc; the label artwork is hand-painted with slightly thick acrylic paint directly onto the clay. The softgel stays glossy translucent orange-red resin."
  },
  "canonical_prop_design": {
    "bottle": "Hand-rolled matte white plasticine, clearly handmade: soft rounded edges everywhere (no crisp machined corners), walls very slightly bulging and not perfectly straight or symmetrical, the whole surface covered in visible thumbprints and fingerprint whorls, a few shallow smoothing-tool strokes, tiny dents, and a faint seam line where the clay was joined. Zero specular plastic shine, only a soft satin sheen. Cap: a thick separate disc of white clay with hand-pressed vertical ribs cut with a modelling tool, slightly uneven in spacing and depth, its top edge softly rounded and a little wobbly; a thin rolled clay ring at the neck.",
    "label_front": "Hand-painted onto the clay on the FRONT FACE ONLY, sitting within the front third of the bottle's circumference, never wrapping onto the sides. Same layout as @image_1, top to bottom: small lotus-figure logo (dusty-mauve figure line with a circle head rising from two sage-green leaves); large deep burgundy script wordmark \"Mysa\" with the long swash under the y; \"Feminine Moisture Support\" in two lines of warm grey-brown; three rounded-outline badges: \"Pure Sea Buckthorn Oil\" with a small star, then \"OBCYN tested\" with a drop icon and \"Estrogen free\" with a leaf icon; \"60 softgels\" at the bottom. The paint has slight thickness and brush texture and follows the clay's fingerprinted surface, yet every letter stays crisp and readable.",
    "softgel": "One oval softgel the length of the label's badge row height, glossy translucent deep orange-red with a bright highlight and a warm glow inside, set on the floor in front of the bottle at frame-left as in the photo.",
    "scale": "In scenes the bottle stands about as tall as Penny's shoulder; one softgel is about the size of a Layer Maker."
  },
  "canvas_and_layout": {
    "output_image_count": 1,
    "aspect_ratio": "16:9 landscape",
    "composite_rule": "All views share one image canvas; never separate images.",
    "layout": "1x3 row with thin solid #d1d1d2 vertical separators, each cell centred with generous margins, same scale and camera height in every cell.",
    "labels": "No captions, view names or overlaid text; only the text printed on the bottle."
  },
  "views": [
    {
      "cell": "left",
      "view": "straight front, label facing the camera square-on",
      "visible": "The full front label as described, cap ribs, rounded shoulders, the softgel lying in front at the bottle's lower left.",
      "hidden": "Back of the bottle."
    },
    {
      "cell": "centre",
      "view": "true side profile, bottle rotated 90 degrees so the label's front faces frame-left",
      "visible": "The hand-made silhouette: wobbly ribbed cap, neck ring, softly bulging shoulder curve, slightly uneven sides, rounded base; only the thin edge of the painted label visible at the far left of the bottle; the side itself is plain fingerprinted white clay with no text.",
      "hidden": "All label text and the logo; no softgel in this cell."
    },
    {
      "cell": "right",
      "view": "high three-quarter from above-front, about 35 degrees down, label facing camera-left of centre",
      "visible": "The flat top of the cap and its rib ring, the label's logo and wordmark at an angle, and the softgel beside the base seen from above showing its oval shape and inner glow.",
      "hidden": "Base underside."
    }
  ],
  "background_and_lighting": {
    "background": "Uniform solid #504f50 studio backdrop in every cell.",
    "light": "Soft neutral frontal product light, about 5500K, small soft contact shadows; the softgel's translucent glow comes from light passing through it, no coloured light."
  },
  "camera_and_optics": "Near-orthographic macro product photography of a physical miniature, normal lens, deep focus, everything sharp.",
  "material_detail": "Matte plasticine is the dominant read: deep visible thumbprints and fingerprint whorls over every surface, tool strokes, tiny dents, faint dust specks and a soft satin sheen, very slight asymmetry; hand-painted label with brush texture; softgel glassy and smooth as a clear contrast to the clay.",
  "consistency_locks": [
    "One bottle design in every cell matching @image_1's silhouette, cap, label layout, colours and text exactly.",
    "Wordmark spelled \"Mysa\"; label text exactly: \"Feminine Moisture Support\", \"Pure Sea Buckthorn Oil\", \"OBCYN tested\", \"Estrogen free\", \"60 softgels\".",
    "Unmistakably hand-made clay bottle (fingerprints, uneven walls, soft edges, no plastic shine); glossy orange-red softgel; label on the front face only."
  ],
  "negative_prompt": [
    "smooth moulded plastic, real product photo look, glossy specular highlights, crisp machined edges, perfect symmetry",
    "printed sticker label, label wrapping round onto the sides, text on the side view",
    "misspelled or redrawn wordmark, changed logo, invented or extra label text",
    "different bottle shape, amber or coloured bottle, pump or dropper cap",
    "melted, lumpy-blob or cartoon-deformed bottle",
    "face, arms or legs on the bottle",
    "hands, people, scenery, extra bottles or extra softgels",
    "view labels, captions, watermarks",
    "golden or coloured light, heavy colour grade"
  ],
  "final_generation_instruction": "Using @image_1 as the exact design source, generate one 16:9 landscape studio sheet of the Mysa bottle as an obviously hand-sculpted matte white plasticine stop-motion prop: deep thumbprints and fingerprint whorls everywhere, soft rounded edges, slightly uneven bulging walls, a hand-pressed ribbed clay cap with uneven ribs, no plastic shine. The label is hand-painted on the front face only and matches @image_1 exactly: lotus-figure logo, burgundy \"Mysa\" wordmark, \"Feminine Moisture Support\", badges \"Pure Sea Buckthorn Oil\", \"OBCYN tested\", \"Estrogen free\", and \"60 softgels\", crisp and readable. Three cells with thin #d1d1d2 separators: straight front with one glossy translucent orange-red softgel at lower left; true side profile showing plain clay with no text; high three-quarter showing the cap top and the softgel. Uniform #504f50 backdrop, soft neutral light, deep focus, no labels."
}
```
