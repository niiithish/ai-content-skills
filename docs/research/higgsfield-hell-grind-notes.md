# Research notes: Higgsfield / Hell Grind patterns

Working notes so we don't lose usable ideas for our skills (`character-generation`, `prop-generation`, `environment-generation`, `video-generation`, `script-generation`).

**Captured:** 2026-08-06  
**Branch context:** cleanup/lean-skills  
**Sources:**

| Source | URL | What we got |
|---|---|---|
| Hell Grind project brief (Cinema Studio) | https://higgsfield.ai/generate?projectId=3caa2f3a-52b5-4293-9237-0c8f76c7158a&brief=1 | Full public brief text via `agent-browser` |
| Hell Grind fight rebuild (Adil) | https://www.youtube.com/watch?v=s-eeHOkkLss | EN auto-subs via `yt-dlp` |
| Car commercial full workflow (Adil) | https://www.youtube.com/watch?v=GNxmt_4IifA | EN auto-subs via `yt-dlp` |
| 1-min 4K short film workflow (Adil) | https://www.youtube.com/watch?v=HSON-SoFz7s | EN auto-subs via `yt-dlp` |

**How to re-fetch later**

```bash
# Brief (public shell + brief body; login unlocks more)
agent-browser --profile Default open "https://higgsfield.ai/generate?projectId=3caa2f3a-52b5-4293-9237-0c8f76c7158a&brief=1"
agent-browser wait --load networkidle && agent-browser wait 3000
agent-browser read

# YouTube transcripts
yt-dlp --skip-download --write-auto-sub --sub-langs en -o "notes/%(id)s.%(ext)s" \
  "https://www.youtube.com/watch?v=s-eeHOkkLss" \
  "https://www.youtube.com/watch?v=GNxmt_4IifA" \
  "https://www.youtube.com/watch?v=HSON-SoFz7s"
```

---

## 1. Big picture (what actually mattered for them)

Hell Grind production problems they say they solved:

1. Faces / identity drift shot to shot  
2. Spaces falling apart when camera moves  
3. Voices drifting  
4. Scene geography lost between cuts  
5. **Root cause they name:** video models have **no memory** — incomplete descriptors → new face/jacket every gen  

Their five compressed rules (brief conclusion):

1. **Assets first** — lock & stress-test character/location/prop before any shot  
2. **Describe everything, every time** — full descriptor in every prompt, never shortened  
3. **Change one thing at a time** — one line per iteration; log everything  
4. **Give the model less freedom** — corner not whole room, anchor not open space, map not guesswork, one action per shot  
5. **If a shot won't land, simplify the shot, not the words** — split, remove an action, change angle  

**Already aligned with us:** assets pipeline (character / prop / environment → video), rigid video blocks, positive phrasing, 3/4 environments, grey studio sheets, natural skin texture.

---

## 2. Character patterns

### Hell Grind sheet layout (different from ours — note, don't force)

They use **three images**, not our two-panel landscape sheet:

| Panel | Content | Why |
|---|---|---|
| 1 | Large face close-up | Only place model should pull identity from |
| 2 | Full body **front with head removed** | On wides, model was stealing face from tiny full-body figure (blurry). Headless front forces face from the CU |
| 3 | Full body back | Rear wardrobe / silhouette |

**Our skill today:** left = outfit only (ghost mannequin, no body), right = shoulder-up portrait. Same *problem class* (identity vs wardrobe separation), different layout.

### Keep the sheet boring on purpose (strong match with us)

From the brief — keep / reinforce:

- **Neutral grey** background  
- **Flat / soft studio light**  
- **Real skin, visible pores, no retouch**  
- Do **not** bake film grain, cinematic lenses, or heavy grade into the sheet — that look belongs in **locations + video prompts**. Baked cinema look makes the character stop reacting to new light  
- Prefer **large portrait in 3/4** (face slightly turned) over dead-on — they claim models read these better  

**Conflict to decide later:** our default is **facing camera** shoulder-up. Hell Grind prefers **3/4 large head**. Worth an optional toggle, not a silent default flip (user preference).

### Skin / face selection

- Pick the **most believable** face, not the prettiest. Beautiful-but-fake shows up later in video  
- **Catch-lights in eyes** required even on dark eyes — dead eyes kill acting in video  
- Natural pores / no beauty filter (matches our updated no-mole / real bare-skin rule)  
- Their Style Prefix still mentions "asymmetric moles" for *video* skin realism — **we deliberately do not invent moles** on character sheets; natural texture only  

### Point edits, never full re-gen of locked face

Rule: **an image never runs through a model twice in full.**

Workflow they used:

1. Point-change (jacket / scar / blood) on a copy via image model  
2. Mask composite only the changed region onto the locked original  
3. Original skin texture survives  

After two full passes: face goes symmetrical, plastic, lifeless → hurts video acting.

### Separate asset per state (high value for prop + character)

Do **not** mix states in one text descriptor:

| Bad | Good |
|---|---|
| one `@roco` text mixing dry / wet / bloody | `@roco`, `@roco_wet`, `@roco_blood` each with own sheet + text |
| one location "any weather" | day / night / rain as **three** location assets |
| one prop description for all shots | prop variants by camera need |

**Prop example (artifact):**

1. Full crystal — close-ups  
2. Small bloodied — palm reveal  
3. "Hidden" — clenched fist; prompt forbids showing crystal, allows only blue light between fingers  

### Behavior + voice locked in pre-pro (script/video adjacent)

- One **behavior paragraph** per hero before shooting: hands, habits, eyes under pressure, how they break  
- Scene adapts posture; core never changes  
- Physically impossible habits are **transferred**, not deleted (pacer on sofa → sway / finger-tap)  
- Voice descriptor fixed and pasted every time the character speaks (register, tempo, accent, manner)  

### Extras / crowds

Don't ask for "a crowd." Build **distinct character classes** (e.g. heavy brute + light scout) for silhouette variety and cross-shot consistency (fight rebuild video).

### Car-commercial character tips (GNxmt_4IifA)

- Product/hero stills on **neutral grey** for later composite  
- Name assets consistently (`@car_sheet`, etc.) so Claude + Cinema Studio auto-attach  
- Don't force one model to do everything: Soul Cinema for alive performance → face-swap identity in a second pass if needed  
- Cut face out of full body as a cheap head reference (credit save)  
- Character **not looking at camera** for many commercial beats  

---

## 3. Environment / location patterns

### Strong match with `environment-generation`

Already in our skill:

- Wide **3/4**, not frontal wallpaper  
- Spatial plan, landmarks, pathways  

Hell Grind adds / reinforces:

| Tip | Detail |
|---|---|
| **3/4 not frontal** | Frontal pretty plate → flat wallpaper on wides; model invents past the edges |
| **Anchor object** | Column, lamp, sofa — stage to it: "hero at the lamp, facing the door" beats "hero in the room" |
| **One light logic** | One source, one shadow direction, never two suns |
| **Front + back location sheets for action** | Snow plain: front with crimson tree **and** empty back view so model doesn't invent what's behind |
| **Fog as cleanup** | Cap visibility (e.g. 20 m) to hide far-field glitches in dense scenes |
| **GEO / LOCATION MAP block** | Floor plan in words, locked across every shot of a scene — landmarks, left/right **from camera**, meters, axis the camera never crosses. No heroes/action in GEO — pure place |
| **Location ref role ban** | When tagging location in video: *"do not use as starting frame, do not inherit composition, angle, or grade — take only space and texture"* |

### Reverse angles (two methods)

1. Generate another corner of same room in still model, match soft focus of original  
2. **Empty location walkthrough video** (camera slowly moves through space) → screenshot needed angle → still model improves texture/light. Full location coverage from one sheet  

### Lazy vibe pass then lock palette (car ad)

1. First location prompt deliberately lazy (vibe + colors only)  
2. Lock color transfer / palette for the project  
3. Then write specific geometry (glass wall, orange accent wall as photo placement anchor)  

### Clean plate when model invents furniture

If phantom booths/rows appear: erase in image editor, re-save as clean location element.

### When you can skip a location asset

For one-off backgrounds simple enough for the video model, describe in prompt only (4K short film video). **Reused or multi-shot places still need sheets.**

---

## 4. Prop patterns

| Tip | Source |
|---|---|
| Multi-view prop sheets (they use GPT Image 2 often) | Both ads + brief |
| **Neutral grey product backdrop** always | Car ad — easier to drop into any scene |
| **Four-view** truck / complex products | 4K short film |
| Split prop states by shot need (full / palm / hidden) | Hell Grind brief |
| **Arrow on prop sheet** pointing at the exact control/button the hand must hit — model follows the visual cue | 4K short film |
| Pre-generate readable text props (newspaper) with big headlines; small text pre-blurred so model doesn't invent mush | Car ad |
| Landing physics for flying props (cap lands on asphalt in wide) instead of "doesn't vanish" | Car ad |

---

## 5. Video prompt skeleton (compare to our `video-generation`)

Hell Grind / CINEDANCE order (brief):

```
SCENE CONTEXT          (incl. "EXACT N CHARACTERS — NO DUPLICATES")
ACTIVE REFERENCES      (tags + role + short physical summary)
LOCATION MAP / GEO     (locked spatial map for the scene)
FIRST FRAME / BLOCKING
FORMAT MODE            (oner vs hard cuts, duration)
OPTICS
CAMERA                 (what it does and never does)
ACTION TIMING          (seconds)
PHYSICS
LIGHTING               (one source logic)
AUDIO                  (voice descriptors + lines; SFX only)
CHARACTER ACTING       (want, hide, body rhythm)
STYLE                  (Style Prefix pasted verbatim)
QUALITY
POSITIVE CONSTRAINTS   (counts as what IS present — "exactly ONE mannequin")
```

**Our skill is already very close.** Useful deltas:

| Their add | Why it matters |
|---|---|
| `EXACT N CHARACTERS — NO DUPLICATES` header | Stops extra people / clones |
| Explicit **furniture counts** as positive constraints | Model clones props |
| **Name role of every @tag** (`for character reference` / `for location reference`) | Stops wrong inheritance (composition vs face vs palette) |
| **Style Prefix** pasted **word-for-word** every prompt | Continuity of look |
| **First ~1s always a wide that only locks positions** | Stops teleports; optional tail of previous VO line for seam glue |
| Left/right always **from camera**; positions in **meters** from landmarks | Model doesn't understand "left of hero" well |
| Action timing in **half-seconds** for staged rises | Model can't rush stages |
| Camera math over adjectives (`8m → 4m`, `3× faster than a dolly pull`) | Models understand comparisons better than "dramatically" |
| Match-cut lock: end pose of shot A = start pose of shot B | Without it, cut = new scene |
| Physics for impacts (angles, "crystal always beats steel") | Better than "epic clash" |
| Transformations as **weapon deploy in 0.4s**, not magic power-up | Avoids anime glow |

### Positive only (they relearned the hard way)

Negative prompting failed for the monster arm-blade ("no hand holding a sword" → still drew a hand). Fix: **raise the arm so the model must see the blade grow from the elbow.**  
Same lesson in fight cleanup: replace "no cheap VFX" with the lighting/texture you want.

### Multi-shot vs oner for "cinematic vs game"

Long unbroken action from a floating third-person camera → game cutscene feel.  
Fix: **hard cuts** with distinct optics per beat (e.g. 50mm orbit / 24mm low / 85mm CU / 35mm wide).

### Batch discipline

- Generate **batches of 4** to tell glitch vs prompt failure  
- Know **broken prompt** vs **bad roll** — only rewrite when pattern fails across the batch  
- Steal best segments across takes (open from gen1, middle from gen2…)  
- **Tighter frame = less slop** (traffic, intersections, dense overtake often unfixable — crop them out)  
- Shot 1 as **blocking lock** when multiple people keep teleporting  

### Scale writing

Giant figures: human comparison + absolute rules ("silhouette at least 5× human height"; frame cannot hold feet and head at once).  
Armies: **three layers** (sharp front warrior, dense mid, silhouettes in mist) — never "show 1000 samurai."

### Audio / VO (differs from our silent-default ads)

Hell Grind used Seedance speech, cleaned in post, SFX only in prompt, **no generation music**.  
Our ad skills stay **silent + VO over** by default — keep that. Steal only: ambient continuity + "SFX only, no music in gen."

---

## 6. Style Prefix (Hell Grind — for reference only)

They paste this verbatim at the end of every video prompt. **Do not paste into product ads blindly** (cinematic / against-the-light / moles language conflicts with UGC product work). Useful as a pattern of *what a reusable style lock looks like*:

```text
Style: 8K IMAX. Photorealistic — no 3D render, no game engine, no game-cutscene aesthetic.
Cinematography: floating immersive camera that lives with the actors; natural motivated light;
painterly composed frames, strong silhouettes against the light.
Lighting: Natural light only — contre-jour backlight, camera on shadow side, atmospheric haze.
Key light from sky and windows only.
Color: 60:30:10 — dominant / secondary / accent.
Camera: Physical cine lens. 180° shutter motion blur.
Skin: Pore-level realism — vellus hair, asymmetric moles, capillary flush, pore-shadow matching on-set light.
Acting: Hollywood — micro-pauses before reactions, precise eye-line, wet living eyes with catch-lights,
visible breath and chest rise.
Physics: Gravity and inertia respected — mass has real weight, correct contact shadows. No floating props.
Composition: Rule of thirds + golden ratio. Every person moving from frame one.
Continuity: Characters, props, environment identical across every cut. No identity drift.
Technical: 24fps smooth motion. 8K detail. No jitter.
Audio: Environmental SFX only. No music. No subtitles.
```

**Adapt carefully:** we want natural skin **without inventing moles**; product ads often need frontal/side key not pure contre-jour; silent default.

---

## 7. Acting rules (steal for video PERFORMANCE / script beat notes)

- Write **behavior and want**, not emotion labels ("sad")  
- Muscle-level: jaw set/release, breath pattern, blink phases (lazy → double → hard reset)  
- Gaze direction or darting eyes always  
- Micro-event every 1–2s so faces don't freeze  
- Stillness = **held tension**, never "nobody moves" (that freezes the frame)  
- INNER (unspoken) intention lines for action stretches  
- Progressive fight for the goal: joke → fail → push → fail → beg as **visible** posture/tempo changes  

---

## 8. Production / org tips (not skill text, still useful)

- Folder per scene; subfolder per asset type; iteration subfolders  
- Save every locked asset as named **Element** + tell Claude the same name  
- Canvas as single workspace so nothing gets lost  
- Edit in parallel with generation; reshoots are cheap — cut aggressively; trim first/last ~0.5s of every clip  
- Cleanup pass **before** color: fingers, boiling texture, fake sign text  
- Color unifies generations (each gen has its own baked grade); look already lives in location assets  
- Shared continuous ambience glues shots even when picture drifts slightly  

---

## 9. Map: what to consider for *our* skills later

Do **not** apply yet unless we choose to. Preserve existing creative choices (two-panel character, dark-grey, no moles, silent ads, etc.).

| Skill | Already good | Candidate upgrades (optional) |
|---|---|---|
| **character-generation** | Grey studio, natural skin, no invented moles, ghost outfit panel, opacity locks | Optional 3/4 head angle; stress-test note (10 gens); catch-light reminder; "boring sheet / no cinema grade"; separate sheets per wardrobe state |
| **prop-generation** | 3–4 views, grey, no labels | Explicit state variants (full / in-hand / hidden); grey composite-friendly note; optional "mark feature with arrow" for interaction shots |
| **environment-generation** | Wide 3/4, spatial plan | Anchor object language; one light logic callout; front+back for action sets; reverse-angle / empty walkthrough method in references |
| **video-generation** | Block order, positive phrasing, FOV table, silent default, short tags | EXACT N characters header; tag **roles**; location "space/texture only" ban; GEO map as first-class; 1s blocking wide; camera math; match-cut pose lock; furniture counts |
| **script-generation** | Cut list, env changes, muted test | Behavior profile paragraph per talent; note when a shot needs a new character **state** asset |

---

## 10. Tools attached to Hell Grind (names only — not pulled yet)

Brief mentions these as project attachments (may need login / download from project):

- `CINEDANCE HIGGSFIELD SKILL.md` — video prompt writer/auditor  
- `ACTING SKILL.md` — performance writing  
- `LIRA SKILL.md` — image prompts / model weak points  
- Full production brief, team guide, 11-stage pipeline, slop gallery, shotlists  

If we get login or file exports later, dump them under `docs/research/hell-grind-attachments/`.

---

## 11. Quick "steal first" shortlist (highest leverage, low conflict)

1. **Asset = text descriptor + image**, descriptor repeated every video prompt  
2. **Separate asset per state** (wet/blood/day/night/prop variant)  
3. **Location 3/4 + spatial anchor + one light** (we mostly have this)  
4. **Tag roles** + location "texture only, not starting frame"  
5. **GEO map locked per scene**  
6. **First second = wide position lock**  
7. **Positive counts** ("exactly 3 people, exactly 1 mat")  
8. **Iterate one failure at a time** after reading the batch  
9. **Boring grey character/product sheets**; cinema look in video  
10. **No full double-pass** on locked faces — mask composites for wardrobe/damage  

---

*End of notes. Prefer updating this file when we pull more Hell Grind attachments or re-watch with better transcripts.*
