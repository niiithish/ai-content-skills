#!/usr/bin/env python3
"""Keeps B-roll and box inserts in step with the captions: a new picture may only appear on the frame a new caption
starts or V1 cuts, never mid-caption. A client called inserts that changed mid-caption "very rookie mistakes" and
"super messy" (Aleo video-3, 2026-10-24).

Inserts are every clip on the video tracks between V1 (the talking head or main video) and the top track (captions).

  split PROJECT [--dry]   split a caption block (captions/<stem>.blocks.txt) wherever an insert starts or ends
                          mid-caption, at the word nearest the change; prefers a comma, full stop or the line break
                          and never ends a half on "the", "your", "of". Then run `fc_captions.py plan` and `build`.
  snap PROJECT [--dry]    move every insert edge onto the nearest caption start or V1 cut (two pictures never share
                          one; a clip never plays past its media). Trims and moves only, so motion keyframes stay.
  check PROJECT [--render]  frame by frame, what the viewer sees (top insert, else the main video) may only change
                          on a caption start or cut, never for under 8 frames, with no caption 1-2 frames off a
                          change. --render also renders the frames around every change and checks the picture
                          switches on that exact frame. Exit 1 on any problem. It also warns (no exit 1) where
                          the speaker shows under 18 frames between pictures or at the end (FLASH), and at a jump
                          cut on the speaker with no zoom change (JUMP): look at each one's frame.

Order after any caption or insert change: split -> fc_captions.py plan -> build -> snap -> check --render."""
import argparse, bisect, datetime, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fc_captions as fcc

MIN = 8                         # shortest a picture may show, frames
FLASH = 18                      # shortest a stretch of the speaker (V1, uncovered) should show between other pictures
NEAR, REACH, MINF = 11, 18, 10  # split: a change this close to a mark is left to snap; farthest split word; shortest half


def fc(proj, *a):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), *a],
                                     capture_output=True, text=True, check=True).stdout)


def run(proj, cmds):
    script = Path(proj).parent / ".fc-inserts.jsonl"
    script.write_text("".join(json.dumps(c) + "\n" for c in cmds + [{"id": "file.save", "params": {}}]))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(script)],
                         capture_output=True, text=True)
    script.unlink()
    bad = [r for r in (json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")) if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"FilmCraft failed: {bad or out.stderr[-2000:]}")


def layout(proj):
    """(video tracks, insert track indices, ticks per frame, fps)"""
    v = fc(proj, "inspect", "sequence")["video"]
    # the caption track is the top one with text on it: an empty track or an image overlay (an emoji) above it is not
    while len(v) > 1 and not any(e["effect"] == "graphic_text" for c in v[-1]["items"] for e in c["effects"]):
        v = v[:-1]
    if len(v) < 3:
        sys.exit("need V1, at least one insert track and a caption track on top")
    fpt = v[0]["items"][0]["duration"] // v[0]["items"][0]["durationFrames"]
    return v, range(1, len(v) - 1), fpt, 254016000000 / fpt


def v1_cuts(v):
    """V1 cuts the viewer sees: a join where the same media runs on (a razor around a sped-up pause) is not one."""
    v1 = sorted(v[0]["items"], key=lambda c: c["startFrame"])
    half = v1[0]["duration"] // max(1, v1[0]["durationFrames"]) // 2
    return {b["startFrame"] for a, b in zip(v1, v1[1:]) if b["item"] != a["item"] or abs(b["sourceIn"] - a["sourceOut"]) > half
            or fcc.zoom_of(a) != fcc.zoom_of(b)}   # a zoom change at a razor is a baked-in jump cut


def marks_of(v):
    return sorted(v1_cuts(v) | {c["startFrame"] for c in v[-1]["items"]}
                  | {0, max(c["endFrame"] for c in v[0]["items"])})


# ---------- split ----------

def cmd_split(a):
    P = fcc.paths(a.project)
    cap = json.loads(P["captions.json"].read_text())
    blocks = [l.strip() for l in P["blocks.txt"].read_text().splitlines() if l.strip()]
    if len(blocks) != len(cap["blocks"]):
        sys.exit("blocks.txt changed since the last plan: run fc_captions.py plan first")
    fps = cap["fps"]
    v, tracks, _, _ = layout(a.project)
    marks = sorted(set(cap["cuts"]) | {b["start"] for b in cap["blocks"]})
    changes = sorted({c[k] for t in tracks for c in v[t]["items"] for k in ("startFrame", "endFrame")})
    pk = fcc.asr_tokens(json.load(open(P["pk.json"])), {})
    toks, where = [], []
    for bi, b in enumerate(blocks):
        for wi, w in enumerate(b.replace(" / ", " ").split()):
            if fcc.norm(w):
                toks.append((fcc.norm(w), 0)); where.append((bi, wi))
    wf = {k: round((pk[ai][1] + cap["lead"]) * fps) for k, ai in zip(where, fcc.align(toks, pk)) if ai is not None}
    cuts = {}
    for ch in changes:
        if min(abs(ch - x) for x in marks) <= NEAR:
            continue
        bi = next((i for i, b in enumerate(cap["blocks"]) if b["start"] <= ch < b["end"]), None)
        if bi is None:
            continue   # no caption up (a pause): snap moves it
        b = cap["blocks"][bi]
        words = b["text"].replace(" / ", " ").split()
        brk = len(b["text"].split(" / ")[0].split()) if " / " in b["text"] else None

        def cost(wi, f):
            prev = words[wi - 1]
            return abs(f - ch) - (8 if prev[-1] in ",.:;?!" or wi == brk else 0) + (8 if fcc.norm(prev) in fcc.WEAK_END else 0)
        cand = [(cost(wi, f), wi) for (i, wi), f in wf.items() if i == bi and wi > 0
                and f - b["start"] >= MINF and b["end"] - f >= MINF and abs(f - ch) <= REACH]
        if cand:
            cuts.setdefault(bi, set()).add(min(cand)[1])
        else:
            print(f"  no split for the change at {ch / fps:.2f}s in {b['text']!r}: snap moves the picture instead")
    out = []
    for bi, b in enumerate(blocks):
        w = b.replace(" / ", " ").split()
        keep = []
        for k in sorted(cuts.get(bi, ())):
            if not keep or wf.get((bi, k), 0) - wf.get((bi, keep[-1]), 0) >= MINF:
                keep.append(k)
        if not keep:
            out.append(b); continue
        parts = [" ".join(w[x:y]) for x, y in zip([0] + keep, keep + [len(w)])]
        print(f"  {b!r} -> {parts}")
        out += parts
    print(f"{len(blocks)} captions -> {len(out)}" + ("" if a.dry else ": now run fc_captions.py plan and build, then snap"))
    if not a.dry and len(out) != len(blocks):
        bk = P["blocks.txt"].with_suffix(".pre-split.txt")
        if not bk.exists():
            bk.write_text(P["blocks.txt"].read_text())
        P["blocks.txt"].write_text("\n".join(out) + "\n")


# ---------- snap ----------

def cmd_snap(a):
    proj = Path(a.project).resolve()
    v, tracks, fpt, fps = layout(proj)
    marks = marks_of(v)
    ins = [dict(c, track=t) for t in tracks for c in v[t]["items"]]
    media = {}

    def walk(n):
        if isinstance(n, dict):
            if "item" in n and "duration" in n:
                media[n["item"]] = (n["duration"] // fpt, n.get("type"))
            for x in n.values():
                walk(x)
        elif isinstance(n, list):
            for x in n:
                walk(x)
    walk(fc(proj, "inspect", "project")["root"])
    for c in ins:   # frames a movie can play from its start; a still can stretch
        n, kind = media.get(c["item"], (None, None))
        c["room"] = int((n - c["sourceIn"] // fpt) / (c.get("speed") or 1.0)) if kind == "Movie" and n else None   # a slowed clip plays longer

    def at_or_before(f):
        return marks[bisect.bisect_right(marks, f) - 1]
    prev = None   # in story order across tracks: two pictures never share a mark, the later takes the next one
    for c in sorted(ins, key=lambda c: c["startFrame"]):
        c["S"] = min(marks, key=lambda m: (abs(m - c["startFrame"]), m > c["startFrame"]))
        if prev is not None and c["S"] <= prev:
            c["S"] = marks[bisect.bisect_right(marks, prev)]
        prev = c["S"]
    starts = {}
    for c in ins:
        starts.setdefault(c["startFrame"], []).append(c)

    def end_mark(c):
        nxt = starts.get(c["endFrame"])
        return nxt[0]["S"] if nxt else min(marks, key=lambda m: (abs(m - c["endFrame"]), m > c["endFrame"]))
    for c in ins:   # a movie 1-2 frames short of its end mark starts that much later instead
        if c["room"] and 0 < end_mark(c) - (c["S"] + c["room"]) <= 2:
            c["S"] = end_mark(c) - c["room"]
    for c in ins:
        c["E"] = end_mark(c)
        if c["room"] and c["E"] > c["S"] + c["room"]:   # else it ends on the last mark it reaches
            c["E"] = at_or_before(c["S"] + c["room"])
    short = []
    for t in tracks:
        row = sorted((c for c in ins if c["track"] == t), key=lambda c: c["startFrame"])
        for x, y in zip(row, row[1:]):
            x["E"] = min(x["E"], y["S"])
        short += [c for c in row if c["E"] - c["S"] < MIN]
    moved = [c for c in ins if (c["S"], c["E"]) != (c["startFrame"], c["endFrame"])]
    for c in sorted(moved, key=lambda c: c["startFrame"]):
        print(f"  V{c['track'] + 1} {c['name'][:30]:30} {c['startFrame'] / fps:7.2f}-{c['endFrame'] / fps:7.2f}s -> "
              f"{c['S'] / fps:7.2f}-{c['E'] / fps:7.2f}s  ({c['S'] - c['startFrame']:+d}f, {c['E'] - c['endFrame']:+d}f)")
    for c in short:
        print(f"  SHORT V{c['track'] + 1} {c['name']} {c['S'] / fps:.2f}-{c['E'] / fps:.2f}s: split a caption there "
              f"(split), or drop the insert")
    print(f"{len(moved)} of {len(ins)} inserts move, {len(short)} too short")
    if a.dry or short:
        sys.exit(1 if short else 0)
    bk = proj.parent / f"backup-{datetime.date.today()}-snap"
    bk.mkdir(exist_ok=True)
    if not (bk / proj.name).exists():
        shutil.copy2(proj, bk / proj.name)
    # 1: shrink every clip to the overlap of its old and new range, so no clip ever overwrites another
    cmds = []
    for c in moved:
        if c["S"] > c["startFrame"]:
            cmds.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "in", "mode": "regular",
                                                           "deltaFrames": c["S"] - c["startFrame"]}})
        if c["E"] < c["endFrame"]:
            cmds.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular",
                                                           "deltaFrames": c["E"] - c["endFrame"]}})
    run(proj, cmds)
    # 2: move the clips that start earlier, then grow each end to its mark
    cur = {x["clip"]: x for t in tracks for x in fc(proj, "inspect", "sequence")["video"][t]["items"]}
    cmds = []
    for c in moved:
        s, e = cur[c["clip"]]["startFrame"], cur[c["clip"]]["endFrame"]
        if c["S"] < s:
            cmds.append({"id": "timeline.move", "params": {"moves": [{"clip": c["clip"], "track": f"V{c['track'] + 1}",
                                                                      "time": c["S"] * fpt}], "insert": False}})
            e -= s - c["S"]
        if c["E"] != e:
            cmds.append({"id": "timeline.trim", "params": {"clip": c["clip"], "edge": "out", "mode": "regular",
                                                           "deltaFrames": c["E"] - e}})
    run(proj, cmds)
    v = fc(proj, "inspect", "sequence")["video"]
    got = {x["clip"]: (x["startFrame"], x["endFrame"]) for t in tracks for x in v[t]["items"]}
    wrong = [c["name"] for c in ins if got.get(c["clip"]) != (c["S"], c["E"])]
    sys.exit(f"NOT on their marks: {wrong}" if wrong else 0)


# ---------- check ----------

def cmd_check(a):
    v, tracks, _, fps = layout(a.project)
    end = max(c["endFrame"] for c in v[0]["items"])
    caps = {c["startFrame"] for c in v[-1]["items"]}
    marks = set(marks_of(v))
    seq = ["main"] * end
    for t in tracks:   # higher tracks cover lower ones
        for c in v[t]["items"]:
            for f in range(c["startFrame"], min(c["endFrame"], end)):
                seq[f] = (t, c["clip"])
    changes = [f for f in range(1, end) if seq[f] != seq[f - 1]]
    bad = [f for f in changes if f not in marks]
    runs = list(zip([0] + changes, changes + [end]))
    short = [(x, y) for x, y in runs if y - x < MIN]
    near = sorted(c for c in caps if c not in changes and any(0 < abs(c - x) <= 2 for x in changes))
    for f in bad:
        print(f"  OFF    {f / fps:7.2f}s  the picture changes mid-caption")
    for x, y in short:
        print(f"  SHORT  {x / fps:7.2f}s  a picture shows only {y - x} frames")
    for c in near:
        print(f"  NEAR   {c / fps:7.2f}s  a caption starts 1-2 frames from a picture change")
    warns = speaker_warnings(a.project, v, seq, end, fps)
    for w in warns:
        print("  " + w)
    late = []
    if a.render:
        import numpy as np
        from PIL import Image
        from concurrent.futures import ThreadPoolExecutor
        d = Path(tempfile.mkdtemp(prefix="fc-inserts-"))

        def render(f):
            subprocess.run(["filmcraft-cli", "--project", a.project, "render", "--seconds", str((f + 0.5) / fps),
                            "--out", str(d / f"{f}.png"), "--scale", "0.25"], capture_output=True)
        with ThreadPoolExecutor(6) as ex:
            list(ex.map(render, sorted({x for f in changes for x in (f - 2, f - 1, f)})))

        def diff(x, y):
            return np.abs(np.asarray(Image.open(d / f"{x}.png").convert("L"), float)
                          - np.asarray(Image.open(d / f"{y}.png").convert("L"), float)).mean()
        for f in changes:   # the picture must switch between f-1 and f, not a frame early
            at, before = diff(f - 1, f), diff(f - 2, f - 1)
            if at < 8 or before > at / 2:
                late.append(f); print(f"  RENDER {f / fps:7.2f}s  the frame doesn't switch here (change {at:.1f}, frame before {before:.1f})")
        shutil.rmtree(d)
    print(f"{a.project}: {len(changes)} picture changes, {len(bad)} mid-caption, {len(short)} under {MIN} frames, "
          f"{len(near)} near misses, {len(warns)} speaker warnings (look at each)"
          + (f", {len(late)} not switching in the render" if a.render else ""))
    sys.exit(1 if bad or short or near or late else 0)


def scale_at(clip, t):
    """Motion scale of an fcproj clip at source time t (ticks), from its keyframes (linear) or its static value."""
    m = next((e for e in clip.get("effects", []) if e.get("effect") == "motion"), None)
    sc = m and m["params"].get("scale")
    if not sc:
        return 100.0
    kf = sorted(sc.get("keyframes") or [], key=lambda k: k["time"])
    if not kf:
        return float(sc["value"]["Float"])
    if t <= kf[0]["time"]:
        return kf[0]["value"]["Float"]
    for k0, k1 in zip(kf, kf[1:]):
        if t <= k1["time"]:
            f = (t - k0["time"]) / max(1, k1["time"] - k0["time"])
            return k0["value"]["Float"] + f * (k1["value"]["Float"] - k0["value"]["Float"])
    return kf[-1]["value"]["Float"]


def speaker_warnings(proj, v, seq, end, fps):
    """What the user caught by eye on video-23 (2026-11-09, "weird cut… hard cut zoom in short time just after that
    b roll end"): the speaker showing for under FLASH frames between other pictures or at the end, and a jump cut
    on the speaker with no zoom change. Warnings: some are meant, so look at each one's frame."""
    out = []
    v1 = sorted(v[0]["items"], key=lambda c: c["startFrame"])
    cuts = {b["startFrame"] for a, b in zip(v1, v1[1:])}
    edges = sorted(cuts | {0, end})
    # visible stretches of V1: uncovered frames, split at V1 cuts
    f = 0
    while f < end:
        if seq[f] != "main":
            f += 1
            continue
        g = f + 1
        while g < end and seq[g] == "main" and g not in cuts:
            g += 1
        covered_before = f > 0 and seq[f - 1] != "main"
        covered_after = g < end and seq[g] != "main"
        if g - f < FLASH and (covered_before or covered_after or g == end) and f > 0:
            where = "at the end" if g == end else ("between two pictures" if covered_before and covered_after
                                                   else "next to a picture and a cut")
            out.append(f"FLASH  {f / fps:7.2f}s  the speaker shows only {g - f} frames {where}")
        f = g
    try:
        d = json.load(open(proj))
        seqj = next(i for i in d["project"]["items"].values() if "Sequence" in i["kind"])["kind"]["Sequence"]
        byid = {c["id"]: c for c in seqj["video_tracks"][0]["items"]}
    except Exception:
        return out
    tpf = v1[0]["duration"] // max(1, v1[0]["durationFrames"]) if v1 else 1
    for a, b in zip(v1, v1[1:]):
        x = b["startFrame"]
        if x >= end or seq[x] != "main" or b["item"] != a["item"] or abs(b["sourceIn"] - a["sourceOut"]) <= tpf // 2:
            continue   # covered, another clip, or a razor where the media runs on
        ca, cb = byid.get(a["clip"]), byid.get(b["clip"])
        if not ca or not cb:
            continue
        za = scale_at(ca, ca["source_in"] + ca["duration"] * ca.get("speed", 1.0))
        zb = scale_at(cb, cb["source_in"])
        if abs(zb - za) < 0.03 * za:
            out.append(f"JUMP   {x / fps:7.2f}s  a jump cut on the speaker with no zoom change ({za:.0f}% -> {zb:.0f}%)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("split", cmd_split), ("snap", cmd_snap), ("check", cmd_check)):
        p = sub.add_parser(name)
        p.add_argument("project")
        p.add_argument("--dry" if name != "check" else "--render", action="store_true")
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)
