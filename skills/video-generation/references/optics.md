# Optics

Contents: shot sizes · focal-length intent · FOV anchor table · optical recipes · camera, light and colour rules.

Two levers define how a shot reads: shot size and focal length.

## Shot sizes

| Abbr | Meaning | In frame |
|---|---|---|
| ECU | Extreme close-up | one detail: eyes, clasp, a link, a hand |
| CU | Close-up | full face or one element large |
| MCU | Medium close-up | head and shoulders |
| MS | Medium shot | roughly to the waist |
| WS | Wide shot | full figure plus surroundings |
| EWS | Extreme wide | scale, location |

## Focal-length intent

Use this to reason about the look while writing. Never put millimetres in the prompt.

| Lens | Effect | Use for |
|---|---|---|
| 24-35mm wide | space, slight perspective stretch | action, immersion, establishing |
| 50mm normal | natural perspective | realism, neutral coverage |
| 85mm portrait | soft bokeh, subject separation | portrait, emotion |
| 135mm+ tele | strong compression | observation, distance, sport |

## FOV anchor table

Put FOV in the prompt in degrees, using only these discrete steps. Not 23 degrees — pick 18 or 29.

| FOV | mm equiv | Purpose | When |
|---|---|---|---|
| 180 | fisheye | spherical distortion | POV, dream state |
| 107 | 14-16mm | architectural ultra-wide | large interiors, epic establishing |
| 84 | 20-24mm | wide | establishing, group blocking |
| 63 | 28-35mm | observational | reportage, wide observation |
| 47 | 40-50mm | neutral human perspective | universal establishing, medium |
| 29 | 75-85mm | portrait compression | medium isolate, dialogue bust |
| 18 | 100-135mm | natural portrait | close portrait, identity-preserving |
| 12 | 180-200mm | tele detail | hands, objects, product macro |
| 8 | 300-400mm | extreme compression | observation, broadcast |

In a multishot, set FOV per segment and add "no drift mid-segment".

**Placement.** The CAMERA block sits third among the core layers. At the end of a prompt its FOV gets ignored; at the front it conflicts with identity references.

## Optical recipes

**Observation / hidden-camera.** Needs all three at once, or it reads as a normal long lens: foreground occlusion covering 20-30% of frame and out of focus (wall, pillar, branch); atmospheric haze between camera and subject; a distance vantage at 8-12 degrees with the operator anchored far away. Change the occlusion type between beats, keep one vantage.

**Sports broadcast.** 8 degrees super-tele, handheld 1-2cm tremor, "anchored at distance, finding the action".

**Detail-on-wide (snake cam).** 84 degrees wide, low angle right up against a small object. Foreground exaggerates, background recedes.

**Intimate wide.** 63-84 degrees on a close face. Face centred, surroundings readable rather than blurred.

**Tele compressed air column.** At 8-12 degrees: "dust suspended in the long compressed air column between camera and subject", "heat shimmer compressed into a wall of haze in front of the figure".

**Product macro.** 12 degrees ECU, camera 20-30cm out, focus on the material's specular behaviour rather than its silhouette. State how light travels across the surface — that is what sells the material.

## Camera, light and colour

- **White balance in Kelvin**, matched to scene mood and fixed within the scene: 3200K tungsten, 4000K mixed, 5600K daylight, 8500K cool shade.
- **No equipment names.** Describe the look. Camera, film stock, and lens models get ignored or break complex moves.
- **Colour as material plus light beam plus compositional role.** "Crimson silk catching the cold tungsten spill from the corridor", never "she wears red and he wears blue".
- **Background in layers.** State foreground, midground, and background separately.
- **Camera on the shadow side**, with the operator axis stated explicitly.
