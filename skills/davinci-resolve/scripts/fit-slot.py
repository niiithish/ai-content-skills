#!/usr/bin/env python3
"""Render one timeline slot as a frame-exact ProRes LT .mov (no audio), ready for build.py.

Fixes what Resolve's API can't do in one append:
  - a clip SHORTER than its slot is slowed down (to 0.5x at most), then holds its last frame;
  - a clip LONGER than its slot keeps its action: --from picks where to start (default 0; the first
    frames are often a static lead-in, so look at the clip first);
  - --split: two clips stacked top/bottom, each the centre half of its own frame (split-screen hooks:
    each side is generated as its own clip, never as one split frame);
  - --inset GREEN.mp4 --inset-at T: a green-screen presenter keyed and laid bottom-left (the doctor
    cut-out over B-roll), taken from the same moment T of her talking track so her lips stay in sync.

Usage:
  fit-slot.py OUT.mov --dur SECONDS SRC [SRC2] [--split] [--from S] [--inset GREEN.mp4 --inset-at T]
              [--fps 24] [--size 1080x1920]
Two SRCs without --split play one after the other, sharing the slot by their lengths.
"""
import argparse, subprocess


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out"); ap.add_argument("src", nargs="+")
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--from", dest="start", type=float, default=0.0)
    ap.add_argument("--split", action="store_true")
    ap.add_argument("--inset"); ap.add_argument("--inset-at", type=float, default=0.0)
    ap.add_argument("--inset-key", default="0x00FE02", help="green to key out")
    ap.add_argument("--fps", type=int, default=24); ap.add_argument("--size", default="1080x1920")
    a = ap.parse_args()
    W, H = map(int, a.size.split("x")); F = a.fps
    n = round(a.dur * F)
    base = f"fps={F},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"

    def seg(i, avail, secs):
        k = max(min(avail / secs, 1.0), 0.5)          # slow down at most 2x
        slow = "" if k >= 1 else f"setpts=PTS/{k:.4f},"
        return (f"[{i}]{slow}{base},tpad=stop_mode=clone:stop_duration={secs},"
                f"trim=end_frame={round(secs * F)},setpts=PTS-STARTPTS")

    ins = []
    for f in a.src:
        ins += (["-ss", f"{a.start}"] if a.start else []) + ["-i", f]
    avail = [dur(f) - a.start for f in a.src]
    if a.split:
        if len(a.src) != 2:
            raise SystemExit("--split needs two clips: top, bottom")
        fc = (f"{seg(0, avail[0], a.dur)},crop={W}:{H // 2}:0:{H // 4}[t];"
              f"{seg(1, avail[1], a.dur)},crop={W}:{H // 2}:0:{H // 4}[b];[t][b]vstack[v]")
    elif len(a.src) == 2:
        n1 = round(n * avail[0] / sum(avail))
        fc = f"{seg(0, avail[0], n1 / F)}[x];{seg(1, avail[1], (n - n1) / F)}[y];[x][y]concat=n=2:v=1[v]"
    else:
        fc = f"{seg(0, avail[0], a.dur)}[v]"
    if a.inset:
        gi = len(a.src)
        ins += ["-ss", f"{a.inset_at:.3f}", "-t", f"{a.dur + 0.2:.3f}", "-i", a.inset]
        # 60 % size, bottom-left, partly off the left edge, like the reference's presenter cut-out
        iw, ih = round(W * 0.6), round(H * 0.6)
        fc += (f";[{gi}]fps={F},trim=end_frame={n},setpts=PTS-STARTPTS,chromakey={a.inset_key}:0.13:0.06,"
               f"despill=type=green,scale={iw}:{ih},format=yuva444p[g];[v][g]overlay=x={-round(W * 0.105)}:y={H - ih}:format=auto[v]")
    fc = fc[:-3] + ",setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]"   # untagged ProRes trips decoders
    tmp = a.out + ".tmp.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-an",
                    "-c:v", "prores_aw", "-profile:v", "1", "-pix_fmt", "yuv422p10le", "-vendor", "apl0",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-frames:v", str(n), tmp], check=True)
    subprocess.run(["mv", tmp, a.out], check=True)
    print(f"{a.out}: {n} frames ({a.dur:.2f} s)" + ("" if min(avail) >= a.dur else f", slowed/held (source {min(avail):.2f} s)"))


if __name__ == "__main__":
    main()
