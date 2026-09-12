---
name: labflow
description: >
  Generate Google Flow images and videos with the local `flow` CLI. Use for
  Flow, labflow, Nano Banana Pro, Omni Flash, `flow image`, `flow images`, or
  `flow generate`. Do not use for prompt-only requests targeting other engines.
---

# labflow

Run `flow` and deliver the requested media. Do not stop after writing a prompt unless the user explicitly asks for prompt text only.

## Let the CLI manage itself

Run the requested generation command directly. Labflow owns session validation and repair, recognized Google re-login, credit checks, account selection, project alignment, and browser reuse.

- Do not preflight with `flow account ls`, `flow whoami`, `flow credits`, or `flow doctor` unless the user explicitly asks for account diagnostics.
- Do not run `flow account use`, `flow rotate`, `flow sync`, or `flow account refresh` during ordinary generation.
- Never expose or request session tokens, cookies, passwords, recovery data, or vault credentials.
- Treat progress and `accountSwitch` output as informational; let the command finish.
- On `BUSY`, wait for the active job and retry the exact command once. On `LOGIN_REQUIRED`, stop and tell the user a Google challenge needs manual completion. For any other failure, report the CLI's error code and hint instead of inventing a workaround or retry loop.

For multi-clip work, run clips sequentially and continue after each successful download. `remainingCredits` is only the submitting account's balance; the next `flow generate` automatically selects another funded saved account. A final `QUOTA` means the CLI checked the usable account pool. If a command emitted a media ID but later timed out, do not submit that clip again: run `flow wait MEDIA_ID`, then `flow download MEDIA_ID`. The CLI remembers or discovers the submitting account.

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

The CLI opens the active account's mapped Chromium profile for verification, reuses it within the command, and closes it when the command exits. Let the CLI handle that window.
