---
name: video-breakdown
description: >
  Decode a reference / inspiration video locally into the pattern we copy: every
  cut, what kind of picture each shot is (speaker close-up, wide, split two-shot,
  B-roll, product, CGI, screen recording), which spoken words each shot sits on,
  how often inserts come and how that changes beat by beat, then lay that pattern
  onto our script so the plan copies the reference's rhythm. Runs on this machine
  (ffmpeg cut detection, shot grouping, Parakeet word timing, shot sheets the agent
  reads); no Gemini. Use when a client sends a reference or inspiration video with
  a brief, when the user wants a breakdown, decode, cut list, shot list, rhythm or
  "how often do the clips come", wants to copy or remake an ad, or on
  /video-breakdown. Triggers: decode this video, breakdown, the cuts, scene changes,
  shot-by-shot, beat-by-beat, analyze this clip/ad/reel, recreate this ad.
---

# Video breakdown (local)

The client's brief is usually the reference's voiceover rewritten for our product. So what the plan needs from the reference is its **visual pattern on the words**: on which words it cuts, what kind of picture comes in (and for how long), how often inserts come, and how this changes from the hook to the CTA. The words we already have.

`<skill-dir>` is the folder holding this file. `breakdown.py` needs only ffmpeg, numpy, Pillow (tesseract optional).

## 1. Analyze (about 7 s for a 1-minute video, ~30 s for 4 minutes)

The reference goes in `<project>/reference-video/`. If the user dropped it loose in the video folder, `plan.py init` (video-plan) moves it there; otherwise move it yourself with `mv`, never a copy. Then:

```bash
python3 "<skill-dir>/scripts/breakdown.py" analyze "/abs/path/reference-video/REF.mp4"
```

It writes `REF.breakdown/` next to the video:

- `words.json`, `transcript.txt`, `transcript.srt`: word-timed transcript (local Parakeet; it reuses `REF.words.json` if one exists).
- `shots.json`: every shot with start, end, length, how it was cut in (`hard`, or `soft` for dissolves and whips), its **group**, its motion (`static` / `moving` / `busy`), its words, and where the cut falls against the voice (`on-word`, `mid-word`, `word-end`, `in-pause`).
- `sheets/clusters_NN.jpg`: one row per **group**, meaning shots that look like each other (the same camera on the same person, the same B-roll clip). The group that comes back most is at the top.
- `sheets/shots_NN.jpg`: 12 shots a sheet. Each shot shows its start, middle and end frames, a header (`#id time length group motion` plus flags) and the words spoken over it. `JUMP` means the same group as the shot before, so a punch-in or a cut inside the same angle. `SOFT` means a soft transition.
- `labels.json`: what you fill in next.

## 2. Look and label (the only judgment step)

Read **every** sheet in order: the cluster sheets first, then the shot sheets. Don't open single frames unless a cell is unclear, and don't hand this to a subagent. Then fill in `labels.json`:

- **`groups`**: give every group a `type` and a short `label` (who or what, framing, camera move). Types are `talking-head` (one speaker; say which and how framed), `two-shot`, `split` (stacked or side by side speakers), `broll` (live-action clip), `still` (photo with a push), `cgi` (3D, inside the body, animated diagram), `product` (packshot or product in hand), `text` (screen recording, article, review, website, UI), `compare` (before/after side by side or a wipe between them), `story` (the cast acting a scene in a story or song ad; it counts as the spine like a speaker), `transition` (a black frame, flash or whip blur bridging two shots; not counted as an insert), and `other`. Because one group is often 30+ speaker shots, labeling the groups labels most of the video.
- **`shots`**: `{"12": {"type": "...", "label": "...", "note": "..."}}` for single shots that differ from their group. Keys can be ranges (`"40-55"`); a later key overrides an earlier one. In an animated story or song ad almost every shot is its own group, so label by ranges along the story instead of by group.
- **`drop_cuts`**: ids of shots that are not real cuts, such as one website scroll split into four pieces or a clip that carries on after a flash. Each one is merged into the shot before it.
- **`sections`**: `[[start_sec, "Hook"], [8.9, "Host asks"], …]`. Name the beats from the transcript, and use the brief's beat names when the client gives them.

Then:

```bash
python3 "<skill-dir>/scripts/breakdown.py" report "/abs/path/reference-video/REF.breakdown"
```

This writes `rhythm.md` and `timeline.png`:

- `rhythm.md` has the share of runtime and average length for each type, the insert cadence (one insert block every N s, block length, speaker-shot lengths), cut timing against the voice, a per-section table (shots, average shot, speaker share, inserts by type) and the full shot list.
- `timeline.png` is a colour bar of the whole video, one colour per type, with the sections marked.

Read the timeline image to check the labels look right.

**Story and song ads (Pixar, claymation, sung):** there is no speaker, so the cast acting the story is `story` (the spine) and inserts are the mechanism CGI, product and screens. The rhythm number that matters is in `rhythm.md` under "Words a shot" (how many sung words each picture carries) and the average shot per section (tempo follows the emotion). ASR is weak on singing; the burned-in captions on the sheets are the true lyric. Merge continuous camera moves and morphs that were cut into pieces (`drop_cuts`), but keep deliberate flicker montages.

## 3. Lay the pattern on our script

```bash
python3 "<skill-dir>/scripts/breakdown.py" map "/abs/path/REF.breakdown" "/abs/path/brief/script.txt" [--hook 2]
```

- **What it does:** it aligns the reference words with ours. Runs of matching words are anchors, and every reference cut is placed between them, so each of our words lands in exactly one reference shot. The result is `pattern-on-script.md`: one row per reference shot with its type, the reference picture and **our words** under it, plus our lines that have no reference shot (new copy, which gets the pattern of the nearest beat).
- **Script input:** `.txt`, `.md` or `.pdf`. Give it the plain script or lyric sheet, not a brief laid out as a table (the table's visuals column gets read as words). `--hook N` picks which `HOOK N` to use with the body. Speaker tags and BEAT headings are skipped.
- **Once our voiceover exists:** run it again with `--vo our.words.json` to get our real times (`pattern-on-vo.md`).
- **The match rate:** it prints this. Above ~50% the mapping is solid. Lower means the script was restructured, so map beat by beat yourself using `sections`.

## 4. Write the breakdown

Save `REF.breakdown/BREAKDOWN.md`. Keep it short, because the tables are already in `rhythm.md`:

1. **Specs:** size, length, words and wpm, shot count, average shot. Look, audio (VO, music, SFX), and captions in one line each.
2. **Pattern:** the format (for example, two-person podcast with the expert carrying the script), the beat structure, what the inserts do (illustrate the noun being said, prove a claim, show the product on the brand name), and the rhythm rules visible in `rhythm.md`. Write those rules as numbers the plan can copy, for example "an insert block every ~10 s, 1–3 shots, 1–3 s each; inserts cluster on the mechanism and product beats; host shots carry no inserts; split two-shot on beat transitions".
3. **Insert vocabulary:** each kind of insert the reference uses, with the trigger word and length. For example: "screen recording of a search result when a new term is named", "CGI of the problem inside the body on the symptom line", "product macro burst of 0.2–1 s shots on the brand name".
4. **Captions:** font, case, colour, box, words per page, position (y as % of height), then the nearest `captions-filmcraft` template (2 bold caps one-liner, 3 small native, 4 sentence-case, 6 two-line box) and how it differs.
5. **Cast and setting:** who is on camera, their wardrobe and set, and how many camera angles each has (for the still prompts).
6. **Not settled from frames:** music or SFX you can't hear, motion between sampled frames, unclear text.

Then go to `video-plan` with `pattern-on-script.md` as the shot spine.

## Rules for the remake

- Copy the **rhythm and the kind of picture** on each phrase, not the exact pictures. A reference insert of gym powder becomes our product's own "old way" picture.
- Keep our word count within ~5% of the reference unless the client's script says otherwise.
- Cite where every product claim comes from (brief, product page), and never invent numbers.
- Never generate a split screen as one split frame. Plan each half as its own still and clip (subject centred, action inside the middle half of the width), and build the split, seam and labels in the edit.
- A known toy or brand look is fine to match. Describe it generically in prompts and use original characters and invented competitor brands.

## Gemini (only if the user asks)

Gemini can hear music and SFX and see motion between frames. If the user wants that layer, the old prompt is still in [references/gemini-prompt.md](references/gemini-prompt.md). Run it in the browser pane on Gemini Pro, and treat its output as notes on top of the local breakdown, never as the shot list.
