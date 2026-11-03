# Inserts

What the viewer sees over her. The reference video (Aleo's) runs still pictures in a box under the speaker's face that change every 1–3 s, and cuts to full screen only for science animation and the product. Copy the client's reference: count its pace and its box size before placing anything.

## Two kinds

| | Box still (V2) | Full-screen clip (V3) |
|---|---|---|
| What | A still image, fitted into a 720×500 box centred at (540, 1490): over the mic and chest, never the face | A 1080p clip, full frame, video only |
| For | Every line's illustration: scenes, diagrams, charts, papers, reviews, the site | CGI science (skin layers, collagen fraying), the product in hand (CTA), a site scroll |
| Made at | Stills cost nothing: approved 360p-only is fine | 1080p finals, only for these (the user runs them) |
| Longest | 4.5 s before the next (`BOX_MAX`), then held to the next insert | 4 s, and never past the end of its media |

## Sources (log every one in `assets/inserts/CREDITS.md`)

- **Scene stills** (`scenes/scene-3NN/`, Flow, `photoreal-video-production`): the story beats. Generate each from scratch: never pass an older scene still as a reference (user rule) — it hands back its framing and degrades. When a line has no fitting picture, write a new still; never reuse one already shown.
- **Pairs** (`assets/inserts/pairs/pair-N.jpg`): `scene-Na | scene-Nb` side by side, made by `build_inserts.py`'s `make_pair` (same height, 12 px white gap; drawings on white are cropped to the drawing first: `DIAGRAM_PAIRS`). They tell the story only: mom | daughter, age 30 | 48, hiding | confident. **Never a product before/after result** (Meta ad policy, and the client's earlier rule) unless the client asks in writing.
- **Research screenshots** (`assets/inserts/web/pubmed-*.png`): the PubMed abstract page in the built-in browser, the claim's sentence highlighted. Client-sent papers are padded white to the box ratio (1.44) and upscaled 2× so text reads.
- **Diagrams**: Wikimedia Commons, CC licence noted, cropped to the drawing (drop any text panels that claim more than the line says).
- **Charts** (`assets/inserts/charts/`): matplotlib, large type, the figure and its source in CREDITS. Load `dataviz` first.
- **Site and reviews** (`assets/screens/`): the client's live product page captured with headless Chromium at mobile 3× (or 2×), cropped to one section; reviews cropped card by card.
- **Site scroll** (`assets/inserts/screenrec/<brand>-site-scroll.mp4`): a 5 s eased scroll down a full-page capture, PIL frames piped to ffmpeg (`h264_vaapi`), placed on V3 like a CGI clip.
- **CGI clips** (`clips/clip-2NN/`): the brief's medical-animation look (Aleo used calvin video-10's), 6 s, a slow camera move; the action starts in the first second (or set the in point: clip-204 plays from 1.2 s).
- **Product in hand**: reuse an approved clip from an earlier video (`make.py reuse`) before generating; its label must be spelled right and sharp.

## Placing them: `build_inserts.py`

Copy `<skill-dir>/templates/build_inserts.py` to `video-N/edit/` and fill in:

- `WORDS`: the master's words.json (`transcribe`). Read it line by line; each anchor is a word (`("mom's", 12)` = the first "mom's" after 12 s) or a source second, in **master** time. They are mapped through each hook's V1 cuts, so the same list works on every hook and after any re-tighten.
- `FULL`: shot → its versioned 1080p final path.
- `HOOKS[n]`: hook n's own lines; `BODY`: the shared rest. One `(anchor, media)` per picture, with the line it covers as a comment; `None` shows her clean from there.

`build_inserts.py N [--replace]` stops on any repeated picture, imports, places box stills on V2 (scale `min(720/w, 500/h)`, position 540,1490) and clips on V3, and prints the plan. Then the clean-up in `edit-pipeline.md` snaps every edge onto a caption start or cut.

## Changing one insert later

`<skill-dir>/scripts/replace_insert.py edit/hook-N.fcproj OLD_NAME_PREFIX NEW_PATH [--full]` swaps one insert for new media in the same slot (box fit for stills, V3 for `--full`). Do it in every hook that shows it, update `build_inserts.py`'s anchor too (or it is out of date for the next rebuild), and log the source.

## Reviewing them

Render a frame of each new insert in place (`filmcraft-cli --project P render --seconds S --out f.png`) and look at phone size: does it read in a 720×500 box? Faint or busy pictures (a wide room, small text) fail; make a closer still or crop.
