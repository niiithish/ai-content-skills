---
name: labflow
description: >
  Run the unofficial `flow` CLI to generate Google Flow stills (Nano Banana Pro)
  and Omni Flash videos. Use when the user says Flow, labflow, labs.google,
  Omni Flash, Nano Banana, flow image, flow generate, flow images, or wants
  clips from existing scene stills. Use when they run /labflow.
  Do NOT use video-generation (that skill is prompt-only for other engines).
  Do NOT use ugc-ad-remake for silent clay ads.
---

# labflow

Run `flow`. Do the generation. Do not stop at a prompt unless they ask for prompt-only.

| Kind | Model | Credits |
|---|---|---|
| Still | Nano Banana Pro `GEM_PIX_2` 1K | often 0, **not unlimited** (daily quota) |
| Video | Omni Flash `abra` | 4s=7 · 6s=10 · 8s=12 · 10s=15 × `--count` |

Never upsample 2K/4K. Never invent a new endpoint.

## Before anything

```bash
flow doctor
flow whoami
flow credits
```

Never print `FLOW_SESSION_TOKEN`. Wrong account after editing `.env` → `flow sync`. Expired → `flow login` (HttpOnly cookie from Chromium → Application → Cookies → labs.google → `__Secure-next-auth.session-token`).

## Route

| They want | Do |
|---|---|
| One still | `flow image` |
| Folder of `scene1.md`… | `flow images DIR --out DIR --aspect portrait --rpm 6` |
| **Video from existing stills** | `flow generate --prompt-file ABS.md` + `--ingredient` each still |
| Prompt text they will paste elsewhere | **video-generation**, not this skill |
| Talking-head remake of a winning UGC | **ugc-ad-remake**, not this skill |

Look at every still they name before writing the prompt.

## Still → video (this is the usual remake)

Do **one** `flow generate` for the first N scenes that fit in 8s or 10s. Do **not** make one 4s clip per still and stitch.

```bash
flow generate --prompt-file /ABS/path/clip1.md \
  --aspect portrait --duration 8 \
  --ingredient /ABS/path/scene1.jpg \
  --ingredient /ABS/path/scene2.jpg \
  --ingredient /ABS/path/scene3.jpg \
  --name clip1.mp4
```

Hard rules:

- `--prompt-file` and `--ingredient` are **absolute** paths. Never `$(cat clip.md)` from a random cwd.
- `--ingredient` = identity / cut refs (max 7), **not** start/end frames.
- Flags can be in any order. `--name` / `--rename` / `-o` write **in the cwd**. If they want `clips/clip1.mp4`, either `cd` into `clips/` first or pass `--name /ABS/path/clips/clip1.mp4`.
- `flow credits` first. Say remaining vs cost. Do not ask permission. Stop if remaining < cost.
- Freemium uses the same cost table.

## Images

```bash
flow image "PROMPT" --aspect portrait --ingredient ./ref.png --name scene1.jpg
flow images ./scripts --out ./new-images --aspect portrait --rpm 6
```

`flow images` skips complete jpgs (resume). Stops on the first failure (`QUOTA`, recaptcha). Same command resumes. `--force` regenerates.

Prompt a **single composed frame**, not a character-sheet layout.

## Recaptcha / Chromium

API calls are HTTP. Recaptcha needs a **headed** labs.google tab (`agent-browser` session `flow-recaptcha`). It **closes when the command finishes** (success, fail, or Ctrl-C).

- `flow generate` / `flow image`: one window for that job, then close.
- `flow images`: one window for the whole batch, then close.
- Leftover after a crash: `flow recaptcha-close`

Do not mint recaptcha headless. Do not replace this with a raw HTTP recaptcha call.

## When it breaks

`flow errors` first.

| Symptom | Do |
|---|---|
| Empty / garbage prompt, `cat: ... No such file` | Use `--prompt-file /absolute/path`. |
| Clip saved in the wrong folder | `--name clip1.mp4` is cwd. `cd` to `clips/` or use an absolute `--name`. |
| `RECAPTCHA_FAILED` / `UNUSUAL_ACTIVITY` | Retry once. `flow recaptcha-close` then retry. Open labs.google/fx/tools/flow in Chromium once. |
| `QUOTA` / `PER_MODEL_DAILY_QUOTA_REACHED` | **Stop.** Image/video caps are real. Switch account (`flow sync`) or wait. Resume later; do not keep submitting. |
| Wrong Google account | `flow whoami` → `flow sync` or `flow login`. |
| 404 on `flowMedia` after generate accepted | Generate used the **wrong FLOW_PROJECT** (old account’s UUID). Job may still have spent credits. `flow sync` so project follows the session `.env`. New project UUID is in **this** account’s Flow URL. Re-run generate. |
| Chrome left open after generate | Update labflow. Current CLI closes the window when the command exits. `flow recaptcha-close` for leftovers. |
| Leftover Chromiums | `flow recaptcha-close` |

Unofficial backend. Their Google account. Google’s terms.
