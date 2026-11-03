# The master file

The approved finals become one file of her speaking the whole script, in one voice, at the pace the edit starts from. Every hook is cut from it.

1. **Timeline.** `<skill-dir>/scripts/build_talking_head.py video-N --mp3` builds `edit/talking-head.fcproj`: every final back to back on V1/A1, untrimmed, in the manifest's order (or `--order 1a,1b,...`), from each shot's newest versioned `final/clip-Nx-vK-1080p.mp4` (never `clips/all`). `--mp3` also writes `audio/NN-clip-X.mp3` (320k, play order).
2. **Export** with `filmcraft` (`fc.py export … -o deliverables/<Brand>_TalkingHead_Full_9x16.mp4`) when the user says so, and extract its mp3 if they want the whole voice in one file.
3. **Voice change (the user).** The user runs the per-clip mp3s (or the full mp3) through ElevenLabs voice changer / voice isolation so every clip sounds like one person, and gives back the result.
4. **Mux** it under the picture: `<skill-dir>/scripts/mux_voice.sh deliverables/<…>_Full_9x16.mp4 "<isolated>.mp3"` → `…_isolated.mp4` (picture copied, AAC 320k). The two durations it prints must match (Aleo: 240.79 s both).
5. **Speed.** `<skill-dir>/scripts/speed_up.sh deliverables/<…>_isolated.mp4 1.1` → `…_isolated_1.1x.mp4` (picture `setpts`, voice `atempo`, pitch kept, VAAPI). Flow's doctors talk slowly; 1.1x read as natural on Aleo (240.8 s → 218.9 s). Ask before going faster.

That last file is the **master**. From here on nothing regenerates her; the edit cuts this file.

## Then the edit project

- `edit/<brand>-full.fcproj`: the master on V1/A1, 1080×1920, 24 fps, 3 video tracks (V1 talking, V2 box stills, V3 full-screen clips; captions go on top), 1 audio. The talking head is the only audio: inserts go on video-only.
- `filmcraft-pacing` report, then `tighten --style calm` (dead air cut to a breath). Don't run `motion` on V1: `punch_cuts.py` does the zooms after the cut clean-up.
- Transcribe the master once (`transcribe` → `edit/words/<master>.words.json`): insert anchors are written in master source seconds and words, so they survive every re-cut.
- Hooks: `hook-N.fcproj` = that hook's lines + the shared body, cut from the full project (Aleo kept all three hooks back to back in `aleo-full.fcproj` and cut each hook from it). Each is delivered as its own full-length video.
