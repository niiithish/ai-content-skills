# The master file

The approved finals become one file of her speaking the whole script, in one voice, at the pace the edit starts from. Every hook is cut from it.

0. **One voice (before the timeline).** Flow makes each clip's voice on its own, so the clips never sound like one person. Fix it per clip:
   - `<skill-dir>/scripts/voice_change.py export video-N [--order 1a,1b,2] [--pick 3=v9] [--speakers jess=2,12,18]`: copies each talking clip's audio from its approved 1080p final to `audio/original/NN-clip-X.mp3` (play order, mono 320k; `--wav` for lossless) and makes the empty `audio/voice-changed/`.
     - **Which final:** the one `clips/PICKS.md` names (`- clip-7/final/clip-7-v2-s2-1080p.mp4`), else the newest (v3 < v3a < v3b, a `-s2` reseed after its take), unless `--pick`. Clips come from `clips/clips-batch.json`, else whichever `clips/*.json` manifest names the most shots; hook takes (h2, h3) count, silent `listen-*` clips don't.
     - **One loudness:** every file is set to −19 LUFS (`--lufs`), peaks under −1 dBFS (video-23: levels jumped clip to clip).
     - **Two or more speakers** (a podcast): each speaker gets a folder, `audio/original/<speaker>/`, found from each clip's master still (`scenes/master/jess-cu/…` → jess) or `--speakers`. One ElevenLabs voice per folder.
     - **The full audio:** `<speaker>/<speaker>-joined.mp3` (one speaker: `all-joined.mp3`), every clip back to back with 0.5 s between, to listen to or to voice-change in one go.
     - **Listen-for list:** it flags a repeated word, a cut-off start ("th- third"), a word held over 0.9 s and a pause over 0.7 s, from each final's words.json. Listen to those before the voice change (video-23's fumbled "third" was found only in the edit).
     - Then tell the user: "Copied N clips' original audio to audio/original/, ready for ElevenLabs" with the folder path and the listen-for list.
   - **The user** voice-changes either each clip file or the joined file (same voice per speaker) and saves the result in `audio/voice-changed/` under the same name and folder (any audio extension).
   - `voice_change.py apply video-N`: muxes the changed voice under each clip's picture as `final/clip-X-vK-1080p-vc.mp4` (picture copied, AAC 320k, padded or trimmed to the picture). A clip without its own changed file is cut out of its speaker's changed joined file (tested on video-23: in sync to the frame 152 s in). It names any clip still missing and flags a changed file whose length is off. `voice_change.py status video-N` shows where each clip stands.
   - A clip regenerated later: export again (it replaces the set) and voice-change just that file.
1. **Timeline.** `<skill-dir>/scripts/build_talking_head.py video-N` builds `edit/talking-head.fcproj`: every final back to back on V1/A1, untrimmed, in the manifest's order (or `--order 1a,1b,...`), from each shot's newest versioned `final/clip-Nx-vK-1080p.mp4` (never `clips/all`), or the clips and versions `voice_change.py` exported, and the `-vc.mp4` copy of each when it exists. It prints which clips are voice-changed.
2. **Export** with `filmcraft` (`fc.py export … -o deliverables/<Brand>_TalkingHead_Full_9x16.mp4`) when the user says so, and extract its mp3 if they want the whole voice in one file.
3. **Voice change of the whole file (old way, Aleo):** only when the clips weren't changed one by one in step 0. The user runs the full mp3 through ElevenLabs, then **mux** it under the picture: `<skill-dir>/scripts/mux_voice.sh deliverables/<…>_Full_9x16.mp4 "<isolated>.mp3"` → `…_isolated.mp4` (picture copied, AAC 320k). The two durations it prints must match (Aleo: 240.79 s both).
4. **Speed.** `<skill-dir>/scripts/speed_up.sh deliverables/<…>_Full_9x16.mp4 1.1` (or the `_isolated.mp4` from step 3) → `…_1.1x.mp4` (picture `setpts`, voice `atempo`, pitch kept, VAAPI). Flow's doctors talk slowly; 1.1x read as natural on Aleo (240.8 s → 218.9 s). Ask before going faster.

That last file is the **master**. From here on nothing regenerates her; the edit cuts this file.

## Then the edit project

- `edit/<brand>-full.fcproj`: the master on V1/A1, 1080×1920, 24 fps, 3 video tracks (V1 talking, V2 box stills, V3 full-screen clips; captions go on top), 1 audio. The talking head is the only audio: inserts go on video-only.
- `filmcraft-pacing` report, then `tighten --style calm` (dead air cut to a breath). Don't run `motion` on V1: `punch_cuts.py` does the zooms after the cut clean-up.
- Transcribe the master once (`transcribe` → `edit/words/<master>.words.json`): insert anchors are written in master source seconds and words, so they survive every re-cut.
- Hooks: `hook-N.fcproj` = that hook's lines + the shared body, cut from the full project (Aleo kept all three hooks back to back in `aleo-full.fcproj` and cut each hook from it). Each is delivered as its own full-length video.
