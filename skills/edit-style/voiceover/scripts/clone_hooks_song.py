#!/usr/bin/env python3
"""Builds edit/hook-2.fcproj and hook-3.fcproj from the user's finished edit/hook-1.fcproj (every tweak, insert, split,
punch-in and the CTA card kept), retimed to song/hook-N.mp3. Hooks 2 and 3 are separate Suno takes that drift up to 3 s
from hook 1, so every cut moves to the same sung word in the other take: hook-1 song time -> hook-N song time is piecewise
linear through the words both transcripts share (song/hook-N.words.json), with the intro anchored by hand (the hooks'
first lines differ). Hook 3 opens on clip 0 (Greg leaves) under its extra first line. Captions (Video 3) are dropped;
add them per hook with captions-filmcraft. A clip stretched past its media is slowed to fit and reported.
Run only while FilmCraft is closed (it writes the files directly)."""
import bisect, json, re, statistics, subprocess, sys
from pathlib import Path

V = Path(__file__).resolve().parents[1]
EDIT = V / "edit"
SRC = EDIT / "hook-1.fcproj"
FPS, TPS = 30, 254016000000
TPF = TPS // FPS
OFF1 = 0.667  # hook 1's song starts this far in (timeline = song - OFF1)
# hand anchors (hook-1 song s -> hook-N song s) for the intro, where the words differ
INTRO = {2: [(0.56, 0.64), (4.00, 4.16), (8.00, 8.08), (10.48, 10.96), (13.84, 15.76)],
         3: [(0.56, 4.08), (4.00, 5.20), (8.00, 8.48), (10.48, 9.28), (13.84, 13.84)]}
OFFN = {2: 0.747, 3: 0.56}
CLIP0 = V / "clips/clip-0/final/clip-0-v2-1080p.mp4"


def words(h):
    return [(re.sub(r"[^a-z0-9]", "", w["word"].lower()), w["start"]) for w in json.load(open(V / f"song/hook-{h}.words.json"))]


def anchors(h):
    import difflib
    a, b = words(1), words(h)
    sm = difflib.SequenceMatcher(None, [x for x, _ in a], [x for x, _ in b], autojunk=False)
    pairs = [(a[m.a + k][1], b[m.b + k][1]) for m in sm.get_matching_blocks() if m.size >= 3 for k in range(m.size)]
    pairs = [p for p in pairs if p[0] > INTRO[h][-1][0] + 0.5]
    d = [y - x for x, y in pairs]
    keep = [p for i, p in enumerate(pairs) if abs(d[i] - statistics.median(d[max(0, i - 10):i + 11])) < 0.4]
    out = list(INTRO[h])
    for p in keep:
        if p[0] > out[-1][0] + 0.2 and p[1] > out[-1][1] + 0.1:
            out.append(p)
    return out


def mapper(h):
    an = anchors(h)
    xs = [x for x, _ in an]

    def f(t1):  # hook-1 timeline seconds -> hook-N timeline seconds
        s = t1 + OFF1
        if s <= xs[0]:
            y = an[0][1] + (s - xs[0])
        elif s >= xs[-1]:
            y = an[-1][1] + (s - xs[-1])
        else:
            i = bisect.bisect_right(xs, s) - 1
            (x0, y0), (x1, y1) = an[i], an[i + 1]
            y = y0 + (s - x0) * (y1 - y0) / (x1 - x0)
        return y - OFFN[h]
    return f, an


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def build(h):
    out = EDIT / f"hook-{h}.fcproj"
    if out.exists():
        sys.exit(f"{out.name} exists: back it up and remove it first (it may hold the user's tweaks)")
    f, an = mapper(h)
    raw = SRC.read_text().replace("song/hook-1.mp3", f"song/hook-{h}.mp3").replace('"hook-1.mp3"', f'"hook-{h}.mp3"')
    d = json.loads(raw)
    p = d["project"]
    p["name"] = f"hook-{h}"
    seq = next(v for v in p["items"].values() if "Sequence" in v.get("kind", {}))
    seq["name"] = f"Hook {h}"
    sq = seq["kind"]["Sequence"]
    media = {}
    for k, it in p["items"].items():
        m = re.search(r'"(/[^"]+\.(?:mp4|mp3))"', json.dumps(it))
        if m:
            media[int(k)] = m[1]
    lens = {}
    fr = lambda t: round(t * FPS)
    end1 = max(c["start"] + c["duration"] for t in sq["video_tracks"] for c in t["items"]) / TPS
    endN = fr(f(end1))
    report = []
    for t in sq["video_tracks"]:
        if t["name"] == "Video 3":
            t["items"] = []
            continue
        prev = {}
        for c in sorted(t["items"], key=lambda c: c["start"]):
            s1, e1 = c["start"] / TPS, (c["start"] + c["duration"]) / TPS
            a, b = fr(f(s1)), min(fr(f(e1)), endN)
            src = c["source_in"]
            pv = prev.get(c["item"])
            if pv and abs(pv[0] - src) < TPF:  # a later piece of a split clip: keep the source running on
                src = pv[1]
            c["start"], c["duration"], c["source_in"] = a * TPF, (b - a) * TPF, src
            path = media.get(c["item"])
            if path and path.endswith(".mp4"):
                L = lens.setdefault(path, dur(path))
                need = (b - a) / FPS * c["speed"]
                if src / TPS + need > L + 0.01:
                    sp = max(0.5, (L - src / TPS - 0.02) / ((b - a) / FPS))
                    c["speed"] = sp
                    for e in c["effects"]:
                        if e["effect"] == "time_remap":
                            e["params"]["speed"]["value"]["Float"] = sp * 100
                    report.append(f"{c['name']} slowed to {sp * 100:.0f}%")
            prev[c["item"]] = (c["source_in"] if not pv else pv[0], src + round((b - a) * TPF * c["speed"]))
            prev[c["item"]] = (round(src + (b - a) * TPF * c["speed"]), round(src + (b - a) * TPF * c["speed"]))
    for t in sq["audio_tracks"]:
        for c in t["items"]:
            c["start"], c["source_in"], c["duration"] = 0, round(OFFN[h] * TPS), endN * TPF
    out.write_text(json.dumps(d))
    first = min(c["start"] for c in sq["video_tracks"][0]["items"]) // TPF
    if h == 3:  # clip 0 under "He left because of her dry vaginal tissue."
        run = EDIT / ".fc-run.jsonl"
        run.write_text(json.dumps({"id": "file.import", "params": {"paths": [str(CLIP0)]}}) + "\n")
        r = subprocess.run(["filmcraft-cli", "--compact", "--project", str(out), "run", str(run), "--save"], capture_output=True, text=True)
        item = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")][0]["result"]["items"][0]
        run.write_text(json.dumps({"id": "timeline.place", "params": {"item": item, "track": "V1", "frame": 0, "insert": False,
                                                                      "sourceIn": TPS // 2, "duration": first * TPF, "audio": False}}) + "\n")
        r = subprocess.run(["filmcraft-cli", "--compact", "--project", str(out), "run", str(run), "--save"], capture_output=True, text=True)
        if '"ok":false' in r.stdout.replace(" ", "") or r.returncode:
            sys.exit(r.stdout + r.stderr)
        run.unlink()
        if first / FPS > dur(CLIP0) - 0.5:
            report.append(f"clip 0 needs {first / FPS:.2f} s, has {dur(CLIP0) - 0.5:.2f} s")
    print(f"built {out.name}: {endN / FPS:.2f} s, {len(an)} anchors" + (f", clip 0 0-{first / FPS:.2f} s" if h == 3 else ""))
    for r_ in report:
        print("  " + r_)


if __name__ == "__main__":
    for h in map(int, sys.argv[1:] or ["2", "3"]):
        build(h)
