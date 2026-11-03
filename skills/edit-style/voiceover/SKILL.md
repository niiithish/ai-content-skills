---
name: voiceover-edit
description: The voiceover and song format of the house edit style in FilmCraft. Generated shots (3D, claymation, photoreal B-roll) or stills under a voiceover or a sung track, one picture per line, often 100–150 shots per hook, as in the Mysa (Calvin) videos 7–18 and the CloudAlign (Alaria) ads. It covers laying shots on V1 from PLAN.md times mapped through the sped-up and tightened voice, cuts rolled onto first words, Flow clips skipping their slow first 0.5 s, start-to-end clips sped to play whole, splits built from two clips, captions on sung words, and hooks 2–3 cloned and retimed to their own voiceover or song take. Use with edit-style (load it first) for any FilmCraft edit of a voiceover, song or slideshow ad.
---

# Voiceover edit

**Load `edit-style` first.** Its principles all apply here. This file adds only what a timeline of many shots under one voice needs. Worked examples:

- `upwork-calvin/video-18`: claymation under a voiceover, 3 hooks. These are the scripts in `scripts/`.
- `upwork-calvin/video-16`: 3D under a sung track.
- `upwork-alaria/video-4`: a watercolour stills slideshow.

## Layout

| Track | Holds |
|---|---|
| V1 | one shot after another, each from its line's first word to the next shot. No gaps. |
| V2 | the second half of a split (or a box over V1). |
| Above | captions, overlays (end card, CTA). |
| A1 | the voiceover or song: sped up 1.1x and tightened before the edit (`filmcraft-pacing` calm). |
| A2 | music, 12–18 dB under the voice, with a fade. |

Clip sound is off: the voice is the only sound from the media.

## Building hook 1 (`scripts/build_hook1.py`)

1. **Time each shot.** PLAN.md times come from the 1.0x read. Divide by the speed, then map through the A1 pieces left after pause cuts. A time that fell inside a cut pause snaps to the next piece.
2. **Pick the media.** Each shot uses its 1080p final, else its newest draft. Skip the first 0.5 s of every Flow clip (user, video-16: the slow start).
3. **Fit each clip to its slot.**
   - A start-to-end-frame clip is sped up to play whole in its slot, so its end state is seen.
   - Any other clip is trimmed to its slot.
   - A clip shorter than its slot is slowed to fit and reported. Never leave a gap.
4. **Check the cuts.** Run `fc_captions.py plan`, then `scripts/roll_cuts.py`, which rolls every cut onto its phrase's first word. A rolling edit moves nothing else.
5. **Captions.** Build them with the client's template, then run `scripts/caption_positions.py` to move any caption off busy picture (rerun it after every build).
   - **Songs:** the music fills the pauses, so the plan finds none and ASR stretches words. `scripts/caption_ends.py` ends each caption on faster-whisper's word end.
6. **Music.** Run `scripts/add_music.py`, measured with ebur128.

## Stills slideshow

For a storybook or ELI5 slideshow (CloudAlign video-4):

- Copy the reference's cut rate. Every still gets the slow push, or a pan where the picture is wide.
- Hard cuts. Captions are small and mid-frame when the reference does that (template 5).
- Pauses halved if the voice drags.

## Splits

- Two separate clips, each with its subject centred and the action inside the middle half of the frame.
- Side by side: each cropped 25% left and right. Top/bottom: each cropped 25% top and bottom (`scripts/split_horizontal.py`).
- A thin seam line between them. Labels are text clips.
- Captions over a split sit on the seam.

## Hooks 2 and 3

- **Voiceover** (`scripts/clone_hooks_voiceover.py`): copy hook 1, then replace its opening shots and voice with hook N's voiceover (tightened the same way) and shots. The body moves to follow. Music is laid again.
- **Song** (`scripts/clone_hooks_song.py`): each hook is its own take and drifts up to 3 s. Every cut maps through the words both takes share (piecewise linear), with the intro anchored by hand. Captions are rebuilt per hook.
- Both keep every tweak, insert, split and punch-in the user made in hook 1.

The scripts are templates. Copy them into the video's `edit/` and set the constants at the top: shot ids, the split pair, speed and fps. Check the project fps: video-18 is 30 fps, Aleo is 24.
