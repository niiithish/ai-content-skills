# Shared Failure Locks (Every Style)

Cross-style QA checklist and known failure modes for Flow, ElevenLabs fallbacks, batching, and delivery. Read this alongside your loaded style module in `references/styles/`.

## Autonomous Pre-Review QA Checklist

Check every tile in `make.py review` before showing the user:

1. **Identity & Demographics:** Faces, hair, age, and outfits match approved sheets and `PROJECT_STATE.json` cast locks.
2. **Before/After Arc:** For transformation/beauty/health products, early "problem" shots visibly show the problem state; "after" glow appears only post-product.
3. **Counts & Permanence:** Exact count of characters, pills, softgels, bottles, and papers from first frame to last — nothing multiplies or vanishes.
4. **Anatomy & Real-Life Logic:** Products applied to the right body part (e.g., cellulite on thighs, never calves); monitors/drawers face their user; hands/limbs look natural; mirrors reflect the exact same pose and outfit (never draw a second person in a mirror).
5. **No Burned-In Artifacts:** Zero captions, subtitles, UI buttons, watermarks, film gear (cameras/tripods), or grey reference-sheet backdrops.
6. **Printed Text & Realistic Competitor Branding:** Hero product labels match the real pack photo (`--ref`). **Never make plain white / blank unbranded packaging** for competitor or alternative products just to avoid trademarks — invent a **realistic fictional retail brand** (believable invented name, clean typography, distinct colors, and real store-bought label layout that contrasts with the hero product).
7. **Spatial & Background Continuity:** Adjacent shots in the same location share walls, lighting, and left/right character placement (pin characters to room landmarks, not "left/right").
8. **Start State & Motion:** Still shows the state *before* the clip's action; clips actually move (never a frozen still-image clip) and never exceed Flow's simple-action comfort zone (avoid writing/ticking calendars, complex spins, or simultaneous multi-step hand choreography).
9. **Eyeline & Tone:** Nobody stares into the camera unless the plan says so; facial expression matches the VO emotion (never smiling on a pain/problem line).
10. **Talking Clips (Audio Check):** Transcribe with `transcribe` and diff against the script — every word said once, zero dropped/repeated words, zero mid-word cutoffs.

## Engine & Batch Failure Locks

| Symptom | Root Cause | Fix |
|---|---|---|
| **Broken/glitched still keeps repeating its flaws** | Rejected image fed back as a reference | **From-Scratch Regeneration Lock:** never pass a broken image as ref. Regenerate cleanly from canonical sheets + simplified prompt. |
| **Clip opens on wrong pose or jumps backward** | End-state still passed as `start_frame`, or `ingredient` confused with start-frame | Default to **reference-image (`ingredient`)** mode. Only use `start_frame` when the still is explicitly frame 0. |
| **ElevenLabs burns 4x credits or returns sideways/cropped 16:9** | ElevenLabs defaults to `quantity=4` and `aspect_ratio=auto/16:9` | Always set explicit `aspect_ratio: 9:16` (or target ratio) and **`generations_count: 1`**. Check output dimensions immediately. |
| **Flow hard blocks (`PROMPT_REJECTED` / `UNSAFE_GENERATION`) on bed/couple, child, or bare-skin/cellulite scenes** | Google hard safety filter | Try once cleanly (scene still only), then route straight to `elevenlabs-creative` (`Seedance 2.0 Mini`, `Kling 4.0`, or `MiniMax H3 Max`). Never silently rewrite the client's script. |
| **Flow soft / false-positive blocks (gym activewear/midriff, pill box/capsules, `IDENTIFIABLE_PERSON` on normal adults)** | Over-literal body/clinical keywords or multi-ref false positive | **Always reword & simplify on Flow first** (blocked runs are refunded): (1) replace body/weight-loss words with emotion/activity ("happy with her gym progress"), (2) replace "pills/medication/dosage" with neutral objects ("compartment organizer box", "amber wellness bottle", "golden softgels"), (3) drop extra refs, simplify to 1–2 plain sentences + new seed, or switch `--ingredient` → `--start-frame` on the approved still for `IDENTIFIABLE_PERSON`. |
| **Flow `UNSAFE_GENERATION` on older men ("60, bald") or legal/religious text** | Keyword trigger in prompt | Drop age numbers + "bald" → "middle-aged, salt-and-pepper hair"; soften formal legal/religious prop text ("DIVORCE AGREEMENT", plain book). |
| **Flow launches/closes Chrome in a loop or hangs >10 min** | Stale session/cookie or stalled queue | Stop immediately (`flow` skill recovery). Report exact command, error code, and last log lines to user; do not poll endlessly. |
| **Scene stills come out landscape (1376×768)** | Missing `"aspect": "9:16"` in job | `make.py` auto-fills `"aspect": "9:16"` for stills/clips; sheets stay 16:9. |
| **Camera/tripod appears inside the scene** | Prompt said "locked off on a tripod" | Never name camera gear in clip prompts. Write "Camera: static, exact framing of @image1; no cameras, tripods, or film gear." |
| **Stray manifests / logs piling up in `scenes/` or `clips/`** | Ad-hoc `flow batch` calls outside `make.py` | Always use `make.py`; all run files and logs stay in `.flow/`. Run `make.py status` to catch stray files. |
| **Still/clip picks up random outfit or background** | Unneeded extra reference passed | Every ingredient must have one explicit job named in the prompt; remove any reference that isn't strictly needed. |
| **Regenerated an already-approved shot after compaction** | Lost conversation history | Check `PROJECT_STATE.json` (`approved_stills` / `approved_clips`) before writing any batch job. |
| **Clips slowed to 77% or stretched audio in edit** | Clip generated shorter than VO line | Time every shot from the real VO/song before generating; pick the shortest Flow length (4/6/8/10 s) that covers the slot + 1 s buffer. Never slow normal action clips to 77%. |
