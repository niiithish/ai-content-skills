---
name: video-breakdown
description: Decode a reference or inspiration video locally into its visual and editing pattern (every cut, shot type, spoken-word alignment, insert cadence, and beat rhythm) and map that pattern onto a new script. Runs locally with ffmpeg, Parakeet word timing, and contact sheets — no cloud video API required. Use when a client sends a reference ad to analyze, remake, or copy, or when asked for a shot-by-shot breakdown, cut list, or rhythm analysis. Not for writing new scripts (use script-generation) or full production planning (use video-plan).
compatibility: Requires python3, ffmpeg, numpy, Pillow, and transcribe CLI (tesseract optional).
metadata:
  author: ai-content-skills
  version: "2.0"
---

# Video Breakdown (Local)

The client's brief is usually the reference's voiceover rewritten for our product. What the plan needs from the reference is its **visual pattern on the words**: on which words it cuts, what kind of picture comes in (and for how long), how often inserts come, and how this changes from hook to CTA.

`<skill-dir>` is the folder holding this file. `breakdown.py` needs only `ffmpeg`, `numpy`, `Pillow` (`tesseract` optional).

## 1. Analyze (~7 s for 1 min, ~30 s for 4 min)

Place the reference in `<project>/reference-video/` (move with `mv`, never copy; `plan.py init` moves loose videos there automatically). Then run:

```bash
python3 "<skill-dir>/scripts/breakdown.py" analyze "/abs/path/reference-video/REF.mp4"
```

Writes `REF.breakdown/` next to the video:
- `words.json`, `transcript.txt`, `transcript.srt`: word-timed transcript via local `transcribe` (reuses `REF.words.json` if present).
- `shots.json`: every shot with start, end, duration, cut type (`hard` or `soft`), **group**, motion (`static` / `moving` / `busy`), spoken words, and cut alignment (`on-word`, `mid-word`, `word-end`, `in-pause`).
- `sheets/clusters_NN.jpg`: one row per visual **group** (repeated camera angles/clips), most frequent first.
- `sheets/shots_NN.jpg`: 12 shots/sheet with start/mid/end frames, header (`#id time length group motion` + flags `JUMP`/`SOFT`), and spoken words.
- `labels.json`: template to fill in next.

## 2. Look and Label (the judgment step)

Inspect **every** sheet in order: cluster sheets first, then shot sheets. Do not delegate sheet reading to a subagent; open single frames only when a cell is unclear. Fill in `labels.json`:

- **`groups`**: assign each group a `type` and short `label` (who/what, framing, camera move). Types: `talking-head`, `two-shot`, `split`, `broll`, `still`, `cgi`, `product`, `text`, `compare`, `story` (cast acting a scene in a story/song ad — counts as spine), `transition` (black frame/flash/whip — not an insert), `other`.
- **`shots`**: `{"12": {"type": "...", "label": "...", "note": "..."}}` for single shots differing from their group. Keys support ranges (`"40-55"`).
- **`drop_cuts`**: shot IDs that are false splits (e.g., one continuous scroll or zoom-out split into pieces) — merged into the previous shot.
- **`sections`**: `[[start_sec, "Hook"], [8.9, "Mechanism"], ...]`. Use the brief's beat names when provided.

Generate the rhythm report and timeline bar:

```bash
python3 "<skill-dir>/scripts/breakdown.py" report "/abs/path/reference-video/REF.breakdown"
```

Inspect `rhythm.md` (runtime share, average length, insert cadence, per-section table, full shot list) and `timeline.png` to verify labels look right.

**Story and song ads (3D, claymation, AI singing):** the cast acting the story is `story` (spine); inserts are mechanism CGI, product, and screens. Check "Words a shot" and per-section average shot length in `rhythm.md`. For sung ads, burned-in captions on the sheets are the true lyrics (or split vocals first with `vocals` from `transcribe`). Merge continuous camera moves/morphs via `drop_cuts`, but keep deliberate flicker montages.

## 3. Map the Pattern onto Our Script

```bash
python3 "<skill-dir>/scripts/breakdown.py" map "/abs/path/REF.breakdown" "/abs/path/brief/script.txt" [--hook 2]
```

- Aligns reference words with our script and writes `pattern-on-script.md` (one row per reference shot with type, reference visual, and **our words**).
- Pass a plain script or lyric sheet (`.txt`, `.md`, `.pdf`), not a two-column brief table. Use `--hook N` to pick a specific hook.
- Once our voiceover exists, rerun with `--vo our.words.json` to produce `pattern-on-vo.md` with real timestamps.
- If the printed match rate is below ~50%, the script was restructured — map beat by beat manually using `sections`.

## 4. Write `BREAKDOWN.md`

Save `REF.breakdown/BREAKDOWN.md` concisely (tables already live in `rhythm.md`):

1. **Specs:** resolution, duration, words & WPM, shot count, average shot, look, audio (VO/music/SFX), captions.
2. **Pattern:** format, beat structure, insert role, and numeric rhythm rules (e.g., "insert block every ~10 s, 1–3 shots of 1–3 s each; cluster on mechanism/product; no inserts on host").
3. **Insert vocabulary:** each insert kind with trigger word and typical length.
4. **Captions:** font, case, color, box, words/page, y-position %, and closest `captions-filmcraft` template.
5. **Cast & setting:** on-camera cast, wardrobe, set, camera angles per speaker.
6. **Unsettled from frames:** music/SFX, fast motion between sampled frames, unclear text.

Hand off `pattern-on-script.md` and `BREAKDOWN.md` to `video-plan`.

## Remake & Comparison Rules

- Copy the **rhythm and shot category** on each phrase, not copyrighted visuals or exact frames.
- Keep word count within ~5% of the reference unless the client's script says otherwise.
- Cite every product claim from the brief/product page; never invent stats.
- Never generate a split screen as one image; plan each half as its own still/clip and composite in FilmCraft.
- **Side-by-side comparison:** when reviewing a remake or rip against the original, serve original vs. ours side-by-side on a local review page (see `media-utils` for the localhost review board + shot-number overlay workflow) so pacing, transitions, and visual arc can be checked frame-for-frame.

## Capability-Aware Multimodal Fast-Path

- **Video/audio-native agents (e.g., Gemini / Antigravity):** Watch the reference `.mp4` directly to verify camera motion (e.g., single continuous zoom-out vs. a cut), transitions, SFX/music cues, and pacing/energy — while still running local `breakdown.py` (`ffmpeg` + `transcribe`) for exact cut timestamps, `shots.json`, and `rhythm.md`.
- **Text/image-only agents (e.g., Claude Code / Codex):** Rely on the local `clusters_NN.jpg` / `shots_NN.jpg` contact sheets + Parakeet transcript. If the user wants a video-model double-check on motion or audio between sampled frames, use [references/gemini-prompt.md](references/gemini-prompt.md) as supplemental notes on top of `rhythm.md` (never as a replacement for `shots.json`).
