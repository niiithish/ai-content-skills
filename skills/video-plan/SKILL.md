---
name: video-plan
description: Turn a client's video brief into an approved production plan (PLAN.md and matching PLAN.pdf) before generating any stills or clips. Times every shot from a real voiceover read (Cartesia, client recording, or song), locks cast/before-after arc/brand CTA hex colors/asset reuse/engine routing, and produces a Shot | Time | Voiceover | What we show table for any style (photoreal, 3D/Pixar, claymation, talking-head, AI singing, AI drama, informational). Use when starting a new client video or asked for a plan, treatment, shot list, or storyboard. Not for writing ad copy from scratch (use script-generation) or single ad-hoc prompts.
compatibility: Requires python3, chromium, pdf2md, transcribe, and cartesia CLIs.
metadata:
  author: ai-content-skills
  version: "2.0"
---

# Video Plan

The first step of every client video, regardless of style. Outputs `video-N/PLAN.md` (source of truth for `video-production`) and `video-N/PLAN.pdf` (printed directly from `PLAN.md` so the two never drift).

`<skill-dir>` is the folder holding this file. Run every command yourself.

## Mandatory Upfront Plan Locks

Lock these five items in `PLAN.md` **before** generating a single still or clip:

1. **Before/After Visual Arc** *(required for transformation, beauty, health, skincare, or supplement products)*: Define the exact "before" state, the mechanism/product transition, and the visible "after" payoff so stills never contradict the script.
2. **Target Cast & Demographic Lock**: Cast for the **buyer**, not the reference (e.g., women 45–65 → cast ~50–58 even if the reference cast is 28). Lock age, look, outfits, and explicit host vs. guest roles + which lines each speaks. When cloning a reference, change at least one visible attribute per person.
3. **Brand CTA Hex Colors**: Verify exact brand/CTA hex colors from the live product website or client brand kit before locking **End card** and captions. Never guess pure white/black.
4. **Existing Client Asset Reuse Check**: Before planning new insert stills or clips, inspect `<client>/assets/clips/` (and `../assets/`) plus prior approved `video-*/clips/clip-*/final/` folders. Write verified reuses directly into *What we show* (e.g., `reuse assets/clips/pour.mp4, from 1.0 s`) and show a contact sheet of candidates.
5. **Configurable Engine Routing**: State in **Look** / **Sheets** which engine generates what:
   - Default: **Google Flow** (direct 1080p for clips; Nano Banana 2.1 for stills).
   - Optional overrides via `elevenlabs-creative`: **Seedream 5.5 (1K)** for realistic human character sheets *(configurable; Google's upcoming Flow image model is expected to supersede it)*, **Seedance 2.0 Mini / MiniMax H3 Max** for Flow policy-blocked scenes, **Kling 4.0 (1080p)** for strict product-label text fidelity.

## Workflow

### 1. Initialize Folders & Read Brief in Full
- Run `python3 <skill-dir>/scripts/plan.py init <client-folder> video-1` (creates `brief/`, `video-1/PLAN.md`, `video-1/voiceover/` without overwriting; moves loose videos to `reference-video/` and docs/images/audio to `brief/`). For standalone video folders that already hold their own brief or `AGENTS.md`, run `plan.py init <client>/video-N .` so it initializes in place.
- Save chat-message briefs verbatim to `brief/message-YYYY-MM-DD.md`.
- Convert PDFs once: `pdf2md --raw "brief/<name>.pdf" > "brief/<name>.md"` and read every `.md` in `brief/` in full (including editing and caption notes).
- **Reference videos**: run the local `video-breakdown` skill on each reference video before planning. Copy its rhythm, insert cadence, and beat structure into the plan.

### 2. Layout & Style
- Follow [templates/PLAN.md](templates/PLAN.md) strictly: Title (`<Product> "<Concept>" <ad type>: plan`), summary line, bold-labelled paragraphs (**Concept**, **Look**, **Camera**, **Cast**, **Sheets**, **Blocking**, **Light**, **On camera**, **End card**, **Open questions**), then the shot table. No extra headings or stray lists.
- Pick the visual style from the brief/reference/client history (`photoreal`, `pixar-3d`, `claymation`, `talking-head`, `ai-singing`, `ai-drama`, `informational`). If ambiguous, ask the user before proceeding.

### 3. Time the Voiceover First
- **Ask playback speed up front** for talking-head or VO ads (commonly `1.1x`) so timing and clip lengths match the edit from day one.
- Copy the script word for word into `video-N/voiceover/script.md` (one spoken line per row, story order).
- **Voice source**:
  - Client recording → save at `voiceover/recording.wav` (or `.mp3`/`.m4a`).
  - TTS → follow `cartesia-tts` in **one concise message** (tool, 3–5 suggested voices with samples in `voiceover/voices/`, speed, emotion), wait for pick, then generate `voiceover/recording.wav` + `recording.words.json`.
  - **On-camera speakers** (Flow generates voice inside clips) → run `plan.py voiceover <video-folder> --on-camera` (estimates at 3.2 words/sec).
  - **Sung ads (AI singing)** → follow `video-production/references/styles/ai-singing.md` first to lock lyrics and chosen Suno take as `voiceover/recording.wav` (split vocals via `vocals` / `transcribe --vocals` for accurate timing).
  - No spoken words → skip voiceover timing and time shots by action.
- Run `plan.py voiceover <video-folder>` to produce `voiceover/timing.md` (uses `recording.words.json` or local `transcribe` Parakeet).

### 4. Build the Shot Table (`Shot | Time | Voiceover | What we show`)
- **Time**: `12.6 – 14.4 s`, back-to-back from `0.0 s` to end of audio. Max 10 s per clip (shortest Flow length: 4, 6, 8, or 10 s).
- **Voiceover**: exact spoken words heard in that shot; `(cont.)` for continuations; `[instrumental]` / `(intro)` for music-only beats.
- **On-camera dialogue**: never split a sentence mid-clip; keep lines ≤9.5 s in one clip ending 0.5–2 s after the last word; split longer lines at sentence/clause breaks into the fewest chained clips.
- **Shot IDs**: `1`, `2`, or `1a`, `1b` for distinct visual beats within one scene (never alternate takes).
- **No text/captions in the shot table**: captions, end card copy, CTA hex colors, and music go in **End card** so they never leak into generation prompts.
- **Visual craft**:
  - Open each *What we show* with place + camera framing (`Kitchen, low angle, locked:`). Change camera framing between adjacent shots; aim for something new every 2–5 s.
  - Every shot must start from a composable still (characters already in place, facing/eyeline stated, clear action and end state).
  - Paired continuous moments (pour → sip) are planned as a chained edit of the first still so props never vanish/appear.
  - Note asset reuses explicitly (`reuse assets/clips/...`).

### 5. Cast, Sheets, Blocking & Light
- **Character sheets**: required for anyone in **2+ shots** or **speaking/singing on camera**. List every outfit with its exact shot range (`everyday (4–23)`, `sleep (1–3, 24–27)`). Base outfit = base sheet; extra outfits = edited from approved base so face stays locked. Include base **Acting** direction per character.
- **Extras never get a sheet**: list them at the end of **Sheets** under `Extras, no sheet:` and keep them secondary.
- **Environment sheets**: for **3D animation & claymation only** (places appearing in 2+ shots, listing key story items). **Photoreal uses no environment sheets** — each location's first approved still is its look reference. Never make sheets for CGI/macro/voids/product tabletops.
- **Prop sheets**: always make one for the client's product from real product photos (`--ref`); only make other prop sheets if the same item travels across 2+ locations.
- **Blocking & Light**: whenever 2+ sheet characters share a room, lock spatial positions by room landmarks (180° rule) and specify the visible key light, rim light, and shadow areas.

### 6. Verify, Print & Gate
Run `plan.py pdf <video-folder>` (updates summary line, flags gaps/overlaps/>10 s shots, prints `PLAN.pdf` via Chromium) and check:
- [ ] Every sentence of the script is in Voiceover word for word (rerun after any shot merge/split/cut).
- [ ] Upfront locks present: Before/After arc (if applicable), Buyer demographic cast, verified Brand CTA hex colors, `assets/` reuse check, Engine routing.
- [ ] On-camera lines never split mid-sentence; every shot starts from a composable still; no two consecutive identical framings.
- [ ] Sheet rules followed (2+ shots / on-camera = sheet; extras = no sheet; outfits listed; env sheets only for 3D/clay).
- [ ] Zero captions or on-screen text inside the shot table.

Send `PLAN.pdf` with a short summary of invented visuals and open questions. Once approved, set the top Status comment to `approved YYYY-MM-DD`. In unattended runs, resolve open questions conservatively, mark them `(agent)`, and self-approve.

## Hand-Over

Once approved, load **`video-production`** and its matching style reference (all styles share one pipeline and `make.py`):

| Style | Pipeline Skill + Style Reference |
|---|---|
| Photoreal VO / B-roll / VSL / UGC | `video-production` → `references/styles/photoreal.md` |
| 3D feature animation (Pixar / DreamWorks) | `video-production` → `references/styles/pixar-3d.md` |
| Claymation / stop-motion / halfway-clay | `video-production` → `references/styles/claymation.md` |
| Talking head + inserts / podcast / hybrid | `video-production` → `references/styles/talking-head.md` |
| AI singing / Suno story song ad | `video-production` → `references/styles/ai-singing.md` |
| AI drama / VSL cold-open remake | `video-production` → `references/styles/ai-drama.md` |
| Informational / medical / 3D CGI explainer | `video-production` → `references/styles/informational.md` |
