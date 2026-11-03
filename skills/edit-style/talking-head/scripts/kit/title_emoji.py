#!/usr/bin/env python3
"""The brief's 🤯 after each hook's title caption (user 2026-10-29: "check client brief use that emoji"; brief-2810:
"How to make thighs look 35 at 57 🤯"). FilmCraft draws no colour emoji (a tofu box in TikTok Sans, blank strips in
Noto Color Emoji), so the emoji is a PNG (assets/emoji/exploding-head.png, from Noto Color Emoji) on its own track
right above the captions (under them the white box hid it), for exactly the title caption's frames, beside its text:
the text and emoji are centred together and the white box is widened to hold both. fc_inserts.py skips a top track
with no text on it, so the captions still count as the caption track.
The title caption is the first caption ending "at 57"; the emoji goes after its last line, whose full stop is dropped, as in the brief.
Rerun after make_hook.py or a caption build. Usage: title_emoji.py hook-1.fcproj [...]"""
import datetime, json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMOJI = ROOT / "assets/emoji/exploding-head.png"
EM = 60          # emoji height on screen, px (text is 58 px TikTok Sans)
GAP = 12         # between the last word and the emoji
PAD = 17         # template 6 box side padding
TPS, FPS = 254016000000, 24
F = TPS // FPS


def cli(proj, cmds):
    f = proj.with_suffix(".emoji.jsonl"); f.write_text("".join(json.dumps(c) + "\n" for c in cmds))
    out = subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "run", str(f)], capture_output=True, text=True)
    f.unlink(); rs = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    bad = [r for r in rs if not r.get("ok")]
    if bad or out.returncode:
        sys.exit(f"{proj.name}: {bad or out.stderr[-1500:]}")
    return [r.get("result") for r in rs]


def seq(proj):
    return json.loads(subprocess.run(["filmcraft-cli", "--compact", "--project", str(proj), "inspect", "sequence"],
                                     capture_output=True, text=True, check=True).stdout)


def text_of(c):
    """the caption's lines, joined with " / " (a two-line template 6 caption has a text layer per line)"""
    return " / ".join(re.sub(r'^(?:String|Text)\("(.*)"\)$', r"\1", e["params"]["text"]["value"])
                      for e in c["effects"] if e["effect"] == "graphic_text")


def ypos(c):
    return float(re.findall(r"y: ([-\d.]+)", c["effects"][0]["params"]["position"]["value"])[0])


iw, ih = map(int, subprocess.run(["magick", "identify", "-format", "%w %h", str(EMOJI)], capture_output=True, text=True).stdout.split())
for a in [a for a in sys.argv[1:] if a.endswith(".fcproj")]:
    proj = Path(a).resolve()
    bk = proj.parent / f"backup-{datetime.date.today()}-emoji"; bk.mkdir(exist_ok=True)
    if not (bk / proj.name).exists():
        shutil.copy2(proj, bk / proj.name)
    s = seq(proj); v = s["video"]
    caps = max(range(len(v)), key=lambda i: sum(1 for c in v[i]["items"] if text_of(c)))
    old = [c["clip"] for t in v for c in t["items"] if c.get("name") == EMOJI.name]
    pre = [{"id": "edit.clear", "params": {"clips": old}}] if old else []
    em_track = caps + 2         # the track right above the captions: empty, the emoji's own, or a new one
    if caps + 1 >= len(v):
        pre += [{"id": "sequence.addTracks", "params": {"video": 1, "audio": 0}}]
    elif any(c.get("name") != EMOJI.name for c in v[caps + 1]["items"]):
        sys.exit(f"{proj.name}: V{em_track} above the captions holds other clips")
    title = next(c for c in sorted(v[caps]["items"], key=lambda c: c["startFrame"]) if re.search(r"at 57\.?$", text_of(c)))
    layers = cli(proj, [{"id": "graphics.list", "params": {"clip": title["clip"]}}])[0]["layers"]
    tl = max((L for L in layers if L["kind"] == "text"), key=lambda L: L["position"][1])     # the last line
    bl = min((L for L in layers if L["kind"] != "text"), key=lambda L: abs(L["position"][1] - tl["position"][1] + 20))   # its box
    text = tl["text"].rstrip(".")
    item = cli(proj, pre + [{"id": "graphics.setText", "params": {"clip": title["clip"], "layer": tl["layer"], "text": text}},
                            {"id": "file.import", "params": {"paths": [str(EMOJI)]}}, {"id": "file.save", "params": {}}])[-2]["items"][0]
    layers = cli(proj, [{"id": "graphics.list", "params": {"clip": title["clip"]}}])[0]["layers"]
    box, txt = layers[bl["layer"]], layers[tl["layer"]]
    w = txt["localBounds"][2] - txt["localBounds"][0]
    total = w + GAP + EM
    tx = 540 - total / 2 + w / 2
    by = box["position"][1]
    clip = cli(proj, [{"id": "graphics.set", "params": {"clip": title["clip"], "layer": tl["layer"], "props": {"position": [round(tx, 1), txt["position"][1]]}}},
                      {"id": "graphics.set", "params": {"clip": title["clip"], "layer": bl["layer"], "props": {"size": [round(total + 2 * PAD, 1), box["localBounds"][3] * 2]}}},
                      {"id": "timeline.place", "params": {"item": item, "track": f"V{em_track}", "frame": title["startFrame"], "insert": False,
                                                          "duration": title["durationFrames"] * F, "video": True, "audio": False}},
                      {"id": "file.save", "params": {}}])[2]["clips"][0]
    ex, ey = 540 + total / 2 - EM / 2, ypos(title) - 960 + by - 2
    cli(proj, [{"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "scale", "value": round(EM / ih * 100, 2)}},
               {"id": "effects.setParam", "params": {"clip": clip, "effect": "motion", "param": "position", "value": [round(ex, 1), round(ey, 1)]}},
               {"id": "file.save", "params": {}}])
    print(f"{proj.name}: \"{text} 🤯\" frames {title['startFrame']}-{title['endFrame']}, captions V{caps + 1}, emoji V{em_track} at {ex:.0f},{ey:.0f}, box {total + 2 * PAD:.0f} px")
