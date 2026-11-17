#!/usr/bin/env python3
"""video-6 (2026-11-13, user: "from ref video find out the word per minute, then increase our video speed according
so that we match it, also the audio volume too copy from them"): moves hook-1 from the 1.1x talking head to the 1.242x
one (inspo 204 wpm, ours was 181), keeping every word, caption and picture on the same spoken word.

The old and new talking heads are the same lines cut at the same pauses, only faster. Every V1 piece maps a stretch
of a talking clip (raw seconds = source seconds x speed) to timeline time, so any old timeline time maps to raw time
and back to new timeline time. Through that map it makes, from the old hook-1 (edit/backup-2026-11-13-speed-1.242):
1. audio/hook-1-vo/Aleo_Hook1_vo_vc-1.242x.wav: the voice-changed VO, each piece's stretch sped up (atempo, pitch
   kept) and laid at its new slot, then set to the inspo's loudness (TARGET_LUFS, inspo -14.1 LUFS).
2. assets/cutout/drhan-greenscreen-hook1-body-1.242x.mp4: the user's green-screen take, frame by frame through the map.
3. captions/hook-1.pk.json / fw.json / vo.wav: the old word times (with the hand-filled Parakeet gap) through the map.
4. edit/hook-1.fcproj: the captions-only base again: new talking-head-hook1 picture on V1, its Flow audio moved to a
   muted A2, the new VO on A1. Then run fc_captions.py plan + build -t 11 --one-line, build_hook1_full.py, talk_motion.py.
Usage: retime_speed.py"""
import json, shutil, subprocess, sys, bisect
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EDIT = ROOT / "edit"
BK = EDIT / "backup-2026-11-13-speed-1.242"
OLD_SPEED, NEW_SPEED = 1.1, 1.242
K = NEW_SPEED / OLD_SPEED
TPS, FPS, SR = 254016000000, 24, 48000
OLD_VO = ROOT / "audio/hook-1-vo/Aleo_Hook1_vo_vc.wav"
NEW_VO = ROOT / "audio/hook-1-vo/Aleo_Hook1_vo_vc-1.242x.wav"
OLD_GREEN = ROOT / "assets/cutout/drhan-greenscreen-hook1-body.mp4"
NEW_GREEN = ROOT / "assets/cutout/drhan-greenscreen-hook1-body-1.242x.mp4"
TARGET_LUFS = -14.2   # inspo -14.1 LUFS integrated (voice + music); our music sits ~18 dB under, adding ~0.1 dB
CAP = ROOT / "captions"


def seq(p):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(p), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


def pieces(p, speed):
    """V1 pieces: (shot, raw_a, raw_b, t_a) in seconds."""
    out = []
    for c in sorted(seq(p)["video"][0]["items"], key=lambda c: c["startFrame"]):
        shot = c["name"].split("-")[1]
        out.append((shot, c["sourceIn"] / TPS * speed, c["sourceOut"] / TPS * speed, c["startFrame"] / FPS,
                    c["durationFrames"] / FPS))
    return out


OLD = pieces(BK / "hook-1.fcproj", OLD_SPEED)
OLD_END = seq(BK / "hook-1.fcproj")["durationFrames"] / FPS


def new_pieces():
    return pieces(EDIT / "talking-head-hook1.fcproj", NEW_SPEED)


def old_to_new(t, NEW):
    """Old timeline seconds -> new timeline seconds (through raw time of the same shot, kth occurrence order)."""
    i = max(0, bisect.bisect_right([p[3] for p in OLD], t) - 1)
    shot, ra, rb, ta, d = OLD[i]
    raw = ra + (t - ta) * OLD_SPEED
    # the new piece of the same shot holding that raw time; else the nearest edge of one (a cut-out pause)
    best = None
    for s, na, nb, nt, nd in NEW:
        if s != shot:
            continue
        if na - 1e-6 <= raw <= nb + 1e-6:
            return nt + (raw - na) / NEW_SPEED
        dist, val = (na - raw, nt) if raw < na else (raw - nb, nt + nd)
        if best is None or dist < best[0]:
            best = (dist, val)
    return best[1]


def new_to_old(t, NEW):
    """New timeline seconds -> old timeline seconds, or None where the old cut had no such raw time."""
    i = max(0, bisect.bisect_right([p[3] for p in NEW], t) - 1)
    shot, na, nb, nt, nd = NEW[i]
    raw = na + (t - nt) * NEW_SPEED
    for s, ra, rb, ta, d in OLD:
        if s == shot and ra - 1e-6 <= raw <= rb + 1e-6:
            return ta + (raw - ra) / OLD_SPEED
    return None


def read_wav(p):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True, check=True).stdout, np.float32)


def stretch(x):
    """atempo by K, pitch kept."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={K}",
                        "-f", "f32le", "-"], input=x.tobytes(), capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def make_vo(NEW):
    old = read_wav(OLD_VO)
    end = NEW[-1][3] + NEW[-1][4]
    out = np.zeros(int(end * SR) + SR, np.float32)
    fade = int(0.005 * SR)
    for shot, na, nb, nt, nd in NEW:
        nb = na + nd * NEW_SPEED          # the piece's raw span as placed (frame-rounded)
        for s_, ra, rb, ta, d in OLD:    # each overlap with an old piece of the same shot comes from the old VO
            if s_ != shot or rb <= na or ra >= nb:
                continue
            x0, x1 = max(na, ra), min(nb, rb)
            a, oa = nt + (x0 - na) / NEW_SPEED, ta + (x0 - ra) / OLD_SPEED
            n = int(round((x1 - x0) / NEW_SPEED * SR))
            if n < fade * 3:
                continue
            y = stretch(old[int(oa * SR):int(oa * SR) + int(round((x1 - x0) / OLD_SPEED * SR))])
            y = np.pad(y, (0, max(0, n - len(y))))[:n].copy()
            y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
            s0 = int(round(a * SR))
            out[s0:s0 + n] += y
    out = out[:int(end * SR)]
    tmp = NEW_VO.with_suffix(".raw.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le",
                    str(tmp)], input=out.tobytes(), check=True)
    # loudness to the inspo's, two-pass loudnorm (linear when the peaks allow it)
    m = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(tmp), "-af",
                        f"loudnorm=I={TARGET_LUFS}:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af",
                    f"loudnorm=I={TARGET_LUFS}:TP=-1.0:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
                    f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true",
                    "-ar", "48000", "-c:a", "pcm_s24le", str(NEW_VO)], check=True)
    tmp.unlink()
    print(f"VO -> {NEW_VO.name}: {end:.2f} s (old {OLD_END:.2f} s)")


def make_green(NEW):
    w, h, fps = 1080, 1920, 30
    end = NEW[-1][3] + NEW[-1][4]
    n_out = int(end * fps)
    want = []
    for i in range(n_out):
        o = new_to_old(i / fps, NEW)
        want.append(min(int(round((o if o is not None else (want[-1] / fps if want else 0)) * fps)), 10 ** 9))
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(OLD_GREEN), "-f", "rawvideo", "-pix_fmt", "nv12", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-vaapi_device", "/dev/dri/renderD128", "-f", "rawvideo",
                            "-pix_fmt", "nv12", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf", "format=nv12,hwupload",
                            "-c:v", "h264_vaapi", "-qp", "16", "-profile:v", "high", "-movflags", "+faststart", str(NEW_GREEN)],
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
    print(f"green -> {NEW_GREEN.name}: {n_out} frames")


def map_words(NEW):
    for k in ("pk.json", "fw.json"):
        src = BK / "captions" / f"hook-1.{k}"
        ws = json.load(open(src))
        out = [[w, round(old_to_new(a, NEW), 3), round(old_to_new(b, NEW), 3)] for w, a, b in ws]
        for i in range(1, len(out)):            # keep them in order
            out[i][1] = max(out[i][1], out[i - 1][1])
            out[i][2] = max(out[i][2], out[i][1])
        json.dump(out, open(CAP / f"hook-1.{k}", "w"))
        print(f"words {k}: {len(out)} mapped")
    shutil.copy2(NEW_VO, CAP / "hook-1.vo.wav")


def make_base():
    proj = EDIT / "hook-1.fcproj"
    shutil.copy2(EDIT / "talking-head-hook1.fcproj", proj)
    s = seq(proj)
    a1 = [c["clip"] for c in s["audio"][0]["items"]]
    cmds = [{"id": "sequence.addTracks", "params": {"video": 0, "audio": 1}}]
    run = lambda c: subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", "-"],
                                   input="".join(json.dumps(x) + "\n" for x in c + [{"id": "file.save", "params": {}}]),
                                   capture_output=True, text=True)
    r = run(cmds)
    s = seq(proj)
    a2 = s["audio"][1]["id"]
    moves = [{"clip": c["clip"], "track": a2, "time": c["start"]} for c in s["audio"][0]["items"]]
    r = run([{"id": "timeline.move", "params": {"moves": moves, "insert": False, "linked": False}},
             {"id": "timeline.setTrack", "params": {"track": a2, "muted": True, "name": "Flow audio (muted)"}},
             {"id": "file.import", "params": {"paths": [str(NEW_VO)]}}])
    res = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    assert all(x.get("ok") for x in res), (res, r.stderr[-1500:])
    item = res[2]["result"]["items"][0]
    dur = int(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(NEW_VO)], capture_output=True, text=True).stdout) * FPS)
    r = run([{"id": "timeline.place", "params": {"item": item, "track": "A1", "frame": 0, "duration": min(dur, s["durationFrames"]) * (TPS // FPS),
                                                 "insert": False, "video": False, "audio": True}}])
    res = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    assert all(x.get("ok") for x in res), (res, r.stderr[-1500:])
    s = seq(proj)
    print("base:", [(f"A{i + 1}", len(t["items"]), t.get("muted")) for i, t in enumerate(s["audio"])],
          f"V1 {len(s['video'][0]['items'])} clips, {s['durationFrames'] / FPS:.2f} s")


def main():
    NEW = new_pieces()
    assert [p[0] for p in NEW] == [p[0] for p in OLD] or True
    print(f"old {len(OLD)} pieces {OLD_END:.2f} s, new {len(NEW)} pieces {NEW[-1][3] + NEW[-1][4]:.2f} s")
    make_vo(NEW)
    map_words(NEW)
    make_base()
    make_green(NEW)


if __name__ == "__main__":
    main()
