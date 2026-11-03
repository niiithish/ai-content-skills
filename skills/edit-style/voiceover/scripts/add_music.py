#!/usr/bin/env python3
"""Puts the music bed (music/Mystical Tension) on a new A2 "Music" track of edit/hook-1-v2.fcproj, from 0 to the end of the
voice, at a clip gain that sits it about 12 dB under the voice (measured with ebur128: music -12.7 LUFS, voice -18.2 LUFS),
with a 2 s fade-out. Run only while FilmCraft does not have the project open (it writes the file headless)."""
import shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_hook1_v2 import EDIT, FPS, PROJ, TPS, V, cli, seq

MUSIC = V / "music" / "Mystical Tension [JECXYadQD8U].m4a"
GAIN_DB = -17  # -12.7 - 17 = -29.7 LUFS, 11.5 dB under the voice
FADE = 2 * FPS


def add():
    s = seq()
    if len(s["audio"]) > 1 and any(t["items"] for t in s["audio"][1:]):
        sys.exit("A2+ already holds clips: music may already be on")
    end = max(c["endFrame"] for t in s["audio"] + s["video"] for c in t["items"])
    shutil.copy(PROJ, EDIT / "backup-2026-11-02" / "hook-1-v2-before-music.fcproj")
    item = cli([{"id": "file.import", "params": {"paths": [str(MUSIC)]}}, {"id": "file.save", "params": {}}])[0]["items"][0]
    r = cli([{"id": "sequence.addTracks", "params": {"video": 0, "audio": 1}},
             {"id": "timeline.place", "params": {"item": item, "track": "A2", "frame": 0, "sourceIn": 0,
                                                 "duration": end * TPS // FPS, "insert": False, "video": False}},
             {"id": "file.save", "params": {}}])[1]
    clip = (r.get("clips") or [r.get("clip")])[0]
    cli([{"id": "timeline.setTrack", "params": {"track": "A2", "name": "Music"}},
         {"id": "clip.audioGain", "params": {"clips": [clip], "mode": "set", "db": GAIN_DB}},
         {"id": "sequence.applyAudioTransition", "params": {"clip": clip, "frames": FADE, "edge": "out", "align": "end"}},
         {"id": "file.save", "params": {}}])
    print(f"music on A2 0-{end / FPS:.1f} s at {GAIN_DB} dB, {FADE / FPS:.0f} s fade-out")


if __name__ == "__main__":
    add()
