#!/usr/bin/env python3
"""Build (and optionally render) a whole Resolve edit in ONE command through claude_bridge.

Why: the MCP does one tool call per step, and its append looks every clip up by scanning the
media pool one bridge call at a time (~2,000 round trips for 64 clips). This script imports
once, appends every piece in one AppendToTimeline call, and polls the render locally.

Usage:
  build.py spec.json [--render] [--replace] [--dry-run]

spec.json (times in seconds on the timeline; source in/out in seconds, default the whole clip):
{
  "project": "video-8",                 # optional: load or create; default the open project
  "timeline": "Hook 1",
  "width": 1080, "height": 1920, "fps": 24,
  "video": [{"file": "/abs/clip-1.mov", "at": 0.0, "in": 0.0, "dur": 5.0}, ...],   # track 1 unless "track"
  "audio": [{"file": "/abs/recording.wav", "at": 0, "track": 1},
            {"file": "/abs/song.mp3", "at": 0, "track": 2, "dur": "timeline"}],
  "render": {"dir": "/abs/video-8/deliverables/raw", "name": "video-8-hook-1"}   # used with --render
}
Prints one timing line per phase and a mismatch table if Resolve placed anything off by a frame.
"""
import json
import math
import os
import subprocess
import sys
import time

for p in (os.path.expanduser("~/.local/share/davinci-resolve-mcp/lua_bridge/Modules"),
          os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bridge")):
    if os.path.isfile(os.path.join(p, "resolve_lua_bridge.py")):
        sys.path.insert(0, p)
        break

T0 = time.monotonic()


def log(msg):
    print(f"[{time.monotonic() - T0:6.1f}s] {msg}", flush=True)


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        die(f"ffprobe can't read {path}")


def video_fps(path):
    """Source frame rate (Resolve takes trim points in the clip's own frames), None if no video."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    try:
        n, d = out.split("/")
        return float(n) / float(d)
    except ValueError:
        return None


def plan_pieces(spec):
    """Spec -> pieces with frame numbers (timeline-relative record frame, source in/out)."""
    fps = float(spec.get("fps", 24))
    f = lambda s: int(round(float(s) * fps))
    pieces = []
    for kind, mtype in (("video", 1), ("audio", 2)):
        for e in spec.get(kind, []):
            path = os.path.abspath(e["file"])
            if not os.path.isfile(path):
                die(f"missing file: {path}")
            sfps = (video_fps(path) if kind == "video" else None) or fps
            src_len = int(duration(path) * fps)  # in timeline frames
            sin = f(e.get("in", 0))
            pieces.append({"kind": kind, "mediaType": mtype, "file": path, "track": int(e.get("track", 1)),
                           "rec": f(e.get("at", 0)), "at": float(e.get("at", 0)), "in": sin, "dur": e.get("dur"),
                           "src_len": src_len, "sfps": sfps})
    # length = rounded end - rounded start, so neighbours meet exactly (rounding each separately can overlap by a frame)
    slot = lambda p: f(p["at"] + float(p["dur"])) - p["rec"]
    vid_end = max((p["rec"] + (slot(p) if p["dur"] not in (None, "timeline") else p["src_len"] - p["in"])
                   for p in pieces if p["kind"] == "video"), default=0)
    warn = []
    for p in pieces:
        if p["dur"] == "timeline":
            n = vid_end - p["rec"]
        elif p["dur"] is None:
            n = p["src_len"] - p["in"]
        else:
            n = slot(p)
        avail = p["src_len"] - p["in"]
        if n > avail:
            warn.append(f"{os.path.basename(p['file'])}: slot {n}f but only {avail}f of source; using {avail}f")
            n = avail
        p["len"] = max(n, 1)
    return pieces, warn


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        die(__doc__)
    spec = json.load(open(args[0]))
    render, replace, dry = "--render" in args, "--replace" in args, "--dry-run" in args
    pieces, warn = plan_pieces(spec)
    for w in warn:
        log("warning: " + w)
    log(f"planned {len(pieces)} pieces")
    if dry:
        for p in pieces:
            print(f"  {p['kind']:5} T{p['track']} rec {p['rec']:6d} in {p['in']:5d} len {p['len']:5d}  {os.path.basename(p['file'])}")
        return

    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        die("bridge not running: in Resolve click Workspace > Scripts > claude_bridge")
    pm = resolve.GetProjectManager()
    if spec.get("project"):
        proj = pm.LoadProject(spec["project"]) or pm.CreateProject(spec["project"])
    else:
        proj = pm.GetCurrentProject()
    if not proj:
        die("no project open")
    log(f"project {proj.GetName()}")

    # timeline with this name already there?
    old = None
    for i in range(1, int(proj.GetTimelineCount() or 0) + 1):
        tl = proj.GetTimelineByIndex(i)
        if tl and tl.GetName() == spec["timeline"]:
            old = tl
    mp = proj.GetMediaPool()
    if old:
        if not replace:
            die(f'timeline "{spec["timeline"]}" exists; pass --replace to rebuild it')
        mp.DeleteTimelines([old])
        log("deleted old timeline")
    for k, v in (("timelineFrameRate", spec.get("fps", 24)), ("timelineResolutionWidth", spec.get("width", 1080)),
                 ("timelineResolutionHeight", spec.get("height", 1920))):
        if str(proj.GetSetting(k)) != str(v) and not proj.SetSetting(k, str(v)):
            log(f"warning: could not set {k}={v} (frame rate is locked once a timeline exists)")

    # media: reuse what is already in the pool, import the rest in one call
    have = {}
    stack = [mp.GetRootFolder()]
    while stack:
        folder = stack.pop()
        for c in folder.GetClipList() or []:
            have[c.GetClipProperty("File Path")] = c
        stack.extend(folder.GetSubFolderList() or [])
    need = sorted({p["file"] for p in pieces} - set(have))
    if need:
        for c in mp.ImportMedia(need) or []:
            have[c.GetClipProperty("File Path")] = c
    missing = [f for f in {p["file"] for p in pieces} if f not in have]
    if missing:
        die("Resolve did not import: " + ", ".join(missing[:5]))
    log(f"media ready ({len(need)} imported, {len(have)} in pool)")

    tl = mp.CreateEmptyTimeline(spec["timeline"])
    if not tl:
        die("could not create timeline")
    proj.SetCurrentTimeline(tl)
    for kind in ("video", "audio"):
        want = max((p["track"] for p in pieces if p["kind"] == kind), default=1)
        while int(tl.GetTrackCount(kind) or 0) < want:
            tl.AddTrack(kind, "stereo") if kind == "audio" else tl.AddTrack(kind)
    start = int(tl.GetStartFrame())
    # start/endFrame are source frames: scale timeline frames by the clip's own rate (30 fps clip on a 24 fps timeline)
    # (end rounded up, or a half-frame slot comes out one frame short)
    src = lambda p, n, up=False: int((math.ceil if up else math.floor)(n * p["sfps"] / float(spec.get("fps", 24)) + (-1e-6 if up else 1e-6)))
    infos = [{"mediaPoolItem": have[p["file"]], "startFrame": src(p, p["in"]), "endFrame": src(p, p["in"] + p["len"], True),
              "recordFrame": start + p["rec"], "trackIndex": p["track"], "mediaType": p["mediaType"]}
             for p in pieces]
    items = mp.AppendToTimeline(infos) or []
    log(f"appended {len(items)}/{len(infos)} pieces in one call")

    # check placement once (one pass, not per append)
    bad = []
    for kind in ("video", "audio"):
        for t in range(1, int(tl.GetTrackCount(kind) or 0) + 1):
            placed = sorted((int(i.GetStart()) - start, int(i.GetEnd()) - start) for i in tl.GetItemListInTrack(kind, t) or [])
            want = sorted((p["rec"], p["rec"] + p["len"]) for p in pieces if p["kind"] == kind and p["track"] == t)
            if placed != want:
                bad.append((kind, t, len(want), len(placed), [w for w in want if w not in placed][:3]))
    for b in bad:
        log(f"MISMATCH {b[0]} T{b[1]}: wanted {b[2]} items, got {b[3]}; e.g. missing {b[4]}")
    if not bad:
        log("timeline verified: every piece where planned")
    pm.SaveProject()
    log("saved")

    if not render:
        return
    r = spec.get("render") or die('--render needs "render": {"dir", "name"} in the spec')
    os.makedirs(r["dir"], exist_ok=True)
    codecs = proj.GetRenderCodecs("mov") or {}
    codec = next((v for k, v in codecs.items() if "422" in k and "LT" in k), None) or die(f"no ProRes LT in {codecs}")
    proj.SetCurrentRenderFormatAndCodec("mov", codec)
    proj.SetRenderSettings({"SelectAllFrames": True, "TargetDir": r["dir"], "CustomName": r["name"]})
    job = proj.AddRenderJob() or die("AddRenderJob failed")
    proj.StartRendering(job)
    log("rendering")
    last = -1
    while proj.IsRenderingInProgress():
        pct = int((proj.GetRenderJobStatus(job) or {}).get("CompletionPercentage", 0))
        if pct >= last + 10:
            log(f"  {pct}%")
            last = pct
        time.sleep(2)
    st = proj.GetRenderJobStatus(job) or {}
    out = os.path.join(r["dir"], r["name"] + ".mov")
    if st.get("JobStatus") != "Complete":
        die(f"render ended: {st}")
    log(f"rendered {out}")


if __name__ == "__main__":
    main()
