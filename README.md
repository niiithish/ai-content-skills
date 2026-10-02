# AI Content Skills

Agent skills for the short-form video pipeline: **script** → **character / prop / environment** references → **AI video** on Google Flow, plus a talking-head remake path for cloning winning UGC ads and a Gemini 3.1 Pro JSON video decode.

Compatible with the [Agent Skills](https://agentskills.io/) open standard and installable via [skills.sh](https://skills.sh).

[![skills.sh](https://skills.sh/b/niiithish/ai-content-skills)](https://skills.sh/niiithish/ai-content-skills)

## Install

```bash
# Install all skills
npx skills add niiithish/ai-content-skills --all

# Or pick specific skills
npx skills add niiithish/ai-content-skills --skill script-generation
npx skills add niiithish/ai-content-skills --skill prop-generation
npx skills add niiithish/ai-content-skills --skill character-generation
npx skills add niiithish/ai-content-skills --skill environment-generation
npx skills add niiithish/ai-content-skills --skill photoreal-still-prompt
npx skills add niiithish/ai-content-skills --skill video-production
npx skills add niiithish/ai-content-skills --skill animated-video-production
npx skills add niiithish/ai-content-skills --skill photoreal-video-production
npx skills add niiithish/ai-content-skills --skill captions
npx skills add niiithish/ai-content-skills --skill song-ad
npx skills add niiithish/ai-content-skills --skill clay-animation-video-prompt
npx skills add niiithish/ai-content-skills --skill ugc-ad-remake
npx skills add niiithish/ai-content-skills --skill simple-talking-head
npx skills add niiithish/ai-content-skills --skill video-breakdown
npx skills add niiithish/ai-content-skills --skill flow
```

List without installing:

```bash
npx skills add niiithish/ai-content-skills --list
```

## Skills

| Skill | Description |
| --- | --- |
| [`script-generation`](./skills/script-generation) | Spoken TikTok/Reels UGC scripts. Cut list only when you ask for AI video. |
| [`prop-generation`](./skills/prop-generation) | One 16:9 JSON composite prop sheet (2 for loop-and-clasp jewellery, otherwise 3–4) on a #504f50 background, cells butted edge to edge with no divider lines. |
| [`character-generation`](./skills/character-generation) | One 16:9 JSON three-panel sheet: headless front + back bodies, large 3/4 portrait; #504f50 background, panels butted edge to edge with no divider lines. |
| [`environment-generation`](./skills/environment-generation) | JSON wide 3/4-view location references for image and video. |
| [`photoreal-still-prompt`](./skills/photoreal-still-prompt) | JSON prompts for one believable real-world image or video start frame, defaulting to 9:16 portrait, with grounded product packaging, camera, and light. |
| [`video-plan`](./skills/video-plan) | Client brief to an approved PLAN.md + PLAN.pdf for any style: brief table, sheets to make, and a shot table timed from a real voiceover read (Cartesia or faster-whisper), with suggested visuals marked. |
| [`video-production`](./skills/video-production) | The shared pipeline from an approved plan to 1080p clips on Google Flow, any style: project layout, a `make.py` batch/review/reuse/hand-off tool, review gates and a failure-locks checklist. |
| [`animated-video-production`](./skills/animated-video-production) | The DreamWorks-style 3D animation layer on `video-production`: look, still and clip prompts, product mascots, on-camera speech. |
| [`photoreal-video-production`](./skills/photoreal-video-production) | The photoreal ad layer on `video-production`: look, clip prompts with a subtle camera move, real-life logic and content-filter lessons. |
| [`captions`](./skills/captions) | Burns locked-style captions and red section labels into a finished 9:16 edit: script wording, whisper timing, a preview frame first. |
| [`song-ad`](./skills/song-ad) | AI singing ads: a sung story with a hook, real lyrics (rhyme, refrain, backing answers) and a music direction per section, the song generated first as the timing source, gapless lip-sync slices and animated B-roll. |
| [`clay-animation-video-prompt`](./skills/clay-animation-video-prompt) | Claymation performance-ad packages with reference prompts, VO timing, and shot continuity. |
| [`ugc-ad-remake`](./skills/ugc-ad-remake) | Still-first remake of a winning talking-head UGC ad with new talent and product. |
| [`simple-talking-head`](./skills/simple-talking-head) | Raw iPhone 9:16 talking-head prompt: one line, selfie or tripod, no product in hand. |
| [`video-breakdown`](./skills/video-breakdown) | Send the clip to Gemini 3.1 Pro for a remake-bible JSON (pattern, hook, one scene per cut, how each builds on the spoken words), then check it against contact sheets of the real frames. |
| [`flow`](./skills/flow) | Run Google Flow via the local Labflow `flow` CLI: Nano Banana Pro 1K images, Omni Flash video, `flow batch` manifests, seeds, and 1080p upsample. Rotates saved accounts on quota. |

## Pipeline

```text
script-generation      →  spoken UGC script (+ cut list if AI video)
    ↓
character / prop /     →  reference images per cut
environment-generation
    ↓
flow                   →  stills and clips on Google Flow
```

Animated and photoreal projects run on one shared pipeline, with a style layer on top:

```text
video-plan → video-production + animated- or photoreal-video-production
  sheets (character / environment / prop) → stills → 360p clips (agent runs and reviews)
  → 1080p finals (user runs) → hand-off → the user's edit → captions      (generation via flow)
```

| Stage | Delivers |
| --- | --- |
| **script-generation** | Spoken UGC script for TikTok/Reels. Optional ≤3s cut list for AI video. |
| **prop-generation** | Studio multi-view product identity sheet. |
| **character-generation** | Front/back wardrobe + large face sheet for consistent talent. |
| **environment-generation** | Spatially clear 3/4 location sheet. |
| **photoreal-still-prompt** | One photoreal lifestyle, product-in-context, or scene image prompt. |
| **animated-video-production** / **photoreal-video-production** | A whole animated or photoreal project on `video-production`: sheets, stills, 360p drafts, 1080p finals, ordered clips for the editor. |
| **captions** | Captions and section labels burned into the user's finished edit. |
| **ugc-ad-remake** | Beat map, 9:16 product-swap stills, then Gemini Omni talking-head clips. |
| **simple-talking-head** | One-line raw iPhone talking-head prompt (selfie or tripod). |
| **video-breakdown** | Gemini 3.1 Pro JSON → form + one rebuildable scene per hard cut (not a props dump). |
| **flow** | Generate the still/clip on Google Flow (`flow image` / `flow generate`). |

## Layout

Each skill is a focused agent prompt (`SKILL.md`) plus optional load-on-demand references:

```text
skills/
├── <skill>/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/        load-on-demand blueprints and checklists
│   ├── scripts/           helper scripts (video-breakdown, video-production, captions, song-ad)
│   └── templates/         project files (video-production)
```

- `SKILL.md` — name, description (auto-invoke triggers), actionable instructions
- `references/` — blueprints and tables loaded when the skill runs
- `agents/openai.yaml` — optional agent UI metadata
- `scripts/`, `templates/` — files the skill runs or copies into a project

## License

MIT
