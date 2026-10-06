# Clip prompts (claymation, Flow Omni image to video)

One clip is one continuous shot, 4 or 6 s (8 when a beat needs it), from **one approved still and nothing else**: no sheets as ingredients, the still already holds the faces. Save the prompt to `clips/clip-N/prompts/clip-N-vK.md`: a one-line `#` heading naming the source still, then the prompt in a `text` code block. Flow reads only the code block.

Clips play silent under the voiceover, so length comes from the shot's span in the voiceover, rounded to 4 or 6 s. Make 360p drafts of every clip first, then finals after the user approves them. The user reviews clips themselves.

## Rules

- **The still is the state before the action.** The clip adds the one action. If the still already shows the result (softgels in the flipper), the model invents a second action and the hands change shape: fix the still first (`scene-still.md`, edit).
- **Add nothing.** No character, object or prop that isn't in the still; nothing disappears, multiplies or swaps.
- **Characters act, the camera makes one gentle move** (a slow push-in, a slow slide). Lock the camera when hands handle a product, when props must not drift, or when there are no characters.
- **No characters in frame:** keep the still's exact framing (at most an almost imperceptible push-in), state that nothing enters or leaves the frame, and move only one small thing (a candle flame, dust motes, one layer rising). Never ask the camera to tilt or reveal what lies outside the still: it invents it (clip 4 v1: the cave vanished and something slid in).
- **Few, separate props held still.** Piles of paper or many similar props drift (pages vanish, angles change). Pin each prop: "exactly two pages, held in exactly the same place; they do not move, bend, swap, multiply or disappear".
- **Time every beat** ("0–2 s: ... 2–4 s: ...") and end on a held state.
- **Printed text stays** exactly as in the still.
- **Silent:** nobody speaks; only wordless sounds. No music, narration or captions.

## Template (characters acting)

```text
[N]-second vertical 9:16 stop-motion claymation clip, one continuous shot with no cuts. @image1 is the starting frame and the source of truth: the same characters, faces, clay costumes, set, props, colours and warm light as in @image1. Do not add any character, object or prop that is not in @image1. Printed text on labels, signs, papers and screens stays exactly as it is in @image1. No reference sheets, panels or grey backgrounds ever appear.

Shot (0–[N] s): [timed action: "0–2 s: ... 2–4 s: ..."; the expression and how it changes; where each prop stays]. Nobody says anything. Camera: [one gentle move, or "locked off, perfectly still"].

Everyone in frame is actively acting the whole time with clear, expressive performances, plus small secondary motion: blinking, breathing, little settles of the clay.

Style: handmade stop-motion claymation exactly as in @image1: hand-sculpted plasticine puppets and props with visible fingerprints, tool marks and slight asymmetry, a detailed miniature set, warm golden practical light with soft falloff, shallow macro depth of field. Animated on twos with the slightly stepped cadence and faint surface boil of real stop-motion. Never smooth CGI, never photoreal or live action: every character stays the same clay puppet from @image1 in every frame.

Sound: [ambience]; sounds of the visible actions only. Nobody speaks; only wordless sounds like sighs, gasps and laughs. No music, no score, no narration. No captions, subtitles or added on-screen text.
```

## Variant: product action from zero (clip 58 v2, approved)

The still shows the empty flipper; the clip only drops the softgels in:

```text
Shot (0–4 s): Penny's flipper starts empty, exactly as in @image1. Both flippers stay in the same place the whole time: her right flipper holds the tilted bottle still, her left flipper stays held out flat under the bottle mouth. 0–2 s: two orange-red softgels roll out of the bottle mouth, one after the other, and land on her empty flipper. That is the only thing that moves: no other softgels, the bottle does not move, her flippers do not change shape, turn or swap. 2–4 s: she glances down at the two softgels and her smile warms a little, then she holds still. Exactly two softgels at the end. Nobody says anything. Camera: locked off, perfectly still.

Small secondary motion only: blinking, breathing, a little settle of the clay.
```

(Replace the "Everyone in frame is actively acting" paragraph with the "Small secondary motion only" line whenever hands or props must hold still.)

## Variant: no characters (clip 4 v2, approved)

```text
4-second vertical 9:16 stop-motion claymation clip, one continuous shot with no cuts. @image1 is the starting frame and the source of truth, and the whole clip keeps exactly this framing and this set: [name every landmark in the still]. Nothing enters the frame from any side, nothing passes in front of the camera, nothing appears or disappears, and the [place] never changes. The "[label]" label stays exactly as it is in @image1. No reference sheets, panels or grey backgrounds ever appear.

Shot (0–4 s): [the big thing] stands still and solid; it does not move. 0–2 s: [one small thing moves]. 2–4 s: [it continues or settles]. The only things that move are [that thing] and a few tiny dust motes drifting in the warm light. No characters. Camera: an almost imperceptible slow push-in toward [target], staying on this same framing; no tilt, no pan, no cut.

Style: handmade stop-motion claymation exactly as in @image1: hand-sculpted plasticine set with visible fingerprints, tool marks and slight asymmetry, warm golden practical light with soft falloff, shallow macro depth of field. Animated on twos with the slightly stepped cadence and faint surface boil of real stop-motion. Never smooth CGI, never photoreal or live action.

Sound: [soft ambience]. Nobody speaks. No music, no score, no narration. No captions, subtitles or added on-screen text.
```

## Variant: held props, only the face acts (clip 15 v2, approved)

```text
@image1 is the starting frame and the source of truth: the same Penny, face, clay cardigan, background and warm light as in @image1. Exactly two pages the whole time, held in exactly the same place: the bright rose page in her left flipper and the faint rose page in her right flipper. The pages do not move, bend, change, swap, multiply or disappear, and the roses on them do not change. [...]

Shot (0–4 s): Only Penny's head and eyes move. 0–2 s: she glances from the bright page to the faint page. 2–4 s: she leans her head a little closer to the faint page, squints, and her brows knit in puzzlement, then she holds still. Nobody says anything. Camera: locked off, perfectly still.
```
