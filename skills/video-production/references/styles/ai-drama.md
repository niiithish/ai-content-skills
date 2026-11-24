# Style Module: AI Drama / Cinematic VSL Cold Open (`--style ai-drama`)

Photoreal cinematic storytelling and shot-for-shot VSL cold-open remakes ("rip" of a winning control: e.g., 3 AM hospital alarm, suburban dog rescue, rainy foster-home departure, period black-and-white flashbacks).

## 1. Breakdown & Shot-Length Lock

1. Decode the control video first with **`video-breakdown`** to get exact shot lengths, camera angles, eyelines, and beat rhythm.
2. Match the control's emotional pacing and cut lengths — typically 1.5–3.5 s per shot in tense action, holding slightly longer on emotional reveals.
3. For side-by-side QA against the original control, use the localhost side-by-side comparison review board (`media-utils`).

## 2. Multi-Character Spatial Continuity Lock

The #1 failure mode in AI drama is characters **shifting positions, swapping sides, or changing room walls** between consecutive shots in the same scene (e.g., hospital room, river bank, living room).

- **Generate recurring character & environment sheets first** (prefer `Seedream 5.5 1K` for human character sheets when configured in `PROJECT_STATE.json`, keeping `9:16` / `16:9` explicit and `quantity=1`).
- **Chain consecutive stills inside a conversation/room:** When shot `N+1` stays in the same space with the same two people, wait for shot `N` to approve and pass shot `N` (or a reference frame from the control for blocking/angle) so spatial geometry and character sides stay locked.
- **Pin every character to a room landmark** (never bare "left/right"): e.g., *"Marcus stands on the river-bank side by the wooden railing; the doctor stands on the house-porch side."*
- **Lock lighting & color grade per location** (e.g., *dark blue 3 AM bedroom with one warm bedside lamp*; *harsh cool-white cath lab*; *overcast late-autumn brick suburb*; *black-and-white documentary film grain for 1950s flashbacks*). Copy the exact Light line into every still of that location.

## 3. Clip Generation & Safety-Block Fallback

- **Reference-image mode by default:** Pass the approved still as `@image1` (reference image, **never** start-frame unless explicitly requested). Include character sheets only when a face is hidden/turns or someone enters.
- **Audio:** Write `"Quiet room tone and natural foley only; no music, no score, no dialogue"` (unless on-camera speech is explicitly in the plan). Writing `"quiet room tone"` works better than bare `"no music"`.
- **Flow Safety Blocks (beds, medical emergencies, children, conflict/violence):**
  1. Do **not** silently rewrite the client's script or alter the scene image to bypass a block without asking.
  2. Test **once** on Flow without the character sheet (scene still only) — bed + character sheet frequently triggers false-positive identifiable-human blocks.
  3. If Flow still blocks, immediately route the blocked shots to **`elevenlabs-creative`**:
     - **Seedance 2.0 Mini (720p, `9:16`, `quantity=1`)** for photoreal drama & bed/medical scenes.
     - **MiniMax H3 Max (`9:16`, `quantity=1`)** for scenes with clearly visible children.
  4. Report the exact count of blocked clips and estimated ElevenLabs credits before running the fallback batch.

## 4. Pre-Review QA Additions

- Verify characters never swap sides or teleport between adjacent shots in the same room.
- Verify color temperature and film grain match across consecutive shots of the same location/era.
- Verify no floating leashes, duplicated props, or camera/tripod gear in frame.
