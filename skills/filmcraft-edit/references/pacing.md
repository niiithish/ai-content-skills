# Pacing & Motion Reference (`scripts/fc_pace.py`)

Run `fc_pace.py` after the timeline is built and **before** `captions-filmcraft` (cutting pauses shifts every word's frame). `fc_pace.py` uses `fc.py` (live bridge when open) and `transcribe`'s `pauses.py` (waveform-based pause detection — never ASR word ends).

## Workflow

```bash
# 1. Inspect current pacing numbers (quote these before editing)
scripts/fc_pace.py report video-N/edit/hook-1.fcproj              # --vo A2 if voice is on A2

# 2. Cut dead air (use --dry first to preview cuts)
scripts/fc_pace.py tighten video-N/edit/hook-1.fcproj --style calm --dry
scripts/fc_pace.py tighten video-N/edit/hook-1.fcproj --style calm

# 3. Add subtle motion to static clips (never overwrites existing keyframes/scales)
scripts/fc_pace.py motion video-N/edit/hook-1.fcproj --style calm  # --face-y Y if face != 40% height

# 4. Rebuild captions because timing shifted, then re-run report
scripts/fc_pace.py report video-N/edit/hook-1.fcproj
```

Each run backs up the `.fcproj` to `edit/backup-<date>-pacing/` on the first run of the day.

## Calm vs. Punchy Presets

| Parameter | `calm` (default, 35+ Meta buyers) | `punchy` (fast young-creator style) |
|---|---|---|
| Short pause cut target | `0.12 s` | `0.08 s` |
| Sentence-end pause (≥ 0.35 s) cut target | `0.20 s` | `0.12 s` |
| Lead silence kept before next consonant | `0.04 s` | `0.04 s` |
| Visible jump-cut punch-in | `108%` | `115%` |
| Slow push on long static talking stretch | > 4.0 s → `106%` | > 2.5 s → `110%` |
| Static B-roll push in/out | `100 ↔ 106%` | `100 ↔ 110%` |

## Guardrails

- **Cover jump cuts with B-roll first.** A jump cut on a talking head reads as an edit; a cut to B-roll reads as a story. Place B-roll over visible jump cuts before running `motion`.
- **No jarring hard-cut jump zooms in hook openings.** If a hook has tight dead-air cuts, prefer one continuous slow zoom across the opening (or brief 1.5x playback across a micro-pause) instead of abrupt 100↔110% jumps.
- **Never touch clips that already have motion.** `fc_pace.py motion` skips any clip with existing scale/position keyframes, non-100 scale, or moved position.
- **Never cut B-roll or music to fit.** Only V1 + the voice track are razored; B-roll, overlays, and music shift with the timeline.
- **Music level:** `report` prints music gain for reference; keep music **−16 to −18 dB under voice**.
- **Raw-timeline exception:** skip `fc_pace.py` completely when the user asks for an untrimmed timeline to edit by hand.
