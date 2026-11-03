#!/usr/bin/env python3
"""Heals the talking-head jump cuts that fall mid-phrase (client Loom, 2026-10-24: "the jump cut is on firmer ... we only
want jump cuts where the new text starts"). Pacing cut every pause, including tiny ones inside a phrase ("needs to get |
firmer first"); the removed bit there is only 0.04-0.38 s. Healing puts it back: the clip after the cut is removed, the
clip before it runs on through the same source, and every later clip on every track moves right by the restored time.
Cuts at a clause break stay, and a caption starts on each of them. Which cuts are healed is --pairs, word pairs (the
last word before the cut | the first after it) picked by reading the script, or --at, the cuts at those frames
(declutter_cuts.py passes it). Needs captions/<stem>.pk.json (fc_captions.py words).
Usage: heal_cuts.py edit/hook-N.fcproj (--pairs "get|firmer,is|thinner" | --at F1,F2,...) [--dry]. Then rerun the captions pipeline (words, plan, build, snap, cta, check)."""
import datetime, json, re, shutil, subprocess, sys
from pathlib import Path

TPS = 254016000000
PROJ = Path(sys.argv[1]).resolve()
DRY = "--dry" in sys.argv
HEAL = {tuple(p.split("|")) for p in sys.argv[sys.argv.index("--pairs") + 1].lower().split(",")} if "--pairs" in sys.argv else set()
AT = {int(f) for f in sys.argv[sys.argv.index("--at") + 1].split(",")} if "--at" in sys.argv else None
W = json.load(open(PROJ.parent.parent / "captions" / f"{PROJ.stem}.pk.json"))


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


def word(w):
    return re.sub(r"[^\w']", "", w.lower().replace("’", "'"))


def run(cmds):
    script = PROJ.parent / ".fc-heal.jsonl"
    script.write_text("".join(json.dumps(x) + "\n" for x in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
    script.unlink()
    bad = [r for r in (json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")) if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")


s = fc("inspect", "sequence")
v1 = sorted(s["video"][0]["items"], key=lambda c: c["startFrame"])
heals = []
for a, b in zip(v1, v1[1:]):
    f = b["startFrame"]
    i = min(range(len(W)), key=lambda k: abs(W[k][1] - f / 24))
    if f in AT if AT is not None else abs(W[i][1] - f / 24) < 0.25 and (word(W[i - 1][0]), word(W[i][0])) in HEAL:
        g = round((b["sourceIn"] - a["sourceOut"]) / TPS * 24)
        heals.append((f, g))
        print(f"  heal {f / 24:7.2f}s  +{g} frames  {W[i - 1][0]} | {W[i][0]}")
print(f"{len(heals)} of {len(v1) - 1} cuts healed, {sum(g for _, g in heals) / 24:.2f}s put back")
if DRY or not heals:
    sys.exit()
bk = PROJ.parent / f"backup-{datetime.date.today()}-heal"
bk.mkdir(exist_ok=True)
if not (bk / PROJ.name).exists():
    shutil.copy2(PROJ, bk / PROJ.name)
for f, g in sorted(heals, reverse=True):      # last first, so earlier frames stay put
    s = fc("inspect", "sequence")
    tracks = s["video"] + s["audio"]
    cmds, moves = [], []
    for t in (s["video"][0], s["audio"][0]):   # the talking head: picture and sound
        a = next(c for c in t["items"] if c["endFrame"] == f)
        b = next(c for c in t["items"] if c["startFrame"] == f)
        cmds += [{"id": "edit.clear", "params": {"clips": [b["clip"]]}}]
        cmds_trim = {"id": "timeline.trim", "params": {"clip": a["clip"], "edge": "out", "mode": "regular",
                                                       "deltaFrames": g + b["durationFrames"]}}
        moves_skip = b["clip"]
        cmds.append(("trim", cmds_trim, moves_skip))
    skip = {x[2] for x in cmds if isinstance(x, tuple)}
    for ti, t in enumerate(tracks):
        for c in t["items"]:
            if c["clip"] in skip:
                continue
            if c["startFrame"] >= f:
                moves.append({"clip": c["clip"], "track": t["id"], "time": (c["startFrame"] + g) * TPS // 24})
            elif c["endFrame"] > f and t not in (s["video"][0], s["audio"][0]):
                cmds.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": g}})
    moves.sort(key=lambda m: -m["time"])
    order = [x for x in cmds if not isinstance(x, tuple) and x["id"] == "edit.clear"]
    order += [{"id": "timeline.move", "params": {"moves": moves, "insert": False, "linked": False}}] if moves else []
    order += [x[1] for x in cmds if isinstance(x, tuple)]
    order += [x for x in cmds if not isinstance(x, tuple) and x["id"] == "timeline.trim"]
    run(order)
