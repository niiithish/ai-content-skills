# Voiceover, Song & Slideshow Edit Reference

Use when generated shots (photoreal B-roll, 3D animation, claymation) or illustrated stills run under a voiceover or AI sung track (typically 15–150 shots per hook).

## Track Layout

| Track | Contents |
|---|---|
| `V1` | Sequential shots from each line's first word to the next shot. Zero gaps, zero black frames. |
| `V2` | Second half of a split screen, or picture-in-picture box / overlay over V1. |
| `V3+` | Captions (`captions-filmcraft`), end cards, CTA overlays. |
| `A1` | Voiceover (normalized to −16 LUFS, sped up 1.1x and pause-tightened) or edited song track. |
| `A2` | Background music (**−16 to −18 dB under voice**, 1–2 s fade-out). Omit for sung ads. |

Clip sound is muted on all video tracks — A1 is the only voice/song audio.

## Building Hook 1

1. **Map `PLAN.md` times to the edited voice.** Divide 1.0x script timestamps by voice speed (e.g., 1.1x) and map through any pause cuts removed from A1.
2. **Select versioned finals.** Use each shot's 1080p final (`clips/clip-N/clip-Nx/final/...-1080p.mp4`), never `clips/all/`.
3. **Trim Flow lead-in.** Skip dead/static lead-in using motion/audio onset (fallback **0.5–1.0 s**).
4. **Fit each clip to its slot without ugly slow-downs:**
   - Start-to-end-state clips: speed up to play whole inside the slot so the end state is seen.
   - Standard clips longer than slot: trim out-point to slot length.
   - Clips shorter than slot: **do not** drag down to ~77% speed. Prefer trimming/tightening the slot, pairing with a second complementary shot, or regenerating a longer clip (report any unavoidable slight slow-down).
5. **Snap cuts onto first words.** Run `fc_captions.py plan` to flag cuts off their spoken phrase, then roll cuts onto the exact first frame of each phrase.
6. **Captions:**
   - For **voiceover ads**: standard `captions-filmcraft` workflow (`words`, `plan`, `build`, `check`).
   - For **AI sung ads (Suno)**: always use vocal-separated timing (`fc_captions.py words --vocals` or `vocals` -> `transcribe`) so instrumental beds don't mask line onsets or drag caption ends. Sync clip 1 to the actual vocal onset (trimming any silent/instrumental intro before the singer starts).
7. **Music:** lay music on A2 at **−16 to −18 dB under voice** (verify with `ffmpeg` `ebur128` / `fc_qa.py`) with a 1–2 s fade-out.

## Stills Slideshow (Storybook / ELI5)

- Match the reference's cut rate.
- Every still gets a centred **2 %/s slow push** (or gentle pan on wide compositions) from its first frame to its last.
- Hard cuts; captions small and centred/mid-frame when the reference uses that look (Template 5).

## Splits (Side-by-Side & Top/Bottom)

- Always build from **two separate clips/stills** whose subjects are centred in the middle half of the frame.
- Side-by-side: crop 25% left and right on each; top/bottom: crop 25% top and bottom on each.
- Add a thin seam line between halves; place labels as text clips and captions on the seam.

## Cloning Hooks 2 & 3

- **Voiceover ads:** copy the approved `hook-1.fcproj`, replace only the opening shots and hook voiceover (tightened identically), shift the entire body as one block, re-lay music, and verify body parity with `scripts/audit.py --body-of`.
- **Sung ads:** each Suno hook take drifts slightly (up to ~3 s). Map body cuts piecewise-linearly through shared sung words, anchor the intro by hand to the vocal onset, and rebuild captions per hook.
