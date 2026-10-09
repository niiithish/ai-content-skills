#!/usr/bin/env python3
"""Map a reference video's cuts onto our voiceover: where each reference shot lands in our edit.

For a remake that follows the reference script line for line (Mysa video-10: 96 reference shots over a 4:40 VO).
Matches the two word-timed transcripts word by word, anchors on content words, interpolates each reference cut
time into our VO, and snaps it to just before our nearest word start (cuts land on a word, the yap-style look).

Usage:
  ref-cuts.py REF.words.json REF.cuts.txt OURS.words.json [--syn "allfemme=mysa,gummy=softgel"] [-o map.json]

REF.cuts.txt: one cut time in seconds per line (video-breakdown prep.sh writes it as cuts.txt).
Prints one row per reference shot: shot, reference time, our time, reference words | our words.
map.json: [{"shot", "ref": [a, b], "ours": [a, b], "ref_words", "our_words"}], times in seconds.
"""
import argparse, difflib, json, re

STOP = set("the a an and to of it is in that you your i for on with this be are so or".split())
LEAD = 0.04   # cut this long before the word starts


def load(p):
    w = json.load(open(p))
    w = w if isinstance(w, list) else w["words"]
    out = []
    for x in w:
        if isinstance(x, (list, tuple)):
            t, s, e = x[0], x[1], x[2]
        else:
            if x.get("type", "word") != "word":
                continue
            t, s, e = x.get("word", x.get("text", "")), x["start"], x["end"]
        k = re.sub(r"[^a-z0-9']", "", t.lower())
        if k:
            out.append((k, s, e, t.strip()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ref"); ap.add_argument("cuts"); ap.add_argument("ours")
    ap.add_argument("--syn", default="", help="reference word=our word, comma separated (brand and product swaps)")
    ap.add_argument("-o", "--output", default="map.json")
    a = ap.parse_args()
    syn = dict(x.split("=") for x in a.syn.split(",") if "=" in x)
    R, O = load(a.ref), load(a.ours)
    rn = [syn.get(x[0], x[0]) for x in R]
    on = [x[0] for x in O]
    anch = [(0.0, 0.0)]
    for blk in difflib.SequenceMatcher(None, rn, on, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            if rn[blk.a + k] not in STOP:
                anch.append((R[blk.a + k][1], O[blk.b + k][1]))

    def m(t):
        for (r0, o0), (r1, o1) in zip(anch, anch[1:]):
            if r0 <= t <= r1:
                return o0 + (t - r0) * (o1 - o0) / max(r1 - r0, 1e-6)
        return anch[-1][1] + (t - anch[-1][0])

    starts = [x[1] for x in O]
    snap = lambda t: 0.0 if t <= 0 else max(0.0, min(starts, key=lambda s: abs(s - t)) - LEAD)
    end_r = R[-1][2] if R else 0
    cuts = [0.0] + [float(l) for l in open(a.cuts) if l.strip()] + [end_r]
    rows = []
    for i, (ra, rb) in enumerate(zip(cuts, cuts[1:]), 1):
        oa, ob = snap(m(ra)), (snap(m(rb)) if i < len(cuts) - 1 else O[-1][2])
        rw = " ".join(x[3] for x in R if ra <= x[1] < rb)
        ow = " ".join(x[3] for x in O if oa <= x[1] < ob)
        rows.append({"shot": i, "ref": [round(ra, 2), round(rb, 2)], "ours": [round(oa, 2), round(ob, 2)], "ref_words": rw, "our_words": ow})
        print(f"{i:>3} {ra:6.2f} -> {oa:6.2f}-{ob:6.2f} | {rw[:45]:45} | {ow[:55]}")
    json.dump(rows, open(a.output, "w"), indent=1, ensure_ascii=False)
    print(f"{len(anch) - 1} anchor words, {len(rows)} shots -> {a.output}")


if __name__ == "__main__":
    main()
