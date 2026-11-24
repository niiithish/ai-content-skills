# AI Content Skills

Cross-agent skill suite for end-to-end short-form AI video production: **script** → **reference breakdown** → **production plan** → **stills & 1080p clips** (Google Flow + ElevenLabs Creative) → **FilmCraft edit, pacing & frame-exact captions**.

Built strictly to the [Agent Skills (`agentskills.io`)](https://agentskills.io/) open standard — flat `skills/<name>/SKILL.md` layout with progressive-disclosure `references/` and `scripts/`, working cleanly across **Claude Code**, **OpenAI Codex**, **Gemini CLI**, and **Antigravity**.

[![skills.sh](https://skills.sh/b/niiithish/ai-content-skills)](https://skills.sh/niiithish/ai-content-skills)

---

## Quickstart

### Option A: Local Clone + Cross-Agent Bootstrap (Recommended)

```bash
git clone https://github.com/niiithish/ai-content-skills.git ~/Work/ai-content-skills
bash ~/Work/ai-content-skills/scripts/install.sh
bash ~/Work/ai-content-skills/scripts/doctor.sh
```

`scripts/install.sh` auto-discovers every skill in `skills/`, symlinks them into `~/.agents/skills`, `~/.claude/skills`, `~/.gemini/skills`, `~/.gemini/config/skills`, and `~/.codex/skills`, installs `~/.local/bin/` CLI wrappers (`transcribe`, `vocals`, `cartesia`, `rembg-cutout`), and installs caption fonts.

### Option B: Install via `skills.sh`

```bash
# Install all 11 skills
npx skills add niiithish/ai-content-skills --all

# Or list available skills first
npx skills add niiithish/ai-content-skills --list
```

### Validate Repo Spec Compliance

```bash
python3 scripts/validate_skills.py
```

Moving to a new SSD or fresh Linux/Arch/Omarchy machine? See **[docs/new-ssd-migration.md](./docs/new-ssd-migration.md)** for the full backup, restore, and Intel Arc GPU optimization guide.

---

## Skills (11)

### Pre-Production & Strategy
| Skill | Description |
| --- | --- |
| [`script-generation`](./skills/script-generation) | Spoken TikTok/Reels/Shorts UGC ad scripts that sound like a real person and hold a scroll (optional cut list for AI video). |
| [`video-breakdown`](./skills/video-breakdown) | Local reference-video decoder (ffmpeg cut detection, shot clustering, local Parakeet word timing, contact sheets, rhythm map) — no Gemini required. |
| [`video-plan`](./skills/video-plan) | Client brief to approved `PLAN.md` + `PLAN.pdf` timed from a real voiceover or song read, with cast demographics, before/after arc, and reuse audit locked before generation. |

### Production & Generation Engines
| Skill | Description |
| --- | --- |
| [`video-production`](./skills/video-production) | Unified production hub (`make.py`, `PROJECT_STATE.json`, direct 1080p default, concurrency 10–12, autonomous QA gate) with 9 on-demand visual style modules in `references/styles/` (`photoreal`, `pixar-3d`, `claymation`, `talking-head`, `ai-singing`, `ai-drama`, `medical-cgi`, `hybrid-ugc`, `storybook-2d`). |
| [`flow`](./skills/flow) | Google Flow generation via the local Labflow `flow` CLI (Nano Banana 2.1/Pro images, Omni Flash video, batch manifests, automatic account rotation, 1080p upsample). |
| [`elevenlabs-creative`](./skills/elevenlabs-creative) | ElevenLabs Creative fallback and specialist engine (Seedream 5.5, Seedance 2.0 Mini, Kling, MiniMax H3 Max, Voice Isolator) with mandatory `quantity=1`, explicit aspect ratio, and `cloudflared` local image tunnel helpers. |

### Audio & Media Utilities
| Skill | Description |
| --- | --- |
| [`cartesia-tts`](./skills/cartesia-tts) | Cartesia Sonic 3.6 TTS (`cartesia voices / audition / say`) with exact word timestamps (`OUT.words.json`) for plan timing and voiceovers. |
| [`transcribe`](./skills/transcribe) | 100% local speech-to-text (`transcribe`, Parakeet TDT 0.6B v3 on Intel Arc Vulkan → CPU → faster-whisper) and vocal stem separation (`vocals`, MelBand RoFormer on Arc XPU) for sung ads. |
| [`media-utils`](./skills/media-utils) | Local media helpers: `rembg` background removal & clean cutouts (`rembg_cutout.py`), headless browser screen recording (`agent-browser`), and side-by-side review board workflows. |

### Editing & Captions
| Skill | Description |
| --- | --- |
| [`filmcraft-edit`](./skills/filmcraft-edit) | Unified FilmCraft editing hub: house edit style, live bridge (`fc.py`), talking-head and voiceover/song edit formats, waveform-driven pacing & motion (`fc_pace.py`), pre-export audit (`audit.py`), and Meta-ready GPU exports. |
| [`captions-filmcraft`](./skills/captions-filmcraft) | Frame-exact editable text-clip captions in FilmCraft (`fc_captions.py`, `fc_inserts.py`), calibrated against the voiceover/vocal-stem waveform and snapped to cuts and inserts. |

---

## Pipeline Overview

```text
brief / reference video
  ├─► video-breakdown (local rhythm + pattern)
  ├─► script-generation (spoken script / hooks)
  ├─► cartesia-tts / transcribe / vocals (real audio + word timing)
  └─► video-plan (approved PLAN.md + PLAN.pdf)
        ↓
  video-production (+ style module in references/styles/<style>.md)
    ├─► flow (primary engine)
    ├─► elevenlabs-creative (specialist / fallback engine)
    └─► media-utils (rembg cutouts, screen recordings, review board)
        ↓
  filmcraft-edit (timeline, pacing, motion, audit)
        ↓
  captions-filmcraft (frame-exact captions + insert snap)
        ↓
  filmcraft-edit export (1080×1920 H.264 VA-API + AAC)
```

---

## Repository Layout

```text
ai-content-skills/
├── README.md
├── skills.sh.json
├── docs/
│   └── new-ssd-migration.md        # SSD swap backup, restore & Intel Arc optimization guide
├── scripts/
│   ├── install.sh                  # Cross-agent symlink + CLI wrapper + font installer
│   ├── doctor.sh                   # Environment, GPU, model & symlink health check
│   └── validate_skills.py          # Strict agentskills.io spec & Python syntax validator
└── skills/
    └── <skill-name>/
        ├── SKILL.md                # Strict agentskills.io frontmatter + core instructions (<500 lines)
        ├── references/             # On-demand style modules, checklists, and templates (1 level deep)
        ├── scripts/                # Executable CLI helpers
        └── assets/ | fonts/        # Static assets
```

## License

MIT
