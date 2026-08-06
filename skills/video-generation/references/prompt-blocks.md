# Prompt blocks

Use only blocks the shot needs. Naturalistic clips may skip COLOR GRADE, WARDROBE, OUTPUT SETTINGS and fold notes into LIGHTING + POSITIVE LOCKS. User-supplied block text is used verbatim.

## Block template

```text
SCENE CONTEXT
[1–2 sentences: what happens, where, when. Geo-position of every character.]

ACTIVE REFERENCES
[@tag + short anchor of critical details + "100% matches the reference"]

LOCATION MAP
[Foreground / midground / background, camera seat, light entry, movement paths.]

FIRST FRAME / BLOCKING
[Who is where in frame one: position, orientation, gaze. Composition rule. Already moving at frame one.]

FORMAT MODE
[Oner, sequential cuts, or timed multishot with explicit HARD CUTs.]

OPTICS
[Shot size + FOV in degrees per segment + lens character. Multishot: "no drift mid-segment".]

CAMERA
[Height, distance, movement, focus. Tonal character as a look — never a model name.]

ACTION
[Events at needed precision. Camera motion and subject motion stated separately.]

PERFORMANCE
[Muscle-level emotion, eye-line, catch-lights, breath, pore-level skin. Texture and shine only — no scars/moles/freckles the character reference does not have.]

PHYSICS
[Mass, inertia, contact shadows, fluids, particles.]

LIGHTING
[Source, direction, exposure, key/fill, haze. Priority — never omit.]

COLOR GRADE
[Only when grade is strong. Palette as material + light + role.]

WARDROBE
[Only when costume matters. Material + condition, scene-logical.]

AUDIO
[Only sound actually needed. Ambient only for silent b-roll.]

STYLE
[Technical suffix: look in words, photoreal, format, grain.]

OUTPUT SETTINGS
[Resolution, aspect ratio, real-time vs slow-mo per segment.]

POSITIVE LOCKS
[Short positive fixers against likely failures. Continuity lives here.]
```

## Style placement

Descriptive style lives in the block it describes. Technical style is a suffix before POSITIVE LOCKS. Nothing style-related opens the prompt.

| Aspect | Home block |
|---|---|
| Lighting | LIGHTING |
| Colour / grade | COLOR GRADE, or LOCATION + LIGHTING if naturalistic |
| Lens character | OPTICS |
| Camera tonality | CAMERA |
| Skin realism + acting | PERFORMANCE |
| Physics | PHYSICS |
| Composition | FIRST FRAME / BLOCKING |
| Continuity | POSITIVE LOCKS |
| Wardrobe | WARDROBE |
| Format, grain, fps | STYLE + OUTPUT SETTINGS |

## Special protocols

**Extreme-FOV multishot (8° or 107°)** — all four required: one location reference every beat; FOV phrase opening each beat; FOV confirmation closing each beat; colour via material + light.

**Whip-pan** — settle, blur ≥0.8s, settle:

```text
0.3s — subject A settled
0.8s — WHIP motion-blur transition
1.4s — subject B settled
```

**Cracks with no impact** — pressure/edge stress language; timed edge-to-centre, not radial from a strike.

**Mixed speeds** — hard cuts only between speed modes; one speed per shot.

**Hidden-camera** — see [optics.md](optics.md); needs all three ingredients.

## Worked example

Two-cut product b-roll, vertical ad, silent, character + product referenced.

```text
SCENE CONTEXT
Late morning in a small tiled bathroom. A woman stands at the sink, rinsing her hands, a
thin gold chain at her throat. She is alone and facing the mirror.

ACTIVE REFERENCES
@image1 — woman, 26, medium-blonde hair loose to the shoulders, white ribbed cotton tank
top. 100% matches the reference.
@image2 — flat gold herringbone chain, 5mm uniform width, ribbon-thin, worn snug about
2cm above the collarbones, flush to the skin. 100% matches the reference.

LOCATION MAP
Foreground: white ceramic sink edge and running chrome tap, lower right. Midground: her
torso and throat, square to the mirror. Background: soft-focus tiled wall and mirror
frame. Daylight from a window off frame left. Camera just right of the mirror axis, shadow side.

FIRST FRAME / BLOCKING
Frame one already in motion: hands under running water, head tipped slightly down, chain
catching a highlight at the base of her throat. Framed jaw to collarbone, chain on the lower third.

FORMAT MODE
Timed multishot. Cuts only at the specified points, the camera does not cut on its own.
0.0s to 3.0s — she cups water and runs a wet hand down her throat across the chain.
3.0s HARD CUT
3.0s to 5.0s — macro on the chain as water beads and runs off the flat links.

OPTICS
Segment one: MCU at 29 degrees, portrait compression, shallow but readable. Segment two:
ECU at 12 degrees, tele-detail on the chain surface. No drift mid-segment.

CAMERA
Handheld at chest height with a 1cm tremor, holding 60cm from the subject, focus riding the
chain. Wide tonal latitude with soft highlight roll-off so wet gold keeps detail.

ACTION
Camera holds steady. Right hand lifts from the sink; water sheets down her neck and over
the chain; chain shifts 3mm and settles flush. On the cut, water beads bulge at the lower
edge of the links and release.

PERFORMANCE
Neutral practical expression, lips closed, one slow blink. Visible pores and faint capillary
flush along the jaw; real skin shine, not filtered smoothing.

PHYSICS
Water follows gravity down the neck and pools at the collarbone hollow. Chain carries its
own weight, soft contact shadow against skin; beads roll rather than cling.

LIGHTING
Soft daylight from frame left at 5600K, gentle key on the throat, fill from tile, specular
pinpoints along the wet gold.

AUDIO
Running tap and light room reverb only.

STYLE
Photoreal handheld phone-camera footage, fine natural grain, no stylized grade.

OUTPUT SETTINGS
9:16 vertical, 1080x1920, real time throughout.

POSITIVE LOCKS
The chain stays flat, ribbon-thin and warm gold in both cuts, snug above the collarbones
and flush to the skin. Ears stay bare. The tank top stays white ribbed cotton. Her lips stay
closed. The tap keeps running in both cuts. Daylight keeps arriving from frame left.
```
