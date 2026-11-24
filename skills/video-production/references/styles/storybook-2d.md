# Style Module: 2D Storybook / ELI5 Slideshow (`--style storybook-2d`)

Hand-inked watercolour, editorial illustration, or "explain like I'm 5" (ELI5) storybook ads built from **still illustrations only** (no AI video clip generation). Motion, Ken Burns pushes, pans, and transitions are added cleanly in **`filmcraft-edit`**.

## 1. Pipeline Differences (Stills-Only)

- **Skip Phase 4 (video clip generation)** unless the user explicitly asks to animate a specific hero beat.
- **Cut rhythm:** Because every frame is an illustration, aim for a fresh illustration every **2.0–3.5 s** aligned to voiceover beats so the slideshow never feels static.
- **Every still moves in post:** Hand off approved 9:16 stills to `filmcraft-edit`, where each still gets subtle continuous motion (slow zoom-in/out or gentle pan) and clean beat-synced cuts.

## 2. Visual Direction (Default ELI5 Watercolour Look)

Match the client's reference illustrations exactly; default when no reference is given:
- **Medium:** Hand-inked storybook illustration with fine warm brown-grey ink linework and soft translucent watercolour washes on warm cream textured paper (`#FAF5EB`–`#F5ECD9`).
- **Consistency Lock:** Keep identical line weight, paper grain, muted warm palette, and character proportions across every illustration. Never drift into glossy 3D CGI, vector flat-design clip art, or photorealism.
- **Composition:** Clear, simple single-idea visual per beat with generous breathing room in the central 70% of the 9:16 frame (safe from social UI and bottom captions).
- **Text & Labels:** Prefer clean, text-free illustrations and add crisp typography in `filmcraft-edit`. Only include simple hand-lettered 1–2 word diagram labels when the ELI5 format specifically calls for them (quote exact spelling and verify every letter in QA).

## 3. Sheets & Prompting

- **Character & Product Style Sheets:** Generate one character illustration sheet (matching the exact ink + watercolour medium) and one illustrated product sheet (from the real product photo `--ref`, translated into hand-inked watercolour while keeping silhouette and brand name recognizable).
- **Negatives in every still prompt:** `"3D render, Pixar, photorealistic, photography, glossy plastic, vector clip art, neon gradients, UI chrome, subtitles, watermarks, misspelled text."`
- **Batching:** Generate all stills at full concurrency (`make.py stills`, `CONCURRENCY=10`), inspect every tile in `make.py review stills` for style/paper-tone drift, fix any outliers from scratch, then hand off directly to `filmcraft-edit` + `captions-filmcraft`.
