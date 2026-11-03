#!/usr/bin/env python3
"""DCT-2190 hook text (AGENTS 2026-11-02: the hook copies the reference). On the captions track of hook-N.fcproj:
- the title (first caption) becomes two template-6 lines on white boxes, centred at TITLE_Y, over the hook photo;
- the next captions up to her face ("losing more" ... "change that.") become the black card: big white bold
  capitals, each new word adding a line ("LOSING MORE / WEIGHT / WILL NOT / CHANGE THAT"), same frames.
Run after fc_captions build and caption_layout.py. Usage: hook_text.py hook-1.fcproj"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/captions-filmcraft/scripts"))
import fc_captions as fcc

TITLE = ["If a woman finally lost the weight", "and her thighs look worse than before"]
CARD = ["LOSING MORE", "WEIGHT", "WILL NOT", "CHANGE THAT"]
TITLE_Y = 380            # centre of the two boxes (reference: about 20% down)
CARD_FONT = ("Montserrat", "ExtraBold")
# sizes measured on the reference card (5.9 s): a left-aligned block about 825 px wide centred on the frame,
# "LOSING MORE" 825 px wide, "WEIGHT" the biggest (cap 145 px), the last line small (cap 77 px); gap 32 px
CARD_SIZES = [111, 186, 106, 106]
CARD_X, CARD_GAP, CAP = 128, 32, 0.727      # left edge, gap between lines, Montserrat cap height / size
TPS = 254016000000


def fc(proj, *a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), *a],
                                     capture_output=True, text=True, check=True).stdout)


def run(proj, cmds):
    f = proj.with_suffix(".text.jsonl")
    f.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink()
    rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs):
        sys.exit(f"{[r for r in rs if not r.get('ok')] or out.stderr[-1500:]}")
    return [r.get("result") for r in rs]


proj = Path(sys.argv[1]).resolve()
bk = proj.parent / f"backup-{datetime.date.today()}-hooktext"; bk.mkdir(exist_ok=True)
shutil.copy2(proj, bk / proj.name)
s = fc(proj, "inspect", "sequence")
v = next(i for i, t in enumerate(s["video"]) if t["items"] and all(any(e.get("effect") == "graphic_text" for e in c["effects"]) for c in t["items"]))
caps = sorted(s["video"][v]["items"], key=lambda c: c["startFrame"])
title, card = caps[0], caps[1:1 + len(CARD)]
st = dict(fcc.STYLES["6"])
size = min(fcc.fit_size(st, t) for t in TITLE)
gap = st["lines"][1] - st["lines"][0]
pos = [[540, TITLE_Y + 0.35 * size - gap / 2], [540, TITLE_Y + 0.35 * size + gap / 2]]   # baselines around the box centre
cmds = [{"id": "edit.clear", "params": {"clips": [c["clip"] for c in [title] + card]}}]
made = []
cmds += [{"id": "graphics.newText", "params": {"text": TITLE[0], "position": pos[0], "size": size, "font": st["font"],
                                                "fontStyle": st["fontStyle"], "seconds": title["durationFrames"] / 24,
                                                "track": v, "time": title["startFrame"] * TPS // 24}},
         {"id": "graphics.set", "params": {"props": dict(st["props"], position=pos[0])}}]
made.append(("title", len(cmds) - 2))
for k, c in enumerate(card):
    n = k + 1
    caps_h = [CAP * z for z in CARD_SIZES]
    top = 960 - (sum(caps_h) + CARD_GAP * (len(CARD) - 1)) / 2
    ys = [top + sum(caps_h[:j + 1]) + CARD_GAP * j for j in range(n)]   # baselines in fixed slots: earlier words never move
    cmds += [{"id": "graphics.newText", "params": {"text": CARD[0], "position": [CARD_X, ys[0]], "size": CARD_SIZES[0],
                                                    "font": CARD_FONT[0], "fontStyle": CARD_FONT[1],
                                                    "seconds": c["durationFrames"] / 24, "track": v,
                                                    "time": c["startFrame"] * TPS // 24}},
             {"id": "graphics.set", "params": {"props": {"align": "left", "fill_color": "#ffffff", "stroke": False,
                                                         "shadow": False, "position": [CARD_X, ys[0]]}}}]
    made.append((ys, len(cmds) - 2))
cmds.append({"id": "file.save", "params": {}})
res = run(proj, cmds)
second = []
for what, i in made:
    clip = res[i]["clip"]
    if what == "title":
        second += [{"id": "graphics.newText", "params": {"text": TITLE[1], "position": pos[1], "size": size,
                                                          "font": st["font"], "fontStyle": st["fontStyle"], "clip": clip}},
                   {"id": "graphics.set", "params": {"clip": clip, "layer": 1, "props": dict(st["props"], position=pos[1])}}]
        second += fcc.box_cmds(st, clip, TITLE, size, pos)
    else:
        for j, y in enumerate(what[1:], 1):
            second += [{"id": "graphics.newText", "params": {"text": CARD[j], "position": [CARD_X, y], "size": CARD_SIZES[j],
                                                              "font": CARD_FONT[0], "fontStyle": CARD_FONT[1], "clip": clip}},
                       {"id": "graphics.set", "params": {"clip": clip, "layer": j, "props": {
                           "align": "left", "fill_color": "#ffffff", "stroke": False, "shadow": False, "position": [CARD_X, y]}}}]
run(proj, second + [{"id": "file.save", "params": {}}])
print(f"{proj.name}: title two lines at y {TITLE_Y}, card {len(card)} clips ({card[0]['startFrame']}-{card[-1]['startFrame'] + card[-1]['durationFrames']})")
