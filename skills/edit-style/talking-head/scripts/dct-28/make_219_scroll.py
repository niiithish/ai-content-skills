#!/usr/bin/env python3
"""219: the product page scrolled slowly from just under the sale bar (hidden, user 2026-11-09 "dont show the fall
sale") down to the Add to Cart button, which lands at frame centre and holds. 108 frames (4.5 s) at 24 fps."""
import subprocess, sys
from pathlib import Path
from PIL import Image
SCR = Path(__file__).resolve().parent / "media/screens"
N, HOLD, FPS = int(sys.argv[1]) if len(sys.argv) > 1 else 108, 18, 24
page = Image.open(SCR / "pdp-mobile.png").convert("RGB")
k = 1080 / page.width
vh = round(1920 / k)                          # page px in one frame
y0, y1 = 212, 3586 - vh // 2                 # below the sale bar -> Add to Cart (rows 3510-3662) centred
out = SCR / "219-pdp-scroll-v2.mp4"
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                       "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
move = N - HOLD
for f in range(N):
    t = min(f / (move - 1), 1.0)
    e = t * t * (3 - 2 * t)                    # ease in and out
    y = round(y0 + (y1 - y0) * e)
    ff.stdin.write(page.crop((0, y, page.width, y + vh)).resize((1080, 1920), Image.LANCZOS).tobytes())
ff.stdin.close(); ff.wait()
print(out, N, "frames", f"scroll {y1 - y0} page px over {move} frames")
