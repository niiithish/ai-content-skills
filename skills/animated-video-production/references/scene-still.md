# Scene still prompts

A scene still is one composed 9:16 frame: the opening image of one clip. Write it as JSON in a `json` code block, saved to the shot's `prompts/scene-Nx-vK.md`. The model reads the JSON as text, so the field names only organise your thinking. Say each important thing once, in plain words.

## Before writing

- Look at every reference you'll pass: sheets, the location's hero still, and any approved still whose composition you're reusing.
- Read the shot's row in `PLAN.md` and the lessons in `failure-locks.md`.
- The still shows the **first frame** of the clip: the starting pose and prop state before the main action. Put characters where the clip needs them to start.

## Ingredients, in this order

1. **The look still:** the location's hero still, which fixes light, brightness, colour and render style. For a location's first still, use the environment sheet instead.
2. **The composition still** (optional): an approved still whose framing you want. Say exactly what to take from it ("composition only") and what to ignore ("ignore its dark lighting").
3. **Character sheets**, one per character in frame.
4. **Prop sheets** for props whose design matters.
5. **The environment sheet**, when no hero still exists yet.

Never pass a rejected attempt as a reference, because its flaws get copied. Name each ingredient by its role ("the look still", "the orange tabby cat sheet"), list them in `reference_images_in_order`, and give each one a `use_for`.

## Required sentences

- **Three-panel character sheets:** "The left and middle panels are the body, the right panel is the head; show one complete character with a full head, not the sheet layout and not a headless body."
- **A group sheet** (several full characters in a lineup): "The scene shows those same N characters."
- **Scale**, whenever two or more characters share the frame. Use comparisons: "the cat's back is at the man's shin", "each kitten is a third of the cat's size".
- **Counts, spelled out:** "EXACTLY THREE kittens, all three clearly visible side by side". Also add the wrong counts to the negative list ("two kittens", "four kittens").
- **Frame share** for any subject that must read clearly: "fills the lower-left third".
- **Light:** the physical source, its direction, and brightness ("soft, fairly bright daylight from the broken window on the left; not dark, not night, not golden").
- **Render:** "Fully 3D rendered feature-animation CG exactly like the look still: soft 3D shading, sculpted appealing shapes, big glossy expressive eyes, soft groomed stylized fur. Not 2D, no outlines, not photographic."
- **Format:** "one 9:16 frame for a vertical short film; important action in the central 70% of the frame". Never name a social app or mention a phone interface.

## Negative list

Keep it to concrete failure modes for this shot:
- wrong counts
- a character who shouldn't be there
- the wrong prop state
- the 2D or photoreal drift
- the sheet layout, a headless body, a grey studio backdrop
- golden light
- captions, watermarks, app UI, garbled or misspelled lettering

Don't list an object the positive text never mentions and that the frame has no reason to contain. In clip prompts and in positive text, naming an absent thing tends to summon it.

## Text in the frame

In-world text is welcome; overlays are not. Anything that carries print in real life (a newspaper, a sign, a book cover, packaging, a label, a shop front) gets short, readable, plausible text written into the prompt in quotes: a headline, a brand name, a product line. Invent fictional brands; use a real one only when the user supplies it. Keep each surface to a few words and leave fine print soft. Never captions, subtitles, watermarks, app UI or on-screen graphics. Say which surface each text is on, and check the spelling in the render before approving.

## Blueprint

```json
{
  "prompt_type": "animated_scene_still",
  "objective": "One fully 3D animated frame for a vertical short film: [who does what, where, at the start of the beat].",
  "reference_images_in_order": ["the look still", "the [character] sheet", "..."],
  "references": [
    {"image": "the look still", "use_for": "the exact look of [location] and its light: [source, direction, brightness, key landmarks]. Match its brightness and colour exactly."},
    {"image": "the [character] sheet", "use_for": "[name]'s exact design", "adapt": "Left and middle panels are the body, right panel is the head; show one complete [character] with a full head, not the sheet layout."}
  ],
  "canvas": {"image_count": 1, "aspect_ratio": "9:16", "orientation": "portrait"},
  "scene": "[Viewpoint, then subjects with position, frame share, pose, gaze, contact points and prop state, then the background landmarks from the look still.]",
  "identity": ["[name]: [3-6 locked visible traits from the sheet, including scale]"],
  "camera": "[height in cm or m, distance, angle, normal lens, what's sharp]",
  "lighting": "[source, direction, brightness, shadow softness]; not golden.",
  "rendering": "Fully 3D rendered DreamWorks-inspired feature-animation CG exactly like the look still: [visible qualities]. Not 2D, no outlines, not photographic.",
  "negative_prompt": ["[concrete failure modes for this shot]", "three-panel sheet layout", "headless body", "grey studio background", "golden light", "garbled or misspelled lettering", "phone interface, app buttons or on-screen UI", "captions or watermark"],
  "final_generation_instruction": "Create one 9:16 fully 3D animated frame, [one-sentence restatement of viewpoint, subjects, counts, prop state and light]."
}
```

## Fixing a rejected still

Change only what was wrong, in a new version. Put the fix where the model will weigh it: in `scene` and `final_generation_instruction`, not only in the negative list. If the same fault comes back twice, change the approach rather than the wording: a different viewpoint, a composition still, or a start pose that avoids the fault. Then add the lesson to `failure-locks.md`.
