---
name: flow
description: Generate Google Flow images and videos with the local Labflow `flow` CLI (direct 1080p video default, Nano Banana 2.1 stills, parallel `flow batch`). Use for Flow, Labflow, Nano Banana Pro, Nano Banana 2.1, Omni Flash, `flow image`, `flow images`, `flow generate`, `flow batch`, or `flow upsample`. Not for ElevenLabs Seedream/Seedance/Kling/MiniMax jobs (use elevenlabs-creative) or prompt-only requests for other engines.
compatibility: Requires flow (labflow) CLI configured in ~/.config/labflow/.
metadata:
  author: ai-content-skills
  version: "2.0"
---

# Flow (Labflow CLI)

Google Flow is our **primary generation engine** for stills and video clips (Google's upcoming Flow image model is also expected to supersede ElevenLabs Seedream 5.5 for realistic human character sheets). Run `flow` and deliver media; do not stop at prompt text unless asked.

## Hard Production Defaults

1. **Direct 1080p by default** for video clips: generate native `720p` with `"upsample": "1080p"` (or `--upsample 1080p`). Only use `360p` drafts when the user explicitly opts in (`--draft` or draft-first request). **Never claim a 360p file was upscaled to 1080p** — 360p drafts cannot be upscaled; a 1080p final is always a fresh native 720p generation + download upscale.
2. **Batch concurrency 10–12**: use `flow batch` with `--concurrency 10` (or `12`) for reliable parallel throughput across the browser pool (`FLOW_BROWSER_POOL`). Never fire clips one-by-one in sequential shell calls, and never split one batch into multiple concurrent `flow batch` processes.
3. **Reference-Image vs. Start-Frame rule**:
   - `--ingredient` / `"ingredient"` = identity, wardrobe, prop, or cut references (up to 10 for images, 7 for videos; tag as `@image1`, `@image2` in prompts). They are **not** frame 0.
   - `--start-frame` (and optional `--end-frame`) = exact frame-0 / final-frame lock. **Never pass an end-state still** (e.g., capsules already poured, character mid-jump) as `--start-frame` when the action hasn't happened yet.
   - Never mix `--start-frame` and `--ingredient` in the same video job; `--end-frame` requires `--start-frame`.
4. **From-Scratch Regeneration rule**: When fixing a flawed image or clip (photoshopped product, warped anatomy, wrong gaze, AI sheen, wrong pill count), regenerate **from scratch** using the clean original character/product sheets, a simplified prompt, and a **new `"seed"`**. **Never** feed the broken output back as an ingredient/remix.

## Commands

```bash
# Single image (default: Nano Banana 2.1; pass --model nano-banana-pro only if asked)
flow image --prompt-file /ABS/scene.md --aspect 9:16 --ingredient /ABS/ref.png --name /ABS/scene.jpg

# Folder of prompt .md files
flow images /ABS/scripts --out /ABS/images --aspect portrait

# Bulk batch (preferred for 2+ jobs)
flow batch /ABS/jobs.json --concurrency 12 --continue-on-error
# Single named account ONLY when user explicitly asks:
flow batch /ABS/jobs.json --concurrency 12 --account acc8

# Single video with identity ingredients (direct 1080p)
flow generate --prompt-file /ABS/clip.md --aspect portrait --duration 6 \
  --resolution 720p --upsample 1080p \
  --ingredient /ABS/scene1.jpg --ingredient /ABS/sheet.png --name /ABS/clip.mp4

# Single video locked to exact start (and optional end) frame
flow generate --prompt-file /ABS/clip.md --aspect portrait --duration 6 \
  --resolution 720p --upsample 1080p \
  --start-frame /ABS/first.jpg --end-frame /ABS/last.jpg --name /ABS/clip.mp4

# Upscale an existing native 720p clip to 1080p (Pro, free)
flow upsample MEDIA_ID --name /ABS/clip-1080p.mp4
```

### Manifest Format (`jobs.json`)

```json
{"jobs": [
  {"id": "scene-1a-v1", "kind": "image", "prompt_file": "/ABS/scene-1a-v1.md", "aspect": "9:16",
   "ingredient": ["/ABS/sheet.png"], "output": "/ABS/scene-1a-v1.jpg", "seed": 12345},
  {"id": "clip-1a-v1", "kind": "video", "prompt_file": "/ABS/clip-1a-v1.md", "aspect": "9:16",
   "duration": 6, "resolution": "720p", "upsample": "1080p", "timeout": 1500,
   "ingredient": ["/ABS/scene-1a-v1.jpg", "/ABS/sheet.png"], "output": "/ABS/clip-1a-v1.mp4"}
]}
```

Use absolute paths. Write each scene into its own folder (`-o scene-3/scene-3-v1.jpg`) so status output stays grouped. An `upsample` job saves `<name>-1080p.mp4` next to its output.

## Let Labflow Manage Accounts & Waiting

- Run `flow` (or `make.py`) directly as a background task and wait for its completion notification.
- Never poll with `pgrep -f` / `pkill -f` (matches the shell itself). Always use PIDs (`kill <PID>`). Never run `flow stop` unless the user asks to halt all Flow jobs globally.
- Check local progress without spending credits via `flow summary`.
- Do **not** preflight with `flow account ls`, `flow whoami`, `flow credits`, or `flow doctor` unless asked. Do not run `flow account use`, `flow rotate`, `flow sync`, `flow logout`, `flow account clear`, or `flow account rm`. Leave rotation enabled (`--no-rotate` only if explicitly requested). Never expose tokens/cookies/credentials.

## Chrome-Loop, Quota & Error Recovery

- **Chrome launch/close loop or >10 min stall**: Stop immediately — never kill and relaunch in a loop. Run `flow summary` and `flow browser status`, then report to the user in a few lines: exact command, last output lines, error code, and offending account (e.g., stuck profile lock, expired login, age check).
- **`LOGIN_REQUIRED` (`details.signInFailed`) / Age Check**: Account has credits but needs manual browser sign-in. Tell the user to run `flow account open accX`; do not call it "out of credits" and do not retry in a loop.
- **`QUOTA` with `details.signedOut`**: Run `flow account refresh --only accX` once and rerun; if still failing, ask user to run `flow account open accX`.
- **`QUOTA` (`details.allOut` / `"outOfCredits": true`)**: Stop and tell the user all accounts are depleted; ask them to run `flow account refresh` or top up before rerunning.
- **`PROJECT_MISSING`**: Tell the user to open a Flow project in that account and run `flow account add NAME --project UUID --force`.
- **`NOT_FOUND` (lost after auto-regen)**: Assign a new `"seed"` and rerun.
- **`BATCH_WORKER_FAILED` / `NETWORK`**: Rerun the same command once (accepted jobs resume without re-charging). Stop if it fails twice.
- **`UNSAFE_GENERATION`**: Never resend unchanged. Check the reason:
  - `IP_INPUT_IMAGE` / `IP_PROHIBITED`: remove copyrighted/branded elements from the reference still.
  - `IDENTIFIABLE_PERSON_SAFETY` / `MINOR` / `CHILD_SAFETY`: make subjects clearly non-celebrity adults.
  - `AUDIO_FILTERED` / `DANGER_FILTER`: simplify dialogue or tone down action.
  - If Flow repeatedly blocks a legitimate scene (bed/intimacy, skin/cellulite, children-adjacent) or blurs product text, switch that shot to **`elevenlabs-creative`** (Seedance 2.0 Mini / Kling 4.0 / MiniMax H3 Max).

## Models, Credits & Hygiene

- **Video models**: Default **Omni Flash 1.1** (4, 6, 8, 10 s; 720p = 7 / 10 / 12 / 15 credits; opt-in 360p = 4 / 5 / 6 / 7). **Omni Flash 1.2** (`--model omni-1.2`, 3–15 s, 3 cr/s up to 10 s, 6 cr/s above) is auto-selected only for lengths 1.1 lacks.
- **Image models**: Default **Nano Banana 2.1** (`BELUGA`, 0 credits up to daily cap); `--model nano-banana-pro` only if requested.
- **Cut & artifact check**: Flow sometimes inserts an unwanted mid-clip cut after ~2 s or warps limbs late in the clip. Inspect every generated clip before handoff; trim before the cut or regenerate from scratch.
- **Prompt hygiene**: Never write "TikTok", social app names, or phone UI in prompts (use "vertical short film"). Image prompts describe one composed frame, not a multi-panel sheet unless explicitly making a character sheet.
