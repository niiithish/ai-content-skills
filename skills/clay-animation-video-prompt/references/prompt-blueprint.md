# Portable Claymation Prompt Blueprint

Use only the sections needed for the request. The order is optimized for video models that need a clear subject and first frame before motion.

```text
SCENE / PURPOSE
What the ad beat is for, what is visible, and the one idea the viewer should understand. For a social ad, name the hook, product role, payoff, and CTA destination.

REFERENCES
Name each supplied reference and what it controls. Preserve identity, geometry, labels, and spatial landmarks.

FIRST FRAME / BLOCKING
Opening shot size and camera viewpoint. Place every visible subject from the camera's perspective: foreground, midground, background, left, right, and center. State what the product or focal subject is facing and where its key feature is visible.

CLAY WORLD / MATERIALS
Handmade clay construction, miniature set materials, physical seams and joints, scale cues, and the requested clay mode. Keep a real product manufactured when required.

ACTION / TIMING
One main beat or a small set of explicitly timed beats. Describe replacement-animation increments, pauses, contact, weight, settle, and any limited squash-and-stretch. Keep background motion subordinate. Use `HARD CUT` only at stated times; if a block is too dense, split it into another generation.

CAMERA
Shot size, camera height, angle, focus priority, motivated movement, direction, speed, and endpoint. Keep the camera physically plausible for a miniature stage.

LIGHTING / COLOR
Key direction, softness, fill, practical sources, palette, and shadow behavior. Lock exposure and white balance for the shot.

AUDIO (ONLY IF REQUESTED)
Ambience and tactile clay or miniature-set SFX only. For a social ad, provide a separate voiceover timing note; voiceover is added in edit and is not spoken by the on-screen characters. Otherwise state silent footage.

OUTPUT
Duration, aspect ratio, frame cadence or stop-motion feel, generation-block number, whether the last frame should hold for chaining, and `SPEC AD — FICTIONAL PORTFOLIO CONCEPT — NOT FOR PUBLICATION` when portfolio/spec mode is active. State the engine limit when supplied.

POSITIVE LOCKS / EXCLUSIONS
Short high-value constraints: preserve identity, readable label, stable product proportions, clay texture, approved copy only, and the requested shot/cut behavior. Add a separate negative prompt only when useful for the target tool.
```

## Motion vocabulary

Prefer measurable actions:

- “moves in three small replacement-animation increments, pauses, then settles”
- “the clay hand presses the button; the finger compresses slightly and rebounds”
- “the product stays upright and rigid while the clay set changes around it”
- “a paper backdrop slides a few centimetres on a hidden track, creating gentle parallax”
- “hold the hero product for the final 1.2 seconds with the label facing camera”

Avoid relying on “fluid,” “magical,” “dynamic,” or “cinematic” without saying what visibly moves and how.

## Product-ad anchor checklist

For a real product, explicitly lock as applicable:

- silhouette and proportions
- material and finish
- dominant and secondary colors
- logo and exact label placement
- cap, lid, buttons, ports, seams, or distinctive hardware
- hero angle and readable feature
- size relationship to clay characters and set
- final hold and optional clean copy area

Never use clay texture, fingerprints, or squash-and-stretch on the real product unless the user asks for the product itself to be clay.

## Example shape

For a request such as “make a clay animation ad for this skincare bottle,” the prompt should establish: a hand-built clay bathroom or vanity set, the exact bottle as a rigid product reference, one simple interaction such as a clay hand placing it on a tray, a short push-in or lateral track, readable label facing camera, tactile replacement-animation timing, and a final product hold. It should not add unverified skincare claims or turn the bottle into a different package.
