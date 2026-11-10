#!/usr/bin/env python3
"""video-23 (user 2026-11-10): replace a dead-air jump cut in a hook opening with the real pause played at 1.5x
plus a quick zoom (x1.08), so the speaker never jumps. At V1 cut C between talking pieces A and B (same source
clip), the source frames A skipped are put back as a new clip at speed gap/D (D = round(gap / 1.5) frames).
Everything from C on moves D frames later. The voice (A1) is split at C, leaving D frames of silence under the
music. The caption ending on C holds through, and clips across C (music, a split's listener, a caption) grow by D.
Usage: fill_jumpcuts.py hook-N.fcproj C [C ...]   (FilmCraft must not have that project open; cuts last to first)"""
import copy, json, sys, shutil, datetime
from pathlib import Path

T = 10584000000
P = Path(sys.argv[1]).resolve()
cuts = sorted((int(x) for x in sys.argv[2:]), reverse=True)  # last first: earlier frames stay put
bk = P.parent / f"backup-{datetime.date.today()}-fill-jumpcuts"
bk.mkdir(exist_ok=True)
shutil.copy2(P, bk / P.name)
d = json.load(open(P))
pr = d["project"]
s = next(i for i in pr["items"].values() if "Sequence" in i["kind"])["kind"]["Sequence"]


def new_id():
    pr["next_id"] += 1
    return pr["next_id"] - 1


def scale_kf(c):
    return next(e for e in c["effects"] if e["effect"] == "motion")["params"]["scale"]


def val_at(c, src):  # the clip's scale at a source frame
    sc = scale_kf(c)
    k = sc.get("keyframes") or []
    if not k:
        return sc["value"]["Float"]
    pts = [(x["time"] / T, x["value"]["Float"]) for x in k]
    if src <= pts[0][0]:
        return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if src <= t1:
            return v0 + (v1 - v0) * (src - t0) / (t1 - t0)
    return pts[-1][1]


def set_keys(c, a_src, va, b_src, vb):
    sc = scale_kf(c)
    tmpl = {"interp": "Linear", "out_influence": 1 / 3, "in_influence": 1 / 3}
    sc["keyframes"] = [dict(tmpl, time=round(a_src * T), value={"Float": round(va, 2)}),
                       dict(tmpl, time=round(b_src * T), value={"Float": round(vb, 2)})]


report = []
for C in cuts:
    v1 = s["video_tracks"][0]["items"]
    A = next(c for c in v1 if c["start"] + c["duration"] == C * T)
    B = next(c for c in v1 if c["start"] == C * T)
    assert A["item"] == B["item"] and A["speed"] == B["speed"] == 1.0, (A["name"], B["name"])
    a_end = A["source_in"] / T + C - A["start"] / T     # first source frame A skipped
    gap = B["source_in"] / T - a_end
    assert 0 < gap < 30, gap
    D = max(1, round(gap / 1.5))
    # shift / grow everything at or across C
    for tr in s["video_tracks"] + s["audio_tracks"]:
        for c in tr["items"]:
            st, en = c["start"], c["start"] + c["duration"]
            if st >= C * T:
                c["start"] += D * T
            elif en > C * T or (en == C * T and tr is s["video_tracks"][-1]):
                c["duration"] += D * T          # across C, or the caption that ends on C
        for t in tr.get("transitions") or []:
            if t["start"] >= C * T:
                t["start"] += D * T
    # music fade keys are in source time = timeline time (source_in 0)
    for c in s["audio_tracks"][-1]["items"]:
        for e in c["effects"]:
            for p in e["params"].values():
                for k in p.get("keyframes") or []:
                    if k["time"] >= C * T:
                        k["time"] += D * T
    # the voice: split at C, second half D later (it was grown above, so undo that first)
    vo = s["audio_tracks"][0]["items"]
    V = next((c for c in vo if c["start"] < C * T < c["start"] + c["duration"]), None)
    if V:
        V["duration"] -= D * T
        W = copy.deepcopy(V)
        W["id"] = new_id()
        cut_in = C * T - V["start"]
        W["start"], W["source_in"], W["duration"] = (C + D) * T, V["source_in"] + cut_in, V["duration"] - cut_in
        V["duration"] = cut_in
        vo.insert(vo.index(V) + 1, W)
    # the fill: A's skipped frames at speed gap/D, zooming x1.08; B carries on from there
    v0 = val_at(A, a_end - 1)
    F = copy.deepcopy(B)
    F["id"] = new_id()
    F["start"], F["duration"], F["source_in"], F["speed"] = C * T, D * T, round(a_end * T), gap / D
    b_src0 = B["source_in"] / T
    set_keys(F, a_end, v0, b_src0 - gap / D, v0 * 1.08)
    b_len = B["duration"] / T
    b_end_old = val_at(B, b_src0 + b_len - 1)
    b_start_old = val_at(B, b_src0)
    set_keys(B, b_src0, v0 * 1.08, b_src0 + b_len - 1, v0 * 1.08 + max(b_end_old - b_start_old, 0))
    v1.insert(v1.index(B), F)
    report.append(f"cut {C}: {gap:g} source frames back as {D} frames at {gap / D:.2f}x, zoom {v0:.1f} -> {v0 * 1.08:.1f} %")
P.write_text(json.dumps(d, separators=(",", ":"), ensure_ascii=False))
print(f"{P.name}:", *reversed(report), f"backup {bk / P.name}", sep="\n  ")
