---
name: labflow
description: >
  Generate Google Flow images and Omni Flash videos with the unofficial `flow`
  CLI (labflow). Use when the user wants a Flow still, Nano Banana Pro image,
  Omni Flash clip, labs.google generation, `flow image` / `flow generate`, or
  to attach ingredient/reference images and download the result. Triggers:
  Google Flow, labflow, Nano Banana Pro, Omni Flash, labs.google, flow image,
  flow generate, generate this in Flow. Use when the user runs /labflow.
  Do not use for prompt-only character/prop/environment sheets
  (those skills) or for writing a video prompt the user will paste elsewhere
  (video-generation).
---

# labflow

Run the unofficial `flow` CLI. Do the generation. Do not stop at a prompt unless they ask for prompt-only.

Image = **Nano Banana Pro** (`GEM_PIX_2`) at **1K**. Never upsample to 2K/4K. Images cost **0** — skip the credit check.
Video = **Omni Flash** (`abra`). Costs credits. Do **not** ask permission to spend. Before every `flow generate`, run `flow credits` and report remaining vs this run's cost. Stop only if remaining is below the cost.

## First check

```bash
command -v flow && flow doctor
```

If `flow` is missing: install from https://github.com/niiithish/labflow (`pip install -e .` in that repo). Session + project live in `FLOW_SESSION_TOKEN` and `FLOW_PROJECT` (`.env` or `~/.config/labflow/.env`). Never print those values.

Session expired → `flow login` (paste `__Secure-next-auth.session-token` from Chromium → Application → Cookies → `labs.google`).

## Route

| They want | Command |
|---|---|
| Still / image / Nano Banana / 1K | `flow image` |
| Clip / Omni Flash / Flow video | `flow generate` |
| Prompt text only | do **not** run this skill |

Look at every local file they name before writing the prompt.

## Image

```bash
flow image "PROMPT" --aspect portrait \
  --ingredient /abs/path/ref-a.png \
  --ingredient /abs/path/ref-b.png \
  -o /abs/path/out.jpg
```

- `--aspect`: `landscape` `portrait` `square` `4:3` `3:4`. Default portrait for UGC/product-in-hand; otherwise match the brief.
- Repeat `--ingredient` for each reference (max 10). Character sheet, product sheet, room plate — each is one file.
- Images are 0 credits. Still wait for the JPEG/PNG and open it.
- 1K sizes: landscape 1376×768, portrait 768×1376, square 1024×1024.

### Prompt (image)

One composed frame. Not a sheet. Not a product grid.

1. Frame: "single portrait / single shot, one frame".
2. Who: short identity lock that matches the character ref (hair, age, wardrobe). Face from the sheet, not a new person.
3. What they hold: exact product lock (shape, colors, label words). "from the product reference".
4. Where: room in one sentence if they asked for a place.
5. Action: which hand, where the object sits, label facing camera.
6. Style: match the refs ("same handmade clay / stop-motion look as both references").
7. Exclusions: only this person, only this object, no extra panels.

Do not describe the character-sheet layout (headless body, panels). The model will copy the sheet.

## Video

Before every video run:

```bash
flow credits
```

Read `credits` (or `subscriptionCredits`). Cost (Pro): 4s=7, 6s=10, 8s=12, 10s=15. `--count` multiplies. Tell the user remaining and this run's cost, then generate. Do not wait for approval. If remaining < cost, stop and say so.

```bash
flow generate "PROMPT" --aspect portrait --duration 4 \
  --ingredient /abs/path/still.jpg \
  -o /abs/path/out.mp4
```

- `--ingredient` = reference images (max 7), not start/end frames.
- Default wait + download. `--no-wait` only if they say submit-only.
- Output is 720p. 1080p/4K are paid upscales — do not request them.

## After a run

Read the result image/video. If identity, product, or hands are wrong: one tighter lock, one new generate. Do not spam retries.

Recaptcha uses `agent-browser` (`IMAGE_GENERATION` / `VIDEO_GENERATION`). Leftover headless Chromium: `agent-browser --session flow-recaptcha close`. Failures: `flow errors` (`~/.config/labflow/errors.jsonl`, tokens redacted).

Unofficial backend. Use their Google account. Respect credits and Google’s terms.
