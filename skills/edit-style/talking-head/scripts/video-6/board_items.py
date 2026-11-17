#!/usr/bin/env python3
"""Client Loom 4 (2026-11-15): the tier board stays put; only the product being ranked swooshes in from the
right, the same animation every time, with the Cartoon Swipe on that product. No swoosh anywhere else.
  - the 9 V2 board slides are removed; every board now cuts in on its frame (the two that started 6 f early
    over her face, 3810 and 5642, now start on the cut, with the cutout);
  - each ranking show's board is razored 6 f in; the head plays slide-<state>.mp4 (make_boards.py: the board
    before, the new product easing in from x +1080), so it stays under her cutout on V2;
  - the Cartoon Swipe sits on the slide start (its peak, 3 f in, lands mid-slide); swipes on recap boards and on
    the non-board cuts (first insert, the 7 zoom-blur card cuts) are removed;
  - 5149 ("Not Aveli ...", 3:35) is Aleo's ranking into S (Max: Aleo must already be in S there); 5648 is board-S.
Usage: FC_HEADLESS=1 board_items.py PROJECT"""
import json, subprocess, sys
from pathlib import Path
F = 10584000000; P = sys.argv[1]
TB = Path(__file__).resolve().parent.parent / "assets/tierboard"
N = 6
# show frame: (state whose product slides in, base board, frames to cover)
SHOWS = {1037: "D", 1455: "C1", 2051: "C2", 2678: "C3", 3114: "C4", 3497: "B", 5149: "S"}
BASE = {"D": "empty", "C1": "D", "C2": "C1", "C3": "C2", "C4": "C3", "B": "C4", "S": "B"}
RECAP_FIX = {3810: 3816, 5642: 5648}       # board start -> cut frame (her cutout starts there)
def cli(*a, inp=None):
    r = subprocess.run(["filmcraft-cli", "--compact", "--project", P, *a], input=inp, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr + r.stdout)
    return r.stdout
def run(cmds):
    out = cli("run", "-", inp="".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    res = [json.loads(l) for l in out.splitlines() if l.startswith("{")]
    if not all(r.get("ok") for r in res): sys.exit(f"failed: {[r for r in res if not r.get('ok')]}")
    return res
seq = lambda: json.loads(cli("inspect", "sequence"))
s = seq(); V2, V4 = s["video"][1], s["video"][3]; SFX = s["audio"][3]
boards = sorted([c for c in V2["items"] if c["name"].startswith("board")], key=lambda c: c["startFrame"])
slides = [x["id"] for x in V2["transitions"] if x["effect"] == "slide"]
cmds = [{"id": "sequence.removeTransition", "params": {"transitions": slides}}]
for b in boards:
    if b["startFrame"] in RECAP_FIX:
        cmds.append({"id": "timeline.trim", "params": {"clip": b["clip"], "edge": "in", "mode": "regular",
                     "deltaFrames": RECAP_FIX[b["startFrame"]] - b["startFrame"], "linked": False}})
# swipes: keep only the 7 ranking shows (moved to the show frame), delete the rest
swipes = [c for c in SFX["items"] if "Swipe" in c["name"]]
keep, moves = set(), []
for T in SHOWS:
    c = min(swipes, key=lambda c: abs(c["startFrame"] - T))
    assert abs(c["startFrame"] - T) <= 6, (T, c["startFrame"])
    keep.add(c["clip"]); moves.append({"clip": c["clip"], "track": SFX["id"], "time": {"frame": T}})
cmds.append({"id": "timeline.delete", "params": {"clips": [c["clip"] for c in swipes if c["clip"] not in keep], "ripple": False}})
cmds.append({"id": "timeline.move", "params": {"moves": moves, "insert": False, "linked": False}})
paths = [str(TB / f"slide-{k}.mp4") for k in SHOWS.values()]
res = run(cmds + [{"id": "file.import", "params": {"paths": paths}}])
items = dict(zip(paths, next(r["result"]["items"] for r in res if r.get("id") == "file.import")))
proj = json.load(open(P))
def item_of(name):
    for k, v in proj["project"]["items"].items():
        m = v.get("kind", {}).get("Media", {}).get("media", {})
        for f in m.values():
            if isinstance(f, dict) and str(f.get("path", "")).endswith("/" + name): return int(k)
# each ranking show: razor the board N f in; the head plays slide-<state>.mp4 (board before + product easing in)
run([{"id": "timeline.razor", "params": {"time": (T + N) * F, "track": "V2"}} for T in SHOWS])
s = seq(); V2 = s["video"][1]
isb = lambda c: c["name"].startswith("board")
cmds = []
for T, k in SHOWS.items():
    h = next(c for c in V2["items"] if c["startFrame"] == T and isb(c))
    assert h["endFrame"] == T + N, h
    cmds.append({"id": "clip.replaceFromBin", "params": {"clips": [h["clip"]], "item": items[str(TB / f"slide-{k}.mp4")],
                                                         "keepSourceIn": False}})
    if k == "S":   # Aleo's ranking: the rest of this board run shows board-S
        end = T + N
        while True:
            c = next((c for c in V2["items"] if c["startFrame"] == end and isb(c)), None)
            if not c: break
            cmds.append({"id": "clip.replaceFromBin", "params": {"clips": [c["clip"]], "item": item_of("board-S.png"),
                                                                 "keepSourceIn": True}})
            end = c["endFrame"]
run(cmds)
s = seq()
print("V2 boards:", [(c["startFrame"], c["endFrame"], c["name"], round(c["sourceIn"] / F, 1))
                     for c in s["video"][1]["items"] if c["name"].startswith(("board", "slide"))])
print("swipes:", [c["startFrame"] for c in s["audio"][3]["items"] if "Swipe" in c["name"]])
print("V2 slides left:", [x["id"] for x in s["video"][1]["transitions"] if x["effect"] == "slide"])
