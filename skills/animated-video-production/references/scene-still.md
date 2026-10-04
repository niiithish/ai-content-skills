# Scene still prompts

A scene still is one composed 9:16 frame: the opening image of one clip. Write it as JSON in a `json` code block, saved to the shot's `prompts/scene-Nx-vK.md`. The model reads the JSON as text, so the field names only organise your thinking. Say each important thing once, in plain words.

## Before writing

- Look at every reference you'll pass: sheets, the location's hero still, and any approved still whose composition you're reusing.
- Read the shot's row in `PLAN.md` and the lessons in `failure-locks.md`.
- Open two or three images in `look/` that are closest to this shot (store, home at night, close-up, group, product, cutaway) and read their `.md` prompts. Every new prompt is written to that level of detail; a thin prompt gives a flat, boring frame.
- The still shows the **first frame** of the clip: the starting pose and prop state before the main action. Put characters where the clip needs them to start.

## Ingredients, in this order

1. **The look still:** the location's hero still, which fixes light, brightness, colour and render style. For a location's first still, use the environment sheet instead. Its `use_for` says light, colour and render **only**, and names what must differ: "Take only its light, colour and render. This is a new camera: [where it stands, what fills the frame]. Do not copy its framing, camera angle or anyone's pose." Otherwise the model hands back the look still with small changes (pie heist 2b and 3a came back as scene 1 again).
2. **The composition still** (optional): an approved still whose framing you want. Say exactly what to take from it ("composition only") and what to ignore ("ignore its dark lighting").
3. **Character sheets**, one per character in frame.
4. **Prop sheets** for props whose design matters.
5. **The environment sheet**, when no hero still exists yet.

Never pass a rejected attempt as a reference, because its flaws get copied. Name each ingredient by its role ("the look still", "the orange tabby cat sheet"), list them in `reference_images_in_order`, and give each one a `use_for`.

## Required sentences

- **Three-panel character sheets:** "The left and middle panels are the body, the right panel is the head; show one complete character with a full head, not the sheet layout and not a headless body."
- **A group sheet** (several full characters in a lineup): "The scene shows those same N characters."
- **Facing and eyeline, for every character.** Say which way the body and the face point *in the frame* (towards camera, back to camera, profile facing left or right, three-quarter back) and what they look at, and where that thing is in the frame. If the thing they want sits deeper in the picture than they do, they face away from the camera: we see their backs or the backs of their heads, as in an over-the-shoulder shot ("Rocco, back three-quarters to camera in the lower left, head turned to the upper right, staring at the pie on the sill"). Characters face the camera only when the plan says so; left alone, the model poses them for the camera like the sheets, looking out of the picture instead of at the target.
- **Scale**, whenever two or more characters share the frame. Use comparisons: "the cat's back is at the man's shin", "each kitten is a third of the cat's size".
- **Counts, spelled out:** "EXACTLY THREE kittens, all three clearly visible side by side". Also add the wrong counts to the negative list ("two kittens", "four kittens").
- **Frame share** for any subject that must read clearly: "fills the lower-left third".
- **Layers:** write `scene` as Viewpoint, then FOREGROUND (sharp: a table with labelled props, a hand, a product), MIDGROUND (the subject, pose, expression), BACKGROUND (named lived-in set dressing: wallpaper, plants, framed photos, a brass lamp, a magenta throw; or a stocked shelf). Every frame has depth.
- **Expression, described physically:** not "sad" but "brows drawn together, mouth turned down, a faraway look toward the rainy window". Say what the expression is hiding when that's the beat ("a strained polite smile while her brows pinch").
- **Age, for older characters, every time:** "She is clearly 63, not young: crow's feet, laugh lines, gentle lines under the eyes, a mature lived-in face exactly like the sheet portrait." Without it, close-ups come back as a 30-year-old.
- **Background people** do something real and named (reading a label, reaching for a bottle, laughing over wine), are given a size in the frame ("each about one tenth of the frame height"), a distance and a facing, and don't look at the camera. Every character the beat needs is in the first still, with their sheet passed.
- **Light:** the physical sources, direction, brightness and warmth, and the mood ("Night: one warm brass floor lamp as the key, pooling amber light on Carol, the room in warm moody shadow, raindrops catching the lamp light. Sad but rich and warm, never grey."). Default warm: window sun, rim light on hair, warm practicals, candles, string lights, golden bokeh. A store is "bright and inviting, warm-white overhead light plus soft daylight from skylights, never cold or fluorescent".
- **Render:** "Fully 3D rendered high-end Disney/Pixar-style feature-animation CG: sculpted, appealing, slightly stylized characters with big glossy expressive eyes and catch-lights, soft subsurface glow on skin, big sculpted groomed hair with clumped curls, detailed fabric weave and stitching, rich saturated jewel-tone colour, polished like a theatrical release. Not 2D, no outlines, not photographic, not plastic or toy-like." (For a project with a different agreed look, describe that look's visible qualities instead.)
- **Format:** "one 9:16 frame for a vertical short film; important action in the central 70% of the frame". Never name a social app or mention a phone interface.

## Negative list

Keep it to concrete failure modes for this shot:
- wrong counts
- a character who shouldn't be there
- the wrong prop state
- the 2D or photoreal drift
- the sheet layout, a headless body, a grey studio backdrop
- "looking at the camera, posing for the camera" when the characters should watch something in the scene
- grey, desaturated or washed-out colour; cold blue or fluorescent light; flat lighting (or golden light, when the project's look is neutral daylight)
- "photoreal humans", "plastic toy look", "a young woman" for an older character
- captions, watermarks, app UI, garbled or misspelled lettering

Don't list an object the positive text never mentions and that the frame has no reason to contain. In clip prompts and in positive text, naming an absent thing tends to summon it.

## Base negatives (the warm Pixar look)

Append these to every still's own negatives:

```json
"three-panel sheet layout", "headless body", "grey studio background", "2D cartoon, outlines", "photoreal humans", "plastic toy look", "grey, desaturated or washed-out colour", "cold blue or fluorescent light", "flat lighting", "captions, subtitles, watermark", "phone interface, app buttons or on-screen UI", "garbled or misspelled lettering", "store logos or real brand names"
```

## Text in the frame

In-world text is welcome; overlays are not. Anything that carries print in real life (a newspaper, a sign, a book cover, packaging, a label, a shop front) gets short, readable, plausible text written into the prompt in quotes: a headline, a brand name, a product line. Invent fictional brands; use a real one only when the user supplies it. Keep each surface to a few words and leave fine print soft. Stores are stocked like a real store: each product has its own shape and a readable fictional label ("Silk Lotion", "Honey Oat", "Vanilla Glow", a "Bath & Body" aisle sign, price tags on the shelf edges), never plain colour blocks or blank jars. Story props carry their words ("DIVORCE AGREEMENT" on the papers). A phone screen shows the client's real web page from a screenshot, typed by touch, never a mouse pointer. Never captions, subtitles, watermarks, app UI or on-screen graphics. Say which surface each text is on, and check the spelling in the render before approving.

## Blueprint

```json
{
  "prompt_type": "animated_scene_still",
  "objective": "One fully 3D animated frame for a vertical short film: [who does what, where, at the start of the beat].",
  "reference_images_in_order": ["the look still", "the [character] sheet", "..."],
  "references": [
    {"image": "the look still", "use_for": "only the look of [location] and its light: [source, direction, brightness]. Match its brightness and colour exactly. This is a new camera: [where it stands, what fills the frame]. Do not copy its framing, camera angle or anyone's pose."},
    {"image": "the [character] sheet", "use_for": "[name]'s exact design", "adapt": "Left and middle panels are the body, right panel is the head; show one complete [character] with a full head, not the sheet layout."}
  ],
  "canvas": {"image_count": 1, "aspect_ratio": "9:16", "orientation": "portrait"},
  "scene": "[Viewpoint. FOREGROUND (sharp): ... MIDGROUND: ... BACKGROUND: .... Each subject with position, frame share, pose, which way the body and face point in the frame, what they look at and where it is, contact points and prop state, then the background landmarks this camera sees.]",
  "identity": ["[name] ([look]), [age]: [3-6 locked visible traits from the sheet, including scale]. She is clearly [age], not young: [age marks], exactly like the sheet portrait."],
  "camera": "[height in cm or m, distance, angle, normal lens, what's sharp]",
  "lighting": "[sources, direction, brightness, warmth and mood: warm, rich, never grey]",
  "rendering": "[the Render sentence above]",
  "format": "One 9:16 frame for a vertical short film; important action in the central 70% of the frame, clear of the bottom and right edges.",
  "negative_prompt": ["[concrete failure modes for this shot]", "...the base negatives above"],
  "final_generation_instruction": "Create one 9:16 fully 3D animated frame, [one-sentence restatement of viewpoint, subjects, counts, prop state and light]."
}
```

## A new angle or expression of an approved frame: edit it

A new framing or expression of a locked character is an **edit of an approved still**, never a fresh description: a fresh description of a known face drifts (younger, slimmer, photoreal, wrong hair colour). Pass that one still as the only reference and change only the one thing:

```json
{
  "prompt_type": "animated_scene_still_edit",
  "objective": "Edit this image. Change ONLY [the expression / where the eyes look / the one prop]. Everything else stays pixel-identical: same framing, same crop, same head size, same camera, same render.",
  "reference_images_in_order": ["scene N vK (the frame to edit)"],
  "edit": "[the one change, described physically]",
  "keep": "The exact framing and crop of the image, the face shape, features, hair, outfit, background, colours, light and the stylized 3D cartoon render. Do not zoom out, do not show more of the body.",
  "negative_prompt": "zoomed out, full body, bigger head, smaller body, photorealistic, real human, [the old expression]"
}
```

- Keep the close-up's framing: asking an edit of a close-up to pull back gives a giant head on a small body.
- When the user liked a take and one thing is off (cart too far, a mouse pointer on a phone), pass that take and change only that thing.
- A new look of a character (before/after) is an edit of the approved sheet: keep face, eyes, nose, mouth and hair colour; change hair styling, outfit, expression and a little weight.
- For likeness across many stills of one look, pass the sheet plus one approved still of that look, and describe the character mildly. Piling on weight or age words overshoots ("not heavier, older or slimmer than the approved stills").

## Fixing a rejected still

Change only what was wrong, in a new version. Put the fix where the model will weigh it: in `scene` and `final_generation_instruction`, not only in the negative list. If the same fault comes back twice, change the approach rather than the wording: a different viewpoint, a composition still, or a start pose that avoids the fault. Then add the lesson to `failure-locks.md`.
