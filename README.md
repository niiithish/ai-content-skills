# AI Content Skills

Agent skills for the whole short-form video pipeline: write the **script**, generate consistent **prop**, **character** and **environment** references, then write the **AI video** prompts that turn them into clips.

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
| [`script-generation`](./skills/script-generation) | Short-form ad scripts delivered as a numbered cut list, paced for AI generation. |
| [`prop-generation`](./skills/prop-generation) | Multi-view studio prop reference sheets with a tight 3-4 view set on a neutral grey background. |
| [`character-generation`](./skills/character-generation) | Two-panel character sheets: invisible-body full outfit (left) + matching shoulder-up identity portrait (right). |
| [`environment-generation`](./skills/environment-generation) | Spatially clear 3/4-view interior and exterior location references for image and video workflows. |
| [`video-generation`](./skills/video-generation) | Block-structured AI video prompts for Seedance, Veo, Kling and similar engines. |

## Pipeline

The skills chain in one direction. Each stage hands a concrete artifact to the next.

```text
script-generation      →  voiceover + numbered cut list
    ↓
character / prop /     →  reference images per cut
environment-generation
    ↓
video-generation       →  one prompt per generation, chained by last frame
```

### script-generation

Write the script as an edit, not an essay: a numbered cut list with the spoken line and shot for each cut, capped at 3 seconds per cut, one environment change per cut, grouped into generations that fit the video engine's clip limit. Encodes the awareness-stage diagnosis, hook patterns, a pre-delivery audit, and the anti-confusion rule for scripts that contrast the product against a worse alternative.

**Use when:** writing a TikTok, Reels or Shorts ad script; writing hooks or voiceover copy; making an existing script faster or less ad-like.

### prop-generation

Create one standalone image-generation prompt for a clean, consistent multi-view prop reference sheet. Chooses a tight 3-4 view set that shows the surfaces a downstream video or ad will actually put on camera (front, sides, rear, top, three-quarter, detail), skips pointless views like appliance undersides, uses no orientation labels, and locks identity across every panel.

**Use when:** designing products, footwear, toys, tools, vehicles, furniture, or other non-character props; building orthographic turnarounds; remixing a prop from a reference image.

### character-generation

Create one landscape character reference sheet prompt with two panels: complete worn outfit with no body visible, and a large matching head-and-shoulders identity portrait.

**Use when:** establishing a consistent face, wardrobe, and accessories for AI images or video; remixing a character from a reference image.

### environment-generation

Create one establishing environment prompt with a true 3/4 camera angle that reveals depth, boundaries, openings, and landmarks so downstream models understand the space.

**Use when:** designing rooms, streets, stadiums, landscapes, or other interiors/exteriors as stable location references.

### video-generation

Turn a cut list into standalone AI video prompts using a fixed block order, FOV in degrees from an anchor table, positive-only phrasing, and measurable atmosphere. Covers reference tagging, timed multishot cuts, per-engine clip caps, and the moderation and silent-b-roll rules that short-form ad work needs.

**Use when:** writing a prompt for Seedance, Veo, Kling, Sora, Runway or Hailuo; building a shot or multi-cut sequence; turning reference sheets into clips.

## Repository layout

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

Each skill follows the Agent Skills format:

- `SKILL.md` — name, description, and instructions
- `references/` — prompt blueprints loaded when the skill runs
- `agents/openai.yaml` — optional agent UI metadata

## License

MIT
