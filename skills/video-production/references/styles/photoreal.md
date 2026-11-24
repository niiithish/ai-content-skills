# Style Module: Photoreal (`--style photoreal`)

Real-world ad scenes, lifestyle, and product B-roll under a voiceover. Must look like genuine camera footage, never AI-generated.

## 1. Sheets & Engine Routing

- **Character sheets:** Shared layout (`../sheets/character-sheet.md`). For realistic human character sheets, check `PROJECT_STATE.json` (`engines.sheets_human` — currently `Seedream 5.5 1K` via `elevenlabs-creative` is strong, though Flow's upcoming image model is expected to supersede it). Lock target demographics, age, and before/after appearance upfront.
- **Product sheet:** Always build from the client's real product photo (`--ref <photo>`, `../sheets/product-sheet.md`). Never invent a label from text.
- **No environment sheets by default.** Each location's **first approved still** acts as its look reference for later stills in that place (pass it as an ingredient for light/colour/room continuity only, and specify the new camera angle).
- **Continuous shots are chained edits:** When two consecutive shots show the exact same moment/table/props (e.g., picking up a glass and drinking), edit the first approved still rather than generating fresh from sheets so props don't vanish or morph. Check both stills side by side.

## 2. Visual Direction

- **Authentic real life:** Natural skin texture, pores, real fabric creases, motivated practical/window light, true-to-life color. No waxy skin, no unmotivated rim-glow, no hyper-symmetrical "AI ad" sheen.
- **Real-world placement:** Monitors face their user; glasses sit on tables; drawers have knobs on the front; products are at real human scale.
- **Mirrors:** Never draw a person and their reflection in the same frame (models hallucinate a second person). Aim straight into a full-length mirror filling the frame so only the reflection is visible, and negate "second copy of her, her real body in front of the mirror, camera/phone in mirror."
- **Eyelines & emotion:** Nobody looks into the lens unless the plan says so. Match facial expression to the exact VO line (worried on a problem line, relieved on a solution line).
- **Safe zone:** Keep key action in the central 70% of the 9:16 frame (clear of bottom/right social UI).

## 3. Still Prompt Structure

Use `../sheets/` + JSON/structured prompt fields (`prompt_type: real_world_still`):
- Name every ingredient's exact job (`@image1`: woman's face/hair/outfit, ignore grey sheet backdrop; `@image2`: product pack with exact quoted label text).
- State camera height, focal length feel (e.g., candid 35mm handheld phone or natural documentary lens — never name camera gear in clip prompts), foreground/midground/background, exact light source, eyeline, and hand/prop counts.
- **Other brands' products:** Give competing products believable colored fictional labels — never plain blank white bottles.

## 4. Clip Prompt Template (Flow Omni, 4/6/8/10 s)

Pass the approved still as `@image1` (reference image by default). Add a character/product sheet ONLY if a face is hidden/turns, someone enters, or printed product text moves.

```text
Vertical 9:16 real-world shot, matching @image1.

[1-2 sentences: who does what, matching the voiceover emotion.]

[For multi-step physical beats, time in seconds at normal real-life speed:]
0-[t] s: [...]. [t]-[t] s: [...]. [t]-[N] s: [...ending state].

[Counts & continuity: "Exactly one softgel, as in @image3; no others appear." "One sheet of paper on the desk the whole time."] [Eyeline: "She looks at the screen, never at the camera."]

Camera: a very slow, steady push-in, barely noticeable, same angle throughout. [Or: Static camera, exact framing of @image1; no cameras, tripods, or film gear anywhere.]
Natural real-life motion at normal speed, real skin and fabric. Ambient room sound only; nobody speaks, no music. No text, captions, or graphics on screen. One continuous shot, no cuts.
```

## 5. Photoreal-Specific Failure Locks

- **Swallowing / pouring / handing beats:** Always use 6 s with second-by-second timing and explicit object counts ("water level visibly drops by a third; softgel stays visible until lips close").
- **Cellulite / thigh / skin close-ups:** Describe the exact visual texture (soft wavy dimples vs. deep fibrous dimples) and place product on the **thighs** (never calves). If Flow triggers `PUBLIC_ERROR_SEXUAL`, switch that still to Seedream 5.5 and clip to Seedance 2.0 Mini / Kling 4.0 via `elevenlabs-creative` (with `9:16` and `quantity=1`).
- **Couple-in-bed safety blocks:** Night + pyjamas + bed triggers Flow `NOT_FOUND` / `PROMPT_REJECTED`. Stage in evening knitwear on a living room sofa, or route to `elevenlabs-creative` fallback.
- **Never name camera gear in clip prompts:** Writing "on a tripod" puts a physical tripod inside the scene. Write "Camera: static, exact framing of @image1."
- **Never freeze the whole clip:** Either write one subtle camera move (slow push-in/drift) or apply a slow zoom in `filmcraft-edit`.
