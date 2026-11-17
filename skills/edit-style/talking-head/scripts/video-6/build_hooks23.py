#!/usr/bin/env python3
"""video-6 (2026-11-14, user: "make the hook2 and hook3 ... the body should be 100% match"): hook-2 and hook-3 are copies of
the user's finished hook-1 with only the opening rebuilt. The body (and everything from hook-2's clip-4 lines on) keeps
hook-1's frames exactly: no clip after the opening moves.
  hook-2: frames 0-133 replaced (clip-2 "As a Korean dermatologist ... Today, I'm ranking them all"); 133-259 is hook-1's.
  hook-3: frames 0-259 replaced (clip-3 + clip-5). Its talking-head opening is 263 f; 4 single silent frames are dropped at
          its joins (T 127, 176, 242 and the tail 262) so it is 259 f like hook-1's (each pause stays >= 0.13 s).
Opening media from make_hook_media.py (1.242x voice-changed VO and green-screen take). Layout copies hook-1's opening:
her shot on V2 from "dermatologist" to the first insert with zoom_blur 8 f centred on that cut (cutout 2 f in), a swipe
5 f before it, inserts 202 / 201 / 203 / (hook-3) 205, cutout right, captions = template-11 copies of hook-1's.
FilmCraft must be closed. Usage: build_hooks23.py 2|3"""
import json, shutil, subprocess, sys
from pathlib import Path

N = int(sys.argv[1])
ED = Path(__file__).resolve().parent
ROOT = ED.parent
SRC, PROJ = ED / "hook-1.fcproj", ED / f"hook-{N}.fcproj"
TPS, FPS = 254016000000, 24
F = TPS // FPS
TM = ED / "talking-media"
VO = ROOT / f"audio/hook-{N}-vo/hook{N}_open_vc-1.242x.wav"
GREEN = ROOT / f"assets/cutout/drhan-greenscreen-hook{N}-1.242x.mp4"
INS = {k: ROOT / f"clips/clip-{k}/final/clip-{k}-v2-1080p.mp4" for k in (201, 202, 203, 205)}
RIGHT = [991.0, 1423.0]

if N == 2:
    END = 133                                   # opening replaced up to here
    TALK = [("clip-2", 0, 95, 0.25), ("clip-2", 95, 133, 4.542)]          # (media, from, to, source s) on V1/A2
    AUDIO = [(0, 133, 0.0)]                                                  # VO pieces (from, to, source s)
    C1 = 35                                                                  # first insert cut ("I've")
    CAPS = [("As a Korean", 0, 13), ("dermatologist", 13, 35), ("I’ve seen", 35, 46),
            ("every cellulite product", 46, 75), ("sold online", 75, 95), ("Today I’m ranking them all", 95, 133)]
    V2 = [(202, 35, 95), (201, 95, 133)]
    V3 = [(35, 133, 35 / FPS)]
else:
    END = 259
    TALK = [("clip-3", 0, 91, 0.208), ("clip-3", 91, 127, 4.542), ("clip-5", 127, 175, 0.208),
            ("clip-5", 175, 240, 2.5), ("clip-5", 240, 259, 5.542)]
    AUDIO = [(0, 127, 0.0), (127, 175, 128 / FPS), (175, 240, 177 / FPS), (240, 259, 243 / FPS)]
    C1 = 34
    CAPS = [("As a Korean", 0, 13), ("dermatologist", 13, 34), ("I have seen", 34, 48), ("every treatment", 48, 61),
            ("for cellulite there is", 61, 91), ("Today I’m ranking them all", 91, 127),
            ("Some of them I recommend", 127, 151), ("to my own patients", 151, 175),
            ("Some of them I consider", 175, 200), ("permanent damage", 200, 219), ("waiting to happen", 219, 240),
            ("Let us start", 240, 259)]
    V2 = [(202, 34, 91), (201, 91, 127), (203, 127, 175), (205, 200, 259)]
    V3 = [(34, 127, 34 / FPS), (127, 175, 128 / FPS), (200, 240, 177 / FPS + 25 / FPS), (240, 259, 243 / FPS)]
COPY0 = 13                                      # her shot copied on V2 from the "dermatologist" caption start


def cli(*a, inp=None):
    return subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a], capture_output=True, text=True, input=inp)


def seq():
    return json.loads(cli("inspect", "sequence").stdout)


def run(cmds, save=True):
    out = cli("run", "-", inp="".join(json.dumps(c) + "\n" for c in cmds + ([{"id": "file.save", "params": {}}] if save else [])))
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {[r for r in res if not r.get('ok')][:3]} {out.stderr[-800:]}")
    return [r.get("result") for r in res]


def clips(s):
    for k in ("video", "audio"):
        for i, t in enumerate(s[k]):
            for c in t["items"]:
                yield k, i, t, c


if PROJ.exists():
    bk = ED / "backup-2026-11-14-hooks23"; bk.mkdir(exist_ok=True); shutil.copy2(PROJ, bk / PROJ.name)
shutil.copy2(SRC, PROJ)
s = seq()
before = {(k, i, c["clip"]): (c["startFrame"], c["durationFrames"], c["sourceIn"]) for k, i, t, c in clips(s)
          if c["startFrame"] >= END}

# 1) media
paths = [TM / f"{TALK[0][0]}-voice-1.242x.mp4"] + ([TM / "clip-5-voice-1.242x.mp4"] if N == 3 else []) + [VO, GREEN] + \
        [INS[k] for k, *_ in V2]
r = run([{"id": "file.import", "params": {"paths": [str(p) for p in paths]}}])[0]
item = dict(zip([p.name for p in paths], r["items"]))
swipe = next(c["item"] for k, i, t, c in clips(s) if c["name"] == "Cartoon Swipe.mp3")
tmpl = next(c["clip"] for c in s["video"][4]["items"] if c["startFrame"] == 0)

# 2) caption copies on a new track, far past the end
far = s["durationFrames"] + 50
run([{"id": "timeline.move", "params": {"moves": [{"clip": tmpl, "track": "new", "time": {"frame": far}}],
                                         "insert": False, "copy": True}}])
s = seq(); tmp = s["video"][-1]["id"]
run([{"id": "timeline.move", "params": {"moves": [{"clip": tmpl, "track": tmp, "time": {"frame": far + 60 * j}}],
                                         "insert": False, "copy": True}} for j in range(1, len(CAPS))])
s = seq()
cap = sorted(s["video"][-1]["items"], key=lambda c: c["startFrame"])
assert len(cap) == len(CAPS)
cmds = []
for c, (txt, a, b) in zip(cap, CAPS):
    cmds += [{"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular",
                                                "deltaFrames": (b - a) - c["durationFrames"], "linked": False}},
             {"id": "graphics.setText", "params": {"clip": c["clip"], "layer": 1, "text": txt}}]
run(cmds)
lst = run([{"id": "graphics.list", "params": {"clip": c["clip"]}} for c in cap], save=False)
cmds = []
for c, g in zip(cap, lst):
    tb = next(l for l in g["layers"] if l["kind"] == "text")["localBounds"]
    cmds.append({"id": "graphics.set", "params": {"clip": c["clip"], "layer": 0,
                                                   "props": {"size": [round(tb[2] - tb[0] + 13.6, 1), 80.6]}}})
run(cmds)

# 3) clear the opening (not the music); hook-2 razors hook-1's A1 voice at 133 first
s = seq()
if N == 2:
    run([{"id": "timeline.razor", "params": {"time": END * F, "track": "A1"}}]); s = seq()
music = s["audio"][2]["id"]
dead = [c["clip"] for k, i, t, c in clips(s) if t["id"] != music and t["id"] != tmp and c["startFrame"] < END]
assert all(c["endFrame"] <= END for k, i, t, c in clips(s) if c["clip"] in dead), "a clip crosses the opening's end"
run([{"id": "timeline.delete", "params": {"clips": dead, "ripple": False}}])

# 4) place the new opening
P = lambda **k: {"id": "timeline.place", "params": dict(insert=False, **k)}
cmds = []
for m, a, b, si in TALK:
    it = item[f"{m}-voice-1.242x.mp4"]
    cmds += [P(item=it, track="V1", frame=a, sourceIn={"seconds": si}, duration=(b - a) * F, video=True, audio=False),
             P(item=it, track="A2", frame=a, sourceIn={"seconds": si}, duration=(b - a) * F, video=False, audio=True)]
for a, b, si in AUDIO:
    cmds.append(P(item=item[VO.name], track="A1", frame=a, sourceIn={"seconds": si}, duration=(b - a) * F, video=False, audio=True))
t0 = next(t for t in TALK if t[1] <= COPY0 < t[2])
cmds.append(P(item=item[f"{t0[0]}-voice-1.242x.mp4"], track="V2", frame=COPY0, sourceIn={"seconds": t0[3] + (COPY0 - t0[1]) / FPS},
              duration=(C1 - COPY0) * F, video=True, audio=False))
for k, a, b in V2:
    cmds.append(P(item=item[INS[k].name], track="V2", frame=a, sourceIn={"seconds": 1.0}, duration=(b - a) * F, video=True, audio=False))
for a, b, si in V3:
    cmds.append(P(item=item[GREEN.name], track="V3", frame=a, sourceIn={"seconds": si}, duration=(b - a) * F, video=True, audio=False))
# 2026-11-15 (client Loom 4): no swoosh except on the board products, so no swipe on the first insert
run(cmds)

# 5) motion, cutout look, blur, swipe gain, captions onto V5
s = seq()
cmds = []
for c in s["video"][0]["items"]:
    if c["startFrame"] < END and c["name"].split("-voice")[0] in {m for m, *_ in TALK}:
        x, y = c["startFrame"], c["endFrame"]
        for f, val in ((x, 100.0), (y - 1, 100.0 + 3.0 * (y - x) / 72)):
            cmds.append({"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "scale",
                                                              "value": round(val, 2), "keyframe": True, "time": f * F}})
v3 = s["video"][2]["items"]
new3 = [c["clip"] for c in v3 if c["startFrame"] < END]
ref = next(c for c in v3 if c["startFrame"] >= END and c["name"].startswith("drhan-greenscreen-hook1"))
cmds += [{"id": "timeline.select", "params": {"clips": [ref["clip"]], "add": False, "toggle": False, "linked": False}},
         {"id": "edit.copy", "params": {}},
         {"id": "edit.pasteAttributes", "params": {"clips": new3, "timeRemapping": False, "volume": False}}]
cmds += [{"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "position", "value": RIGHT}} for c in new3]
v2 = {c["startFrame"]: c for c in s["video"][1]["items"]}
cmds += [{"id": "sequence.applyVideoTransition", "params": {"clip": v2[COPY0]["clip"], "effect": "zoom_blur", "frames": 8,
                                                           "edge": "out", "align": "center"}},
         {"id": "sequence.applyVideoTransition", "params": {"clip": next(c for c in v3 if c["startFrame"] == C1)["clip"],
                                                           "effect": "zoom_blur", "frames": 2, "edge": "in", "align": "start"}}]

cap = sorted(s["video"][-1]["items"], key=lambda c: c["startFrame"])
cmds.append({"id": "timeline.move", "params": {"moves": [{"clip": c["clip"], "track": s["video"][4]["id"], "time": {"frame": a}}
                                                         for c, (txt, a, b) in zip(cap, CAPS)], "insert": False}})
run(cmds)
s = seq()
assert not s["video"][-1]["items"]
run([{"id": "sequence.deleteTrack", "params": {"track": s["video"][-1]["id"]}}])

# 6) checks: nothing from END on moved; V1 has no gap; length unchanged
s = seq()
after = {(k, i, c["clip"]): (c["startFrame"], c["durationFrames"], c["sourceIn"]) for k, i, t, c in clips(s)
         if c["startFrame"] >= END}
moved = [k for k in before if after.get(k) != before[k]]
v1 = sorted(s["video"][0]["items"], key=lambda c: c["startFrame"])
gaps = [(a["endFrame"], b["startFrame"]) for a, b in zip(v1, v1[1:]) if a["endFrame"] != b["startFrame"]]
print(f"hook-{N}: {s['durationFrames']} f; body clips moved/changed: {moved[:8]} ({len(moved)}); V1 gaps {gaps}; "
      f"new captions {len(CAPS)}; first insert at {C1}")
