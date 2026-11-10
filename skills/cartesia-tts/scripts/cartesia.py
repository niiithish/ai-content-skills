#!/usr/bin/env python3
"""Cartesia text-to-speech from the terminal: browse voices, hear their previews, read a script with exact word times.

  cartesia voices [WORDS] [--gender feminine|masculine] [--lang en] [--mine] [--limit 20] [--previews DIR]
      List voices (id, name, gender, tagline). --previews DIR downloads each listed voice's sample as
      DIR/<name>-<id8>.mp3 so the user can listen and pick.
  cartesia say (TEXT | --script FILE) --voice ID --out OUT.wav
               [--speed 1.0] [--volume 1.0] [--emotion calm] [--model sonic-3.6] [--lang en] [--gap 0.4]
      Read TEXT, or FILE one spoken line per row (blank lines and # headings skipped, "1." / "-" stripped).
      Each line is one request (cached in OUT.lines/, so changing one line rereads only that one), joined with
      GAP seconds of silence. Writes OUT.wav, OUT.words.json (Cartesia's own word times, the same layout as
      `transcribe`), OUT.lines.json (each line's start/end) and OUT.voice.json (the settings used).
  cartesia audition (TEXT | --script FILE) --voices ID,ID,... --out DIR [--lines 2] [say options]
      The first LINES lines read by each voice, one DIR/<name>-<id8>.wav each, for the user to compare.
  cartesia emotions | models
      What --emotion and --model accept.

Inline tags work inside the text: <emotion value="sad"/>, <speed ratio="0.9"/>, <volume ratio="1.2"/>, [laughter].
The key is read from $CARTESIA_API_KEY, else ~/.config/cartesia/api_key (chmod 600). Never print it.
Docs: https://docs.cartesia.ai (API version below; latest model alias sonic-3.6).
"""
import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path

API = "https://api.cartesia.ai"
VERSION = "2026-08-14"
MODEL = "sonic-3.6"  # alias of the latest stable snapshot (sonic-3.6-2026-08-27 when it was written)
MODELS = {"sonic-3.6": "latest stable (default)", "sonic-3.6-2026-08-27": "pinned snapshot: never changes",
          "sonic-3.5": "previous", "sonic-3": "older", "sonic-preview": "beta, not for delivery"}
EMOTIONS = ("neutral calm content sad angry scared happy excited enthusiastic elated euphoric triumphant amazed surprised "
            "flirtatious curious peaceful serene grateful affectionate trust sympathetic anticipation mysterious mad "
            "outraged frustrated agitated threatened disgusted contempt envious sarcastic ironic dejected melancholic "
            "disappointed hurt guilty bored tired rejected nostalgic wistful apologetic hesitant insecure confused "
            "resigned anxious panicked alarmed proud confident distant skeptical contemplative determined").split()
BEST = EMOTIONS[:6]  # Cartesia: these six are the most reliable
RATE, WIDTH = 44100, 2
UA = "cartesia-cli/1.0"  # files.cartesia.ai answers 403 to the default Python-urllib agent


def die(msg):
    sys.exit(f"cartesia: {msg}")


def key():
    k = os.environ.get("CARTESIA_API_KEY", "").strip()
    f = Path.home() / ".config" / "cartesia" / "api_key"
    if not k and f.is_file():
        k = f.read_text().strip()
    if not k:
        die("no key: save it once to ~/.config/cartesia/api_key (chmod 600)")
    return k


def request(path, body=None, stream=False):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, headers={
        "Cartesia-Version": VERSION, "Authorization": f"Bearer {key()}", "Content-Type": "application/json", "User-Agent": UA})
    try:
        r = urllib.request.urlopen(req, timeout=180)
    except urllib.error.HTTPError as e:
        die(f"{e.code} {e.read().decode(errors='replace')[:400]}")
    except urllib.error.URLError as e:
        die(f"network: {e.reason}")
    return r if stream else r.read()


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kw):
        return None


def download(url):
    """A preview file: authorised on files.cartesia.ai, which redirects to a signed storage URL that must get no key."""
    req = urllib.request.Request(url, headers={"Cartesia-Version": VERSION, "Authorization": f"Bearer {key()}", "User-Agent": UA})
    try:
        return urllib.request.build_opener(_NoRedirect).open(req, timeout=60).read()
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
            return urllib.request.urlopen(urllib.request.Request(e.headers["Location"], headers={"User-Agent": UA}), timeout=60).read()
        raise


def save_preview(data, dest):
    """Previews come as headerless 16-bit 44.1 kHz mono PCM (audio/pcm, checked by speaking rate); mp3/wav pass through."""
    if data[:3] == b"ID3" or data[:2] in (b"\xff\xfb", b"\xff\xf3") or data[:4] == b"RIFF":
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", "pipe:", str(dest)]
    else:
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(RATE), "-ac", "1", "-i", "pipe:", str(dest)]
    subprocess.run(cmd, input=data, check=True)


def cmd_voices(a):
    q = {"limit": a.limit, "expand[]": "preview_file_url"}
    if a.words:
        q["q"] = " ".join(a.words)
    if a.gender:
        q["gender"] = a.gender
    if a.lang:
        q["language"] = a.lang
    if a.mine:
        q["is_owner"] = "true"
    voices = json.loads(request("/voices?" + urllib.parse.urlencode(q)))["data"]
    if not voices:
        print("no voices match")
    out = Path(a.previews).expanduser() if a.previews else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    for v in voices:
        print(f"{v['id']}  {v['name'][:22]:<22} {(v.get('gender') or '-')[:9]:<9} {(v.get('tagline') or v.get('description') or '')[:90]}")
        if out and v.get("preview_file_url"):
            dest = out / f"{re.sub(r'[^A-Za-z0-9]+', '-', v['name']).strip('-').lower()}-{v['id'][:8]}.mp3"
            if not dest.is_file():
                try:
                    save_preview(download(v["preview_file_url"]), dest)
                except (urllib.error.URLError, subprocess.CalledProcessError) as e:
                    print(f"    (no preview: {e})")
    if out:
        print(f"previews: {out}")


def lines_of(a):
    if a.script:
        lines = []
        for raw in Path(a.script).expanduser().read_text().splitlines():
            s = raw.strip()
            if s and not s.startswith("#"):
                lines.append(re.sub(r"^(\d+[.)]|[-*])\s+", "", s).strip().strip('"“”'))
        return lines
    return [" ".join(a.text)]


def read_line(text, a):
    """One SSE request: raw 16-bit PCM plus Cartesia's word times for this line."""
    body = {"model_id": a.model, "transcript": text, "voice": {"mode": "id", "id": a.voice}, "language": a.lang,
            "output_format": {"container": "raw", "encoding": "pcm_s16le", "sample_rate": RATE},
            "add_timestamps": True, "use_normalized_timestamps": False,
            "generation_config": {"speed": a.speed, "volume": a.volume, **({"emotion": a.emotion} if a.emotion else {})}}
    pcm, words = bytearray(), []
    for raw in request("/tts/sse", body, stream=True):
        line = raw.decode().strip()
        if not line.startswith("data:"):
            continue
        ev = json.loads(line[5:])
        if ev.get("type") == "chunk" and ev.get("data"):
            pcm += base64.b64decode(ev["data"])
        elif ev.get("type") == "timestamps":
            w = ev["word_timestamps"]
            words += [{"word": x, "start": s, "end": e} for x, s, e in zip(w["words"], w["start"], w["end"])]
        elif ev.get("type") == "error":
            die(f"{ev.get('status_code')} {ev.get('title')}: {ev.get('message')}")
    return bytes(pcm), words


def cmd_say(a):
    if not (0.6 <= a.speed <= 1.5):
        die("--speed is 0.6 to 1.5")
    if not (0.5 <= a.volume <= 2.0):
        die("--volume is 0.5 to 2.0")
    if a.emotion and a.emotion not in EMOTIONS:
        die(f"--emotion must be one of: {' '.join(EMOTIONS)}")
    lines = lines_of(a)
    if not lines or not any(lines):
        die("nothing to read")
    out = Path(a.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    cache = out.with_suffix(".lines")
    cache.mkdir(exist_ok=True)
    used, all_words, spans, t = set(), [], [], 0.0
    gap = b"\0" * (int(a.gap * RATE) * WIDTH)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1), w.setsampwidth(WIDTH), w.setframerate(RATE)
        for i, text in enumerate(lines, 1):
            h = hashlib.sha1("|".join(map(str, [text, a.model, a.voice, a.speed, a.volume, a.emotion, a.lang])).encode()).hexdigest()[:10]
            pf, jf = cache / f"{i:03d}-{h}.pcm", cache / f"{i:03d}-{h}.json"
            if pf.is_file() and jf.is_file():
                pcm, words = pf.read_bytes(), json.loads(jf.read_text())
            else:
                print(f"reading line {i}/{len(lines)}: {text[:70]}", flush=True)
                pcm, words = read_line(text, a)
                pf.write_bytes(pcm), jf.write_text(json.dumps(words))
            used |= {pf, jf}
            d = len(pcm) / (RATE * WIDTH)
            w.writeframes(pcm + (gap if i < len(lines) else b""))
            all_words += [{"word": x["word"], "start": round(t + x["start"], 3), "end": round(t + x["end"], 3)} for x in words]
            spans.append({"line": i, "text": text, "start": round(t, 3), "end": round(t + d, 3)})
            t += d + (a.gap if i < len(lines) else 0)
    for f in cache.iterdir():
        f in used or f.unlink()
    stem = out.with_suffix("")
    Path(f"{stem}.words.json").write_text(json.dumps(all_words, indent=0))
    Path(f"{stem}.lines.json").write_text(json.dumps(spans, indent=1))
    Path(f"{stem}.voice.json").write_text(json.dumps({"voice": a.voice, "model": a.model, "speed": a.speed, "volume": a.volume,
                                                      "emotion": a.emotion, "lang": a.lang, "gap": a.gap}, indent=1))
    n = len(all_words)
    print(f"{out}  {t:.1f} s, {len(lines)} lines, {n} words ({n / t * 60:.0f} wpm)" if t else str(out))


def cmd_audition(a):
    names = {}
    for vid in a.voices.split(","):
        vid = vid.strip()
        try:
            names[vid] = json.loads(request(f"/voices/{vid}"))["name"]
        except SystemExit:
            names[vid] = "voice"
    out = Path(a.out).expanduser()
    lines = lines_of(a)[: a.lines]
    tmp = out / ".script.txt"
    out.mkdir(parents=True, exist_ok=True)
    tmp.write_text("\n".join(lines) + "\n")
    for vid, name in names.items():
        b = argparse.Namespace(**{**vars(a), "voice": vid, "script": str(tmp), "text": [],
                                  "out": str(out / f"{re.sub(r'[^A-Za-z0-9]+', '-', name).strip('-').lower()}-{vid[:8]}.wav")})
        cmd_say(b)
    tmp.unlink()


def say_options(s):
    s.add_argument("--model", default=MODEL)
    s.add_argument("--speed", type=float, default=1.0)
    s.add_argument("--volume", type=float, default=1.0)
    s.add_argument("--emotion")
    s.add_argument("--lang", default="en")
    s.add_argument("--gap", type=float, default=0.4)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("voices")
    v.add_argument("words", nargs="*")
    v.add_argument("--gender", choices=["feminine", "masculine", "gender_neutral"])
    v.add_argument("--lang", default="en")
    v.add_argument("--mine", action="store_true", help="only voices you cloned or made")
    v.add_argument("--limit", type=int, default=20)
    v.add_argument("--previews", metavar="DIR")
    s = sub.add_parser("say")
    s.add_argument("text", nargs="*")
    s.add_argument("--script")
    s.add_argument("--voice", required=True)
    s.add_argument("--out", required=True)
    say_options(s)
    au = sub.add_parser("audition")
    au.add_argument("text", nargs="*")
    au.add_argument("--script")
    au.add_argument("--voices", required=True)
    au.add_argument("--out", required=True)
    au.add_argument("--lines", type=int, default=2)
    say_options(au)
    sub.add_parser("emotions")
    sub.add_parser("models")
    a = p.parse_args()
    if a.cmd == "voices":
        cmd_voices(a)
    elif a.cmd == "say":
        if bool(a.text) == bool(a.script):
            die("give the TEXT or --script FILE")
        cmd_say(a)
    elif a.cmd == "audition":
        if bool(a.text) == bool(a.script):
            die("give the TEXT or --script FILE")
        cmd_audition(a)
    elif a.cmd == "emotions":
        print("most reliable:", " ".join(BEST))
        print("all:", " ".join(EMOTIONS))
    else:
        for m, d in MODELS.items():
            print(f"{m:<22} {d}")


if __name__ == "__main__":
    main()
