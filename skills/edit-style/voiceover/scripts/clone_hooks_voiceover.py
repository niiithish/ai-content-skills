#!/usr/bin/env python3
"""Builds edit/hook-2.fcproj and edit/hook-3.fcproj from edit/hook-1-v2.fcproj (user, 2026-11-02: "have all 3 ready").
Each is a copy of hook 1 whose opening (V1 shots 1-3 and their voice, frames 0-322) is replaced by that hook's own
voiceover (voiceover/hook-N-1.1x.wav) and shots, and the body (V1 from shot 4a, the 9d/9e split, the split line, the
body voice) moves to follow it. The hook voice is tightened like hook 1's (pace.py calm: a pause of 0.35 s or more is
cut to 0.20 s, keeping 0.04 s before the voice comes back). Shots cut where their first word is heard; clip 1 plays
whole (start/end-frame clip), the others are trimmed to their slot. The music is laid again over the new length.
Run only while FilmCraft does not have these projects open (it writes the files headless)."""
import json, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_hook1_v2 import EDIT, FPS, TPS, V, clip_for, dur

SRC = EDIT / "hook-1-v2.fcproj"
BODY = 322         # first frame of the body (shot 4a) in hook 1
GAP = 5            # frames of silence between the hook's last word and the body's voice
MUSIC = V / "music" / "Mystical Tension [JECXYadQD8U].m4a"
HOOKS = {  # shot, first word's time in the hook wav (s); pauses (start, end) in the wav from pauses.py
    "2": dict(wav="hook-2-1.1x.wav", shots=[("15", 0.0), ("1", 1.20), ("2", 5.44), ("16", 8.96)],
              pauses=[(5.03, 5.67), (8.62, 9.13)]),
    "3": dict(wav="hook-3-1.1x.wav", shots=[("2", 0.0), ("1", 4.16), ("17", 9.28)],
              pauses=[(3.79, 4.39), (8.90, 9.50)]),
}
WHOLE = {"1"}


def run(proj, cmds):
    f = EDIT / ".fc-run.jsonl"
    f.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in res if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")
    return [r.get("result") for r in res]


def inspect(proj):
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"], capture_output=True, text=True)
    d = json.loads(out.stdout)
    return d.get("result", d)


def cid(r):
    return (r.get("clips") or [r.get("clip")])[0]


def segments(h, length):
    """Kept stretches of the wav (src_in, src_out) after tightening, and a map from wav time to timeline frame."""
    segs, a = [], 0.0
    for p0, p1 in h["pauses"]:
        if p1 - p0 >= 0.35:
            segs.append((a, p0 + 0.16)); a = p1 - 0.04
    segs.append((a, length))
    frames, f = [], 0
    for s0, s1 in segs:
        n = round((s1 - s0) * FPS); frames.append((f, n, s0)); f += n
    def at(t):
        for (f0, n, s0), (_, s1) in zip(frames, segs):
            if t < s1:
                return f0 + max(0, round((t - s0) * FPS))
        return f
    return frames, at, f


def build(n):
    h = HOOKS[n]
    proj = EDIT / f"hook-{n}.fcproj"
    if proj.exists():
        sys.exit(f"{proj.name} exists: back it up and remove it first (it may hold the user's tweaks)")
    shutil.copy(SRC, proj)
    wav = V / "voiceover" / h["wav"]
    frames, at, hook_len = segments(h, dur(str(wav)))
    end_hook = hook_len + GAP
    delta = end_hook - BODY
    s = inspect(proj)
    head = [c["clip"] for t in (s["video"][0], s["audio"][0]) for c in t["items"] if c["startFrame"] < BODY]
    music = [c["clip"] for t in s["audio"][1:] for c in t["items"]]
    body = [dict(c, track=t["id"]) for t in s["video"] + s["audio"][:1] for c in t["items"] if c["startFrame"] >= BODY]
    run(proj, [{"id": "edit.clear", "params": {"clips": head + music}}, {"id": "file.save", "params": {}}])
    # the body moves by delta as one move, so no clip lands on one not yet moved
    run(proj, [{"id": "timeline.move", "params": {"moves": [{"clip": c["clip"], "track": c["track"], "time": (c["startFrame"] + delta) * TPS // FPS}
                                                           for c in body], "insert": False, "linked": False}},
               {"id": "file.save", "params": {}}])
    paths = [str(wav)] + [clip_for(k) for k, _ in h["shots"]] + [str(MUSIC)]
    paths = list(dict.fromkeys(paths))
    item = dict(zip(paths, run(proj, [{"id": "file.import", "params": {"paths": paths}}, {"id": "file.save", "params": {}}])[0]["items"]))
    # the hook voice, tightened
    run(proj, [{"id": "timeline.place", "params": {"item": item[str(wav)], "track": "A1", "frame": f0, "sourceIn": round(s0 * TPS),
                                                   "duration": nf * TPS // FPS, "insert": False, "video": False}}
               for f0, nf, s0 in frames] + [{"id": "file.save", "params": {}}])
    # the hook shots, each from its first word to the next shot (the last to the body)
    cuts = [at(t) for _, t in h["shots"]] + [end_hook]
    cuts[0] = 0
    placed = []
    for (k, _), f0, f1 in zip(h["shots"], cuts, cuts[1:]):
        p = clip_for(k); full = round(dur(p) * FPS)
        nfr = full if k in WHOLE else min(full, f1 - f0)
        r = run(proj, [{"id": "timeline.place", "params": {"item": item[p], "track": "V1", "frame": f0, "sourceIn": 0,
                                                           "duration": nfr * TPS // FPS, "insert": False, "audio": False}},
                       {"id": "file.save", "params": {}}])
        c = cid(r[0]); post = [{"id": "clip.fillFrame", "params": {"clips": [c]}}]
        if k in WHOLE or nfr < f1 - f0:   # play it whole in its slot, or stretch a short one to the next cut
            speed = round(100 * dur(p) / ((f1 - f0 + 0.5) / FPS), 2)
            post.append({"id": "clip.speedDuration", "params": {"clips": [c], "speed": speed, "ripple": False}})
        run(proj, post + [{"id": "file.save", "params": {}}])
        placed.append((k, f0, f1, Path(p).name))
    s = inspect(proj)
    end = max(c["endFrame"] for t in s["audio"] + s["video"] for c in t["items"])
    r = run(proj, [{"id": "timeline.place", "params": {"item": item[str(MUSIC)], "track": "A2", "frame": 0, "sourceIn": 0,
                                                       "duration": end * TPS // FPS, "insert": False, "video": False}},
                   {"id": "file.save", "params": {}}])
    m = cid(r[0])
    run(proj, [{"id": "clip.audioGain", "params": {"clips": [m], "mode": "set", "db": -17}},
               {"id": "sequence.applyAudioTransition", "params": {"clip": m, "frames": 2 * FPS, "edge": "out", "align": "end"}},
               {"id": "file.save", "params": {}}])
    print(f"hook-{n}.fcproj: hook {hook_len / FPS:.2f} s (body moved {delta:+d} frames), ends {end / FPS:.1f} s")
    for k, f0, f1, name in placed:
        print(f"  {k:>3} {f0 / FPS:5.2f}-{f1 / FPS:5.2f} s  {name}")


if __name__ == "__main__":
    for n in sys.argv[1:] or HOOKS:
        build(n)
