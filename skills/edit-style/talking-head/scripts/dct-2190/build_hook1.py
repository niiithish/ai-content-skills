#!/usr/bin/env python3
"""DCT-2190: builds edit/hook-1.fcproj, export-ready (user 2026-11-03: "use the talking head .mp4 with the replaced
enhanced audio ... we have the timing of where the cuts happen ... no music, but captions should be there").

- Master: exports/talking-head.mp4 (the export of talking-head.fcproj) with the user's enhanced voice
  (audio/talking-head-enhanced.mp3) muxed in -> edit/talking-media/talking-head-enhanced.mp4 (picture copied).
- V1/A1: hook 1 (master frames 0-158) then the body (481-2551), cut at every clip join of talking-head.fcproj, so
  each hidden jump is a real V1 cut that captions and inserts can land on.
- V2: one full-screen picture per phrase (PLAN.md), from its word (edit/words/talking-head-enhanced.words.json)
  until the next one; a join just before the word wins (the picture covers the jump). None = her face.
  Stills get a slow centred push 100 -> 106% up to the cut; clips are scaled to fill 1080x1920.
Captions come after, with captions-filmcraft (template 6), then fc_inserts.py snap/check.
Usage: build_hook1.py [--replace]"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
LIB = ROOT.parent / "assets" / "clips"
PROJ = EDIT / "hook-1.fcproj"
MASTER = EDIT / "talking-media" / "talking-head-enhanced.mp4"
TPS, FPS = 254016000000, 24
PUSH = 1.06
# talking-head.fcproj V1 joins (master frames); hook 1 = [0, 158), body = [481, 2551)
JOINS = [0, 101, 158, 256, 317, 481, 603, 683, 716, 798, 831, 864, 908, 1007, 1014, 1043, 1104, 1224, 1262, 1318,
         1379, 1437, 1531, 1652, 1691, 1780, 1900, 2060, 2120, 2223, 2390, 2551]
RANGES = [(0, 158), (481, 2551)]
# dead air at each join (user 2026-11-03: "we didn't consider the silence from the start of next clip"): keep at most
# TAIL_KEEP of the clip's tail and LEAD_KEEP of the next clip's lead-in, so voice to voice is about 0.25 s.
# The hook -> body join (158 | 481) keeps its own ~0.33 s.
TAIL_KEEP, LEAD_KEEP = 0.16, 0.07

S = lambda n, v: ROOT / f"scenes/all/scene-{n}-{v}.jpg"
C = lambda f: ROOT / "clips/all" / f
L = lambda p: LIB / f"{p}.mp4"
# (word index in talking-head-enhanced.words.json, picture or None for her face), story order
SHOTS = [
    (0, C("clip-201-v4-seedance.mp4")),                       # If a woman finally lost the weight ... before,
    (14, EDIT / "media/black-card.png"),                      # losing more weight will not change that.
    (64, None),                                               # I'm a dermatologist, and I hear this constantly
    (71, C("clip-204-v2-1080p.mp4")),                         # from women after GLP-1 weight loss.
    (77, S("205a", "v2")),                                    # They lose 40,
    (80, S("205b", "v2")),                                    # 50,
    (81, S("205c", "v3")),                                    # even 70 pounds.
    (84, None),                                               # Then they take their clothes off.
    (90, C("clip-206-v5-seedance.mp4")),                      # Their thighs look loose.
    (94, C("clip-207-v5-seedance.mp4")),                      # The skin looks thin and crepey.
    (100, L("b-roll/problem-cellulite/front-of-knees-and-thighs-dimpled_v4-201")),  # The dimples show through.
    (104, S("208", "v2")),                                    # They lost the weight,
    (108, L("b-roll/problem-hiding/cardigan-on-sofa-covering-legs_v4-207")),  # but they're still hiding their thighs.
    (114, S("210", "v2")),                                    # If you think you need to lose another 10 pounds,
    (124, None),                                              # you don't.
    (126, S("211", "v2")),                                    # The weight loss worked.
    (130, C("clip-212-v6-flux3max.mp4")),                     # Now the problem is the skin it left behind.
    (139, L("b-roll/tried-everything/squats-in-living-room_v3-220")),  # Instead of more squats (only 360p exists)
    (143, None),                                              # or a cosmetic procedure, I tell women ... (213 open)
    (156, C("clip-214-v2-1080p.mp4")),                        # because when the weight came off,
    (162, C("clip-215-v5-seedance.mp4")),                     # the skin on their thighs didn't bounce back.
    (170, L("animation/skin-science/thin-skin-over-fat-lobules_v3-202")),  # Squats and procedures work on what's underneath,
    (177, L("animation/skin-science/skin-surface-dimples-deepen_v3-217")),  # but the skin on top can still look loose.
    (186, None),                                              # That's why
    (188, L("b-roll/problem-cellulite/backs-of-thighs-living-room-navy-shorts_v2-103a")),  # the dimples show more ... (plan's mirror-turns is 360p only)
    (196, S("216", "v2")),                                    # If you want firmer, smoother-looking thighs,
    (203, L("animation/oil-absorbs/oil-spheres-slip-between-skin-cells_v2-123b")),  # you need to get firming ingredients past the surface.
    (212, L("animation/creams-dont-work/cream-beads-sit-on-skin-surface_v3-206")),  # Most creams just stop there.
    (217, None),                                              # That's why I always recommend this body oil. (bottle)
    (225, L("animation/ingredients/collagen-helix_client")),  # It's made with collagen
    (229, L("animation/ingredients/stem-cells_client")),      # and stem cells,
    (232, L("b-roll/product/in-use/oil-in-palm-bottle-beside_client")),  # the firming ingredients that loose skin needs.
    (239, L("animation/ingredients/eucalyptus-leaves-in-water_client")),  # And eucalyptus
    (241, L("animation/oil-absorbs/eucalyptus-carries-oil-past-surface_v3-205")),  # carries them past the surface,
    (246, L("animation/skin-science/skin-layer-thickens-hides-dimples_v3-203")),  # helping the skin over the dimples
    (252, L("b-roll/routine/palm-smooths-oil-up-thigh_v2-128")),  # look firmer and smoother again.
    (257, EDIT / "media/mosaic-218-v1.jpg"),                  # Over 19,000 women have already used it.
    (264, S("219", "v2")),                                    # Many of them report
    (268, S("220", "v5")),                                    # smoother, firmer,
    (270, S("221", "v2")),                                    # and less dimply thighs within weeks.
    (276, L("b-roll/confident/walking-out-to-patio-denim-shorts_v2-131b")),  # If your goal is to feel confident wearing shorts again,
    (286, C("clip-222-v2-1080p.mp4")),                        # not just fit a smaller size,
    (292, S("223", "v2")),                                    # I definitely recommend giving this a try.
    (299, None),                                              # I'll leave a link below ... guarantee. (CTA, bottle)
]


def make_pieces():
    """[(master in, length, hook frame)]: V1 pieces with the silence at every inner join trimmed."""
    from join_gaps import voiced, gap
    on = voiced()
    pieces, at = [], 0
    for a, b in RANGES:
        js = [j for j in JOINS if a <= j < b] + [b]
        for x, y in zip(js, js[1:]):
            sin, sout = x, y
            if x != a:                                    # lead-in silence of this clip
                _, s_ = gap(on, x)
                sin += max(0, int((s_ - x / FPS - LEAD_KEEP) * FPS))
            if y != b:                                    # tail silence before the next clip
                e_, _ = gap(on, y)
                sout -= max(0, int((y / FPS - e_ - TAIL_KEEP) * FPS))
            pieces.append((sin, sout - sin, at))
            at += sout - sin
    return pieces


PIECES = None


def to_hook(m):
    """Master frame -> hook-1 frame (a frame in trimmed silence goes to the nearest kept edge)."""
    for sin, d, at in PIECES:
        if m < sin:
            return at
        if m < sin + d:
            return at + m - sin
    return PIECES[-1][2] + PIECES[-1][1]


def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height:format=duration", "-of", "json", str(p)],
                                  capture_output=True, text=True, check=True).stdout)
    d = float(j["format"].get("duration", 1e6)) if p.suffix == ".mp4" else 1e6
    return j["streams"][0]["width"], j["streams"][0]["height"], d


def cli(proj, cmds, save_as=None):
    script = EDIT / ".fc-run.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    args = ["filmcraft-cli", "--compact"] + (["--project", str(proj)] if not save_as else []) + ["run", str(script)]
    if save_as:
        args += ["--save-as", str(save_as)]
    out = subprocess.run(args, capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    script.unlink()
    return [r.get("result") for r in res]


def main():
    if PROJ.exists():
        if "--replace" not in sys.argv:
            sys.exit(f"{PROJ.name} exists: pass --replace")
        PROJ.unlink()
    ws = json.load(open(EDIT / "words/talking-head-enhanced.words.json"))
    global PIECES
    PIECES = pieces = make_pieces()          # (master in, length, hook frame)
    end = sum(p[1] for p in pieces)
    cuts = sorted({p[2] for p in pieces})
    anchors = []
    for wi, pic in SHOTS:
        f = to_hook(round(ws[wi]["start"] * FPS))
        near = [c for c in cuts if f - 8 <= c <= f + 1]   # a join just before the word: start on it, the cut is hidden
        anchors.append((max(near) if near else f, pic))
    anchors[0] = (0, anchors[0][1])
    pics = [p for _, p in anchors if p]
    assert len(pics) == len(set(pics)), "a picture repeats"
    for p in pics:
        assert p.exists(), p
    paths = [str(MASTER)] + sorted({str(p) for p in pics})
    r = cli(None, [{"id": "file.newProject", "params": {"name": "hook-1"}},
                   {"id": "file.import", "params": {"paths": paths}},
                   {"id": "file.newSequence", "params": {"name": "hook-1", "width": 1080, "height": 1920, "fps": FPS,
                                                         "video": 2, "audio": 1}}], save_as=PROJ)
    items = dict(zip(paths, r[1]["items"]))
    place, meta = [], []
    for sin, d, at in pieces:
        place.append({"id": "timeline.place", "params": {"item": items[str(MASTER)], "track": "V1", "audioTrack": "A1",
                                                         "frame": at, "sourceIn": sin * TPS // FPS,
                                                         "duration": d * TPS // FPS, "insert": False}})
        meta.append(None)
    report = []
    for i, (at, p) in enumerate(anchors):
        nxt = anchors[i + 1][0] if i + 1 < len(anchors) else end
        if not p:
            report.append(f"{at / FPS:6.2f}s {(nxt - at) / FPS:4.1f}s  face")
            continue
        w, h, dur = probe(p)
        mdur = int(dur * FPS) - 1
        d = nxt - at
        slow = None
        if d > mdur:                     # the clip is a little short: slow it to fill its slot (at most 10%)
            slow = round(100 * mdur / d, 1)
            assert slow >= 90, (p.name, d, mdur)
        place.append({"id": "timeline.place", "params": {"item": items[str(p)], "track": "V2", "frame": at,
                                                         "duration": min(d, mdur) * TPS // FPS, "insert": False,
                                                         "video": True, "audio": False}})
        meta.append((p, at, d, w, h, slow))
        report.append(f"{at / FPS:6.2f}s {d / FPS:4.1f}s  {p.name}{f'  (slowed to {slow}%)' if slow else ''}")
    res = cli(PROJ, place + [{"id": "file.save", "params": {}}])[:-1]
    fx = []
    for r_, m in zip(res, meta):
        if not m:
            continue
        p, at, d, w, h, slow = m
        clip = r_["clips"][0]
        s = max(1080 / w, 1920 / h) * 100
        if slow:
            fx.append({"id": "clip.speedDuration", "params": {"clips": [clip], "speed": slow, "ripple": False}})
        if p.suffix != ".mp4":       # still: one slow centred push, right up to the cut
            fx += [{"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale",
                                                         "value": round(v, 2), "keyframe": True, "time": f * TPS // FPS}}
                   for v, f in ((s, at), (s * PUSH, at + d - 1))]
        elif abs(s - 100) > 0.3:
            fx.append({"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale",
                                                            "value": round(s, 2)}})
    cli(PROJ, fx + [{"id": "file.save", "params": {}}])
    print("\n".join(report))
    print(f"{PROJ.name}: {len(pieces)} talking pieces, {len(pics)} inserts, {end / FPS:.1f} s; V1 cuts {cuts}")


if __name__ == "__main__":
    main()
