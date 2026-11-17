#!/usr/bin/env python3
"""video-6 (2026-11-13, user: "remove that silence and adjust everything"): ripple-cut frames [A, B) out of every track
of the open hook in FilmCraft, live through the bridge (the app holds the project). Razor each track at A and B, delete
what lies between, move everything from B on left by B-A. Music (A3) is not cut at A, where a skip would be heard: its
first play is shortened by B-A at its seam with the second play instead, and the second play moves left by B-A.
captions/<stem>.captions.json, .pk.json and .fw.json are shifted the same way so a later caption build matches.
Usage: [FC_HEADLESS=1] cut_silence.py A B [PROJECT]   (frames, 24 fps; FC_HEADLESS=1 when FilmCraft is closed)"""
import json, os, subprocess, sys
from pathlib import Path

A, B = int(sys.argv[1]), int(sys.argv[2])
PROJ = Path(sys.argv[3] if len(sys.argv) > 3 else Path(__file__).resolve().parent / "hook-1.fcproj")
TPS, FPS = 254016000000, 24
F = TPS // FPS
N = B - A
HEADLESS = bool(os.environ.get("FC_HEADLESS"))   # app closed: edit the file itself, saving after every step
if HEADLESS:
    CLI = ["filmcraft-cli", "--compact", "--project", str(PROJ)]
else:
    os.environ["FILMCRAFT_CONTROL_TOKEN"] = Path("~/.config/filmcraft/control-token").expanduser().read_text().strip()
    CLI = ["filmcraft-cli", "--bridge", "127.0.0.1:9876", "--compact"]


def seq():
    return json.loads(subprocess.run(CLI + ["inspect", "sequence"], capture_output=True, text=True, check=True).stdout)


def run(cmds):
    if HEADLESS and not any(c["id"] == "file.save" for c in cmds):
        cmds = cmds + [{"id": "file.save", "params": {}}]
    out = subprocess.run(CLI + ["run", "-"], capture_output=True, text=True,
                         input="".join(json.dumps(c) + "\n" for c in cmds))
    res = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    if out.returncode or not all(r.get("ok") for r in res):
        sys.exit(f"FilmCraft failed: {res} {out.stderr[-1500:]}")


def tracks(s):
    return [(k, i, t) for k in ("video", "audio") for i, t in enumerate(s[k])]


def name(k, i):
    return ("V" if k == "video" else "A") + str(i + 1)


before = seq()
music = (("audio", 2))
# 1. razor every track (but music) where a clip spans A or B
cuts = []
for k, i, t in tracks(before):
    if (k, i) == music:
        continue
    for x in (A, B):
        if any(c["startFrame"] < x < c["startFrame"] + c["durationFrames"] for c in t["items"]):
            cuts.append({"id": "timeline.razor", "params": {"time": x * F, "track": name(k, i)}})
run(cuts)
s = seq()
# 2. delete what lies in [A, B)
dead = [c["clip"] for k, i, t in tracks(s) if (k, i) != music for c in t["items"]
        if c["startFrame"] >= A and c["startFrame"] + c["durationFrames"] <= B]
run([{"id": "timeline.delete", "params": {"clips": dead, "ripple": False}}])
s = seq()
# 3. move everything from B on left by N (music: shorten the first play at its seam, move the second)
moves = [{"clip": c["clip"], "track": name(k, i), "time": {"frame": c["startFrame"] - N}}
         for k, i, t in tracks(s) if (k, i) != music for c in t["items"] if c["startFrame"] >= B]
m = sorted(s["audio"][2]["items"], key=lambda c: c["startFrame"])
assert len(m) == 2, "music: expected two plays"
run([{"id": "timeline.move", "params": {"moves": moves, "insert": False, "linked": False}},
     {"id": "timeline.trim", "params": {"clip": m[0]["clip"], "edge": "out", "mode": "regular", "deltaFrames": -N,
                                        "linked": False}},
     {"id": "timeline.move", "params": {"moves": [{"clip": m[1]["clip"], "track": "A3",
                                                    "time": {"frame": m[1]["startFrame"] - N}}],
                                        "insert": False, "linked": False}},
     {"id": "file.save", "params": {}}])
after = seq()
# check: nothing before A moved, everything after B moved by exactly N, no track keeps a gap at A
def spans(s, k, i):
    return sorted((c["startFrame"], c["startFrame"] + c["durationFrames"], c["name"]) for c in s[k][i]["items"])
for k, i, t in tracks(before):
    if (k, i) == music:
        continue
    want = []
    for a, b, n in spans(before, k, i):
        a2, b2 = (a if a < A else max(a, B) - N), (b if b <= A else max(b, B) - N)
        if b2 > a2:
            want.append((a2, b2, n))
    got = spans(after, k, i)
    # pieces split at A/B rejoin in the comparison: merge touching spans of the same name
    def merge(xs):
        out = []
        for a, b, n in xs:
            if out and out[-1][1] == a and out[-1][2] == n and a in (A,):
                out[-1] = (out[-1][0], b, n)
            else:
                out.append((a, b, n))
        return out
    assert merge(got) == merge(want), (name(k, i), [x for x in merge(got) if x not in merge(want)][:3],
                                       [x for x in merge(want) if x not in merge(got)][:3])
print(f"cut frames {A}-{B} ({N} f, {N / FPS:.3f} s) on every track; music shortened at its seam; length "
      f"{before['durationFrames']} -> {after['durationFrames']}")

# caption work files (blocks/cuts/end in frames; word lists [word, start s, end s])
cap = PROJ.parent.parent / "captions"
sh = lambda f: f if f < A else (A if f < B else f - N)
st = lambda t: t if t < A / FPS else (A / FPS if t < B / FPS else round(t - N / FPS, 3))
p = cap / f"{PROJ.stem}.captions.json"
j = json.loads(p.read_text())
for b in j["blocks"]:
    b["start"], b["end"] = sh(b["start"]), sh(b["end"])
j["cuts"] = sorted({sh(c) for c in j["cuts"]})
j["end"] = sh(j["end"])
p.write_text(json.dumps(j, indent=1))
for suf in ("pk", "fw"):
    p = cap / f"{PROJ.stem}.{suf}.json"
    if p.exists():
        p.write_text(json.dumps([[w, st(a), st(b)] for w, a, b in json.loads(p.read_text())]))
print("caption work files shifted")
