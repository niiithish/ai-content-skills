# Failure locks

Known ways Nano Banana Pro stills and Flow Omni clips go wrong, with the fix that worked. Check new prompts against this list, and use it as the QA checklist when reading review sheets. Add a row whenever a fix works that isn't here yet.

## QA checklist for review sheets

For every tile, check:

1. **Identity:** faces and outfits match the sheets (moustache, eye colour, stripes, badge).
2. **Count:** exactly the number of characters and props the shot needs.
3. **Scale:** relative sizes as in `AGENTS.md`, and the main subject large enough to read.
4. **Light:** matches the location's hero still. No golden or sunset drift, and not too dark.
5. **Render:** 3D CG like the sheets, not 2D or outlined, not photoreal.
6. **Layout:** no sheet panels, headless bodies or grey backdrop.
7. **Text:** in-world text (papers, signs, labels, packaging) is readable and spelled as the prompt quotes it; no captions, UI or watermarks.
8. **Geometry:** nobody inside a wall, bench or prop, and doors and props look real and sit in the known layout.
9. **Start state:** the still works as the first frame of the clip's action.
10. **Eyelines:** everyone faces and looks where the plan says: at the pie, at each other, at the dog. Nobody poses for the camera unless the plan asks for it.
11. **New picture:** the camera differs from the shot before and from the look still. A still that is the look still again with small changes is a reject.
12. **Clips:** the frame stays put from start to end, everyone moves, and props don't multiply or vanish.
13. **Finals:** the same content as the draft.

## Stills

| Symptom | Cause | Fix |
|---|---|---|
| The app's buttons or captions drawn into the frame | A social app or phone named in the prompt | Never name the app. Say "vertical short film", with action in the central 70% of the frame. |
| 2D, outlined or flat cartoon look | Only a style word, no visual anchor | Pass an approved 3D still as the look still, and write "fully 3D rendered… not 2D, no outlines". |
| Blank labels and papers, or garbled lettering | No text quoted, or too much of it | Quote a short exact text for each surface (a headline, a brand name, 2–4 words); invent fictional brands; leave fine print soft. |
| Golden-hour or sunset light | The model's default for "warm" or "afternoon" | Name the real source and brightness; add "not golden, not sunset" to the lighting line and the negatives. |
| Each shot in the same room lit differently (7B took eight tries) | No locked look for the location | A hero still per environment, passed first in every still there. |
| The look still comes back with small changes (pie heist 2b, 3a: the same garden view and poses as scene 1) | The look still passed with "match this" and the same characters in the same spot | Its `use_for` says light, colour and render only, and describes the new camera. If it still copies, pass the environment sheet instead of the look still for that shot and describe the light in words. |
| Characters face the camera while the thing they want is behind them (pie heist 1: raccoons "planning" with their backs to the pie) | Facing never stated; the sheets show them facing camera | State each character's facing in the frame and what they look at. When the target is deeper in the picture, shoot over their shoulders: backs or three-quarter backs to camera. Negatives: "looking at the camera, posing for the camera". |
| Too dark, or a heavy blue tint | "Abandoned" or "moody" read as night | State the brightness ("fairly bright daylight, walls clearly visible"); negatives "dark scene, night, deep blue tint". |
| Two or four kittens instead of three | Count stated once | "EXACTLY THREE… all three clearly visible side by side", identity line per group, wrong counts in the negatives. Re-check finals too. |
| The subject too small to read | No frame share given | "Large in the frame, fills the lower-left third"; viewpoint close and low. |
| A three-panel sheet or headless body in the scene | Sheet passed without instructions | The atlas sentence from `scene-still.md`, plus the "three-panel sheet layout" and "headless body" negatives. |
| A character clips through a bench or wall | Contact not described | Say what they stand or sit on and where ("sits on the seat boards beside the box, paws on the wood"). |
| A character holding a prop they shouldn't have (Daniel with bread in 2B) | Prop state unstated | State both hands' contents: "holds only the empty open lunch box; nothing else in his hands". |
| A fake-looking or pasted-on door | A door invented for a close shot | Shoot from a side the environment sheet already shows (6C: straight behind Daniel, from the alley). |
| The flaws of a rejected still come back | The rejected still was passed as a reference | Never pass a rejected attempt; describe the wanted composition in words or use an approved still. |
| An environment sheet like a melted toy or clay town (curved walls, doll-sized door, lumpy grass) | "Rounded", "curved", "exaggerated" or "playful" geometry asked for to escape a photoreal first try | Real-world architecture and proportions; stylize through the render words (simplified textures, soft 3D shading, controlled saturated colour). See `environment-generation` animated mode. |
| Photoreal cats or animals | A real-animal word dominating | Keep the "stylized feature-animation fur, big glossy eyes" wording and pass the sheet. |

## Clips

| Symptom | Cause | Fix |
|---|---|---|
| A face drifts mid-clip (lost moustache) | Only the still passed | Pass every character's sheet after `@image1`; name 2–3 identity locks in the prompt. |
| Zoom, push or drift | A camera move named anywhere, or no framing line | The positive locked-frame paragraph, naming the landmarks that must stay the same size and place. |
| A character stands frozen | No timed action for them | Give every visible character timed action plus secondary motion. |
| Food multiplies or reappears | Bite-by-bite eating | Take it whole in one go; "exactly ONE sandwich… never multiplies"; the empty wrapper stays. |
| Something appears in a gap after "no kitten" | A negation naming the thing | Remove the word entirely. Describe the gap: "stays completely dark and still the whole time". |
| A character walks out of a wall | The start position is off-screen or behind geometry | Remake the still with the character already at their spot (10B: Daniel already by the lamp). |
| Glitchy growth or morph | Scale-up transforms, "comes closer and gets bigger" | Split into two shots: far, then near. |
| Spinning, or a glitchy turn | Complex turn or reversal in 4 s | One direction of travel; a turn is its own beat with time. |
| A character walks when they shouldn't (8A) | Action verbs implying travel | "Feet planted; stays on the same spot"; give the energy to the face and arms. |
| Unwanted voices or creature sounds (kitten cries in 6A) | Sound named for an off-screen source | Leave it out of the clip and add it in the edit from another clip. |
| Thunder or rain nobody asked for | Weather words in the prompt | Describe only the wanted ambience in Sound. |
| Words spoken on camera | Character "shouts" or "says" | "Never says any words; only wordless sounds such as…". |
| A random object (red box, glitch box) | An ambiguous prop in the still | Simplify the still's props, or name the object and its fixed place in the clip. |

## Flow and batches

| Symptom | Fix |
|---|---|
| `NOT_FOUND`, or a lost job that resumes to nothing | Put a new `"seed"` on the job: the batch resumes jobs by prompt, ingredients and seed. |
| A 1080p final differs from the approved draft | Finals are new generations. Review finals against drafts; rename the bad one `rejected-…`, change the seed, rerun that shot. |
| The 1080p upsample fails or costs credits | It is free only on a paid account; flow sends upsample jobs only to paid accounts; if none has credits, finals fail with a hint. A 360p draft cannot be upscaled. |
| A batch interrupted | Rerun the same command; outputs that exist are skipped and accepted jobs resume. |

## Edit and delivery

| Symptom | Fix |
|---|---|
| Full subtitles delivered when the client wanted a few captions | Reread the brief's caption section before any edit deliverable; use the client's exact wording at the moments they name; quote the brief back to the user. |
| Time spent building an edit tool the user didn't need | The user edits (CapCut). Deliver ordered clips, timings and placements unless asked for more. |
| Clips shorter than their voiceover line, regenerated longer | Time the voiceover with `video-plan` before the shot list; each line's clips cover its slot plus 1 s. Longer is only trimmed. |
| Shots added after the finals (a third of Milo video 1) | Story lock with the approved `PLAN.md`; check voiceover coverage with the animatic before any clips. |
