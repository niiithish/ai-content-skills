# Scene still prompts (claymation)

A scene still is one composed 9:16 frame: the opening image of one clip. Write it as JSON in a `json` code block, saved to the shot's `prompts/scene-N-vK.md`. The model reads the JSON as text, so the field names only organise your thinking. Say each important thing once, in plain words.

## Before writing

- Look at every reference you'll pass: sheets and the place's look still.
- Read the shot's row in `PLAN.md` and the lessons in `failure-locks.md`.
- Open two or three images in `look/` closest to this shot (home at night, bathroom, metaphor prop, inside world, group, crowd, macro, landscape, product) and read their `.md` prompts. Write to that level of detail; a thin prompt gives a flat, toy-like frame.
- The still shows the **state before the action** of its clip: an empty flipper before the softgels drop in, a closed drawer before it opens. The clip adds the action; it can't take away what the still already shows.

## Ingredients, in this order

1. **The look still** of this place (its first approved still), when one exists. Its `use_for` takes the set design, light, colour and clay render **only**, and describes the new camera: "Take only its set design, light, colour and clay render; match its brightness and colour exactly. This is a new camera: [where it stands, what fills the frame]. Do not copy its framing, camera angle or anyone's pose."
2. **Character sheets**, one per character in frame, with an `adapt`: "The left and middle panels are the body, the right panel is the head; show one complete character with a full head, not the sheet layout and not a headless body."
3. **The clay product sheet** whenever the product is in frame, even small or in the background. Its `use_for` lists the pack's print word for word.

The first still in a place has no look still: write the set, palette and light in full. Never pass a rejected attempt as a reference.

## Required content

- **Viewpoint and layers** in `scene`: Viewpoint, then FOREGROUND (sharp: a hand, a prop, a mug), MIDGROUND (the subject, pose, expression), BACKGROUND (named set dressing: teal wallpaper with gold leaves, ruby curtains, a rose-shaded brass lamp). Every frame has depth.
- **Facing and eyeline** for every character: which way body and face point in the frame and what they look at.
- **Expression, physically:** "eyes narrowed under her heavy lids, one brow cocked, beak set in a firm little smile". Clay faces read through lids, brows and beak/mouth shape.
- **Age** for older characters in `identity`: "She is clearly in her late 50s, not young: heavy lids, laugh-line creases at the eye corners, exactly like the sheet portrait."
- **Scale** whenever two characters or a character and a product share the frame; hand-held products at real size ("a tube about the length of her face, held in one flipper").
- **Counts spelled out** ("ONE big brass stopwatch", "exactly two softgels") with the wrong counts in the negatives.
- **One readable prop per metaphor.** A metaphor prop is a single everyday object whose meaning reads at a glance, with its words painted on it: a stopwatch whose dial says "90 SECONDS". Never two clocks, never a gauge plus a dial.
- **Real-world object logic:** knobs on drawer fronts, a screen facing its user, a label facing camera. If an object would be odd in a real room, the user will flag it.
- **Light:** the physical sources, direction, warmth and mood. "Night: the rose-shaded lamp from frame-left is the key, warm amber light on her face; rich warm shadows behind. Cosy and warm, never grey." Day: "warm golden sun through the frosted window from frame-right as the key, soft bounce off the tiles; bright, warm and lived-in, never cold or clinical."
- **Rendering** (every still, word for word unless the agreed look differs):

  > Real stop-motion claymation photographed on a handmade miniature set, like a high-end modern clay-animation short: hand-sculpted matte plasticine puppets with visible fingerprints, thumb-pressed edges, small tool marks and slight asymmetry; costumes sculpted from clay with pressed knit texture; big matte white clay disc eyes with glossy black bead pupils and a tiny catch-light; miniature props and furniture built from carved wood, clay, painted card and felt; shallow macro depth of field with creamy bokeh; rich saturated jewel-tone colour. Not CGI, not a smooth 3D render, no plastic sheen, not 2D, no outlines, not live action.

- **Format:** "One 9:16 frame for a vertical short film, full-bleed edge to edge; important action in the central 70% of the frame, clear of the bottom and right edges." Never name a social app.

## Text in the frame

Anything that carries print in real life (a cream tube, a jar, a calendar, a book, a phone screen, a sign) gets short, readable text quoted in the prompt ("RAW MATERIAL" on a jar, "DAY 4" on a wall calendar), painted or pressed into the clay. Never a blank white product. Never captions, subtitles, watermarks or app UI. Check spelling in the render.

## "Inside the body" stills

A cosy miniature clay world: a warm terracotta cave, hanging little lights, a tall stack of rose-pink clay layers, a candle in an alcove, little builder creatures with clay tools, labelled jars. Negatives: "human anatomy, organs, cells, blood", "medical diagram", "scary, slimy or gross". See `look/inside-world-cave.md` and `look/inside-world-workshop.md`.

## Base negatives

Append these to every still's own negatives (swap the penguin lines for the project's characters):

```json
"three-panel sheet layout", "headless body", "grey studio background", "smooth glossy 3D CGI render", "plastic toy sheen, vinyl figure", "Pingu-style simple flat penguins with tiny dot eyes", "real feathers, realistic birds", "2D cartoon, outlines", "photoreal humans", "grey, desaturated or washed-out colour", "cold blue or fluorescent light", "flat even lighting", "black bars, borders, letterbox", "captions, subtitles, watermark", "phone interface, app buttons or on-screen UI", "garbled or misspelled lettering", "real brand names"
```

Add the shot's own failure modes first (wrong counts, a character who shouldn't be there, the wrong prop state). Don't list objects the frame has no reason to contain.

## Blueprint

```json
{
  "prompt_type": "claymation_scene_still",
  "objective": "One stop-motion claymation frame for a vertical short film: [who does what, where, at the start of the beat].",
  "reference_images_in_order": ["the [place] look still", "the [character] sheet", "the [product] clay sheet"],
  "references": [
    {"image": "the [place] look still", "use_for": "[place]. Take only its set design, light, colour and clay render; match its brightness and colour exactly. This is a new camera: [...]. Do not copy its framing, camera angle or anyone's pose."},
    {"image": "the [character] sheet", "use_for": "[name]'s exact design: [5-8 locked visible traits]", "adapt": "The left and middle panels are the body, the right panel is the head; show one complete character with a full head, not the sheet layout and not a headless body."}
  ],
  "canvas": {"image_count": 1, "aspect_ratio": "9:16", "orientation": "portrait"},
  "scene": "Viewpoint: [...]. FOREGROUND (sharp): [...]. MIDGROUND: [...]. BACKGROUND (soft): [...].",
  "identity": ["[name], [what she is], [age]: [locked traits]. She is clearly [age], not young: [...], exactly like the sheet portrait."],
  "camera": "[height, distance, normal or macro lens, what's sharp]",
  "lighting": "[sources, direction, warmth, mood: warm, rich, never grey]",
  "rendering": "[the rendering sentence above]",
  "format": "One 9:16 frame for a vertical short film, full-bleed edge to edge; important action in the central 70% of the frame, clear of the bottom and right edges.",
  "negative_prompt": ["[this shot's failure modes]", "...the base negatives"],
  "final_generation_instruction": "Create one 9:16 claymation frame: [one-sentence restatement of viewpoint, subjects, counts, prop state and light]."
}
```

## Fixing a still: edit, don't rewrite

When one thing is wrong in an otherwise good still (a prop too big, the wrong product print, an object that shouldn't be there yet), **edit that still** instead of writing a new prompt:

```json
{
  "prompt_type": "claymation_scene_still_edit",
  "objective": "Edit the first image so [the one change]. Nothing else changes.",
  "reference_images_in_order": ["scene N vK (the frame to edit)", "the [product] clay sheet (only when the product must be corrected)"],
  "edit": "[the change, described physically, including where things stay]",
  "keep": "The exact framing and crop, [the character's face, eyes, costume and pose], [the product and its print], [named set pieces], the warm light and the clay render. Do not zoom in or out.",
  "negative_prompt": ["[the old state]", "changed pose", "changed bottle", "misspelled text", "zoomed in or out", "captions, subtitles, watermark"]
}
```

Used on video-7 for: 52 (bottles with wrong labels → edit with the bottle sheet as the second ingredient), 58 (softgels already in the flipper → edit them out, see `look/product-in-hand-before-action.md`), 6 (tube too big → smaller tube).

When the fault is the idea itself (a confusing prop, a busy scene that will drift in video), write a simpler shot instead: 15 went from a printer tray with fanned pages and flowers to Penny holding two pages side by side against a plain blurred background. If a fault comes back twice, change the approach, not the wording, and add the lesson to `failure-locks.md`.
