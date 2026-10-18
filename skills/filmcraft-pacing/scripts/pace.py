#!/usr/bin/env python3
"""Pacing pass on a FilmCraft edit: dead air out, something always moving, numbers to prove it.

  pace.py report  PROJECT [--vo A1]                    pauses, shot lengths, still stretches, b-roll without motion
  pace.py tighten PROJECT [--style calm|punchy] [--vo A1] [--dry]
                                                       shortens every pause in the voice on V1+A1 (the talking track),
                                                       every other track follows the time it was cut to
  pace.py motion  PROJECT [--style calm|punchy] [--face-y Y] [--dry]
                                                       a framing change at each visible jump cut, a slow push on long
                                                       still stretches, a slow push in/out on b-roll that has none

Never touches a clip that already has motion (scale or position set by hand or by a build script). Edits go live
to the app when it has the project open, else to the file (the filmcraft skill's fc.py decides); a copy of the
project goes to edit/backup-<date>-pacing/ first. Pauses come from the waveform (transcribe skill's pauses.py),
never from ASR word ends.
"""
import argparse, datetime, json, math, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent.parent
for d in (SKILLS / "filmcraft" / "scripts", SKILLS / "transcribe" / "scripts",
          Path.home() / ".claude/skills/filmcraft/scripts", Path.home() / ".claude/skills/transcribe/scripts"):
    sys.path.insert(0, str(d))
import fc                                   # noqa: E402  (filmcraft skill)
from pauses import load, find_pauses        # noqa: E402  (transcribe skill)

TPS = 254016000000  # FilmCraft ticks per second
# calm: viewers over ~35 (most of Meta's buyers); punchy: young, fast creator style
STYLES = {
    "calm":   dict(keep=0.12, keep_long=0.20, long=0.35, punch=108, push=106, broll=106, still=4.0),
    "punchy": dict(keep=0.08, keep_long=0.12, long=0.35, punch=115, push=110, broll=110, still=2.5),
}
LEAD = 0.04  # s of silence kept before the voice comes back, so the first consonant isn't clipped


def die(msg):
    sys.exit(f"pace.py: {msg}")


# ---------- reading the sequence ----------

def seq(project):
    return fc.inspect(project, "sequence")


def fps_of(s):
    fr = s["settings"]["frame_rate"]
    return fr["num"] / fr["den"]


def is_text(c):
    return any(e["effect"] == "graphic_text" for e in c["effects"])


def nums(v):
    return [float(x) for x in re.findall(r"-?[0-9.]+", v)]


def motion_of(c, center=(540.0, 960.0)):
    """(static scale, has any motion): scale or position keyframed, or set away from the default."""
    m = next((e for e in c["effects"] if e["effect"] == "motion"), None)
    if not m:
        return 100.0, False
    p = m["params"]
    sc = nums(p["scale"]["value"])[0]
    pos = tuple(nums(p["position"]["value"])[-2:])
    moved = bool(p["scale"].get("keyframes") or p["position"].get("keyframes")) or sc != 100.0 or pos != center
    return sc, moved


def keyframed(c):
    return any(e["effect"] == "motion" and e["params"]["scale"].get("keyframes") for e in c["effects"])


def track_index(s, name):
    kind, n = name[0].upper(), int(name[1:])
    return (s["video"] if kind == "V" else s["audio"])[n - 1]


def broll_tracks(s):
    """Video tracks above V1 that carry pictures (not only text)."""
    return [t for t in s["video"][1:] if any(not is_text(c) for c in t["items"])]


def covered(s, total):
    cov = [False] * total
    for t in broll_tracks(s):
        for c in t["items"]:
            if c["enabled"] and not is_text(c):
                for f in range(max(0, c["startFrame"]), min(total, c["endFrame"])):
                    cov[f] = True
    return cov


# ---------- the voice ----------

def voice_wav(project, vo):
    """The talking track alone as WAV, exported headless from the saved file (never saved back)."""
    b = fc.bridge_project()
    p = Path(project).resolve()
    if b and b[0] and Path(b[0]).resolve() == p and b[1]:
        subprocess.run([fc.CLI, "--bridge", fc.BRIDGE, "--compact", "exec", "file.save"], check=True, capture_output=True)
    s = json.loads(subprocess.run([fc.CLI, "--project", str(p), "--compact", "inspect", "sequence"],
                                  capture_output=True, text=True, check=True).stdout)
    keep, n = int(vo.lstrip("Aa")), len(s["audio"])
    out = Path(tempfile.mkdtemp(prefix="pace-")) / "vo.wav"
    cmds = [{"id": "sequence.deleteTrack", "params": {"track": f"A{k}"}} for k in range(n, 0, -1) if k != keep]
    cmds.append({"id": "file.exportMedia", "params": {"path": str(out), "format": "wav", "wait": True}})
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write("\n".join(json.dumps(c) for c in cmds) + "\n")
    r = subprocess.run([fc.CLI, "--project", str(p), "--compact", "run", f.name], capture_output=True, text=True)
    if r.returncode or not out.exists():
        die(f"voice export failed: {r.stdout[-300:]} {r.stderr[-300:]}")
    return out


def cuts_to_make(pauses, fps, st):
    """Frame ranges [a, b) to remove so each pause keeps `keep` (or `keep_long` for a long one) seconds."""
    out = []
    for s, e in pauses:
        keep = st["keep_long"] if e - s >= st["long"] else st["keep"]
        a = math.ceil((s + keep - LEAD) * fps)
        b = math.floor((e - LEAD) * fps)
        if b - a >= 1:
            out.append((a, b))
    return out


def mapper(ranges):
    def m(f):
        gone = 0
        for a, b in ranges:
            if f >= b:
                gone += b - a
            elif f > a:
                gone += f - a
        return f - gone
    return m


# ---------- commands ----------

def backup(project):
    p = Path(project).resolve()
    d = p.parent / f"backup-{datetime.date.today():%Y%m%d}-pacing"
    d.mkdir(exist_ok=True)
    dst = d / p.name
    if not dst.exists():  # the first backup of the day is the one before any pacing pass
        shutil.copy2(p, dst)
    return dst


def cmd_report(a):
    s = seq(a.project)
    fps, total = fps_of(s), s["durationFrames"]
    ps = find_pauses(load(voice_wav(a.project, a.vo)))
    st = STYLES["calm"]
    over = [(x, y) for x, y in ps if y - x > st["keep_long"] + 0.05]
    print(f"{Path(a.project).name}: {total / fps:.1f} s at {fps:g} fps")
    print(f"voice pauses >= 0.15 s: {len(ps)}, {sum(y - x for x, y in ps):.1f} s; "
          f"longer than {st['keep_long']} s: {len(over)} (tighten would save "
          f"{sum(b - a for a, b in cuts_to_make(ps, fps, st)) / fps:.1f} s calm, "
          f"{sum(b - a for a, b in cuts_to_make(ps, fps, STYLES['punchy'])) / fps:.1f} s punchy)")
    for x, y in sorted(over, key=lambda p: p[0] - p[1])[:5]:
        print(f"   {y - x:.2f} s at {x:.2f}")
    # what the viewer sees change: any cut on the top visible picture, any start/end of a moving clip
    cov = covered(s, total)
    changes = {0, total}
    still_moving = [False] * total
    for t in [s["video"][0]] + broll_tracks(s):
        for c in t["items"]:
            if is_text(c) or not c["enabled"]:
                continue
            on_top = t is not s["video"][0] or not all(cov[c["startFrame"]:c["endFrame"]])
            if not on_top:
                continue
            changes.add(c["startFrame"])
            sc, moved = motion_of(c)
            if moved:
                if keyframed(c):
                    for f in range(c["startFrame"], min(total, c["endFrame"])):
                        if t is not s["video"][0] or not cov[f]:
                            still_moving[f] = True
    ch = sorted(changes)
    shots = [b - a for a, b in zip(ch, ch[1:]) if b > a]
    stills, run = [], 0
    for f in range(total):
        if still_moving[f] or f in changes:
            if run:
                stills.append((f - run, run))
            run = 0 if still_moving[f] else 1
        else:
            run += 1
    stills.append((total - run, run))
    longest = sorted(stills, key=lambda x: -x[1])[:3]
    print(f"picture changes: {len(shots)} shots, average {sum(shots) / len(shots) / fps:.1f} s; "
          f"longest stretch with nothing moving: " + ", ".join(f"{n / fps:.1f} s at {f / fps:.1f}" for f, n in longest))
    still_broll = [c for t in broll_tracks(s) for c in t["items"] if not is_text(c) and not motion_of(c)[1]]
    v1 = [c for c in s["video"][0]["items"]]
    print(f"b-roll clips without motion: {len(still_broll)} of {sum(len([c for c in t['items'] if not is_text(c)]) for t in broll_tracks(s))}; "
          f"talking clips with a zoom or push: {sum(motion_of(c)[1] for c in v1)} of {len(v1)}")
    caps = [c for t in s["video"] for c in t["items"] if is_text(c)]
    linger = [c for c in caps for x, y in ps if y - x >= 0.4 and c["startFrame"] < x * fps and c["endFrame"] > y * fps]
    print(f"captions: {len(caps)}; up through a pause of 0.4 s or more: {len(linger)}")
    music = [c for t in s["audio"][1:] for c in t["items"]]
    if music:
        print("music: " + ", ".join(f"{c['name'][:30]} {c.get('gainDb', 0):+.0f} dB" for c in music[:3]))


def cmd_tighten(a):
    st = STYLES[a.style]
    s = seq(a.project)
    fps, total = fps_of(s), s["durationFrames"]
    vo_track = track_index(s, a.vo)
    ranges = [(x, y) for x, y in cuts_to_make(find_pauses(load(voice_wav(a.project, a.vo))), fps, st) if y <= total]
    # only where the talking track has a clip all the way through (its picture is what gets cut)
    v1 = s["video"][0]["items"]
    ranges = [(x, y) for x, y in ranges if any(c["startFrame"] <= x and c["endFrame"] >= y for c in v1)
              or all(any(c["startFrame"] <= f < c["endFrame"] for c in v1) for f in range(x, y))]
    # an existing cut inside or next to a pause: cut up to it, so no sliver of a frame or two is left over
    seams = sorted({c["startFrame"] for c in v1} | {c["endFrame"] for c in v1})
    snapped = []
    for x, y in ranges:
        near = [f for f in seams if x - 2 <= f <= y + 2]
        if near:
            f = near[0]
            x, y = (x, f) if f > x else (f, y)
        if y - x >= 1:
            snapped.append((x, y))
    ranges = snapped
    gone = sum(y - x for x, y in ranges)
    print(f"{len(ranges)} pauses to shorten, {gone} frames ({gone / fps:.1f} s) out of {total / fps:.1f} s ({a.style})")
    if a.dry or not ranges:
        for x, y in ranges[:40]:
            print(f"   {x / fps:7.2f}  -{y - x}f")
        return
    print(f"backup: {backup(a.project)}")
    others = [(t, "V%d" % (i + 1)) for i, t in enumerate(s["video"]) if i > 0] + \
             [(t, "A%d" % (i + 1)) for i, t in enumerate(s["audio"]) if t is not vo_track]
    lock = [{"id": "timeline.setTrack", "params": {"track": n, "syncLock": False}} for t, n in others]
    razor = []
    for x, y in ranges:
        for tr in ("V1", a.vo.upper()):
            razor += [{"id": "timeline.razor", "params": {"time": round(x * TPS / fps), "track": tr}},
                      {"id": "timeline.razor", "params": {"time": round(y * TPS / fps), "track": tr}}]
    fc.run_cmds(a.project, lock + razor)
    s2 = seq(a.project)
    v1, vo = s2["video"][0]["items"], track_index(s2, a.vo)["items"]
    dels = []
    for x, y in reversed(ranges):
        ids = [c["clip"] for c in v1 + vo if c["startFrame"] >= x and c["endFrame"] <= y]
        if ids:
            dels.append({"id": "edit.rippleDelete", "params": {"clips": ids}})
    fc.run_cmds(a.project, dels)
    # every other track follows: move each clip to where its time went, trim what was cut out under it
    m = mapper(ranges)
    post = []
    for t, name in others:
        for c in sorted(t["items"], key=lambda c: c["startFrame"]):
            ns, ne = m(c["startFrame"]), m(c["endFrame"])
            if ns != c["startFrame"]:
                post.append({"id": "timeline.move", "params": {
                    "moves": [{"clip": c["clip"], "track": name, "time": round(ns * TPS / fps)}], "insert": False, "linked": False}})
            d = (ne - ns) - (c["endFrame"] - c["startFrame"])
            if d:
                post.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular", "deltaFrames": d}})
    # the cut pieces of picture and voice stay linked
    s3 = seq(a.project)
    vo3 = {(c["startFrame"], c["endFrame"]): c["clip"] for c in track_index(s3, a.vo)["items"]}
    for c in s3["video"][0]["items"]:
        k = (c["startFrame"], c["endFrame"])
        if k in vo3 and c.get("link") is None:
            post.append({"id": "clip.link", "params": {"clips": [c["clip"], vo3[k]]}})
    post += [{"id": "timeline.setTrack", "params": {"track": n, "syncLock": t.get("syncLock", True)}} for t, n in others]
    fc.run_cmds(a.project, post)
    s4 = seq(a.project)
    print(f"now {s4['durationFrames'] / fps:.1f} s (was {total / fps:.1f} s). Captions moved with their words; "
          "re-run captions-filmcraft words/plan/build for frame-exact starts.")


def cmd_motion(a):
    st = STYLES[a.style]
    s = seq(a.project)
    fps, total = fps_of(s), s["durationFrames"]
    H = s["settings"]["height"]
    fy = a.face_y or round(0.4 * H)
    cov = covered(s, total)
    cmds = []

    def tick(f):
        return round(f * TPS / fps)

    def punch(c, scale):
        # zoom on her face: the face point stays where it was
        y = round(fy - (fy - H / 2) * scale / 100)
        cmds.extend([{"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "position",
                                                           "value": [s["settings"]["width"] / 2, y]}},
                     {"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "scale", "value": scale}}])

    def push(c, s0, s1):
        cmds.extend([{"id": "effects.setParam", "params": {"clip": c["clip"], "effect": "motion", "param": "scale",
                                                           "value": v, "keyframe": True, "time": tick(f)}}
                     for v, f in ((s0, c["startFrame"]), (s1, c["endFrame"] - 1))])

    v1 = sorted(s["video"][0]["items"], key=lambda c: c["startFrame"])
    visible = lambda c: not all(cov[c["startFrame"]:c["endFrame"]]) and c["endFrame"] - c["startFrame"] >= fps / 2
    jumps = pushes = 0
    prev = None
    for c in v1:
        sc, moved = motion_of(c)
        if prev is not None and visible(c) and visible(prev) and prev["endFrame"] == c["startFrame"] \
                and prev["item"] == c["item"] and prev["sourceOut"] != c["sourceIn"] and not moved:
            if not motion_of(prev)[1] and not prev.get("_punched"):
                punch(c, st["punch"]); c["_punched"] = True; jumps += 1
                prev = c
                continue
        if not moved and not c.get("_punched") and visible(c) and (c["endFrame"] - c["startFrame"]) / fps >= st["still"]:
            push(c, 100, st["push"]); pushes += 1
        prev = c
    broll, k = 0, 0
    for t in broll_tracks(s):
        for c in t["items"]:
            if is_text(c) or motion_of(c)[1] or c["endFrame"] - c["startFrame"] < round(fps):
                continue
            s0, s1 = (100, st["broll"]) if k % 2 == 0 else (st["broll"], 100)
            push(c, s0, s1); k += 1; broll += 1
    print(f"{jumps} jump cuts get a framing change ({st['punch']}%), {pushes} long talking stretches a slow push "
          f"(to {st['push']}%), {broll} b-roll clips a slow push in/out ({st['broll']}%)")
    if a.dry or not cmds:
        return
    print(f"backup: {backup(a.project)}")
    fc.run_cmds(a.project, cmds)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("report", "tighten", "motion"):
        p = sub.add_parser(n)
        p.add_argument("project")
        p.add_argument("--vo", default="A1", help="the audio track with the voice (default A1)")
        if n != "report":
            p.add_argument("--style", choices=STYLES, default="calm")
            p.add_argument("--dry", action="store_true", help="print what would change, change nothing")
        if n == "motion":
            p.add_argument("--face-y", type=int, help="face height in the frame, px (default 40%% of the height)")
    a = ap.parse_args()
    {"report": cmd_report, "tighten": cmd_tighten, "motion": cmd_motion}[a.cmd](a)


if __name__ == "__main__":
    main()
