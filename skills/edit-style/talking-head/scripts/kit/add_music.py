#!/usr/bin/env python3
"""Background music on A2 for the whole hook (user 2026-10-29: Frank Ocean "Pink + White" instrumental, YouTube N9GXZD8y-bg).
From the track's start, cut at the hook's end with a 1 s fade out; gain set so it sits about 18 dB under the voice (user 2026-10-29: -21 dB was "too loud")
(voice -22.2 LUFS, track -13.4 LUFS). Replaces any music already on A2, so it is safe to rerun (after make_hook.py too).
Usage: add_music.py hook-1.fcproj [...]"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSIC = ROOT / "assets/music/Frank Ocean - Pink + White(instrumental) [N9GXZD8y-bg].m4a"
GAIN_DB = -26.0   # DCT-2190: voice -21.1 LUFS (video-5 -22.2), keeps the same ~18 dB gap
FADE = 24   # frames
TPS, FPS = 254016000000, 24


def cli(proj, cmds):
    f = proj.with_suffix(".music.jsonl"); f.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink(); rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in rs if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"{proj.name}: {bad or out.stderr[-1500:]}")
    return [r.get("result") for r in rs]


def seq(proj):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


for a in [a for a in sys.argv[1:] if a.endswith(".fcproj")]:
    proj = Path(a).resolve(); s = seq(proj)
    end = max(c["endFrame"] for t in s["video"][:1] for c in t["items"])
    pre = []
    if len(s["audio"]) < 2:
        pre.append({"id": "sequence.addTracks", "params": {"video": 0, "audio": 1}})
    else:
        old = [c["clip"] for c in s["audio"][1]["items"] if c["name"] == MUSIC.name]
        if old:
            pre.append({"id": "edit.clear", "params": {"clips": old}})
    item = cli(proj, pre + [{"id": "file.import", "params": {"paths": [str(MUSIC)]}}, {"id": "file.save", "params": {}}])[-2]["items"][0]
    clip = cli(proj, [{"id": "timeline.place", "params": {"item": item, "track": "A2", "frame": 0, "insert": False,
                                                          "duration": end * TPS // FPS, "video": False, "audio": True}},
                      {"id": "file.save", "params": {}}])[0]["clips"][0]
    cli(proj, [{"id": "clip.audioGain", "params": {"clips": [clip], "mode": "set", "db": GAIN_DB}},
               {"id": "sequence.applyAudioTransition", "params": {"clip": clip, "edge": "out", "frames": FADE}},
               {"id": "file.save", "params": {}}])
    m = [c for c in seq(proj)["audio"][1]["items"]]
    print(f"{proj.name}: music A2 {m[0]['startFrame']}-{m[0]['endFrame']} f of {end}, gain {m[0]['gainDb']} dB")
