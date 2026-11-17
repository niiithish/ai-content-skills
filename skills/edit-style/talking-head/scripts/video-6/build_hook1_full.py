#!/usr/bin/env python3
"""video-6: makes edit/hook-1.fcproj export-ready like the inspo (Koriderm tier list), user 2026-11-13: "make it
export ready since we have everything we need, dont export tho, make hook-1 only".

Adds, under the template-11 captions (which stay on the top track):
- V2: a full-screen picture per phrase (MAP: caption block index -> insert number, a tier-board state, or None for
  her face), each from its caption start until the next one. Clips fill 1080x1920, start 1 s in when long enough,
  are slowed (never under 60 %) when short; stills (tier board) push 2 %/s up to the cut.
- V3: her green-screen take (assets/cutout, same timeline time) over every picture run, keyed (Ultra Key), small in
  the bottom-right as in the inspo (scale 72 %, face at about x 960, desk at the frame bottom).
- V4: the product name card (white caps, bar at left) over the first picture of each product.
- A3: music (Frank Ocean instrumental) about 18 dB under the voice, looped once, 1 s fade out.
Usage: build_hook1_full.py   (backs the project up first; run on the captions-only hook-1)"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
PROJ = EDIT / "hook-1.fcproj"
TB = ROOT / "assets/tierboard"
GREEN = ROOT / "assets/cutout/drhan-greenscreen-hook1-body-1.242x.mp4"   # the user's take retimed to the 1.242x talking head (edit/retime_speed.py)
MUSIC = ROOT.parent / "assets/music/Frank Ocean - Pink + White(instrumental) [N9GXZD8y-bg].m4a"
TPS, FPS = 254016000000, 24
F = TPS // FPS
PUSH_PER_S = 0.02
# 2026-11-13 (user: "a bit big"): eyes measured on the inspo at (978, 1145), 108 px apart; ours were 55 px left of
# that. Scale 70 keeps her a touch smaller (101 px) and shows more desk; position puts her eyes on the inspo's spot.
KEY = dict(scale=70.0, position=[991, 1423], key_color=[0, 182 / 255, 88 / 255, 1])
# 2026-11-13 (user: "in the green screened ones she is a bit yellow"): the green-screen take's skin is (185.6, 138.5,
# 107.9) against V1's (186.7, 139.9, 115.5) on the same face patch: lift blue (and a touch of R/G) with Lumetri curves.
GRADE = {"curve_blue": [[0, 0], [0.423, 0.453], [1, 1]], "curve_red": [[0, 0], [0.718, 0.732], [1, 1]],
         "curve_green": [[0, 0], [0.537, 0.549], [1, 1]]}
MUSIC_DB = -19.0          # voice now -14.2 LUFS (inspo -14.1, user 2026-11-13), music -13.5 LUFS: -19 dB puts it ~18 dB under
FADE = 24

# caption block index -> picture: an int (insert 2NN), "T:<state>" (tier board), None (her face)
MAP = [
    (0, None), (2, 202), (5, 201), (6, 203), (8, None), (9, 204), (11, None),
    (12, 207), (14, 208), (16, 209), (17, 210), (18, 211), (19, None),
    (22, 213), (23, 212), (24, 214), (25, 215), (27, None), (28, 260), (30, 261), (32, 262), (35, 263),
    (38, 216), (41, 264), (42, 265), (43, None), (44, "T:D"),
    (46, 218), (48, 219), (49, 220), (52, 221), (55, 222), (57, 223), (60, 266), (63, "T:C1"),
    (67, 224), (68, 225), (70, 226), (72, 267), (73, 228), (74, None), (75, 229), (78, 230),
    (79, 231), (82, None), (84, 232), (86, "T:C2"),
    (89, 233), (91, 234), (92, 235), (95, 236), (97, None), (99, 237), (102, 238), (105, 239), (106, 268),
    (108, 269), (111, 240), (112, 241), (113, "T:C3"),
    (115, 242), (116, 243), (117, 244), (119, 245), (121, 246), (124, None), (126, 247), (128, 248), (130, 249),
    (131, "T:C4"),
    (133, 250), (135, 251), (138, 270), (140, 252), (144, 253), (148, 254), (149, "T:B"),
    (150, 271), (152, 256), (154, 272), (156, None), (159, "T:B"), (164, 273), (166, None), (169, 274),
    (173, None), (174, 275), (177, None), (178, 276), (180, None), (182, 277), (184, 278), (188, 279),
    (190, 281), (193, 280), (196, None), (198, 257), (200, 282), (202, None), (204, 283), (206, 258),
    (209, 259), (213, 284), (216, "T:B"), (219, None), (221, 285), (222, 286), (225, None),
    (230, 287), (231, 288), (234, None), (235, "T:S"),
]
CARDS = {213: "creams", 218: "dry-brushing", 224: "aveli", 233: "leggings", 242: "devices", 250: "oils"}


def cli(cmds):
    f = EDIT / ".fc-run.jsonl"
    f.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(f)], capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad[:3] or out.stderr[-2000:]}")
    f.unlink()
    return [r.get("result") for r in res]


def seq():
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height:format=duration", "-of", "json", str(p)],
                                  capture_output=True, text=True, check=True).stdout)
    d = float(j["format"].get("duration", 1e6)) if p.suffix == ".mp4" else 1e6
    return j["streams"][0]["width"], j["streams"][0]["height"], d


def main():
    s = seq()
    if len(s["video"]) != 2:
        sys.exit(f"expected V1 talking + V2 captions only, found {len(s['video'])} video tracks")
    end = s["durationFrames"]
    caps = json.load(open(ROOT / "captions/hook-1.captions.json"))["blocks"]
    src = json.load(open(EDIT / "insert_sources.json"))
    anchors = [(caps[i]["start"], p) for i, p in MAP]
    assert [a for a, _ in anchors] == sorted(a for a, _ in anchors)
    nums = [p for _, p in anchors if isinstance(p, int)]
    assert len(nums) == len(set(nums)), "an insert repeats"

    def path(p):
        return Path(src[str(p)]["path"]) if isinstance(p, int) else TB / f"board-{p[2:]}.png"
    pics = sorted({str(path(p)) for _, p in anchors if p})
    cards = [TB / f"card-{v}.png" for v in CARDS.values()]
    for p in pics + [str(c) for c in cards] + [str(GREEN), str(MUSIC)]:
        assert Path(p).exists(), p

    bk = EDIT / f"backup-{datetime.date.today()}-full-build"
    bk.mkdir(exist_ok=True)
    if not (bk / PROJ.name).exists():
        shutil.copy2(PROJ, bk / PROJ.name)

    paths = pics + [str(c) for c in cards] + [str(GREEN), str(MUSIC)]
    r = cli([{"id": "sequence.addTracks", "params": {"video": 3, "audio": 1, "videoAfter": "V1"}},
             {"id": "file.import", "params": {"paths": paths}}, {"id": "file.save", "params": {}}])
    items = dict(zip(paths, r[1]["items"]))

    place, meta, report = [], [], []
    runs = []                                  # picture runs (for the cutout)
    for k, (at, p) in enumerate(anchors):
        nxt = anchors[k + 1][0] if k + 1 < len(anchors) else end
        d = nxt - at
        if not p:
            report.append(f"{at / FPS:7.2f}s {d / FPS:4.1f}s  face")
            continue
        if runs and runs[-1][1] == at:
            runs[-1][1] = nxt
        else:
            runs.append([at, nxt])
        pp = path(p)
        w, h, dur = probe(pp)
        mfr = int(dur * FPS) - 1
        sin, slow = 0, None
        if pp.suffix == ".mp4":
            if mfr - FPS >= d:
                sin = FPS                     # Flow clips start slow: from the 1 s mark
            elif mfr < d:
                slow = round(100 * mfr / d, 1)
                assert slow >= 60, (pp.name, d, mfr)
        place.append({"id": "timeline.place", "params": {"item": items[str(pp)], "track": "V2", "frame": at,
                                                         "sourceIn": sin * F, "duration": min(d, mfr) * F,
                                                         "insert": False, "video": True, "audio": False}})
        meta.append((pp, at, d, w, h, slow))
        tag = src[str(p)]["kind"] if isinstance(p, int) else "board"
        report.append(f"{at / FPS:7.2f}s {d / FPS:4.1f}s  {p} {pp.name} [{tag}]{f' slowed to {slow}%' if slow else ''}")
    # cutout over every picture run, same timeline time in the green-screen take
    for a, b in runs:
        place.append({"id": "timeline.place", "params": {"item": items[str(GREEN)], "track": "V3", "frame": a,
                                                         "sourceIn": a * F, "duration": (b - a) * F,
                                                         "insert": False, "video": True, "audio": False}})
        meta.append(("cut", a, b - a))
    # name cards over the first picture of each product
    for k, (at, p) in enumerate(anchors):
        if p in CARDS:
            d = anchors[k + 1][0] - at
            place.append({"id": "timeline.place", "params": {"item": items[str(TB / f'card-{CARDS[p]}.png')],
                                                             "track": "V4", "frame": at, "duration": d * F,
                                                             "insert": False, "video": True, "audio": False}})
            meta.append(("card", at, d))
    # music, looped once to cover the hook
    mlen = int(probe(MUSIC)[2] * FPS) - 1 if False else int(185.5 * FPS)
    place.append({"id": "timeline.place", "params": {"item": items[str(MUSIC)], "track": "A3", "frame": 0,
                                                     "duration": mlen * F, "insert": False, "video": False, "audio": True}})
    place.append({"id": "timeline.place", "params": {"item": items[str(MUSIC)], "track": "A3", "frame": mlen,
                                                     "duration": (end - mlen) * F, "insert": False, "video": False,
                                                     "audio": True}})
    meta += [("music",), ("music",)]
    res = cli(place + [{"id": "file.save", "params": {}}])[:-1]

    fx = []
    for r_, m in zip(res, meta):
        clip = r_["clips"][0]
        if m[0] == "music":
            fx.append({"id": "clip.audioGain", "params": {"clips": [clip], "mode": "set", "db": MUSIC_DB}})
            last_music = clip
            continue
        if m[0] == "card":
            continue
        if m[0] == "cut":
            fx += [{"id": "effects.apply", "params": {"clips": [clip], "effect": "ultra_key"}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": "ultra_key", "param": "key_color",
                                                         "value": KEY["key_color"]}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale",
                                                         "value": KEY["scale"]}},
                   {"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "position",
                                                         "value": KEY["position"]}},
                   {"id": "effects.apply", "params": {"clips": [clip], "effect": "lumetri"}}]
            fx += [{"id": "effects.setParam", "params": {"clip": clip, "effect": "lumetri", "param": k, "value": v}}
                   for k, v in GRADE.items()]
            continue
        pp, at, d, w, h, slow = m
        sc = max(1080 / w, 1920 / h) * 100
        if slow:
            fx.append({"id": "clip.speedDuration", "params": {"clips": [clip], "speed": slow, "ripple": False}})
        if pp.suffix != ".mp4":
            fx += [{"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale",
                                                         "value": round(v, 2), "keyframe": True, "time": f * F}}
                   for v, f in ((sc, at), (sc * (1 + PUSH_PER_S * d / FPS), at + d - 1))]
        elif abs(sc - 100) > 0.3:
            fx.append({"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale",
                                                            "value": round(sc, 2)}})
    fx.append({"id": "sequence.applyAudioTransition", "params": {"clip": last_music, "edge": "out", "frames": FADE}})
    cli(fx + [{"id": "file.save", "params": {}}])
    # a slowed clip can end a frame short of the next picture (speed rounding): trim its end out to close the gap
    v2 = sorted(seq()["video"][1]["items"], key=lambda c: c["startFrame"])
    gaps = [{"id": "timeline.trim", "params": {"clip": a["clip"], "edge": "out", "mode": "regular",
                                                "deltaFrames": b["startFrame"] - a["startFrame"] - a["durationFrames"]}}
            for a, b in zip(v2, v2[1:]) if 0 < b["startFrame"] - a["startFrame"] - a["durationFrames"] < 8]
    if gaps:
        cli(gaps + [{"id": "file.save", "params": {}}])
        report.append(f"closed {len(gaps)} one-frame gaps after slowed clips")
    print("\n".join(report))
    print(f"{len(nums)} inserts, {len(runs)} cutout runs, {len(CARDS)} cards; backup {bk}")


if __name__ == "__main__":
    main()
