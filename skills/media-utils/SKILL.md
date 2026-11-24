---
name: media-utils
description: >
  Local media helper utilities for video production: (1) local background removal (`rembg-cutout` with birefnet-general / isnet-general-use) and color-accurate green-screen keying without color shift, (2) headless browser screen recording (`agent-browser`) for web/Amazon/review scroll shots, and (3) clean localhost side-by-side review boards with optional shot-number overlays. Use when cutting out subjects, recording web pages, or setting up a local visual review page. Not for Flow generation (use flow) or FilmCraft editing (use filmcraft-edit).
compatibility: Requires python3, ffmpeg; optional rembg venv, agent-browser.
metadata:
  author: ai-content-skills
  version: "1.0"
---

# Media Utils (Cutouts, Screen Recording & Review Boards)

Standard local utilities for tasks that frequently break when improvised ad hoc.

## 1. Local Background Removal (`rembg-cutout`)

Never hand-mask or produce rough "photoshopped" cutouts when local `rembg` models are available. Use `rembg-cutout` (installed to `~/.local/bin/rembg-cutout`, or run `<skill-dir>/scripts/rembg_cutout.py` directly):

```bash
# Single image -> transparent PNG (default model: birefnet-general)
rembg-cutout input.png -o cutout.png

# Faster / cleaner edges on hard products or graphics
rembg-cutout input.png -o cutout.png --model isnet-general-use

# Batch directory of images
rembg-cutout ./frames/ -o ./cutouts/ --model birefnet-general

# Composite onto a clean solid background (e.g. pure green or brand hex)
rembg-cutout input.png -o cutout-white.png --bg "#FAF8F5"
```

- **Models directory**: `$REMBG_MODELS_DIR` (defaults to `$HOME/.local/share/rembg/models`, containing `birefnet-general/` and `isnet-general-use/`).
- **Venv**: automatically uses `$HOME/.local/share/rembg-venv/bin/python` if `rembg` is not in the active Python environment, and prints the exact install command if missing.

### Clean Green-Screen Video Cutout (No Color Shift)

When keying an external green-screen video in `ffmpeg`, lock BT.709 color metadata and apply `despill` so skin/clothing tones never shift yellow or washed-out white, and keep scale/anchor fixed across frames:

```bash
ffmpeg -y -i greenscreen.mp4 \
  -vf "format=rgba,chromakey=0x00FF00:0.18:0.08,despill=green:mix=0.5" \
  -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  cutout.mov
```

- Tune `similarity` (`0.12–0.22`) and `blend` (`0.05–0.12`) on a 1-frame PNG test first (`-frames:v 1`) and inspect visually before encoding the full clip.
- If the cutout will sit over another video, lock its exact `(x, y)` anchor and scale so it never jumps left/right between cuts.

## 2. Headless Browser Screen Recording (`agent-browser`)

Use `agent-browser` for clean, reproducible recordings of product pages, Amazon listings, reviews, or search results without desktop UI chrome:

```bash
# Mobile vertical viewport (9:16 social insert)
agent-browser open "https://example.com/product" --viewport 390x844
agent-browser record start /ABS/path/scroll.webm
agent-browser scroll down 600
agent-browser wait 800
agent-browser scroll down 600
agent-browser record stop
agent-browser close
```

Convert to edit-ready 1080×1920 H.264 before importing into FilmCraft:

```bash
ffmpeg -y -i scroll.webm \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an scroll-1080p.mp4
```

## 3. Localhost Side-by-Side Review Board & Shot Overlays

When handing stills, clips, or remake comparisons to the user:

1. **Keep the review folder spotless**: remove rejected/stale takes before sharing so the board only shows active candidates.
2. **Serve via localhost (never broken `file://` video embeds)**:
   ```bash
   python3 -m http.server 8765 --bind 127.0.0.1 --directory /ABS/path/to/review
   ```
   Give the user `http://127.0.0.1:8765/`.
3. **Side-by-side reference vs. ours**: for remakes/rips, render a synchronized HTML page (two `<video controls>` side by side with a shared play/pause/seek button) or a side-by-side MP4:
   ```bash
   ffmpeg -y -i reference.mp4 -i ours.mp4 \
     -filter_complex "[0:v]scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2[l];[1:v]scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2[r];[l][r]hstack=inputs=2[v]" \
     -map "[v]" -map 1:a? -c:v libx264 -crf 20 -pix_fmt yuv420p compare.mp4
   ```
4. **Top-left shot-number overlay (review renders only — never finals)**: burn shot IDs so the user can give instant feedback (`"fix shot 4b"`):
   ```bash
   ffmpeg -y -i clip-4b.mp4 \
     -vf "drawtext=text='4b':x=28:y=28:fontsize=56:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=12" \
     -c:v libx264 -crf 20 -c:a copy review-4b.mp4
   ```
