# Style Module: Medical / Anatomical 3D CGI (`--style medical-cgi`)

Realistic 3D anatomical and supplement mechanism visualisations (gut lining, microbiome, skin layers, collagen fibers, blood vessels, oil absorption) — typically intercut with photoreal lifestyle B-roll (`photoreal.md`).

## 1. Biological & Physical Plausibility Lock (Critical)

The #1 user complaint on medical CGI is **"random BS that doesn't match the voiceover or breaks basic physics"** (e.g., blobs falling off the side of a floating skin slab, strands cutting and rejoining, unrecognizable abstract tunnels).

- **Every visual must directly illustrate the exact VO line.** Before writing a prompt, map each spoken phrase to a literal, recognizable physical action:
  - *"oil sinks in, ingredients don't"* → clear golden oil droplets soaking down into the top dermal layer while distinct active-ingredient blocks sit cleanly **on top** of the surface (never falling off the edge of an island!).
  - *"rebuilds collagen fibers"* → taut, interwoven amber-gold fibers thickening and tightening cleanly — never snapping and randomly rejoining.
  - *"supports the gut barrier"* → tightly sealed peach-coral intestinal villi walls with gentle drifting beneficial microbes inside the lumen.
- **No floating islands or falling-off-the-edge slabs** unless the plan explicitly asks for a 3D cross-section block. Even on a cross-section, keep all droplets/particles **contained strictly on the top surface or inside the layers** — explicitly negate `"liquid or particles spilling off the edges, floating island in empty void"`.
- **No accidental gore or clinical textbook ugliness:** Clean, premium luxury skincare/supplement CGI — warm translucent peach/coral tissue, amber-gold droplets, soft subsurface scattering, clean shallow macro DOF. Never blood, gore, slime, or neon sci-fi lasers unless the client reference demands it.

## 2. Visual Direction & Palette

- **Match client style references** (`assets/style-refs/`) when provided.
- **Problem vs. Solution contrast:**
  - *Problem state:* muted dusty beige, dry cracked surface, thin sparse fibers, dull lighting.
  - *Solution state:* warm hydrated peach-pink, rich amber/gold active liquid, plump dense tissue, brighter clean backlight.
- **Keep each shot distinct:** When a video has 4+ consecutive internal CGI shots, vary camera scale (wide lumen → macro barrier surface → extreme close-up absorption) and environment angle so the sequence doesn't look like the same shot repeated.

## 3. Clip Prompt Template (Flow Omni, 4 or 6 s)

```text
[N]-second vertical 9:16 premium 3D medical visualization CGI clip, one continuous shot with no cuts. @image1 is the reference for exact tissue texture, lighting, palette and composition.

Action (0–[N] s): [one clear, physically plausible biological motion matching the VO: "0–2 s: ... 2–4 s: ..."]. All droplets and particles stay strictly on or within the tissue layers; nothing spills off the edges, vanishes, or reverses.

Camera: [one smooth slow push-in or gentle lateral drift; locked framing if showing precise absorption].
Style: clean luxury supplement commercial 3D CGI, soft subsurface scattering, translucent organic materials, shallow macro depth of field. No gore, no blood, no neon sci-fi glow, no flat textbook arrows.
Sound: soft subtle organic ambience only. No speech, no music, no captions, no labels or on-screen text (add anatomy labels in FilmCraft).
```

## 4. Optional: Stylized "Inner World" Action Sequence (3D/Clay Ads ONLY)

Use **ONLY** when the user explicitly requests a playful Pixar/clay inside-the-body mini-action-movie (see `../look/inner-world/`). **Never use for photoreal/medical ads.**
- Product enters as a hero (e.g., golden softgel flying through a glowing tunnel), fixes the dull problem world into warm white-gold glow.
- **Generated transitions:** Pass both start still (`@image1`) and arrival world still (`@image2`) in one 8–10 s clip (`"no cut, no fade, no dissolve; one continuous fly-through transition inside the shot"`).
- Add any HUD/status words (`CLEAR`, `LOCKED`) in `filmcraft-edit`, never in the prompt.
