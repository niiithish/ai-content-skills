#!/usr/bin/env python3
"""Pre-handback QA check for FilmCraft projects (.fcproj) and exported renders (.mp4/.mov).

Checks:
  For .fcproj:
    - All referenced media files exist on disk (no offline media)
    - No fractional-frame clips (when filmcraft-cli is available)
    - Sequence duration and track counts
  For .mp4/.mov/.mkv (exported preview or deliverable):
    - Codecs (H.264 video + AAC audio), resolution, fps, duration, file size
    - Black frames via ffmpeg `blackdetect` (catches accidental black flashes/gaps)
    - Excessive silence gaps via ffmpeg `silencedetect`
    - Audio peak / mean volume via ffmpeg `volumedetect` (catches clipping or dead/muted audio)

Usage:
  fc_qa.py edit/hook-1.fcproj
  fc_qa.py deliverables/hook-1.mp4 [--max-silence 0.45] [--silence-db -42] [--black-min 0.04]
Exit 1 if any FAIL is reported, 0 otherwise.
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

TPS = 254016000000


def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def walk_dict(obj, fn):
    if isinstance(obj, dict):
        fn(obj)
        for v in obj.values():
            walk_dict(v, fn)
    elif isinstance(obj, list):
        for v in obj:
            walk_dict(v, fn)


def qa_fcproj(path: Path) -> int:
    fails = 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"FAIL cannot parse {path}: {e}")
        return 1

    # 1. Missing media check directly from .fcproj JSON
    media = set()
    def collect(o):
        f = o.get("File") if isinstance(o.get("File"), dict) else None
        if f and isinstance(f.get("path"), str):
            media.add(f["path"])
    walk_dict(data, collect)

    missing = sorted(m for m in media if not Path(m).exists())
    if missing:
        for m in missing:
            print(f"FAIL missing media: {m}")
        fails += len(missing)
    else:
        print(f"OK   all {len(media)} media paths exist on disk")

    # 2. Sequence inspection via filmcraft-cli (if available)
    if shutil.which("filmcraft-cli"):
        r = run_cmd(["filmcraft-cli", "--compact", "--project", str(path), "inspect", "sequence"])
        if r.returncode == 0 and r.stdout.strip():
            seq = json.loads(r.stdout)
            fr = (seq.get("settings") or {}).get("frame_rate") or {}
            if isinstance(fr, dict) and fr.get("num") and fr.get("den"):
                fps = float(fr["num"]) / float(fr["den"])
            else:
                fps = float(seq.get("fps") or seq.get("frameRate") or 24)
            ticks_per_frame = round(TPS / fps)
            v_tracks = seq.get("video", [])
            a_tracks = seq.get("audio", [])
            frac = []
            for ti, t in enumerate(v_tracks, 1):
                for c in t.get("items", []):
                    st, dur = c.get("start", 0), c.get("duration", 0)
                    if st % ticks_per_frame or dur % ticks_per_frame:
                        frac.append((f"V{ti}", c.get("clip"), c.get("name", "?"),
                                     st / ticks_per_frame, dur / ticks_per_frame))
            if frac:
                for tr, cid, name, sf, df in frac[:15]:
                    print(f"FAIL fractional clip {tr} #{cid} {name}: start={sf:.4f}f dur={df:.4f}f")
                fails += len(frac)
            else:
                print(f"OK   all timeline clips align to whole frames ({fps} fps)")
            dur_f = seq.get("durationFrames", 0)
            print(f"INFO sequence: {len(v_tracks)} video track(s), {len(a_tracks)} audio track(s), {dur_f} frames ({dur_f / float(fps):.2f}s)")
        else:
            print(f"WARN filmcraft-cli inspect failed (skipping frame-alignment check): {r.stderr.strip()[-160:]}")
    else:
        print("WARN filmcraft-cli not on PATH (skipped timeline frame-alignment check)")

    return fails


def qa_media(path: Path, max_silence: float, silence_db: float, black_min: float) -> int:
    fails = 0
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        print("FAIL ffmpeg/ffprobe required for media QA")
        return 1

    # 1. Probe streams
    pr = run_cmd(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)])
    if pr.returncode != 0:
        print(f"FAIL ffprobe failed: {pr.stderr.strip()[-200:]}")
        return 1
    info = json.loads(pr.stdout)
    streams = info.get("streams", [])
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    dur = float(info.get("format", {}).get("duration", 0) or 0)
    size_mb = path.stat().st_size / (1024 * 1024)

    if not v_stream:
        print("FAIL no video stream")
        fails += 1
    else:
        vc = v_stream.get("codec_name", "?")
        w, h = v_stream.get("width", 0), v_stream.get("height", 0)
        if vc != "h264":
            print(f"WARN video codec is {vc} (Meta deliverables expect h264)")
        else:
            print(f"OK   video: {vc} {w}x{h} {dur:.2f}s ({size_mb:.1f} MB)")

    if not a_stream:
        print("FAIL no audio stream")
        fails += 1
    else:
        ac = a_stream.get("codec_name", "?")
        sr = a_stream.get("sample_rate", "?")
        if ac != "aac":
            print(f"WARN audio codec is {ac} (Meta deliverables expect aac)")
        else:
            print(f"OK   audio: {ac} {sr} Hz")

    # 2. Black frame detection
    if v_stream:
        br = run_cmd([
            "ffmpeg", "-v", "info", "-i", str(path),
            "-vf", f"blackdetect=d={black_min}:pix_th=0.05",
            "-an", "-f", "null", "-"
        ])
        blacks = re.findall(r"black_start:([\d.]+)\s+black_end:([\d.]+)\s+black_duration:([\d.]+)", br.stderr)
        # Ignore tiny trailing black at very end (<0.15s) if any, flag everything else
        real_blacks = [(float(s), float(e), float(d)) for s, e, d in blacks if not (dur > 0 and float(s) >= dur - 0.15 and float(d) < 0.15)]
        if real_blacks:
            for s, e, d in real_blacks[:10]:
                print(f"FAIL black frames: {s:.2f}s -> {e:.2f}s ({d:.2f}s)")
            fails += len(real_blacks)
        else:
            print("OK   no black frames detected")

    # 3. Silence & volume detection
    if a_stream:
        ar = run_cmd([
            "ffmpeg", "-v", "info", "-i", str(path),
            "-af", f"silencedetect=noise={silence_db}dB:d={max_silence},volumedetect",
            "-vn", "-f", "null", "-"
        ])
        silences = re.findall(r"silence_start:\s*([\d.]+).*?silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)", ar.stderr, re.S)
        # Filter out leading/trailing fades (<0.8s at very start or very end)
        mid_silences = []
        for s, e, d in silences:
            sf, ef, df = float(s), float(e), float(d)
            if sf < 0.25 or (dur > 0 and ef > dur - 0.5):
                continue
            mid_silences.append((sf, ef, df))
        if mid_silences:
            for s, e, d in mid_silences[:10]:
                print(f"FAIL silence gap > {max_silence:.2f}s: {s:.2f}s -> {e:.2f}s ({d:.2f}s)")
            fails += len(mid_silences)
        else:
            print(f"OK   no mid-video silence gaps > {max_silence:.2f}s (at {silence_db} dB)")

        mean_m = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", ar.stderr)
        max_m = re.search(r"max_volume:\s*([-\d.]+)\s*dB", ar.stderr)
        mean_v = float(mean_m.group(1)) if mean_m else None
        max_v = float(max_m.group(1)) if max_m else None
        if mean_v is not None and mean_v < -50.0:
            print(f"FAIL audio appears nearly silent (mean {mean_v:.1f} dB)")
            fails += 1
        elif max_v is not None and max_v >= -0.1:
            print(f"WARN audio peak near/at clipping (max {max_v:.1f} dB, mean {mean_v:.1f} dB)")
        elif mean_v is not None:
            print(f"OK   audio level: mean {mean_v:.1f} dB, peak {max_v:.1f} dB")

    return fails


def main():
    ap = argparse.ArgumentParser(description="Pre-handback QA for FilmCraft .fcproj or exported video.")
    ap.add_argument("target", help="Path to .fcproj or exported .mp4/.mov")
    ap.add_argument("--max-silence", type=float, default=0.50, help="Max allowed mid-video silence in seconds (default: 0.50)")
    ap.add_argument("--silence-db", type=float, default=-42.0, help="Silence threshold in dB (default: -42)")
    ap.add_argument("--black-min", type=float, default=0.04, help="Min black duration in seconds (~1 frame at 24fps, default: 0.04)")
    a = ap.parse_args()

    p = Path(a.target).resolve()
    if not p.exists():
        sys.exit(f"FAIL target not found: {p}")

    if p.suffix.lower() == ".fcproj":
        fails = qa_fcproj(p)
    else:
        fails = qa_media(p, a.max_silence, a.silence_db, a.black_min)

    print("RESULT: FAIL" if fails else "RESULT: PASS")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
