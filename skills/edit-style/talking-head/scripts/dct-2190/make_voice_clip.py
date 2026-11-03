#!/usr/bin/env python3
"""Put the user's ElevenLabs voice under a talking clip, cut to a slot, speed 1.12x (as the master), -16 LUFS
(the hook's A1 clip gain -4.9 dB brings it to the master's -21.1). Audio outside [a0, a1] (source s) is silenced
with 30 ms fades, so voice-changer artifacts before and after the line never play.
Usage: make_voice_clip.py VIDEO VOICE OUT v0 frames a0 a1   (v0 = source second the clip starts, frames = slot length at 24 fps)"""
import json, subprocess, sys
SPEED, LUFS = 1.12, -16.0
video, voice, out, v0, frames, a0, a1 = sys.argv[1:8]
v0, frames, a0, a1 = float(v0), int(frames), float(a0), float(a1)
v1 = v0 + frames / 24 * SPEED
gate = f"volume=enable='lt(t,{a0})+gt(t,{a1})':volume=0,afade=t=in:st={a0-0.03}:d=0.03,afade=t=out:st={a1}:d=0.03"
af = f"[1:a]aresample=48000,{gate},atrim={v0}:{v1},asetpts=PTS-STARTPTS,atempo={SPEED}"
def run(extra_af, dst, measure=False):
    cmd = ["ffmpeg", "-v", "error" if not measure else "info", "-y", "-i", video, "-i", voice]
    if measure:
        return subprocess.run(cmd + ["-filter_complex", af + extra_af + "[a]", "-map", "[a]", "-f", "null", "-"], capture_output=True, text=True).stderr
    vf = f"[0:v]trim={v0}:{v1},setpts=(PTS-STARTPTS)/{SPEED},fps=24,format=nv12,hwupload[v]"
    subprocess.run(cmd[:3] + ["-vaapi_device", "/dev/dri/renderD128"] + cmd[3:] + ["-filter_complex", vf + ";" + af + extra_af + "[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "h264_vaapi", "-b:v", "12M", "-c:a", "aac", "-b:a", "320k", "-ac", "1", "-frames:v", str(frames), dst], check=True)
t = run(",loudnorm=print_format=json", None, True).split("[Parsed_loudnorm")[-1]
m = json.loads(t[t.index("{"):t.rindex("}") + 1])
gain = LUFS - float(m["input_i"])
run(f",volume={gain:.2f}dB,alimiter=limit=0.89:level=false", out)
print(f"{out}: {frames} f, source {v0:.2f}-{v1:.2f}s, voice {a0}-{a1}s, gain {gain:+.1f} dB (was {m['input_i']} LUFS)")
