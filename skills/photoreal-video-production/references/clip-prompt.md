# Clip prompts: photoreal (Flow Omni, image to video)

One clip is one continuous shot, 4, 6, 8 or 10 s, from one approved still. Save the prompt to `clips/clip-N/clip-Nx/prompts/clip-Nx-vK.md`: a one-line `#` heading naming the source still, then the prompt in a `text` code block.

Keep it short and plain. The prompts that worked in the Mysa video were a few lines: what happens, timed; then the fixed lines. Long lists of things that must not happen made them happen.

## Ingredients

`@image1` is the approved still: the opening frame. Then the sheet of every person in the shot, then the product sheet when the product is on screen, then any small prop whose look must hold (a softgel). Say what each one is for and what to ignore ("ignore that image's backdrop").

## Template

```text
Vertical 9:16 short film shot, starting exactly from @image1.

[One or two sentences: who does what, and how they feel, matching the voiceover line over this shot.]

[For a beat with steps, timed at normal real-life speed:]
0-[t] s: [...]. [t]-[t] s: [...]. [t]-[N] s: [...ending state].

[Counts and continuity: "Only one softgel, as in @image3; no other softgels appear." "There is one sheet of paper on the desk the whole time."] [Eyeline: "She looks at the screen, never at the camera."]

Camera: a very slow, steady push-in, barely noticeable, the same angle throughout. [or: Locked-off camera, framing as in @image1. (then a slow zoom is added in post)]
Natural real-life motion at normal speed, real skin and fabric. Ambient room sound only; nobody speaks, no music. No text, captions or graphics on screen. One continuous shot, no cuts.
[The woman looks like @image2[ and the man like @image3].] [The Mysa bottle keeps the exact label from @image4: quote the label text; lettering never changes.]
```

## Writing the action

- **The feeling is part of the action.** Write the emotion the voiceover line needs ("tired and frustrated", "relieved, a small smile"). A default happy face on a problem line is a reject.
- **Hard physical beats get 6 s and timed steps.** Taking a softgel, for example:
  - 0–2 s: she places the single softgel on her tongue; it stays visible until her lips close over it, and never vanishes or shrinks first;
  - 2–5 s: she lifts the glass, takes two or three real gulps, and the water level visibly drops by about a third while her throat moves;
  - 5–6 s: she sets down the glass, now clearly less full.
- **Count what matters** in the prompt ("only one softgel", "exactly two softgels in her palm") and again in review.
- **Real-life logic.** A monitor faces its user; a person drinks from a glass that was on the table; a paper that is handed over leaves one hand and arrives in the other.
- **Intimacy.** Google's filter takes down the finished clip (`NOT_FOUND`, then `PROMPT_REJECTED` once it vanishes on a second account) for night + pyjamas + bed however mild the action. Evening + knitwear + armchair or sofa + laughing together passes. Aim for romantic, not sexual, and put the couple in a living room, not a bedroom.
- **Camera.** Never fully static. If the push-in wobbles or reframes, the next version is locked-off, and the slow zoom goes on in post (ffmpeg `zoompan`, about 1.00 → 1.06 over the clip) on the final.
