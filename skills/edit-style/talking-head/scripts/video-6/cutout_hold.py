#!/usr/bin/env python3
"""Hold one cutout (V3) frame over a timeline range, so a head jump lands exactly on the
picture change (Loom 6 item 1/3: "the caption and new clip come together, her cut comes late").
  A:B:G  -> timeline frames A..B-1 on V3 show the source frame that timeline frame G shows now.
  Late jump at E+1 with the picture change at E:  E:E+1:E+1  (one repeated frame).
Timeline positions never change. Usage: FC_HEADLESS=1 cutout_hold.py PROJECT A:B:G [...]"""
import json, subprocess, sys
F = 10584000000
P = sys.argv[1]; SPECS = [tuple(int(x) for x in a.split(":")) for a in sys.argv[2:]]
def cli(*a, inp=None):
    r = subprocess.run(["filmcraft-cli", "--compact", "--project", P, *a], input=inp, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr + r.stdout)
    return r.stdout
def run(cmds):
    out = cli("run", "-", inp="".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    res = [json.loads(l) for l in out.splitlines() if l.startswith("{")]
    if not all(r.get("ok") for r in res): sys.exit(f"failed {cmds}: {res}")
def v3(): return json.loads(cli("inspect", "sequence"))["video"][2]["items"]
def at(t): return next(c for c in v3() if c["startFrame"] <= t < c["endFrame"])
# source of every G first (before any edit moves sources)
src = {}
for A, B, G in SPECS:
    c = at(G); src[(A, B, G)] = c["sourceIn"] + round((G - c["startFrame"]) * F * c["speed"])
for A, B, G in sorted(SPECS, key=lambda s: -s[0]):
    for cut in (B, A):
        if not any(c["startFrame"] == cut for c in v3()):
            run([{"id": "timeline.razor", "params": {"time": cut * F, "track": "V3"}}])
    h = next(c for c in v3() if c["startFrame"] == A)
    assert h["endFrame"] == B, (A, B, h["startFrame"], h["endFrame"])
    run([{"id": "timeline.slip", "params": {"clip": h["clip"], "delta": src[(A, B, G)] - h["sourceIn"]}},
         {"id": "clip.frameHoldOptions", "params": {"clips": [h["clip"]], "enabled": True, "holdOn": "in"}}])
    print(f"V3 {A}-{B}: hold of frame {G}")
