---
name: video-production
description: The shared production pipeline for a short-form Google Flow video in any style. It starts from an approved video-plan PLAN.md and covers the project layout, init-project.sh, make.py (every batch, review and hand-off command), reference sheets, stills, 360p draft clips, 1080p finals, reuse of approved clips and the hand-off to the user's edit. It is loaded by a style skill (animated-video-production, photoreal-video-production or clay-video-production), which adds the look and the prompt templates. Use it with one of those; use it alone only for project housekeeping (status, layout, sync, reuse).
---

# Video Production

Turn an approved plan into a finished set of 1080p 9:16 clips with as few regenerations as possible, in a folder the user can find their way around. Most lost time comes from four things:

- the story changing after production has started;
- the same prompt failures repeating from shot to shot;
- reviewing one file at a time;
- batch files and retries piling up beside the media.

This workflow stops each of them at a gate. It is style-agnostic: the style skill that loaded it (`animated-video-production`, `photoreal-video-production` or `clay-video-production`) holds the look, the still and clip prompt templates and its own failure locks.

Files, loaded only when a phase needs them:

| File | Load it for |
|---|---|
| [references/sheets/](references/sheets/) | The character, place and product sheet layouts every style uses (phase 2), each with its JSON blueprint |
| [references/failure-locks.md](references/failure-locks.md) | The QA checklist for every review, Flow and batch problems, the edit and delivery lessons |
| `scripts/init-project.sh` | Phase 2: adds the production folders to a planned video |
| `scripts/make.py` | Copied into each video by init; every batch, review, reuse and hand-off command |
| `templates/AGENTS.md` | Used by init: the client file skeleton |

Generation runs through the `flow` skill's CLI. Flow chooses the account for every job: stills and 360p drafts go only to free accounts, and finals go only to paid ones, since the 1080p upscale needs one. If no free account has credits, a draft batch stops with `QUOTA` rather than spend paid credits: run `flow account refresh`, and if that doesn't help, tell the user. If it stops with `RECAPTCHA_FAILED` (Google refusing every free account), don't just wait and rerun: tell the user right away and ask whether to spend premium credits with `FLOW_ALLOW_PAID_DRAFTS=1`; premium is rarely refused. Never set `FLOW_ALLOW_PAID_DRAFTS=1` unless the user says to. Don't pin or switch accounts.

## Working with the user

- **Who runs what.**
  - **You run** sheets, stills and 360p clip batches yourself, in the background (`run_in_background`, let its exit notify you; see `flow`, Waiting on a run). Then you review them and report.
  - **The user runs only 1080p finals**, because they spend paid credits: give the one `make.py finals` command in its own code block.
  - Everything else in `make.py` (`status`, `review`, `pick`, `reuse`, `animatic`, `handoff`, `sync`, `--dry-run`) is quick: run it yourself, never hand it to the user.
- **One take per shot.** Every still and clip job makes one version (`"variants": 1`, the default). Never make a second take or a second version for the user to choose between. The user sees one result per shot; more only when they ask for it.
- **Check your own work before the user sees it.** After every batch, build the review sheet with `make.py review` and read it against the checklist in `failure-locks.md`. If you'd reject a shot, write its next version with the fix and rerun that shot once, before the user sees it. Then report. When the user says they review clips (or stills) themselves, stop reviewing those until they ask.
- **The user reviews in review-board.** At the start of every session in a project, run `~/Work/review-board/bin/review <project>` (it starts the local board if needed; clone https://github.com/niiithish/review-board to `~/Work/review-board` if it's missing), and give the user the URL once. New stills and clips show up there on their own.
  - When the user says they've reviewed, run `~/Work/review-board/bin/review flags <project>`:
    - flagged files are rejects, with the user's reason in the comment;
    - approved files are picks (record them in `APPROVED.md`);
    - a comment alone is a note;
    - an `attached image:` line is a picture the user pasted to show what they mean: open it.
  - Never ask the user to list what they flagged. Reviews are saved in `<project>/review.json`; don't edit it.
- **Stop at every gate** and wait for approval.
- **Terse replies.** At most a short table (shot, result, your call) and one line on what's next, ending on your recommendation or the command. No write-ups, no menus of options, no detail the user didn't ask for.
- **The edit is in FilmCraft, with the user.** Build the timeline from the approved clips with the `filmcraft` skill, ready to export but not exported. The user tweaks it in the open app. Then `filmcraft-pacing` (dead air, motion) and `captions-filmcraft` (captions as text clips) when asked, and `filmcraft` exports when the user says so.
- **Nothing is overwritten.** A new attempt is the next version (`v2`, `v3`), with its own prompt file and a manifest job that replaces the old one. An approved still or clip is listed in `APPROVED.md` in `scenes/all/` or `clips/all/`. From then on it's locked unless the user asks to redo it.
- **`make.py` owns batching (hard rule).**
  - Every still and clip is a job in the one manifest (`scenes/stills-batch.json`, `clips/clips-batch.json`), run by `make.py stills|clips|finals [shots]`.
  - A retry is the next version's job in that same manifest, replacing the old one, then `make.py clips 3b 7a`.
  - Never write another manifest, a `redo` batch file or a script of your own, and never call `flow batch` or `flow generate` directly for shots: those files pile up beside the media (video-3 ended with about 80 of them in `clips/` and `stills/`).
  - `make.py` keeps its run files, flow state and logs in `video-N/.flow/`. If it can't do something you need, say so rather than working around it.
- **Reuse before regenerating.** A clip or still the client already approved in an earlier video is better than a new one: `make.py reuse 7b ../video-1/clips/all/clip-3.mp4` copies it in as the shot's next version (and its final, if it's 1080p).
- **Make only what was asked.** When the user has picked a take or a base to build on, work from exactly that file. No extra designs they didn't ask for.
- **A rule change redoes only the rejected shots.** When feedback changes a rule, write new versions for the shots the user rejected. Approved and working prompts stay as they are unless the user names them.
- **Stop means stop.** When the user says stop, stop every background task, pending wakeup and monitor you started, not just the current command.
- **Stop when flow is broken.** If `flow` hangs with no progress for about 10 minutes, or fails the same way twice after following its hint, stop at once. Report, in a few lines the user can hand to whoever fixes flow:
  - the exact command;
  - the last lines of output;
  - the error code;
  - what you think is wrong.

  Don't wait longer or work around it.
- **Standing defaults, in every project, overridden only when the user says so:**
  - Generated stills and clips never contain captions, subtitles, text overlays or music. The user's edit carries those, and captions go into the FilmCraft edit afterwards.
  - Clip audio is what you would hear standing in that scene: ambience, footsteps, objects, and wordless sounds tied to a visible action.
  - No music, narration or spoken words, unless the plan has people speaking their lines on camera.

  The style skill's clip template writes all of this into every prompt. Keep it.
- **Record decisions.** When the user or the client decides something that changes a default, add it with the date to the Decisions list in the project `AGENTS.md`. If it's a prompt lesson that would apply to other projects too, also add it to the right `failure-locks.md`.

## Unattended runs

Only when the user says to run the whole video without them (they are away and won't review). Then:

- **You also run finals** and wait for them.
- **You are the reviewer at every gate.** Approve the plan and sheets yourself, read every review sheet, and add each approval to `APPROVED.md` marked `(agent)`.
- **Retry limits.** A still gets at most 2 new versions and a clip at most 1; after that, keep the best one and flag it. The video-credit budget is 200 unless the user gives one: check `flow accounts` before each clip batch, and don't start one that would go over.
- **Stop only for** `LOGIN_REQUIRED`, a spent budget, a `QUOTA` on drafts that `flow account refresh` doesn't fix, a CLI error whose hint doesn't resolve it, or flow hanging.
- **Log everything in `video-N/RUN-LOG.md`** as you go:
  - each gate you passed;
  - what you picked or rejected, and why;
  - credits spent;
  - a final "Check these" list.
- **Finish with** `make.py handoff` and `make.py status`, and end on the summary from `RUN-LOG.md`.

## Phases 0–1: plan

Every video starts with the `video-plan` skill. It writes `video-N/PLAN.md` and prints `PLAN.pdf`. `PLAN.md` holds:

- the concept, look, camera, cast, sheets, on-camera and end card paragraphs;
- the shot table: Shot, Time (timed to the voiceover), Voiceover, What we show.

Don't start phase 2 until the user has approved the plan.

- The plan's shot table is the story lock. After approval, add or cut shots only when the user asks. When they do, update `PLAN.md` and reprint the PDF. Then insert the new job in `scenes/stills-batch.json` at its place in story order, because the manifest order is the edit order.
- A shot's clip covers its Time in the plan and is never shorter.
- When the client's real voiceover arrives, retime it with `video-plan` before the clips are made.
- Mark shots that reuse an approved clip from an earlier video, and bring them in with `make.py reuse` instead of writing prompts.

## Phase 2: reference sheets

1. Run init. `<skill-dir>` is the folder holding this file, and `--style` is the style skill's name without `-video-production`:

   ```bash
   bash <skill-dir>/scripts/init-project.sh <client-folder> video-N --style photoreal
   ```

   - It adds `AGENTS.md` (naming the style skill), the sheet folders, `project.conf`, the manifests, `.flow/` and `scripts/make.py`. It never overwrites existing files.
   - After the skill is updated, refresh a video's copy of `make.py` with `--update-scripts`.
   - For a standalone video (its own `AGENTS.md` and brief inside the video folder), pass `.` as the video: `init-project.sh <client>/video-2 . --style animated`.
2. Take every recurring character, location and prop from the plan's Cast and Sheets paragraphs. Make only the character sheets the plan lists: never one for an extra (waiter, other diners, passers-by; see `video-plan` step 7). Make each character's base sheet first (`assets/characters/hero/hero-v1`); once it's approved, make each outfit sheet the plan lists as an edit of it (`make.py sheet assets/characters/hero/prompts/hero-sleep-v1.md --ref assets/characters/hero/hero-v1.jpg`), changing only the clothes, so the face can't drift. Every still of that character passes the outfit sheet for what they wear in that shot. Make only the environment and prop sheets the plan lists (see `video-plan` step 7): in animated and clay videos an environment sheet for each place with characters in two or more shots, holding the story items in it (the old pillow on the bed, the clock); in photoreal videos no environment sheets. Every style gets a prop sheet for the product, made from its real photos. CGI, macro and one-shot sets, and items that sit in a room, get no sheet of their own. Write each sheet prompt from the shared layout in `references/sheets/` (`character-sheet.md`, `place-sheet.md`, `product-sheet.md`) plus what the style skill's `characters.md`, `places.md` or `product.md` changes. Save it to `assets/characters/<name>/prompts/`, `assets/environments/<name>/prompts/` or `assets/props/<name>/prompts/`. Sheets always live under `assets/`, never loose in the client folder's root.
3. Generate them one or two at a time, because sheets need individual attention: run from the client folder, `video-N/scripts/make.py sheet assets/characters/rocco/prompts/rocco-v1.md` saves `assets/characters/rocco/rocco-v1.jpg`. Add `--ref <image>` for a reference (a new version made from an approved one).
4. **No scene still as a reference (user rule, video-13).** Every still is made from the sheets only: the place's environment sheet, the outfit sheet of each character in frame, and the product sheet. Never pass another scene still (an earlier shot, a "hero" still, an older version of the same shot) as an ingredient: it degrades the image and hands back its framing and poses. Light and colour stay consistent because each place's light is written the same way in every prompt: keep one Light line per place in the Environments table in `AGENTS.md` and copy it into each still of that place.
5. **Gate:** the user approves the sheets. Fill in the Characters, Environments, Props and Look sections of `AGENTS.md`.

## Phase 3: stills

1. Load the style skill's still reference and both `failure-locks.md` files. Write one prompt per shot to `scenes/scene-N/scene-Nx/prompts/scene-Nx-v1.md`.
2. Add one job per shot to `scenes/stills-batch.json`, one variant. Its ingredients are sheets only: the environment sheet (if the location has one), then the character and prop sheets. No scene stills.
3. **Show every still in the chat** (SendUserFile, display render) as soon as it's made, as well as in review-board.
4. Run `make.py stills` for the rest.
   - A job whose ingredient is a still that isn't made yet is held back and named in the output.
   - Finished outputs are skipped.
5. Run `make.py review stills` and read every sheet. Rerun any shot you'd reject as its next version (once), then report.
6. The user decides in review-board. Approvals go in `scenes/all/APPROVED.md` (file name and date). Rejected shots get the next version's job, replacing the old job in place, with only that shot's prompt changed. Then run `make.py stills 3b 7a`.
7. Once most stills are approved, run `make.py animatic` and send the user `edit/animatic.mp4`, laid over the voiceover if there is one, before any clip credits are spent.
8. **Gate:** every still is approved.

## Phase 4: 360p draft clips

1. Load the style skill's clip reference. Open each approved still first, then write its clip prompt from what is actually in it (who stands where, facing which way), not from the still's prompt. One prompt per shot, in `clips/clip-N/clip-Nx/prompts/clip-Nx-v1.md`.
2. Add jobs to `clips/clips-batch.json`:
   - `"resolution": "360p"` and `"timeout": 900`;
   - duration: the shortest Flow length (4, 6, 8 or 10 s) that holds the shot's Time in the plan;
   - ingredients: the approved still first, then a sheet only where the still can't hold the look by itself (below);
   - one variant.
   **Which sheets go with the still.** The still alone is the default: it already holds every face, outfit and label the clip needs. Add a sheet when the clip has to show something the still doesn't:
   - **A face the still hides.** A sheet character seen from behind, in profile or three-quarter, small in the distance, out of focus, cropped, or with the face covered by hair, hands or a cup. Pass that character's sheet for the outfit they wear in the shot (`hero-sleep`, not the base), even if the prompt doesn't ask them to turn: when they turn, or the camera moves round them, the model invents the face. Not for extras.
   - **Someone who enters** or comes into view during the clip: their sheet (but the still should normally show everyone; see the style skill).
   - **The product with printed text** in frame (a supplement bottle, a box, a label): the product sheet, so the label stays readable and spelled right as it moves or turns. Not for a softgel or anything else without print, unless its shape must hold.
   In the prompt, tag each one and say what it is for: "@image2 is Anna's sheet, a reference for her face, hair and lilac nightgown when she turns; @image3 is the Mysa bottle sheet, its label text stays exactly as printed. The sheets are references only: their panels and grey backgrounds never appear in the clip." Up to 7 ingredients.
3. Run `make.py clips` in the background. Every clip starts from its own approved still, so every clip can run in the first batch. Chaining is only for when the user asks for it, or when the plan splits one spoken line across clips.
   - **Chained clips** wait until the clip before them is approved and has its final. After `8a`'s final exists, `make.py lastframe 8a 8b` saves a frame 0.5 s before its end as `8b`'s opening still. Never take the frame from a 360p draft, and never redraw it with an image model.
   - List chained clips as "waiting on 8a" in every report.
4. Run `make.py review clips` (start, middle and end frames for each clip) and check them against the list. Rerun any you'd reject as the next version (once). For motion problems the frames can't show, ask the user to watch those clips.
5. Report every plan clip as made, failed (with the error) or not run (with the reason). `make.py clips` ends with this "Not made" list.
6. The user decides in review-board. Rejects become the next version, as with stills. Approvals go in `clips/all/APPROVED.md`.
7. **Gate:** every clip is approved.

## Phase 5: 1080p finals

1. Give the user the command, in its own code block. Name shots to make finals for only some of them, and `--into new-1080p` for finals of new or redone shots only:

   ```bash
   video-N/scripts/make.py finals
   ```

   - Every clip job needs an approved draft.
   - Each final reruns the approved prompt and ingredients as a native 720p generation, then upsamples it to 1080p.
   - The output goes to `clip-Nx/final/` and replaces the draft in `clips/all/`.
   - Reused clips that already have a 1080p file are skipped.
2. A final is a new generation and can differ from its draft. Run `make.py review finals`, which shows each draft beside its final, and check every one.
3. To redo a bad final:
   - In `clip-Nx/final/`, rename both the 720p file and its `-1080p` file to `rejected-<reason>-<name>`.
   - Put a new `"seed"` on that clip's job, because the same seed resumes the same result.
   - Give the user `make.py finals <shot>`.

## Phase 6: hand-off and captions

1. Run `make.py handoff`. `edit/clips/` gets the final clips numbered in story order, plus `ORDER.txt`.
2. The user edits: music, voiceover, timing.
3. Captions go into the FilmCraft edit with `captions-filmcraft`, after `filmcraft-pacing` when the edit is tightened, since cuts move the timing. Before any caption or other edit-stage deliverable, reread that section of the brief and quote it to the user.
4. Deliverables are named `<Brand>_<Concept>_<Variant>_<Ratio>.mp4` (`Mysa_Dose-to-Done_Hook1-Control_9x16.mp4`) and go in `video-N/deliverables/`.
5. Update the Videos table in `AGENTS.md`.

## make.py

Run it from anywhere as `video-N/scripts/make.py <command>`:

| Command | Does |
|---|---|
| `status` | Warns when `PLAN.pdf` is older than `PLAN.md`, and lists files outside the layout (stray manifests, logs, loose media). Then every shot in story order: newest still, clip, whether a 1080p exists, takes waiting for a pick |
| `stills [shots] [--dry-run]` | Stills batch (all shots, or only those named). Skips outputs that exist, holds back jobs waiting on an unmade still, syncs `scenes/all` |
| `clips [shots] [--dry-run]` | 360p clip batch. Ends with every manifest job that has no output and why (failed with its code, waiting, missing input, not named). Syncs `clips/all` |
| `finals [shots] [--into DIR] [--no-draft] [--dry-run]` | 720p + 1080p upsample on paid accounts. Skips finals that exist and reused clips. `--into` also copies the named shots' 1080p files to `clips/DIR/` |
| `sheet PROMPT [--ref IMG] [--seed N] [--dry-run]` | One 16:9 reference sheet from its prompt file, saved next to `prompts/` with the same name (`rocco-v2.md` → `rocco-v2.jpg`). Refuses to overwrite |
| `reuse SHOT SRC` | Copies an approved still or clip from another video in as the shot's next version (a 1080p clip also becomes its final), notes the source in `prompts/`, and points the manifest job at it |
| `lastframe FROM TO` | Opening still for a chained clip: the frame 0.5 s before the end of FROM's 1080p final, saved as TO's next still version |
| `pick SHOT TAKE [--clip]` | Copies a take up to the shot's version file (only for a job the user asked to run with more than one variant) |
| `review stills\|clips\|finals [shots]` | Contact sheets in `review/`, 10 stills or 4 clips per image |
| `animatic` | `edit/animatic.mp4`: clips where they exist, stills elsewhere, labelled, over `voiceover/recording.*` or the scratch read |
| `handoff` | Numbered final clips in `edit/clips/` |
| `sync` | Refreshes `scenes/all/` and `clips/all/` to the newest version of each shot (1080p once it exists) |

Manifest job shapes. Paths are absolute or relative to the manifest (from `scenes/`, a sheet is `../../assets/characters/milo/milo-v1.png`). The id is the output's file name without the extension:

```json
{"id": "scene-1a-v1", "kind": "image", "prompt_file": "/ABS/scenes/scene-1/scene-1a/prompts/scene-1a-v1.md",
 "aspect": "9:16", "ingredient": ["/ABS/assets/characters/milo/milo.png", "/ABS/assets/environments/street/street-v1.jpg"],
 "output": "/ABS/scenes/scene-1/scene-1a/scene-1a-v1.jpg"}
{"id": "clip-1a-v1", "kind": "video", "prompt_file": "/ABS/clips/clip-1/clip-1a/prompts/clip-1a-v1.md",
 "aspect": "9:16", "duration": 4, "resolution": "360p", "timeout": 900,
 "ingredient": ["/ABS/scenes/scene-1/scene-1a/scene-1a-v1.jpg", "/ABS/assets/characters/milo/milo.png"],
 "output": "/ABS/clips/clip-1/clip-1a/clip-1a-v1.mp4"}
```

Optional: `"seed"` to force a fresh job, since Flow resumes a job whose prompt, ingredients and seed match a lost one. `"variants": 2` only when the user asks for two takes of a shot. Reused jobs carry `"reused_from"` and are never generated.

## Project layout

```
<client>/
  AGENTS.md                 client rules, style, look, sheets, decisions
  brief/                    the client's files, untouched
  assets/                   reference sheets, shared by every video
    characters/<name>/<name>-v1.jpg + prompts/
    environments/<name>/...   props/<name>/...
  video-1/
    PLAN.md  PLAN.pdf  project.conf  scripts/make.py
    .flow/                    make.py's run files, flow batch state and logs (never beside the media)
    voiceover/                script.md, timing.md, scratch.wav, recording.* (the real read; a sung ad's chosen song take), slices/ (song-ad)
    song/                     a sung ad's lyric sheets (song-ad)
    scenes/stills-batch.json  scenes/scene-1/scene-1a/{scene-1a-v1.jpg, prompts/scene-1a-v1.md}   scene with several shots
                              scenes/scene-3/{scene-3-v1.jpg, prompts/scene-3-v1.md}             scene with one shot
    scenes/all/               newest still per shot + APPROVED.md
    clips/clips-batch.json    clips/clip-1/clip-1a/{clip-1a-v1.mp4, prompts/, final/}
                              clips/clip-3/{clip-3-v1.mp4, prompts/, final/}
    clips/all/                newest clip per shot, 1080p once it exists + APPROVED.md
    review/  edit/
    captions/                 the caption tool's words, plan and frames for this video
    deliverables/             <Brand>_<Concept>_<Variant>_<Ratio>.mp4
```

Nothing else goes in `scenes/` or `clips/`: `make.py status` lists anything that does. A standalone video has the same contents with no client level above it.

Shot ids are a scene number with no leading zero.

- A letter only ever means another shot in the same scene: a different beat with its own camera (the cat grabs the bread in `5a`, the police give chase in `5b`). It never means another try of the same shot. Tries are versions (`-v2`).
- A scene with one shot has no letter (`3`: `scenes/scene-3/scene-3-v1.jpg`). A scene with several gets one letter per shot and a folder each (`1a`, `1b`: `scenes/scene-1/scene-1a/scene-1a-v1.jpg`). Clips mirror scenes.
- Letters follow play order. A shot inserted between `8a` and `8b` becomes `8b`, and the old `8b` and every later letter move up one (files, prompts, manifest ids and the plan).
- If a one-shot scene gains a second shot, first move its files to `scene-3/scene-3a/` (and `clip-3/clip-3a/`), renaming `scene-3-` to `scene-3a-` in the files, prompts and manifests. `make.py` refuses a scene with both.

## Final check before each gate

- **Plan:** `video-plan`'s own checks passed, and the user approved `PLAN.pdf`.
- **Stills and clips:** you read the review sheets yourself, and fixed what you'd reject before reporting. `make.py status` shows no files outside the layout.
- **Finals:** each one was compared with its draft.
- **Hand-off:** it matches what the brief asks for, no more.
