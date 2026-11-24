---
name: captions-filmcraft
description: "Add editable, frame-accurate captions into a FilmCraft (`.fcproj`) timeline as text clips synchronized to the exact spoken word and picture cuts, snap B-roll/box inserts so visuals only change on a caption start or V1 cut (`fc_inserts.py`), and verify visual styling before export. Uses local Parakeet + faster-whisper word timing calibrated against the voice waveform (with vocal separation via `vocals` -> `transcribe` for sung ads). Use when adding, restyling, or fixing captions/subtitles/supers on a FilmCraft project. Not for general timeline editing, pacing, or non-caption swaps (use `filmcraft-edit`)."
compatibility: "Requires `filmcraft-cli`, `ffmpeg`, `numpy`, and the `transcribe` + `filmcraft-edit` skills. Fonts are bundled in `fonts/`."
metadata:
  author: ai-content-skills
  version: "2.0"
---

# Captions in FilmCraft

Adds editable text-clip captions directly into `.fcproj` timelines via `scripts/fc_captions.py` and keeps B-roll/inserts aligned via `scripts/fc_inserts.py`. Load `filmcraft-edit` alongside this skill for house editing rules, bridge safety, and exports.

## Core Rules

1. **Picture, caption, and voice change on the same frame.** Every V1 cut starts a caption, and every caption starts on the exact frame its first word is heard (never late, never before the cut).
2. **Whole script phrases, max 4 words.** Keep natural clauses together (3 words preferred, 4 max; never split a name, number + unit, or `"65% off"`). **Never leave an orphan 1-word second line** when wrapping.
3. **Back-to-back while speaking, cleared in real pauses.** Each caption holds until the next starts unless the voice pauses ≥ 0.4 s (clears 2 frames after the voice stops). Pass `--hide 0` for continuous back-to-back captions.
4. **Inserts only change on a caption start or V1 cut.** No B-roll or box insert may start or end mid-caption, and no picture may show for fewer than 8 frames.
5. **Never write caption copy that isn't in the script** (use `--fixes` for ASR mishearings of brand words like `alio | aleo` — matching only, never alters on-screen text).

## Step-by-Step Workflow

### 1. Extract voice & word timestamps
FilmCraft may stay open (`fc_captions.py` saves/reloads via `filmcraft-edit`'s live bridge).

```bash
scripts/fc_captions.py words video-N/edit/hook-1.fcproj            # --vo A2 if voice is on A2
scripts/fc_captions.py words video-N/edit/hook-1.fcproj --fast     # Parakeet-only (faster drafts)
scripts/fc_captions.py words video-N/edit/hook-1.fcproj --vocals   # Sung ads: splits vocals first
```

- **Sung ads (Suno / AI singing):** pass `--vocals` (or auto-enabled when `song/` exists). This runs `vocals` (MelBand RoFormer) -> `transcribe` so word timing, pauses, and waveform checks run on the isolated vocal stem rather than the full mix. The project's audio track is never modified.
- Run `words` in the background while preparing the script; check for `captions/<stem>.fw.json` rather than polling with `pgrep`.

### 2. Plan & review caption blocks
Save the hook's exact voiceover script to `video-N/captions/hook-1.script.txt`, then run:

```bash
scripts/fc_captions.py plan video-N/edit/hook-1.fcproj --script video-N/captions/hook-1.script.txt
```

- First run generates a draft `captions/<stem>.blocks.txt` and stops. **Review every line by hand** against Rule 2 (clean phrase breaks, no orphan 1-word 2nd lines), then re-run `plan`.
- `plan` calibrates Parakeet + faster-whisper against the waveform (`pauses.py`), leads pop captions (≤3 words) by 3 frames mid-phrase, snaps captions onto cuts within 6 frames, and runs an automatic waveform audit. Fix any `CHECK`, `BRIEF`, or `NOTE` warnings before building.

### 3. Build text clips into `.fcproj`
```bash
scripts/fc_captions.py build video-N/edit/hook-1.fcproj -t 4       # -t <template>, --track V3, --one-line
```
Backs up the original project to `edit/backup-<date>-captions/` before writing. End cards and overlays stay untouched. Re-run any custom caption Y-position script afterwards (a build resets hand-moved positions).

### 4. Align inserts (when B-roll/insert tracks exist)
Run after every caption build or insert change (skip `snap` on user-tweaked edits — run `check` only):

```bash
scripts/fc_inserts.py split video-N/edit/hook-1.fcproj
scripts/fc_captions.py plan video-N/edit/hook-1.fcproj ... && scripts/fc_captions.py build video-N/edit/hook-1.fcproj -t N
scripts/fc_inserts.py snap video-N/edit/hook-1.fcproj
scripts/fc_inserts.py check video-N/edit/hook-1.fcproj --render
```
`check` must report 0 mid-caption changes, 0 short (<8 f) flashes, and 0 missed frame flips.

### 5. Mandatory Visual Preview Gate (Before Full Export)
**Never export a full video before visually verifying 3–5 rendered frames.**

```bash
scripts/fc_captions.py check video-N/edit/hook-1.fcproj
```
This renders before/after caption-flip pairs into `captions/<stem>.check.png` (or render specific timestamps with `filmcraft-cli --project P render --seconds S --out /tmp/cap_check.png`). Inspect the rendered frames and confirm:
- **Font, weight, size, and stroke/shadow** match the reference or chosen template.
- **Readability against background** (high contrast — darken/grade bright backgrounds or add outline/box if white text washes out).
- **Zero orphan 1-word second lines** and all text inside the Meta/TikTok safe box (bottom `y ≤ 1500` on 1080×1920).
- **Frame-exact flips** on both caption starts and picture cuts.

Send the preview sheet to the user for quick visual sign-off before exporting via `filmcraft-edit` (`fc.py export` or `fc_captions.py export`).

## Templates

Previews are in `templates/`; bundled fonts (`Montserrat`, `TikTokSans`, `AvenirNext-DemiBold`) live in `fonts/` and install to `~/.local/share/fonts`.

| # | Look & Use Case |
|---|---|
| `1` | **Podcast ALL CAPS black boxes:** White TikTok Sans SemiBold 70, no punctuation/hyphens, solid black rounded box per line (`y 1413`), 1–3 words (`--max-words 3`), balanced 2-line wrap. |
| `2` | **ALL CAPS bold:** White TikTok Sans ExtraBold 68, 3 px black outline, soft shadow (`y 1420`). |
| `3` | **TikTok-native sentence case:** White TikTok Sans SemiBold 64, 2 px black outline, dark glow (`y 1408`). |
| `4` | **House default (sentence case):** White Montserrat ExtraBold 68, 3 px black outline, soft shadow (`y 1420`). |
| `5` | **Storybook / ELI5:** White TikTok Sans SemiBold 50, thin outline, 1–2 words (`--max-words 2`), mid-frame (`y 1116`). |
| `6` | **Doctor / explainer white boxes:** Black TikTok Sans SemiBold 58 on tight white rounded boxes (`y 1098/1173` two-line, or `--one-line` at `y 1360`, max ~24 chars). |
| `7` | **Word-by-word pop:** ALL CAPS white Montserrat ExtraBold 85, 3 px outline, hard 6 px shadow, no punctuation (`y 1306`, `--max-words 3`). |
| `10` | **Podcast-ad bold outline:** Sentence-case white Montserrat Bold 57 with punctuation, 5 px black outline, soft downward shadow (`y 1342`), 2–4 words. |

## Rules

- Store all work files (`.vo.wav`, `.pk.json`, `.fw.json`, `.blocks.txt`, `.captions.json`, `.check.png`) in `video-N/captions/`, never in `/tmp`.
- Re-run `words`, `plan`, and `build` after `fc_pace.py tighten` or any voice/cut change (`build` refuses stale plans).
- Never save a `.fcproj` headless while FilmCraft has it open.
