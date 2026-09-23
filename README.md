# AI Content Skills

Agent skills for the short-form video pipeline: **script** → **character / prop / environment** references → **AI video** prompts, plus a talking-head remake path for cloning winning UGC ads and a Gemini 3.1 Pro JSON video decode.

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
npx skills add niiithish/ai-content-skills --skill animated-video-production
npx skills add niiithish/ai-content-skills --skill video-generation
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
| [`prop-generation`](./skills/prop-generation) | One 16:9 JSON composite prop sheet (2 for loop-and-clasp jewellery, otherwise 3–4) with #504f50 background and #d1d1d2 dividers. |
| [`character-generation`](./skills/character-generation) | One 16:9 JSON three-panel sheet: headless front + back bodies, large 3/4 portrait; #504f50 background and #d1d1d2 dividers. |
| [`environment-generation`](./skills/environment-generation) | JSON wide 3/4-view location references for image and video. |
| [`photoreal-still-prompt`](./skills/photoreal-still-prompt) | JSON prompts for one believable real-world image or video start frame, defaulting to 9:16 portrait, with grounded product packaging, camera, and light. |
| [`animated-video-production`](./skills/animated-video-production) | DreamWorks-inspired CG animation workflow: reference assets, composed stills, fixed-frame clips, scene-native sound, and exact visible text without music or captions. |
| [`video-generation`](./skills/video-generation) | Block-structured AI video prompts (Seedance, Veo, Kling, etc.). |
| [`clay-animation-video-prompt`](./skills/clay-animation-video-prompt) | Claymation performance-ad packages with reference prompts, VO timing, and shot continuity. |
| [`ugc-ad-remake`](./skills/ugc-ad-remake) | Still-first remake of a winning talking-head UGC ad with new talent and product. |
| [`simple-talking-head`](./skills/simple-talking-head) | Raw iPhone 9:16 talking-head prompt: one line, selfie or tripod, no product in hand. |
| [`video-breakdown`](./skills/video-breakdown) | Send the clip to Gemini 3.1 Pro for a remake-bible JSON: form, one detailed scene per cut, start/end states. |
| [`flow`](./skills/flow) | Run Google Flow via the local Labflow `flow` CLI: Nano Banana Pro 1K images and Omni Flash video. Rotates saved accounts on quota; do not switch mid-job. |

## Pipeline

```text
script-generation      →  spoken UGC script (+ cut list if AI video)
    ↓
character / prop /     →  reference images per cut
environment-generation
    ↓
video-generation       →  one prompt per generation, chained by last frame
```

| Stage | Delivers |
| --- | --- |
| **script-generation** | Spoken UGC script for TikTok/Reels. Optional ≤3s cut list for AI video. |
| **prop-generation** | Studio multi-view product identity sheet. |
| **character-generation** | Front/back wardrobe + large face sheet for consistent talent. |
| **environment-generation** | Spatially clear 3/4 location sheet. |
| **photoreal-still-prompt** | One photoreal lifestyle, product-in-context, or scene image prompt. |
| **animated-video-production** | Consistent 3D animation assets, scene stills, and clip prompts with ambient sound and controlled on-screen text. |
| **video-generation** | One model-ready prompt per generation from the cut list. |
| **ugc-ad-remake** | Beat map, 9:16 product-swap stills, then Gemini Omni talking-head clips. |
| **simple-talking-head** | One-line raw iPhone talking-head prompt (selfie or tripod). |
| **video-breakdown** | Gemini 3.1 Pro JSON → form + one rebuildable scene per hard cut (not a props dump). |
| **flow** | Generate the still/clip on Google Flow (`flow image` / `flow generate`). |

## Layout

Each skill is a focused agent prompt (`SKILL.md`) plus optional load-on-demand references:

```text
skills/
├── script-generation/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/{hooks,audit,tracker}.md
├── prop-generation/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/prompt-blueprints.md
├── character-generation/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/prompt-blueprint.md
├── environment-generation/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/prompt-blueprints.md
├── video-generation/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/{prompt-blocks,optics,engine-notes}.md
└── clay-animation-video-prompt/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/{prompt-blueprint,ad-reference-pack}.md
├── ugc-ad-remake/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/{beat-map,still-prompts,clip-prompts,failure-locks}.md
├── simple-talking-head/
│   ├── SKILL.md
│   └── agents/openai.yaml
└── video-breakdown/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/gemini-prompt.md
├── flow/
    ├── SKILL.md
    └── agents/openai.yaml
```

- `SKILL.md` — name, description (auto-invoke triggers), actionable instructions
- `references/` — blueprints and tables loaded when the skill runs
- `agents/openai.yaml` — optional agent UI metadata

## License

MIT
