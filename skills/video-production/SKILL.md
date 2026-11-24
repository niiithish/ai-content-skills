---
name: video-production
description: Shared short-form AI video production hub for any visual style (photoreal, Pixar 3D, claymation, talking-head, AI singing, AI drama, medical CGI, hybrid UGC, 2D storybook). Use for turning an approved PLAN.md into reference sheets, scene stills, 1080p clips, and edit hand-offs via init-project.sh and make.py, or for single style-specific sheet/still/clip prompts. Not for writing scripts (script-generation), breaking down reference videos (video-breakdown), planning/timing shots (video-plan), FilmCraft timeline editing (filmcraft-edit), or captions (captions-filmcraft).
compatibility: "Requires Python 3, ffmpeg, ffprobe, ImageMagick (magick), and the flow (labflow) CLI. Optional: elevenlabs-creative fallbacks, vocals/transcribe for sung or talking-head ads."
metadata:
  author: ai-content-skills
  version: "2.0"
---

# Video Production Hub

Turn an approved `PLAN.md` into a finished set of 1080p 9:16 clips with minimal retries, autonomous QA, and zero wasted credits.

## 1. Load Your Style Module (1 Level Deep)

Pick the project's style from `PLAN.md` / `PROJECT_STATE.json` and read **only that one** module under `references/styles/`:

| Style (`--style`) | Module | Use when |
|---|---|---|
| `photoreal` | [references/styles/photoreal.md](references/styles/photoreal.md) | Real-world lifestyle, UGC, and product B-roll under voiceover |
| `pixar-3d` | [references/styles/pixar-3d.md](references/styles/pixar-3d.md) | Stylized 3D feature-animation CG (Pixar/DreamWorks look, product mascots, animated talking clips) |
| `claymation` | [references/styles/claymation.md](references/styles/claymation.md) | Hand-sculpted plasticine / stop-motion / halfway-clay videos |
| `talking-head` | [references/styles/talking-head.md](references/styles/talking-head.md) | Doctor/expert/creator speaking to camera + inserts, simple talking-head clips, or UGC ad remakes |
| `ai-singing` | [references/styles/ai-singing.md](references/styles/ai-singing.md) | Suno story-song / singing ads (lyrics, vocal-onset sync via `vocals`, `song.py` slices, lip-sync handoff) |
| `ai-drama` | [references/styles/ai-drama.md](references/styles/ai-drama.md) | Cinematic VSL cold-open drama rips with multi-character spatial continuity & safety-block fallbacks |
| `medical-cgi` | [references/styles/medical-cgi.md](references/styles/medical-cgi.md) | Anatomical / skin-layer / gut-health 3D CGI explainers (biological plausibility lock; optional stylized inner-world) |
| `hybrid-ugc` | [references/styles/hybrid-ugc.md](references/styles/hybrid-ugc.md) | Mixed talking-head + B-roll + UGC montage + surgical brand/product swaps |
| `storybook-2d` | [references/styles/storybook-2d.md](references/styles/storybook-2d.md) | Hand-inked watercolour / ELI5 illustrated stills-only slideshows |

Core references (load on demand):
- [references/sheets/](references/sheets/) — shared character, place, and product sheet layouts + JSON blueprints.
- [references/failure-locks.md](references/failure-locks.md) — cross-style QA checklist, Flow/ElevenLabs locks, and batch recovery.
- [references/project-state.md](references/project-state.md) — anti-compaction `PROJECT_STATE.json` schema.

## 2. Non-Negotiable Production Locks

1. **Read & update `PROJECT_STATE.json`** at session start, after every context compaction, and at every gate. Never regenerate any shot listed in `approved_stills` or `approved_clips` unless the user explicitly names it.
2. **Direct 1080p clips by default.** Run `make.py clips` (which generates native 720p + 1080p upsample directly) yourself once stills are approved — do not force the user to type `make.py finals` manually. Use `make.py clips --draft` (360p) **only** when the user explicitly asks for drafts or on a risky experimental beat.
3. **Concurrency 10–12 default (`CONCURRENCY=10`, `RPM=12`).** Batch all independent sheets, stills, and clips in parallel via `make.py`. Never generate 1-at-a-time unless a shot explicitly chains from the previous shot's output (e.g., outfit edits from a base sheet, or `lastframe` chains).
4. **From-Scratch Regeneration Lock.** NEVER feed a broken, glitched, blurry, or rejected still/clip back as a reference image — it carries the defect forward. Regenerate cleanly from canonical sheets + a simplified prompt.
5. **Reference-Image vs. Start-Frame Lock.** Pass stills and sheets as **reference images (`ingredient`)** by default. Only use start-frame mode when the still is explicitly the exact opening pose (frame 0) and the user/style calls for it — never pass an end-state still as frame 0.
6. **Configurable Engine Routing (never permanently hardcoded).** Read `engines` from `PROJECT_STATE.json`:
   - **Flow** (`flow` skill) is the primary engine for stills and 1080p clips.
   - **Seedream 5.5 (1K)** via `elevenlabs-creative` is currently strong for realistic human character sheets (note: Google's upcoming Flow image model is expected to supersede it — update `PROJECT_STATE.json` when switching defaults).
   - **ElevenLabs video fallbacks** (`Seedance 2.0 Mini`, `Kling 4.0`, `MiniMax H3 Max`) handle Flow safety blocks (beds, thighs/cellulite, children) or blur. Always set explicit aspect ratio (`9:16`) and **`quantity=1`**.
7. **Reuse before regenerating.** Check `../assets/` and prior client videos first. Pull approved assets in with `make.py reuse SHOT /abs/path/to/clip.mp4`.
8. **`make.py` owns all batching.** Every still and clip belongs in `scenes/stills-batch.json` or `clips/clips-batch.json`. A retry is the next version (`v2`, `v3`) replacing the old job in place, then `make.py stills 3b 7a`. Never write stray manifests or call `flow batch` ad-hoc beside the media.
9. **Clean plates only.** Never generate captions, subtitles, watermarks, or music inside stills or clips unless the plan explicitly requires on-camera dialogue.

## 3. Autonomous Pre-Review QA Gate (Before Showing the User)

After every batch, run `make.py review stills|clips|finals` and inspect **every tile** before reporting to the user. Auto-fix (regenerate from scratch once as the next version) if any tile fails:

- [ ] **No burned-in captions, UI chrome, watermarks, or sheet grey backdrops.**
- [ ] **Object & anatomy counts:** exact number of pills, softgels, papers, bottles, limbs, and characters from start to end frame.
- [ ] **Anatomy & product placement logic:** product applied to the right body part (e.g., thighs, not calves), monitors/drawers facing their user, readable product label matching the real photo.
- [ ] **Before/after visual arc consistency:** transformation/beauty/health products visibly show the "before" problem state in early shots and the "after" result only after product introduction.
- [ ] **Background & spatial continuity:** adjacent shots in the same room keep consistent walls, props, lighting, and left/right character positions.
- [ ] **Voiceover / action match:** facial expression matches the VO emotion (no smiling on a problem line) and motion actually happens (no static "still image" clip).

**Capability-aware video QA fast-path:** If your runtime supports native video input (e.g., Gemini / Antigravity), watch generated `.mp4` clips directly (especially complex motion or flagged shots) to catch temporal defects contact sheets miss — disappearing/reappearing items, auto-closing doors or trays, wrong walk direction, morphing objects, and AI physics glitches. Text/image-only agents fall back seamlessly to `make.py review` contact sheets and extracted frames.

For human review, start the local review board if installed (`${REVIEW_BOARD_BIN:-review} <project>`, or see `media-utils`) and read flags with `${REVIEW_BOARD_BIN:-review} flags <project>`. Keep chat replies terse: a short status table + one line on what is next.

## 4. Pipeline Phases

### Phase 1: Plan & Init
1. Start from an approved `PLAN.md` (`video-plan` skill) with locked cast demographics, before/after arc, brand CTA hex colors, and VO/song timestamps.
2. Initialize the folder (from `<skill-dir>`):
   ```bash
   bash scripts/init-project.sh <client-folder> video-N --style <style>
   ```
   Fill `video-N/PROJECT_STATE.json` with the plan's locks and engine config.

### Phase 2: Reference Sheets
1. Make only the recurring character, environment (for 3D/clay/drama), and product sheets listed in `PLAN.md`. Never make sheets for background extras.
2. Generate base sheets in parallel (`make.py sheet <prompt> [--ref <photo>]`). Outfit variants wait for their approved base sheet (`--ref <base-sheet>`).
3. **Gate:** user approves sheets. Record approved paths in `AGENTS.md` and `PROJECT_STATE.json`.

### Phase 3: Scene Stills
1. Write one prompt per shot (`scenes/scene-N/scene-Nx/prompts/scene-Nx-v1.md`) using the loaded style module.
2. Populate `scenes/stills-batch.json` (`"aspect": "9:16"`, `"variants": 1`) and run `video-N/scripts/make.py stills` in the background.
3. Run `make.py review stills`, complete the Pre-Review QA Gate, fix obvious rejects once from scratch, then present to the user.
4. Optionally generate `make.py animatic` over the voiceover/song to verify pacing before clip spend.
5. **Gate:** user approves stills → record IDs in `PROJECT_STATE.json` and `scenes/all/APPROVED.md`.

### Phase 4: 1080p Clips
1. Open each approved still and write its clip prompt from what is **actually visible** in the still (`clips/clip-N/clip-Nx/prompts/clip-Nx-v1.md`).
2. Populate `clips/clips-batch.json` (duration = shortest Flow length 4/6/8/10 s covering the plan's Time; `"ingredient"` = approved still first, plus character/product sheet only when a face is hidden, someone enters, or a printed label must stay readable).
3. Run `video-N/scripts/make.py clips` (direct 1080p default; pass `--draft` only if 360p drafts were requested) in the background.
4. For chained shots, extract the opening frame from the previous clip's 1080p final: `make.py lastframe 8a 8b`.
5. Run `make.py review finals` (or `review clips` for drafts), complete the Pre-Review QA Gate (and transcribe talking clips with `transcribe` to verify zero repeated/dropped words), then report to the user.
6. **Gate:** user approves clips → record IDs in `PROJECT_STATE.json` and `clips/all/APPROVED.md`.

### Phase 5: Hand-off to Edit & Captions
1. Run `video-N/scripts/make.py handoff` (writes story-ordered `edit/clips/NN-*.mp4` + `ORDER.txt`).
2. Hand off timeline assembly, pacing, and export to **`filmcraft-edit`**, and captions to **`captions-filmcraft`**.
3. Deliverables go in `video-N/deliverables/<Brand>_<Concept>_<Variant>_<Ratio>.mp4`.

## 5. `make.py` Quick Reference

| Command | Action |
|---|---|
| `status` | Shot-by-shot table (still, clip, 1080p final), checks `PLAN.pdf` freshness & stray files |
| `sheet PROMPT [--ref IMG] [--seed N]` | Generate one 16:9 reference sheet next to `prompts/` |
| `stills [shots] [--dry-run]` | Batch scene stills (`CONCURRENCY=10`, skips finished, syncs `scenes/all/`) |
| `clips [shots] [--draft] [--into DIR]` | Direct 1080p clips by default (`--draft` for opt-in 360p) |
| `finals [shots] [--into DIR]` | Alias for 1080p generation / upscaling of existing drafts |
| `reuse SHOT SRC` | Import an approved still/clip from another video or `../assets/` |
| `lastframe FROM TO` | Extract frame 0.5 s before end of `FROM`'s 1080p final for chained shot `TO` |
| `review stills\|clips\|finals [shots]` | Build labeled contact sheets in `review/` |
| `animatic` | Build `edit/animatic.mp4` over `voiceover/recording.*` |
| `handoff` | Export story-ordered clips + `ORDER.txt` into `edit/clips/` |
| `sync` | Refresh `scenes/all/` and `clips/all/` to newest versions |
