---
name: animated-video-production
description: The stylized 3D animation layer for a short-form Google Flow video (DreamWorks-style, Pixar-style feature-animation CG). It adds the look, the scene-still and clip prompt templates, product mascots, characters speaking on camera and the animated failure locks, on top of the shared video-production pipeline (layout, make.py, gates), which it loads. Use when a video plan's style is 3D feature animation, when continuing a project whose AGENTS.md names this skill, or for a single animated scene still or clip prompt. Not for claymation (clay-animation-video-prompt), photoreal ads (photoreal-video-production) or UGC talking heads.
---

# Animated Video Production

Stylized 3D feature-animation CG, 9:16, made with Google Flow.

**Load `video-production` first.** It holds the pipeline: who runs which batch, the gates, the project layout, `init-project.sh` and every `make.py` command. This skill adds only what is specific to animation. Start a project with:

```bash
bash <video-production-dir>/scripts/init-project.sh <client-folder> video-N --style animated
```

Files, loaded only when a phase needs them:

| File | Load it for |
|---|---|
| [references/scene-still.md](references/scene-still.md) | Writing any still prompt (phase 3) |
| [references/clip-prompt.md](references/clip-prompt.md) | Writing any clip prompt (phase 4), including characters who speak on camera |
| [references/failure-locks.md](references/failure-locks.md) | Before writing prompts, and whenever a result is rejected, with `video-production/references/failure-locks.md` |

## Reference sheets

- Follow `character-generation`, `environment-generation` and `prop-generation` in their animated mode: one landscape image, stylized CG, neutral light, and no grey studio backdrop leaking into scenes.
- **Hero still per environment.** Video 1 of the Milo project lost most of its rejected versions to shots in a location that had no hero still. A still that lists the hero takes it for light and render only: it must not hand over its framing or poses (see `scene-still.md`).
- **Product mascots** (a real product with a face and limbs): image models redraw logos and labels wrong. Make the sheet by editing the client's real product photo with `make.py sheet ... --ref`, adding only the face, arms and legs. Quote the label text exactly, and never generate the product or its logo from a description.

## Visual direction

- The default for "Pixar-style", "DreamWorks-style" or plain "AI animation" is DreamWorks-inspired feature-animation CG:
  - sculpted, appealing, slightly stylized characters with large expressive eyes;
  - soft groomed fur, and shaped hair and fabric;
  - rich but controlled colour, layered sets and readable depth.

  Describe these visible qualities in every prompt instead of relying on a studio name. The look is not photoreal and not a flat cartoon.
- Light comes from sources that exist in the location. No golden hour, amber haze, orange rim light or sunset unless the brief asks for it. Image models drift into these by default.
- Keep identity, wardrobe, proportions, scale, location layout and light consistent from sheets through stills to clips. Put relative scale in every prompt with more than one character (for example: the cat's back is at the man's shin).
- 9:16 unless the brief says otherwise. Keep the action in the central 70% of the frame, clear of the bottom and right edges where short-video apps put their buttons.
- In a clip, the frame stays locked unless the shot is a talking clip with its one smooth move (`clip-prompt.md`).

## Review additions

On top of the shared checklist: the render is 3D CG like the sheets (not 2D or outlined, not photoreal), and a talking clip says its whole line, each word once, with no gaps.
