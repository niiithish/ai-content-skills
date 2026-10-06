# product-in-hand-before-action (video-7 still 58-v2, approved)

## scene-58-v1

```json
{
  "prompt_type": "claymation_scene_still",
  "objective": "One stop-motion claymation frame for a vertical short film: Kitchen, morning sun: Penny tips two softgels from the Mysa bottle into her flipper, a glass of water beside her, smiling.",
  "reference_images_in_order": [
    "the kitchen look still",
    "the Penny sheet",
    "the Mysa bottle sheet"
  ],
  "references": [
    {
      "image": "the kitchen look still",
      "use_for": "Penny's kitchen. Take only its set design, light, colour and clay render; match its brightness and colour unless the lighting below describes a different time of day. This is a new camera: a medium close-up of Penny at the counter. Do not copy its framing, camera angle or anyone's pose."
    },
    {
      "image": "the Penny sheet",
      "use_for": "Penny's exact design: charcoal-black head and back, cream-white face patch and belly, short saffron-orange beak, big white disc eyes with black pupils under heavy charcoal lids with three lashes, rosy blush, dusty-rose clay cable-knit cardigan with gold buttons, short pearl string",
      "adapt": "The left and middle panels are the body, the right panel is the head; show one complete character with a full head, not the sheet layout and not a headless body."
    },
    {
      "image": "the Mysa bottle sheet",
      "use_for": "the exact clay Mysa bottle and softgel: a hand-rolled matte white clay bottle with a white ribbed clay cap; on its front a burgundy \"Mysa\" wordmark with a small lotus-figure logo above it, \"Feminine Moisture Support\" under it and \"60 softgels\" at the bottom; and the glossy translucent deep orange-red softgel. Label faces the camera.",
      "adapt": "The sheet shows one bottle from three views; show the bottle as one real object in the scene (or the number stated), not the sheet layout."
    }
  ],
  "canvas": {
    "image_count": 1,
    "aspect_ratio": "9:16",
    "orientation": "portrait"
  },
  "scene": "Viewpoint: front three-quarter at counter height. MIDGROUND (sharp): Penny tilts the clay Mysa bottle, label facing camera, over her other flipper; EXACTLY TWO glossy orange-red softgels have rolled out onto it. The bottle is real size against the penguins: about as tall as Penny's head from crown to chin. A glass of water on the counter. Her face three-quarter to camera, warm content smile, eyes soft. BACKGROUND: the cobalt-tiled kitchen, herbs on the sill. Every object follows real-world logic: knobs and handles on the fronts of drawers and doors, things face the person using them, products are their real size.",
  "identity": [
    "Penny, a female clay penguin in her late 50s: charcoal-black head and back, cream-white face patch and belly, short saffron-orange beak, big matte white disc eyes with black bead pupils under heavy drooping charcoal lids with three short lashes, rosy blush dabs, dusty-rose clay cable-knit cardigan with small gold buttons, short pearl string at her neck. She is clearly in her late 50s, not young: heavy lids, laugh-line creases at the eye corners, exactly like the sheet portrait."
  ],
  "camera": "Camera at counter height, 60 cm away, normal lens; label and softgels sharp.",
  "lighting": "Morning: warm golden sun through the window; bright and happy.",
  "rendering": "Real stop-motion claymation photographed on a handmade miniature set, like a high-end modern clay-animation short: hand-sculpted matte plasticine puppets with visible fingerprints, thumb-pressed edges, small tool marks and slight asymmetry; costumes sculpted from clay with pressed knit texture; big matte white clay disc eyes with glossy black bead pupils and a tiny catch-light; miniature props and furniture built from carved wood, clay, painted card and felt; shallow macro depth of field with creamy bokeh; rich saturated jewel-tone colour. Not CGI, not a smooth 3D render, no plastic sheen, not 2D, no outlines, not live action.",
  "format": "One 9:16 frame for a vertical short film, full-bleed edge to edge; important action in the central 70% of the frame, clear of the bottom and right edges.",
  "negative_prompt": [
    "a giant bottle",
    "one or three softgels",
    "misspelled label",
    "three-panel sheet layout",
    "headless body",
    "grey studio background",
    "smooth glossy 3D CGI render",
    "plastic toy sheen, vinyl figure",
    "Pingu-style simple flat penguins with tiny dot eyes",
    "real feathers, realistic birds",
    "2D cartoon, outlines",
    "photoreal humans",
    "grey, desaturated or washed-out colour",
    "cold blue or fluorescent light",
    "flat even lighting",
    "black bars, borders, letterbox",
    "captions, subtitles, watermark",
    "phone interface, app buttons or on-screen UI",
    "garbled or misspelled lettering",
    "real brand names"
  ],
  "final_generation_instruction": "Create one 9:16 claymation frame: sunny cobalt-tiled kitchen, smiling Penny tips exactly two orange-red softgels from a clay Mysa bottle into her flipper, a glass of water beside her."
}

```

## scene-58-v2

```json
{
  "prompt_type": "claymation_scene_still_edit",
  "objective": "Edit the first image so it becomes the moment just BEFORE the softgels come out: Penny's flipper is empty. Remove the two orange-red softgels lying on her flipper and the softgel coming out of the bottle mouth. Nothing else changes.",
  "reference_images_in_order": [
    "scene 58 v1 (the frame to edit)",
    "Mysa bottle sheet (the exact product, to keep the bottle print correct)"
  ],
  "edit": "Penny's left flipper stays exactly where it is, held out flat and palm-up just below the open bottle mouth, but it is completely empty: plain charcoal clay, no softgels on it. The bottle stays tilted in her right flipper in the same position, mouth open toward her empty flipper, with no softgel showing at the mouth or in the air. No softgels anywhere in the frame.",
  "keep": "The exact framing and crop, Penny's face, eyes, warm smile, dusty-rose cable cardigan, pearls and pose, the Mysa bottle with its print exactly as in the first image (lotus logo, burgundy \"Mysa\", \"Feminine Moisture Support\"), the glass of water, the chopping board, the kitchen, dresser, copper pans, blue tiles, window plants, the warm morning light and the clay render. Do not zoom in or out.",
  "negative_prompt": [
    "softgels on the flipper", "softgel at the bottle mouth", "falling capsules", "pills anywhere",
    "changed pose", "changed bottle", "misspelled text", "zoomed in or out", "captions, subtitles, watermark"
  ]
}

```

