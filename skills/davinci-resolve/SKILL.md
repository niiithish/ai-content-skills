---
name: davinci-resolve
description: Edit videos in FREE DaVinci Resolve on Linux through the davinci-resolve MCP. Covers converting MP4 clips to ProRes LT so Resolve can read them, building a timeline from clips and music, trimming and cutting, rendering a ProRes .mov, and turning it into a client-sized H.264 MP4 with ffmpeg. Use when the user asks to put clips or music in Resolve, assemble, cut or trim an edit, or export or render from Resolve. Not for captions (use captions on the finished MP4) or for generating clips (use flow).
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

## Process

1. **Convert** the clips, keeping their names, into a `resolve-prores/` folder next to them. Add `--no-audio` when the clips' own sound isn't wanted (it usually isn't for AI clips under music):

   ```bash
   <skill-dir>/scripts/to-prores.sh --no-audio -o video-N/clips/resolve-prores video-N/clips/all/*.mp4
   ```

   It skips files already converted. Run it in the background for many clips.
2. **Project settings** before the first timeline: `project_settings` `set_setting` with `timelineResolutionWidth` 1080, `timelineResolutionHeight` 1920 for 9:16, and `timelineFrameRate` to match the clips (`ffprobe` them). The frame rate can't change once a timeline exists.
3. **Import**: `media_pool` `import_media` with `params.paths` (absolute paths to the `.mov` files and the music). Then `media_pool` `probe_media_pool` to get each clip's id.
4. **Timeline**:
   - Whole clips in order: `media_pool` `create_timeline_from_clips` with `name` and `clip_ids`.
   - Cuts and trims: `media_pool` `append_to_timeline` with `clip_infos`, one entry per piece: `media_pool_item_id`, `start_frame`/`end_frame` (SOURCE frames inside the clip; a 32 s piece at 24 fps is 0 to 768), `record_frame`, `track_index`, `media_type` (1 video, 2 audio). The same clip can appear several times with different ranges, which is how to cut one clip into pieces.
   - **`record_frame` is relative to the timeline start** (0 = the first frame, even though Resolve shows 01:00:00:00 / frame 86400). Passing 86400 puts the item an hour in.
   - Music: one `append_to_timeline` entry with `media_type` 2 on audio track 1, `record_frame` 0, `end_frame` = timeline length in frames, so the song ends with the picture.
5. **Check** with `timeline` `probe_timeline_structure` (or `get_items`): every item's start, end and track. Report the edit as a short table (clip, in, out, seconds).
6. **Fix** with `timeline` `delete_clips` (`params.clip_ids` = timeline item ids, not `item_ids`), then append again. Destructive calls return a `confirm_token`: call again with the same params plus `confirm_token`. Never pass `ripple: true` without asking.
7. **Save**: `project_manager` `save` after each finished step.
8. **Render** (only when the user says the edit is done):
   - `render` `get_codecs` with `format` `mov` and pick ProRes 422 LT (names vary, so read the list);
   - `render` `set_format_and_codec`, then `set_settings` with `TargetDir` (`video-N/exports/`) and `CustomName`;
   - `render` `add_job`, `start`, and poll `get_job_status` until it finishes.
9. **MP4 for the client**:

   ```bash
   <skill-dir>/scripts/to-mp4.sh video-N/exports/edit.mov video-N/deliverables/<Brand>_<Concept>_<Variant>_9x16.mp4
   ```

   crf 20 by default; 18 is near-lossless, 23 is smaller. Report the final size. Then offer captions if the brief has them.

## Rules

- Never edit or delete the user's original MP4s. Converted files and exports live in their own folders.
- The MCP covers far more (color, Fusion, markers, Fairlight). When an action isn't here, use the tool's own action list or the `knowledge` tool rather than guessing params.
- Ask before deleting the ProRes folders; offer it once the deliverable is approved.
