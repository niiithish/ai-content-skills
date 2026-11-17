#!/usr/bin/env python3
"""video-6 (2026-11-14, user: "make the hook2 and hook3 ... the body should be 100% match"): the opening media of
hooks 2 and 3 at the 1.242x pace of hook-1, made the way retime_speed.py made hook-1's:
the 1.1x talking-head-hookN (edit/backup-2026-11-13-speed-1.242/) and the 1.242x one are the same lines cut at the same
pauses, so old timeline time maps through raw clip time to new timeline time. Through that map:
  audio/hook-N-vo/hookN_open_vc-1.242x.wav       the voice-changed opening (Aleo_TalkingHead_HookN_vc.mp3), same loudness as hook-1's VO
  assets/cutout/drhan-greenscreen-hookN-1.242x.mp4  the user's green-screen take of the opening
both on talking-head-hookN.fcproj's 1.242x timeline from 0 to the body (the first clip-6 frame).
Usage: make_hook_media.py 2 3"""
import json, subprocess, sys, bisect
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
BK = EDIT / "backup-2026-11-13-speed-1.242"
OLD_SPEED, NEW_SPEED = 1.1, 1.242
K = NEW_SPEED / OLD_SPEED
TPS, FPS, SR = 254016000000, 24, 48000
REF_VO = ROOT / "audio/hook-1-vo/Aleo_Hook1_vo_vc-1.242x.wav"


def seq(p):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(p), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


def pieces(p, speed):
    out = []
    for c in sorted(seq(p)["video"][0]["items"], key=lambda c: c["startFrame"]):
        shot = c["name"].split("-")[1]
        out.append((shot, c["sourceIn"] / TPS * speed, c["sourceOut"] / TPS * speed, c["startFrame"] / FPS,
                    c["durationFrames"] / FPS))
    return out


def read(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, np.float32)


def stretch(x):
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={K}",
                        "-f", "f32le", "-"], input=x.tobytes(), capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def rms_db(x):
    x = x[np.abs(x) > 1e-3]
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


for n in map(int, sys.argv[1:]):
    OLD = pieces(BK / f"talking-head-hook{n}.fcproj", OLD_SPEED)
    NEW = pieces(EDIT / f"talking-head-hook{n}.fcproj", NEW_SPEED)
    body = next(i for i, p in enumerate(NEW) if p[0] == "6")
    NEW = NEW[:body]
    end = NEW[-1][3] + NEW[-1][4]

    def new_to_old(t):
        i = max(0, bisect.bisect_right([p[3] for p in NEW], t) - 1)
        shot, na, nb, nt, nd = NEW[i]
        raw = na + (t - nt) * NEW_SPEED
        for s, ra, rb, ta, d in OLD:
            if s == shot and ra - 1e-6 <= raw <= rb + 1e-6:
                return ta + (raw - ra) / OLD_SPEED
        return None

    # voice
    old = read(ROOT / f"audio/voice-changed/Aleo_TalkingHead_Hook{n}_vc.mp3")
    out = np.zeros(int(end * SR), np.float32)
    fade = int(0.005 * SR)
    for shot, na, nb, nt, nd in NEW:
        nb = na + nd * NEW_SPEED
        for s_, ra, rb, ta, d in OLD:
            if s_ != shot or rb <= na or ra >= nb:
                continue
            x0, x1 = max(na, ra), min(nb, rb)
            a, oa = nt + (x0 - na) / NEW_SPEED, ta + (x0 - ra) / OLD_SPEED
            m = int(round((x1 - x0) / NEW_SPEED * SR))
            y = stretch(old[int(oa * SR):int(oa * SR) + int(round((x1 - x0) / OLD_SPEED * SR))])
            y = np.pad(y, (0, max(0, m - len(y))))[:m].copy()
            y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
            s0 = int(round(a * SR)); out[s0:s0 + m] += y[:len(out) - s0]
    ref = read(REF_VO)[: int(11 * SR)]            # hook-1's opening, as it plays
    out *= 10 ** ((rms_db(ref) - rms_db(out)) / 20)
    dst = ROOT / f"audio/hook-{n}-vo"; dst.mkdir(exist_ok=True)
    vo = dst / f"hook{n}_open_vc-1.242x.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le",
                    str(vo)], input=np.clip(out, -1, 1).tobytes(), check=True)
    print(f"hook {n}: VO {vo.name} {end:.3f} s, peak {20*np.log10(np.abs(out).max()):.1f} dBFS")

    # green screen, frame by frame through the map
    w, h, fps = 1080, 1920, 30
    src = ROOT / f"assets/cutout/drhan-greenscreen-hook{n}.mp4"
    want = []
    for i in range(int(end * fps)):
        o = new_to_old(i / fps)
        want.append(int(round(o * fps)) if o is not None else (want[-1] if want else 0))
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "nv12", "-"],
                           stdout=subprocess.PIPE)
    dstv = ROOT / f"assets/cutout/drhan-greenscreen-hook{n}-1.242x.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-vaapi_device", "/dev/dri/renderD128", "-f", "rawvideo",
                            "-pix_fmt", "nv12", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "format=nv12,hwupload",
                            "-c:v", "h264_vaapi", "-qp", "16", "-profile:v", "high", "-movflags", "+faststart", str(dstv)],
                           stdin=subprocess.PIPE)
    fsz = w * h * 3 // 2
    cur, idx = None, -1
    for t in want:
        while idx < t:
            b = dec.stdout.read(fsz)
            if len(b) < fsz:
                break
            cur, idx = b, idx + 1
        enc.stdin.write(cur)
    enc.stdin.close(); enc.wait(); dec.kill()
    print(f"hook {n}: green {dstv.name} {len(want)} frames")
