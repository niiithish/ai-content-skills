#!/usr/bin/env python3
"""Builds edit/hook-N.fcproj (N = 1, 2, 3) from the 360p drafts so the user can see how the video will look (user
2026-10-29: "just using this draft clip, set up it like export ready ... to give me an idea"). Not the final pipeline:
no ElevenLabs voice change and no joined master yet. Each talking clip is sped up 1.1x (speed_up.sh, as the master will
be) into edit/draft-media/, trimmed to its speech and laid back to back on V1/A1: hook N's take, then body clips 4-13.
Every insert is full screen on V2 (video only), from the word the plan puts it on until the next anchor, or its media
end; None shows her face. Captions go on top with captions-filmcraft afterwards.
Usage: build_draft.py N [--replace]"""
import json, re, shutil, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
DM = EDIT / "draft-media"
WORDS = EDIT / "words"
LIB = ROOT.parent / "assets" / "clips"
TPS, FPS = 254016000000, 24
LEAD, TAIL, HOOK_TAIL = 0.06, 0.14, 0.37   # silence kept before and after each line; hook to body gap (skill: ~0.37 s)
SPEED = Path.home() / ".claude/skills/talking-head-video-production/scripts/speed_up.sh"
sys.path.insert(0, str(Path.home() / ".claude/skills/transcribe/scripts"))

INS = {s: f"clips/all/clip-{s}-v1.mp4" for s in ["201", "202", "203", "206", "207", "209", "210", "212", "213", "214", "215"]}
INS.update({"204": "clips/all/clip-204-v2.mp4", "211": "clips/all/clip-211-v2.mp4",
            "217": "clips/clip-217/clip-217-v2.mp4"})   # user 2026-10-29: the reference's deflating skin cells
L = {"collagen-mesh": "animation/skin-science/collagen-mesh-thinning_v3-204",
     "pinch": "b-roll/problem-cellulite/pinch-test-shows-dimples_v4-205",
     "backs": "b-roll/problem-cellulite/backs-of-thighs-grey-shorts-hallway_v4-204",
     "shorts-away": "b-roll/problem-hiding/putting-denim-shorts-away-wardrobe_v2-105",
     "scale": "pov/tried-everything/stepping-on-bathroom-scale_v3-222",
     "spheres": "animation/oil-absorbs/oil-spheres-slip-between-skin-cells_v2-123b",
     "beads": "animation/creams-dont-work/cream-beads-sit-on-skin-surface_v3-206",
     "takes-bottle": "b-roll/product/in-use/hand-takes-bottle-two-on-counter_client",
     "palm": "b-roll/product/in-use/oil-in-palm-bottle-beside_client",
     "helix": "animation/ingredients/collagen-helix_client",
     "stem": "animation/ingredients/stem-cells_client",
     "leaves": "animation/ingredients/eucalyptus-leaves-in-water_client",
     "carries": "animation/oil-absorbs/eucalyptus-carries-oil-past-surface_v3-205",
     "cardigan": "b-roll/problem-hiding/cardigan-on-sofa-covering-legs_v4-207",
     "lounger": "pov/product/bottle-in-hand-legs-on-lounger_client"}

# user 2026-10-29: as in the reference, lifestyle and body inserts are stills with a slow centred push (the still each
# approved clip was made from); only CGI, product and hand-action shots (209, 212, 214, the library) stay clips
STILLS = {"201", "202", "203", "204", "205", "206", "207", "209", "210", "211", "213", "215", "216",
          "218", "219", "220", "221", "222", "223", "224", "225", "226", "227", "228"}
# user 2026-10-29: close stills made after the swap (thighs fully in view, as in the reference); the rest are the
# stills their approved clips were made from. 218-228 match the reference shot for shot: three women on "firm, tight
# and smooth.", severe problem stills (220-222, 227, 228, 209 v2, 215 v3) and four before/after splits (223-226,
# two stills joined side by side)
NEW_STILLS = {"201": "scene-201-v2", "204": "scene-204-v3", "205": "scene-205-v1", "216": "scene-216-v1", "206": "scene-206-v2",
              "207": "scene-207-v2", "218": "scene-218-v1", "219": "scene-219-v1", "220": "scene-220-v1",
              "221": "scene-221-v1", "209": "scene-209-v2", "227": "scene-227-v1", "222": "scene-222-v1",
              "228": "scene-228-v1", "223": "split-223-v1", "224": "split-224-v1", "225": "split-225-v1",
              "226": "split-226-v1", "213": "scene-213-v3", "215": "scene-215-v3"}
PUSH = 1.06

# talking shot: [(first words of the phrase, insert or None)], from PLAN.md
HOOKS = {1: "201", 2: "202", 3: "203"}
BODY = {"4": [("i modeled", "204"), ("victoria's", "205"), ("for", "216"), ("and here's", "206"), ("every single", None)],
        "5": [(0, None), ("our skin", "217"), ("the stuff", "207"), ("firm", "218"), ("and smooth", "219")],
        "6": [("your thighs", "220"), ("your cellulite", "221"), ("and your skin", "209")],
        "7": [("that's why", "227"), ("stop", "222"), ("even when", "scale")],
        "8": [("what you", None), ("is get", "228"), ("past", "spheres"), ("most creams", "beads")],
        "9": [("that's why", "takes-bottle"), ("this body", "palm"), ("it contains", "helix"), ("stem", "stem"),
              ("and eucalyptus", "leaves"), ("which are", "223"), ("for cellulite", "224")],
        "10": [("the eucalyptus", "carries"), ("and stem", "225"), ("making", "226")],
        "11": [("i massage", "212"), ("and over", None), ("they looked", "213"), ("firmer", "214")],
        "12": [("if the", "215"), ("and you've", "cardigan"), ("definitely", "lounger")],
        "13": [("i'll", None)]}


def take(shot):
    out = Path(job(shot)["output"])
    final = out.parent / "final" / f"{out.stem}-1080p.mp4"   # user 2026-10-29: 1080p talking finals swapped in
    return final if final.exists() else out


def sped(shot):
    src = take(shot)
    out = DM / f"{src.stem}-1.1x.mp4"
    if not out.exists():
        DM.mkdir(parents=True, exist_ok=True)
        subprocess.run(["bash", str(SPEED), str(src), "1.1", str(out)], check=True, capture_output=True)
    return out


def words(p):
    out = WORDS / f"{p.stem}.words.json"
    if not out.exists():
        WORDS.mkdir(exist_ok=True)
        subprocess.run([sys.executable, str(Path.home() / ".claude/skills/transcribe/scripts/transcribe.py"), "--engine",
                        "parakeet", "--out-dir", str(WORDS), str(p)], check=True, capture_output=True)
    return json.load(open(out))


def speech(p):
    """First and last moment of voice, from the waveform (threshold as pauses.py: 40% from noise floor to speech)."""
    a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(p), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                     capture_output=True, check=True).stdout, np.int16) / 32768
    db = np.array([20 * np.log10(np.sqrt((a[i:i + 160] ** 2).mean()) + 1e-9) for i in range(0, len(a) - 160, 160)])
    lo, hi = np.percentile(db, 8), np.percentile(db, 90)
    on = np.where(db > lo + 0.4 * (hi - lo))[0]
    return on[0] / 100, (on[-1] + 1) / 100, len(a) / 16000


def norm(w):
    return re.sub(r"[^a-z']", "", w.lower().replace("’", "'"))


def find(ws, phrase, after):
    if isinstance(phrase, int):
        return ws[phrase]["start"]
    p = phrase.split()
    for i in range(len(ws) - len(p) + 1):
        if ws[i]["start"] >= after - 0.01 and [norm(w["word"]) for w in ws[i:i + len(p)]] == p:
            return ws[i]["start"]
    sys.exit(f"phrase {phrase!r} not found in {[w['word'] for w in ws]}")


def job(shot):
    return next(j for j in json.load(open(ROOT / "clips/clips-batch.json"))["jobs"] if re.match(rf"clip-{shot}-v\d+$", j["id"]))


def media(m):
    if m in NEW_STILLS:
        return ROOT / f"scenes/scene-{m}/{NEW_STILLS[m]}.jpg"
    if m in STILLS:
        return Path(job(m)["ingredient"][0])
    return (LIB / f"{L[m]}.mp4") if m in L else ROOT / INS[m]


def probe(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                        "-of", "json", str(p)], capture_output=True, text=True, check=True).stdout
    j = json.loads(o)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"].get("duration", 1e6)) if p.suffix == ".mp4" else 1e6


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


def fr(s):
    return round(s * FPS)


def build(n):
    proj = EDIT / f"hook-{n}.fcproj"
    if proj.exists():
        if "--replace" not in sys.argv:
            sys.exit(f"{proj.name} exists: pass --replace")
        proj.unlink()
    shots = [(str(n), [(0, HOOKS[n]), ("i'm", None)])] + list(BODY.items())
    pieces, anchors, t = [], [], 0   # t in frames
    for i, (shot, anc) in enumerate(shots):
        p = sped(shot)
        ws = words(p)
        s0, s1, dur = speech(p)
        a = max(0.0, s0 - LEAD)
        b = min(dur, s1 + (HOOK_TAIL if i == 0 else TAIL))
        fa, fb = fr(a), fr(b)
        pieces.append((p, fa, fb - fa, t))
        last = 0
        for ph, m in anc:
            w = find(ws, ph, last) if ph != 0 else a
            last = w
            anchors.append((t + max(0, fr(w) - fa), m))
        t += fb - fa
    end = t
    shown = [m for _, m in anchors if m]
    if len(shown) != len(set(shown)):
        sys.exit(f"repeats: {shown}")
    paths = sorted({str(p) for p, *_ in pieces} | {str(media(m)) for m in shown})
    r = cli(None, [{"id": "file.newProject", "params": {"name": f"hook-{n}"}},
                   {"id": "file.import", "params": {"paths": paths}},
                   {"id": "file.newSequence", "params": {"name": f"hook-{n}", "width": 1080, "height": 1920, "fps": FPS,
                                                         "video": 2, "audio": 1}}], save_as=proj)
    items = dict(zip(paths, r[1]["items"]))
    place, meta = [], []
    for p, sin, d, at in pieces:
        place.append({"id": "timeline.place", "params": {"item": items[str(p)], "track": "V1", "audioTrack": "A1", "frame": at,
                                                         "sourceIn": sin * TPS // FPS, "duration": d * TPS // FPS, "insert": False}})
        meta.append((p, None, None))
    plan = []
    for i, (at, m) in enumerate(anchors):
        if not m:
            continue
        nxt = anchors[i + 1][0] if i + 1 < len(anchors) else end
        p = media(m)
        mdur = fr(probe(p)[2]) - 1
        d = min(nxt - at, mdur, end - at)
        place.append({"id": "timeline.place", "params": {"item": items[str(p)], "track": "V2", "frame": at,
                                                         "duration": d * TPS // FPS, "insert": False, "video": True, "audio": False}})
        meta.append((p, at, d))
        plan.append((at, d, m, nxt - at > mdur))
    res = cli(proj, place + [{"id": "file.save", "params": {}}])[:-1]
    fx = []
    for r_, (p, at, d) in zip(res, meta):
        w, h, _ = probe(p)
        s = max(1080 / w, 1920 / h) * 100   # fill the 1080x1920 frame (drafts are 360x640)
        if p.suffix != ".mp4":   # a still: slow centred push from fill to PUSH x fill over its time on screen
            fx += [{"id": "effects.setParam", "params": {"clip": r_["clips"][0], "effect": "motion", "param": "scale",
                                                         "value": round(v, 2), "keyframe": True, "time": f * TPS // FPS}}
                   for v, f in ((s, at), (s * PUSH, at + d - 1))]
        elif abs(s - 100) > 0.3:
            fx.append({"id": "effects.setParam", "params": {"clip": r_["clips"][0], "effect": "motion", "param": "scale", "value": round(s, 2)}})
    cli(proj, fx + [{"id": "file.save", "params": {}}])
    for at, d, m, short in plan:
        print(f"{at / FPS:6.2f}s {d / FPS:4.1f}s  {m}{' (still)' if m in STILLS else ''}{'  (media ends, face shows after)' if short else ''}")
    print(f"{proj.name}: {len(pieces)} talking clips, {len(plan)} inserts, {end / FPS:.1f} s")


for n in [int(a) for a in sys.argv[1:] if a.isdigit()]:
    build(n)
