#!/usr/bin/env python3
"""Hooks 2 and 3 as clones of the approved hook-1.fcproj (user 2026-11-03: "just clone the hook-1 into 2 and 3, then
you only need to change the hook parts"). Only the opening changes:
- V1/A1: hook N's two title lines from the master (cut at the same pause points as hook 1: lead 0.15 s before a line,
  0.13 s kept after its first half, 0.18 s after its second); "losing more weight will not change that." stays hook 1's
  take, so the black card and its clicks stay in sync;
- everything from the card on (frame 97) moves by the length difference as one block, music extended to match;
- V2 under the title: hook N's own photo clip (202, 203) for line one, then hook 1's two pictures splitting line two,
  push transitions between them as in hook 1;
- the two-line title rebuilt with hook N's words, same template and motion (anchor 540,380, position 540,422, scale 85).
Usage: clone_hooks.py 2 3"""
import json, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/captions-filmcraft/scripts"))
import fc_captions as fcc

EDIT = Path(__file__).resolve().parent
ROOT = EDIT.parent
TPS, F = 254016000000, 10584000000
FPS = 24
HOOKS = {   # line-one source in/out, line-two source in/out (master seconds), title lines, photo clip
    2: dict(a=(6.51, 9.23), b=(9.28, 10.67), title=["If a woman never had dimples on", "her thighs until she lost the weight"],
            pic=ROOT / "clips/clip-202/clip-202-v4-seedance.mp4"),
    3: dict(a=(13.19, 15.49), b=(15.57, 17.78), title=["If a woman lost weight on GLP-1", "and still has loose, dimply thighs"],
            pic=ROOT / "clips/clip-203/final/clip-203-v2-1080p.mp4"),
}
OPEN = 97            # hook 1: V1 cut onto "losing more weight..." (the card starts at 98)
V1A, V1B, A1A, A1B, PIC1, PIC2, PIC3, TITLE, MUSIC = 44, 360, 45, 362, 127, 373, 556, 540, 369
PUSH = {"effect": "push", "frames": 6, "align": "center", "params": {"direction": 1, "motion_blur": 80.0}}


def run(proj, cmds):
    f = EDIT / ".clone-run.jsonl"
    f.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink()
    rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs):
        sys.exit(f"{proj.name}: {[r for r in rs if not r.get('ok')] or out.stderr[-1500:]}")
    return [r.get("result") for r in rs]


def seq(proj):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


def frames(sec):
    return round(sec * FPS)


for n in map(int, sys.argv[1:]):
    h = HOOKS[n]
    proj = EDIT / f"hook-{n}.fcproj"
    if proj.exists():
        bk = EDIT / "backup-2026-11-03-clone"; bk.mkdir(exist_ok=True); shutil.copy2(proj, bk / proj.name)
    shutil.copy2(EDIT / "hook-1.fcproj", proj)
    la, lb = frames(h["a"][1] - h["a"][0]), frames(h["b"][1] - h["b"][0])
    end = la + lb                      # new V1 cut onto "losing more..."
    d = end - OPEN
    p2 = (end + 1 - la) // 2           # line two split between hook 1's two pictures
    s = seq(proj)
    moves = [{"clip": c["clip"], "track": t["id"], "time": (c["startFrame"] + d) * F}
             for k in ("video", "audio") for t in s[k] for c in t["items"] if c["startFrame"] >= OPEN]
    moves.sort(key=lambda m: -m["time"] if d > 0 else m["time"])
    pic = run(proj, [{"id": "file.import", "params": {"paths": [str(h["pic"])]}}])[0]["items"][0]
    cmds = [{"id": "timeline.move", "params": {"moves": moves, "insert": False, "linked": False}},
            {"id": "timeline.trim", "params": {"clip": MUSIC, "edge": "out", "mode": "regular", "deltaFrames": d}},
            {"id": "timeline.delete", "params": {"clips": [V1A, V1B, A1A, A1B, PIC1, TITLE], "ripple": False}},
            {"id": "timeline.place", "params": {"item": 1, "track": "V1", "audioTrack": "A1", "frame": 0, "insert": False,
                                                "sourceIn": {"seconds": h["a"][0]}, "duration": {"frame": la}}},
            {"id": "timeline.place", "params": {"item": 1, "track": "V1", "audioTrack": "A1", "frame": la, "insert": False,
                                                "sourceIn": {"seconds": h["b"][0]}, "duration": {"frame": lb}}},
            {"id": "timeline.trim", "params": {"clip": PIC3, "edge": "out", "mode": "regular", "deltaFrames": d}},
            {"id": "timeline.trim", "params": {"clip": PIC3, "edge": "in", "mode": "regular", "deltaFrames": la + p2 - 65}},
            {"id": "timeline.trim", "params": {"clip": PIC2, "edge": "out", "mode": "regular", "deltaFrames": p2 - 21}},
            {"id": "timeline.move", "params": {"moves": [{"clip": PIC2, "track": 40, "time": la * F}], "insert": False}},
            {"id": "timeline.place", "params": {"item": pic, "track": 40, "frame": 0, "insert": False, "audio": False,
                                                "sourceIn": {"seconds": 0.04}, "duration": {"frame": la}}}]
    res = run(proj, cmds)
    new_pic = res[len(cmds) - 1]["clips"][0]
    if "seedance" in h["pic"].name:   # 720p, scaled as hook 1's clip-201 (anchor 360,640, scale 150)
        run(proj, [{"id": "effects.setParam", "params": {"clip": new_pic, "effect": "motion", "param": p, "value": v}}
                   for p, v in (("anchor", [360, 640]), ("scale", 150.0))])
    # push transitions as in hook 1 (re-applied where the moves dropped them)
    s = seq(proj)
    have = {(tr["from"], tr["to"]) for t in s["video"] for tr in t["transitions"]}
    card = next(c["clip"] for c in s["video"][1]["items"] if c["name"] == "card")
    tcmds = [{"id": "sequence.applyVideoTransition", "params": dict(PUSH, clip=a, edge="out")}
             for a, b in ((new_pic, PIC2), (PIC2, PIC3), (PIC3, card)) if (a, b) not in have]
    # title: hook N's two lines, template 6, same motion as hook 1's title
    st = dict(fcc.STYLES["6"])
    size = min(fcc.fit_size(st, t) for t in h["title"])
    gap = st["lines"][1] - st["lines"][0]
    pos = [[540, 380 + 0.35 * size - gap / 2], [540, 380 + 0.35 * size + gap / 2]]
    tcmds += [{"id": "graphics.newText", "params": {"text": h["title"][0], "position": pos[0], "size": size, "font": st["font"],
                                                     "fontStyle": st["fontStyle"], "seconds": (end + 1) / FPS, "track": 2, "time": 0}},
              {"id": "graphics.set", "params": {"props": dict(st["props"], position=pos[0])}}]
    res = run(proj, tcmds)
    title = res[len(tcmds) - 2]["clip"]
    run(proj, [{"id": "graphics.newText", "params": {"text": h["title"][1], "position": pos[1], "size": size, "font": st["font"],
                                                      "fontStyle": st["fontStyle"], "clip": title}},
               {"id": "graphics.set", "params": {"clip": title, "layer": 1, "props": dict(st["props"], position=pos[1])}}]
              + fcc.box_cmds(st, title, h["title"], size, pos)
              + [{"id": "effects.setParam", "params": {"clip": title, "effect": "motion", "param": p, "value": v}}
                 for p, v in (("anchor", [540, 380]), ("position", [540, 422]), ("scale", 85.0))]
              + [{"id": "clip.rename", "params": {"clip": title, "name": h["title"][0]}}])
    print(f"hook-{n}: lines {la}+{lb} f, block moved {d:+d} f, pictures {la}/{p2}/{end + 1 - la - p2} f, title clip {title}")
