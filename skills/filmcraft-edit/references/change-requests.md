# Change Requests & Recipes (Saved `.fcproj`)

## Standard Change-Request Procedure

1. **Back up first:** copy every affected hook to `edit/backup-<date>-<what>/`.
2. **Check live state:** run `scripts/fc.py status edit/hook-1.fcproj`. If the app is open with the bridge up, edits go live automatically via `fc.py`; if open without the bridge, ask the user to save, quit, and reopen via `filmcraft-live`.
3. **Never confuse `"update filmcraft"` with `filmcraft-update`:** `"update filmcraft"` means updating the project timeline via `fc.py` / bridge. Never run the `filmcraft-update` binary updater unless explicitly asked to upgrade the app.
4. **Inspect current IDs:** run `filmcraft-cli --compact --project P inspect sequence` (or via `--bridge`). Hooks 2–3 have shifted frames, so look up each hook separately.
5. **Apply minimal changes** via `scripts/fc.py run PROJECT cmds.jsonl`. Never move clips the user placed unless asked.
6. **Verify before replying:**
   - `scripts/audit.py edit/hook-N.fcproj --baseline edit/backup-<latest>/hook-N.fcproj`
   - `scripts/fc_qa.py edit/hook-N.fcproj`
   - `fc_inserts.py check edit/hook-N.fcproj` (if captions + inserts exist)
   - Render check frames at every changed timestamp (`filmcraft-cli --project P render --seconds S --out /tmp/check.png`).
7. **Log decisions** in the video's `AGENTS.md` / `RUN-LOG.md`.

## Common Recipes

### Swap a clip or still in place (same slot)
```bash
scripts/fc.py swap edit/hook-1.fcproj 6a clips/clip-6/clip-6a/final/clip-6a-v3-1080p.mp4
```
- Uses `media.replaceFootage` + `clip.rename` — keeps start, duration, trim, and motion keyframes.
- **Check first:** if two timeline clips share the same project `item`, both will update. Ensure the new clip is at least as long as the slot (or report the shortfall). For stills, scale to match the old still's pixel dimensions (e.g., 1080×1920) before swapping.
- **Never** swap a video clip for a still.

### Remove a silent piece and close the gap
1. Verify the piece is truly silent (check waveform/RMS) and confirm its exact frame range.
2. Delete with `{"id":"timeline.delete","params":{"clips":[ID],"ripple":false}}`. **Avoid `ripple: true`** — single-track ripple desyncs other tracks via CLI.
3. Trim adjacent clips so the cut lands cleanly on a caption start or under an insert.
4. Move every clip with `startFrame >= cut_end` by `-D` ticks (in ascending order) across **all** video and audio tracks.
5. Trim the music clip's out-point by `-D`.

### Extend a talking clip so a word finishes
1. Extend the V1/A1 clip's `out` edge by `+D` frames so the word completes cleanly (no mid-word cutoff).
2. Shift all subsequent clips across all tracks by `+D` as one block.
3. Align the next insert and caption to the next spoken word.

### Re-push stills after a length change
1. Delete existing `motion.scale` keyframes on the still clip.
2. Add two keyframes: first frame at `start_scale`, last frame at `start_scale * (1 + 0.02 * duration_seconds)`. Skip V1 and `cta-` overlays.

### Propagate hook-1 fixes to hooks 2–3
- If hooks 2–3 have NOT been hand-tweaked: re-clone from hook 1 (swapping only the opening) and prove parity with `scripts/audit.py hook-N.fcproj --body-of hook-1.fcproj --offset O --from F`.
- If the user already hand-tweaked hooks 2–3: apply the exact same change by clip ID in each hook rather than overwriting their tweaks.

## Known FilmCraft Traps

- **Headless `file.save` with a new path renames the project** inside the `.fcproj` JSON (`project.name` and `project.root.name`); restore them if cloning via save-as.
- **Caption builds reset hand-moved caption positions:** always re-run any caption layout/seam positioning script after `fc_captions.py build`.
- **Never run `fc_inserts.py snap` on a user-saved edit** — it moves inserts. Use `fc_inserts.py check` only.
- **Push transitions belong on picture clips only**, never on text/caption or emoji clips (they smear). Hide titles as a push starts.
- **Never open a `.fcproj` for writing before reading it** in a Python one-liner (`open(p, 'w')` truncates immediately). Read into memory first, then write atomically.
