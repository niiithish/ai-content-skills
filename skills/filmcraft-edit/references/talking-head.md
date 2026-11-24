# Talking-Head Edit Reference

Use when one speaker (doctor, expert, creator) or a two-woman podcast carries the script on V1/A1 with full-screen inserts on V2.

## Track Layout & Numbers (24 fps, 1080×1920)

| Track | Contents | Key Numbers |
|---|---|---|
| `V1` / `A1` | Speaker talking clips | Normalized to **−16 LUFS**; 1.1x speed default (1.12x when reference is faster); joins cut to ~0.25 s voice-to-voice; hook-to-body ~0.37 s; inner pauses ≥ 0.35 s cut to ~0.20 s; opening silence < 0.3 s. |
| `V2` | Full-screen inserts (B-roll / stills) | Scaled to fill 1080×1920; new picture every 2–4 s; speaker face visible ~25% of runtime; stills push at **2 %/s** from first frame to last; never swap a video clip for a still. |
| `V3` | Optional green-screen speaker cutout (Format D) or split listener (Format C) | Scale 70%, right `(991, 1423)` or left `(301, 1423)`. |
| `V4+` | Captions, hook title, overlays (`exploding-head-iphone.png`, `cta-arrows-red.png`) | Captions via `captions-filmcraft` (e.g., Template 6 one-line at box centre `y 1360`, or Template 1 for podcast). |
| `A2` | Background music | **−16 to −18 dB under voice**, 1–2 s fade-out. |
| `A3` | SFX (card word clicks, camera clicks) | `assets/switch-click-02.mp3` where reference uses clicks. |

## Build Order

1. **Talking master (`talking-head.fcproj`).** Assemble approved talking finals (with ElevenLabs Voice Isolator / voice-changed audio normalized to −16 LUFS). Cut V1 at every clip join so hidden jumps become real cuts.
2. **Hook 1 (`hook-1.fcproj`).** Place V2 inserts on their spoken phrases, ensuring every V1 jump cut sits under an insert or on a caption start. Ensure the speaker finishes her word before an insert covers her.
3. **Pacing & motion.** Tighten dead air (`fc_pace.py`), add slow centred push on talking stretches (+3% per 3 s) and 2 %/s push on all stills. Avoid jarring hard-cut jump zooms in the hook opening (use one continuous slow zoom across opening cuts).
4. **Captions.** Run `captions-filmcraft` (`words`, `plan`, `build`, `check`) and `fc_inserts.py check`. Re-apply any custom caption Y-positions (a caption build resets positions).
5. **Audit & QA.** Run `scripts/audit.py` and `scripts/fc_qa.py`, then hand hook 1 to the user.
6. **Hooks 2–3.** Clone the user's finished hook 1, swapping only the opening clips/voice/captions. Prove body parity with `scripts/audit.py hook-N.fcproj --body-of hook-1.fcproj --offset O --from F`.

## Approved Formats (A–D)

- **Format A — Podcast Mic (single speaker):** Speaker looks slightly off-lens. ~3 s hook: glam photo under 2-line title + `exploding-head-iphone.png` (scale 12, box centre `y ~655`, never over her face), 8-frame Push from east (80% blur) onto her face (hide title as push starts so text doesn't smear).
- **Format B — Straight to Lens (expert/doctor):** ~4 s hook: 3 pictures (2 s, 1 s, 1 s) with 6-frame Push transitions under 2-line title (`y 422`), into a black word card where each word pops on its spoken onset with `switch-click-02.mp3` on A3, then Push onto speaker. Optional `cta-arrows-red.png` bobbing over CTA.
- **Format C — Two-Woman Podcast (splits):** Host and guest on separate masters looking off-camera at each other. Splits are built in the edit (top/bottom crop: top 10%, bottom 40%, positions `y 768` / `1728`) using silent listener clips. Move split captions onto the seam (`y 506`) after every caption build. Use separate ElevenLabs voices per speaker.
- **Format D — Tier List / Cutout Over Inserts:** Keyed green-screen cutout on V3 in a bottom corner over V2 inserts.
  - **One side per stretch:** switch sides only between full-face shots, name cards, or tier boards — never per clip. Hide cutout on full-face shots (never two of her), name cards, bottle hero, and CTA.
  - **Clean cutout cuts:** sit in silence between sentences; eyes open on first frame; no late head jumps 1–2 frames after the V2 cut; mouth closes before the insert ends; whole-frame durations only (`duration % frame_ticks == 0`).
  - **Never** use 2–4 frame freezes, 1.5x speed-ups, or morph/cross-dissolve across cutout jumps. If source is a 30 fps Canva export of 24 fps footage, deduplicate repeated every-5th frames back to 24 fps before retiming.
