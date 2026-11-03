#!/usr/bin/env python3
"""Voice-to-voice silence at every talking-head.fcproj join, measured on the enhanced master (10 ms frames,
threshold 40% from noise floor to speech level, as pauses.py). Imported by build_hook1.py."""
import subprocess
import numpy as np
from pathlib import Path
MASTER = Path(__file__).resolve().parent / "talking-media/talking-head-enhanced.mp4"

def voiced():
    a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(MASTER), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                     capture_output=True, check=True).stdout, np.int16) / 32768
    db = np.array([20 * np.log10(np.sqrt((a[i:i + 160] ** 2).mean()) + 1e-9) for i in range(0, len(a) - 160, 160)])
    lo, hi = np.percentile(db, 8), np.percentile(db, 90)
    return db > lo + 0.4 * (hi - lo)

def gap(on, j, fps=24):
    """(last voice before, first voice after) a join at master frame j, in seconds."""
    k = int(j / fps * 100)
    e = k
    while e > 0 and not on[e - 1]:
        e -= 1
    s = k
    while s < len(on) and not on[s]:
        s += 1
    return e / 100, s / 100

if __name__ == "__main__":
    import sys; sys.path.insert(0, str(Path(__file__).parent))
    from build_hook1 import JOINS
    on = voiced()
    for j in JOINS[1:-1]:
        e, s = gap(on, j)
        print(f"join {j:5d} ({j/24:6.2f}s)  silence {s - e:5.2f}s  (before {j/24 - e:4.2f}, after {s - j/24:4.2f})")
