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

## Format C: two-woman podcast (Calvin video-23, DCT#28 reference, 2026-11-09)

- **Cast.** A host and a guest in one room, each on her own master (close-up and wide per woman), never in one frame. They look at each other off-camera, never into the lens. Recast them at the audience's age (Mysa: 45–65) and change at least one outfit item from the reference (the user picked a camel-brown blazer for the host).
- **One clip per spoken line, from one angle.** The guest alternates close-up and wide by line. A cut inside a line is a digital punch-in at a clause.
- **Splits are built in the edit**: speaker on top, listener under, from two clips (crop top 10 % and bottom 40 %, motion position y 768 / 1728). The two silent listening clips (one per woman) feed every split. Captions inside a split move onto the seam (`dct-28/seam_captions.py PROJECT`, y 506), rerun after every caption build.
- **Voice:** the clips split into one folder per speaker, one ElevenLabs voice each (`talking-head-video-production`, `voice_change.py`, speakers found from the master stills).
- **Captions:** template 1 (ALL CAPS TikTok Sans SemiBold on black boxes, no punctuation, no word hyphens, 1–3 words).
- **Screen inserts:** focus screens and a slow product-page scroll (`edit-style/references/screen-inserts.md`).
- **Hook opening:** one continuous slow zoom across its jump cuts (no ×1.08 steps), a cut pause put back at 1.5x with a quick ×1.08 zoom instead of a hard jump cut (`dct-28/fill_jumpcuts.py`), and a FilmCraft `zoom_blur` transition (8 frames on V1, 4 on a split's listener) on the hook-to-body cut.
- **Scripts (`dct-28/`, video-23's own; set the paths and shot lists at the top):** `build_hook1.py` (the whole hook-1 build: talking pieces, inserts, splits, pushes), `seam_captions.py`, `make_focus_screens.py`, `make_219_scroll.py`, `build_hooks23.py` + `add_opening_captions.py` (hooks 2–3), `fill_jumpcuts.py`. `speech_ranges.py` + `build_speaker_projects.py` + `check_exports.py` were the first voice-change route (one continuous track per speaker, silences over 0.3 s squeezed); `voice_change.py` replaces them.

## Building a fourth format

When a new reference ad doesn't fit A or B:

1. Break it down with `video-breakdown`.
2. Measure from its frames: the title position, caption height and length, pictures per second, the hook structure.
3. Write the new choices in the video's `AGENTS.md`.
4. Keep every client rule in `client-rules.md`: they hold for every format.
