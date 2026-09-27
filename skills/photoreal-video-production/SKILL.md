---
name: photoreal-video-production
description: The photoreal layer for a short-form Google Flow video (real-world ad scenes, lifestyle and product b-roll under a voiceover). It adds the look, still prompts through photoreal-still-prompt, the photoreal clip template with a subtle camera move, and the photoreal failure locks (real-life logic, eyelines, tone, object counts, content-filter-safe intimacy), on top of the shared video-production pipeline (layout, make.py, gates), which it loads. Use when a video plan's style is photoreal scenes, when continuing a project whose AGENTS.md names this skill, or for a single photoreal clip prompt. Not for UGC talking heads (ugc-ad-remake, simple-talking-head) or 3D animation (animated-video-production).
---

# Photoreal Video Production

Real-world scenes, 9:16, made with Google Flow, that must not look AI-made.

**Load `video-production` first.** It holds the pipeline: who runs which batch, the gates, the project layout, `init-project.sh` and every `make.py` command. Photoreal projects use exactly the same layout and commands as animated ones: `scenes/scene-N/...`, `clips/clip-N/...`, one manifest each, state in `.flow/`. This skill adds only what is specific to photoreal. Start a project with:

```bash
bash <video-production-dir>/scripts/init-project.sh <client-folder> video-N --style photoreal
```

Files, loaded only when a phase needs them:

| File | Load it for |
|---|---|
| [references/clip-prompt.md](references/clip-prompt.md) | Writing any clip prompt (phase 4) |
| [references/failure-locks.md](references/failure-locks.md) | Before writing prompts, and whenever a result is rejected, with `video-production/references/failure-locks.md` |

## Sheets and stills

- Sheets follow `character-generation`, `environment-generation` and `prop-generation` in their default photoreal mode. The product sheet is made from the client's real product photo (`make.py sheet ... --ref`), never generated from a description, and every prompt that shows it quotes the label text exactly.
- Each still prompt is a `photoreal-still-prompt` JSON object, saved in `scenes/scene-N/scene-Nx/prompts/scene-Nx-vK.md`: a one-line `#` heading, then the JSON in a `text` code block (flow reads only a `text`, `prompt` or bare code block, never a `json` one). Its `reference_fidelity` names what each ingredient gives (product label, a person's face, a softgel's look) and what to ignore (the sheet's grey backdrop, its layout).
- **Casting.** Before the sheets, check each person's age and look against what the scene asks of them (a couple in a romantic beat reads wrong if they look too old for it). Put the age in the character sheet and every still.
- **Reuse first.** When an earlier video for the client has an approved clip of the same beat (`video-1/clips/all/`, `video-1/final/`), bring it in with `make.py reuse` rather than regenerate it.

## Look

- Ordinary real life: real skin, fabric and materials; light from sources in the room; true-to-life colour. No AI look (waxy skin, glow, perfect symmetry), and no stylization the brief doesn't ask for (the Mysa client rejected a red glow).
- Diagrams and science shots match the brief's inspiration look (a clean anatomical diagram), not a glowing CG render.
- Things are where they would be in real life: a monitor faces the person using it, a glass stands on the table, a paper stays one paper.
- People never look at the camera unless the shot calls for it. Put the eyeline in every still and clip.
- The face and body match the voiceover line over the shot: worried on a problem line, relieved on a solution line.
- Keep the action in the central 70% of the frame, clear of the bottom and right edges where short-video apps put their buttons.

## Clips

- A clip is never fully static: it makes one subtle, slow camera move (a gentle push-in, a slight drift) or holds a locked frame that gets a slow zoom in post. The template in `clip-prompt.md` writes the move in.
- Short, plain prompts work best: what happens, timed, then the fixed lines (motion, sound, no text, one shot). Long lists of prohibitions invite what they forbid.
- Hard beats (taking a pill and swallowing it with water, pouring, handing something over) get 6 s with each step timed to the second, and a count of every object that matters. Review them by counting.

## Review additions

On top of the shared checklist, for every still and clip:

- it looks like a photograph, not a render (skin, fabric, light, no glow);
- nobody looks into the lens unless the plan says so;
- ages and looks fit the scene;
- every object that matters keeps its count from first frame to last (the pills, the papers, the water level dropping when someone drinks).
