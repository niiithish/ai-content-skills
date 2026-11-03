# The edit, after the inserts are placed

Every step runs on one `edit/hook-N.fcproj` at a time, through `filmcraft-cli` (live in the app through the bridge when it is open; see `filmcraft`). Each script backs the project up to `edit/backup-<date>-<step>/` the first time that day. `S=<skill-dir>/scripts`, `C=~/.claude/skills/captions-filmcraft/scripts`.

## Order

1. **Captions first pass**: `$C/fc_captions.py words edit/hook-N.fcproj`, then write `captions/hook-N.blocks.txt` by hand from the script's clauses ("So for anything to change," / "that thin skin needs to get firmer first."), at most 10 words, and `plan --max-words 10`. The cut clean-up reads these files.
2. **Cut clean-up** (the talking head):
   - `$S/declutter_cuts.py edit/hook-N.fcproj [--add "end of caption|start of next"] --dry`, read it, then without `--dry`. Pacing cut every pause; this keeps a jump cut only at a new sentence or clause, heals the rest (puts the 0.04–0.38 s pause back, never more than 0.45 s), and no talking shot stays under 1.8 s. `--add` razors a cut the client asked for. It calls `heal_cuts.py --at …`.
   - `$S/heal_cuts.py edit/hook-N.fcproj --pairs "get|firmer,is|thinner"` heals named mid-phrase cuts by hand.
   - `$S/tighten_pauses.py edit/hook-N.fcproj --dry`, then without `--dry`: pauses of 0.35 s or more left after the clean-up are cut to about 0.2 s (0.16 s after the voice, 0.04 s before it), only where a caption starts at a clause and both shots stay 1.8 s or longer (or a V3 clip hides the cut). `--force "WORDS"` cuts the one before the caption starting with WORDS anyway, when the user names a gap. It also keeps a caption up over words spoken after a pause. Every later clip moves left; a clip running through the pause plays on.
   - `$S/split_pause.py edit/hook-N.fcproj FIRST TEXT1 TEXT2`: the longest pause inside the caption starting with FIRST is cut the same way, and that caption is rebuilt as two template 6 captions, TEXT1 up to the cut and TEXT2 from it (Aleo: "And what you got from your mom is" / "thinner skin.").
   - **A one-take hook** (`talking-clip.md`): `$S/one_take_hook.py edit/hook-N.fcproj TAKE-1080p.mp4 TAKE.words.json --body SECONDS` takes out everything before the body (the master second it starts), puts the take in at 0 with `--gap` 0.7 s after its last word (at most to the take's end; 0.37 s was "too tight"), sets the take's audio to the body's loudness, closes the gap and moves the hook's captions and box stills onto the take's words.
   - `$S/punch_cuts.py edit/hook-N.fcproj`: every remaining cut changes zoom, 100% ↔ 108% centred on her face (0.4 H). Clips with keyframed motion stay.
3. **Insert pace**:
   - `$S/thin_inserts.py edit/hook-N.fcproj --dry` when inserts come faster than the reference (it drops the shortest box stills down to one per 3.4 s, keeping her clean ~20%; V3 clips stay).
   - `$S/hold_inserts.py edit/hook-N.fcproj` then holds every insert until the next one starts (client Loom 3). Gaps left are only where a `None` anchor or a V3 clip's media end leaves one; it reports those.
4. **Captions pipeline** (the client's order, after any caption or insert change):
   1. `$C/fc_inserts.py split edit/hook-N.fcproj` (splits a caption where an insert changes mid-caption)
   2. `$C/fc_captions.py plan edit/hook-N.fcproj --max-words 10` and `build -t 6` (or the client's template)
   3. `$C/fc_inserts.py snap edit/hook-N.fcproj` (every insert edge onto a caption start or V1 cut). **Not after a slowed V3 clip** (`fill_held_clips.py` speed below 100%): snap ignores clip speed and cuts those clips short (Aleo: clip-205 lost 32 frames). The check passes without it; fix a single "mid-caption" edge by hand (out-trim one clip, in-trim the next).
   4. `$S/cta_captions.py edit/hook-N.fcproj --clip clip-232` (captions over the product clip go to the top, off the label)
   5. `$C/fc_inserts.py check edit/hook-N.fcproj --render`: must pass (exit 0) before export.
5. **Look** at it in FilmCraft with the user; their tweaks are the base from then on (read `inspect sequence` first).
6. **Preview, then export.** Export the part you changed as a short preview (`fc.py export edit/hook-N.fcproj -o deliverables/preview/HookN_<what>_0-12s.mp4 --start 0 --end 12`, ~17 s) and send it. Export in full only when the user says so: `fc.py export edit/hook-{1,2,3}.fcproj -d deliverables` in the background (~1.3 s per second of video each), named `<Brand>_<Concept>_Hook<N>_9x16.mp4`.

## Traps seen on Aleo

- **Ripple delete refuses** ("V2 is sync-locked and has a clip in the way") when an insert or caption runs over the bit being cut. Trim those clips' out-edge to the cut first, ripple-delete the V1/A1 pieces, then trim them back out by what they lost. `sequence.closeGap {track V1, time}` closes an empty stretch on every sync-locked track at once.
- **Lengthening a V1 clip later** (more tail after a take): `timeline.trim {clip, edge: out, mode: ripple, deltaFrames: N}` on it moves everything after it, on every track, by N frames, its A1 audio with it; then out-trim the caption and box still over it by N (regular). Clip ids are JSON numbers, not strings.
- **A caption's in-edge trim doesn't extend it.** Use `timeline.move` to its new start and an out-edge trim for its length.
- **Clip names are only the first line** of a two-line caption; read the full text from `captions/hook-N.blocks.txt`, and `fcc.STYLES` keys are strings (`"6"`).
- **The app's open copy wins.** A project file the app has open is overwritten when the app saves; when the bridge is down, edit the file and tell the user to close without saving and reopen.

- **A hidden source jump.** A cut in the master can sit one frame before the voice returns (0:59 in hook 1: jump at frame 1436, voice at 1437). An insert that starts on the voice frame shows the jump on her face for one frame. Start the insert and its caption on the jump frame, and razor V1/A1 there so a caption rebuild snaps to it.
- **`fc_captions.py build` replaces the caption track**, so CTA captions go back to the bottom: always rerun `cta_captions.py` after it.
- **After any re-tighten** (pacing again, a heal), rerun `words` — every word moved.
- **Never ffmpeg the edit.** Not to preview, not to join hooks. FilmCraft exports.
- **Keep `build_inserts.py` in step** with hand swaps (`replace_insert.py`), or the next `--replace` rebuild brings old pictures back.
