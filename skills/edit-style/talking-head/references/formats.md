# The two approved formats

Pick the one the client's reference ad looks like, and copy the reference's pacing, layout and severity as closely as you can. The client judges every cut against his winning ad, so the closer the copy, the fewer rounds.

## Shared body (both formats)

1. **Credentials.** Her face, then pictures of her world.
2. **Problem.** Severe, real cellulite in plain home phone photos under the ceiling light: deep dents, not bumps, never smooth or AI-looking. Then the things that failed: creams, exercise, weight loss.
3. **Mechanism.** CGI on the science words (collagen, stem cells, eucalyptus "carries them past the surface"). A viewer must tell at a glance what it shows: real hands on real skin beat abstract meshes (Loom 8).
4. **Product.** The client's own bottle footage only (`assets/clips/b-roll/product/`), or generations made from the bottle sheets. When she holds it, it must be the real black-label bottle (Loom 11).
5. **Results.**
   - Confident US women of 55+ in shorts and swimsuits (no Asian women: the client sells in the US only).
   - Before/afters done as the reference does them: the same woman full length with her face shown. Before: at home in pyjamas, checking her thigh. After: outside in the sun, in a different outfit, smiling. Two ordinary phone photos side by side with a thin white line.
   - A reviews mosaic: a grid of many different women, each in a different pose with the bottle. One talks, one applies the oil, one reads the label, one is unboxing, and so on. The same pose everywhere reads as fake (user).
6. **CTA.** Her face for the whole line. The captions sit on each spoken word.

Hooks 2 and 3 are clones of the approved hook 1 with only the opening swapped. The body, its inserts and its captions move as one block.

## Format A: podcast mic (video-5, "thighs at 57")

- **Speaker.** A polished woman of the target's age at a podcast mic with headphones. She looks just left of the lens at an unseen host. No host voice is ever heard.
- **Hook, about 3 s.**
  - A glam "stunning at 57" campaign photo of her (high-end, not a normal older lady; Looms 8–9) under a two-line title with 🤯 and no full stop. Example: "How to make thighs" / "look 35 at 57 🤯".
  - The title box sits just under her chin (y about 655).
  - An 8-frame FilmCraft Push from the east with 80% motion blur takes the photo out onto her face as she says the line that ends the hook ("I'm 57"). The title and emoji hide as the push starts. A push on the text clips themselves smears them.
- **Scripts:** `kit/build_draft.py`, then captions, then `caption_layout.py`, `title_emoji.py`, `title_push.py`, `talk_motion.py`, `add_music.py`. Hooks 2 and 3 come from `make_hook.py 2 3`.

## Format B: straight to lens (DCT-2190, "GLP-1 thighs")

- **Speaker.** A dermatologist in scrubs with a made-up name on them ("Dr Susan Avery, MD"), in a clinic, talking **straight into the lens** as the reference does. She holds the bottle on the product and CTA lines.
- **Hook, about 4 s, copied from the reference.**
  1. Three pictures run under one two-line title ("If a woman finally lost the weight" / "and her thighs look worse than before"), holding about 2 s, 1 s and 1 s. A 6-frame Push with 80% blur joins each picture to the next and into the card.
     - The title is template 6 at 85% scale, anchor (540, 380), position (540, 422).
  2. A black card, a nested `card` sequence of about 58 frames. "LOSING MORE / WEIGHT / WILL NOT / CHANGE THAT" builds in big white Montserrat ExtraBold capitals (sizes 111/186/106/106). Each word appears on the frame it is spoken (`card_words.py`) with a click on A3 (`edit-style/assets/switch-click-02.mp3`).
  3. A push from the card onto her face for "I'm a dermatologist…".
  - In the clones, "losing more weight will not change that" stays hook 1's take, so the card and its clicks stay in sync.
- **Body captions:** a whole clause each, 3–5 words, up to about 32 characters, no end punctuation, at y 1360.
- **CTA:** two red arrows bobbing over her (`edit-style/assets/cta-arrows-red.png`).
- **Scripts:** `dct-2190/build_talking_head.py` (per-clip voice, 1.12x, gaps, −16 LUFS), then `build_hook1.py` (V1 cut at every join, V2 from the plan's shots), then captions, then `caption_layout.py`, `hook_text.py`, `card_words.py`, `talk_motion.py`, `add_music.py`. Hooks 2 and 3 come from `clone_hooks.py 2 3`.

## Building a third format

When a new reference ad doesn't fit A or B:

1. Break it down with `video-breakdown`.
2. Measure from its frames: the title position, caption height and length, pictures per second, the hook structure.
3. Write the new choices in the video's `AGENTS.md`.
4. Keep every client rule in `client-rules.md`: they hold for every format.
