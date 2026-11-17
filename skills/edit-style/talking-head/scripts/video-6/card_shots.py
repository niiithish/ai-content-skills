#!/usr/bin/env python3
"""video-6 (2026-11-13, user: "it felt repeated, we do what the ref did"): on each name-card shot the inspo shows only
the picture and the card (LASERS, MICRONEEDLING): no caption and no cutout of her. So for every V4 card: delete the
V5 captions inside its span, and razor the V3 cutout at the card's start and end and delete the piece between.
Live through the bridge when the app has the project open. Rerun after any caption build (a build brings the captions
back). Usage: card_shots.py [PROJECT]"""
import json, os, subprocess, sys
from pathlib import Path

PROJ = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent / "hook-1.fcproj")
F = 254016000000 // 24
os.environ["FILMCRAFT_CONTROL_TOKEN"] = Path("~/.config/filmcraft/control-token").expanduser().read_text().strip()
CLI = ["filmcraft-cli", "--bridge", "127.0.0.1:9876", "--compact"]


def seq():
    return json.loads(subprocess.run(CLI + ["inspect", "sequence"], capture_output=True, text=True, check=True).stdout)


def run(cmds):
    out = subprocess.run(CLI + ["run", "-"], capture_output=True, text=True,
                         input="".join(json.dumps(c) + "\n" for c in cmds))
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {res} {out.stderr[-1500:]}")


sp = lambda c: (c["startFrame"], c["startFrame"] + c["durationFrames"])
s = seq()
cards = [sp(c) for c in s["video"][3]["items"] if c["name"].startswith("card-")]
caps = [c for c in s["video"][4]["items"] if any(a <= sp(c)[0] and sp(c)[1] <= b for a, b in cards)]
over = [c["name"] for c in s["video"][4]["items"] if c not in caps and any(sp(c)[0] < b and sp(c)[1] > a for a, b in cards)]
assert not over, f"captions cross a card edge: {over}"
razor = [{"id": "timeline.razor", "params": {"time": x * F, "track": "V3"}}
         for a, b in cards for x in (a, b) if any(sp(c)[0] < x < sp(c)[1] for c in s["video"][2]["items"])]
if razor:
    run(razor)
    s = seq()
cut = [c for c in s["video"][2]["items"] if any(a <= sp(c)[0] and sp(c)[1] <= b for a, b in cards)]
run([{"id": "timeline.delete", "params": {"clips": [c["clip"] for c in caps + cut], "ripple": False}},
     {"id": "file.save", "params": {}}])
print(f"{len(cards)} card shots: removed {len(caps)} captions ({', '.join(c['name'] for c in caps)}) and "
      f"{len(cut)} cutout pieces")
