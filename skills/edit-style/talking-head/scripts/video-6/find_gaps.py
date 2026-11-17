#!/usr/bin/env python3
"""video-6: rebuild hook-1's voice (A1 pieces) from the live project and list every pause of MIN s or more
(10 ms steps under -40 dB), with the next caption start. Prints `A B` frame ranges that cut each pause to BREATH s,
ending on the next caption start (or the voice's return when none is near). Usage: find_gaps.py [MIN] [BREATH]"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np
MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25
BREATH = float(sys.argv[2]) if len(sys.argv) > 2 else 0.18
F = 10584000000; SR = 16000
os.environ["FILMCRAFT_CONTROL_TOKEN"] = Path("~/.config/filmcraft/control-token").expanduser().read_text().strip()
s = json.loads(subprocess.run(["filmcraft-cli", "--bridge", "127.0.0.1:9876", "--compact", "inspect", "sequence"],
                              capture_output=True, text=True, check=True).stdout)
out = np.zeros(int(s["durationFrames"] / 24 * SR) + SR)
cache = {}
for c in s["audio"][0]["items"]:
    p = c["path"] if "path" in c else None
    p = p or str(Path("audio/hook-1-vo/Aleo_Hook1_vo_vc-1.242x-fix25.wav"))
    if p not in cache:
        cache[p] = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                                capture_output=True, check=True).stdout, np.float32)
    x = cache[p]; a = int(c["startFrame"] / 24 * SR); src = int(c["sourceIn"] / F / 24 * SR); n = int(c["durationFrames"] / 24 * SR)
    out[a:a + n] = x[src:src + n]
w = SR // 100
db = 20 * np.log10(np.sqrt((out[:len(out) // w * w].reshape(-1, w) ** 2).mean(1)) + 1e-9)
q = db < -40
caps = sorted(c["startFrame"] for c in s["video"][4]["items"])
cuts = sorted({c["startFrame"] for k in (0, 1) for c in s["video"][k]["items"]})
i = 0
while i < len(q):
    if not q[i]:
        i += 1; continue
    j = i
    while j < len(q) and q[j]: j += 1
    d = (j - i) * 0.01
    if d >= MIN and i > 0 and j < len(q) - 50:
        t0, t1 = i * 0.01, j * 0.01
        n = int(round((d - BREATH) * 24))
        marks = [f for f in caps + cuts if t0 * 24 + 1 <= f <= t1 * 24 + 1]
        b = max(marks) if marks else int(t1 * 24)
        b = min(b, int(t1 * 24))
        a = max(b - n, int(np.ceil(t0 * 24)) + 1)
        if b - a > 0:
            print(f"{a} {b}  # {t0:.2f}s pause {d:.2f}s -> {d - (b - a) / 24:.2f}s")
    i = j
