#!/usr/bin/env python3
"""One tool for an animated video project: Flow batches, review sheets, picks, rough cut, handoff.

Run from anywhere; it works on the video folder that contains this scripts/ folder.

  make.py status                       every shot: newest still, clip, final
  make.py stills [shots] [--dry-run]   generate stills in scenes/stills-batch.json (jobs whose
                                       ingredient is an unmade still wait for it)
  make.py clips  [shots] [--dry-run]   generate 360p drafts in clips/clips-batch.json
  make.py finals [shots] [--into DIR] [--no-draft] [--dry-run]
                                       native 720p + 1080p upsample of each clip
  make.py pick 1a 2 [--clip]           keep take 2 as the shot's version
  make.py review stills|clips|finals [shots]
                                       contact sheets in review/ (one image per page)
  make.py animatic                     edit/animatic.mp4: clips where they exist,
                                       stills elsewhere, over voiceover/recording.* if present
  make.py handoff                      edit/clips/01-....mp4 in story order for the editor
  make.py sync                         refresh scenes/all and clips/all

Shots are ids like 3 (a scene with one shot), 1a or 10b. Story order is the job order in scenes/stills-batch.json.

A manifest job may carry "variants": 2-4. Each variant is a take with its own seed, saved in the
shot's takes/ folder (scene-4/takes/scene-4-v1-take1.jpg, -take2, ...) until `pick` copies one
up to scene-4-v1.jpg. Letters in a name only ever mean a shot (4a, 4b), never a take. Jobs whose
output already exists are skipped, so any command can be rerun after an interruption.

Settings come from ../project.conf (CONCURRENCY, RPM). Accounts are flow's job: it sends stills and
360p drafts to free accounts first, and finals (720p + 1080p upsample) only to paid ones.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

VIDEO = Path(__file__).resolve().parent.parent
KINDS = {
    "stills": {"folder": "scenes", "stem": "scene", "manifest": "stills-batch.json", "ext": ".jpg"},
    "clips": {"folder": "clips", "stem": "clip", "manifest": "clips-batch.json", "ext": ".mp4"},
}
MAX_TAKES = 4
BASE_SEED = 12345
JOB_ID = re.compile(r"^(scene|clip)-((0|[1-9]\d*)([a-z]?))-v([1-9]\d*)$")  # scene-3-v1 (one-shot scene) or scene-3a-v1
FONTS = [
    "/usr/share/fonts/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]
FONT = next((f for f in FONTS if Path(f).is_file()), None)


def die(msg):
    sys.exit(f"error: {msg}")


def conf():
    c = {"CONCURRENCY": "3", "RPM": "6"}
    p = VIDEO / "project.conf"
    if p.is_file():
        for line in p.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                k, v = line.split("=", 1)
                c[k.strip()] = v.strip().strip("\"'")
    return c


# ---------- manifests ----------

def manifest_path(kind):
    return VIDEO / KINDS[kind]["folder"] / KINDS[kind]["manifest"]


def load_jobs(kind):
    path = manifest_path(kind)
    if not path.is_file():
        return []
    data = json.loads(path.read_text())
    jobs = data["jobs"] if isinstance(data, dict) else data
    stem = KINDS[kind]["stem"]
    for j in jobs:
        m = JOB_ID.match(j.get("id", ""))
        if not m or m[1] != stem:
            die(f"{path.name}: job id {j.get('id')!r} must look like {stem}-3-v1 (a one-shot scene) or {stem}-1a-v1 (scene number, shot letter, version)")
        for key in ("prompt_file", "output"):
            j[key] = str((path.parent / j[key]).resolve())
        if Path(j["output"]).name != j["id"] + KINDS[kind]["ext"]:
            die(f"{path.name}: job {j['id']} must write {j['id']}{KINDS[kind]['ext']}, not {Path(j['output']).name}")
        j["ingredient"] = [str((path.parent / p).resolve()) for p in j.get("ingredient", [])]
        folder = VIDEO / KINDS[kind]["folder"] / f"{stem}-{m[3]}" / (f"{stem}-{m[2]}" if m[4] else "")
        if Path(j["output"]).parent != folder:
            die(f"{path.name}: job {j['id']} must write into {folder.relative_to(VIDEO)}/")
    scenes = {}
    for j in jobs:
        m = JOB_ID.match(j["id"])
        scenes.setdefault(m[3], set()).add(m[4])
    mixed = sorted((n for n, letters in scenes.items() if "" in letters and len(letters) > 1), key=int)
    if mixed:
        die(f"{path.name}: scene {', '.join(mixed)} has both a one-shot id ({stem}-N-v1) and lettered shots: "
            f"once a scene has two shots, rename its first shot to {stem}-Na (folder {stem}-N/{stem}-Na/)")
    return jobs


def shot(job):
    return JOB_ID.match(re.sub(r"-take\d$", "", job["id"]))[2]  # take jobs end in -take1, -take2, ...


def version(job):
    return int(JOB_ID.match(job["id"])[5])


def select(jobs, shots):
    if not shots:
        return jobs
    want = [s.lower() for s in shots]
    unknown = set(want) - {shot(j) for j in jobs}
    if unknown:
        die("no job for: " + ", ".join(sorted(unknown)))
    return [j for j in jobs if shot(j) in want]


def story_order():
    """Shot ids in story order: stills manifest first, then any clip-only shots."""
    order = []
    for kind in ("stills", "clips"):
        for j in load_jobs(kind):
            if shot(j) not in order:
                order.append(shot(j))
    return order


def variant_paths(out):
    return [out.parent / "takes" / f"{out.stem}-take{i}{out.suffix}" for i in range(1, MAX_TAKES + 1)]


def take_no(path):
    return path.stem.rsplit("-take", 1)[1]


def expand(jobs):
    """One flow job per variant; a shot that was already picked is not regenerated."""
    run = []
    for j in jobs:
        j = dict(j)
        n = int(j.pop("variants", 1))
        out = Path(j["output"])
        if n <= 1 or out.is_file():
            run.append(j)
            continue
        base = int(j.get("seed", BASE_SEED))
        for i, path in enumerate(variant_paths(out)[:n]):
            path.parent.mkdir(exist_ok=True)
            run.append({**j, "id": f"{j['id']}-take{i + 1}", "output": str(path), "seed": base + 1000 * i})
    return run


def check_inputs(jobs):
    missing = sorted({p for j in jobs for p in [j["prompt_file"], *j["ingredient"]] if not Path(p).is_file()})
    if missing:
        die("missing files:\n  " + "\n  ".join(missing))


def split_ready(run):
    """Drop jobs whose output exists (flow rejects a batch that feeds one job's output into another,
    even a finished one) and hold back jobs whose ingredient is a still or clip not made yet."""
    made_by = {j["output"]: j["id"] for kind in KINDS for j in load_jobs(kind)}
    todo = [j for j in run if not Path(j["output"]).is_file()]
    ready, waiting = [], {}
    for j in todo:
        deps = sorted({made_by[p] for p in j["ingredient"] if p in made_by and not Path(p).is_file()})
        if deps:
            waiting[shot(j)] = deps
        else:
            ready.append(j)
    return ready, waiting


def run_batch(jobs, name, dry):
    c = conf()
    folder = VIDEO / ("scenes" if name == "stills" else "clips")
    run_file = folder / f".run-{name}.json"
    run_file.write_text(json.dumps({"jobs": jobs}, indent=2))
    logs = folder / ".logs"
    logs.mkdir(exist_ok=True)
    log = logs / f"{name}-{datetime.now():%Y%m%d-%H%M%S}.log"
    print(f"{len(jobs)} jobs · log {log}")
    cmd = ["flow", "batch", str(run_file), "--concurrency", c["CONCURRENCY"], "--rpm", c["RPM"], "--continue-on-error"]
    if dry:
        cmd.append("--dry-run")
    with open(log, "w") as fh:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            line = f"[{datetime.now():%H:%M:%S}] {line.rstrip()}"
            print(line, flush=True)
            fh.write(line + "\n")
        proc.wait()
    return proc.returncode


def report(paths):
    print("\nOn disk:")
    for p in paths:
        print(("  ok      " if Path(p).is_file() else "  MISSING ") + str(Path(p).relative_to(VIDEO)))


# ---------- all/ folders ----------

def sync(quiet=False):
    for kind, k in KINDS.items():
        root = VIDEO / k["folder"]
        if not manifest_path(kind).is_file():
            continue
        name = re.compile(rf"^{k['stem']}-(\d+[a-z]?)-v(\d+)(-1080p)?\{k['ext']}$")
        wanted = {shot(j) for j in load_jobs(kind)}
        all_dir = root / "all"
        all_dir.mkdir(exist_ok=True)
        latest = {}
        paths = [p for pattern in ("*/", "*/*/") for p in root.glob(f"{k['stem']}-{pattern}*")]  # scene-3/ and scene-1/scene-1a/
        paths += [p for pattern in ("*/", "*/*/") for p in root.glob(f"{k['stem']}-{pattern}final/*-1080p.mp4")]
        for p in paths:
            m = name.match(p.name)
            if not m or m[1] not in wanted:
                continue
            v = int(m[2])
            if m[1] not in latest or v > latest[m[1]][0]:
                latest[m[1]] = (v, [p])
            elif v == latest[m[1]][0]:
                latest[m[1]][1].append(p)
        keep = set()
        for _, files in latest.values():
            finals = [p for p in files if p.name.endswith("-1080p.mp4")]
            for p in finals or files:  # once a final exists, all/ holds only the final
                dest = all_dir / p.name
                keep.add(dest.name)
                if not dest.exists() or dest.stat().st_size != p.stat().st_size:
                    shutil.copy2(p, dest)
                    quiet or print(f"added   {k['folder']}/all/{dest.name}")
        for old in all_dir.iterdir():
            if name.match(old.name) and old.name not in keep:
                old.unlink()
                quiet or print(f"removed {k['folder']}/all/{old.name}")
        quiet or print(f"{k['folder']}/all: {len(latest)} shots")


def newest_in_all(kind, s):
    k = KINDS[kind]
    pat = re.compile(rf"^{k['stem']}-{s}-v(\d+)(-1080p)?\{k['ext']}$")
    files = sorted((f for f in (VIDEO / k["folder"] / "all").glob(f"{k['stem']}-{s}-v*") if pat.match(f.name)),
                   key=lambda f: int(pat.match(f.name)[1]))
    finals = [f for f in files if f.name.endswith("-1080p.mp4")]
    return (finals or files or [None])[-1]


# ---------- commands ----------

def cmd_generate(kind, args):
    jobs = select(load_jobs(kind), args.shots)
    if not jobs:
        die(f"{manifest_path(kind).relative_to(VIDEO)} has no jobs")
    run = expand(jobs)
    ready, waiting = split_ready(run)
    check_inputs(ready)
    if ready:
        run_batch(ready, kind, args.dry_run)
        args.dry_run or report([j["output"] for j in ready])
    else:
        print("nothing to generate: every output exists or waits on another shot")
    for s, deps in waiting.items():
        print(f"{s} waits for {', '.join(deps)}: make (and pick) that first, then rerun")
    pending = [shot(j) for j in jobs if not Path(j["output"]).is_file() and any(p.is_file() for p in variant_paths(Path(j["output"])))]
    if pending:
        print(f"\nVariants waiting for a pick: {', '.join(pending)}  (make.py review {kind}, then make.py pick SHOT TAKE)")
    sync()


def cmd_finals(args):
    finals = []
    jobs = select(load_jobs("clips"), args.shots)
    if not jobs:
        die("clips/clips-batch.json has no jobs")
    no_draft = [j["id"] for j in jobs if not Path(j["output"]).is_file()]
    if no_draft and not args.no_draft:
        die(f"no approved draft for {', '.join(no_draft)}: make or pick it, name only the shots that have one, or pass --no-draft")
    for j in jobs:
        draft = Path(j["output"])
        finals.append({
            "id": j["id"] + "-final", "kind": "video", "prompt_file": j["prompt_file"],
            "aspect": j.get("aspect", "9:16"), "duration": j.get("duration", 4),
            "resolution": "720p", "upsample": "1080p", "ingredient": j["ingredient"],
            "timeout": 1500,  # upsample jobs only go to paid accounts; flow picks one
            "output": str(draft.parent / "final" / draft.name),
            **({"seed": j["seed"]} if "seed" in j else {}),
        })
    hd = [Path(f["output"]).with_name(Path(f["output"]).stem + "-1080p.mp4") for f in finals]
    finals = [f for f, h in zip(finals, hd) if not (Path(f["output"]).is_file() and h.is_file())]
    check_inputs(finals)
    print(f"{len(finals)} finals to make, {len(hd) - len(finals)} already there")
    finals and run_batch(finals, "finals", args.dry_run)
    args.dry_run or report(hd)
    sync()
    if args.into and not args.dry_run:
        dest = VIDEO / "clips" / args.into
        dest.mkdir(parents=True, exist_ok=True)
        for p in hd:
            if p.is_file():
                shutil.copy2(p, dest / p.name)
                print(f"copied  {p.name} -> clips/{args.into}/")
    print("\nFinals are new generations: run `make.py review finals` and compare them with the drafts.")


def cmd_pick(args):
    kind = "clips" if args.clip else "stills"
    jobs = [j for j in load_jobs(kind) if shot(j) == args.shot.lower()]
    if not jobs:
        die(f"no {kind} job for {args.shot}")
    out = Path(jobs[-1]["output"])
    src = variant_paths(out)[args.take - 1]
    if not src.is_file():
        die(f"no take {src.relative_to(VIDEO)}")
    shutil.copy2(src, out)
    print(f"{src.name} -> {out.name}")
    sync()


def ffprobe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def frame(video, t, dest):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(dest)],
                   check=True)
    return dest


def montage(tiles, cols, size, dest):
    """tiles: [(label, path)]; one labelled contact sheet."""
    cmd = ["magick", "montage", "-background", "#111114", "-fill", "#f4f4f5", "-pointsize", "22"]
    if FONT:
        cmd += ["-font", FONT]
    for label, path in tiles:
        cmd += ["-label", label, str(path)]
    cmd += ["-tile", f"{cols}x", "-geometry", f"{size}+10+10", str(dest)]
    subprocess.run(cmd, check=True)
    return dest


def cmd_review(args):
    kind = args.kind
    base = "clips" if kind == "finals" else kind
    jobs = select(load_jobs(base), args.shots)
    if not jobs:
        die("nothing to review")
    out_dir = VIDEO / "review"
    out_dir.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".frames-", dir=out_dir))
    try:
        sheets, missing = review_sheets(kind, jobs, out_dir, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for p in sheets:
        print(p)
    if missing:
        print("not generated yet: " + ", ".join(missing))


def review_sheets(kind, jobs, out_dir, tmp):
    stamp = f"{datetime.now():%Y%m%d-%H%M%S}"
    rows, missing = [], []  # each row: list of (label, path)
    for j in jobs:
        s, v = shot(j), version(j)
        out = Path(j["output"])
        if kind == "finals":
            hd = out.parent / "final" / f"{out.stem}-1080p.mp4"
            if not hd.is_file():
                missing.append(f"{s} v{v} final")
                continue
            row = []
            if out.is_file():
                row.append((f"{s} v{v} draft", frame(out, ffprobe_duration(out) / 2, tmp / f"{s}-d.jpg")))
            d = ffprobe_duration(hd)
            for name, t in (("start", 0.3), ("mid", d / 2), ("end", d - 0.3)):
                row.append((f"{s} final {name}", frame(hd, t, tmp / f"{s}-f-{name}.jpg")))
            rows.append(row)
            continue
        candidates = [(f"{s} v{v}", out)] if out.is_file() else [
            (f"{s} v{v} take {take_no(p)}", p) for p in variant_paths(out) if p.is_file()]
        if not candidates:
            missing.append(f"{s} v{v}")
        for label, path in candidates:
            if kind == "stills":
                rows.append([(label, path)])
            else:
                d = ffprobe_duration(path)
                n = label.replace(" ", "-")
                rows.append([(f"{label} {name}", frame(path, t, tmp / f"{n}-{name}.jpg"))
                             for name, t in (("start", 0.3), ("mid", d / 2), ("end", max(d - 0.3, 0)))])
    sheets = []
    if kind == "stills":
        tiles = [t for row in rows for t in row]
        for i in range(0, len(tiles), 10):
            sheets.append(montage(tiles[i:i + 10], 5, "300x533", out_dir / f"stills-{stamp}-{i // 10 + 1}.jpg"))
    else:
        cols = 4 if kind == "finals" else 3
        for i in range(0, len(rows), 4):
            tiles = []
            for row in rows[i:i + 4]:
                if kind == "finals" and len(row) == 3:  # no draft on disk: pad so columns line up
                    blank = tmp / "blank.jpg"
                    if not blank.is_file():
                        subprocess.run(["magick", "-size", "240x427", "xc:#111114", str(blank)], check=True)
                    row = [("no draft", blank)] + row
                tiles += row
            sheets.append(montage(tiles, cols, "240x427", out_dir / f"{kind}-{stamp}-{i // 4 + 1}.jpg"))
    return sheets, missing


def real_voiceover():
    vo = VIDEO / "voiceover"
    return next((p for ext in ("wav", "mp3", "m4a", "aac") for p in [vo / f"recording.{ext}"] if p.is_file()), None)


def encode_segment(src, seconds, label, dest, still):
    vf = "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p"
    if FONT:
        vf += f",drawtext=fontfile='{FONT}':text='{label}':x=16:y=16:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=8"
    inp = ["-loop", "1", "-t", f"{seconds}", "-i", str(src)] if still else ["-i", str(src)]
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inp, "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", str(dest)],
                   check=True)


def shot_list_lengths():
    """{shot: seconds} from the Clip column of PLAN.md rows like | 1a | ... | 6 s | (SHOT-LIST.md in older videos)."""
    p = next((f for f in (VIDEO / "PLAN.md", VIDEO / "SHOT-LIST.md") if f.is_file()), VIDEO / "PLAN.md")
    rows = [l.strip().strip("|").split("|") for l in p.read_text().splitlines() if l.lstrip().startswith("|")] if p.is_file() else []
    return {r[0].strip().lower(): float(m[1]) for r in rows
            if len(r) > 1 and (m := re.match(r"^\s*(\d+(?:\.\d+)?)\s*s", r[-1]))}


def cmd_animatic(args):
    clip_len = {**shot_list_lengths(), **{shot(j): j["duration"] for j in load_jobs("clips") if "duration" in j}}
    edit = VIDEO / "edit"
    edit.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".animatic-", dir=edit))
    try:
        animatic(clip_len, edit, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def animatic(clip_len, edit, tmp):
    segs, total, lines = [], 0.0, []
    for s in story_order():
        clip, still = newest_in_all("clips", s), newest_in_all("stills", s)
        if clip:
            dur = ffprobe_duration(clip)
            src, is_still, what = clip, False, clip.name
        elif still:
            dur = float(clip_len.get(s, 4))
            src, is_still, what = still, True, still.name
        else:
            lines.append(f"  {s:>4}  (nothing yet, skipped)")
            continue
        seg = tmp / f"{len(segs):03d}.mp4"
        encode_segment(src, dur, s, seg, is_still)
        segs.append(seg)
        lines.append(f"  {s:>4}  {total:6.1f}s  {dur:4.1f}s  {what}")
        total += dur
    if not segs:
        die("no stills or clips yet")
    (tmp / "list.txt").write_text("".join(f"file '{p}'\n" for p in segs))
    vo = real_voiceover() or next((p for p in [VIDEO / "voiceover" / "scratch.wav"] if p.is_file()), None)
    dest = edit / "animatic.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt")]
    cmd += ["-i", str(vo), "-map", "0:v", "-map", "1:a", "-c:a", "aac"] if vo else []
    subprocess.run(cmd + ["-c:v", "copy", str(dest)], check=True)
    print("\n".join(lines))
    print(f"\n{dest}\npicture {total:.1f}s" + (f" · voiceover {ffprobe_duration(vo):.1f}s ({vo.name})" if vo else " · no voiceover/recording.* yet"))


def cmd_handoff(args):
    dest = VIDEO / "edit" / "clips"
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("[0-9][0-9]-*.mp4"):
        old.unlink()
    lines = []
    for s in story_order():
        clip = newest_in_all("clips", s)
        if not clip:
            lines.append(f"--  {s}: no clip")
            continue
        n = len([l for l in lines if not l.startswith("--")]) + 1
        name = f"{n:02d}-{clip.name}"
        shutil.copy2(clip, dest / name)
        lines.append(f"{name}  {ffprobe_duration(clip):.1f}s" + ("" if clip.name.endswith("-1080p.mp4") else "  (draft, no 1080p yet)"))
    if not any(dest.glob("[0-9][0-9]-*.mp4")):
        die("no clips yet")
    (dest / "ORDER.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n{dest}")


def cmd_status(args):
    sync(quiet=True)
    stills = {shot(j): j for j in load_jobs("stills")}
    clips = {shot(j): j for j in load_jobs("clips")}
    plan, pdf = VIDEO / "PLAN.md", VIDEO / "PLAN.pdf"
    if plan.is_file() and (not pdf.is_file() or pdf.stat().st_mtime < plan.stat().st_mtime):
        print("PLAN.pdf is older than PLAN.md: reprint it with the video-plan skill's plan.py pdf\n")
    if not story_order():
        die("no jobs yet: add them to scenes/stills-batch.json")
    print(f"{'shot':>5}  {'still':<22}{'clip':<22}final")
    for s in story_order():
        cells = []
        for jobs in (stills, clips):
            j = jobs.get(s)
            if not j:
                cells.append("-")
                continue
            out = Path(j["output"])
            if out.is_file():
                cells.append(f"v{version(j)}")
            elif any(p.is_file() for p in variant_paths(out)):
                cells.append(f"v{version(j)} pick take {','.join(take_no(p) for p in variant_paths(out) if p.is_file())}")
            else:
                cells.append(f"v{version(j)} to make")
        j = clips.get(s)
        hd = j and Path(j["output"]).parent / "final" / f"{Path(j['output']).stem}-1080p.mp4"
        cells.append("1080p" if hd and hd.is_file() else "-")
        print(f"{s:>5}  {cells[0]:<22}{cells[1]:<22}{cells[2]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("stills", "clips"):
        p = sub.add_parser(name)
        p.add_argument("shots", nargs="*")
        p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("finals")
    p.add_argument("shots", nargs="*")
    p.add_argument("--into")
    p.add_argument("--no-draft", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("pick")
    p.add_argument("shot")
    p.add_argument("take", type=int, choices=range(1, MAX_TAKES + 1))
    p.add_argument("--clip", action="store_true")
    p = sub.add_parser("review")
    p.add_argument("kind", choices=["stills", "clips", "finals"])
    p.add_argument("shots", nargs="*")
    for name in ("animatic", "handoff", "sync", "status"):
        sub.add_parser(name)
    args = ap.parse_args()
    {
        "stills": lambda: cmd_generate("stills", args),
        "clips": lambda: cmd_generate("clips", args),
        "finals": lambda: cmd_finals(args),
        "pick": lambda: cmd_pick(args),
        "review": lambda: cmd_review(args),
        "animatic": lambda: cmd_animatic(args),
        "handoff": lambda: cmd_handoff(args),
        "sync": lambda: sync(),
        "status": lambda: cmd_status(args),
    }[args.cmd]()


if __name__ == "__main__":
    main()
