---
name: flow
description: >
  Generate Google Flow images and videos with the local Labflow `flow` CLI. Use for
  Flow, Labflow, Nano Banana Pro, Omni Flash, `flow image`, `flow images`,
  `flow generate`, `flow batch`, or `flow upsample`. Do not use for prompt-only requests
  targeting other engines.
---

# Flow

Run `flow` and deliver the requested media. Do not stop after writing a prompt unless the user explicitly asks for prompt text only. When a project skill says the user runs batches (for example `animated-video-production`), write the manifest and give the command instead of running it.

## Let the CLI manage itself

Run the requested generation command directly. Labflow owns:
- session validation and repair, and recognised Google re-login
- credit checks and account selection
- project alignment and browser reuse
- FIFO queueing and durable job resume

What not to do:
- Do not preflight with `flow account ls`, `flow whoami`, `flow credits` or `flow doctor` unless the user explicitly asks for account diagnostics.
- Do not run `flow account use`, `flow rotate`, `flow sync` or `flow account refresh` during ordinary generation. The one exception is a project script that pins the paid account for 1080p finals.
- Do not pass `--no-rotate` unless the user explicitly asks to lock one account. Normal generation leaves rotation on so depleted or unhealthy accounts are replaced automatically.
- Never expose or request session tokens, cookies, passwords, recovery data or vault credentials.

Treat queue and resume progress as informational, and let the command finish. On `LOGIN_REQUIRED`, stop and tell the user a Google challenge needs manual completion. For any other failure, report the CLI's error code and hint instead of inventing a workaround or retry loop.

## Batches

For independent bulk jobs, use `flow batch` with one manifest entry per output. Do not launch many separate CLI processes.
- **Pacing:** the default is three accepted jobs in flight and at most six new submissions per minute, with per-account video-credit accounting.
- **Sequencing:** keep review-dependent or sequential shots in separate batches.
- **Resume:** rerun the same batch after an interruption; completed outputs are skipped and accepted jobs resume. Do not wrap Flow commands in an external retry loop.

What the errors mean:
- A final `QUOTA` means the live account pool lacks enough credits.
- `TIMEOUT` means an accepted job may still be resumable.
- If accepted media vanishes twice, `PROMPT_REJECTED` means rewrite or simplify the prompt.

Seeds:
- A job resumes by its prompt, ingredients and seed. After a lost job (`NOT_FOUND`), or to get a genuinely new take of the same prompt, set a new `"seed"` on it.
- Different seeds on the same prompt are the cheap way to get variants.

```json
{"jobs": [
  {"id": "scene-1a-v1", "kind": "image", "prompt_file": "/ABS/scene-1a-v1.md", "aspect": "9:16",
   "ingredient": ["/ABS/sheet.png"], "output": "/ABS/scene-1a-v1.jpg", "seed": 12345},
  {"id": "clip-1a-v1", "kind": "video", "prompt_file": "/ABS/clip-1a-v1.md", "aspect": "9:16",
   "duration": 4, "resolution": "360p", "timeout": 900,
   "ingredient": ["/ABS/scene-1a-v1.jpg", "/ABS/sheet.png"], "output": "/ABS/clip-1a-v1.mp4"},
  {"id": "clip-1a-v1-final", "kind": "video", "prompt_file": "/ABS/clip-1a-v1.md", "aspect": "9:16",
   "duration": 4, "resolution": "720p", "upsample": "1080p", "no_rotate": true, "timeout": 1500,
   "ingredient": ["/ABS/scene-1a-v1.jpg", "/ABS/sheet.png"], "output": "/ABS/final/clip-1a-v1.mp4"}
]}
```

Paths in a manifest may be absolute or relative to that manifest. An `upsample` job also saves `<name>-1080p.mp4` next to its output.

## Commands

```bash
# One image
flow image --prompt-file /ABS/scene.md --aspect 9:16 --ingredient /ABS/ref.png --name /ABS/scene.jpg

# A folder containing scene1.md, scene2.md, ...
flow images /ABS/scripts --out /ABS/images --aspect portrait --rpm 6

# Independent images/videos with different references and output paths
flow batch /ABS/jobs.json --concurrency 3 --rpm 6 --continue-on-error

# One video, optionally using existing stills as references
flow generate --prompt-file /ABS/clip.md --aspect portrait --duration 8 \
  --ingredient /ABS/scene1.jpg --ingredient /ABS/scene2.jpg \
  --name /ABS/clip.mp4

# 1080p of an existing native 720p clip (Pro, free)
flow upsample MEDIA_ID --name /ABS/clip-1080p.mp4
```

Use absolute paths for prompt files, ingredients and outputs. Inspect every referenced still before writing a video prompt. Ingredients are identity and cut references, not start or end frames. Tag them in a prompt as `@image1`, `@image2`, … in ingredient order when the shot needs an explicit reference. Up to 10 ingredients for an image and 7 for a video.

## Resolution and cost

- Clip lengths are 4, 6, 8 or 10 s.
- **Credits:**

  | Resolution | 4 s | 6 s | 8 s | 10 s |
  |---|---|---|---|---|
  | 360p draft | 4 | 5 | 6 | 7 |
  | 720p | 7 | 10 | 12 | 15 |

  Nano Banana Pro stills cost nothing (there is a daily cap per account).
- 1080p is a download upscale of a **native 720p** generation, free only on a paid account. A 360p draft cannot be upscaled, so a final reruns the same prompt at 720p with `--upsample 1080p`. That is a new generation and can differ from the draft; check it.
- Never request 1080p, 2K or 4K generation, and never invent endpoints.
- For story work, a single coherent multi-beat generation can replace several tiny clips. Project skills that lock one shot per clip (such as `animated-video-production`) take precedence.

## Prompt hygiene

- Never write "TikTok" or name any social app, phone interface or on-screen UI in a prompt: the model draws the app's buttons into the frame. Say "vertical short film" instead.
- Image prompts describe one composed frame, not a reference-sheet layout.

The CLI mints verification in a headed Chromium parked off the active screen, reuses it for nearby commands, and closes it automatically after a short idle period. Do not manage that browser between generations. `flow browser status` and `flow browser close` are only for diagnostics or explicit cleanup.
