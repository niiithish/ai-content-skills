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
12. **Clips:** the frame stays put from start to end (or makes its one smooth move in a talking clip), everyone moves, and props don't multiply or vanish. A talking clip says its whole line, each word once, with no gaps.
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
| A product mascot's logo or label redrawn wrong (Mysa bottle, four tries) | The product generated from a description or restyled from a sheet | Edit the real product photo with `--ref`, adding only the face and limbs; quote the label text exactly. Once the user likes a take, build on that exact file. |
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
| A word said twice with a gap ("growing… growing") | Impact sounds (stamp, thud, slam) under the speech, or the line's words quoted again in Action as timing cues | Quote the line once, in Dialogue; time Action in seconds; "The spoken line above is the only dialogue… every word said exactly once, in order"; no impact sounds while anyone speaks. See `clip-prompt.md`. |
| A sentence cut off at the end of a clip (Mysa 8a) | One sentence split across two clips | Never split a sentence; a clip holds whole sentences, up to 10 s. |
| A mascot sad, flat or grumpy all clip | Mood words in the prompt ("deadpan stare", "yikes face", "awkward grin") | Only the plan's expression, said positively, held first frame to last. |
| A "continuous" clip jumps back to its opening frame midway | @image1 read as a frame to return to | The one-take paragraph: changes only go forward, the effect never vanishes, "@image1 is only the first frame, never a frame to return to", the camera never returns to the opening framing. |
| A clip comes back complete but silent, line and action gone | The content filter on sensitive words ("lube", "vaginal") | Soften the wording around the line; ask the user before changing the client's line. |
| Boring first drafts (Mysa v1, "5/10") | A locked camera, gestures only, no visual idea | A slow smooth camera move and a playful visual idea per line that builds on its words, planned in `PLAN.md`. |
| Over-the-top fixes (crash zooms, fire, dirt on the mascot) | "Make it exciting" read as violence and speed | Smooth moves only; big effects that transform the world, never damage or dirty the character, unless the plan asks. |
| Speech with gaps, or action after the last word | Action timed to pause the line, sparkles or gags written for the end | Speech starts on frame one and never waits; after the last word the character only holds the pose. |
| A random object (red box, glitch box) | An ambiguous prop in the still | Simplify the still's props, or name the object and its fixed place in the clip. |

## Flow and batches

| Symptom | Fix |
|---|---|
| `lost by Google · regenerating on another account` | Normal: Google dropped the clip or left it stuck for 5 minutes, and flow is regenerating it once in the same run. Let the batch finish; don't stop or rerun it. |
| `NOT_FOUND`, or `QUEUE_STALLED`, after that regeneration | Rerun the batch once later; if it fails the same way, put a new `"seed"` on the job: the batch resumes jobs by prompt, ingredients and seed. |
| `PROMPT_REJECTED` | Google discarded that exact clip on two accounts. Simplify or rewrite the shot's prompt. |
| `BATCH_WORKER_FAILED` | Rerun the same command. |
| The same shots `NOT_FOUND` ("media vanished", "not visible to this account") on every account and seed while the rest succeed (Mysa video 3: 4 of 31) | Google's content filter took the finished clip down, not flow. Stop rerunning (each try spends credits on another account). Soften the still and the prompt: clothed or abstract figures, no bedroom or couple-in-bed staging, no quoted intimate label text (Mysa 8 went through as the couple at the bathroom sink). Tell the user the changes before rerunning as a new version. |
| A job stuck with no progress; there is no cancel command | Stop and report it to the user (command, last output, what you think is stuck); don't wait it out. See `flow`. |
| A chained clip's opening frame soft or different | Frame taken from the 360p draft, or redrawn with an image model | `make.py lastframe` from the approved clip's 1080p final. |
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
