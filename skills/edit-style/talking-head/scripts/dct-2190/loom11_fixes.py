#!/usr/bin/env python3
"""Client Loom 11 (2026-11-03) edit fixes, on hook-N.fcproj (body clip ids are shared by the clones):
1. "you don't": the take ran 550 (to src 41.958) + 74 (4 f) and jumped to 77 at src 42.25, clipping "The"; insert 211
   came in 4 f before "don't" ended ("she doesn't even completely say it and she's already gone"). Now 74 runs on to
   77's source (one continuous shot, +3 f, everything after moves +3 f as one block), the face holds until "The"
   (src 42.16), and "you don't" stays up until then; insert 139 and caption 438 start on "The".
2. Still pushes ("static, then 0.1 s, then it starts zooming" / "the zoom stops, then the cut comes"): every still on
   the insert tracks pushes from its first frame to its last at one slower rate (RATE % of its start scale a second).
3. "money-back guarantee" came up 14 f before she says it: captions 534/536/538 on the spoken words.
Usage: loom11_fixes.py hook-1.fcproj [...]"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path

F = 10584000000
TPS = 254016000000
RATE = 2.0                      # % per second (was about 5 %/s, 140.6 -> 149.1 over ~1.2 s)
SRC_THE = 42.16                 # master second "The" starts (words/talking-head-enhanced)
SRC_WITH, SRC_MONEY = 104.16, 105.2


def run(proj, cmds):
    f = proj.with_suffix(".l11.jsonl")
    f.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink()
    rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs):
        sys.exit(f"{proj.name}: {[r for r in rs if not r.get('ok')] or out.stderr[-1500:]}")


def seqj(proj):
    d = json.load(open(proj))
    return next(it["kind"]["Sequence"] for it in d["project"]["items"].values()
                if isinstance(it.get("kind"), dict) and "Sequence" in it["kind"])


def by_id(sq):
    out = {}
    for kind in ("video_tracks", "audio_tracks"):
        for ti, tr in enumerate(sq[kind]):
            for c in tr["items"]:
                out[c["id"]] = dict(c, s=c["start"] // F, e=(c["start"] + c["duration"]) // F, kind=kind, ti=ti, tid=tr.get("id"))
    return out


def trim(clip, edge, d):
    return {"id": "timeline.trim", "params": {"clip": clip, "edge": edge, "mode": "regular", "deltaFrames": d}}


for a in sys.argv[1:]:
    proj = Path(a).resolve()
    bk = proj.parent / f"backup-{datetime.date.today()}-loom11"; bk.mkdir(exist_ok=True)
    shutil.copy2(proj, bk / proj.name)

    # 1. "you don't"
    c = by_id(seqj(proj))
    s77, D = c[77]["s"], 3
    src74 = c[74]["source_in"] / TPS
    the = c[74]["s"] + round((SRC_THE - src74) * 24)                   # frame "The" lands on before the shift
    s = json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"],
                                  capture_output=True, text=True, check=True).stdout)
    moves = [{"clip": x["clip"], "track": t["id"], "time": (x["startFrame"] + D) * F}
             for k in ("video", "audio") for t in s[k] for x in t["items"] if x["startFrame"] >= s77]
    moves.sort(key=lambda m: -m["time"])
    span = [x["clip"] for k in ("video", "audio") for t in s[k] for x in t["items"]
            if x["startFrame"] < s77 < x["startFrame"] + x["durationFrames"] and x["clip"] not in (74, 75, 139)]
    cmds = [{"id": "timeline.move", "params": {"moves": moves, "insert": False, "linked": False}}]
    cmds += [trim(x, "out", D) for x in span + [74, 75, 139]]
    cmds += [trim(139, "in", the - c[139]["s"]),                       # insert 211 on "The"
             trim(438, "in", the - (c[438]["s"] + D)),                 # caption "The weight loss worked" on "The"
             trim(436, "out", the - c[436]["e"])]                      # "you don't" up until then
    run(proj, cmds)

    # 3. CTA captions on the spoken words
    c = by_id(seqj(proj))
    src125 = c[125]["source_in"] / TPS
    fw, fm = (c[125]["s"] + round((t - src125) * 24) for t in (SRC_WITH, SRC_MONEY))
    run(proj, [trim(534, "out", fw - c[534]["e"]), trim(536, "in", fw - c[536]["s"]),
               trim(538, "in", fm - c[538]["s"]), trim(536, "out", fm - c[536]["e"])])

    # 2. still pushes: first frame to last, one rate
    sq = seqj(proj); cmds = []; n = 0
    for ti, tr in enumerate(sq["video_tracks"]):
        if ti == 0:
            continue
        for x in tr["items"]:
            if not x["name"].lower().endswith((".jpg", ".jpeg", ".png")) or x["name"].startswith("cta-"):
                continue
            sc = x["effects"][0]["params"]["scale"]
            kfs = sc.get("keyframes") or []
            v0 = kfs[0]["value"]["Float"] if kfs else sc["value"]["Float"]
            cmds += [{"id": "effects.deleteKeyframe", "params": {"clip": x["id"], "effect": "motion", "param": "scale", "mediaTime": k["time"]}}
                     for k in kfs]
            a0, a1 = x["start"] // F, (x["start"] + x["duration"]) // F - 1
            for f, v in ((a0, v0), (a1, v0 * (1 + RATE / 100 * (a1 - a0) / 24))):
                cmds.append({"id": "effects.setParam", "params": {"clip": x["id"], "effect": "motion", "param": "scale",
                                                                  "value": round(v, 2), "keyframe": True, "time": f * F}})
            n += 1
    run(proj, cmds)
    print(f"{proj.name}: 'you don't' face held to frame {the}, block +{D} f; "
          f"CTA captions with {fw}, money-back {fm}; {n} stills re-pushed at {RATE}%/s")
