---
name: animated-video-production
description: Run a stylized 3D animated short-form video project end to end with Google Flow. Covers client brief intake, a shot list timed to the voiceover, character, environment and prop sheets, composed scene stills, 360p draft clips, 1080p finals and the hand-off to the editor, using batch scripts the user runs. Use when a client brief or message asks for a DreamWorks-style, Pixar-style or feature-animation AI video; when starting a new animated video project in an empty folder; when continuing a project whose AGENTS.md names this skill; or for a single animated scene still or clip prompt. Not for claymation (clay-animation-video-prompt), photoreal ads or UGC talking heads.
---

# Animated Video Production

Turn a client's brief into a finished set of 1080p 9:16 clips in stylized 3D feature-animation CG, with as few regenerations as possible. Most lost time comes from three things: the story changing after production has started, the same prompt failures repeating from shot to shot, and reviewing one file at a time. This workflow stops each of them at a gate.

Files, loaded only when a phase needs them:

| File | Load it for |
|---|---|
| [references/scene-still.md](references/scene-still.md) | Writing any still prompt (phase 3) |
| [references/clip-prompt.md](references/clip-prompt.md) | Writing any clip prompt (phase 4) |
| [references/failure-locks.md](references/failure-locks.md) | Before writing prompts, and whenever a result is rejected |
| `scripts/init-project.sh` | Phase 0: creates the project folders |
| `scripts/make.py` | Copied into each video by init; every batch, review and hand-off command |
| `templates/` | Used by init: the `AGENTS.md` and `SHOT-LIST.md` skeletons |

Generation runs through the `flow` skill's CLI. Reference sheets follow `character-generation`, `environment-generation` and `prop-generation` in their animated mode.

## Working with the user

- **The user runs batches.** For anything with more than one shot, write the prompts and manifest jobs, then give the one `make.py` command to run, in its own code block. Don't run long generations yourself or sit waiting on them. A single test still is fine to run inline when it settles a question.
- **Stop at every gate** and wait for approval. Show results as review sheets, never as a list of file paths to open one by one.
- **Nothing is overwritten.** A new attempt is the next version (`v2`, `v3`) with its own prompt file and a manifest job that replaces the old one. An approved still or clip is listed in `APPROVED.md` in `scenes/all/` or `clips/all/`, and from then on it's locked unless the user asks to redo it.
- **Check your own work before the user sees it.** After every batch, build the review sheet, read it yourself against the checklist in `failure-locks.md`, and report per shot: which variant you'd pick, and what's wrong with any you wouldn't. Write the fix for any shot you'd reject before the user asks.
- **Record decisions.** When the user or the client decides something that changes a default, add it with the date to the Decisions list in the project `AGENTS.md`, and to `failure-locks.md` if it's a prompt lesson that would apply to other projects too.

## Phase 0: intake

This phase runs in a new or empty client folder, or when the user pastes a brief or message.

1. Run `bash <skill-dir>/scripts/init-project.sh <client-folder> video-1`, where `<skill-dir>` is the folder holding this file. It never overwrites existing files. For another video in the same client folder, run it with `video-2` and so on.
2. If the brief is a chat message, save it verbatim to `brief/message-YYYY-MM-DD.md`. Read every file in `brief/` in full, including the editing and caption sections.
3. Fill in the **Brief digest** in `AGENTS.md`, quoting the brief section for every answer. Take particular care with voiceover, music, captions, deliverables and clip rules: these are what get delivered wrong. Mark anything the brief doesn't settle as **ASK**, and write the questions for the client. Keep them short and ready to paste into a message.
4. **Gate:** the user confirms the digest and answers or forwards the questions.

## Phase 1: story lock

1. Write `video-N/SHOT-LIST.md` from the voiceover script, in story order.
   - Every voiceover line has a shot under it.
   - Each shot is one visible beat, 4, 6 or 8 s long (Flow lengths; trim in the edit).
   - Picture total is at least the voiceover length. Estimate about 2.6 spoken words per second. When `edit/voiceover.*` exists, measure it instead with a speech-to-text tool that gives word timestamps (for example faster-whisper).
2. Plan each shot so it can start from a still:
   - Characters are already where the action needs them in the first frame.
   - Nothing grows on screen.
   - Nobody walks in through a wall.
   - The action fits the clip length.
   - A beat that needs a new camera side gets its own shot.
3. Run the coverage check at the bottom of the shot list.
4. **Gate: story lock.** The user approves the shot list. After that, add or cut shots only when the user asks. When they do, insert the new job in `scenes/stills-batch.json` at its place in story order (the manifest order is the edit order) and update the shot list.

## Phase 2: reference sheets

1. List every recurring character, location and prop. Write each sheet prompt with the matching sheet skill in its animated mode: one landscape image, stylized CG, neutral light, and no grey studio backdrop leaking into scenes. Save it to `characters/<name>/prompts/`, `environments/<name>/prompts/` or `props/<name>/prompts/`.
2. Generate them one or two at a time: sheets need individual attention.
3. **Hero still per environment:** the first approved still in each location becomes its look reference, fixing brightness, light direction, colour and render style. Record it in the Environments table in `AGENTS.md`. Every later still in that location passes it as an ingredient. Video 1 of the Milo project lost most of its rejected versions to shots in a location that had no hero still.
4. **Gate:** the user approves the sheets. Fill in the Characters, Environments, Props and Look sections of `AGENTS.md`.

## Phase 3: stills

1. Load `scene-still.md` and `failure-locks.md`. Write one prompt per shot to `scenes/scene-N/scene-Nx/prompts/scene-Nx-v1.md`.
2. Add one job per shot to `scenes/stills-batch.json` with `"variants": 2`. Stills cost no credits, so a second seed is cheaper than another round of review.
3. The user runs `video-N/scripts/make.py stills`.
4. Run `make.py review stills` and read every sheet. Report a pick or a fix for each shot.
5. The user decides. For each pick, run `make.py pick 1a b` and list it in `scenes/all/APPROVED.md`. Rejected shots get a `v2` job with only that shot's prompt changed, and the user reruns `make.py stills 3b 7a`.
6. Once most stills are approved, run `make.py animatic` and send the user `edit/animatic.mp4`, laid over the voiceover if there is one. The user watches the timing before any clip credits are spent.
7. **Gate:** every still is approved.

## Phase 4: 360p draft clips

1. Load `clip-prompt.md`. Write one prompt per shot to `clips/clip-N/clip-Nx/prompts/clip-Nx-v1.md`.
2. Add jobs to `clips/clips-batch.json`:
   - `"resolution": "360p"` and `"timeout": 900`.
   - Duration from the shot list.
   - Ingredients: the approved still first, then the sheet of every character in the shot.
   - One variant by default, because clips cost credits. Use `"variants": 2` only for a shot that has already failed twice.
3. The user runs `make.py clips`.
4. Run `make.py review clips` (start, middle and end frames for each clip) and check them against the list. For motion problems the frames can't show, ask the user to watch those clips.
5. Rejects become the next version, as with stills. Approvals go in `clips/all/APPROVED.md`.
6. **Gate:** every clip is approved.

## Phase 5: 1080p finals

1. The user runs `make.py finals`. Set `PRO_ACCOUNT` in `project.conf` to the paid Flow account first.
   - Each final reruns the approved prompt and ingredients as a native 720p generation, then upsamples it to 1080p.
   - The output goes to `clip-Nx/final/` and replaces the draft in `clips/all/`.
   - For finals of new or redone shots only: `make.py finals --into new-1080p 7c 10b`.
2. A final is a new generation and can differ from its draft (the Milo project's 7C final had four kittens instead of three). Run `make.py review finals`, which shows each draft beside its final, and check every one.
3. To redo a bad final:
   - Rename the file to `rejected-<reason>-<name>`.
   - Put a new `"seed"` on that clip's job, because the same seed resumes the same result.
   - The user reruns `make.py finals <shot>`.

## Phase 6: hand-off

1. Run `make.py handoff`. `edit/clips/` gets the final clips numbered in story order, plus `ORDER.txt`.
2. The user edits. So far that has been in CapCut, with music, voiceover and captions added there.
3. Before any edit-stage deliverable (captions, a cut list, music notes, a stitched preview), reread that exact section of the brief and quote it to the user first. Give the user what the brief describes:
   - Captions are the client's own wording, at the few moments the brief names, with in/out times taken from the voiceover.
   - Never full subtitles or new caption copy unless asked.
   - Don't build an editing tool or render the edit yourself unless the user asks for it.
4. Update the Videos table in `AGENTS.md`.

## make.py

Run it from anywhere as `video-N/scripts/make.py <command>`:

| Command | Does |
|---|---|
| `status` | Every shot in story order: newest still, clip, whether a 1080p exists, variants waiting for a pick |
| `stills [shots] [--dry-run]` | Stills batch (all shots, or only those named); skips outputs that exist; syncs `scenes/all` |
| `clips [shots] [--dry-run]` | 360p clip batch; syncs `clips/all` |
| `finals [shots] [--into DIR] [--no-draft]` | 720p + 1080p upsample on `PRO_ACCOUNT`, then restores the previously active account |
| `pick SHOT LETTER [--clip]` | Copies variant `-b` to the shot's version file |
| `review stills\|clips\|finals [shots]` | Contact sheets in `review/`, 10 stills or 4 clips per image |
| `animatic` | `edit/animatic.mp4`: clips where they exist, stills elsewhere, labelled, over `edit/voiceover.*` |
| `handoff` | Numbered final clips in `edit/clips/` |
| `sync` | Refreshes `scenes/all/` and `clips/all/` to the newest version of each shot (1080p once it exists) |

Manifest job shapes (all paths absolute or relative to the manifest):

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
  AGENTS.md                 client rules, brief digest, sheets, decisions
  brief/                    the client's files, untouched
  characters/<name>/<name>-v1.jpg + prompts/     shared by every video
  environments/<name>/...   props/<name>/...
  video-1/
    SHOT-LIST.md  project.conf  scripts/make.py
    scenes/stills-batch.json  scenes/scene-1/scene-1a/{scene-1a-v1.jpg, prompts/scene-1a-v1.md}
    scenes/all/               newest (or picked) still per shot + APPROVED.md
    clips/clips-batch.json    clips/clip-1/clip-1a/{clip-1a-v1.mp4, prompts/, final/}
    clips/all/                newest clip per shot, 1080p once it exists + APPROVED.md
    review/  edit/
```

Shot ids are a scene number plus a letter (`1a`, `10b`), and file stems are `scene-1a-v1` and `clip-1a-v1`. An inserted shot gets the next free letter in its scene (`2c`), and its place in the manifest sets its position in the edit.

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

- **Intake:** the digest quotes the brief on voiceover, music, captions and deliverables, and the questions for the client are written.
- **Story lock:** every voiceover line is covered, picture ≥ voiceover, one beat per shot, and each shot can start from a still.
- **Stills:** you read the review sheets yourself, and each shot has a pick or a fix.
- **Clips:** the frame stays locked, everyone keeps moving, and the audio is scene-only.
- **Finals:** each one was compared with its draft.
- **Hand-off:** it matches what the brief asks for, no more.
