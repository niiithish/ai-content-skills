#!/usr/bin/env python3
"""video-6 (2026-11-13, user: "clip-25: she says 'all gya' instead of 'all day'"): splice one word from the user's
ElevenLabs TTS read into hook-1's voice, unstretched apart from the 1.242x speed every other word has (the stretched
TTS on clips 11/45 sounded processed). Cut at the stop closure before the word (both sides), 8 ms crossfades, level
matched to the voice around it. Writes a new VO file; the old one is kept.
Usage: splice_word.py VO_IN VO_OUT TTS DST_START DST_END TTS_START TTS_END   (seconds in the VO / TTS files)"""
import subprocess, sys
import numpy as np

vin, vout, tts = sys.argv[1:4]
d0, d1, t0, t1 = map(float, sys.argv[4:8])
SR, SPEED, XF = 48000, 1.242, int(0.008 * 48000)


def load(p, af=""):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-af", af or "anull", "-ac", "1", "-ar", str(SR),
                                         "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32).copy()


vo = load(vin)
w = load(tts, f"atrim={t0}:{t1},asetpts=PTS-STARTPTS,atempo={SPEED}")
a, b = int(d0 * SR), int(d1 * SR)
rms = lambda x: np.sqrt((x[np.abs(x) > 1e-3] ** 2).mean())
around = np.concatenate([vo[a - int(0.25 * SR):a], vo[b:b + int(0.25 * SR)]])
w *= rms(vo[a - int(0.25 * SR):a]) / rms(w)
n = len(w)
out = vo.copy()
seg = out[a:a + n].copy()
fade = np.linspace(0, 1, XF, dtype=np.float32)
w[:XF] = w[:XF] * fade + seg[:XF] * (1 - fade)
w[-XF:] = w[-XF:] * (1 - fade) + seg[-XF:] * fade
if a + n < b:  # what's left of the old word after the new one ends is quiet tail: fade it out
    out[a + n:b] *= 0
out[a:a + n] = w
print(f"spliced {n / SR:.3f} s at {d0:.3f}-{d0 + n / SR:.3f} (old word {d1 - d0:.3f} s), gain {20*np.log10(rms(vo[a - int(0.25*SR):a]) / rms(load(tts, f'atrim={t0}:{t1}'))):+.1f} dB")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s24le", vout],
               input=out.tobytes(), check=True)
