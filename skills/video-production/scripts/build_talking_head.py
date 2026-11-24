#!/usr/bin/env python3
"""Builds video-N/edit/talking-head.fcproj: every talking clip's 1080p final back to back, untrimmed, in story order, on
V1/A1. The order is the clip manifest's (clips/clips-batch.json, which is the edit order), talking shots only (numbered
below 200 or hook takes like h2; inserts are 201 up, listening clips are left out), or --order 1a,1b,2,...
Finals are the ones clips/PICKS.md names, else each shot's newest versioned final/ file (voice_change.py rules),
never clips/all (no Link Media popups).
Uses each final's voice-changed copy (-vc.mp4, from voice_change.py apply) when it exists, and the clips and
versions voice_change.py exported (audio/original/sources.json) unless --order is given.
--mp3 (old way, before voice_change.py) writes audio/NN-clip-X.mp3 (320k, play order).
Usage: build_talking_head.py video-N [--order 1a,1b,...] [--name talking-head] [--mp3]"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
EDIT = ROOT / "edit"
NAME = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else "talking-head"
PROJ = EDIT / f"{NAME}.fcproj"


sys.path.insert(0, str(Path(__file__).resolve().parent))
import voice_change as VC  # the same clip list, picks (clips/PICKS.md) and finals the voice change used


def order():
    return VC.order(ROOT)


def final(shot):
    VC.PICKED.update(VC.picked(ROOT))
    return VC.final(ROOT, shot, {})


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


def with_vc(p):
    """The voice-changed copy (voice_change.py apply) when it exists."""
    vc = p.with_name(p.stem + "-vc.mp4")
    return vc if vc.exists() else p


SOURCES = ROOT / "audio" / "original" / "sources.json"
if SOURCES.exists() and "--order" not in sys.argv:  # the clips and versions voice_change.py exported
    rows = json.loads(SOURCES.read_text())
    shots, paths = [r["shot"] for r in rows], [ROOT / r["final"] for r in rows]
else:
    shots = order()
    paths = [final(s) for s in shots]
paths = [with_vc(p) for p in paths]
print("voice-changed: " + (", ".join(s for s, p in zip(shots, paths) if p.stem.endswith("-vc")) or "none"))
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
