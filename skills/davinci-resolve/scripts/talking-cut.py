#!/usr/bin/env python3
"""Spec for a yap-style talking-head cut: clips back to back, each trimmed to its speech, no gaps.

Each clip is cut to start 0.04 s before its first word and end 0.12 s after its last (word times from the
transcribe skill, cached as <clip>.words.json next to it), and its own audio rides with it on A1.
Mysa video-10: 47 doctor clips -> 4:39.8 with no gap or overlap.

Usage:
  talking-cut.py CLIP [CLIP ...] --timeline "Hook 1 (talking cut)" [--pre 0.04] [--post 0.12] [--fps 24] > spec.json
Clips must already be Resolve-readable (ProRes/DNxHR .mov from to-prores.sh); pass them in script order.
Then: build.py spec.json --dry-run, build.py spec.json.
"""
import argparse, json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE.parents[1] / "transcribe" / "scripts", Path.home() / ".claude/skills/transcribe/scripts"):
    if (p / "transcribe.py").is_file():
        sys.path.insert(0, str(p))
        break


def words(clip):
    cache = clip.with_suffix(".words.json")
    if cache.is_file():
        w = json.loads(cache.read_text())
        return [(x["word"], x["start"], x["end"]) if isinstance(x, dict) else tuple(x) for x in w]
    from transcribe import words as tw
    w = [tuple(x) for x in tw(clip)]
    cache.write_text(json.dumps([list(x) for x in w]))
    return w


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="+", type=Path)
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--pre", type=float, default=0.04); ap.add_argument("--post", type=float, default=0.12)
    ap.add_argument("--fps", type=int, default=24)
    a = ap.parse_args()
    spec = {"timeline": a.timeline, "width": 1080, "height": 1920, "fps": a.fps, "video": [], "audio": []}
    at = 0.0
    for c in a.clips:
        c = c.resolve()
        w = [x for x in words(c) if str(x[0]).strip()]
        if not w:
            print(f"warning: no speech in {c.name}, skipped", file=sys.stderr)
            continue
        i, o = max(0.0, w[0][1] - a.pre), w[-1][2] + a.post
        d = round((o - i) * a.fps) / a.fps
        for kind in ("video", "audio"):
            spec[kind].append({"file": str(c), "at": round(at, 4), "in": round(i, 4), "dur": d, "track": 1})
        print(f"{at:7.2f}  {c.name}  {i:.2f}-{i + d:.2f}  {' '.join(x[0] for x in w)[:60]}", file=sys.stderr)
        at += d
    print(f"total {at:.2f} s, {len(spec['video'])} clips", file=sys.stderr)
    json.dump(spec, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
