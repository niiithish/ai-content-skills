# Speaker cutout over inserts (format D, Aleo video-6)

The inspo (Koriderm tier list) keeps the speaker on screen as a green-screen cutout in a bottom corner over every full-screen insert. Max took six Looms (3–8) to get its cuts clean. Every rule here came from one of them.

## Layout

- V1 her full shot, V2 the insert, V3 the cutout (her own green-screen take keyed with Ultra Key), V4 name cards, V5 captions.
- Size and spots measured on the inspo: scale 70 %, right spot (991, 1423), left spot (301, 1423), never mirrored. Grade the cutout to match V1 (Canva/phone takes come out warmer: Lumetri blue +7.5).
- **One side per stretch.** A stretch runs between two full-face shots, cards or boards. Switch sides only there, never per clip ("we keep dancing left and right"), and alternate stretches so it isn't right for minutes on end (Loom 1, "boring"). Move her to the other side only for a whole stretch, when she covers the subject (legs, a mirror reflection, a poured palm). Every tier board has her on the right (left covers the C-row products).
- Hide her on name-card shots (picture + card only), the bottle hero and the CTA.
- Never show the cutout over her own full shot (two of her: Loom 3/4, "beginner mistake"). At a talk-to-insert cut, the transition runs from a copy of her shot on V2 into the insert, and the cutout appears only once the insert is up.

## Clean cuts (Looms 3–8)

Max looks at her face in the corner on every picture change. A cut is clean only when:

1. **It sits in the silence between sentences**, and the cutout and the background change on the same frame.
2. **Her head doesn't jump after the cut.** The green-screen take is cut into pieces by the silence cuts. If a piece's own jump lands 1 frame after the V2 cut, the head visibly jumps late (Loom 6/8 at 0:04 and 0:50). Check with `scripts/video-6/find_late_jumps.py PROJECT`. Fix by starting that piece 1 frame later in the source at (L-1)/L speed (`skip_blinks.py`), so it still ends in sync.
3. **Her eyes are open on the first frame** (`find_blink_cuts.py`, then `skip_blinks.py`).
4. **She stops talking before the picture ends.** Her cutout must not start the next sentence under the old picture (Loom 6/8, "she has already nodded and started the next sentence"). End V3 on her mouth closing.
5. **Every clip starts and ends on a whole frame.** After any `clip.speedDuration`, check `duration % F == 0`. A 0.00001-frame tail showed her cutout on the next picture (2:28:19).

## Never

- **No holds or freezes** of her frames to hide a jump (2–4 frame holds read as freezes: "like 3 fps").
- **No speed-ups** (1.5x pieces) or long speed ramps on pieces: her lips drift and her head twitches. Speed changes stay within (L±1)/L.
- No morph_cut or cross-dissolve across a jump inside one file (double face).

## Source checks before the edit

- **Canva 30 fps exports of 24 fps footage repeat every 5th frame.** Retimed, the repeats stutter. Count repeats (frame diff 0) first; rebuild at 24 fps from the real frames (`dedupe_green.py`).
- Retime the take through the same piece map as the voice (`retime_speed.py`), so the lips stay in sync.

## Before handing back

Render every cutout cut (or the whole V3 track on black) and look at her face crops frame by frame. Then run `~/.claude/skills/edit-style/scripts/audit.py` against the last approved copy.
