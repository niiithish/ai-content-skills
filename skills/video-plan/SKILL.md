---
name: video-plan
description: Turn a client's video brief into an approved production plan before anything is generated. Writes PLAN.md and a matching PLAN.pdf — the style, format and length, the character, environment and prop sheets to make, and a shot table with each voiceover line, what we show and a clip length timed from a real voiceover read (Cartesia scratch read or the client's recording). Fills in the visuals the brief leaves out, marked as suggestions. Works for any style (3D animation, claymation, photoreal, UGC) and then hands over to that style's skill. Use when a client sends a brief, script or message for a new AI video, when starting a video in an empty client folder, or when the user asks for a plan, treatment, shot list or storyboard. Not for a single prompt with no brief.
---

# Video Plan

The first step of every client video, whatever the style. Its output is `video-N/PLAN.md`, the file the style skill works from, and `video-N/PLAN.pdf`, printed from it for the user to read. The two never drift apart because the PDF is only ever printed from the Markdown: edit `PLAN.md`, then reprint.

Most wasted time happens when the story changes after generation has started, or a clip turns out shorter than its voiceover line. This plan settles both before anything is generated.

Run every command yourself: they take seconds. `<skill-dir>` is the folder holding this file.

## Steps

1. **Folders.** `python3 <skill-dir>/scripts/plan.py init <client-folder> video-1` creates `brief/`, `video-1/PLAN.md` and `video-1/voiceover/`, and never overwrites anything. If the brief came as a chat message, save it verbatim to `brief/message-YYYY-MM-DD.md`. Read every file in `brief/` in full, including the editing and caption sections.
2. **Brief table.** Fill in the Brief table in `PLAN.md`, quoting the brief next to every answer. Take particular care with voiceover, music, captions, deliverables and clip rules: these are what get delivered wrong. Mark anything the brief doesn't settle as **ASK**, and write the open questions short enough to paste into a message to the client.
3. **Style.** Choose it from the brief: its words, its reference videos, or the client's earlier videos in this folder. If the brief doesn't make it clear, ask the user before going on, because the style changes the sheets and the shots.
4. **Time the voiceover.**
   - Copy the script to `video-N/voiceover/script.md`, one spoken line per row, in story order, worded exactly as the client wrote it.
   - Run `plan.py voiceover <video-folder>`. It times the client's recording at `voiceover/recording.wav` (or `.mp3`/`.m4a`) with faster-whisper. Without one, it reads each line with Cartesia into `voiceover/scratch.wav`. The Cartesia key comes from `~/.config/cartesia/api_key`.
   - Match the read to the brief's tone: `CARTESIA_SPEED=0.9` in `video-N/project.conf` for slow storytelling. `plan.py voiceover <video-folder> --voices narrat` lists voices; set one with `CARTESIA_VOICE=<id>`.
   - The result is `voiceover/timing.md`: each line's in and out time, its slot (until the next line starts) and the clip length that covers the slot plus 1 s.
   - A brief with no voiceover (pure action, or characters talking on camera) skips this step: time each shot by its action instead.
5. **Story and shots.** Write the Story paragraph, then the shot table.
   - Each line's shots add up to at least its clip length. Never go shorter; a longer clip is only trimmed in the edit. A line marked `split` gets two or more shots.
   - Clips are 4, 6 or 8 s. Each shot is one visible beat.
   - Shot ids: a scene with one shot is just its number (`3`); a scene with several shots gets a letter each (`1a`, `1b`). Number scenes from 1 in story order. A letter means a different beat of the same line with its own camera ("the cat steals the bread and the police give chase": `5a` the grab, `5b` the chase), never another try of the same picture.
   - The Shots table is only what gets generated. Captions and music go in **Edit notes** at the bottom (captions with their shot and the client's exact wording), because the user adds them in the edit and they must never reach a prompt.
6. **Fill the gaps.** Where the brief only gives voiceover, decide what we show and set it in *italic* so the user can see it's a suggestion.
   - Show the line; don't just repeat it. "The cat stole the food from the police officer" becomes a scene someone can film: *The officer sits on the station bench, lunch box open beside him, turned away to wave at a colleague. The cat hops up and slides the sandwich out.*
   - Say who is where, which way they face and what they look at ("backs to us, staring up at the pie on the sill"), what they're doing and what changes by the end of the shot, so every shot can start from a still: characters already in place, nothing growing on screen, nobody walking in through a wall.
   - Make it move. Open each "What we show" with the camera in bold (**Wide.**, **Low angle.**, **Close-up.**, **Over his shoulder.**, **Her POV.**) and change it from the shot before. These are framings, not moves: clips are generated with a locked camera, so the motion comes from the characters. A POV shows what that character sees, so they aren't in it (at most a paw or a nose at the frame edge). Two shots of the same characters in the same spot need clearly different cameras (wide from behind them, then a close-up of one face), or the stills come out alike. Every shot has something happen: someone grabs, falls, turns, reacts. Characters just sitting and looking is a deliberate pause, never two shots in a row. Aim for something new on screen every 2–5 s.
   - Keep the cast and sets manageable, not tiny: reuse locations and characters before adding new ones (each is another sheet to make), but use enough of them for the story to travel. A story in one room with one character can't move.
   - Where the brief does say what to show, follow it exactly, including its order.
7. **Sheets to make.** List every recurring character, location and prop the shots need, with the details that must never drift and their relative scale ("the cat's back is at the officer's shin"). The style skill writes the sheet prompts from this list.
8. **Check and print.** Run the coverage check at the bottom of `PLAN.md`, then `plan.py pdf <video-folder>`. It rewrites the totals line under the shot table (shot count, voiceover and picture length, Flow credits for 360p drafts and 720p finals) and prints `PLAN.pdf` with your installed Chromium.
9. **Gate.** Give the user `PLAN.pdf` and a few lines on what you invented and what you're asking the client. Revise `PLAN.md` and reprint until they approve, then set **Status** to approved with the date. In an unattended run (the user is away), run the coverage check yourself, answer the open questions with the most conservative choice, mark them "(agent)", and approve the plan yourself.

After approval, add or cut shots only when the user asks, and reprint the PDF after each change. When the client's real voiceover arrives, save it as `voiceover/recording.*`, rerun `plan.py voiceover`, and lengthen any shot that no longer covers its line before its clip is made. On the real recording, In and Out are also the caption in/out times: copy them into Edit notes.

## Hand-over

Once the plan is approved, load the skill for its style. It starts from `PLAN.md` and doesn't repeat the intake.

| Style | Skill |
|---|---|
| 3D feature animation (DreamWorks, Pixar) | `animated-video-production` |
| Claymation or stop-motion | `clay-animation-video-prompt` |
| Photoreal scenes under a voiceover | `photoreal-still-prompt` for the stills; the sheet skills in photoreal mode |
| UGC: a person talking to camera | `ugc-ad-remake` to remake a winning ad, `simple-talking-head` for a single line |

The sheet skills (`character-generation`, `environment-generation`, `prop-generation`) follow the style: photoreal by default, animated mode for 3D animation.
