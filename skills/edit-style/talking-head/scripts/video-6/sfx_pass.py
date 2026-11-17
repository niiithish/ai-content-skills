#!/usr/bin/env python3
"""video-6 (2026-11-14, user: copy the inspo's sound effects, its "camera click + sun" flash and its transitions, and use
the closest music, from Gemini's breakdown `sounds-effect-analysis/sound-effects-and-transitions-breakdown.md`).

Measured on the inspo (voice-removed `asdasd.mp3` + reference.mp4, not taken from Gemini's table on trust):
  - name cards (LASERS, ...): the new shot pushes in from the right in ~3 frames; a short whoosh starts 0.2 s before the cut
    (library match by spectrogram: Fast Woosh 03), peak about 1 dB under the voice.
  - tier board shown: a hard cut with a swipe on the cut (Cartoon Swipe), about 6 dB under the voice.
  - story pivots ("I have been a dermatologist", "Now the only thing", "Korean dermatology takes..."): a warm light leak
    across the cut (~8 frames, peak on the cut) with a camera shutter (Camera Click) starting 0.25 s before, ~4 dB under.
  - first switch to an insert (the push-in blur, frame 40): the swipe starting 0.2 s before the cut.
  - music: upbeat funk (Gemini's pick, checked by ear-free measures only): funky-strut-soul-music.mp3, 128 bpm. It is 163 s,
    so it plays twice: bar line 0.40 s -> 152.33 s, then again from 0.40 s (beat-continuous), the user's two volume levels
    and the -19 dB clip gain kept, offset by the loudness difference to the Frank Ocean track (-13.2 vs -11.5 LUFS).
Our moments mapped onto them are in EVENTS. SFX go on a new audio track named "SFX". Nothing else moves.
Usage: sfx_pass.py [PROJECT]   (FilmCraft closed; back up first)"""
import json, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / "hook-1.fcproj")
TPS, FPS = 254016000000, 24
F = TPS // FPS
LIB = Path.home() / ("Music/sounds-effects")
SFX = {  # file, clip gain dB, start offset in frames from the cut
    "card":  (LIB / "Whooshes, Risers and Transitions/Fast Woosh 03.mp3", 5.0, -5),
    "board": (LIB / "Whooshes, Risers and Transitions/Cartoon Swipe.mp3", -2.0, 1),
    "first": (LIB / "Whooshes, Risers and Transitions/Cartoon Swipe.mp3", -2.0, -5),
    "flash": (LIB / "Foley/Camera Click.mp3", 0.0, -6),
}
MUSIC = Path.home() / ("Music/music-for-meta-ads/funky-strut-soul-music.mp3")
M_IN, M_SEAM_SRC = 0.40, 152.33          # first downbeat, a bar line before the outro (128 bpm grid)
M_GAIN = -19.0 + (-13.2 - -11.5)         # same loudness as the Frank Ocean bed it replaces
LEAK = {"color": [1.0, 0.62, 0.22, 1.0], "amount": 75.0}   # 0-100 scale
PUSH_FRAMES, LEAK_FRAMES = 3, 8

# frame -> kind (hook-1, 2026-11-14 timeline)
EVENTS = {
    40: "first",
    299: "flash",    # "I've been a dermatologist" (the inspo's flash is on the same line, 11.8 s)
    3559: "flash",   # "Now, the one exception" (inspo: "Now the only thing", 144.0 s)
    3940: "flash",   # "This one takes..." pivot (inspo: "Korean dermatology takes the opposite approach", 160.8 s)
    574: "card", 1073: "card", 1555: "card", 2107: "card", 2705: "card", 3154: "card",
    4350: "card",    # "Aleo has eucalyptus" (inspo whips into "Koriderm has Centella", 178.8 s)
    1041: "board", 1459: "board", 2051: "board", 2675: "board", 3108: "board", 3540: "board", 3804: "board",
    5137: "board", 5636: "board",
}


def cli(*a, inp=None):
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a], capture_output=True, text=True,
                         input=inp)
    return out


def seq():
    return json.loads(cli("inspect", "sequence").stdout)


def run(cmds):
    out = cli("run", "-", inp="".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {[r for r in res if not r.get('ok')]} {out.stderr[-1500:]}")
    return res[:-1]


s = seq()
end = s["durationFrames"]
v2 = {c["startFrame"]: c for c in s["video"][1]["items"]}
v4 = {c["startFrame"]: c for c in s["video"][3]["items"]}
music = s["audio"][2]["items"]
assert len(music) == 2 and "Pink + White" in music[0]["name"], "music track is not the Frank Ocean pair any more"
lv = [next(e["params"]["level"]["value"] for e in c["effects"] if e["effect"] == "volume") for c in music]
lv = [float(str(x).split("(")[1].rstrip(")")) if isinstance(x, str) else x for x in lv]

# 1) transitions (video)
tr = []
for at, kind in EVENTS.items():
    if kind == "card":
        tr.append({"id": "sequence.applyVideoTransition", "params": {
            "clip": v2[at]["clip"], "effect": "push", "frames": PUSH_FRAMES, "edge": "in", "align": "start",
            "params": {"direction": "From East", "motion_blur": 0.0}}})
        if at in v4:
            tr.append({"id": "sequence.applyVideoTransition", "params": {
                "clip": v4[at]["clip"], "effect": "push", "frames": PUSH_FRAMES, "edge": "in", "align": "start",
                "params": {"direction": "From East", "motion_blur": 0.0}}})
    elif kind == "flash":
        tr.append({"id": "sequence.applyVideoTransition", "params": {
            "clip": v2[at]["clip"], "effect": "light_leak", "frames": LEAK_FRAMES, "edge": "in",
            "align": "center" if any(c["endFrame"] == at for c in s["video"][1]["items"]) else "start",
            "params": LEAK}})
run(tr)

# 2) music swap + SFX track
imp = run([{"id": "file.import", "params": {"paths": [str(MUSIC)] + sorted({str(v[0]) for v in SFX.values()})}}])[0]
items = {Path(p).name: i for p, i in zip([str(MUSIC)] + sorted({str(v[0]) for v in SFX.values()}),
                                          imp["result"]["items"] if "result" in imp else imp["items"])}
run([{"id": "timeline.delete", "params": {"clips": [c["clip"] for c in music], "ripple": False}},
     {"id": "sequence.addTracks", "params": {"video": 0, "audio": 1, "audioAfter": "A3"}}])
s = seq()
a3, a4 = s["audio"][2]["id"], s["audio"][3]["id"]
run([{"id": "timeline.setTrack", "params": {"track": a4, "name": "SFX"}}])
seam = round((M_SEAM_SRC - M_IN) * FPS)
pl = [{"id": "timeline.place", "params": {"item": items[MUSIC.name], "track": a3, "frame": 0,
                                         "sourceIn": {"seconds": M_IN}, "duration": seam * F, "insert": False,
                                         "video": False, "audio": True}},
      {"id": "timeline.place", "params": {"item": items[MUSIC.name], "track": a3, "frame": seam,
                                         "sourceIn": {"seconds": M_IN}, "duration": (end - seam) * F, "insert": False,
                                         "video": False, "audio": True}}]
meta = [("music", 0), ("music", 1)]
for at, kind in sorted(EVENTS.items()):
    path, gain, off = SFX[kind]
    pl.append({"id": "timeline.place", "params": {"item": items[path.name], "track": a4, "frame": max(0, at + off),
                                                 "insert": False, "video": False, "audio": True}})
    meta.append(("sfx", gain))
res = run(pl)
fx = []
for r, m in zip(res, meta):
    clip = (r.get("result") or r)["clips"][0]
    if m[0] == "music":
        fx += [{"id": "clip.audioGain", "params": {"clips": [clip], "mode": "set", "db": round(M_GAIN, 2)}},
               {"id": "effects.setParam", "params": {"clip": clip, "effect": "volume", "param": "level",
                                                     "value": lv[m[1]]}}]
        last = clip
    else:
        fx.append({"id": "clip.audioGain", "params": {"clips": [clip], "mode": "set", "db": m[1]}})
fx.append({"id": "sequence.applyAudioTransition", "params": {"clip": last, "edge": "out", "frames": FPS}})
run(fx)
print(f"{sum(k == 'card' for k in EVENTS.values())} push-ins, {sum(k == 'flash' for k in EVENTS.values())} light leaks, "
      f"{len(EVENTS)} SFX on 'SFX'; music = {MUSIC.name}, seam at frame {seam}")
