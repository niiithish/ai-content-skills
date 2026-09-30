# Failure locks: photoreal

Known ways Nano Banana Pro stills and Flow Omni clips go wrong in photoreal ad scenes, with the fix that worked. Check new prompts against this list, and read it with the shared list in `video-production/references/failure-locks.md` (the QA checklist, Flow and batches, edit and delivery). Add a row whenever a fix works that isn't here yet.

## Stills

| Symptom | Cause | Fix |
|---|---|---|
| A computer monitor angled away from the person at the desk ("in IRL don't we have the monitor straight?") | Composition chosen for the camera, not for life | Put real-life placement in the prompt: the monitor faces her squarely, at eye height. Review every still for "would it be like this in a real room?" |
| People looking into the lens | The model's default portrait pose | Name the eyeline in every prompt ("she looks down at her palm, never at the camera"). |
| The couple read as too old for the romantic beat (Mysa video 3; recast as mid-aged) | Age not checked against the scene's premise | Put the age range in the sheet and every still; check casting against what the scene asks before approving sheets. |
| A red glow or stylized "science" look rejected | The model's default for health and anatomy topics | Plain real light. Diagrams follow the brief's inspiration (a clean anatomical diagram), not a glowing render. |
| Product label redrawn wrong | Generated from a description | Make the product sheet from the real product photo with `--ref`; pass it on every still that shows the product and quote the label text. |

## Clips

| Symptom | Cause | Fix |
|---|---|---|
| The softgel vanishes before her lips close; a tiny sip and the water never drops; 2 softgels become 3 | Untimed, loosely counted swallow beat | 6 s, timed steps (see `clip-prompt.md`), "only one softgel" with its look from a softgel reference, "the water level visibly drops by about a third". Count objects and check the water in review. |
| One sheet of paper multiplied into several; a new paper appeared from nowhere | No count or continuity in the prompt | "There is exactly one sheet of paper the whole time; it never multiplies and no other paper appears." Check props for object permanence in review. |
| A happy woman on a "problem" voiceover line (clip 9) | The emotion wasn't written, so the model smiled | Write the feeling the line needs into the action, and check it against the voiceover line in review. |
| Static shots read as boring next to the reference | Locked-off camera on every clip | A very slow, subtle push-in in the prompt, or a locked frame with a slow zoom in post (ffmpeg `zoompan`), which the user accepted. |
| A couple in bed at night always `NOT_FOUND` or `PROMPT_REJECTED`, even for a mild prompt | Google's content filter on night + pyjamas + bed | Evening, knitwear, armchair or sofa, laughing together: romantic, not sexual. |
| A clip took 20+ versions (clip 8: 26) | Rewriting one long prompt over and over | Keep the prompt short, change one thing per version, and after two failed versions rethink the beat (simpler action, different setting) instead of rewording. |
