#!/usr/bin/env python3
"""video-23 hooks 2/3: add the template-1 captions of the new opening (plan blocks before frame n) to V3, the same
way fc_captions build makes them, without touching hook 1's body captions (the user's tweaks stay). Captions that
start inside the opening's split shot go onto the seam (motion position [540, 506]), like seam_captions.py.
Usage: add_opening_captions.py 2|3   (FilmCraft closed)"""
import json, re, shutil, subprocess, sys, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/skills/captions-filmcraft/scripts"))
import fc_captions as F

EDIT = Path(__file__).resolve().parent
HOOK = sys.argv[1]
PROJ = EDIT / f"hook-{HOOK}.fcproj"
TPS, FPS = 254016000000, 24
T = TPS // FPS
if subprocess.run(["pgrep", "-x", "filmcraft"], capture_output=True).returncode == 0:
    sys.exit("FilmCraft is open: save and quit it first")
op = json.load(open(EDIT / f".hook-{HOOK}.opening.json"))
n, split0 = op["n"], op["starts"][-1]
plan = json.load(open(EDIT.parent / f"captions/hook-{HOOK}.captions.json"))
blocks = [b for b in plan["blocks"] if b["start"] < n]
assert blocks[-1]["end"] == n, blocks[-1]
d = json.load(open(PROJ))
s = next(i for i in d["project"]["items"].values() if "Sequence" in i["kind"])["kind"]["Sequence"]
v3 = s["video_tracks"][2]["items"]
assert min(c["start"] for c in v3) >= n * T, "opening already has captions"
bk = EDIT / f"backup-{datetime.date.today()}-hook{HOOK}-captions"
bk.mkdir(exist_ok=True)
shutil.copy2(PROJ, bk / PROJ.name)

st = dict(F.STYLES["1"])
F.ensure_font(st)
cmds, lines = [], []
for b in blocks:
    text = re.sub(r"[,.!?;:]+(?=\s|$)", "", b["text"].upper())
    ls = F.greedy_lines(st, text)
    size = min(F.fit_size(st, t) for t in ls)
    ys = st["lines"] if len(ls) == 2 else [st["single"]]
    pos = [[540, y] for y in ys]
    cmds.append({"id": "graphics.newText", "params": {
        "text": ls[0], "position": pos[0], "size": size, "font": st["font"], "fontStyle": st["fontStyle"],
        "seconds": (b["end"] - b["start"]) / FPS, "track": 2, "time": b["start"] * T}})
    cmds.append({"id": "graphics.set", "params": {"props": dict(st["props"], position=pos[0])}})
    lines.append((len(cmds) - 2, ls, size, pos, b))
cmds.append({"id": "file.save", "params": {}})
res = F.cli(PROJ, cmds)
second, seam = [], []
for i, ls, size, pos, b in lines:
    clip = res[i]["result"]["clip"]
    if len(ls) == 2:
        second += [{"id": "graphics.newText", "params": {"text": ls[1], "position": pos[1], "size": size,
                                                          "font": st["font"], "fontStyle": st["fontStyle"], "clip": clip}},
                   {"id": "graphics.set", "params": {"clip": clip, "layer": 1, "props": dict(st["props"], position=pos[1])}}]
    second += F.box_cmds(st, clip, ls, size, pos)
    if b["start"] >= split0:
        seam.append({"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "position",
                                                          "value": [540, 506]}})
F.cli(PROJ, second + seam + [{"id": "file.save", "params": {}}])
# project name back (FilmCraft names a project after its file anyway, but keep it explicit)
d = json.load(open(PROJ))
d["project"]["name"] = d["project"]["root"]["name"] = f"hook-{HOOK}"
PROJ.write_text(json.dumps(d, separators=(",", ":"), ensure_ascii=False))
s = next(i for i in d["project"]["items"].values() if "Sequence" in i["kind"])["kind"]["Sequence"]
got = sorted((c["start"] // T, (c["start"] + c["duration"]) // T, c["name"]) for c in s["video_tracks"][2]["items"]
             if c["start"] < n * T)
print(f"{PROJ.name}: {len(got)} opening captions, {len(seam)} on the seam; backup {bk}")
for g in got:
    print("  ", g)
