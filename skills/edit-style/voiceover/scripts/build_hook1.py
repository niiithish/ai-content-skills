#!/usr/bin/env python3
"""Lays the Hook 1 shots (1-14) on V1 of edit/hook-1-v2.fcproj, over its voiceover (scratch-1.1x.wav on A1, already sped up
1.1x and tightened). Each PLAN.md time (timed to the 1.0x scratch read) is divided by 1.1 and mapped through the A1 pieces to
where that moment now sits; a time that fell in a cut pause snaps to the next piece. Each shot uses its 1080p final (else its
newest draft). Start-to-end-frame clips (1, 4a, 10c) are sped up to play whole in their slot, so their end state is seen.
9d (top) and 9e (bottom, on V2) are the 50/50 split. Clip sound is off.
Run only while FilmCraft does not have the project open (it writes the file headless)."""
import glob, json, re, subprocess, sys
from pathlib import Path

V = Path(__file__).resolve().parents[1]
EDIT = V / "edit"
PROJ = EDIT / "hook-1-v2.fcproj"
SPEED, FPS, TPS = 1.1, 30, 254016000000
SPLIT = {"9d": "9e"}
WHOLE = {"1", "4a", "10c", "11b"}  # start/end-frame clips: play all of it


def ver(f):
    return int(re.search(r"-v(\d+)(-1080p)?\.mp4$", f)[1])


def clip_for(s):
    n = re.match(r"[0-9]+", s)[0]
    d = V / "clips" / f"clip-{n}" / (f"clip-{s}" if s != n else "")
    fs = glob.glob(str(d / "final" / f"clip-{s}-v*-1080p.mp4")) or glob.glob(str(d / f"clip-{s}-v*.mp4"))
    return max(fs, key=ver) if fs else None


def cli(cmds):
    script = EDIT / ".fc-run.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    return [r.get("result") for r in res]


def seq():
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "inspect", "sequence"], capture_output=True, text=True)
    d = json.loads(out.stdout)
    return d.get("result", d)


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)


def mapper(pieces):
    def at(t):  # 1.0x scratch seconds -> timeline frame
        u = t / SPEED * TPS
        for p in pieces:
            if u < p["sourceIn"]:
                return p["startFrame"]
            if u < p["sourceOut"]:
                return p["startFrame"] + round((u - p["sourceIn"]) / TPS * FPS)
        return pieces[-1]["endFrame"]
    return at


def plan():
    rows, end = {}, 0
    for l in (V / "PLAN.md").read_text().splitlines():
        if m := re.match(r"^\|\s*(\d+[a-z]?)\s*\|\s*([\d.]+)\s*[–-]\s*([\d.]+)\s*s\s*\|", l):
            rows[m[1]] = float(m[2]); end = float(m[3])
    return rows, end


def build():
    s = seq()
    if s["video"][0]["items"]:
        sys.exit("V1 already has clips: back the project up and clear V1 first (it may hold the user's tweaks)")
    pieces = sorted(s["audio"][0]["items"], key=lambda c: c["startFrame"])
    at = mapper(pieces)
    rows, end = plan()
    order = sorted(rows, key=rows.get)
    shots = []
    for i, k in enumerate(order):
        f0 = at(rows[k]); f1 = at(rows[order[i + 1]]) if i + 1 < len(order) else pieces[-1]["endFrame"]
        shots.append({"shot": k, "f0": f0, "f1": f1, "path": clip_for(k)})
    shots += [{**x, "shot": SPLIT[x["shot"]], "path": clip_for(SPLIT[x["shot"]]), "track": "V2"} for x in shots if x["shot"] in SPLIT]
    assert all(x["path"] for x in shots), [x["shot"] for x in shots if not x["path"]]
    paths = sorted({x["path"] for x in shots})
    item = dict(zip(paths, cli([{"id": "file.import", "params": {"paths": paths}}, {"id": "file.save", "params": {}}])[0]["items"]))
    # start/end-frame clips first, at full length, then sped up into their slot; the rest are trimmed to their slot
    first = [x for x in shots if x["shot"] in WHOLE] + [x for x in shots if x["shot"] not in WHOLE]
    placed = []
    for group in (first[:len(WHOLE)], first[len(WHOLE):]):
        cmds = []
        for x in group:
            full = round(dur(x["path"]) * FPS)
            n = full if x["shot"] in WHOLE else x["f1"] - x["f0"]
            cmds.append({"id": "timeline.place", "params": {"item": item[x["path"]], "track": x.get("track", "V1"), "frame": x["f0"],
                                                            "sourceIn": 0, "duration": n * TPS // FPS, "insert": False, "audio": False}})
        ids = [(r.get("clips") or [r.get("clip")])[0] for r in cli(cmds + [{"id": "file.save", "params": {}}])[:-1]]
        post = [{"id": "clip.fillFrame", "params": {"clips": ids}}]  # first: it resets position
        for x, c in zip(group, ids):
            need, have = (x["f1"] - x["f0"]) / FPS, dur(x["path"])
            if x["shot"] in WHOLE or have < need:  # whole clip into the slot, or stretch a short one to reach the next cut
                x["speed"] = round(100 * have / (need + 0.5 / FPS), 2)  # half a frame over, so no 1-frame gap
                post.append({"id": "clip.speedDuration", "params": {"clips": [c], "speed": x["speed"], "ripple": False}})
            if x["shot"] in SPLIT or x["shot"] in SPLIT.values():  # middle half of the height, above or below the seam (user: top/bottom, 2026-11-02)
                post += [{"id": "effects.apply", "params": {"clips": [c], "effect": "crop"}},
                         {"id": "effects.setParam", "params": {"clip": c, "effect": "crop", "param": "top", "value": 25}},
                         {"id": "effects.setParam", "params": {"clip": c, "effect": "crop", "param": "bottom", "value": 25}},
                         {"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "position",
                                                               "value": [540, 480 if x["shot"] in SPLIT else 1440]}}]
        cli(post + [{"id": "file.save", "params": {}}])
        placed += list(zip(group, ids))
    print(f"placed {len(placed)} clips on {PROJ.name}, picture ends {shots[len(order) - 1]['f1'] / FPS:.1f} s")
    for x, _ in sorted(placed, key=lambda p: p[0]["f0"]):
        print(f"  {x['shot']:>4} {x['f0'] / FPS:6.2f} {(x['f1'] - x['f0']) / FPS:4.1f}s {Path(x['path']).name}"
              + (f" @{x['speed']}%" if x.get("speed") else "") + (" (V2)" if x.get("track") else ""))


if __name__ == "__main__":
    build()
