---
name: talking-head-video-production
description: The talking-head layer for a long-form or short-form Google Flow ad where one person (a doctor, expert or creator) speaks the whole script to camera, with picture inserts over her. It adds the master still, the talking-clip prompt (one line per clip, or one take per hook, no repeated or added words, natural hands), the master assembly (all finals back to back, per-clip mp3s for an ElevenLabs voice change, isolated voice muxed back, 1.1x speed-up), then the edit in FilmCraft — pacing, one project per hook, scene stills in a box under the face and full-screen CGI/product clips, jump cuts only at a clause with a zoom change, dead air cut, inserts held to the next one, captions — on top of the shared video-production pipeline (layout, make.py, gates), which it loads with photoreal-video-production for the insert stills. Use when a video plan is a person talking to camera for most of the video with b-roll or still inserts (the Aleo video-3 method), when continuing such a project, or to add inserts to a talking-head edit. Not for a single line (simple-talking-head), remaking a UGC ad with a product in hand (ugc-ad-remake) or voiceover-over-scenes ads (photoreal-video-production).
---

# Talking-Head Video Production

One speaker carries the whole script to camera; inserts tell the story over her. Worked example: `~/Work/upwork/upwork-max/video-3` (Aleo, a dermatologist at a podcast mic, 3 hooks, ~3 min each).

**Load `video-production` first** (layout, `make.py`, gates, who runs which batch), and **`photoreal-video-production`** for the insert stills and CGI/product clips. Then `filmcraft`, `filmcraft-pacing` and `captions-filmcraft` for the edit. This skill adds only what is specific to a talking head. `<skill-dir>` is the folder holding this file.

| File | Load it for |
|---|---|
| [references/master-still.md](references/master-still.md) | Stage 1: the one still the speaker is generated from |
| [references/talking-clip.md](references/talking-clip.md) | Stage 2: every talking clip prompt |
| [references/master-assembly.md](references/master-assembly.md) | Stage 3: finals back to back, voice change, speed-up |
| [references/inserts.md](references/inserts.md) | Stage 5: what goes over her, how it is made, placed and credited |
| `edit-style` + `talking-head-edit` skills | **The edit (stages 5–7): load them for any FilmCraft work.** The approved house style, both formats, every client rule, change recipes and the edit scripts. It supersedes `edit-pipeline.md` |
| [references/edit-pipeline.md](references/edit-pipeline.md) | Legacy (video-3, 2026-10): box inserts, two-line captions, preview exports. Read only for history |

## The method

1. **Plan** (`video-plan`, `--on-camera` timing). The shot table has one row per spoken line (never a split sentence; long lines split at a clause into chained clips), plus the insert shots (stills, CGI, product) numbered from 201 so they never clash with talking clips. Each insert row says which words it covers.
2. **Master still** (`scenes/scene-1`): the speaker, the set and the framing in one frame, from an identity reference and a frame of the client's reference video. Every talking clip comes from it. Gate: the user approves it.
3. **Talking clips**: one per line, the master still as the only ingredient (a reference, not the first frame). All lines at 360p in one batch; then join them untrimmed so the user hears the transitions; then the user runs 1080p finals of all of them. **Each hook's opening is better as one take** (both its lines in one clip, `talking-clip.md`, "One take per hook"): two clips joined at a jump cut left pauses the user heard as dead air.
4. **Master file**: `build_talking_head.py` → `talking-head.fcproj` → `fc.py export` → per-clip mp3s for the user's ElevenLabs voice change → `mux_voice.sh` → `speed_up.sh` (1.1x). That file is the master; nothing after this regenerates her.
5. **Edit project**: the master on V1/A1 of `edit/<name>-full.fcproj`, tightened with `filmcraft-pacing` (calm), transcribed (`transcribe`) to `edit/words/`. Each hook is a copy cut to that hook plus the shared body (`hook-1.fcproj`, …).
6. **Inserts**: write `edit/build_inserts.py` from `templates/build_inserts.py`: an anchor (word or source second) and a picture for each line, box stills on V2 under her face, full-screen clips on V3. Make the stills the lines need (new ones from scratch, never redrawn from old stills).
7. **The edit: follow `edit-style` and its `talking-head-edit` sub-skill** (it supersedes the rest of this step). Legacy video-3 order, in `edit-pipeline.md`: thin/hold inserts, declutter and heal cuts, tighten the pauses left, punch zooms, captions (split, plan, build, snap, CTA, check). Before a full export, export the changed part as a short preview (`fc.py export … --start 0 --end 12`) and send it: the user judges pauses by ear. Export in full only when the user says so.

## Rules learned on Aleo video-3 (client and user)

- **The speaker never repeats or adds a word.** Each prompt says the line word for word, every word once, and names the join the model fumbled ("nothing between 'genes' and 'getting'"). Review by listening, not by frames.
- **Her hands move.** Natural gestures rising into frame beside the mic, never touching it: from calvin video-10's prompts (`upwork-calvin/video-10/clips/all`, clips 1a–12a).
- **One voice.** AI clips drift in timbre clip to clip; the user voice-changes every clip's mp3 in ElevenLabs, and the isolated voice goes back under the picture.
- **The edit never leaves FilmCraft.** ffmpeg makes source media (the master, insert stills, screen scrolls) and does analysis, never renders or joins an edit. Encode with `h264_vaapi` on `/dev/dri/renderD128`, not libx264.
- **No picture repeats** within one hook video (`build_inserts.py` stops on a repeat).
- **A picture changes only on a caption start or a V1 cut**, never mid-caption, and starts on the words it shows.
- **Jump cuts only at a new sentence or clause**, never inside one, no talking shot under 1.8 s, and each one gets a zoom change (100% ↔ 108% on her face).
- **Each insert holds until the next one comes in** (client Loom 3: an overlay that vanishes while she's still talking "isn't clean"); the face shows clean only where a `None` anchor says so.
- **Inserts follow the reference's pace** (one every ~3.4 s there); count it on the client's reference before placing.
- **No dead air.** A pause of 0.35 s or more left at a clause start reads as a gap ("too much bank sound" meant blank sound): cut it to about 0.2 s (`tighten_pauses.py`). Between a hook and the body keep about 0.37 s: 0.2 s ran straight on ("no gap at all").
- **No word goes uncaptioned.** A caption that ends in a pause must stay up over words spoken after it; a long pause inside one caption is cut and the caption split onto the cut (`split_pause.py`).
- **Captions** follow the script's clauses, at most 10 words, two-line rounded white boxes (`captions-filmcraft` template 6 on Aleo), and move to the top over the product clip.
- **Record each client decision** with its date in the project `AGENTS.md`; the scripts' docstrings say which rule they enforce.
