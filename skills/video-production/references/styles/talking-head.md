# Style Module: Talking Head (`--style talking-head`)

One speaker (doctor, expert, creator, or host) carries the script to camera with B-roll / still inserts over them — plus two-person podcast formats, standalone single-line UGC clips, and still-first UGC ad remakes.

**Editing separation:** This module covers **generation & voice assembly only**. All timeline assembly, pacing, jump-cut punch-ins, insert timing, green-screen/cutout overlays, and exports belong to **`filmcraft-edit`** and **`captions-filmcraft`**.

## 1. Modes

| Mode | When to use | Workflow |
|---|---|---|
| **A. Long-form Expert / Creator + Inserts** | 45 s–3 min ad with one speaker (or 2-person podcast) + B-roll/still inserts | Master still → talking clips (direct 1080p) → ElevenLabs voice change → `build_talking_head.py` + `speed_up.sh` → `filmcraft-edit` |
| **B. Simple Single-Line UGC** | Quick raw-iPhone 9:16 clip of one person saying one line, no product in hand | Use the locked Simple UGC prompt below (selfie or tripod) |
| **C. Still-First UGC Ad Remake** | Cloning a winning TikTok/Reels talking-head ad with a new talent & product | Still-first product swap (pose/hand contact points from reference + our product sheet) → locked-frame Omni clip |

## 2. Mode A: Master Still & Talking Clips

### Master Still (`scenes/scene-1/scene-1-vN.jpg`)
Every talking clip is generated from this one still (use `photoreal.md` + `Seedream 5.5 1K` if configured in `PROJECT_STATE.json`):
- **Ingredients:** `@image1` = speaker identity ref (face/hair/skin only); `@image2` = reference video frame (framing, camera distance, set, light, mic layout — negate reference person & captions).
- **Pin canvas numbers:** top of head ~14% down, eyes ~33% down (top 40% so bottom insert boxes never cover the face), mic/pop filter in bottom ~30%.
- **No readable badges/text** on coat or background (drifts across clips). Hands out of frame in still; clips bring them in. Mouth slightly open mid-word, looking into lens.

### Talking Clip Rules
- **One whole sentence per clip** (never split mid-sentence). Pick shortest Flow length (6, 8, or 10 s) covering ~3.2 words/sec + 0.5–2 s buffer. Avoid 4 s clips (rushed).
- **One take per hook:** Generate a 2-line hook as one 8 s clip rather than two clips joined at a jump cut.
- **Always use `@image1` as a reference image, NOT frame 0:** Write `"It is not the first frame: she is already in the middle of talking, moving naturally"` so cuts don't reset to the same frozen pose.
- **Exact-word lock:** Quote the line once in `Dialogue:`; add `"Every word is said exactly once, in order, with no repeats or restarts; nothing between '<wordA>' and '<wordB>'."`
- **Natural hands:** Hands rise naturally into frame beside the mic in relaxed explaining gestures, never touching the mic or pop filter.
- **Locked camera & identical voice description** across every clip. Never name camera gear ("tripod") in the clip prompt if it leaks into frame — say `"Camera: static, exact crop and angle of @image1; no cameras or tripods visible."`
- **Audio QA (mandatory before user review):** Run `transcribe` on every talking clip and diff against the script. Flag any repeated word, dropped word, cutoff, or accent drift.

### Voice Unification & Master Assembly
AI talking clips drift in voice timbre clip-to-clip. Unify them before handing off to `filmcraft-edit`:
1. Export normalized per-clip MP3s + joined track:
   ```bash
   python3 <skill-dir>/scripts/voice_change.py export video-N
   ```
   (Supports `--speakers host=1,3 guest=2,4` for 2-person podcasts.)
2. User runs `audio/original/` through ElevenLabs Voice Changer / Voice Isolator (`elevenlabs-creative`) and drops matching filenames into `audio/voice-changed/`.
3. Apply voice-changed audio back under each clip (`-vc.mp4`):
   ```bash
   python3 <skill-dir>/scripts/voice_change.py apply video-N
   ```
4. Assemble untrimmed master timeline (`build_talking_head.py`), export master MP4, and apply 1.1x speed-up if desired (`scripts/speed_up.sh`, VA-API GPU encode). Or mux a single isolated voice track with `scripts/mux_voice.sh`.
5. Insert shots (numbered `201+` so they never clash with talking clips) are generated via `photoreal.md` or `medical-cgi.md`, then placed in **`filmcraft-edit`**.

## 3. Mode B: Simple Single-Line UGC Prompt (No Product in Hand)

Swap only `[she/he]`, `"[line]"`, and optional identity line. Keep every lock:

```text
[optional: the woman/man from @image1]
[Holding the phone selfie view | Static framing], natural and realistic arm movements, subtle lean forward, looks directly at the lens the whole time.

[she/he] says in an american 20 year old ugc tone:
"[line]"

Ambient Sound. No cuts. No zooms. No transitions. Raw iPhone footage, expressive ugc movements, UGC aesthetic. Vertical 9:16. NO PRODUCT IN HAND. ONE CONTINUOUS SHOT.
```

## 4. Mode C: Still-First UGC Ad Remake (Product Swap)

1. **Split references cleanly:** Winning-ad screenshot = pose, expression, **hand contact points**, crop, lighting, room; our product sheet = silhouette, color, material, logo text, open/closed state. Never let the old product or grey sheet backdrop leak.
2. **Clip locks:** 4 s or 6 s, fast yappy delivery, line said once then mouth closed until clip ends. Hands stay on the still's contact points; at most one simple move (zip/press/point). If zip + talk + turn fails, split into two shots.
