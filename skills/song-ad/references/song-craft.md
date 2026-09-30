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
- **Brand names spelled for the singer.** Whisper heard "Resilia" as "Rizzilea". Spell it phonetically in the lyric if the model mispronounces it, and check it in every take.
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

**Style prompt:** under 25 words, `[genre], [lead vocal: gender, age, texture], [BPM], [mood arc], [production]`. Never an artist or band name (Suno rejects it, and it's a likeness problem). Example: `soul gospel ballad, raw smoky female alto with gospel choir, 74 BPM, heartbreak to triumph, warm vintage live-band production`.

## Generating the song

The user generates the song and picks the take; you write what they paste. Generate the **whole song in one go**, several times (4–6 takes), and choose the best take by ear. Don't stitch sections from separate generations: music models aren't deterministic and the seams show.

**ElevenLabs Music** (composition plan): one song up to 10 minutes, in up to 30 sections of 3–120 s. Each section gets its own lyrics, duration and positive/negative styles, so the key changes, the drum drop and the double-time climb can be written per section. Give global styles plus the section table. Check the current field names in ElevenLabs' docs before writing JSON for the API; in the web app, paste section by section. It also inpaints one section, useful only as a last resort for a single line. Test first: generate the first three sections (about 75 s) and check the lead stays the same singer across section boundaries.

**Suno** (custom mode, so the lyrics are sung exactly as written): style box = the style prompt, lyrics box = the sheet with its `[Section]` tags. A long song won't fit in one prompt: split it at the bridge and use Extend for the second half.

**Checks on a take before it's used:**

- Every lyric line is sung, in order, with no words dropped or repeated. `plan.py voiceover` marks any line it can't find in the audio: listen to those.
- The brand name is sung correctly.
- The climax line lands clearly.
- Vocals start in the first second, and the ending has a 2–5 s instrumental tail for the end card.
- The lead is one singer throughout.
