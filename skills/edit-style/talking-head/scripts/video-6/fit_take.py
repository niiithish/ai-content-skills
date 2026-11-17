#!/usr/bin/env python3
"""video-6 (2026-11-14, user: new ElevenLabs take of clip 10 (0:27-0:30), "adjust volume, speed etc"): fit a
speech-to-speech take into hook-1's voice, in sync with her lips, without stretching (stretched voice sounded processed,
2026-11-13). The take is sped 1.242x like every other word and cut at its pauses and silent stop closures into chunks.
Each chunk moves so its words start where the picture's own audio (A2) says them: word times from Parakeet, then a
+-2 frame envelope refine. Each chunk is level-matched (RMS) to the old voice it replaces, with 6 ms fades. The gaps
left at the cuts are silence. The result goes into the VO through the A1 piece map. Writes a new VO; the old is kept.
Usage: fit_take.py VO_IN VO_OUT TAKE_SPED.wav REF_A2.wav F0 "f:src,..." "cut_f:anchor_word_index,..." TK.words.json REF.words.json"""
import json, subprocess, sys
import numpy as np
vin, vout, tk, ref = sys.argv[1:5]; f0 = int(sys.argv[5])
amap = [(int(a), float(b)) for a, b in (p.split(":") for p in sys.argv[6].split(","))]
cuts = [float(x) for x in sys.argv[7].split(",")]          # cut points in the take, frames
tw, rw = json.load(open(sys.argv[8])), json.load(open(sys.argv[9]))
SR = 48000; F = SR // 24; HOP = 240; FD = int(0.006 * SR)
load = lambda p: np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                              capture_output=True, check=True).stdout, np.float32).copy()
env = lambda x: np.sqrt((x[:len(x) // HOP * HOP].reshape(-1, HOP) ** 2).mean(1))
vo, w, r = load(vin), load(tk), load(ref)
n = len(r)
def vpos(f):
    k = max(i for i, (a, _) in enumerate(amap) if a <= f)
    return int(amap[k][1] * SR) + int(round((f - amap[k][0]) * F))
bounds = [a for a, _ in amap] + [f0 + n // F]
old = np.concatenate([vo[vpos(a):vpos(a) + (b - a) * F] for a, b in zip(bounds[:-1], bounds[1:])])
er, ew = env(r), env(w)
rms = lambda x: np.sqrt((x[np.abs(x) > 2e-3] ** 2).mean())
edges = [0.0] + cuts + [len(w) / F]
new = np.zeros(n, np.float32); last = 0
for c0, c1 in zip(edges[:-1], edges[1:]):
    ws = [i for i, x in enumerate(tw) if c0 <= x["start"] * 24 < c1]
    sh = float(np.median([rw[i]["start"] * 24 - tw[i]["start"] * 24 for i in ws]))   # frames
    a, b = int(c0 * F), int(c1 * F)
    base = int(round(sh * F / HOP))
    def sc(o):
        s = a // HOP + o; e = b // HOP + o
        if s < 0 or e > len(er): return -1
        return np.dot(ew[a // HOP:b // HOP], er[s:e]) / (np.linalg.norm(er[s:e]) + 1e-9)
    o = max(range(base - 8, base + 9), key=sc)
    p = w[a:b].copy(); q = a + o * HOP
    if q < last: p = p[last - q:]; q = last
    p = p[:max(0, n - q)]
    if len(p) < FD * 2: continue
    p *= rms(old[q:q + len(p)]) / rms(p)
    f = np.linspace(0, 1, FD, dtype=np.float32); p[:FD] *= f; p[-FD:] *= f[::-1]
    new[q:q + len(p)] = p; last = q + len(p)
    print(f"take {c0:5.1f}-{c1:5.1f} f [{' '.join(tw[i]['word'] for i in ws)}] -> +{(q - a) / F:.2f} f (words said {sh:+.1f})")
out = vo.copy(); k = 0; X = int(0.008 * SR); fade = np.linspace(0, 1, X, dtype=np.float32)
for a, b in zip(bounds[:-1], bounds[1:]):
    m = (b - a) * F; seg = new[k:k + m].copy(); o = out[vpos(a):vpos(a) + m]
    seg[:X] = seg[:X] * fade + o[:X] * (1 - fade); seg[-X:] = seg[-X:] * (1 - fade) + o[-X:] * fade
    out[vpos(a):vpos(a) + m] = seg; k += m
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", vout],
               input=out.tobytes(), check=True)
