# Scene still prompts

A scene still is one composed 9:16 frame: the opening image of one clip. Write it as JSON in a `json` code block, saved to the shot's `prompts/scene-Nx-vK.md`. The model reads the JSON as text, so the field names only organise your thinking. Say each important thing once, in plain words.

## Before writing

- Look at every sheet you'll pass.
- Read the shot's row in `PLAN.md` and the lessons in `failure-locks.md`.
- Open two or three images in `look/` that are closest to this shot (store, home at night, close-up, group, product, cutaway) and read their `.md` prompts. Every new prompt is written to that level of detail; a thin prompt gives a flat, boring frame.
- The still shows the **first frame** of the clip: the starting pose and prop state before the main action. Put characters where the clip needs them to start.

## Ingredients, in this order

1. **The environment sheet** of the place, for its layout, furniture and render. Never another scene still as a look or composition reference (user rule, video-13: it degrades the image and copies its framing); write the place's light in words, the same in every still of that place.
2. **Character sheets**, one per character in frame.
3. **The product sheet** when the product is in frame (and any other prop sheet the plan lists). Items that belong to the room come from the environment sheet.

Never pass a rejected attempt as a reference, because its flaws get copied. Name each ingredient by its role ("the kitchen environment sheet", "the orange tabby cat sheet"), list them in `reference_images_in_order`, and give each one a `use_for`.

**Only the references this frame needs.** Before adding an image, name its one job (the product's label, its angle, its size in a hand, a face, this place's look) and check no other reference already does it. If it has no job of its own, leave it out, however relevant it looks or wherever you found it. An image from another scene brings its pose, outfit, room and light into this one (Aleo 127a v29: the product, its angle and its size in a hand were enough; a fourth still of a woman in a yellow robe from another shot was added only because it was in the folder). Fewer references, each with a clear job, beat more.

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
- **Light:** name the source as an object in the room, where it is, and what it does: which side of each face it lights, which side falls into shadow, what rims the hair, and what stays dark ("Night: the brass floor lamp beside the sofa, frame-right, is the key; it lights the right side of Carol's face and leaves the left in soft shadow; the side-table lamp rims her hair; the corners and the photo wall fall into warm darkness."). Start from the place's Light line in the plan. Keep it to two or three sentences: a long light paragraph pulls poses and props off what the prompt asks (Calvin video-13 light test, 2026-10-21). Wide shots need the strongest push ("the room is dim except two pools of lamplight"). Shadows are wanted; what's banned is grey, cold or flat light. A light that isn't in the frame or named ("warm lamplight from the living room") gives an evenly lit, flat frame. Default warm: lamps, window sun, string lights, candles, golden bokeh. A store is "bright and inviting, warm-white overhead light plus soft daylight from skylights, never cold or fluorescent".
- **Render:** "Fully 3D rendered high-end Disney/Pixar-style feature-animation CG: sculpted, appealing, slightly stylized characters with big glossy expressive eyes and catch-lights, soft subsurface glow on skin, big sculpted groomed hair with clumped curls, detailed fabric weave and stitching, rich saturated jewel-tone colour, polished like a theatrical release. Not 2D, no outlines, not photographic, not plastic or toy-like." (For a project with a different agreed look, describe that look's visible qualities instead.)
- **Format:** "one 9:16 frame for a vertical short film; important action in the central 70% of the frame". Never name a social app or mention a phone interface.

## Who is where: blocking and left/right

Two people sharing a place across many stills (a couple in bed over ten shots) swap sides from still to still, and "left" gets read from the wrong point of view, unless every prompt pins them to the room.

- **Pin people to the set, not the frame.** Each place where two or more sheet characters share shots has a Blocking line in the plan, copied to the Environments table in `AGENTS.md`: "Bedroom: Mark on the window side of the bed (tall window, green armchair); Anna on the door side (brass lamp, her nightstand with the book)." Every still there names each side by its landmark: "Mark lies on the window side of the bed, next to the green armchair; Anna on the lamp side."
- **Then say where that lands in this frame, as the viewer sees it.** Work it out from where the camera stands: from the foot of the bed facing the headboard, the window side is frame-left; from the window, Mark is in the foreground. Write "on the LEFT of the picture as the viewer sees it (frame-left)". Never a bare "left" or "right", and never "on his left" for a place in the frame: the model reads it from the character's side, which flips whenever he faces the camera.
- **A character's own hands and sides** go by landmark or camera, not by body: "the hand nearer the camera", "the hand on the window side". If the body side matters (a ring hand): "his own right hand, which is on the left of the picture because he faces us".
- **Keep the camera on one side** of the line between the two people for the whole scene (the 180° rule), so they keep their frame sides from shot to shot. A reverse angle across the line flips both: write the new frame sides out, and keep the landmark sentence the same.
- **Name the traits with the position,** in the same sentence: "Mark (the man: short dark beard, navy T-shirt) on the window side … Anna (the woman: long auburn hair, lilac nightgown) on the lamp side". The model matches each sheet to a position through these traits.
- **Check every still before approving:** who is on which landmark side, and which hand holds what. A swap is a reject: regenerate with the sides in `scene` and `final_generation_instruction`. Never mirror-flip the image instead: text, the room's layout and one-sided details (a hair part, a ring, a watch) flip with it.

## Negative list

Keep it to concrete failure modes for this shot:
- wrong counts
- a character who shouldn't be there
- the wrong prop state
- the 2D or photoreal drift
- the sheet layout, a headless body, a grey studio backdrop
- "looking at the camera, posing for the camera" when the characters should watch something in the scene
- grey, desaturated or washed-out colour; cold blue or fluorescent light; flat lighting, an evenly lit face with no shadow side, every part of the room equally bright (or golden light, when the project's look is neutral daylight)
- "photoreal humans", "plastic toy look", "a young woman" for an older character
- captions, watermarks, app UI, garbled or misspelled lettering

Don't list an object the positive text never mentions and that the frame has no reason to contain. In clip prompts and in positive text, naming an absent thing tends to summon it.

## Base negatives (the warm Pixar look)

Append these to every still's own negatives:

```json
"three-panel sheet layout", "headless body", "grey studio background", "2D cartoon, outlines", "photoreal humans", "plastic toy look", "grey, desaturated or washed-out colour", "cold blue or fluorescent light", "flat lighting", "an evenly lit face with no shadow side", "every part of the room equally bright", "light with no visible source", "captions, subtitles, watermark", "on-screen UI overlays or app buttons", "blank, empty or plain glowing screens", "garbled or misspelled lettering", "logos of real companies", "blank unlabelled packaging", "every product plain white"
```

## Text in the frame

In-world text is welcome; overlays are not. Anything that carries print in real life (a newspaper, a sign, a book cover, packaging, a label, a shop front) gets short, readable, plausible text written into the prompt in quotes: a headline, a brand name, a product line. Invent fictional brands; use a real one only when the user supplies it. Keep each surface to a few words and leave fine print soft. Stores are stocked like a real store: each product has its own shape and a readable fictional label ("Silk Lotion", "Honey Oat", "Vanilla Glow", a "Bath & Body" aisle sign, price tags on the shelf edges), never plain colour blocks or blank jars. Story props carry their words ("DIVORCE AGREEMENT" on the papers). **Screens are never blank.** Every phone, TV, laptop or tablet whose screen faces the camera shows real content written into the prompt: a text-message notification or thread (a round contact photo, the sender's name in quotes, a short message of 2–5 words in quotes, "large type"), a show or game on the TV, a video call, or the client's real web page from a screenshot, typed by touch, never a mouse pointer. A blank white glow reads as a mistake (video-13). A screen turned away from the camera needs nothing; a TV that the story needs off is dark, said in the shot. Never captions, subtitles, watermarks or on-screen graphics laid over the frame. Say which surface each text is on, and check the spelling in the render before approving.

**Other brands' products** (a rival bottle, shelf stock, a jar on her vanity, the "old" product that failed her) get a made-up brand name and their own colour, written into the prompt for each one in focus: "a frosted sage-green glass jar labelled 'Verdelle' in cream serif", "an amber pump bottle, black cap, 'HONEY OAT' label". Left unsaid, the model whitewashes them: plain white bottles with blank labels, the same white as the client's product. The rules:
- **A colour for every product, from a small set.** Pick 2–4 package colours that sit in the scene's palette (sage, terracotta, amber glass, navy, blush, cream, matte black) and spread them over the products; a shelf can repeat them. Not a rainbow, not neon, not all white.
- **Never the client's colours or shape** on a rival: it must not read as our product. With a white client bottle, rivals are any colour but white.
- **Short readable names** where in focus (one invented brand word plus 1–2 words of product line), soft where out of focus. Real brands only when the user supplies them.

## Blueprint

```json
{
  "prompt_type": "animated_scene_still",
  "objective": "One fully 3D animated frame for a vertical short film: [who does what, where, at the start of the beat].",
  "reference_images_in_order": ["the [location] environment sheet", "the [character] sheet", "..."],
  "references": [
    {"image": "the [location] environment sheet", "use_for": "the room's exact layout, furniture, materials and render; the light, people and camera are described below. Never a scene still here."},
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
