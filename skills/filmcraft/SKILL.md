---
name: filmcraft
description: "Edit and export videos in FilmCraft (the open-source Premiere-style editor, `filmcraft-cli`) together with the user: build a ready-to-export timeline from approved clips, let the user tweak it by hand in the open app, apply their change requests live through the bridge (the same project, no stale copies), swap a regenerated clip in without a Link Media popup, and export Meta-ready H.264 deliverables (about 45 MB a minute at 1080x1920, AAC audio) from FilmCraft itself, one hook after another in the background. Use when the user edits in FilmCraft or names a .fcproj: set up or rebuild a timeline, change an edit, replace or relink a clip, fix missing media, or export one or several hooks. Not for captions (captions-filmcraft adds them as text clips), pacing, dead air or zooms (filmcraft-pacing) or generating clips (flow, video-production)."
---

# FilmCraft

The user edits in FilmCraft and so does the agent: one project file, open in the user's app. Tool: `scripts/fc.py` (needs `filmcraft-cli` on PATH and ffprobe for the export check).

## The workflow

1. **Build.** From approved clips (`video-production`), build one project per hook, `video-N/edit/hook-1.fcproj` and so on. Make it ready to export, then stop. **Never export until the user says so.**
2. **The user tweaks it** in FilmCraft (gaps, trims) and saves.
3. **Change requests.** The user asks for changes with the project still open. Edit it live (see "Editing").
4. **Regenerated clip.** When a shot is redone in Flow, swap the new version in (see "Swapping a clip").
5. **Pacing and captions** when asked: `filmcraft-pacing` (dead air out, punch-ins, B-roll motion), then `captions-filmcraft`.
6. **Export** when the user says it's ready (see "Export").

## Setup (once per machine)

`fc.py status` must show `bridge 127.0.0.1:9876: up` while FilmCraft is open. If it's down, or the `filmcraft` MCP isn't in bridge mode, run `scripts/setup.sh`. It does two things:
- It makes the launcher start FilmCraft with `--control 9876`.
- It switches the MCP to `filmcraft-cli mcp --bridge 127.0.0.1:9876`.

Then the user restarts Claude Code and reopens FilmCraft from the launcher.

**Why.** The old headless MCP kept its own copy of the project in memory. When it saved, that copy overwrote the user's saved edits. This was reproduced on 2026-10-18. Bridge mode sends every command to the user's open app instead, so both sides see each other's changes, saved or not.

## Editing

- Use `fc.py run PROJECT cmds.jsonl` (one `{"id","params"}` per line), or the MCP tools when the bridge is up. `fc.py` picks the target itself:
  - When the app has PROJECT open, it edits **live** in the app and then saves.
  - When FilmCraft is closed, or has another project open, it edits the **file**.
  - When FilmCraft is open **without** the bridge, it refuses. Ask the user to save and quit, then reopen FilmCraft from the launcher.
- Look up command ids and params with `filmcraft-cli commands <filter>` and `describe <id>`. Timeline clips use `clip` ids from `inspect sequence`. Project items use `item` ids from `inspect project`.
- **Never save from a headless engine** (`filmcraft-cli --project X --save`, the old MCP's `file.save`) while the app has X open.
- After the user's own tweaks, read `inspect sequence` before changing anything. Their edit is the base now.
- From another skill's script: `fc.save_live(PROJECT)` saves the user's open copy before reading the file (True when the app has it open), and `fc.reload_live(PROJECT)` makes the app reload it after the script rewrote the file.
- Build scripts in `video-N/edit/` assemble the timeline through `fc.py run`, or through `filmcraft-cli --project … --save` while the app is closed.

## Clip paths: no Link Media popups

- Put clips on the timeline from their versioned final files: `clips/clip-N/clip-Nx/final/clip-Nx-vK-1080p.mp4`. **Never use `clips/all/`.** `make.py sync` keeps only the newest version there, so the old file a timeline uses disappears, and FilmCraft shows Link Media on open.
- Missing media already: run `fc.py relink PROJECT`. It searches `video-N/clips/` recursively and matches by name, so the version the timeline was cut with stays.

## Swapping a clip

```bash
<skill-dir>/scripts/fc.py swap video-N/edit/hook-1.fcproj 6a video-N/clips/clip-6/clip-6a/final/clip-6a-v3-1080p.mp4
```

It replaces the project item's media (`media.replaceFootage`) and renames it to the new file. Every use on the timeline keeps its start, length and trim. It runs live when the app has the project open. When the new clip is shorter than its slot, say so: the slot holds as many frames as the clip has.

## Export

```bash
<skill-dir>/scripts/fc.py export video-N/edit/hook-1.fcproj -o video-N/deliverables/<Brand>_<Concept>_<Variant>_9x16.mp4
<skill-dir>/scripts/fc.py export video-N/edit/hook-{1,2,3}.fcproj -d video-N/deliverables    # several, one after another
```

- **Settings:** H.264 High at 6 Mb/s VBR 1-pass (peaks at 9 Mb/s), AAC 192k, GPU rendering on, at the sequence's own size and frame rate. That's about 45 MB a minute, so 2 minutes come to about 90 MB. Use `--kbps 4000` for smaller files (about 32 MB a minute). Meta re-encodes every upload, so more bitrate buys nothing on the phone.
- **It exports the saved file.** If the user's open copy has unsaved changes, it saves them first and says so.
- **Run it with `run_in_background`** so the user can keep editing. It exports one file at a time at low priority. Export rendering uses every core, so parallel exports only slow each other down.
- **Speed:** about 1.3 s per second of video on the Iris Xe laptop (a 2 min hook takes about 2.6 min). Say so up front for several hooks.
- **The check:** it prints size, length, frame size and codecs, and fails unless the file is H.264 + AAC. Report the size.
- **Captions:**
  - Captions made with `captions-filmcraft` are text clips, so they're already in the picture.
  - A caption *track* is burned in automatically. FilmCraft's own default leaves it out, so `fc.py` turns it on whenever the project has one. Pass `--no-captions` for a clean version.
  - Check a frame either way: `filmcraft-cli --project P render --seconds S --out f.png`.

**What made exports slow and big before:** 40 Mb/s VBR 2-pass with max render quality and max depth. Measured on 10 s: 31 s and 50 MB, against 13 s and 7.6 MB with the settings above.

## Rules

- FilmCraft only: never render, re-encode or join a FilmCraft edit with ffmpeg, and never suggest it.
- Never export, delete clips from a project, or rebuild a project the user has tweaked without being asked. Rebuilding overwrites their tweaks, so ask first and keep a backup copy in `edit/backup-<date>/`.
- Ask before rendering anything the user didn't ask for, test exports included. Use short ranges (`--start/--end`) for tests.

## Known limits (FilmCraft 0.9.0, checked 2026-10-18)

- **Hardware encoding on Intel isn't in a release yet.** On Linux, `hardwareEncoding: auto` only reaches NVIDIA. PR #1256 (VA-API) is open, and testers on Iris Xe measured it about 25% faster. On this laptop, encoding is only about 12% of export time, so don't build it.
- **What would make exports really faster** is the export renderer itself: open PRs #2233, #2193, #1284, #2025. Check `gh release list -R storytold/filmcraft` when the user asks about speed.
- **The bridge can stall** for a few seconds while the app loads a project. `fc.py` waits and then stops rather than falling back to the file. Once, after an export started *inside* the app over the bridge, the app stopped answering the bridge. That's why `fc.py` exports from the CLI.
