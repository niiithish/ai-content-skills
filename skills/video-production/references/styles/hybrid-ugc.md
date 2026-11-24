# Style Module: Hybrid UGC & Surgical Product Swaps (`--style hybrid-ugc`)

Mixed-format performance ads combining an on-camera talking head / creator, handheld UGC B-roll montage, screen recordings, and surgical brand/product swaps into proven ad structures.

## 1. Architecture (Combine Only What Each Shot Needs)

A hybrid UGC ad mixes shot types inside **one unified `PLAN.md` and `make.py` manifest**:
- **Talking-head beats** (`1..99`, plus hook takes `h1`, `h2`, `h3`): follow `talking-head.md` (master still, direct 1080p clips, ElevenLabs Voice Isolator/Changer unification).
- **Handheld UGC / lifestyle B-roll inserts** (`201+`): follow `photoreal.md` (raw phone-camera feel, candid natural room light, no studio polish).
- **Anatomical / ingredient mechanism beats** (if present): follow `medical-cgi.md`.
- **Screen scrolls / Amazon / website captures**: capture cleanly via `media-utils` (`agent-browser`), never generated in Flow.
- **Cutout / tier-board / picture-in-picture overlays**: generate clean plates here; handle background removal (`media-utils` `rembg-cutout`) and consistent side placement in **`filmcraft-edit`**.

## 2. Surgical Brand & Product Swap Rules

When remaking a winning reference ad for a new brand/product:
1. **Check `../assets/` library first:** Reuse approved B-roll, ingredient animations, or product shots from earlier client videos with `make.py reuse` — unless the user explicitly asks to build a fresh variant for the library.
2. **Real product fidelity:** Always pass the client's real product photo/sheet (`@image2`) and quote exact label text. Keep hand-to-bottle scale realistic (use a hand-holding scale reference if the bottle drifts too large/small; pass **only 1** clean scale reference, never conflicting pairs).
3. **Avoid over-reusing one clip across multiple VO beats:** If the VO lists 3 distinct problems (e.g., *"sagging skin, small scars, dark spots"*), generate **3 distinct visual clips** — never hold one B-roll clip across all three.
4. **Match reference transitions selectively:** If the reference uses a signature transition (e.g., light leak, golden flash), note it for `filmcraft-edit` and cap its usage (e.g., max 3–4 key pivots — never spam it on every cut).

## 3. Clip & Audio Discipline

- **Direct 1080p clips** via `make.py clips` (concurrency 10–12). Route safety-blocked body/thigh/intimacy inserts to `elevenlabs-creative` (`Seedance 2.0 Mini` or `Kling 4.0`, always `9:16` and `quantity=1`).
- **Voice-isolator batching:** Export all talking clips together via `scripts/voice_change.py export` so the user can run one ElevenLabs pass instead of uploading clips one by one.
- **VO-to-clip sync check (mandatory):** Before handing off to `filmcraft-edit`, verify every insert clip's shot ID maps to the exact VO phrase in `PLAN.md` (never let an insert land on the wrong spoken line).
- **Hook variants (H1, H2, H3):** Finalize Hook 1 completely first; clone the approved body to Hooks 2 & 3 in `filmcraft-edit` and swap only the hook opening clips and hook VO.
