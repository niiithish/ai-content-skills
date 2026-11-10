#!/usr/bin/env python3
"""One voice for every talking clip. Flow makes each clip's voice on its own, so they never sound like one person.

  voice_change.py export video-N [--order 1a,1b,2] [--pick 3=v9,5=v8] [--speakers jess=2,12,18] [--wav] [--lufs -19]
      Copies each talking clip's original audio, all at one loudness (--lufs, default -19, peaks under -1 dBFS), to
        video-N/audio/original/NN-clip-X.mp3                  one speaker
        video-N/audio/original/<speaker>/NN-clip-X.mp3        two or more speakers (a podcast)
      plus each speaker's whole track joined, 0.5 s of silence between clips:
        video-N/audio/original/<speaker|all>-joined.mp3       the full audio, to listen to or to voice-change in one go
      and makes the empty voice-changed/ folders (same layout). It flags words to listen for: a repeated word,
      a cut-off start ("th- third"), a word held over 0.9 s, a pause over 0.7 s inside a line.
      Then the user runs the files through the ElevenLabs voice changer, one voice per speaker, and saves the results
      in audio/voice-changed/ under the SAME names: either every clip file, or just the joined file.
  voice_change.py apply video-N
      Puts the changed voice back under each clip's picture: clips/.../final/<final>-vc.mp4 (picture copied, AAC 320k,
      padded or trimmed to the picture length). A clip with its own changed file uses it; otherwise its piece is cut
      out of the speaker's changed joined file. Lists any clip still missing.
  voice_change.py status video-N
      Which clips have been exported, changed and applied.

Clips: every talking shot (inserts are 201 up; silent listening clips "listen-*" are skipped) in the manifest order
(clips/clips-batch.json, else the clips/*.json manifest holding the most finals, else folder order), or --order.
Each uses the 1080p final clips/PICKS.md names (a line '- clip-7/final/clip-7-v2-s2-1080p.mp4'), else its newest
(v3 < v3a < v3b, a -s2 reseed after its take), unless --pick names the version.
Speakers come from each job's master still (scenes/master/jess-cu/... -> jess); --speakers overrides them.
The choice is saved in audio/original/sources.json, so apply and build_talking_head.py use exactly the same files.
"""
import json, re, subprocess, sys
from pathlib import Path

AUDIO_EXT = (".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac")
GAP = 0.5  # silence between clips in a joined file
PICKED = {}  # shot -> final from clips/PICKS.md


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def is_talking(shot):
    if shot.startswith("listen"):
        return False
    m = re.match(r"\d+", shot)
    return not m or int(m.group()) < 200  # h2, h3 (hook takes) are talking too


def shot_of(job_id):
    m = re.match(r"clip-(.+?)-v\d+", job_id)
    return m and m.group(1)


def manifest_jobs(root):
    """Jobs of clips/clips-batch.json, else of the clips/*.json manifest naming the most shots."""
    c = root / "clips"
    best = c / "clips-batch.json"
    if not best.exists():
        cands = []
        for f in c.glob("*.json"):
            try:
                jobs = [j for j in json.loads(f.read_text()).get("jobs", []) if isinstance(j, dict)]
            except (ValueError, AttributeError):
                continue
            cands.append((len({shot_of(j.get("id", "")) for j in jobs} - {None}), "final" in f.name, f))
        if not cands:
            return []
        best = max(cands)[2]
    return [j for j in json.loads(best.read_text()).get("jobs", []) if isinstance(j, dict)]


def order(root):
    if arg("--order"):
        return arg("--order").split(",")
    seen = []
    for j in manifest_jobs(root):
        s = shot_of(j.get("id", ""))
        if s and s not in seen and is_talking(s):
            seen.append(s)
    if not seen:  # no manifest: folder order
        key = lambda s: (0, int(re.match(r"\d+", s).group()), s) if re.match(r"\d", s) else (1, 0, s)
        seen = sorted((p.name[5:] for p in (root / "clips").glob("clip-*") if p.is_dir() and is_talking(p.name[5:])),
                      key=key)
    return seen


def speakers(root, shots):
    """shot -> speaker, from --speakers or from each job's master still folder."""
    out = {}
    if arg("--speakers"):
        for part in arg("--speakers").split(";"):
            name, ids = part.split("=")
            out.update({s: name for s in ids.split(",")})
        rest = [s for s in shots if s not in out]
        if rest:  # the other speaker gets the rest
            others = {p.split("=")[0] for p in arg("--speakers").split(";")}
            out.update({s: "guest" if "guest" not in others else "other" for s in rest})
        return out
    for j in manifest_jobs(root):
        s = shot_of(j.get("id", ""))
        ing = [Path(i) for i in j.get("ingredient", []) if "master" in str(i) or "scene-1" in str(i)]
        if s in shots and ing:
            out.setdefault(s, re.split(r"[-_]", ing[0].parent.name if "master" in str(ing[0].parent) else ing[0].stem)[0])
    if len(set(out.values())) < 2:
        return {}
    return out


def vkey(p):
    m = re.search(r"-v(\d+)([a-z]?)(?:-s(\d+))?-1080p", p.name)  # v3 < v3a < v3b; a -s2 reseed beats its take
    return ((int(m.group(1)), m.group(2), int(m.group(3) or 0)) if m else (0, "", 0)), p.stat().st_mtime


def picked(root):
    """shot -> final named in clips/PICKS.md (lines like '- clip-7/final/clip-7-v2-s2-1080p.mp4'; the last mention wins)."""
    f, out = root / "clips" / "PICKS.md", {}
    if f.exists():
        for m in re.finditer(r"(clip-[^\s/]+(?:/clip-[^\s/]+)?/final/clip-(.+?)-v\d+[^\s/]*-1080p\.mp4)", f.read_text()):
            p = root / "clips" / m.group(1)
            if p.exists():
                out[m.group(2)] = p
    return out


def shot_dir(root, shot):
    nested = root / "clips" / f"clip-{shot[:-1]}" / f"clip-{shot}" / "final"
    return nested if shot[-1].isalpha() and nested.exists() else root / "clips" / f"clip-{shot}" / "final"


def final(root, shot, picks):
    d = shot_dir(root, shot)
    if shot in picks:
        p = d / f"clip-{shot}-{picks[shot]}-1080p.mp4"
        if not p.exists():
            sys.exit(f"--pick {shot}={picks[shot]}: {p} not found")
        return p
    if shot in PICKED:
        return PICKED[shot]
    files = sorted((p for p in d.glob(f"clip-{shot}-v*-1080p.mp4") if not p.stem.endswith("-vc")), key=vkey)
    if not files:
        sys.exit(f"no 1080p final for {shot} in {d}")
    return files[-1]


def loudness(p):
    """Integrated LUFS and true peak (dBFS) of a file's audio."""
    e = subprocess.run(["ffmpeg", "-nostats", "-i", str(p), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    s = e[e.rindex("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1))
    pk = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", s).group(1)
    return i, (float(pk) if pk != "-inf" else -99.0)


def words_of(src):
    for w in (src.with_suffix(".words.json"), src.with_name(src.stem.replace("-1080p", "") + ".words.json")):
        if w.exists():
            return json.loads(w.read_text())
    return None


def listen_for(words):
    """Spots a listener should check: repeats, cut-off starts, held words, long pauses (from the clip's words.json)."""
    flags = []
    clean = lambda w: re.sub(r"[^a-z0-9']", "", w["word"].lower())
    for a, b in zip(words, words[1:]):
        wa, wb = clean(a), clean(b)
        if wa and wa == wb and wa not in ("very", "really", "no", "so"):
            flags.append(f"'{wa} {wb}' at {a['start']:.1f} s (said twice?)")
        elif wa and len(wa) <= 3 and wb.startswith(wa) and wb != wa:
            flags.append(f"'{a['word']} {b['word']}' at {a['start']:.1f} s (cut-off start?)")
        elif b["start"] - a["end"] > 0.7:
            flags.append(f"{b['start'] - a['end']:.1f} s pause before '{b['word']}' at {a['end']:.1f} s")
    for w in words:
        if w["end"] - w["start"] > 0.9:
            flags.append(f"'{w['word']}' held {w['end'] - w['start']:.1f} s at {w['start']:.1f} s (stretched or fumbled?)")
    return flags


def export(root):
    picks = dict(x.split("=") for x in arg("--pick", "").split(",") if x)
    target = float(arg("--lufs", "-19"))
    orig, changed = root / "audio" / "original", root / "audio" / "voice-changed"
    ext = ".wav" if "--wav" in sys.argv else ".mp3"
    codec = ["-c:a", "pcm_s16le"] if ext == ".wav" else ["-c:a", "libmp3lame", "-b:a", "320k"]
    PICKED.update(picked(root))
    shots = order(root)
    who = speakers(root, shots)
    for d in [orig, changed] + [orig / s for s in set(who.values())] + [changed / s for s in set(who.values())]:
        d.mkdir(parents=True, exist_ok=True)
    for old in list(orig.glob("[0-9][0-9]-clip-*")) + list(orig.glob("*/[0-9][0-9]-clip-*")) + list(orig.glob("*-joined.*")) \
            + list(orig.glob("*/*-joined.*")):
        old.unlink()  # a re-export replaces the set, so no stale file gets voice-changed
    rows, total, flagged = [], 0.0, []
    for i, shot in enumerate(shots, 1):
        src = final(root, shot, picks)
        sp = who.get(shot)
        name = (f"{sp}/" if sp else "") + f"{i:02d}-clip-{shot}"
        lufs, peak = loudness(src)
        gain = round(min(target - lufs, -1.0 - peak), 1)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-vn", "-ac", "1",
                        "-af", f"volume={gain}dB", *codec, str(orig / f"{name}{ext}")], check=True)
        d = dur(src)
        total += d
        rows.append({"name": name, "shot": shot, "speaker": sp, "final": str(src.relative_to(root)),
                     "seconds": round(d, 3), "lufs": lufs, "gain_db": gain})
        w = words_of(src)
        for f in listen_for(w) if w else []:
            flagged.append(f"  clip-{shot}: {f}")
    # each speaker's joined track, GAP s apart; offsets saved so apply can cut a changed joined file back up
    for sp in sorted({r["speaker"] for r in rows}, key=str):
        mine = [r for r in rows if r["speaker"] == sp]
        t = 0.0
        for r in mine:
            r["joined_at"] = round(t, 3)
            t += r["seconds"] + GAP
        jname = (f"{sp}/{sp}" if sp else "all") + f"-joined{ext}"
        inputs, parts = [], []
        for k, r in enumerate(mine):
            inputs += ["-i", str(orig / f"{r['name']}{ext}")]
            parts.append(f"[{k}:a]aresample=48000,apad=whole_dur={r['seconds'] + GAP:.3f}[a{k}]")
        fc = ";".join(parts) + ";" + "".join(f"[a{k}]" for k in range(len(mine))) + f"concat=n={len(mine)}:v=0:a=1[out]"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc,
                        "-map", "[out]", "-ac", "1", *codec, str(orig / jname)], check=True)
        for r in mine:
            r["joined"] = jname
    (orig / "sources.json").write_text(json.dumps(rows, indent=1) + "\n")
    groups = sorted({r["speaker"] for r in rows}, key=str)
    print(f"Copied the original audio of {len(rows)} clips ({total:.0f} s) to {orig}, all at {target:g} LUFS"
          + (f", in {len(groups)} speaker folders ({', '.join(groups)})" if who else "") + ":")
    for r in rows:
        print(f"  {r['name']}{ext}  {r['seconds']:6.2f} s  {r['gain_db']:+5.1f} dB  from {r['final']}")
    print("Full audio: " + ", ".join(str((orig / r).relative_to(root)) for r in sorted({r["joined"] for r in rows})))
    if flagged:
        print("\nListen to these before the voice change (a fumble here goes into every hook):\n" + "\n".join(flagged))
    per = " (one voice per speaker folder)" if who else ""
    print(f"\nReady for ElevenLabs{per}: voice-change either each clip file or the joined file, and save the result in\n"
          f"  {changed}\nunder the same name and folder (01-clip-1.mp3 → 01-clip-1.mp3). Then: voice_change.py apply {root.name}")


def changed_file(root, name):
    for e in AUDIO_EXT:
        p = root / "audio" / "voice-changed" / f"{name}{e}"
        if p.exists():
            return p


def load(root):
    f = root / "audio" / "original" / "sources.json"
    if not f.exists():
        sys.exit(f"nothing exported yet: run voice_change.py export {root.name}")
    return json.loads(f.read_text())


def vc_path(root, r):
    src = root / r["final"]
    return src.with_name(src.stem + "-vc.mp4")


def source_of(root, r):
    """(audio file, start s or None) holding this clip's changed voice."""
    own = changed_file(root, r["name"])
    if own:
        return own, None
    if r.get("joined"):
        j = changed_file(root, str(Path(r["joined"]).with_suffix("")))
        if j:
            return j, r["joined_at"]
    return None, None


def apply(root):
    rows, done, missing = load(root), [], []
    for r in rows:
        a, at = source_of(root, r)
        if not a:
            missing.append(r["name"])
            continue
        src, out = root / r["final"], vc_path(root, r)
        vd = dur(src)
        cut = ["-ss", f"{at:.3f}", "-t", f"{vd:.3f}"] if at is not None else []
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), *cut, "-i", str(a),
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af", "apad", "-t", f"{vd:.3f}",
                        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out)], check=True)
        flag = ""
        if at is None and abs(vd - dur(a)) >= 0.15:
            flag = f"  ← changed audio is {dur(a) - vd:+.2f} s vs the picture, check the sync"
        done.append(f"  {out.relative_to(root)}" + (f"  (from {a.name} at {at:.2f} s)" if at is not None else "") + flag)
    joined = {r["joined"] for r in rows if r.get("joined")}
    for j in joined:  # a changed joined file must keep the original's length, or every later clip drifts
        a = changed_file(root, str(Path(j).with_suffix("")))
        o = root / "audio" / "original" / j
        if a and abs(dur(a) - dur(o)) > 0.15:
            done.append(f"  ← {a.name} is {dur(a) - dur(o):+.2f} s vs the original joined file: later clips drift, "
                        f"voice-change the clip files instead")
    print(f"{len(rows) - len(missing)} of {len(rows)} clips now have the changed voice:")
    print("\n".join(done))
    if missing:
        print(f"\nStill missing in audio/voice-changed/: {', '.join(missing)}")


def status(root):
    for r in load(root):
        a, at = source_of(root, r)
        c = "-" if not a else ("changed" if at is None else "joined")
        ap = "applied" if vc_path(root, r).exists() else "-"
        print(f"  {r['name']:24} {r['seconds']:6.2f} s  {c:8} {ap}")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("export", "apply", "status"):
        sys.exit(__doc__)
    root = Path(sys.argv[2]).resolve()
    {"export": export, "apply": apply, "status": status}[sys.argv[1]](root)
