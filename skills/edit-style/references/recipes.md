# Recipes: change requests on a saved edit

Every recipe starts the same way:

1. **Back up.** Copy each hook into `edit/backup-<date>-<what>/`.
2. **Check that the user has saved.** The FilmCraft app may hold newer, unsaved work. Ask before scripting if they could be mid-edit.
3. **Find the clip ids.** Run `filmcraft-cli --compact --project P inspect sequence`. It lists `clip`, `startFrame` and `endFrame` for each item on each track. Body clip ids are shared by hooks 2–3 (they are clones), but their frames are shifted, so look each hook up separately.
4. **Make the change** as JSONL commands ending in `{"id":"file.save","params":{}}`:

   ```bash
   filmcraft-cli --compact --project P run cmds.jsonl
   ```

   Check that every result line is `"ok": true`. The `run()` helper in any of the scripts does this.
5. **Verify.**
   - Diff the clip starts and ends against the backup.
   - Run `fc_inserts.py check` and compare it with its result before the change.
   - Render frames at the changed spots and look at them.
6. **Log it** in `RUN-LOG.md`, and add any decision to `AGENTS.md`.
7. **Tell the user** to reload the project in FilmCraft.

The commands used most often:

```json
{"id":"media.replaceFootage","params":{"item":ITEM_ID,"path":"/abs/new.jpg"}}
{"id":"clip.rename","params":{"clip":CLIP_ID,"name":"scene-218-v5.jpg"}}
{"id":"timeline.move","params":{"moves":[{"clip":ID,"track":TRACK_ID,"time":FRAME*10584000000}],"insert":false,"linked":false}}
{"id":"timeline.trim","params":{"clip":ID,"edge":"in|out","mode":"regular","deltaFrames":N}}
{"id":"timeline.delete","params":{"clips":[ID,ID],"ripple":false}}
{"id":"effects.setParam","params":{"clip":ID,"effect":"motion","param":"scale","value":104.0,"keyframe":true,"time":FRAME*10584000000}}
{"id":"effects.deleteKeyframe","params":{"clip":ID,"effect":"motion","param":"scale","mediaTime":TICKS}}
```

To find a project item id (needed for `replaceFootage`), look in the `.fcproj` JSON under `project.items`. Each media item has a `kind` with its path. If you're not sure of a command or its parameters, run `filmcraft-cli commands`, or use `command_list` in the MCP.

## Swap a still for a new still (same slot)

Use `media.replaceFootage` on the still's project item, plus `clip.rename`. The clip keeps its start, length and push keyframes.

- Make the new still the same size as the old one: scale it with ffmpeg lanczos to 1080×1920, or to whatever the old one was.
- If the old item is used by two clips, both change. Check that first.
- Script: `talking-head/scripts/kit/replace_stills.py`. Edit its `STILLS` map first.
- Example: the mosaic 218 v4 → v5 swap in DCT-2190 (item 11, clip 157, all three hooks).

## Swap a still for a clip, or a clip for a clip (same slot)

Use `talking-head/scripts/kit/swap_insert_clips.py hook-N.fcproj --map OLD_NAME=/abs/new.mp4`. It clears the old clip and places the new one with the same start and length, scaled to fill.

- The new clip must be at least as long as the slot, or it ends early (a flash of her face). Check its duration first.
- Never swap a clip for a still.

## Swap a talking clip (new take or a new voice)

1. **Make the media.** Use `talking-head/scripts/dct-2190/make_voice_clip.py VIDEO VOICE OUT v0 frames a0 a1`.
   - It puts the user's ElevenLabs voice under the take, at 1.12x and −16 LUFS.
   - It silences everything outside [a0, a1], so voice-changer artifacts never play.
   - It cuts the result to the slot.
2. **Put it in.** Use `talking-head/scripts/dct-2190/swap_voice_clips.py` as the pattern.
   - Same slot: `replaceFootage`.
   - Different length (clip 15 v4 was 12 frames shorter): trim it, then move everything after it as one block, music included.
3. **Fix what depends on it.**
   - Move the captions onto the new word frames: transcribe the new clip and convert its word times to frames.
   - Rerun `talk_motion.py`, or redo that clip's zoom by hand.
   - A1 clip gain −4.9 dB, as on the other clips.
4. **Check.** Run Parakeet on the new clip against the brief. Listen for bleeps and doubled words.

## Remove a piece and close the gap

Use `talking-head/scripts/dct-2190/cut74.py` as the pattern (any format).

1. Assert the piece is what you think it is: its length, its neighbours, and that it is silent (RMS about −70 dB).
2. Delete it with `ripple: false`.
3. Trim the clips around it so the cut lands on a caption start with an insert over it. The jump is then hidden.
4. Move every clip with `startFrame >= cut end` by −D, in ascending order, on all tracks.
5. Trim the music's out point by −D.

Each hook has its own frame numbers, so look them up per hook.

Don't use a ripple delete. Ripple on one track desyncs the other tracks, and FilmCraft's sync locks behave unpredictably from the CLI.

## Lengthen a talking shot so a word finishes

Use `talking-head/scripts/dct-2190/loom11_fixes.py` step 1 as the pattern.

1. Extend the V1 piece's out point to where the word ends.
2. Move everything after it by +D as one block.
3. Start the next insert and caption on the next word.

## Roll a cut onto its word (voiceover and song edits)

Run `fc_captions.py plan`; it reports cuts off the voice. Then `voiceover/scripts/roll_cuts.py` rolls each one onto its phrase's first word, slipping or slowing a clip that has no media left. Nothing else moves.

## Put captions on the words

1. Transcribe the hook's master or the clip with `transcribe.py --engine parakeet --words`.
2. Convert source seconds to timeline frames: `clip startFrame + round((t − source_in/TPS) × 24)`.
3. Trim the caption's `in` and its neighbour's `out` to that frame. A caption may lead the voice by 0–3 frames.
4. If a picture changes on that word, move its `in` to the same frame.

## Re-push the stills

Use `loom11_fixes.py` step 2.

1. Delete each still's scale keyframes.
2. Set two new keyframes: the first frame at its start scale, and the last frame at start × (1 + 0.02 × seconds).

This skips `cta-` overlays and V1. Rerun it after any still swap that changed a slot's length.

## Clone hooks again after hook 1 changes

1. Rerun `clone_hooks.py 2 3`, or `make_hook.py 2 3` for format A. It backs up hooks 2–3 first.
2. Then rerun `add_music.py`, the title scripts and `talk_motion.py` on hooks 2–3.

If the user already hand-tweaked hooks 2–3, don't re-clone. Apply the same change to each hook by clip id instead.

## Traps

- **The open app wins.** The FilmCraft MCP in non-bridge mode, and the CLI, work on the file on disk.
  - If the user's window has unsaved changes and they save later, your edit is lost.
  - If you save over a file they changed, their edit is lost.
  - Prefer the CLI on a saved file, and tell the user to reload.
  - Never `file.save` from a stale MCP document.
  - A headless `file.save` with a different `path` renames the project inside the file. Reset `project.name` and `project.root.name` afterwards.
- **Hidden jump cuts.** A joined master hides a jump at every join. With per-clip V1 (as in DCT-2190) every join is a real cut. Otherwise compute each join as the join time ÷ speed. After any V1 change, recheck that each one sits under an insert or on a caption start.
- **A caption build resets positions.** Always run `caption_layout.py` (and the title scripts) after `fc_captions.py build`.
- **`fc_inserts.py snap`** moves inserts. Never run it on an edit the user saved. Use `check` only.
- **Push transitions** go on the picture clips, not on caption or emoji clips (they smear). Hide the title as the push starts.
- **Opening a file for writing empties it.** A one-liner like `python3 -c "json.load(open(p)); open(p,'w')…"` that opens the file for writing before reading it empties the file. Read first, then write.
- **Paths.** The scripts find the project with `Path(__file__)`, so run them from the video's `edit/` copy, not from the skill folder.
