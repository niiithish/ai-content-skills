# Clip prompts (Flow Omni, image to video)

One clip is one continuous shot, 4, 6 or 8 s, from one approved still. Save the prompt to `clips/clip-N/clip-Nx/prompts/clip-Nx-vK.md`: a one-line `#` heading naming the source still, then the prompt in a `text` code block. Flow reads only the code block.

## Defaults (only the user overrides them; a client brief asking for music or captions means they are added in the edit, not generated)

- **Locked frame.** The view never moves: no zoom, push, pan or tracking, even if the shot list names a camera move. Describe the fixed framing in positive terms.
- **Nobody is ever still.** Every visible character has timed action across the whole clip, plus secondary motion: blinking, breathing, ears, tails, fabric.
- **Scene audio only.** Room tone, weather, footsteps, objects, animals. No music, narration or dialogue. Characters who mustn't speak make only wordless sounds (gasps, grunts, laughs, sighs, hums). Music, voiceover and captions are added in the edit.
- **No overlays.** No captions, subtitles or on-screen graphics. Printed text that belongs to the scene (a newspaper, a label) stays exactly as it is in @image1.

## Ingredients

`@image1` is the approved still: the opening frame and the reference for the set, framing and light. `@image2…` are the sheets of every character in the shot. Without the sheets, faces drift as characters move (Daniel lost his moustache). If a starting pose differs from the still, say "@image1 is the reference for the set and light, not an exact first frame".

## Template

```text
[N]-second vertical 9:16 animated clip, one continuous shot with no cuts. @image1 is the opening frame and the reference for the set, framing and light. @image2 is [name]'s character sheet[; @image3 is ...]. Use each character sheet to keep that character's face, fur or clothing exactly on model in every frame, even when the character moves, turns or is small in the distance; [name] always has [2-3 identity locks that drift]. The sheets are references only: their left and middle panels show the body and the right panel shows the face. The sheets, their panels and their grey backgrounds never appear in the clip.

Opening: [who is where, pose, prop state, matching @image1].

Action: 0–[t] s: [specific physical action]. [t]–[t] s: [...]. [t]–[N] s: [...ending state]. [Exact counts and prop rules: "There is exactly ONE sandwich in the whole clip; it never multiplies."] [Where each character stays: "Daniel stays on the same spot by the street lamp from the first frame to the last."]

Everyone keeps moving naturally the whole time, with small secondary motion too: blinking, breathing, ears and tails moving, fur and fabric shifting.

Framing: The view is completely still, like a fixed security camera: exactly the same crop, angle and distance as @image1 from the first frame to the last. [Named landmarks] stay exactly the same size and position in the frame. Only the characters move.

Style: DreamWorks-inspired feature-animation CG exactly as in @image1: sculpted, appealing characters, large expressive eyes, soft groomed fur, shaped hair and fabric, rich but controlled colour. Every character keeps the exact face, fur pattern, clothing, proportions and size it has in @image1 and its sheet. Keep the [light] of @image1, not golden, not sunset.

Sound: only what you would hear standing in this place. [Ambience.] [Each sound tied to a visible action, in order.] [Name] never says any words; his voice is only wordless human sounds such as grunts, huffs, gasps, laughs, sighs and hums.

No music, no score, no soundtrack, no narration, no spoken words or dialogue. No captions, subtitles or on-screen graphics; any printed text in the scene stays exactly as it is in @image1.
```

## Writing the action

- Time every beat to the second, and end on a clear final state. A clip with nothing timed after 2 s fills the gap with random motion.
- Use one direction of travel per character. Turning around, spinning or doubling back often produces glitches.
- Have characters take props whole: a bite-by-bite eating beat duplicates the food. Write "takes the whole sandwich into his mouth in one go; the empty wax paper stays behind".
- A character who must stay put gets feet planted and a named spot. One who must not appear stays out of the text entirely (see `failure-locks.md`).
- Tie sound to what's visible. An off-screen sound source ("kittens crying inside") tends to get drawn in; if it's needed, keep it faint and name no creature, or add it in the edit from another clip.
- Weather words make weather sounds: "storm clouds" gave 5A thunder. Describe the sky in the still and describe only the wanted audio in the clip.
