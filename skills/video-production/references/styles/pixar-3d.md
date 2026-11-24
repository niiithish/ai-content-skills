# Style Module: Pixar 3D Animation (`--style pixar-3d`)

Stylized 3D feature-animation CG (warm, jewel-toned Disney/Pixar theatrical look by default). Open the approved quality-bar stills and prompts in `../look/pixar-3d/` before writing the first still of a project.

## 1. Sheets & Continuity Rules

- **Sheets only, never scene stills as ingredients** for new shots: every still takes only the environment sheet, the character's outfit sheet (base sheet → outfit edit via `--ref`), and the product sheet. Passing an earlier scene still degrades quality and copies its framing/poses.
- **Opposite-side environment sheets:** When a scene requires shot/reverse-shot dialogue in the same room (e.g., across a cafe table or living room), generate an opposite-angle environment sheet from the primary environment sheet as `--ref` so the reverse wall never duplicates the front wall.
- **Product mascots** (product with face/limbs): Edit the client's real product photo with `--ref`, adding only the face and limbs. Never generate the product or its logo from text.
- **Relative scale:** State relative scale in every multi-character prompt (e.g., "the cat's back is at the man's shin"; product bottle at ~1/5 frame height next to a glass).

## 2. Visual Direction (Default Pixar Look)

- **Render:** High-end 3D feature-animation CG: appealing sculpted characters, big glossy expressive eyes with catch-lights, soft subsurface glow on skin, clumped sculpted hair, detailed fabric weave. Never 2D, never outlined, never photoreal, never plastic/toy/game-like.
- **Color & Light:** Saturated jewel tones (mustard, magenta, emerald, lavender, burgundy, navy, peach). Warm motivated light from named in-room sources (window sun, brass lamp, string lights) with soft warm rim light and bokeh. Anchor warmth to a real source so models don't drift into unmotivated orange sunset haze. Sad moments use a darker moody key, never flat grey.
- **Depth & Acting:** Every still specifies FOREGROUND, MIDGROUND, BACKGROUND with shallow DOF. Describe expressions muscle by muscle ("brows knitted, biting lower lip, shoulders hunched").
- **Pin positions to landmarks:** Never rely on bare "left/right" with two characters — anchor each to a room landmark ("man on the window side, woman on the lamp side") plus "as the viewer sees it."
- **Age locks:** Older characters drift young in 3D close-ups; state age traits explicitly ("clearly 63: crow's feet, laugh lines, silver streaks") and negate "young woman, smooth wrinkle-free skin."

## 3. Clip Prompt Template (Silent B-Roll Under VO or Song)

Pass `@image1` (approved still) as primary reference. Add character/product sheets only when a face is hidden/turns, someone enters, or a printed label moves.

```text
[N]-second vertical 9:16 3D animated clip in a stylized feature-animation CG look, one continuous shot with no cuts. @image1 is the reference and source of truth for characters, faces, hair, clothes, set, props, colours and warm light. Do not add any person, object or prop not in @image1. Printed text on labels, signs, papers and screens stays exactly as in @image1. No reference sheets, panels or grey backgrounds ever appear.

Shot (0–[N] s): [timed beats: "0–2 s: ... 2–4 s: ..."; expression change; prop states; walking direction tied to @image1]. Camera: [one gentle move: slow push-in, slide, or rack focus].

Light: [named key source and position from @image1]; it stays fixed, and every face keeps the same lit side and shadow side throughout.

Acting: [character acting direction]. Everyone in frame acts expressively the whole time with natural secondary motion: blinking, breathing, hair and fabric shifting.

Style: high-end 3D feature-animation CG exactly as in @image1 — appealing stylized characters, big expressive eyes, soft smooth skin, sculpted hair, detailed fabric, rich jewel tones. Never photoreal or live action; faces never drift toward realistic human skin pores or proportions.

Sound: soft ambience of the place and sounds of visible actions only. Nobody speaks; only wordless sounds (sighs, gasps, laughs). No music, no score, no narration. No captions, subtitles or added on-screen text.
```

## 4. Animated Characters Speaking on Camera (Mascots / Talking Remakes)

When a 3D character speaks directly to camera:
- **Whole sentences only** (never split a sentence across clips); clip ends 0.5–2 s after the last word.
- **Speech starts on frame 1** with zero gaps; quote the line **once** in `Dialogue:` only (never re-quote words in `Action:` or the model repeats them).
- **Voice lock:** State adult age, pitch, accent, and `"Clearly a grown adult, never a child or squeaky cartoon voice."` Repeat identically across every clip.
- **No impact SFX under speech** (thuds/slams make Flow restart words).
- **After the last word:** hold the final expression cleanly — no new effects or sparkles.

## 5. Pixar-Specific Failure Locks

- **Complex actions fail:** Avoid writing/ticking calendars, spinning 360°, or bite-by-bite eating (food multiplies — take whole in one go). Simplify into one clear physical beat per clip.
- **Blank screens & white bottles:** Quote 2–5 word phone notification text and give competing shelf products colored fictional labels.
- **Cosy inner-body cutaways:** If an animated ad needs a stylized "inside the body" fantasy sequence (only when requested by user/brief — never unprompted), see `../look/inner-world/` and `medical-cgi.md` (Section 5).
- **Couple-in-bed blocks:** Route to `elevenlabs-creative` (`Seedance 2.0 Mini` with `9:16` and `quantity=1`) rather than burning Flow retries.
