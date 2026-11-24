#!/usr/bin/env python3
"""Pre-export audit of a FilmCraft project. Run it before every export and after every scripted edit.

Why (Aleo video-6, 2026-11-17): every one of these slipped through to a client Loom.
  - Loom 9: a later edit of a cut silently dropped one light-leak transition; its click SFX stayed.
  - 2:28:19: clip.speedDuration left a clip 0.00001 frame long, so her cutout showed on the next picture.
  - Loom 6: a 360p library draft scaled 300 % read as "poor quality".
  - Hooks 2/3 drifted from hook 1's body when a fix went only into hook 1.

Usage:
  audit.py edit/hook-1.fcproj [--baseline edit/backup-<date>-<what>/hook-1.fcproj]
                              [--body-of edit/hook-1.fcproj --offset -2 --from 260]
  --baseline  the last approved or pre-edit copy: every transition and video/audio effect type there
              must still be here (by effect, frame and clip name); added/removed ones are listed.
  --body-of   check this project's body against hook 1: every clip on every track that starts at or
              after --from (hook-1 frames) must exist here at start+offset with the same length,
              source in, speed and name.
Exit 1 when anything fails; prints one line per problem, "OK" lines otherwise.
"""
import argparse, json, subprocess, sys
from pathlib import Path

F = 10584000000  # ticks per frame at 24 fps


def seq(p):
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(p), "inspect", "sequence"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def clips(s):
    for kind in ("video", "audio"):
        for ti, t in enumerate(s[kind]):
            for c in t["items"]:
                yield f"{kind[0].upper()}{ti + 1}", c


def walk(o, hit):
    if isinstance(o, dict):
        hit(o)
        for v in o.values():
            walk(v, hit)
    elif isinstance(o, list):
        for v in o:
            walk(v, hit)


def transitions(proj_path, names):
    out = []
    def hit(o):
        if {"from", "to", "align", "effect", "start", "duration"} <= o.keys() and isinstance(o["effect"], dict):
            out.append((o["effect"].get("effect"), round(o["start"] / F), round(o["duration"] / F),
                        names.get(o["to"], names.get(o["from"], "?"))))
    walk(json.load(open(proj_path)), hit)
    return sorted(out)


def media_paths(proj_path):
    out = set()
    def hit(o):
        f = o.get("File") if isinstance(o.get("File"), dict) else None
        if f and isinstance(f.get("path"), str):
            out.add(f["path"])
    walk(json.load(open(proj_path)), hit)
    return out


def effect_set(s):
    return sorted((tr, c["startFrame"], c["name"], e["effect"]) for tr, c in clips(s)
                  for e in c.get("effects", []) if e["effect"] not in ("motion", "opacity", "time_remap", "volume", "panner"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--baseline")
    ap.add_argument("--body-of")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--from", dest="from_", type=int, default=0)
    a = ap.parse_args()
    bad = 0
    s = seq(a.project)
    names = {c["clip"]: c["name"] for _, c in clips(s)}

    # 1. whole-frame clips
    frac = [(tr, c["clip"], c["name"], c["start"] / F, c["duration"] / F) for tr, c in clips(s)
            if c["start"] % F or c["duration"] % F]
    for f in frac:
        print(f"FAIL fractional clip {f[0]} #{f[1]} {f[2]}: start {f[3]:.5f} f, length {f[4]:.5f} f (trim to whole frames)")
    bad += len(frac)
    if not frac:
        print("OK   every clip starts and ends on a whole frame")

    # 2. media online and at least 720p
    miss, low = [], []
    for m in sorted(media_paths(a.project)):
        if not Path(m).exists():
            miss.append(m); continue
        if Path(m).suffix.lower() in (".mp4", ".mov", ".png", ".jpg", ".jpeg", ".webm", ".mkv"):
            r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=width,height", "-of", "csv=p=0", m], capture_output=True, text=True).stdout.strip()
            try:
                w, h = map(int, r.split(",")[:2])
                if min(w, h) < 720 and not any(m.endswith(x) for x in (".png",)):
                    low.append((m, w, h))
            except ValueError:
                pass
    used = {c["name"] for _, c in clips(s)}
    for m in miss:
        print(f"FAIL missing media {m}")
    for m, w, h in low:
        if Path(m).name in used:
            print(f"WARN low-res source on the timeline {w}x{h}: {m}")
    bad += len(miss)
    if not miss:
        print("OK   all media online")

    # 3. transitions and effects kept from the baseline
    if a.baseline:
        b = seq(a.baseline)
        bnames = {c["clip"]: c["name"] for _, c in clips(b)}
        t_now, t_was = transitions(a.project, names), transitions(a.baseline, bnames)
        gone = [t for t in t_was if t not in t_now]
        new = [t for t in t_now if t not in t_was]
        for t in gone:
            print(f"FAIL transition gone vs baseline: {t[0]} at {t[1]} ({t[2]} f) into {t[3]}")
        for t in new:
            print(f"INFO transition added: {t[0]} at {t[1]} ({t[2]} f) into {t[3]}")
        e_now, e_was = effect_set(s), effect_set(b)
        for e in [e for e in e_was if e not in e_now]:
            print(f"WARN effect gone vs baseline: {e[3]} on {e[0]} {e[2]} at {e[1]}")
        bad += len(gone)
        if not gone:
            print(f"OK   all {len(t_was)} baseline transitions still there ({len(t_now)} now)")
        moved = sorted(set((tr, c["clip"], c["startFrame"], c["endFrame"]) for tr, c in clips(b))
                       - set((tr, c["clip"], c["startFrame"], c["endFrame"]) for tr, c in clips(s)))
        print(f"INFO {len(moved)} baseline clips moved, trimmed or removed" + (": " + ", ".join(
            f"{m[0]} #{m[1]} {m[2]}-{m[3]}" for m in moved[:12]) if moved else ""))

    # 4. body identical to hook 1
    if a.body_of:
        h = seq(a.body_of)
        key = lambda tr, c, o: (tr, c["startFrame"] + o, c["durationFrames"] if "durationFrames" in c else round(c["duration"] / F),
                                round(c["sourceIn"] / F, 2), round(c.get("speed", 1), 4), c["name"])
        want = {key(tr, c, a.offset) for tr, c in clips(h) if c["startFrame"] >= a.from_}
        have = {key(tr, c, 0) for tr, c in clips(s)}
        diff = sorted(want - have)
        for d in diff[:20]:
            print(f"FAIL body differs from hook 1: {d[0]} {d[5]} at {d[1]} ({d[2]} f, in {d[3]} f, speed {d[4]})")
        bad += len(diff)
        if not diff:
            print(f"OK   body identical to {a.body_of} ({len(want)} clips, offset {a.offset})")

    print(f"length {s.get('durationFrames')} f")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
