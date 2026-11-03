#!/usr/bin/env python3
"""DCT-2190 hook card, one word at a time (user 2026-11-03: "only have LOSING first then MORE comes in").
Rebuilds the text clips inside the nested `card` sequence of hook-N.fcproj: each spoken word of
"losing more weight will not change that" adds itself on its onset frame (waveform), in hook_text.py's layout.
Usage: card_words.py hook-1.fcproj"""
import json, subprocess, sys
from pathlib import Path

CARD = ["LOSING MORE", "WEIGHT", "WILL NOT", "CHANGE THAT"]
CARD_FONT = ("Montserrat", "ExtraBold")
CARD_SIZES = [111, 186, 106, 106]
CARD_X, CARD_GAP, CAP = 128, 32, 0.727
TPS = 254016000000
# nest frames (hook frame - 98): word onsets from the voice waveform
WORDS = [(0, 0, "LOSING"), (6, 0, "LOSING MORE"), (16, 1, "WEIGHT"), (23, 2, "WILL"),
         (28, 2, "WILL NOT"), (34, 3, "CHANGE"), (42, 3, "CHANGE THAT")]
NEST_LEN = 58
SEQ_ITEM = 565
MAIN_SEQ = 42


def cli(proj, cmds):
    f = proj.with_suffix(".cw.jsonl"); f.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink(); rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs):
        sys.exit(f"{[r for r in rs if not r.get('ok')] or out.stderr[-1500:]}")
    return [r.get("result") for r in rs]


proj = Path(sys.argv[1]).resolve()
openseq = {"id": "sequence.open", "params": {"item": SEQ_ITEM}}
# find the text track inside the nest
cli(proj, [openseq, {"id": "file.save", "params": {}}])
seq = json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"], capture_output=True, text=True, check=True).stdout)
assert seq["name"] == "card", seq["name"]
v = next(i for i, t in enumerate(seq["video"]) if t["items"] and all(any(e.get("effect") == "graphic_text" for e in c["effects"]) for c in t["items"]))
old = [c["clip"] for c in seq["video"][v]["items"]]
caps_h = [CAP * z for z in CARD_SIZES]
top = 960 - (sum(caps_h) + CARD_GAP * (len(CARD) - 1)) / 2
ys = [top + sum(caps_h[:j + 1]) + CARD_GAP * j for j in range(len(CARD))]
steps = []
for k, (st, line, word) in enumerate(WORDS):
    end = WORDS[k + 1][0] if k + 1 < len(WORDS) else NEST_LEN
    lines = CARD[:line] + [word]
    steps.append((st, end, lines))
cmds = [openseq, {"id": "edit.clear", "params": {"clips": old}}]
idx = []
for st, end, lines in steps:
    cmds += [{"id": "graphics.newText", "params": {"text": lines[0], "position": [CARD_X, ys[0]], "size": CARD_SIZES[0],
                                                    "font": CARD_FONT[0], "fontStyle": CARD_FONT[1], "seconds": (end - st) / 24,
                                                    "track": v, "time": st * TPS // 24}},
             {"id": "graphics.set", "params": {"props": {"align": "left", "fill_color": "#ffffff", "stroke": False,
                                                         "shadow": False, "position": [CARD_X, ys[0]]}}}]
    idx.append((lines, len(cmds) - 2))
cmds.append({"id": "file.save", "params": {}})
res = cli(proj, cmds)
second = [openseq]
for lines, i in idx:
    clip = res[i]["clip"]
    for j in range(1, len(lines)):
        second += [{"id": "graphics.newText", "params": {"text": lines[j], "position": [CARD_X, ys[j]], "size": CARD_SIZES[j],
                                                          "font": CARD_FONT[0], "fontStyle": CARD_FONT[1], "clip": clip}},
                   {"id": "graphics.set", "params": {"clip": clip, "layer": j, "props": {
                       "align": "left", "fill_color": "#ffffff", "stroke": False, "shadow": False, "position": [CARD_X, ys[j]]}}}]
    second.append({"id": "clip.rename", "params": {"clip": clip, "name": " ".join(lines)}})
cli(proj, second + [{"id": "sequence.open", "params": {"item": MAIN_SEQ}}, {"id": "file.save", "params": {}}])
print(f"{proj.name}: card in {len(steps)} word steps")
