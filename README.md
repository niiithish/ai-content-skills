# AI Content Skills

Agent skills for the short-form video pipeline: **script** → **character / prop / environment** references → **AI video** prompts.

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
npx skills add niiithish/ai-content-skills --skill video-generation
```

List without installing:

```bash
npx skills add niiithish/ai-content-skills --list
```

## Skills

| Skill | Description |
| --- | --- |
| [`script-generation`](./skills/script-generation) | Short-form ad scripts as a numbered cut list, paced for AI generation. |
| [`prop-generation`](./skills/prop-generation) | Multi-view prop sheets (3–4 views) on neutral grey. |
| [`character-generation`](./skills/character-generation) | Two-panel sheets: invisible-body outfit + matching identity portrait. |
| [`environment-generation`](./skills/environment-generation) | Wide 3/4-view location references for image and video. |
| [`video-generation`](./skills/video-generation) | Block-structured AI video prompts (Seedance, Veo, Kling, etc.). |

## Pipeline

```text
script-generation      →  voiceover + numbered cut list
    ↓
character / prop /     →  reference images per cut
environment-generation
    ↓
video-generation       →  one prompt per generation, chained by last frame
```

| Stage | Delivers |
| --- | --- |
| **script-generation** | Edit-ready cut list (≤3s cuts, environment changes, silent + VO). |
| **prop-generation** | Studio multi-view product identity sheet. |
| **character-generation** | Outfit + face identity sheet for consistent talent. |
| **environment-generation** | Spatially clear 3/4 location sheet. |
| **video-generation** | One model-ready prompt per generation from the cut list. |

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
└── video-generation/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/{prompt-blocks,optics,engine-notes}.md
```

- `SKILL.md` — name, description (auto-invoke triggers), actionable instructions
- `references/` — blueprints and tables loaded when the skill runs
- `agents/openai.yaml` — optional agent UI metadata

## License

MIT
