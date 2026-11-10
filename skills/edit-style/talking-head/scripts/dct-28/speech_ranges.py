"""Speech ranges for each talking final, from the waveform, with any internal silence over 0.3 s squeezed to 0.3 s and
known bad words cut (ASR times from the 1080p file). Writes edit/ranges.json: {clip: {"path", "keep": [[in, out], ...]}}."""
import json, re, subprocess, pathlib
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
GAP, PAD = 0.30, 0.12          # max silence kept; pad kept before/after speech inside a gap
picks = re.findall(r"- (clip-\S+-1080p\.mp4)", (ROOT / "clips/PICKS.md").read_text())
# cuts in source seconds (from the 1080p transcripts): clip-2 "w-" stutter, clip-h3 the first of "does does"
CUTS = {"h3": [[4.95, 5.42]]}   # from the waveform around the ASR times

def env(path):
    a = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                       capture_output=True, check=True).stdout
    x = np.frombuffer(a, np.float32); hop = 160            # 10 ms
    n = len(x) // hop; r = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    return 20 * np.log10(r), len(x) / 16000

def voiced(db, thr):
    on = db > thr; segs = []; i = 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]: j += 1
            segs.append([i / 100, j / 100]); i = j
        else: i += 1
    out = []
    for s in segs:                       # merge pieces split by short dips (< 0.12 s)
        if out and s[0] - out[-1][1] < 0.12: out[-1][1] = s[1]
        else: out.append(s)
    return [s for s in out if s[1] - s[0] >= 0.06]

ranges = {}
for rel in picks:
    cid = re.match(r"clip-([^/]+)/", rel).group(1)
    if cid.startswith("listen"): continue
    p = ROOT / "clips" / rel
    wj = p.with_suffix(".words.json")
    if not wj.exists(): subprocess.run(["transcribe", str(p)], check=True, capture_output=True)
    words = json.loads(wj.read_text())
    db, L = env(p)
    thr = -45.0                                           # one level for every clip, ~1 dB above the exported tracks' p95-32 (-46.9 guest, -45.9 host)
    on = db > thr                          # same plain test as check_exports.py: no merging, no blip removal
    w0, w1 = max(words[0]["start"] - 0.25, 0), min(words[-1]["end"] + 0.35, L)
    idx = [i for i in range(int(w0 * 100), min(int(w1 * 100), len(on))) if on[i]]
    s0, s1 = idx[0] / 100, (idx[-1] + 1) / 100
    keep, cur = [], max(s0 - PAD, 0)
    i = idx[0]
    while i <= idx[-1]:
        if not on[i]:
            j = i
            while j <= idx[-1] and not on[j]: j += 1
            if (j - i) / 100 > GAP - 0.02:      # squeeze: keep PAD each side
                keep.append([cur, i / 100 + PAD]); cur = j / 100 - PAD
            i = j
        else: i += 1
    keep.append([cur, min(s1 + PAD, L)])
    for c0, c1 in CUTS.get(cid, []):       # remove bad words
        nk = []
        for a, b in keep:
            if b <= c0 or a >= c1: nk.append([a, b])
            else:
                if a < c0: nk.append([a, c0])
                if b > c1: nk.append([c1, b])
        keep = nk
    ranges[cid] = {"path": str(p), "len": round(L, 3), "thr": round(float(thr), 1),
                   "keep": [[round(a, 3), round(b, 3)] for a, b in keep],
                   "words": " ".join(w["word"] for w in words)}
(ROOT / "edit/ranges.json").write_text(json.dumps(ranges, indent=1))
for k, v in ranges.items(): print(k, v["thr"], v["keep"])
