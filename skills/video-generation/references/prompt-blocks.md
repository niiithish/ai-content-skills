# Prompt Blocks

Contents: block-by-block spec · style placement map · special protocols · worked example.

Use only the blocks the shot needs. A plain naturalistic clip may skip COLOR GRADE, WARDROBE, and OUTPUT SETTINGS entirely and fold those notes into LIGHTING and POSITIVE LOCKS. A graded multi-segment piece earns the full stack. If the user supplies their own block text, use it verbatim.

## Block spec

```text
SCENE CONTEXT
[1-2 sentences: what happens, where, when. Geo-position of every character.]

ACTIVE REFERENCES
[@tag + short anchor of critical details + "100% matches the reference"]

LOCATION MAP
[Foreground / midground / background, where the camera sits, where light enters, movement paths. Naturalistic colour can live here.]

FIRST FRAME / BLOCKING
[Who is where in frame one: position, orientation, gaze. Composition rule for this scene. Everyone already moving at frame one.]

FORMAT MODE
[Oner, sequential cuts, or timed multishot with explicit HARD CUTs.]

OPTICS
[Shot size + FOV in degrees per segment + lens character. Multishot adds "no drift mid-segment".]

CAMERA
[Operator behaviour: height, distance, movement, focus. Camera-body tonal character as a look, never a model name.]

ACTION
[Events at the precision the shot needs. Camera motion and subject motion stated separately.]

PERFORMANCE
[Acting plus skin micro-realism: muscle-level emotion, eye-line, catch-lights, breath, pore-level detail. Texture and shine only — do not introduce scars, moles, beauty marks, or freckles that the character reference does not have.]

PHYSICS
[Mass, inertia, contact shadows, fluids, particles.]

LIGHTING
[Source, direction, exposure, key/fill, haze. Priority block — never omit.]

COLOR GRADE
[Only when the grade is strong or stylized. Palette as material + light beam + compositional role.]

WARDROBE
[Only when costume matters. Material + condition, scene-logical.]

AUDIO
[Only the sound or line actually needed. Ambient only for silent b-roll.]

STYLE
[Technical suffix: overall look in words, photoreal, format, grain.]

OUTPUT SETTINGS
[Resolution, aspect ratio, anamorphic, real-time vs slow-mo per segment.]

POSITIVE LOCKS
[Short positive fixers against the likely failures, restating critical info once. Continuity lives here.]
```

## Style placement map

Descriptive style sits inside the block it describes. Technical style forms a suffix before POSITIVE LOCKS. Nothing style-related opens the prompt.

| Aspect | Home block | Write |
|---|---|---|
| Lighting | LIGHTING | source, direction, exposure, key/fill, haze for this scene |
| Colour / grade | COLOR GRADE, or folded into LOCATION + LIGHTING when naturalistic | palette as material + light beam + role |
| Lens character | OPTICS | FOV degrees, rectilinear or anamorphic, prime character, motion blur |
| Camera tonality | CAMERA | tonal latitude, highlight roll-off, colour science as a look |
| Skin realism | PERFORMANCE | pores, capillary flush, living eyes, catch-lights, visible breath |
| Acting | PERFORMANCE | micro-pauses, precise eye-line, restraint, muscle-level emotion |
| Physics | PHYSICS | gravity, inertia, mass, contact shadows, fluids, particles |
| Composition | FIRST FRAME / BLOCKING | framing rule for this scene |
| Continuity | POSITIVE LOCKS | characters, props, environment identical across cuts |
| Wardrobe | WARDROBE | material + condition, scene-logical |
| Format, grain, fps | STYLE + OUTPUT SETTINGS | resolution, grain, real-time vs slow-mo per segment |

## Special protocols

**Extreme-FOV multishot (8 degrees or 107 degrees).** All four mechanisms are required or the sequence breaks down after two or three beats: one location reference across every beat; an explicit FOV phrase opening each beat; an FOV confirmation closing each beat; colour expressed through material and light rather than a list.

**Whip-pan timing.** Settle, blur, settle — and never compress the blur below 0.8s.

```text
0.3s — subject A settled
0.8s — WHIP motion-blur transition
1.4s — subject B settled
```

**Cracks and breaks with no impact point.** "The crowd presses, it does not strike", "fracture originates from edge stress", "pressure-based crack", timed edge-to-centre rather than radial from a point.

**Mixed time speeds.** Hard cuts only between speed modes. One shot holds one speed start to finish.

**Observation / hidden-camera pattern.** See [optics.md](optics.md) — it needs three ingredients at once.

## Worked example

Two-cut product b-roll for a vertical ad, silent, character and product both referenced.

```text
SCENE CONTEXT
Late morning in a small tiled bathroom. A woman stands at the sink, rinsing her hands, a
thin gold chain at her throat. She is alone and facing the mirror.

ACTIVE REFERENCES
@image1 — woman, 26, medium-blonde hair loose to the shoulders, white ribbed cotton tank
top, light freckles across the nose. 100% matches the reference.
@image2 — flat gold herringbone chain, 5mm uniform width, ribbon-thin, worn snug about
2cm above the collarbones, flush to the skin. 100% matches the reference.

LOCATION MAP
Foreground: white ceramic sink edge and a running chrome tap, lower right. Midground: her
torso and throat, square to the mirror. Background: a soft-focus tiled wall and the mirror
frame. Daylight enters from a window off frame left. Camera sits just right of the mirror
axis, on the shadow side.

FIRST FRAME / BLOCKING
Frame one is already in motion: her hands are under the running water, head tipped
slightly down, the chain catching a highlight at the base of her throat. Framed jaw to
collarbone, chain on the lower third.

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
chain. Wide tonal latitude with soft highlight roll-off so the wet gold keeps detail.

ACTION
Camera holds steady. Her right hand lifts from the sink, water sheets down her neck and
over the chain, the chain shifts 3mm and settles flush again. On the cut, water beads bulge
at the lower edge of the links and release.

PERFORMANCE
Neutral practical expression, lips closed, one slow blink. Visible pores and a faint
capillary flush along the jaw, real skin shine rather than filtered smoothing.

PHYSICS
Water follows gravity down the neck and pools at the collarbone hollow. The chain carries
its own weight, keeps a soft contact shadow against the skin, and beads roll rather than
cling.

LIGHTING
Soft daylight from frame left at 5600K, gentle key on the throat, natural fill bouncing off
the tile, specular pinpoints tracking along the wet gold.

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
