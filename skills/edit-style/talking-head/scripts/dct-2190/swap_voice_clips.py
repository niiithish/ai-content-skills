#!/usr/bin/env python3
"""Client Loom 11 (2026-11-03), wrong bottle: put the real-bottle talking clips in their slots, with the user's
ElevenLabs voice (made by make_voice_clip.py: 1.12x, -16 LUFS; A1 gain -4.9 dB as clip-15 v4, = master -21.1 LUFS).
- clip-15 v4 -> v5: same 69 f slot (replace footage); caption "That's why I always" | "recommend this body oil" split
  moved onto "recommend" (clip frame 27). Its zoom (100->115 at clip frames 37-42) stays.
- CTA (master piece 125/126, 160 f) -> clip-19 v3 in the same slot, same 160 f; its centred push / 110% step redone
  on the new caption starts (talk_motion's rule); captions on the new words (frames 33 "So", 52 "first",
  108 "with", 129 "money-back"). Nothing else moves. Usage: swap_voice_clips.py hook-1.fcproj [...]"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path
F, R = 10584000000, Path(__file__).resolve().parents[1]
NEW15 = R / "edit/talking-media/clip-15-v5-voice-1.12x.mp4"
NEW19 = R / "edit/talking-media/clip-19-v3-voice-1.12x.mp4"
REC15 = 27
CTA_WORDS = {"So you can get your": 33, "first bottle for 40% off": 52, "with a 60-day": 108, "money-back guarantee": 129}

def cli(proj, cmds):
    f = proj.with_suffix(".vs.jsonl"); f.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True); f.unlink()
    rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs): sys.exit(f"{proj.name}: {[r for r in rs if not r.get('ok')] or out.stderr[-1500:]}")
    return [r.get("result") for r in rs]

def seq(proj):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"], capture_output=True, text=True, check=True).stdout)

def clips(s):
    return [dict(c, k=k[0] + str(i + 1)) for k in ("video", "audio") for i, t in enumerate(s[k]) for c in t["items"]]

def tr(c, edge, d):
    return {"id": "timeline.trim", "params": {"clip": c, "edge": edge, "mode": "regular", "deltaFrames": d}}

def move_split(left, right, target):
    d = target - left["endFrame"]
    if d == 0: return []
    return [tr(right["clip"], "in", d), tr(left["clip"], "out", d)] if d > 0 else [tr(left["clip"], "out", d), tr(right["clip"], "in", d)]

for a in sys.argv[1:]:
    proj = Path(a).resolve()
    bk = proj.parent / f"backup-{datetime.date.today()}-voiceswap"; bk.mkdir(exist_ok=True); shutil.copy2(proj, bk / proj.name)
    s = seq(proj); cs = clips(s)
    cap = {c["name"]: c for c in cs if c["k"] == "v3"}
    keep = lambda cs: sorted((c["k"], c["startFrame"], c["endFrame"], c["name"]) for c in cs if c["k"] != "v3" and c["k"] != "v1" and c["k"] != "a1")
    before = keep(cs)
    # clip 15: same slot, new footage
    v15 = next(c for c in cs if c["k"] == "v1" and c["name"] == "clip-15-v4-voice-1.12x.mp4")
    item15 = next(it for it in s.get("items", [])) if False else None
    d = json.load(open(proj))
    item15 = next(int(k) for k, it in d["project"]["items"].items() if it.get("name") == "clip-15-v4-voice-1.12x.mp4")
    T = v15["startFrame"]
    cmds = [{"id": "media.replaceFootage", "params": {"item": item15, "path": str(NEW15)}}]
    cmds += move_split(cap["That’s why I always"], cap["recommend this body oil"], T + REC15)
    # CTA: master piece -> clip-19 v3, same slot
    c530 = cap["I’ll leave a link below"]; S = c530["startFrame"]
    old = [c for c in cs if c["k"] in ("v1", "a1") and c["startFrame"] == S and c["name"] == "talking-head-enhanced.mp4"]
    assert len(old) == 2 and all(c["endFrame"] - S == 160 for c in old), old
    item19 = cli(proj, [{"id": "file.import", "params": {"paths": [str(NEW19)]}}])[0]["items"][0]
    cmds += [{"id": "edit.clear", "params": {"clips": [c["clip"] for c in old]}},
             {"id": "timeline.place", "params": {"item": item19, "track": "V1", "audioTrack": "A1", "time": S * F, "duration": 160 * F, "insert": False}}]
    res = cli(proj, cmds)
    new = res[cmds.index(cmds[-1])]["clips"]
    s2 = seq(proj); cs2 = clips(s2)
    v19 = next(c for c in cs2 if c["k"] == "v1" and c["startFrame"] == S); a19 = next(c for c in cs2 if c["k"] == "a1" and c["startFrame"] == S)
    marks = [0, 52, 108, 160]                                  # talk_motion: 100 / 110 / 100, +3 % per 3 s
    fx = [{"id": "clip.audioGain", "params": {"clips": [a19["clip"]], "mode": "set", "db": -4.9}}]
    for i, (x, y) in enumerate(zip(marks, marks[1:])):
        v0 = 100.0 if i % 2 == 0 else 110.0
        for f, v in ((x, v0), (y - 1, v0 + 3 * (y - x) / 72)):
            fx.append({"id": "effects.setParam", "params": {"clip": v19["clip"], "effect": "motion", "param": "scale", "value": round(v, 2), "keyframe": True, "time": (S + f) * F}})
    cap2 = {c["name"]: c for c in cs2 if c["k"] == "v3"}
    names = ["I’ll leave a link below"] + list(CTA_WORDS)
    for l, r in zip(names, names[1:]):
        fx += move_split(cap2[l], cap2[r], S + CTA_WORDS[r])
        cap2[l] = dict(cap2[l], endFrame=S + CTA_WORDS[r])
    cli(proj, fx)
    s3 = seq(proj); cs3 = clips(s3)
    v1 = [(c["startFrame"], c["endFrame"], c["name"]) for c in cs3 if c["k"] == "v1" and c["startFrame"] in (T, S)]
    print(f"{proj.name}: V1 {v1}; CTA captions {[(c['name'], c['startFrame'] - S) for c in cs3 if c['k'] == 'v3' and c['startFrame'] >= S]}; "
          f"15 split at +{cap2 and next(c['startFrame'] for c in cs3 if c['name'] == 'recommend this body oil') - T}; other tracks unchanged: {keep(cs3) == before}")
