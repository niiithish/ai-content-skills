---
name: clay-video-production
description: The claymation / stop-motion layer for a short-form Google Flow video (default look: hand-sculpted plasticine puppets with fingerprints, warm golden practical light, jewel tones, shallow macro depth of field). It adds the look, the sheet, scene-still and clip prompt templates, the clay product treatment and the clay failure locks, on top of the shared video-production pipeline (layout, make.py, gates), which it loads. Use when a video plan's style is claymation, plasticine or stop-motion, when continuing a project whose AGENTS.md names this skill, or for a single claymation still or clip prompt. Not for 3D feature-animation CG (animated-video-production), photoreal ads (photoreal-video-production) or UGC talking heads.
---

# Clay Video Production

Handmade stop-motion claymation, 9:16, made with Google Flow. Built from the Mysa "Hidden Cause" VSL (Calvin, video-7): 64 stills and 64 clips, all approved, a 4-minute voiceover ad with clay penguins, an "inside the body" clay world and a clay version of the real product.

**Load `video-production` first.** It holds the pipeline: who runs which batch, the gates, the project layout, `init-project.sh` and every `make.py` command. This skill adds only what is specific to claymation. Start a project with:

```bash
bash <video-production-dir>/scripts/init-project.sh <client-folder> video-N --style clay
```

Files, loaded only when a phase needs them:

| File | Load it for |
|---|---|
| [references/sheets.md](references/sheets.md) | Character, group and product sheets in clay (phase 2) |
| [references/scene-still.md](references/scene-still.md) | Writing any still prompt (phase 3) |
| [references/clip-prompt.md](references/clip-prompt.md) | Writing any clip prompt (phase 4) |
| [references/failure-locks.md](references/failure-locks.md) | Before writing prompts, and whenever a result is rejected, with `video-production/references/failure-locks.md` |
| [references/look/](references/look/) | Before writing the first still of any project: 13 approved stills from video-7 at the quality bar, each with the exact prompt that made it (`<name>.jpg` + `<name>.md`). Open the images, read the prompts, and match their level of detail |
| [references/sheets/](references/sheets/) | The approved clay sheets (penguin character, a small creature, the clay product) with their prompts |

## Visual direction

The quality bar is `references/look/`: open those images before the first still. The default look, unless the brief or the user asks for something else:

- **Material:** hand-sculpted matte plasticine with visible fingerprints, thumb-pressed edges, tool marks and slight asymmetry. Costumes are clay too (pressed knit texture, pressed dot patterns, rolled gold trim). Eyes are big matte white clay discs with glossy black bead pupils and a tiny catch-light under heavy sculpted lids. Props and furniture are carved wood, clay, painted card and felt.
- **Light:** warm golden practical light (lamps, lanterns, window glow, candles) with soft falloff and rich shadows. Night scenes get one warm lamp as the key, never grey. Never flat, even or cool light.
- **Colour:** saturated jewel tones (emerald, teal, ruby, saffron, royal blue, dusty rose) against warm wood and ochre walls.
- **Camera:** shallow macro depth of field with creamy bokeh; extreme close-ups of hands and props; low floor-level angles; faces filling the frame; wide establishing shots with a crowd in depth.
- **Sets:** detailed, lived-in miniature sets (patterned wallpaper, carved headboards, quilts, mugs, framed art, plants, copper pans).
- **"Inside the body" cutaways:** a cosy clay world (warm caves, stacked clay layers, little builder creatures with tools, lanterns), never anatomy, organs, slime or diagrams.
- **Every line is a literal picture.** A metaphor becomes ONE instantly readable object (a stopwatch reading "90 SECONDS"), a stat becomes a crowd, a myth becomes bottles knocked into a bin.

**Avoid:** Pingu-style simple characters with tiny dot eyes, cold blue-tile flat sets, even lighting (a client reference had this look and the user rejected it), smooth CGI or 3D render, plastic or vinyl sheen, real feathers or fur, clinical medical diagrams.

Describe these visible qualities in every prompt; the word "claymation" alone gives a toy-like or CGI result.

## Reference sheets

See [references/sheets.md](references/sheets.md). In short:

- **Characters:** `character-generation`'s three-panel sheet, written as a hand-sculpted plasticine puppet (the animated mode's layout, with the clay material instead of CG).
- **Creatures** (the inside-world helpers): one three-panel sheet of one creature; stills say how many copies appear.
- **The product:** a clay version of the client's real product photo, made with `make.py sheet ... --ref <photo>`. The silhouette, cap, label layout and every word stay; the material becomes hand-rolled clay with print painted on the front only.
- **No environment sheets.** The first approved still of each place is its look still for every later shot there. Ask the image model for the change (a new camera, a new pose) from that still.

## Workflow notes (what worked on video-7)

- Stills go to the user in **batches of 10**; carry each batch's lessons into the next before writing it. Once the user says the style is locked, bigger batches are fine.
- Clips: **one approved still per clip**, silent, 4 or 6 s timed from the shot's span in the voiceover. Make 360p drafts of all clips, then finals after approval.
- The still shows the state **before** the action; the clip only adds the action (see `clip-prompt.md`).
- Keep scenes simple: few, separate props held still. Busy tables and paper piles drift in video.
- Edit in Resolve (`davinci-resolve` skill), captions in the edit; never in stills or clips.

## Review additions

On top of the shared checklist: the frame reads as real clay (fingerprints, matte surface, no plastic shine, not CGI); the product matches the clay product sheet (no wraparound label, correct cap); real-world object logic holds (knobs on drawer fronts, things face whoever uses them); and in a clip, nothing appears, disappears or multiplies.
