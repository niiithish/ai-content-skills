# AI Content Skills

Agent skills for writing model-ready image prompts for **props**, **characters**, and **environments** — optimized as consistent references for AI image generation, remixing, and video.

Compatible with the [Agent Skills](https://agentskills.io/) open standard and installable via [skills.sh](https://skills.sh).

[![skills.sh](https://skills.sh/b/niiithish/ai-content-skills)](https://skills.sh/niiithish/ai-content-skills)

## Install

```bash
# Install all skills
npx skills add niiithish/ai-content-skills --all

# Or pick specific skills
npx skills add niiithish/ai-content-skills --skill prop-generation
npx skills add niiithish/ai-content-skills --skill character-generation
npx skills add niiithish/ai-content-skills --skill environment-generation
```

List without installing:

```bash
npx skills add niiithish/ai-content-skills --list
```

## Skills

| Skill | Description |
| --- | --- |
| [`prop-generation`](./skills/prop-generation) | Multi-view studio prop reference sheets with a tight 3-4 view set on a neutral grey background. |
| [`character-generation`](./skills/character-generation) | Two-panel character sheets: invisible-body full outfit (left) + matching shoulder-up identity portrait (right). |
| [`environment-generation`](./skills/environment-generation) | Spatially clear 3/4-view interior and exterior location references for image and video workflows. |

### prop-generation

Create one standalone image-generation prompt for a clean, consistent multi-view prop reference sheet. Chooses a tight 3-4 view set that shows the surfaces a downstream video or ad will actually put on camera (front, sides, rear, top, three-quarter, detail), skips pointless views like appliance undersides, uses no orientation labels, and locks identity across every panel.

**Use when:** designing products, footwear, toys, tools, vehicles, furniture, or other non-character props; building orthographic turnarounds; remixing a prop from a reference image.

### character-generation

Create one landscape character reference sheet prompt with two panels: complete worn outfit with no body visible, and a large matching head-and-shoulders identity portrait.

**Use when:** establishing a consistent face, wardrobe, and accessories for AI images or video; remixing a character from a reference image.

### environment-generation

Create one establishing environment prompt with a true 3/4 camera angle that reveals depth, boundaries, openings, and landmarks so downstream models understand the space.

**Use when:** designing rooms, streets, stadiums, landscapes, or other interiors/exteriors as stable location references.

## Repository layout

```text
skills/
├── prop-generation/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/prompt-blueprints.md
├── character-generation/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/prompt-blueprint.md
└── environment-generation/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/prompt-blueprints.md
```

Each skill follows the Agent Skills format:

- `SKILL.md` — name, description, and instructions
- `references/` — prompt blueprints loaded when the skill runs
- `agents/openai.yaml` — optional agent UI metadata

## License

MIT
