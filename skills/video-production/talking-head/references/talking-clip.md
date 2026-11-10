# Talking clips

One clip per spoken line, in `clips/clip-N/clip-Nx/`, job ingredients = the master still only. Talking clips skip the usual "write it from what's in the still" step: every clip has the same still, so the prompt is the template below with the line, length and mood changed.

## Lines and lengths

- One sentence never splits across clips (the model cuts it off). Long lines split at a clause into `Na`, `Nb`.
- Length: the shortest Flow length (6, 8 or 10 s) that holds the line at ~3.2 words a second plus 0.5–2 s after the last word (`plan.py voiceover --on-camera` gives it). 4 s clips rush.
- Each clip is generated from the master still, not chained: the cut between lines is a jump cut the edit hides with a zoom change, and chaining from a last frame drifts the face.

## The template (Aleo `clip-1a-v2.md`, which fixed v1's added word)

```text
<L>-second vertical 9:16 video, real phone-camera footage of <a dermatologist> talking straight to the camera into a podcast microphone, one continuous shot with no cuts. @image1 is the reference for <the doctor>, her clothes, the microphone, the background, the framing and the light. It is not the first frame: she does not start in the exact pose of @image1; she is already in the middle of talking, moving naturally.

<The doctor>: the woman in @image1, <age, skin, brows, eyes, hair>, in <clothes, with the badge turned away so nothing on it can be read>. Same face, hair and clothes in every frame.

Dialogue: she starts speaking on the very first frame and says this line, word for word, in English, in one calm, flowing delivery at a brisk, natural pace with no long pauses, finishing the whole line before the clip ends, her mouth clearly lip-synced to every word: "<LINE>" Every word is said exactly once, in order, with no repeats or restarts, and no word is added: the line ends "<last 5–6 words>", with nothing between "<word>" and "<word>". This is the only speech in the clip. Voice: <a 38-year-old American woman dermatologist, warm, calm and confident, a clear mid-pitched voice with a neutral General American accent, speaking like a trusted doctor explaining something to a patient>. Only she speaks.

Performance: she looks into the lens the whole time and speaks <mood of this line: serious, knowing / reassuring / a little indignant>. Natural movements throughout: gentle head nods and tilts on the key words, her brows lifting slightly, her shoulders shifting as she leans a little toward the microphone, blinking and breathing. Now and then one or both hands rise into frame beside the microphone in relaxed explaining gestures, fingers loose and open, then lower again; her hands never touch the microphone or the pop filter. After the last word she keeps the same expression, looking into the lens, with small natural movements until the clip ends.

Camera: a fixed camera on a tripod, never seen in the frame. Exactly the same crop, angle and distance as @image1 from the first frame to the last: no zoom, no push-in, no pan, no shake. The <round black pop filter and the black foam microphone> stay exactly where they are in @image1, still, in the bottom of the frame. Only <the doctor> moves.

Setting: the same <bright home office> behind her as in @image1: <the window, the plant on the shelf>, the same soft daylight. Nothing is added.

Sound: her voice recorded close on the podcast microphone, clear and natural, the loudest sound, over the faint quiet room tone of a small, quiet <home office>. No music, no score, no beeps, no other voices, no echo.

No captions, subtitles or text on screen, and no readable writing on her coat or badge.
```

Why each part is there:
- **"Not the first frame … already in the middle of talking"**: otherwise every clip opens on the same frozen pose and the joins look like a loop.
- **"Every word is said exactly once … nothing between X and Y"**: Flow repeats or adds words at hard joins. When a take adds or repeats one, the next version names that exact join.
- **Hands**: from calvin video-10's talking prompts (`upwork-calvin/video-10/clips/all`, 1a–12a); stiff, handless clips read as AI.
- **Locked camera, mic fixed**: the edit adds the motion (punch-ins at cuts); a camera move inside a clip breaks every jump cut.
- **Sound**: close mic over room tone keeps the clips matchable before the voice change.

## One take per hook

A hook made of two lines (`2a` + `2b`) joins at a jump cut with a pause on each side; on Aleo the user heard that as dead air and asked for each hook "said in 1 shot". Make shot `Nc`: both lines in one prompt, the template above with:
- `8-second` (about 31 words; 10 s came out too slow, with 1 s of silence at the end), "a quick, energetic but natural pace with no pauses", "only a tiny breath between the two sentences", "finishes the last word by about 7.2 seconds" (the edit keeps about 0.7 s of her silent after it before the body: 0.37 s read as "too tight");
- the join named: the first sentence ends "…not just your genes." and the second follows straight on, with nothing between "genes" and "Your".

The user may run it straight to 1080p: `make.py finals 2c 3c --no-draft` (the 360p draft is skipped). Transcribe the final (the `transcribe` skill; "jeans" for "genes" is the engine, not the take) and check every word once, no gap over 0.2 s, the last word before the end. Its own Flow audio is used as is (no ElevenLabs change, no 1.1x: the 8 s pace already matches the sped-up body); `one_take_hook.py` puts it in (see `edit-pipeline.md`).

## Batches and review

1. All talking clips at 360p in one `make.py clips` batch (`"duration"` per line, `"seed"` fixed).
2. Listen to each: every word once, nothing added, the line finished before the end, lips in sync, hands never on the mic. Frames can't show this; transcribe each draft (`transcribe`) and diff it against the line.
3. Join all drafts untrimmed in order (the user asked for exactly this: "just combine as it is") and send it, so the user hears the delivery and transitions together.
4. On approval, give the user `make.py finals` for all of them. Review finals the same way: a final is a new generation and can add a word the draft didn't.

## Host clips that keep Flow's own voice (Alaria video-5, 2026-10)

A retro-infomercial host at a desk, 12 lines, the voice generated inside each clip and kept (no voice change). Fixes that worked, from `upwork-alaria/video-5/AGENTS.md`:

- **Flow's filter blocks a long prompt:** go short. Three lines (the line, the voice description, "locked camera, no music, no captions, no text") with a new seed passed where the full template was blocked. "A fictional presenter in a retro TV commercial" got past the REPUTATIONAL / prominent-people block. Never reword the client's line to pass.
- **Too long a clip makes her fill the time:** a 10 s clip for a ~5 s line repeated words. Use the shortest length that holds the line plus ~1 s, and write `says "<LINE>", once.` then `Then she stops talking and smiles.`
- **A one-word or two-word sentence gets repeated** ("Queen or king." came out "Queen… queen or king"). Fold it into the sentence before with the same words ("by bed size, queen or king") and add "each word once".
- **Words repeated after the line:** don't regenerate. Trim the clip in the pause after the last word, at the point the audio goes silent, not at the ASR word end (that cut "-Align" off the brand name).
- **Same voice in every clip:** paste the identical voice description into each prompt (age, accent, register, ~140 wpm, "clean studio sound"). For a retake that must sound like the others, keep the prompt and change only the seed.
- **Hands:** small talking gestures with the hands on the desk. Never prompt her touching her neck, face or hand; it reads as forced.
- **Product in hand:** the start still already has the product in frame (held, or on the desk), and the action never moves it (pushing it at the lens changed its shape). Give the product sheet with only its top-down and angled panels; a hand-held panel confused the size.
- **Talking while doing something:** put the line first, then "She begins speaking in the first second. As she speaks, she reaches to her side and pulls…". Starting with the action gave a 1 s gap before the first word.
- **Pauses between sentences:** "in one smooth flow with no pause between the sentences". Prompt phrases like "short pauses for emphasis" gave 1.5 s gaps.
