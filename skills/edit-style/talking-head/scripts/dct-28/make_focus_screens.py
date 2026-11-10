#!/usr/bin/env python3
"""Focus versions of the screen inserts, like the reference's screen shots (user 2026-11-09: "in the ref video ...
zoomed in and blurred ... so it's focused, ours is super boring"): the page zoomed about 2x onto the phrase she
says, sharp in a band around that line, a heavy lens-style blur above and below. Writes edit/media/screens/*-focus.png
(1080x1920). The edit then pushes them in fast.
Sources: 2x re-renders of the screen HTML (sharp at 2x zoom) and the PubMed capture with the study highlight."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

SCR = Path(__file__).resolve().parent / "media/screens"
PP = Path(sys.argv[1]) if len(sys.argv) > 1 else None      # folder with 201-2x.png, 205-2x.png, 206-2x.png


def focus(img, scale, cx, cy, zoom, out, band=150, feather=230, blur=22):
    """img: source; scale: source px per 1080-frame px; (cx, cy): focus point in 1080-frame px."""
    W, H = 1080, 1920
    cw, ch = W / zoom * scale, H / zoom * scale
    x0, y0 = cx * scale - cw / 2, cy * scale - ch / 2
    x0 = min(max(x0, 0), img.width - cw)
    # the focus line stays at the frame centre (y 960), like the reference, so a 1:1 centre crop keeps it
    # (user 2026-11-09); above the page top the page background fills in, under the blur
    bg = img.getpixel((img.width // 2, 5))           # page colour at the top centre (the PubMed page has a cyan strip at x 0-23)
    canvas = Image.new("RGB", (int(cw) + 2, int(ch) + 2), bg)
    canvas.paste(img.crop((int(x0), int(max(y0, 0)), int(x0 + cw), int(min(y0 + ch, img.height)))), (0, int(max(-y0, 0))))
    sharp = canvas.resize((W, H), Image.LANCZOS)
    soft = sharp.filter(ImageFilter.GaussianBlur(blur))
    fy = (cy * scale - y0) / ch * H                    # focus line in output px
    y = np.arange(H)
    d = np.clip((np.abs(y - fy) - band) / feather, 0, 1)
    m = (1 - d[:, None] * np.ones((1, W))) * 255
    Image.composite(sharp, soft, Image.fromarray(m.astype(np.uint8), "L")).save(SCR / out)
    print(out, f"focus line at y {fy:.0f}")


if PP:
    for n, cx, cy, z in (("201", 430, 744.5, 2.0), ("205", 330, 735, 1.8), ("206", 345, 1140, 1.7)):
        focus(Image.open(PP / f"{n}-2x.png").convert("RGB"), 2.0, cx, cy, z, f"{n}-focus.png")
# 201 and 205 pages carry a search bar and tabs above the AI Overview (user 2026-11-09: the top must be blurred page, not empty)
# study: the PubMed page (1170 wide) with the yellow highlight from study-116.png laid back on (multiply)
pub = Image.open(SCR / "study-pubmed.png").convert("RGB")
k = 1170 / 1080
a = np.asarray(Image.open(SCR / "study-116.png").convert("RGB")).astype(int)
m = (a[..., 0] > 230) & (a[..., 1] > 215) & (a[..., 2] < 200)
m[:1500] = False
ys, xs = np.nonzero(m)
off = 1606                                             # study-116 row 0 = row 1606 of the page at 1080 wide
box = [int(xs.min() * k), int((ys.min() + off) * k), int((xs.max() + 1) * k), int((ys.max() + 1 + off) * k)]
hl = np.asarray(pub).astype(float)
hl[box[1]:box[3], box[0]:box[2]] *= np.array([255, 241, 118]) / 255
pub = Image.fromarray(hl.astype(np.uint8))
focus(pub, k, (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2 + off, 1.5, "study-focus.png")
