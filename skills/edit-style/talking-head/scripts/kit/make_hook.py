#!/usr/bin/env python3
"""Makes edit/hook-N.fcproj (N = 2, 3) as a clone of the user's hook-1.fcproj with only the opening swapped
(user 2026-10-29: "clone the hook-1 to hook-2 and 3 and then only change the beginning"; video-4's make_hook.py rule).
Hook 1's opening (its first V1/A1 clip, the inserts and captions that start in it) is cleared; the body moves by the
length difference as one block, nothing inside it moving against anything else; hook N's opening comes from the
current hook-N.fcproj: its talking clip with the same trim, its inserts in the same slots (still push 100 -> 106%),
its opening captions from captions/hook-N.captions.json (built on a spare track, then moved onto V3).
Then caption_zones.py places the captions and add_music.py re-lays the music to the new length. The old hook-N goes to edit/backup-<date>-clone/.
Usage: make_hook.py 2 3"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
SRC = EDIT / "hook-1.fcproj"
TPS, FPS = 254016000000, 24
F = TPS // FPS
PUSH = 1.06
FCC = Path.home() / ".claude/skills/captions-filmcraft/scripts/fc_captions.py"


def cli(proj, cmds, save_as=None):
    script = EDIT / ".fc-run.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    args = ["filmcraft-cli", "--compact", "--project", str(proj), "run", str(script)] + (["--save-as", str(save_as)] if save_as else [])
    out = subprocess.run(args, capture_output=True, text=True)
    script.unlink()
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    return [r.get("result") for r in res]


def seq(proj):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


def find(name):
    for d in ("edit/draft-media", "scenes/all", "clips"):
        hit = sorted((ROOT / d).rglob(name))
        if hit:
            return hit[0].resolve()
    sys.exit(f"no media file {name}")


def probe(p):
    w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                           "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.split(",")
    return int(w), int(h)


def make(n):
    proj = EDIT / f"hook-{n}.fcproj"
    old = seq(proj)
    v = old["video"][0]["items"][0]
    L = v["endFrame"]
    open_ins = [c for c in old["video"][1]["items"] if c["startFrame"] < L]
    plan = json.load(open(ROOT / "captions" / f"hook-{n}.captions.json"))
    heads = [b for b in plan["blocks"] if b["start"] < L]

    bk = EDIT / f"backup-{datetime.date.today()}-clone"; bk.mkdir(exist_ok=True)
    shutil.copy2(proj, bk / proj.name)
    shutil.copy2(ROOT / "captions" / f"hook-{n}.captions.json", bk / f"hook-{n}.captions.json")
    cli(SRC, [], save_as=proj)                       # hook-1 saved as hook-N (the project takes the new name)

    s = seq(proj)
    H = s["video"][0]["items"][0]["endFrame"]
    a1 = s["audio"][0]["items"][0]
    head = [s["video"][0]["items"][0]["clip"], a1["clip"]] + \
           [c["clip"] for t in s["video"][1:] for c in t["items"] if c["startFrame"] < H]
    if any(c["endFrame"] > H for t in s["video"][1:] for c in t["items"] if c["startFrame"] < H):
        sys.exit("a hook-1 insert or caption runs past its opening")
    d = L - H
    body = [(f"{k}{i + 1}", c) for k, kind in (("V", "video"), ("A", "audio")) for i, tr in enumerate(s[kind])
            for c in tr["items"] if c["startFrame"] >= H]
    order = sorted(body, key=lambda tc: tc[1]["startFrame"], reverse=d > 0)
    talk = find(v["name"])
    stills = [find(c["name"]) for c in open_ins]
    items = cli(proj, [{"id": "edit.clear", "params": {"clips": head}},
                       {"id": "timeline.move", "params": {"insert": False, "moves": [
                           {"clip": c["clip"], "track": t, "time": (c["startFrame"] + d) * F} for t, c in order]}},
                       {"id": "file.import", "params": {"paths": [str(talk)] + [str(p) for p in stills]}},
                       {"id": "file.save", "params": {}}])[-2]["items"]
    place = [{"id": "timeline.place", "params": {"item": items[0], "track": "V1", "audioTrack": "A1", "frame": 0, "insert": False,
                                                 "sourceIn": v["sourceIn"], "duration": L * F}}]
    place += [{"id": "timeline.place", "params": {"item": it, "track": "V2", "frame": c["startFrame"], "insert": False,
                                                  "duration": c["durationFrames"] * F, "video": True, "audio": False}}
              for it, c in zip(items[1:], open_ins)]
    res = cli(proj, place + [{"id": "file.save", "params": {}}])[1:-1]
    fx = []
    for r, p, c in zip(res, stills, open_ins):
        w, h = probe(p); sc = max(1080 / w, 1920 / h) * 100
        if p.suffix == ".mp4":
            if abs(sc - 100) > 0.3:
                fx.append({"id": "effects.setParam", "params": {"clip": r["clips"][0], "effect": "motion", "param": "scale", "value": round(sc, 2)}})
            continue
        fx += [{"id": "effects.setParam", "params": {"clip": r["clips"][0], "effect": "motion", "param": "scale", "value": round(val, 2),
                                                     "keyframe": True, "time": f * F}}
               for val, f in ((sc, c["startFrame"]), (sc * PUSH, c["endFrame"] - 1))]
    cli(proj, fx + [{"id": "sequence.deleteTracks", "params": {"video": "empty"}}, {"id": "file.save", "params": {}}])

    # the opening's captions: built alone on a spare top track, moved onto V3 beside hook-1's body captions
    sys.path.insert(0, str(FCC.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("fcc", FCC); fcc = importlib.util.module_from_spec(spec); spec.loader.exec_module(fcc)
    s = seq(proj); nv = len(s["video"])
    json.dump(dict(plan, project=str(proj), cuts=fcc.cuts_of(s), end=s["durationFrames"], blocks=heads),
              open(ROOT / "captions" / f"{proj.stem}.captions.json", "w"), indent=1, ensure_ascii=False)
    r = subprocess.run([str(FCC), "build", str(proj), "-t", "6", "--one-line", "--track", f"V{nv + 1}"], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    top = seq(proj)["video"][nv]["items"]
    cli(proj, [{"id": "timeline.move", "params": {"insert": False, "moves": [
                   {"clip": c["clip"], "track": f"V{nv}", "time": c["startFrame"] * F} for c in top]}},
               {"id": "sequence.deleteTrack", "params": {"track": f"V{nv + 1}"}}]
              + [{"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "position", "value": [540, 1050]}}
                 for c in top] + [{"id": "file.save", "params": {}}])
    print(f"{proj.name}: opening {v['name']} {L} f (hook-1 {H} f), body moved {d:+d} frames, "
          f"{len(open_ins)} opening insert(s), {len(top)} opening captions")


for n in [int(a) for a in sys.argv[1:] if a.isdigit()]:
    make(n)
