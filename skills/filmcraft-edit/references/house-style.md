# House Editing Style (Canonical Rules)

These principles apply across every short-form ad edited in FilmCraft (talking head, voiceover B-roll, AI sung ads, claymation, 3D animation, and stills slideshows). Client/video `AGENTS.md` or `CLAUDE.md` overrides defaults; newest user feedback overrides older notes.

## 1. Visual Rhythm & Picture Cuts

- **Copy the client's reference ad.** Match its pacing (cuts/sec), caption look/height, lighting/contrast, hook structure, and severity. Measure from frames (`video-breakdown`) rather than guessing.
- **Something new every 2–4 s.** A new picture, cut, or subtle motion step. Never two static shots in a row; never repeat a picture inside a hook.
- **Picture changes land ONLY on a caption start or a V1 cut**, on the first frame of the spoken phrase. Never change mid-caption; never show a picture for fewer than 8 frames (no 1–3 frame flashes).
- **Each picture holds until the next one.** Never leave a gap or black frame while the voice runs.
- **Splits, grids, and cards are built in the edit** from separate centred clips/stills (50/50 split with seam, top/bottom split, word cards, CTA overlays) — never generated as one split frame.
- **Respect raw-timeline handoffs.** If the user says *"just add clips rawly without any trim, I will trim"*, place the clips cleanly without auto-trimming or auto-pacing.

## 2. Motion & Flow Clip Lead-In

- **Every still moves:** slow, centred push from its first frame to its last at **2 % of start scale per second** (e.g., 2 s still = 100% → 104%). Never starts late, never stops early, no sideways drift.
- **Flow clip lead-in trim (canonical):** trim dead/static lead-in at the start of AI video clips using **motion/audio onset** (fallback: **0.5–1.0 s** when onset isn't measurable).
- **Start-to-end-state clips play whole:** speed them up to fit their slot so the end state is seen.
- **No destructive speed-downs or robotic stretching:** never slow clips down to ~77% or heavily time-stretch voiceover. If a clip is too short for its slot, extend/swap/regenerate it rather than visibly dragging it.
- **No jarring hard-cut jump zooms on silences:** in hook openings, use a continuous slow zoom across jump cuts rather than harsh 100↔110% steps; cover body jump cuts with B-roll/inserts whenever possible.
- **Hook-to-body transition:** 8-frame FilmCraft `zoom_blur` centred on the V1 cut (4 frames on a split's listener track).

## 3. Audio & Loudness (Canonical)

- **Voice is the only media sound:** mute B-roll/insert audio tracks unless it is a talking clip.
- **Normalize every voice source to −16 LUFS** before building the timeline so multi-clip takes and ElevenLabs voice swaps never jump in volume.
- **Music loudness (canonical): −16 to −18 dB under the voice** (verified with `ffmpeg` `ebur128` / `fc_qa.py`), with a smooth **1–2 s fade-out** at the end. When ducking into a talking head, ramp volume smoothly instead of a hard cut.
- **Dead air cut to a natural breath:** pauses ≥ 0.35 s cut to ~0.20 s (keeping ~0.04 s before the next consonant so words are never clipped). Never cut a speaker off mid-word.
- **Talking-head speed:** 1.1x default (1.12x–1.15x only if the reference WPM is faster and sounds natural; never stretch voices robotically).

## 4. Screen Inserts (Search, AI Answers, Product Pages)

- **Build UI screens locally from HTML templates (`assets/screens/`)**, never cropped screenshots with logos, prompt boxes, or fake iPhone status bars.
- **Focus screen default:** zoom ~2× onto the spoken phrase centred at **y 960** (survives 1:1 Meta centre crop) with heavy lens blur above and below and real page chrome above (never an empty top half).
- **Product-page scroll:** start below any unconfirmed sale banner, scroll smoothly with ease-in/out to land on Add to Cart at frame centre, and hold ~0.75 s.
- **Keep screen sources in `edit/media/screens/src/`** (never in `/tmp` scratchpads).

## 5. Working Rules & Hooks 2–3

- **User's saved hook 1 is the source of truth.** Never move clips the user placed; back up `.fcproj` to `edit/backup-<date>-<what>/` before scripting.
- **Hooks 2–3 are exact clones of the approved hook 1** with only the opening swapped. Verify body parity with `scripts/audit.py --body-of`.
- **No exports unless explicitly asked.** Verify changes with rendered check frames (`filmcraft-cli --project P render --seconds S --out f.png`) and `scripts/fc_qa.py`.
- **Move previous exports to `deliverables/pre-<what>/`** before re-exporting.
