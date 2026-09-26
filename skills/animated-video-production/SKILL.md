---
name: animated-video-production
description: Run a stylized 3D animated short-form video project end to end with Google Flow. Starts from an approved video-plan PLAN.md and covers character, environment and prop sheets, composed scene stills, 360p draft clips, 1080p finals and the hand-off to the editor, using batch scripts the user runs (or the agent, when the user asks for an unattended run). Use when a video plan's style is 3D feature animation (DreamWorks-style, Pixar-style); when continuing a project whose AGENTS.md names this skill; or for a single animated scene still or clip prompt. Not for claymation (clay-animation-video-prompt), photoreal ads or UGC talking heads.
---

# Animated Video Production

Turn a client's brief into a finished set of 1080p 9:16 clips in stylized 3D feature-animation CG, with as few regenerations as possible. Most lost time comes from three things: the story changing after production has started, the same prompt failures repeating from shot to shot, and reviewing one file at a time. This workflow stops each of them at a gate.

Files, loaded only when a phase needs them:

| File | Load it for |
|---|---|
| [references/scene-still.md](references/scene-still.md) | Writing any still prompt (phase 3) |
| [references/clip-prompt.md](references/clip-prompt.md) | Writing any clip prompt (phase 4) |
| [references/failure-locks.md](references/failure-locks.md) | Before writing prompts, and whenever a result is rejected |
| `scripts/init-project.sh` | Phase 2: adds the production folders to a planned video |
| `scripts/make.py` | Copied into each video by init; every batch, review and hand-off command |
| `templates/AGENTS.md` | Used by init: the client file skeleton |

Generation runs through the `flow` skill's CLI. Flow chooses the account for every job: free accounts first for stills and 360p drafts (they cost nothing there), and only paid accounts for finals, since the 1080p upscale needs one. Don't pin or switch accounts. Before a batch, if `flow accounts` shows the free accounts expired, run `flow account refresh` first; otherwise flow falls back to the paid account for stills and drafts. Reference sheets follow `character-generation`, `environment-generation` and `prop-generation` in their animated mode.

## Working with the user

- **The user runs batches.** For anything with more than one shot, write the prompts and manifest jobs, then give the one `make.py` command to run, in its own code block. Don't run long generations yourself or sit waiting on them. A single test still is fine to run inline when it settles a question. Everything else in `make.py` (`status`, `review`, `pick`, `animatic`, `handoff`, `sync`, and `--dry-run`) is quick: run it yourself, never hand it to the user.
- **Stop at every gate** and wait for approval. Show results as review sheets, never as a list of file paths to open one by one.
- **Report short, and decide.** After every batch, one table of every shot in the command: made, failed (with the error) or waiting (with the reason). Then the next command in its own code block, saying what it leaves out and why, and your recommendation. Never end on a menu of options, and leave out detail the user didn't ask for.
- **Nothing is overwritten.** A new attempt is the next version (`v2`, `v3`) with its own prompt file and a manifest job that replaces the old one. An approved still or clip is listed in `APPROVED.md` in `scenes/all/` or `clips/all/`, and from then on it's locked unless the user asks to redo it.
- **Check your own work before the user sees it.** After every batch, build the review sheet, read it yourself against the checklist in `failure-locks.md`, and report per shot: which take you'd pick, and what's wrong with any you wouldn't. Write the fix for any shot you'd reject before the user asks. When the user says they review clips (or stills) themselves, stop: no review sheets, frame reads or transcripts of those until they ask.
- **Make only what was asked.** When the user has picked a take or a base to build on, work from exactly that file and make one take, not several. No extra variants or new designs they didn't ask for.
- **A rule change redoes only the rejected shots.** When feedback changes a rule, write new versions for the shots the user rejected; approved and working prompts stay as they are unless the user names them.
- **Stop when flow is broken.** If `flow` hangs with no progress for about 10 minutes, or fails the same way twice after following its hint, stop at once. Report the exact command, the last lines of output, the error code and what you think is wrong (a stuck lock, an expired login, a Google error) in a few lines the user can hand to whoever fixes flow. Don't wait longer, work around it or offer a list of options.
- **Standing defaults, in every project, overridden only when the user says so:**
  - Generated stills and clips never contain captions, subtitles, text overlays or music. This holds even when the brief asks for captions or music: the user adds those in the edit.
  - Clip audio is what you would hear if you were standing in that scene: ambience, footsteps, objects, animals, and wordless character sounds (gasps, grunts, laughs, sighs), each tied to a visible action.
  - No music, narration or spoken words, unless the plan has characters speaking their lines on camera: then each clip carries its line (see "Characters who speak on camera" in `clip-prompt.md`).

  The clip template in `clip-prompt.md` writes all of this into every prompt. Keep it.
- **Record decisions.** When the user or the client decides something that changes a default, add it with the date to the Decisions list in the project `AGENTS.md`, and to `failure-locks.md` if it's a prompt lesson that would apply to other projects too.

## Unattended runs

Only when the user says to run the whole video without them (they are away and won't review). Then everything above changes like this:

- **You run every batch yourself** and wait for it to finish, including sheets, `stills`, `clips` and `finals`.
- **You are the reviewer at every gate.** Approve the plan and sheets yourself, read every review sheet against `failure-locks.md`, pick takes with `make.py pick`, and add each approval to `APPROVED.md` marked `(agent)`.
- **Retry limits.** A still gets at most 2 new versions and a clip at most 1; after that, keep the best one and flag it. The video-credit budget is 200 unless the user gives one: check `flow accounts` before each clip batch, and don't start one that would go over.
- **Stop only for** `LOGIN_REQUIRED`, a spent budget, a CLI error whose hint doesn't resolve it, or flow hanging with no progress (report it as in "Stop when flow is broken").
- **Log everything in `video-N/RUN-LOG.md`** as you go: each gate you passed, what you picked or rejected and why, credits spent, and a final "Check these" list of anything the user should look at.
- **Finish with** `make.py handoff` and `make.py status`, and end your reply with the summary from `RUN-LOG.md`.

## Phases 0–1: plan

Every video starts with the `video-plan` skill. It writes `video-N/PLAN.md` (brief table, voiceover timing, sheets to make, and a shot table with clip lengths) and prints `PLAN.pdf`. Don't start phase 2 until the user has approved the plan.

- The plan's shot table is the story lock. After approval, add or cut shots only when the user asks. When they do, update `PLAN.md` and reprint the PDF, and insert the new job in `scenes/stills-batch.json` at its place in story order (the manifest order is the edit order).
- A shot's clip length comes from the plan and is never shortened.
- When the client's real voiceover arrives, retime it with `video-plan` before the clips are made.

## Phase 2: reference sheets

1. Run `bash <skill-dir>/scripts/init-project.sh <client-folder> video-N`, where `<skill-dir>` is the folder holding this file. It adds `AGENTS.md`, the sheet folders, `project.conf`, the manifests and `scripts/make.py`, and never overwrites existing files. After the skill is updated, refresh a video's copy of `make.py` with `--update-scripts`. For a standalone video (its own `AGENTS.md` and brief inside the video folder; see `video-plan` step 1), pass `.` as the video: `init-project.sh <client>/video-2 .` puts everything, sheets included, straight into `video-2/`.
2. Take every recurring character, location and prop from the plan's "Sheets to make". Write each sheet prompt with the matching sheet skill in its animated mode: one landscape image, stylized CG, neutral light, and no grey studio backdrop leaking into scenes. Save it to `characters/<name>/prompts/`, `environments/<name>/prompts/` or `props/<name>/prompts/`.
3. Generate them one or two at a time, because sheets need individual attention: `video-N/scripts/make.py sheet characters/rocco/prompts/rocco-v1.md` saves `characters/rocco/rocco-v1.jpg`. Add `--ref <image>` for a reference (a new version made from an approved one). Don't write your own batch files or scripts for sheets or anything else `make.py` covers; they litter the video folder. If `make.py` can't do something you need, say so in `RUN-LOG.md`.
4. **Hero still per environment:** one still in each location, usually its first shot, becomes its look reference, fixing brightness, light direction, colour and render style. It is made and approved first in phase 3, then recorded in the Environments table in `AGENTS.md`. Every other still in that location passes it as an ingredient. Video 1 of the Milo project lost most of its rejected versions to shots in a location that had no hero still.
5. **Product mascots** (a real product with a face and limbs): image models redraw logos and labels wrong. Make the sheet by editing the client's real product photo with `--ref`, adding only the face, arms and legs, and quote the label text exactly; never generate the product or its logo from a description.
6. **Gate:** the user approves the sheets. Fill in the Characters, Environments, Props and Look sections of `AGENTS.md`.

## Phase 3: stills

1. Load `scene-still.md` and `failure-locks.md`. Write one prompt per shot to `scenes/scene-N/scene-Nx/prompts/scene-Nx-v1.md`.
2. Add one job per shot to `scenes/stills-batch.json` with `"variants": 2`. Stills cost no credits, so a second seed is cheaper than another round of review. The two takes land in the shot's `takes/` folder (`scene-4/takes/scene-4-v1-take1.jpg`, `-take2`) until you pick one. A hero still's ingredients are the environment sheet and character sheets; every other still in that location lists the hero's output path (`scene-1a-v1.jpg`) first, for light and render only (see `scene-still.md`: it must not hand over its framing or poses).
3. **Heroes first.** The user runs `video-N/scripts/make.py stills 1a 3a` with just the hero shots. Review, pick and approve them (steps 5–6), and record them in `AGENTS.md`.
4. The user runs `make.py stills` for the rest. A job whose ingredient is a still that isn't made or picked yet is held back and named in the output; finished outputs are skipped.
5. Run `make.py review stills` and read every sheet. Report a pick or a fix for each shot.
6. The user decides. For each pick, run `make.py pick 1a 2` (take 2) and add a line to `scenes/all/APPROVED.md` (file name and date). Rejected shots get a `v2` job, replacing the `v1` job in place, with only that shot's prompt changed, and the user reruns `make.py stills 3b 7a`.
7. Once most stills are approved, run `make.py animatic` and send the user `edit/animatic.mp4`, laid over the voiceover if there is one. The user watches the timing before any clip credits are spent. Stills are held for their `Clip` length from `PLAN.md`.
8. **Gate:** every still is approved.

## Phase 4: 360p draft clips

1. Load `clip-prompt.md`. Open each approved still first, then write its clip prompt from what is actually in it (who stands where, facing which way), not from the still's prompt. One prompt per shot, in `clips/clip-N/clip-Nx/prompts/clip-Nx-v1.md`.
2. Add jobs to `clips/clips-batch.json`:
   - `"resolution": "360p"` and `"timeout": 900`.
   - Duration from the plan's Clip column.
   - Ingredients: the approved still first, then the sheet of every character in the shot.
   - One variant by default, because clips cost credits. Use `"variants": 2` only for a shot that has already failed twice.
3. The user runs `make.py clips`. Every clip starts from its own approved still, so every clip in the plan can run in the first batch. Chaining (starting a clip from the previous clip's last frame) is only used when the user asks for it, or when the plan splits one spoken line across clips so it plays as one shot.
   - **Chained clips** can't run until the clip before them is approved and has its final: approve `8a`, run `make.py finals 8a`, then `make.py lastframe 8a 8b` saves a frame 0.5 s before the end of the 1080p final as `8b`'s opening still. Never take the frame from a 360p draft, and never redraw it with an image model: both come out soft or different.
   - Say which clips are chained and in what order before the first batch, and list them as "waiting on 8a" in every report, so none is held back silently.
4. Every clip report lists all the plan's clips as made, failed (with the error) or not run (with the reason). A clip is never left out of a command without saying so. `make.py clips` ends with this "Not made" list: copy it into the report.
5. Run `make.py review clips` (start, middle and end frames for each clip) and check them against the list. For motion problems the frames can't show, ask the user to watch those clips.
6. Rejects become the next version, as with stills. Approvals go in `clips/all/APPROVED.md`.
7. **Gate:** every clip is approved.

## Phase 5: 1080p finals

1. The user runs `make.py finals`. Every clip job needs an approved draft; name shots to make finals for only some of them.
   - Each final reruns the approved prompt and ingredients as a native 720p generation, then upsamples it to 1080p.
   - The output goes to `clip-Nx/final/` and replaces the draft in `clips/all/`.
   - For finals of new or redone shots only: `make.py finals --into new-1080p 7c 10b`.
2. A final is a new generation and can differ from its draft (the Milo project's 7C final had four kittens instead of three). Run `make.py review finals`, which shows each draft beside its final, and check every one.
3. To redo a bad final:
   - In `clip-Nx/final/`, rename both the 720p file and its `-1080p` file to `rejected-<reason>-<name>`.
   - Put a new `"seed"` on that clip's job, because the same seed resumes the same result.
   - The user reruns `make.py finals <shot>`.

## Phase 6: hand-off

1. Run `make.py handoff`. `edit/clips/` gets the final clips numbered in story order, plus `ORDER.txt`.
2. The user edits. So far that has been in CapCut, with music, voiceover and captions added there.
3. Before any edit-stage deliverable (captions, a cut list, music notes, a stitched preview), reread that exact section of the brief and quote it to the user first. Give the user what the brief describes:
   - Captions are the client's own wording from Edit notes in `PLAN.md`, at the few moments the brief names, with in/out times from `voiceover/timing.md` (retime the real voiceover with `video-plan` first).
   - Never full subtitles or new caption copy unless asked.
   - Don't build an editing tool or render the edit yourself unless the user asks for it.
4. Update the Videos table in `AGENTS.md`.

## make.py

Run it from anywhere as `video-N/scripts/make.py <command>`:

| Command | Does |
|---|---|
| `status` | Warns when `PLAN.pdf` is older than `PLAN.md`; every shot in story order: newest still, clip, whether a 1080p exists, takes waiting for a pick |
| `stills [shots] [--dry-run]` | Stills batch (all shots, or only those named); skips outputs that exist, holds back jobs waiting on an unmade still; syncs `scenes/all` |
| `clips [shots] [--dry-run]` | 360p clip batch; ends with every manifest job that has no output and why (failed with its code, waiting, missing input, not named); syncs `clips/all` |
| `finals [shots] [--into DIR] [--no-draft] [--dry-run]` | 720p + 1080p upsample; flow sends these only to paid accounts; skips finals that exist. `--into` also copies the named shots' 1080p files to `clips/DIR/` |
| `sheet PROMPT [--ref IMG] [--seed N] [--dry-run]` | One 16:9 reference sheet from its prompt file, saved next to `prompts/` with the same name (`rocco-v2.md` → `rocco-v2.jpg`); refuses to overwrite |
| `lastframe FROM TO` | Opening still for a chained clip: the frame 0.5 s before the end of clip FROM's 1080p final, saved as TO's next still version (`make.py lastframe 8a 8b` → `scene-8b-vK.jpg`) |
| `pick SHOT TAKE [--clip]` | Copies a take (`scene-1a/takes/scene-1a-v1-take2.jpg`) up to the shot's version file (`scene-1a/scene-1a-v1.jpg`) |
| `review stills\|clips\|finals [shots]` | Contact sheets in `review/`, 10 stills or 4 clips per image |
| `animatic` | `edit/animatic.mp4`: clips where they exist, stills elsewhere, labelled, over `voiceover/recording.*` or the scratch read |
| `handoff` | Numbered final clips in `edit/clips/` |
| `sync` | Refreshes `scenes/all/` and `clips/all/` to the newest version of each shot (1080p once it exists) |

Manifest job shapes. Paths are absolute or relative to the manifest (from `scenes/`, a sheet is `../../characters/milo/milo-v1.png`). The id is the output's file name without the extension:

```json
{"id": "scene-1a-v1", "kind": "image", "prompt_file": "/ABS/scenes/scene-1/scene-1a/prompts/scene-1a-v1.md",
 "aspect": "9:16", "ingredient": ["/ABS/characters/milo/milo.png", "/ABS/environments/street/street-v1.jpg"],
 "output": "/ABS/scenes/scene-1/scene-1a/scene-1a-v1.jpg", "variants": 2}
{"id": "clip-1a-v1", "kind": "video", "prompt_file": "/ABS/clips/clip-1/clip-1a/prompts/clip-1a-v1.md",
 "aspect": "9:16", "duration": 4, "resolution": "360p", "timeout": 900,
 "ingredient": ["/ABS/scenes/scene-1/scene-1a/scene-1a-v1.jpg", "/ABS/characters/milo/milo.png"],
 "output": "/ABS/clips/clip-1/clip-1a/clip-1a-v1.mp4"}
```

Optional: `"seed"` to force a fresh job, since Flow resumes a job whose prompt, ingredients and seed match a lost one.

## Project layout

```
<client>/
  AGENTS.md                 client rules, look, sheets, decisions
  brief/                    the client's files, untouched
  characters/<name>/<name>-v1.jpg + prompts/     shared by every video
  environments/<name>/...   props/<name>/...
  video-1/
    PLAN.md  PLAN.pdf  project.conf  scripts/make.py
    voiceover/                script.md, timing.md, scratch.wav, recording.* (the real read)
    scenes/stills-batch.json  scenes/scene-1/scene-1a/{scene-1a-v1.jpg, prompts/scene-1a-v1.md, takes/}   scene with several shots
                              scenes/scene-3/{scene-3-v1.jpg, prompts/scene-3-v1.md, takes/}             scene with one shot
                              takes/ holds the unpicked seeds: scene-3-v1-take1.jpg, -take2
    scenes/all/               newest (or picked) still per shot + APPROVED.md
    clips/clips-batch.json    clips/clip-1/clip-1a/{clip-1a-v1.mp4, prompts/, final/}
                              clips/clip-3/{clip-3-v1.mp4, prompts/, final/}
    clips/all/                newest clip per shot, 1080p once it exists + APPROVED.md
    review/  edit/
```

A standalone video has the same contents with no client level above it: `video-2/` holds `AGENTS.md`, `brief/`, `characters/`, `environments/`, `props/`, `PLAN.md`, `scripts/make.py`, `voiceover/`, `scenes/`, `clips/`, `review/` and `edit/`.

Shot ids are a scene number with no leading zero. A letter only ever means another shot in the same scene, a different beat of the line with its own camera (the cat grabs the bread in `5a`, the police give chase in `5b`); it never means another try of the same shot. Tries are versions (`-v2`) and seeds of one version are takes (`takes/…-take2`). A scene with one shot has no letter (`3`: `scenes/scene-3/scene-3-v1.jpg`); a scene with several gets one letter per shot and a folder each (`1a`, `1b`: `scenes/scene-1/scene-1a/scene-1a-v1.jpg`). Clips mirror scenes. Letters follow play order: a shot inserted between `8a` and `8b` becomes `8b`, and the old `8b` and every later letter move up one (files, prompts, manifest ids and the plan). Never give it the next free letter, because `8c` playing before `8b` confuses everyone. If a one-shot scene gains a second shot, first move its files to `scene-3/scene-3a/` (and `clip-3/clip-3a/`), renaming `scene-3-` to `scene-3a-` in the files, prompts and manifests; `make.py` refuses a scene with both.

## Visual direction

- The default for "Pixar-style", "DreamWorks-style" or plain "AI animation" is DreamWorks-inspired feature-animation CG:
  - sculpted, appealing, slightly stylized characters with large expressive eyes
  - soft groomed fur and shaped hair and fabric
  - rich but controlled colour, layered sets and readable depth
  
  Describe these visible qualities in every prompt instead of relying on a studio name. The look is not photoreal and not a flat cartoon.
- Light comes from sources that exist in the location. No golden hour, amber haze, orange rim light or sunset unless the brief asks for it. Image models drift into these by default.
- Keep identity, wardrobe, proportions, scale, location layout and light consistent from sheets through stills to clips. Put relative scale in every prompt with more than one character (for example: the cat's back is at the man's shin).
- 9:16 unless the brief says otherwise. Keep the action in the central 70% of the frame, clear of the bottom and right edges where short-video apps put their buttons.

## Final check before each gate

- **Plan:** `video-plan`'s own checks passed, and the user approved `PLAN.pdf`.
- **Stills:** you read the review sheets yourself, and each shot has a pick or a fix.
- **Clips:** the frame stays locked (or makes its one smooth move in a talking clip), everyone keeps moving, and the audio is scene-only or the exact line, each word once.
- **Finals:** each one was compared with its draft.
- **Hand-off:** it matches what the brief asks for, no more.
