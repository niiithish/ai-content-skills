---
name: talking-head-edit
description: The talking-head format of the house edit style in FilmCraft, as the client (Max, Aleo) approved it on video-5 and DCT-2190. One speaker on V1, a full-screen picture over almost every phrase, one-line template-6 captions at y 1360, still pushes at 2 %/s, 100/110% talking zoom steps, a glam-photo or three-picture-plus-word-card hook, and hooks 2–3 cloned from hook 1. It holds the exact numbers, both approved formats, all 12 client Loom rules and the edit scripts. Use with edit-style (load it first) for any edit, fix or export of a talking-head hook project (`edit/hook-N.fcproj`), any Aleo video, or a client Loom about one. talking-head-video-production makes the media it edits.
---

# Talking-head edit

**Load `edit-style` first.** It holds the principles, the working rules, the checks, the recipes and the new-machine list. This file adds the talking-head format the client approved twice: video-5 (2026-11-02) and DCT-2190 (2026-11-03, "he loved it").

| File | Load it for |
|---|---|
| [references/style.md](references/style.md) | Every edit: the exact numbers (speaker track, pictures, zoom, captions, audio, overlays) |
| [references/formats.md](references/formats.md) | A new edit: format A (podcast mic, glam hook, 🤯 title) and format B (straight to lens, three pictures plus a black word card, red CTA arrows) |
| [references/client-rules.md](references/client-rules.md) | Any feedback from Max: Looms 1–12, each with his words |
| [scripts/README.md](scripts/README.md) | Which script does what and what to set |

For Aleo, read `upwork-max/AGENTS.md` (the playbook) and the video's `AGENTS.md` first. Media comes from `talking-head-video-production`.

## What it looks like

- **One speaker** on V1/A1, sped up 1.1x (1.12x on DCT-2190), with dead air cut to a breath.
- **A full-screen picture (V2) over almost every phrase**, about one every 2–4 s. Her face shows only about a quarter of the time.
- **Captions:** template 6 (TikTok Sans SemiBold 58, black text on a white rounded box), one line, all at box centre y 1360. The hook title sits up top, never on her face.
- **Motion:** stills push at 2 %/s from their first frame to their last. Talking shots push slowly from the centre, with hard 100↔110% steps on cuts or caption starts.
- **Music** sits 18 dB under the voice (−26/−27 dB) with a 1 s fade.

## Order of a new edit

1. **Talking master.** The talking finals (with an ElevenLabs voice if the user asks) are sped up and gap-cut into `talking-head.fcproj` (`scripts/dct-2190/build_talking_head.py`). Joins are cut to about 0.25 s voice to voice, inner pauses to about 0.2 s, and loudness to −16 LUFS.
2. **Hook 1.** V1 is cut at every join of the master, so every hidden jump is a real cut. V2 gets one picture per phrase from the plan, with stills pushed (`dct-2190/build_hook1.py`, or `kit/build_draft.py` for format A).
3. **Captions.** Write the blocks by hand from the script's clauses, then run `fc_captions.py plan` and `build -t 6 --one-line`. Then run `caption_layout.py` and the format's title scripts (`formats.md`).
4. **Motion and audio.** Run `talk_motion.py`, re-push the stills at 2 %/s, then `add_music.py`.
5. **Check** (see `edit-style`), then hand hook 1 to the user. Their tweaks are the base from then on.
6. **Hooks 2–3.** Run `clone_hooks.py 2 3` (format B) or `make_hook.py 2 3` (format A). Then rerun music, titles and motion on them, and check them.
7. **Export only when asked.**
