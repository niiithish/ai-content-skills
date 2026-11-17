#!/usr/bin/env python3
"""Rebuild hook-1's 1.242x green-screen cutout at 24 fps from the user's real frames (user 2026-11-17: "stucky, like 3 fps").
The user's take (drhan-greenscreen-hook1-body.mp4) is 24 fps footage saved by Canva as 30 fps: every frame with
index % 5 == 1 repeats the one before (checked: one phase across the whole file). Those repeats, after the 1.242x
retime and the 24 fps timeline, read as stutters. Here unique frame u (the 4 real frames of each 5) sits at u/24 s,
and each 24 fps output frame takes the real frame nearest its time through retime_speed's map, so the cutout
keeps the same timing (lip sync) and has no repeats.
Writes assets/cutout/drhan-greenscreen-hook1-body-1.242x-24p.mp4"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retime_speed as R
NEW = R.new_pieces(); fps = 24
end = NEW[-1][3] + NEW[-1][4]; n_out = int(round(end * fps))
uniq = lambda u: 5 * (u // 4) + [0, 2, 3, 4][u % 4]          # unique index -> frame index in the 30 fps file
want, last = [], 0.0
for i in range(n_out):
    o = R.new_to_old(i / fps, NEW)
    o = last if o is None else o; last = o
    want.append(uniq(int(round(o * 24))))
rep = sum(1 for a, b in zip(want, want[1:]) if a == b)
print(f"{n_out} frames at 24 fps ({end:.3f} s); repeated picks {rep}")
w, h = 1080, 1920
out = R.ROOT / "assets/cutout/drhan-greenscreen-hook1-body-1.242x-24p.mp4"
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(R.OLD_GREEN), "-f", "rawvideo", "-pix_fmt", "nv12", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-vaapi_device", "/dev/dri/renderD128", "-f", "rawvideo", "-pix_fmt", "nv12",
                        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "format=nv12,hwupload", "-c:v", "h264_vaapi", "-qp", "16",
                        "-profile:v", "high", "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
fsz = w * h * 3 // 2; cur, idx = None, -1
for t in want:
    while idx < t:
        b = dec.stdout.read(fsz)
        if len(b) < fsz: break
        cur, idx = b, idx + 1
    enc.stdin.write(cur)
enc.stdin.close(); enc.wait(); dec.kill()
print("wrote", out)
