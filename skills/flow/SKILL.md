---
name: flow
description: >
  Generate Google Flow images and videos with the local Labflow `flow` CLI. Use for
  Flow, Labflow, Nano Banana Pro, Omni Flash, `flow image`, `flow images`, or
  `flow generate`. Do not use for prompt-only requests targeting other engines.
---

# Flow

Run `flow` and deliver the requested media. Do not stop after writing a prompt unless the user explicitly asks for prompt text only.

## Let the CLI manage itself

Run the requested generation command directly. Labflow owns session validation and repair, recognized Google re-login, credit checks, account selection, project alignment, browser reuse, FIFO queueing, and durable job resume.

- Do not preflight with `flow account ls`, `flow whoami`, `flow credits`, or `flow doctor` unless the user explicitly asks for account diagnostics.
- Do not run `flow account use`, `flow rotate`, `flow sync`, or `flow account refresh` during ordinary generation.
- Never expose or request session tokens, cookies, passwords, recovery data, or vault credentials.
- Treat queue and resume progress as informational; let the command finish.
- On `LOGIN_REQUIRED`, stop and tell the user a Google challenge needs manual completion. For any other failure, report the CLI's error code and hint instead of inventing a workaround or retry loop.

For multi-clip work, run clips sequentially and continue after each successful download. `remainingCredits` is only the submitting account's balance; the next `flow generate` automatically selects another funded saved account. A final `QUOTA` means the CLI checked the usable account pool; a final `RECAPTCHA_FAILED` means it exhausted safe pre-submission verification retries and funded-account rotation. A timeout remains resumable and must not be resubmitted. If accepted media vanishes, the CLI tries the identical payload once on another account. If that also vanishes, `PROMPT_REJECTED` means rewrite or simplify the prompt; do not add another retry loop.

## Commands

```bash
# One image
flow image "PROMPT" --aspect 9:16 --ingredient /ABS/ref.png --name /ABS/scene.jpg

# A folder containing scene1.md, scene2.md, ...
flow images /ABS/scripts --out /ABS/images --aspect portrait --rpm 6

# One video, optionally using existing stills as references
flow generate --prompt-file /ABS/clip.md --aspect portrait --duration 8 \
  --ingredient /ABS/scene1.jpg --ingredient /ABS/scene2.jpg \
  --name /ABS/clip.mp4
```

Use absolute paths for prompt files, ingredients, and outputs. Inspect every referenced still before writing the video prompt. Ingredients are identity/cut references, not start/end frames; tag them in a prompt with `@scene1` or `@image1` when the shot needs an explicit reference.

Prefer one coherent multi-scene generation over one tiny clip per still. Flow generates video at 720p by default or 360p with `--resolution 360p`; do not request 1080p/2K/4K generation or invent endpoints. Image prompts should describe one composed frame, not a reference-sheet layout.

The CLI uses a profile-bound headless Flow browser for verification and closes its owned process after the command. Let the CLI handle it; `flow browser status` and `flow browser close` manage only Labflow-owned sessions.
