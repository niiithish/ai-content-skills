#!/usr/bin/env python3
"""Put the Loom 8–9 stills (2026-10-30) into the hooks in place: same slots, nothing else moves.
- A still that replaces a still: media.replaceFootage on its project item, so the clip keeps its push keyframes
  (the splits are 1080×1920 like the ones they replace, the other stills 768×1376).
- A still that replaces a video clip (the collagen clip, the low-res scale clip): cleared and placed in the same slot
  by swap_insert_clips.py, then given the same slow centred push the other stills have (+6% over the clip, to its end).
Usage: loom89_stills.py hook-1.fcproj [...]"""
import datetime, json, shutil, subprocess, sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
S = R / "scenes"
TPS = 254016000000
STILLS = {"scene-201-v2.jpg": S / "scene-201/scene-201-v3.jpg",
          "scene-202-v1.jpg": S / "scene-202/scene-202-v2.jpg",
          "scene-203-v1.jpg": S / "scene-203/scene-203-v2.jpg",
          "scene-206-v2.jpg": S / "scene-206/scene-206-v3.jpg",
          "scene-213-v3.jpg": S / "scene-213/scene-213-v4.jpg",
          "scene-215-v3.jpg": S / "scene-215/scene-215-v4.jpg",
          "scene-227-v1.jpg": S / "scene-227/scene-227-v2.jpg",
          "scene-217-v4.jpg": S / "scene-217/scene-217-v5.jpg",
          **{f"split-{n}-v1.jpg": S / f"scene-{n}/split-{n}-v2.jpg" for n in (223, 224, 225, 226)},
          # 2026-10-30 (user): same woman, place, light and framing in both halves, her left leg only
          **{f"split-{n}-v2.jpg": S / f"scene-{n}/split-{n}-v3.jpg" for n in (223, 224, 225, 226)},
          # 2026-10-30 (user): as the reference does it: full length, face shown, different place and outfit
          **{f"split-{n}-v3.jpg": S / f"scene-{n}/split-{n}-v4.jpg" for n in (223, 224, 225, 226)}}
CLIPS = {}
PUSH = 1.06


def cli(proj, cmds):
    f = proj.with_suffix(".stills.jsonl"); f.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink(); rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in rs):
        sys.exit(f"{proj.name}: {[r for r in rs if not r.get('ok')] or out.stderr[-1500:]}")
    return [r.get("result") for r in rs]


def v2(proj):
    for it in json.load(open(proj))["project"]["items"].values():
        k = it.get("kind")
        if isinstance(k, dict) and "Sequence" in k:
            return k["Sequence"]["video_tracks"][1]["items"]


for a in [a for a in sys.argv[1:] if a.endswith(".fcproj")]:
    proj = Path(a).resolve()
    bk = proj.parent / f"backup-{datetime.date.today()}-loom89stills"; bk.mkdir(exist_ok=True)
    if not (bk / proj.name).exists():
        shutil.copy2(proj, bk / proj.name)
    clips = v2(proj)
    # 1. stills: swap the footage under the clip
    cmds = [{"id": "media.replaceFootage", "params": {"item": c["item"], "path": str(STILLS[c["name"]])}}
            for c in clips if c["name"] in STILLS]
    cli(proj, cmds)
    # 2. video clips: a still in the same slot
    hit = [c["name"] for c in clips if c["name"] in CLIPS]
    if hit:
        out = subprocess.run([sys.executable, str(Path(__file__).with_name("swap_insert_clips.py")), str(proj)]
                             + [f"{n}={CLIPS[n]}" for n in hit], capture_output=True, text=True)
        print(out.stdout.strip() or out.stderr[-1500:])
        new = [c for c in v2(proj) if c["name"] in {CLIPS[n].name for n in hit}]
        fx = []
        for c in new:
            sc = next(e for e in c["effects"] if e.get("effect") == "motion")["params"]["scale"]["value"]["Float"]
            for t, val in ((c["start"], sc), (c["start"] + c["duration"], round(sc * PUSH, 2))):
                fx.append({"id": "effects.setParam", "params": {"clip": c["id"], "effect": "motion", "param": "scale",
                                                                "value": val, "keyframe": True, "time": t}})
        cli(proj, fx)
    print(f"{proj.name}: {len(cmds)} stills swapped, {len(hit)} clips made stills")
