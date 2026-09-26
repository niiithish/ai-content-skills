# Clip prompts (Flow Omni, image to video)

One clip is one continuous shot, 4, 6, 8 or 10 s, from one approved still. Save the prompt to `clips/clip-N/clip-Nx/prompts/clip-Nx-vK.md`: a one-line `#` heading naming the source still, then the prompt in a `text` code block. Flow reads only the code block.

## Defaults (only the user or the plan overrides them; a client brief asking for music or captions means they are added in the edit, not generated)

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

## Characters who speak on camera

When the plan has characters saying their own lines to camera (mascot ads, talking animals), Flow generates the voice and lip-sync inside the clip. This replaces the "scene audio only" and "locked frame" defaults for those clips; everything else above still holds.

- **One whole sentence or more per clip, never half of one.** The clip ends 0.5–2 s after the last word, up to 10 s (lengths from `plan.py voiceover --on-camera`). A longer line follows the plan's split into chained clips.
- **The speech starts on the first frame** and runs in one continuous delivery with no gaps. Big action happens under the speech and never pauses it.
- **After the last word, nothing new happens.** No sparkles, extra gags or new effects: the character holds the final expression to the end.
- **Quote the line once, in Dialogue only.** In Action, time beats in seconds, never by quoting the line's words: quoted words get spoken again ("growing… growing").
- **The voice is the loudest sound.** No thuds, stamps, slams or impacts while anyone speaks; they make the model restart the word.
- **Mood comes from the plan.** Never write a mood word the plan doesn't want. "Deadpan stare", "yikes face" or "awkward grin" give a sad or flat character for the whole clip. Say the expression positively and say it holds to the last frame.
- **The camera makes one slow, smooth move** (push-in, drift, arc, a slow track as the character walks), never a crash zoom, whip or shake.
- **Make it big but clean.** Each line gets a playful visual idea that builds on its words: something appears, grows or transforms. Don't add dirt on the character, fire or destruction the plan didn't ask for.
- **Voices** name an adult age and pitch and say "never a child" (mascots otherwise sound like kids). Repeat each character's voice description word for word in all their clips.
- Filter-sensitive words (intimate body parts, "lube") can make Flow return a finished clip with the speech and action stripped. When a clip comes back silent, soften that wording in Action and Setting; if it's in the client's line, ask the user before changing a word of it.

Template (replace the Framing and Sound paragraphs of the main template; the Style paragraph stays):

```text
[N]-second vertical 9:16 animated clip, one continuous shot with no cuts. @image1 is the opening frame and the reference for the set, the character and the light. @image2 is [name]'s character sheet. Use it to keep [name] exactly on model in every frame; [name] always has [identity locks]. The sheet is a reference only; the sheet, its panels and its grey background never appear in the clip.

[Chained clips only] Continuity: this clip continues straight on from the previous shot with no cut. @image1 is the exact frame where the previous shot cuts: the first frame matches @image1 exactly in pose, expression, framing, camera position, light and colour, and the camera keeps moving the way it was already moving, [the move], at the same slow speed, with no jump, no reframe and no change in the look.

Opening: [who is where, exactly as in @image1].

Dialogue: [Name] starts speaking on the very first frame and says this line, word for word, in English, in one continuous, flowing delivery at a brisk, natural pace, with no pauses or gaps between phrases, the mouth clearly lip-synced to every word: "[the exact line]" The line takes about [t] seconds. The speech never pauses or waits for the action: [he/she/they] keep talking through every movement and effect. The spoken line above is the only dialogue in this clip; nothing below is spoken. Every word is said exactly once, in order: no word or phrase is repeated, restarted or stuttered, and no sound effect interrupts the voice. Voice: [age, pitch, texture, attitude], American English. Clearly a grown adult, never a child, never a squeaky or high-pitched cartoon voice. Only [name] speaks; no other voices.

Action, happening while [name] speaks and never pausing the speech. From the first frame to about [t] seconds: [action]. From about [t] to [t] seconds: [action]. From about [t] seconds to the last word at about [t] seconds: [action, ending state].

One take: everything changes gradually and only forward. Once [the effect] appears it stays and keeps building until the clip ends: it never vanishes or jumps back, and [name] never snaps back to the opening pose. @image1 is only the first frame, never a frame to return to.

Ending: after the last word there is no new action and no new effect. [Name] just holds the final expression until the clip ends: [expression and pose].

Expression: [Name] [the plan's expression, e.g. smiles warmly] the whole clip, from the first frame to the last, and keeps it after the last word until the clip ends.

Performance: big, snappy, cartoony comedy acting with squash and stretch and strong expressions. [Name] keeps moving the whole time: blinking, breathing, gestures, the eyes coming back to the lens.

Camera: one slow, smooth, continuous [push-in / drift / arc] for the whole clip. The camera never cuts, never jumps, never shakes and never returns to the opening framing. [Name] stays large, filling about [share] of the frame width, face in the upper half of the frame.

Setting: [the place of @image1], staying consistent in layout and light.

Style: [as in the main template]. No sparkles, glitter, twinkles or shimmering particles anywhere in the clip.

Sound: [Name]'s spoken line, clearly the loudest sound; [soft ambience]; [soft sounds tied to visible actions, never thuds or impacts under the speech].

No music, no score, no soundtrack, no narration. No captions, subtitles or on-screen graphics or text.
```
