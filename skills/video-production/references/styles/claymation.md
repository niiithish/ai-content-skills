# Style Module: Claymation & Stop-Motion (`--style claymation`)

Handmade plasticine stop-motion (both full claymation and "halfway-clay" stylized miniature worlds). Open the approved quality-bar stills and clay sheets in `../look/claymation/` and `../look/claymation-sheets/` before writing the first still.

## 1. Visual Direction

Never rely on the word "claymation" alone — it produces smooth toy-like CGI. Describe the physical craft in every prompt:
- **Material:** Hand-sculpted matte plasticine with visible fingerprints, thumb-pressed edges, tool marks, and slight asymmetry. Costumes are sculpted clay (pressed knit texture, rolled trim). Eyes are matte white clay discs with glossy black bead pupils and a tiny catch-light under heavy sculpted lids. Props and furniture are carved wood, clay, painted card, and felt.
- **Light & Color:** Warm golden practical light (lamps, lanterns, window glow, candles) with soft falloff and rich shadows. Saturated jewel tones (emerald, teal, ruby, saffron, royal blue, dusty rose) against warm wood and ochre walls. Never flat, even, or cold blue fluorescent light.
- **Camera:** Shallow macro depth of field with creamy bokeh, extreme close-ups of hands/props, low miniature-scale angles.
- **Literal visual metaphors:** One instantly readable object per beat (a stopwatch reading `"90 SECONDS"`, a crowd for a stat, bottles knocked into a bin).
- **Avoid:** Pingu-style simple flat characters with tiny dot eyes, smooth glossy 3D CGI, plastic/vinyl sheen, real feathers/fur.

## 2. Reference Sheets

Use the shared layouts in `../sheets/` adapted for clay:
- **Characters & Creatures:** Three-panel sheet as a hand-sculpted plasticine puppet. For repeating inside-world helper creatures, make one sheet of one creature and state the count in stills.
- **Places:** Sheet for each recurring miniature set. Note: for tight macro/pillow close-ups filled by one surface, **omit the room look-still** so background lamps don't leak into the edges.
- **Clay Product Sheet:** Make from the client's real product photo (`make.py sheet ... --ref <photo>`). Keep the exact silhouette, cap, and label wording, transformed into hand-rolled matte clay with deep thumbprints, slightly uneven walls, and painted front-only print (no glossy wraparound plastic).

## 3. Still & Clip Rules

- **Still = state BEFORE the action.** If a still already shows the end state (e.g., capsules already in the hand), the video model invents extra actions and mutates hands.
- **Few, separate props held still.** Piles of loose papers or cluttered tables drift and multiply in video. Pin exact counts: `"exactly two pages, held in place; they do not bend, swap, multiply or disappear."`
- **No-character shots:** Keep framing locked (or imperceptible push-in), state `"nothing enters or leaves the frame"`, and move only one small element (flame, dust motes, one layer rising). Never tilt or pan outside the still.
- **Pain indicators:** Never write "red glow on jaw/cheeks" (reads as blush). Use hands holding the painful spot plus sculpted zig-zag pain marks; negate `"red on cheeks like blush"`.

## 4. Clip Prompt Template (Flow Omni, 4 or 6 s)

```text
[N]-second vertical 9:16 stop-motion claymation clip, one continuous shot with no cuts. @image1 is the reference and source of truth: the same hand-sculpted clay characters, faces, costumes, miniature set, props, colours and warm light. Do not add any character, object or prop not in @image1. Printed text on labels and signs stays exactly as in @image1. No reference sheets, panels or grey backgrounds ever appear.

Shot (0–[N] s): [timed action: "0–2 s: ... 2–4 s: ..."; expression change; exact prop counts and fixed positions]. Nobody says anything. Camera: [one gentle move, or "locked off, perfectly still" when handling products/props].

[Active characters: "Everyone in frame acts expressively with small secondary motion: blinking, breathing, subtle settles of the clay." | Held props/hands: "Small secondary motion only: blinking, breathing, subtle settle of the clay."]

Style: handmade stop-motion claymation exactly as in @image1 — hand-sculpted matte plasticine with visible fingerprints, tool marks and slight asymmetry, detailed miniature set, warm golden practical light, shallow macro depth of field. Animated on twos with the slightly stepped cadence and faint surface boil of real stop-motion. Never smooth CGI, never plastic sheen, never photoreal or live action.

Sound: [soft clay foley & ambience]; sounds of visible actions only. Nobody speaks; only wordless sounds. No music, no score, no narration. No captions, subtitles or added on-screen text.
```

## 5. Review Locks

- Frame reads as real matte clay (fingerprints visible, zero plastic shine, not smooth CGI).
- Real-world object logic holds (drawer knobs on fronts, props at real puppet scale).
- Zero multiplying/vanishing props or drifting camera reveals on no-character shots.
