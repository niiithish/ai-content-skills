# Song craft: lyrics, music direction and generating the song

A song ad fails when it's a voiceover with a beat under it (prose, no rhyme, no return). Write something a person would hear out.

## Lyrics

- **Lines of 4–10 words, one image or idea each.** One line becomes one shot of about 2–4 s. Pair shorter lines; split longer ones. `song.py lyrics` flags both.
- **Rhymed couplets, loose soul rhymes** (walked / talk, arm / turned, "going down / coming back around"), not tight pop rhymes that bend the story. Keep a steady meter within a section so the melody can repeat.
- **One refrain that returns 2–4 times and changes meaning.** The winners are sung-through stories, not pop songs with a chorus every 30 s, but a hook phrase always comes back and flips: "scratch, scratch, scratch" becomes "the scratching just got quiet"; "Some women just dry up" becomes "Some women don't dry up". Build the refrain from the insult or the wound, and flip it at the vindication. Mark every return "same melody as refrain 1".
- **Backing answers in parentheses:** a choir or backing voice repeats the key word ("(dry up)", "(she didn't brace)", "(Mysa)"). They make it sound performed and give the editor cut points.
- **Specifics in every verse:** names, ages, numbers, places, days ("Tuesdays she drove me to chemo, Thursdays she drove to him"). Dialogue in quotes, from other characters.
- **Spoken lines are allowed** for the pivot ("So here's what happened"), the sharpest dialogue and the offer. Mark them `[Spoken]`. Keep them few; most of it is sung.
- **The punchline of the climax is sung big**, alone, with space around it. It's the line the whole ad exists for.
- **Brand names spelled for the singer.** Speech-to-text heard "Resilia" as "Rizzilea". Spell it phonetically in the lyric if the model mispronounces it, and check it in every take.
- **Sheet format** (what `song.py` reads): `[Section — direction]` tags on their own line, `{music cues}`, `(backing answers)`, `[Spoken]` before a spoken line. Lead lines are everything else.

## Music direction

Measured on the nine reference songs (librosa: tempo, key per third, loudness in ten bins):

- **Tempo 86–143 BPM, constant for the whole song.** None change tempo. Lift the climb with a double-time feel, handclaps or a stomp, not a new BPM.
- **Energy curve:** the opening sits at about half the peak loudness, builds through the story and peaks at 60–90% (the product and the climb). Several drop for the soft pitch and rise again for the tag.
- **Minor to major at the solution** in some: one goes from F minor to A♯ major in its last third, another from F♯ minor to D major after the product. Use the key change as the sound of the reframe landing, and optionally a step up at the climax.
- This measures structure, not melody or timbre. The user hears the takes; you don't.

Write an energy line (`intro 3/10 → verses 4–5 → refrain 6 → bridge 3 → product 7 → climb 8 → climax 10 → pitch 4 → tag 2`) and a section table: section, length, key, energy, style tags.

**Genre follows the sub-avatar.** From the references and Starpop's map:

| Audience | Genres |
|---|---|
| Black American women or men, 40+ | soul, gospel, R&B, neo-soul |
| Women 40+, RV or rural | country ballad, soft pop, throwback pop |
| Teens, Gen Z women | acoustic pop, pop, R&B, indie pop |
| Millennials | pop, indie pop, R&B, alt-pop, indie rock |
| Pet owners | folk, indie pop, country |
| Wellness | indie folk, soft acoustic |
| Latino market | reggaeton, Latin pop, bachata |
| Short, light ads | upbeat musical theatre, Disney-style |

**Style prompt:** for Suno, use the style template under "Generating the song". The genre, vocal and BPM come from here. Elsewhere: under 25 words, `[genre], [lead vocal: gender, age, texture], [BPM], [mood arc], [production]`. Never an artist or band name (Suno rejects it, and it's a likeness problem). Example: `soul gospel ballad, raw smoky female alto with gospel choir, 74 BPM, heartbreak to triumph, warm vintage live-band production`.

## Generating the song

The user picks every take by ear; you can't hear it, so hand takes over without judging the taste.

### Suno (default)

On Mysa video 6 the user compared both tools and took Suno: "this turned out so much better". The method comes from a singing-ads guide the user follows as written ("why think when someone has a good system"), so don't add to it. Make it on a **paid Suno plan**: songs from the free plan can't be used in ads.

Paste in Create → Advanced:

- **Style:** the template, filled in, short, positive words only. A negative ("no intro") backfires. The approved one:

  ```text
  short commercial jingle, acoustic pop, 136 BPM, mature female vocal, warm and confident, clear diction, brand name sung clearly, vocals start at 00:00, no build-up, memorable hook, tight ending
  ```

  The guide's template: `short commercial jingle, [GENRE], [BPM] BPM, [VOCAL: gender + tone], clear diction, brand name sung clearly, vocals start at 00:00, no build-up, memorable hook, tight ending`. Its starting tempos by genre: hip-hop 100–110, pop 118, R&B 120, hype 126, playful 112, warm acoustic 92 (match the reference ad when there is one; Mysa used 136).
- **Lyrics:** the approved lyrics word for word, under plain section tags only: `[Verse]`, `[Chorus]`, `[Outro]`, `[End]`. No descriptions inside the tags, no exclude-styles list, no timed section directions. Put the brand name on its own line ("…from a company called / Mysa"). Our lyric sheet's `{music cues}` and `(backing answers)` stay out of the paste.

A failed take: fix only that piece. Respell a mispronounced brand name phonetically (hyphens, the stressed syllable in capitals) and regenerate only its section.

### ElevenLabs Music (only when asked)

The guide's short-tag method failed on ElevenLabs (`eleven_music_v2_5`): it ignored the asked length (3:00 instead of 30 s), opened with a 30 s instrumental intro, left long gaps between lines and sang one line four times at the end. ElevenLabs needs its own long, timed prompt:

Use it only when the user asks for ElevenLabs. What got a 3:53 song approved there (Mysa video 6), before Suno beat it:

1. **Decode the reference.** Gemini listens to the first 60 s of the client's reference ad with [gemini-audio-decode.md](gemini-audio-decode.md) and writes an ElevenLabs prompt, a negative list and lyric-phrasing notes. Its BPM and key are only roughly right (it called an F-major take minor): measure them with librosa and correct the prompt.
2. **A 30 s test of the hook,** one generation. Adjust and retest until the user likes one. A prompt Gemini decoded from a second "expression" reference came out mostly music with hardly any vocal: one reference at a time.
3. **The full song in one run.** Copy the liked test prompt **word for word** (rewording it loses the sound) and add **timed section changes**: big, specific contrasts with timestamps, e.g. "0:55–1:40 breakdown: drums and bass drop out, half-time, fingerpicked guitar and cello only, hushed breathy confession", "2:05 key change up a whole step, mandolin, handclaps", "2:45 sudden pull back, almost whispered", "end: back to one guitar". Repeat each change in its lyric section tag (`[Verse 3 - breakdown, drums and bass drop out, ...]`), and add "never one repeating loop" and "the same groove all song" to the avoid list. A loose "the arrangement builds as the story goes" gave one loop and one vocal tone for four minutes.
4. **Never stitch:** a body generated apart from the hook comes back in another tempo and key. Generate hook and body together.

The approved full-song prompt, for the shape (it opens with the liked hook test's prompt, word for word, then the timed changes):

```text
Light acoustic pop from the 2010s, 136 BPM, straight 4/4 feel in F major. Vocal-led: the lead vocal is loud and upfront, and the music is a quiet, sparse bed far beneath it, about half the vocal's loudness. The lead is a mature female vocal in her 50s, clean, crisp and confident, mid-register chest voice, extremely close-mic'd, virtually no reverb, compressed so every word is clear. Fast conversational talk-sung delivery, notes cut short at line ends with almost no gaps. Polished, dry and intimate, narrow mix. This is a story song, so the arrangement, melody and her emotion change clearly every section, never one repeating loop. 0:00-0:35 starts instantly with the vocal and one soft, lightly strummed acoustic guitar, then a soft bass and gentle kick and rim click, breezy and confident. 0:35-0:55 playful muted piano stabs join, she sounds amused. 0:55-1:40 breakdown: drums and bass drop out, half-time feel, only fingerpicked guitar and a soft cello, she drops to a hushed, breathy, vulnerable confession with a wry tired laugh. 1:40-2:05 hope: piano arpeggios and bass return, she warms up and smiles. 2:05-2:45 key change up a whole step, brighter, with mandolin, gentle kick and soft handclaps, her voice clear, warm and more melodic, joyful with tambourine. 2:45-2:55 sudden pull back to a ticking muted guitar and low bass pulse, tense and almost whispered. 2:55-3:35 sassy groove with finger snaps and walking bass, playful and confident, peaking at the climax line as the fullest moment with a warm backing harmony, still never loud. 3:35-end settles warm and direct, then back to one strummed guitar and a soft knowing smile, ending on a final soft chord. Avoid: loud instruments, full drum kit, crash cymbals, electric guitars, minor key, long intro, instrumental breaks, heavy reverb, synth pads, drum machines, long sustained notes, vocal runs, the same groove all song.
```

**What the user rejected, every time:**

- Loud music. Always write that the lead vocal is loud and upfront and the music is a quiet, sparse bed at about half the vocal's loudness.
- Dragged or held notes, slow tempos (68 BPM) and gaps between lines. The winner was fast, conversational talk-singing, notes cut short at line ends, close-mic'd and dry.

**ElevenLabs connector** (`eleven_music_v2_5`, node type `music`): `lyrics_type: custom`, `instrumental: false`, `lyrics`; leave `duration_seconds` out for a full song (the model chose about 3:55). **Always pass `generations_count: 1` to `creative_run_flow_nodes`**: the default is 4, at about 1,800 credits each. Never wire an approved take into the node's audio reference port: the rest of the song came back as plain voiceover with almost no music. The composition plan (per-section styles) and inpainting (re-singing only the hook, for hook variants) are API-only: they need an ElevenLabs API key or the web editor.

**ElevenLabs Music API or web editor** (composition plan): one song up to 10 minutes, in up to 30 sections of 3–120 s. Each section gets its own lyrics, duration and positive/negative styles, so the key changes, the drum drop and the double-time climb can be written per section. Give global styles plus the section table. Check the current field names in ElevenLabs' docs before writing JSON for the API; in the web app, paste section by section. It also inpaints one section, useful only as a last resort for a single line. Test first: generate the first three sections (about 75 s) and check the lead stays the same singer across section boundaries.

**Checks on a take before it's used:**

- Every lyric line is sung, in order, with no words dropped or repeated. `plan.py voiceover` marks any line it can't find in the audio: listen to those.
- The brand name is sung correctly.
- The climax line lands clearly.
- Vocals start in the first second, and the ending has a 2–5 s instrumental tail for the end card.
- The lead is one singer throughout.
