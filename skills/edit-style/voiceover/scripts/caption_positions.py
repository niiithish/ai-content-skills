#!/usr/bin/env python3
"""Moves captions off busy picture in edit/hook-N.fcproj (rerun after every captions build, which resets positions):
over clip 1's first wide shot (the glowing anatomy sits at the default caption height) to y 1000 on her shirt, and over
the 18a/18b split to y 985, centred on the seam. Run only while FilmCraft is closed."""
import json, sys
from pathlib import Path

TPF = 8467200000


def main(path):
    d = json.loads(Path(path).read_text())
    seq = next(v for v in d["project"]["items"].values() if "Sequence" in v.get("kind", {}))["kind"]["Sequence"]
    tr = {t["name"]: t for t in seq["video_tracks"]}
    v1 = sorted(tr["Video 1"]["items"], key=lambda c: c["start"])
    zones = []
    first = next((c for c in v1 if c["name"].startswith("clip-1-")), None)  # the wide shot before the punch-ins
    if first:  # hook 3 no longer has it
        zones.append((first["start"], first["start"] + first["duration"], 1000.0))
    for c in v1:
        if c["name"].startswith("clip-18a"):
            zones.append((c["start"], c["start"] + c["duration"], 985.0))
    n = 0
    for c in tr["Video 3"]["items"]:
        for e in c["effects"]:
            if e["effect"] == "graphic_text":
                e["params"]["position"]["value"]["Vec2"]["y"] = 1420.0  # template 4 baseline
        for a, b, y in zones:
            if min(b, c["start"] + c["duration"]) - max(a, c["start"]) > 2 * TPF:  # really over it, not touching
                for e in c["effects"]:
                    if e["effect"] == "graphic_text":
                        e["params"]["position"]["value"]["Vec2"]["y"] = y
                n += 1
                print(f"  {c['name']!r} {c['start'] // TPF}-{(c['start'] + c['duration']) // TPF} -> y {y:.0f}")
    Path(path).write_text(json.dumps(d))
    print(f"{path}: {n} captions moved")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
