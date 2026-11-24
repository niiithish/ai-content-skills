---
name: filmcraft-edit
description: "Edit, pace, audit, and export short-form video ads in FilmCraft (`filmcraft-cli`) following the house editing style across talking-head, voiceover, sung, and slideshow formats. Handles live bridge editing alongside the user, dead-air cutting and motion (`fc_pace.py`), clip swaps without Link Media popups, hook 2–3 cloning from hook 1, automated pre-handback QA (`fc_qa.py` + `audit.py`), and Meta-ready 1080x1920 H.264/AAC exports. Use for any FilmCraft timeline build, edit, pacing pass, change request, clip relink/swap, client Loom fix, or export. Not for adding/timing caption text clips (use `captions-filmcraft`) or generating raw AI images/clips (use `video-production` / `flow`)."
compatibility: "Requires `filmcraft-cli`, `ffmpeg`, `ffprobe`, and Python 3 (with `numpy` for `fc_pace.py`). Optional `transcribe` skill for waveform pause detection."
metadata:
  author: ai-content-skills
  version: "2.0"
---

# FilmCraft Edit (House Style + CLI + Pacing)

One unified skill for editing, pacing, auditing, and exporting short-form ads in FilmCraft. The user edits in FilmCraft and has the final say; the agent builds export-ready timelines, applies change requests live through the bridge, verifies with automated QA, and exports only when asked.

## When to Load References

Load only the reference file needed for the current task (all 1 level deep):

| Reference | Load when |
|---|---|
| [references/house-style.md](references/house-style.md) | Starting any edit: canonical rules (music −16 to −18 dB under voice, Flow lead-in trim, motion, screen inserts, no robotic speed hacks) |
| [references/talking-head.md](references/talking-head.md) | Speaker on V1 with full-screen inserts, podcast splits, or green-screen cutouts (Formats A–D) |
| [references/voiceover.md](references/voiceover.md) | Voiceover, AI sung ad, or stills slideshow over B-roll/3D/claymation (15–150 shots) |
| [references/pacing.md](references/pacing.md) | Cutting dead air, adding subtle motion/pushes, or diagnosing slow/static edits (`fc_pace.py`) |
| [references/filmcraft-cli.md](references/filmcraft-cli.md) | Scripting `filmcraft-cli` JSONL commands or parsing `inspect project` / `inspect sequence` JSON |
| [references/change-requests.md](references/change-requests.md) | Applying client Loom notes or user tweaks on a saved `.fcproj` (swaps, cuts, hook clones, traps) |

Shared overlays (`exploding-head-iphone.png`, `cta-arrows-red.png`, `switch-click-02.mp3`) and HTML focus-screen templates live in `assets/`.

## End-to-End Workflow

1. **Check project context.** Read the client folder's `AGENTS.md` / `CLAUDE.md` and the video's `AGENTS.md` / `PLAN.md` first — project rules win over defaults.
2. **Build hook 1** (`video-N/edit/hook-1.fcproj`).
   - Always place clips from versioned finals (`clips/clip-N/clip-Nx/final/clip-Nx-vK-1080p.mp4`), **never `clips/all/`** (which causes Link Media popups when `make.py sync` rotates files).
   - If the user asks for a **raw timeline** to trim by hand (*"just add clips rawly without any trim"*), place the clips cleanly without auto-trimming or auto-pacing.
   - Otherwise apply house style: trim dead Flow lead-in (motion/audio onset, fallback 0.5–1.0 s), normalize voice to −16 LUFS, keep music **−16 to −18 dB under voice** with a 1–2 s fade-out.
   - **Stop before exporting.** Never export unless the user explicitly asks.
3. **Pacing pass** (when tightening dead air or adding motion — before captions):
   ```bash
   scripts/fc_pace.py report video-N/edit/hook-1.fcproj
   scripts/fc_pace.py tighten video-N/edit/hook-1.fcproj --style calm
   scripts/fc_pace.py motion video-N/edit/hook-1.fcproj --style calm
   ```
4. **Captions.** Hand off to `captions-filmcraft` (`words`, `plan`, `build`, `check`, and `fc_inserts.py check`). Re-run captions after any cut or voice change.
5. **User tweaks & live change requests.** Once the user tweaks hook 1 in FilmCraft, their saved file is the source of truth.
   - **`"update filmcraft"` ALWAYS means updating the `.fcproj` timeline via the live bridge (`fc.py`).** NEVER run `filmcraft-update` (the app binary updater) unless the user explicitly asks to upgrade the FilmCraft application itself.
   - Back up every `.fcproj` to `edit/backup-<date>-<what>/` before scripting. Never move clips the user placed unless asked.
6. **Clone hooks 2–3 from the approved hook 1.** Swap only the opening; keep hook 1's entire body intact and verify with `audit.py --body-of`.
7. **Pre-handback QA gate (mandatory before showing the user or exporting).** Run `audit.py` and `fc_qa.py` (see below).
8. **Export** (only when asked):
   ```bash
   scripts/fc.py export video-N/edit/hook-1.fcproj -o video-N/deliverables/<Brand>_<Concept>_Hook1_9x16.mp4
   scripts/fc.py export video-N/edit/hook-{1,2,3}.fcproj -d video-N/deliverables
   ```
   Run exports in the background, one hook after another (GPU VA-API encoding, H.264 High 6 Mb/s VBR 1-pass, AAC 192k, ~45 MB/min). Never render or stitch a FilmCraft edit with `ffmpeg`.

## Core Scripts

| Script | Purpose |
|---|---|
| `scripts/fc.py` | Safe bridge/file runner (`status`, `run`, `swap`, `relink`, `export`). Automatically targets the live app when the project is open on port 9876, or refuses if FilmCraft is open without its bridge. |
| `scripts/fc_pace.py` | Waveform-based pause tightening and subtle motion (`report`, `tighten`, `motion`). |
| `scripts/audit.py` | Structural `.fcproj` audit: catches fractional-frame clips, offline/low-res (<720p) media, dropped baseline transitions/effects, and hook 2–3 body drift. |
| `scripts/fc_qa.py` | Automated pre-handback QA: checks `.fcproj` offline media & fractional frames, and inspects exported video/audio via `ffmpeg`/`ffprobe` for **black frames**, **excessive silence gaps**, **clipping / loudness**, and **codec compliance** (H.264 + AAC). |
| `scripts/setup.sh` | One-time per-machine setup: generates `~/.config/filmcraft/control-token`, installs `~/.local/bin/filmcraft-live`, overrides desktop launcher, and configures bridge MCP. |
| `scripts/filmcraft-update` | App binary updater for the patched GPU FilmCraft build — run **only** when explicitly asked to update the FilmCraft app. |

## Pre-Handback QA Gate

Run before handing any edit back or delivering exports:

```bash
# 1. Timeline integrity (and baseline / hook-1 body parity when applicable)
scripts/audit.py edit/hook-1.fcproj --baseline edit/backup-<latest>/hook-1.fcproj

# 2. Timeline + media QA (or run on an exported preview/deliverable .mp4)
scripts/fc_qa.py edit/hook-1.fcproj
scripts/fc_qa.py deliverables/<file>.mp4 --max-silence 0.45

# 3. Render check frames at changed spots (never full test exports unless asked)
filmcraft-cli --project edit/hook-1.fcproj render --seconds 1.5 --out /tmp/check.png
```

Fix any `FAIL` (black frames, offline media, fractional clips, dropped transitions, unrequested silence gaps) before replying.

## Hard Rules (Non-Negotiable)

- **Bridge safety:** Never save from a headless `filmcraft-cli --project X --save` while the FilmCraft app has `X` open. Always use `fc.py` (`fc.save_live` / `fc.reload_live`). Run `scripts/setup.sh` once if `fc.py status` shows `bridge: down`.
- **No `ffmpeg` renders:** `ffmpeg` is for analysis (`ffprobe`, `blackdetect`, `silencedetect`, `volumedetect`) and preparing source assets (voice mux, LUFS normalization) only — never rendering or concatenating a FilmCraft edit.
- **No destructive speed hacks:** Never slow clips to ~77% or apply heavy audio time-stretching that makes voices sound robotic. Keep talking-head speedups within natural bounds (1.0x–1.15x unless a reference explicitly demands higher WPM).
- **No jarring hard-cut jump zooms on silences:** Use a slow continuous zoom across hook openings or cover cuts with B-roll/inserts; do not slap repetitive hard 100→110% jumps on awkward silence cuts.
- **No unasked exports or rebuilds:** Ask before exporting, deleting clips, or rebuilding a user-tweaked project. Always move previous exports to `deliverables/pre-<what>/` before re-exporting.
