#!/usr/bin/env python3
"""Ends each caption in captions/<stem>.captions.json when its last word is sung, not when the next caption starts.
In a song the music fills the pauses, so the plan's loudness-based pause finder sees none, and Parakeet and Scribe
stretch a word over the gap after it ("tissue" 1.8-3.3 s). faster-whisper's word ends match the vocal ("tissue" ends
at 2.08 s). The caption words are aligned to whisper's (difflib), and a caption ends TAIL frames after whisper's end
of its last heard word when that leaves a gap of at least GAP frames before the next caption; otherwise it stays up
until the next one. Run between `plan` and `build`.
Usage: caption_ends.py captions/hook-1.captions.json captions/hook-1.fw.json"""
import difflib, json, math, re, sys

TAIL, GAP, MIN = 3, 12, 15  # frames: after the last word, smallest gap worth clearing, shortest caption
NUM = {"1": "one", "2": "two", "7": "seven", "12": "twelve", "14": "fourteen", "30": "thirty", "42": "fortytwo",
       "60": "sixty", "90": "ninety", "co2": "cotwo"}


def norm(t):
    out = []
    for p in re.split(r"[\s\-/]+", t.lower()):
        p = re.sub(r"[^a-z0-9']", "", p).replace("'", "")
        if p:
            out.append(NUM.get(p, p))
    return out


cap, fw = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
fps, b = cap["fps"], cap["blocks"]
cw, owner = [], []  # caption words and which block each belongs to
for k, r in enumerate(b):
    for w in norm(r["text"]):
        cw.append(w)
        owner.append(k)
ww, wstart, wend = [], [], []  # whisper words and their times
for w in fw:
    for p in norm(w[0]):
        ww.append(p)
        wstart.append(w[1])
        wend.append(w[2])
last, first = {}, {}
for m in difflib.SequenceMatcher(None, cw, ww, autojunk=False).get_matching_blocks():
    for i in range(m.size):
        last[owner[m.a + i]] = (m.a + i, wend[m.b + i])
        if m.a + i == 0 or owner[m.a + i - 1] != owner[m.a + i]:
            first[owner[m.a + i]] = wstart[m.b + i]
# Parakeet drops whole sung phrases ("breakfast" 108-115.5 s on hook 2), so the plan bunches or spreads the blocks
# after them. Whisper hears them: a block whose first word Parakeet missed (or that the plan spread) starts on
# whisper's first word, on a cut when one is within SNAP frames. Elsewhere Parakeet's start stays: whisper's sung
# word starts run early.
pw = [p for w in json.load(open(sys.argv[2].replace(".fw.json", ".pk.json"))) for p in norm(w[0])]
heard = set()  # caption word indexes Parakeet heard
for m in difflib.SequenceMatcher(None, cw, pw, autojunk=False).get_matching_blocks():
    heard.update(range(m.a, m.a + m.size))
lead = {}
for i, o in enumerate(owner):
    lead.setdefault(o, i)
SNAP = 6
for k, r in enumerate(b):
    if k == 0 or k not in first:
        continue
    f = round(first[k] * fps)
    if lead[k] not in heard or r.get("src") == "spread":
        near = [c for c in cap["cuts"] if abs(c - f) <= SNAP]
        f = min(near, key=lambda c: abs(c - f)) if near else f
        if b[k - 1]["start"] < f < (b[k + 1]["start"] if k + 1 < len(b) else 10 ** 9):
            print(f"NOTE {r['text']!r} moved {f - r['start']:+d} frames onto its first word")
            r["start"] = f
for k, r in enumerate(b[:-1]):
    r["end"] = b[k + 1]["start"]
cleared = 0
for k, r in enumerate(b):
    nxt = b[k + 1]["start"] if k + 1 < len(b) else r["end"]
    if k not in last:
        continue
    wi, t = last[k]
    if wi < len(cw) - 1 and owner[wi + 1] == k:  # the block's real last word wasn't heard: leave it up
        continue
    e = max(math.ceil(t * fps) + TAIL, r["start"] + MIN)
    if e <= nxt - GAP:
        r["end"] = e
        cleared += 1
    elif k + 1 == len(b):
        r["end"] = min(r["end"], max(e, r["start"] + MIN))
json.dump(cap, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
for k, r in enumerate(b):
    gap = (b[k + 1]["start"] - r["end"]) / fps if k + 1 < len(b) else 0
    print(f"  {r['start'] / fps:7.2f} {r['end'] / fps:7.2f}  {r['text']:28s}" + (f" gap {gap:.2f}" if gap else ""))
print(f"{cleared} of {len(b)} captions now end with their words")
