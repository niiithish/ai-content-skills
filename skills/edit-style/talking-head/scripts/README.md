# Edit scripts

Every script edits a `.fcproj` through `filmcraft-cli`, writes a backup next to it, and fails loudly if any command isn't `ok`. They are **templates**:

- Copy them into a video's `edit/` (`upwork-max/tools/new_video.sh` does this) and run them from there. Each script finds the video folder with `Path(__file__)`.
- Set the constants at the top for the new video.
- Each script's docstring says which rule it enforces and how to run it.

## kit/: the video-5 (format A) pipeline, also used on DCT-2190

| Script | Does | Set first |
|---|---|---|
| `write_insert_stills.py` | Writes the insert still prompts and their `stills-batch` jobs from `SHOTS` | `MASTER`, `HER`, `SHOTS` |
| `write_clips.py` | Writes the talking and insert clip prompts and their `clips-batch` jobs | `MASTER`, `TALK`, `INS` |
| `build_draft.py N` | Builds `hook-N.fcproj`: talking clips at 1.1x on V1, full-screen inserts on V2 on their words, stills pushed | `INS`, `L`, `STILLS`, `HOOKS`, anchors |
| `caption_layout.py` | Moves body caption boxes to y 1360 and the title (and its emoji) to `TITLE_Y` | `TITLE_Y`, `CAPTION_Y` |
| `title_emoji.py` | Puts the 🤯 PNG beside the title's last word, with the box widened | `EMOJI`, the title match |
| `title_push.py` | Adds an 8-frame Push out of the opening still and hides the title as the push starts | none |
| `talk_motion.py` | Adds a centred slow push and 100↔110% steps on talking-only stretches. Safe to rerun | `PUNCH`, `PUSH` |
| `add_music.py` | Puts music on A2 at `GAIN_DB` with a 1 s fade, replacing what was there. Safe to rerun | `MUSIC`, `GAIN_DB` |
| `make_hook.py 2 3` | Clones hook-1 into hooks 2–3, swapping the opening (format A) | the hook table |
| `replace_stills.py` | Swaps a still for a still in place, keeping its push | `STILLS` |
| `swap_insert_clips.py --map OLD=NEW` | Swaps an insert for a clip in place, same start and length | `--map` |

## dct-2190/: format B and the latest fixes

| Script | Does |
|---|---|
| `build_talking_head.py` | Takes the talking finals with the ElevenLabs voice, speeds them up 1.12x, cuts the gaps (lead, tail, inner pauses), normalises to −16 LUFS, and builds `talking-head.fcproj` |
| `join_gaps.py` | Measures the voice-to-voice silence at each join (waveform). Imported by `build_hook1.py` |
| `build_hook1.py` | Builds hook-1 from the exported master: V1 cut at every join (`JOINS`), V2 one picture a phrase from `SHOTS` (word anchors), stills pushed |
| `hook_text.py` | Makes the two-line title over the hook photos and turns the next captions into the black card |
| `card_words.py` | Adds each card word on its spoken onset frame, inside the nested `card` sequence |
| `clone_hooks.py 2 3` | Clones hook-1 into hooks 2–3 with format B's opening swapped. The card stays hook 1's take |
| `make_voice_clip.py` | Makes one talking clip with a new ElevenLabs voice: cut to a slot, 1.12x, −16 LUFS, silence outside the line |
| `swap_voice_clips.py` | Puts new talking clips into their slots and moves the captions onto the new words |
| `loom11_fixes.py` | Pattern: lengthen a talking shot so a word finishes, move the block after it, re-push every still at 2 %/s, move captions onto words |
| `cut74.py` | Pattern: remove a silent piece, hide the jump under an insert, close the gap on every track, trim the music |

The `dct-2190/` scripts are the latest and most careful versions. When a kit script and a dct-2190 script do the same job (building hook 1, cloning), start from the dct-2190 one and change its constants.

Shared overlays (🤯, CTA arrows, click) are in `../../assets/`, and the FilmCraft installer is in `../../scripts/setup/`.
