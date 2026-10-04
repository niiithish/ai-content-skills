# Failure locks: every style

Known ways Flow batches, reviews and hand-offs go wrong, with the fix that worked, for any style. The style skill has its own file for still and clip prompts (`animated-video-production` or `photoreal-video-production`, `references/failure-locks.md`); read both. Add a row whenever a fix works that isn't here yet.

## QA checklist for review sheets


For every tile, check:

1. **Identity:** faces and outfits match the sheets (moustache, eye colour, stripes, badge).
2. **Count:** exactly the number of characters and props the shot needs.
3. **Scale:** relative sizes as in `AGENTS.md`, and the main subject large enough to read.
4. **Light:** matches the location's hero still and the project's agreed look (warm and motivated by default for animation); no unmotivated sunset drift, not grey or flat, not too dark.
5. **Render:** 3D CG like the sheets, not 2D or outlined, not photoreal.
6. **Layout:** no sheet panels, headless bodies or grey backdrop.
7. **Text:** in-world text (papers, signs, labels, packaging) is readable and spelled as the prompt quotes it; no captions, UI or watermarks.
8. **Geometry:** nobody inside a wall, bench or prop, and doors and props look real and sit in the known layout.
9. **Start state:** the still works as the first frame of the clip's action.
10. **Eyelines:** everyone faces and looks where the plan says: at the pie, at each other, at the dog. Nobody poses for the camera unless the plan asks for it.
11. **Real-life logic:** things sit and face the way they would in life (a monitor faces the person using it), and props keep their count and never appear from nowhere or vanish, from the first frame to the last.
12. **Tone:** the face and body match the line spoken over the shot (no smile on a "problem" line).
13. **New picture:** the camera differs from the shot before and from the look still. A still that is the look still again with small changes is a reject.
14. **Clips:** the frame stays put from start to end (or makes its one smooth move in a talking clip), everyone moves, and props don't multiply or vanish. A talking clip says its whole line, each word once, with no gaps.
15. **Finals:** the same content as the draft.

## Flow and batches

| Symptom | Fix |
|---|---|
| `lost by Google · regenerating on another account` | Normal: Google dropped the clip or left it stuck for 5 minutes, and flow is regenerating it once in the same run. Let the batch finish; don't stop or rerun it. |
| `NOT_FOUND` after that regeneration | Put a new `"seed"` on the job and rerun: the batch resumes jobs by prompt, ingredients and seed, so an unchanged rerun won't retry it. |
| `QUEUE_STALLED` after that regeneration | Rerun the batch once later; if it stalls again, put a new `"seed"` on the job. |
| `PROMPT_REJECTED` | Google discarded that exact clip on two accounts. Simplify or rewrite the shot's prompt. |
| `BATCH_WORKER_FAILED` | Rerun the same command. |
| The same shots `PROMPT_REJECTED` or `NOT_FOUND` ("media vanished", "not visible to this account") on every account and seed while the rest succeed (Mysa video 3: 4 of 31) | Google's content filter took the finished clip down, not flow. Stop rerunning (each try spends credits on another account). Soften the still and the prompt: clothed or abstract figures, no bedroom or couple-in-bed staging, no quoted intimate label text (Mysa 8 went through as the couple at the bathroom sink). Tell the user the changes before rerunning as a new version. |
| Manifests, `.flow-batch.json` state and `batch-*.log` files piling up beside the media, one per retry round (video-3: about 80 in `clips/` and `stills/`) | Only `make.py` batches, and it keeps its run files, flow state and logs in `.flow/`. A retry is a new version's job in the one manifest plus `make.py clips 3b 7a`, never a new manifest. `make.py status` lists files outside the layout. |
| A job stuck with no progress; there is no cancel command | Stop and report it to the user (command, last output, what you think is stuck); don't wait it out. See `flow`. |
| A chained clip's opening frame soft or different | Frame taken from the 360p draft, or redrawn with an image model | `make.py lastframe` from the approved clip's 1080p final. |
| A 1080p final differs from the approved draft | Finals are new generations. Review finals against drafts; rename the bad one `rejected-…`, change the seed, rerun that shot. |
| The 1080p upsample fails or costs credits | It is free only on a paid account; flow sends upsample jobs only to paid accounts; if none has credits, finals fail with a hint. A 360p draft cannot be upscaled. |
| A batch interrupted | Rerun the same command; outputs that exist are skipped and accepted jobs resume. |

## Edit and delivery

| Symptom | Fix |
|---|---|
| Full subtitles delivered when the client wanted a few captions | Reread the brief's caption section before any edit deliverable; use the client's exact wording at the moments they name; quote the brief back to the user. |
| Time spent building an edit tool, or cutting the edit, when the user edits | The user stitches and times the edit themselves (our cut got about 90% there, not good enough). Deliver ordered clips; never offer to edit. |
| Captions took seven rounds to land (video-3) | The `captions` skill: its locked style, one preview frame before any render. |
| Clips shorter than their voiceover line, regenerated longer | Time the voiceover with `video-plan` before the shot list; each line's clips cover its slot plus 1 s. Longer is only trimmed. |
| Shots added after the finals (a third of Milo video 1) | Story lock with the approved `PLAN.md`; check voiceover coverage with the animatic before any clips. |
