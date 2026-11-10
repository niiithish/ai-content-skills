#!/usr/bin/env python3
"""video-23 hooks 2 and 3 (user 2026-11-10: "can we do hook2 and hook3"): clones of the user's finished hook-1.fcproj.
Only the opening changes (edit-style principle 11): hook 1's line 1 (frames 0-206 on V1, V2, V3, A1) is removed, the
body moves as one block by the length difference, the music is lengthened or shortened to the new end (fade kept),
and the new hook line is laid in with hook 1's opening pattern: talking 100 %, the 201 screen on "third generation
fix", talking 112 %, then the Jess split under the last sentence. Voice from the guest ElevenLabs track (1.1x), video
from media/talk-110/clip-hN-110.mp4, pieces from guest-talking.cuts.json. Captions for the opening are added after,
by add_hook_captions (fc_captions words + plan on the new project).
Usage: build_hooks23.py 2|3"""
import copy, json, subprocess, sys
from pathlib import Path

EDIT = Path(__file__).resolve().parent
TPS, FPS, SPEED = 254016000000, 24, 1.1
T = TPS // FPS
L1_END = 206                       # hook 1's line 2 starts here
HOOK = sys.argv[1]
PROJ = EDIT / f"hook-{HOOK}.fcproj"
CID = f"h{HOOK}"
VID = EDIT / f"media/talk-110/clip-{CID}-110.mp4"
WORDS = json.load(open(EDIT / "media/voice/guest-talking-11labs.words.json"))
SHOTS = {"2": [("honestly", ("talk", 100)), ("third", ("ins", "201-focus.png")), ("does for", ("talk", 112)),
               ("id been", ("split", "clip-listen-jess-v2-1080p.mp4", 0.0))],
         "3": [("i used", ("talk", 100)), ("third", ("ins", "201-focus.png")), ("does for", ("talk", 112)),
               ("and i stopped", ("split", "clip-listen-jess-v2-1080p.mp4", 0.0))]}[HOOK]
norm = lambda w: "".join(ch for ch in w.lower() if ch.isalnum())


def cli(proj, cmds):
    f = EDIT / ".hooks23.jsonl"
    f.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f), "--save"],
                         capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    f.unlink()
    return [r.get("result") for r in res]


def main():
    if subprocess.run(["pgrep", "-x", "filmcraft"], capture_output=True).returncode == 0:
        sys.exit("FilmCraft is open: save and quit it first")
    if PROJ.exists() and "--replace" not in sys.argv:
        sys.exit(f"{PROJ.name} exists: pass --replace")
    cuts = [p for p in json.load(open(EDIT / "guest-talking.cuts.json")) if p[0] == CID]
    ps = [(a / SPEED, b / SPEED, at / SPEED) for _, a, b, at in cuts]
    a0 = ps[0][2]
    b0 = ps[-1][2] + ps[-1][1] - ps[-1][0]
    n = round((b0 - a0) * FPS)                 # opening length in frames
    delta = n - L1_END
    ws = [w for w in WORDS if a0 - 0.1 <= w["start"] / SPEED < b0 - 0.1]
    # V1 piece edges (frames from 0) and shot starts: 3 frames before the word (hook 1's captions lead its word times
    # by about 3 frames), onto a piece edge when within 3 frames of one (no slivers of V1)
    pieces = [(round((at - a0) * FPS), round((at + so - si - a0) * FPS), si) for si, so, at in ps]
    edges = sorted({p[0] for p in pieces} | {p[1] for p in pieces})
    starts, i = [0], 0
    nw = [norm(w["word"]) for w in ws]
    for k, (key, _) in enumerate(SHOTS):
        if k == 0:
            continue
        kk = key.replace(" ", "")
        i = next(j for j in range(i, len(nw)) if "".join(nw[j:j + 4]).startswith(kk))
        f = round((ws[i]["start"] / SPEED - a0) * FPS) - 3
        near = [e for e in edges if abs(e - f) <= 3 and 0 < e < n]
        starts.append(min(near, key=lambda e: abs(e - f)) if near else f)
    over = [a for a in sys.argv if a.startswith("--starts=")]
    if over:                                   # shot starts taken from the caption plan (pictures change on caption starts)
        starts = [int(x) for x in over[0].split("=", 1)[1].split(",")]
        assert len(starts) == len(SHOTS) and starts[0] == 0
    bounds = list(zip(starts, starts[1:] + [n]))
    assert all(e - s >= 8 for s, e in bounds), bounds

    # --- clone hook 1 and shift the body
    d = json.load(open(EDIT / "hook-1.fcproj"))
    d["project"]["name"] = d["project"]["root"]["name"] = f"hook-{HOOK}"
    items = d["project"]["items"]
    sq = next(i for i in items.values() if "Sequence" in i["kind"])
    sq["name"] = f"hook-{HOOK}"
    s = sq["kind"]["Sequence"]
    music = s["audio_tracks"][1]["items"]
    assert len(s["audio_tracks"]) == 2 and len(music) == 1
    for tr in s["video_tracks"] + s["audio_tracks"][:1]:
        tr["items"] = [c for c in tr["items"] if c["start"] >= L1_END * T]
        for c in tr["items"]:
            c["start"] += delta * T
    m = music[0]
    m["duration"] += delta * T
    for kf in m["effects"][0]["params"]["level"]["keyframes"]:
        kf["time"] += delta * T
    PROJ.write_text(json.dumps(d, separators=(",", ":"), ensure_ascii=False))
    byname = {v["name"]: int(k) for k, v in items.items() if "Media" in v["kind"]}

    # --- the new opening
    r = cli(PROJ, [{"id": "file.import", "params": {"paths": [str(VID)]}}])
    vid = r[0]["items"][0]
    voice = byname["guest-talking-11labs-110.mp3"]
    place, meta = [], []
    place.append({"id": "timeline.place", "params": {"item": voice, "track": "V1", "audioTrack": "A1", "frame": 0,
                                                     "sourceIn": round(a0 * FPS) * T, "duration": n * T, "insert": False,
                                                     "video": False, "audio": True}})
    meta.append(("audio",))
    shot_of = lambda f: max(k for k, s_ in enumerate(starts) if s_ <= f)
    last, alt = None, False
    for f0, f1, si in pieces:
        f1 = min(f1, n)
        sin = round(si * FPS)
        for x, y in zip([f0] + [s_ for s_ in starts if f0 < s_ < f1], [s_ for s_ in starts if f0 < s_ < f1] + [f1]):
            k = shot_of(x)
            alt = (not alt) if k == last else False
            last = k
            place.append({"id": "timeline.place", "params": {"item": vid, "track": "V1", "frame": x,
                                                             "sourceIn": (sin + x - f0) * T, "duration": (y - x) * T,
                                                             "insert": False, "video": True, "audio": False}})
            meta.append(("v1", SHOTS[k][1], x, y, alt))
    for (st, en), (key, what) in zip(bounds, SHOTS):
        if what[0] == "ins":
            place.append({"id": "timeline.place", "params": {"item": byname[what[1]], "track": "V2", "frame": st,
                                                             "duration": (en - st) * T, "insert": False,
                                                             "video": True, "audio": False}})
            meta.append(("ins", st, en))
        elif what[0] == "split":
            place.append({"id": "timeline.place", "params": {"item": byname[what[1]], "track": "V2", "frame": st,
                                                             "sourceIn": round(what[2] * FPS) * T, "duration": (en - st) * T,
                                                             "insert": False, "video": True, "audio": False}})
            meta.append(("listen",))
    res = cli(PROJ, place)
    fx, gain = [], []

    def half(clip, top):
        fx.extend([{"id": "effects.apply", "params": {"clips": [clip], "effect": "crop"}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": 3, "param": "top", "value": 10}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": 3, "param": "bottom", "value": 40}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "position",
                                                         "value": [540, 768 if top else 1728]}}])

    def push(clip, v0, v1, x, y):
        fx.extend({"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale",
                                                        "value": round(v, 2), "keyframe": True, "time": f * T}}
                  for v, f in ((v0, x), (v1, y - 1)))

    for r_, mt in zip(res, meta):
        clip = r_["clips"][0]
        if mt[0] == "audio":
            gain.append(clip)
        elif mt[0] == "v1":
            _, what, x, y, alt = mt
            if what[0] == "split":
                half(clip, True)                      # speaker on top, like hook 1
                continue
            s0 = (what[1] if what[0] == "talk" else 100) * (1.08 if alt else 1.0)
            push(clip, s0, s0 * (1 + 0.015 * (y - x) / FPS), x, y)
        elif mt[0] == "ins":
            _, x, y = mt
            push(clip, 104.0, 104.0 * (1 + min(0.08 * (y - x) / FPS, 0.25)), x, y)
        elif mt[0] == "listen":
            half(clip, False)
    fx.append({"id": "clip.audioGain", "params": {"clips": gain, "mode": "set", "db": 4.0}})
    cli(PROJ, fx)
    print(f"{PROJ.name}: opening {n} frames ({n / FPS:.2f} s), body moved {delta:+d}, end {(3026 + delta)} frames")
    for (st, en), (key, what) in zip(bounds, SHOTS):
        print(f"  {st:4d}-{en:4d}  {key!r:16} {what[0]} {what[1]}")
    json.dump({"n": n, "delta": delta, "starts": starts, "edges": edges}, open(EDIT / f".hook-{HOOK}.opening.json", "w"))


if __name__ == "__main__":
    main()
