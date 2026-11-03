#!/usr/bin/env python3
"""Thins the talking-head jump cuts to the client's pattern (Loom, 2026-10-24: "boom, new text, boom, it makes sense";
ours were "random"). After heal_cuts.py every cut sat on a caption start, but captions change every 2-3 s, so there were
68 cuts, one every 2.6 s, with shots down to 0.8 s. A cut now stays only at a new sentence or clause:
1. Adds each cut the client asked for with --add "end of one caption|start of the next" (razor on V1 and A1);
   Aleo video-3: --add "anything to change,|that thin skin".
2. Heals every cut inside a sentence (no punctuation before it in the captions).
3. While a shot is shorter than MIN seconds, heals the weaker of its two cuts: clause before sentence, then the one
   that puts back less pause. A cut with more than MAX_GAP s of pause cut out is never healed (it would put dead air
   back), and neither is an added cut or the sentence cut just before it.
Run punch_cuts.py and the captions pipeline afterwards. Needs captions/<stem>.captions.json (fc_captions.py plan). Usage: declutter_cuts.py edit/hook-N.fcproj [--add "a|b" ...] [--min 1.8] [--dry]"""
import json, subprocess, sys
from pathlib import Path

MAX_GAP = 0.45
TPS = 254016000000
PROJ = Path(sys.argv[1]).resolve()
DRY = "--dry" in sys.argv
MIN = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 1.8
ADD = [sys.argv[i + 1].split("|") for i, a in enumerate(sys.argv) if a == "--add"]
HERE = Path(__file__).resolve().parent
B = json.load(open(PROJ.parent.parent / "captions" / f"{PROJ.stem}.captions.json"))["blocks"]


def fc(*a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), *a],
                                     capture_output=True, text=True, check=True).stdout)


def block_at(f):
    return min(range(len(B)), key=lambda k: abs(B[k]["start"] - f))


s = fc("inspect", "sequence")
v1 = sorted(s["video"][0]["items"], key=lambda c: c["startFrame"])
added = set()
for end_txt, start_txt in ADD:
    new = next((b["start"] for a, b in zip(B, B[1:]) if a["text"].endswith(end_txt) and b["text"].startswith(start_txt)), None)
    if new is None:
        sys.exit(f"no caption pair …{end_txt} | {start_txt}")
    added.add(new)
    if any(c["startFrame"] == new for c in v1):
        continue
    print(f"  add  {new / 24:7.2f}s  …{end_txt} | {start_txt}")
    if not DRY:
        script = PROJ.parent / ".fc-razor.jsonl"
        cmds = [{"id": "timeline.razor", "params": {"time": new * TPS // 24, "track": t[0]["id"]}} for t in (s["video"], s["audio"])]
        script.write_text("".join(json.dumps(x) + "\n" for x in cmds + [{"id": "file.save", "params": {}}]))
        out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(PROJ), "run", str(script)], capture_output=True, text=True)
        script.unlink()
        if out.returncode or any(not json.loads(l).get("ok") for l in out.stdout.splitlines() if l.startswith("{")):
            sys.exit(f"razor failed: {out.stdout[-2000:]}{out.stderr[-2000:]}")
        s = fc("inspect", "sequence")
        v1 = sorted(s["video"][0]["items"], key=lambda c: c["startFrame"])

cuts = {}
for a, b in zip(v1, v1[1:]):
    f = b["startFrame"]
    prev = B[block_at(f) - 1]["text"].rstrip()
    rank = 2 if prev[-1] in ".?!" else 1 if prev[-1] in ",;:" else 0
    cuts[f] = dict(rank=rank, gap=(b["sourceIn"] - a["sourceOut"]) / TPS, words=f"…{prev[-26:]} | {B[block_at(f)]['text'][:24]}")
keep = set(added) | {max((f for f in cuts if f < n), default=n) for n in added}
end = v1[-1]["endFrame"]
heal = {f for f, c in cuts.items() if c["rank"] == 0 and c["gap"] <= MAX_GAP and f not in keep}
while True:
    left = sorted(f for f in cuts if f not in heal)
    edges = [0] + left + [end]
    short = [(b - a, a, b) for a, b in zip(edges, edges[1:]) if b - a < MIN * 24]
    opts = [f for _, a, b in sorted(short) for f in (a, b) if f in cuts and f not in keep and cuts[f]["gap"] <= MAX_GAP]
    if not opts:
        break
    _, a, b = min((x for x in sorted(short) if any(f in opts for f in x[1:])))
    heal.add(min((f for f in (a, b) if f in opts), key=lambda f: (cuts[f]["rank"], cuts[f]["gap"])))
for f in sorted(heal):
    c = cuts[f]
    print(f"  heal {f / 24:7.2f}s  {['mid', 'clause', 'sentence'][c['rank']]:8} +{c['gap']:.2f}s  {c['words']}")
left = len(cuts) - len(heal)
print(f"{PROJ.stem}: {len(cuts)} cuts -> {left}, one every {end / 24 / (left + 1):.1f}s, "
      f"{sum(cuts[f]['gap'] for f in heal):.2f}s of pause put back")
if not DRY and heal:
    subprocess.run([sys.executable, str(HERE / "heal_cuts.py"), str(PROJ), "--at", ",".join(map(str, sorted(heal)))], check=True)
