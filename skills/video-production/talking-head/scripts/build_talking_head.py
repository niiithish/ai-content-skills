#!/usr/bin/env python3
"""Builds video-N/edit/talking-head.fcproj: every talking clip's 1080p final back to back, untrimmed, in story order, on
V1/A1. The order is the clip manifest's (clips/clips-batch.json, which is the edit order), talking shots only (numbered
below 200; inserts are 201 up), or --order 1a,1b,2,...
Finals come from each shot's versioned final/ file (the newest -vK-1080p.mp4), never clips/all (no Link Media popups).
With --mp3 it also writes audio/NN-clip-X.mp3 (320k, play order) for the ElevenLabs voice change.
Usage: build_talking_head.py video-N [--order 1a,1b,...] [--name talking-head] [--mp3]"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
EDIT = ROOT / "edit"
NAME = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else "talking-head"
PROJ = EDIT / f"{NAME}.fcproj"


def order():
    if "--order" in sys.argv:
        return sys.argv[sys.argv.index("--order") + 1].split(",")
    seen = []
    for j in json.load(open(ROOT / "clips" / "clips-batch.json"))["jobs"]:
        shot = re.match(r"clip-(.+?)-v\d+", j["id"]).group(1)
        if shot not in seen and int(re.match(r"\d+", shot).group()) < 200:
            seen.append(shot)
    return seen


def final(shot):
    d = ROOT / "clips" / (f"clip-{shot[:-1]}/clip-{shot}" if shot[-1].isalpha() else f"clip-{shot}") / "final"
    files = sorted(d.glob(f"clip-{shot}-v*-1080p.mp4"), key=lambda p: int(p.name.split("-v")[1].split("-")[0]))
    if not files:
        sys.exit(f"no 1080p final for {shot} in {d}")
    return files[-1]


def cli(cmds, project=None, save_as=None):
    script = EDIT / ".fc-run.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    args = ["filmcraft-cli", "--compact"] + (["--project", str(project)] if project else []) + ["run", str(script)]
    if save_as:
        args += ["--save-as", str(save_as)]
    out = subprocess.run(args, capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    script.unlink()
    return [r.get("result") for r in res]


shots = order()
paths = [final(s) for s in shots]
if "--mp3" in sys.argv:
    (ROOT / "audio").mkdir(exist_ok=True)
    for i, (s, p) in enumerate(zip(shots, paths), 1):
        out = ROOT / "audio" / f"{i:02d}-clip-{s}.mp3"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-i", str(p), "-vn", "-c:a", "libmp3lame",
                        "-b:a", "320k", str(out)], check=True)
    print(f"{len(paths)} mp3s in {ROOT / 'audio'}")
if PROJ.exists():
    sys.exit(f"{PROJ.name} exists; move it away first")
EDIT.mkdir(exist_ok=True)
r = cli([{"id": "file.newProject", "params": {"name": NAME}},
         {"id": "file.import", "params": {"paths": [str(p) for p in paths]}},
         {"id": "file.newSequence", "params": {"name": NAME, "width": 1080, "height": 1920, "fps": 24,
                                               "video": 2, "audio": 1}}], save_as=PROJ)
cli([{"id": "timeline.place", "params": {"items": r[1]["items"], "track": "V1", "audioTrack": "A1", "frame": 0, "insert": False}},
     {"id": "file.save", "params": {}}], project=PROJ)
print(f"{PROJ}: {len(paths)} clips ({', '.join(shots)})")
