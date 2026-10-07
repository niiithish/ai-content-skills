---
name: davinci-resolve
description: Edit videos in FREE DaVinci Resolve on Linux through the davinci-resolve MCP. Covers converting MP4 clips to ProRes LT so Resolve can read them, building a timeline from clips and music, trimming and cutting, rendering a ProRes .mov, and turning it into a client-sized H.264 MP4 with ffmpeg (or straight into the captions render). Builds a whole edit in one command with scripts/build.py. Use when the user asks to put clips or music in Resolve, assemble, cut or trim an edit, or export or render from Resolve. Not for captions (the captions skill renders them from the Resolve .mov) or for generating clips (use flow).
---

# DaVinci Resolve (free, Linux)

The agent drives Resolve through the `davinci-resolve` MCP (samuelgursky/davinci-resolve-mcp). Free Resolve 21.1+ blocks external scripting, so the MCP talks to a Lua bridge running inside Resolve (`bridge/`). The edit is real Resolve: the user can open it and keep working by hand.

## Free-on-Linux limits (why the pipeline looks like this)

- **No H.264/H.265/AAC decode.** An MP4 imports as *Audio only*, with no picture. Convert every clip to ProRes LT first with `scripts/to-prores.sh`. MP3 and WAV import fine as they are.
- **No H.264 encode.** Render ProRes `.mov`, then make the MP4 with `scripts/to-mp4.sh`.
- ProRes LT is about 10 MB/s at 1080×1920 (about 2.5 GB for 4 minutes). It is a working format only. The client gets the MP4 (about 150–250 MB for 4 minutes at crf 20). Never send the ProRes.

## Before anything

1. Check the MCP is there: `project_manager` `get_current`. If the tool doesn't exist, run `scripts/install-bridge.sh` and give the user the register command it prints; the agent must be restarted after that.
2. If a call says the bridge isn't running, ask the user to click **Workspace → Scripts → claude_bridge** in Resolve. It's needed once per Resolve launch. Clicking it twice is harmless: the newest one takes over.

## Process (fast path: one command per stage, no per-step tool calls)

Do the edit with `scripts/build.py`, not step by step through the MCP. One MCP call costs a model turn, and the MCP's append looks each clip up by scanning the media pool one bridge call at a time (about 2,000 round trips for 64 clips). `build.py` imports once, appends every piece in one call, checks placement once, saves, and renders while polling locally. It prints a timing line per phase.

1. **Convert** the clips (parallel, skips ones already done). Add `--no-audio` when the clips' own sound isn't wanted (it usually isn't for AI clips under a voiceover or music):

   ```bash
   <skill-dir>/scripts/to-prores.sh --no-audio -o video-N/clips/resolve-prores video-N/clips/all/*.mp4
   ```

2. **Spec.** For the standard layout (a `PLAN.md` shot table, clips named `clip-N-vK-1080p`), generate it; it takes the newest version of each shot, puts it at its plan time and trims it to its slot:

   ```bash
   <skill-dir>/scripts/plan-spec.py video-N --timeline "Hook 1" --vo video-N/voiceover/recording.wav \
     --music path/to/song.mp3 --render-name video-N-hook-1 > video-N/edit/hook-1.spec.json
   ```

   For anything else, write the JSON by hand (format in the `build.py` docstring: `video` / `audio` pieces with `file`, `at`, `in`, `dur`, `track`; `"dur": "timeline"` makes music end with the picture). Keep specs in `video-N/edit/`, so a fix is an edit to the spec plus a rerun.
3. **Dry run**, then **build**. Read the warnings (a clip shorter than its slot leaves a gap):

   ```bash
   <skill-dir>/scripts/build.py video-N/edit/hook-1.spec.json --dry-run
   <skill-dir>/scripts/build.py video-N/edit/hook-1.spec.json            # build + save, no render
   ```

   Rebuilding an existing timeline needs `--replace` (it deletes that timeline first; ask the user if they may have hand-edited it). The frame rate can't change once the project has a timeline. If the bridge isn't running, ask the user to click claude_bridge (see above).
4. **Show the user** and let them check it in Resolve. Render only when they say the edit is done:

   ```bash
   <skill-dir>/scripts/build.py video-N/edit/hook-1.spec.json --replace --render   # ProRes LT .mov into deliverables/raw/
   ```

   Run it in the background for long edits; it waits for the render and reports progress itself.
5. **One encode to the client file.** Free Resolve on Linux can't write H.264, so exactly one ffmpeg pass follows the render:
   - **Captions wanted** (most briefs): do NOT make a plain MP4 first. Hand the `.mov` straight to the `captions` skill; its render burns the captions and writes the final MP4 in that one pass.
   - **No captions:** `<skill-dir>/scripts/to-mp4.sh video-N/deliverables/raw/<name>.mov video-N/deliverables/<Brand>_<Concept>_<Variant>_9x16.mp4` (crf 20 by default; 18 near-lossless, 23 smaller). Report the size.

Use the MCP tools for inspection and one-off fixes on an existing timeline (`timeline` `get_items`, color, Fusion, markers, Fairlight), not for building.

## Rules

- Never edit or delete the user's original MP4s. Converted files and exports live in their own folders.
- The MCP covers far more (color, Fusion, markers, Fairlight). When an action isn't here, use the tool's own action list or the `knowledge` tool rather than guessing params.
- Ask before deleting the ProRes folders; offer it once the deliverable is approved.
