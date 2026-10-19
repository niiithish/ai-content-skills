---
name: inner-world
description: "An action-packed inside-the-body sequence for a 3D or clay supplement ad: the product enters the body as a little hero (a softgel ship, a golden spray), fixes a visible problem (dry layers, a biofilm wall, a blockage) and the world turns from dull to glowing, with a moving camera and built transitions in and out of the room. Use ONLY when the user explicitly asks for an inner-world or inside-the-body sequence in this style, or types /inner-world. Never for IRL or photoreal videos. Never on your own initiative, and never when the client's reference video shows its own inside-the-body look: copy that instead."
disable-model-invocation: true
---

# Inner world

A short inside-the-body sequence (3–5 clips, 1–2 s each in the edit) that turns the product's mechanism into a mini action movie. Learned from a Facebook ad the user liked (`references/breakdown.md`, Gemini's shot-by-shot breakdown of it) and tested on Mysa Sea Buckthorn (`references/look/`, 2026-10-19).

It sits inside the normal pipeline: plan the shots with `video-plan`, make stills and clips with `animated-video-production` (or `clay-video-production`) through Flow. This skill only decides what the inner shots show and how they look and move.

## When not to use it

- **IRL or photoreal videos:** never. There the product's "inside" is macro shots of the real softgel, oil and skin.
- **The reference video has its own inside-the-body look:** copy the reference. This look is for when there is no reference, or the user asks for it.
- **Not every video needs one.** One sequence per ad at most, where the voiceover explains how the product works.

## What makes it entertaining

1. **The product is a hero with a mission.** It travels (a softgel flying like a ship, a jet of golden oil), reaches the problem and does something visible to it.
2. **Problem → fix you can see.** The "sick" world is dull and dark (grey-beige dry layers, maroon blobs, tar); the fix turns it warm, plump and glowing. Pick the product's own mechanism from its page (Mysa: "thin dry layers rebuild thick and moist with omega-7").
3. **The camera never rests.** Fly-throughs, chase cams, barrel rolls, lunges into a target, pull-backs. Speed ramps: slow drift, then a sudden lunge.
4. **Jumps in scale.** Room → into the softgel or the eye → millimetre-tall world → back to the room.
5. **Built transitions,** never plain cuts in and out of the body (below).

## The look (3D)

Paste this into every inner still prompt, after the shot:

```text
Look: high-end 3D macro CGI of a stylized inner-body world, the same polished feature-animation CG as a Pixar-style film but at microscopic scale: clean luxury skincare and supplement commercial CGI. Every tissue surface looks like warm translucent silicone, soft peach wax, pearlescent blown glass or liquid honey, with heavy warm subsurface glow, strong backlight from the centre depth of the frame, crisp warm-white rim highlights, shallow macro depth of field with creamy foreground and background bokeh, and dozens of tiny out-of-focus golden dust motes and micro-bubbles floating in the volume. The viewer feels a few millimetres tall. Full-frame immersive interior view: the tissue walls and soft out-of-focus foreground shapes fill all four edges of the 9:16 frame; no empty background, no void, no floating island, no diorama, no cutaway object on a backdrop. Never gory: no blood, no veins, no organs, no slime; never a flat medical diagram; not 2D, no outlines. No text, no captions, no labels, no watermark.
```

- **Palette:** "sick" = dusty beige, grey-peach, maroon `#7A2234`, tar `#2B0710`; "healed" = peach-pink `#F2A98E`–`#FFE4D6`, amber `#D97706`, gold `#FBBF24`, white-gold `#FFFBEB`. The frame gets brighter as the fix lands.
- **The product** keeps its real look (pass a product photo as an ingredient): the Mysa softgel stayed the exact ruby-amber gelatin.
- **Clay:** the same story, beats and camera, but the world is sculpted clay and translucent resin under the same warm backlight; state that in the look block instead of CGI materials.
- Materials, light and motion in detail: `references/breakdown.md` section 2.

## The shots

A typical sequence (the Mysa test, `references/look/`, prompts beside each still):

| Clip | Shows | Ends on |
|---|---|---|
| Into the body | her face behind the softgel held up close; the camera lunges into the softgel | golden oil filling the frame |
| The problem | fly-through over the dull problem world, flakes and cracks; the product appears far away | the product glowing in the centre |
| The mission | chase cam behind the product; it heals what it touches, then bursts | a white-gold burst |
| The fix | the healed world, plump and glowing, still changing; camera pulls back | a warm white-gold glow |
| Back out | (room clip) her, transformed, in sunlight with golden sparkles | — |

Every clip prompt times the action in seconds. Clips 6 s; the edit uses 1–2 s of each.

## Transitions: generate them, don't build them in the edit

**A transition is part of the generation.** The two scenes on either side of it are ONE Flow clip of 8–10 s, with the move between them happening inside the shot: one unbroken camera path that flies through the softgel, the eye or the burst into the next world. Pass both stills as ingredients: `@image1` is the exact first frame, `@image2` is the world the camera arrives in. Time it: scene 1 for 3–4 s, the fly-through 1–2 s, scene 2 for the rest. Say "no cut, no fade, no flash, no dissolve; the transition happens inside the shot". Example: `references/look/c12-softgel-into-dry-layers.md` (2026-10-19, worked first take: kitchen → into the softgel → a swirling golden tunnel → out over the dry layers).

This overrides the one-still-per-clip rule of `animated-video-production` for transition clips only. The second scene holds up because inner worlds have no faces to drift; a room scene with characters after the transition drifts more, so keep its part short or cut away from it.

**Don't fake it in FilmCraft.** A zoom, blur and flash over a cut (tested on the same pair) only looks like a zoom and a flash; the generated fly-through is what the reference does. FilmCraft cuts only between clips that already end and start on matching frames.

The transition moves, from `references/breakdown.md` section 3A:

1. **Into an object:** the camera flies into the softgel, the eye or the belly and through it into the tunnel.
2. **Through a floating cutaway:** a sphere of the inner world floats in the room and the camera pushes into it. **The floating sphere appears in that one bridge shot only.** Every shot inside is full-frame, never an island on a backdrop.
3. **Body → body:** lunge into a target until its colour fills the frame, and come out in the next place.
4. **Out by burst:** the fix explodes into white-gold light that clears to the room, golden sparkles drifting around her.
5. **Out by shape:** a golden sphere in the centre pulls back to become the softgels in her palm.

## Labels on screen

The reference's HUD words (LOCKED, CLEAR, FLUSH) make it feel like a game. Generate clean plates and add the labels in the edit (FilmCraft text), never in the prompt: Flow misspells them.

## Traps

`references/breakdown.md` section 3C. The main ones: a floating island or diorama on a void (use the full-frame line in the look), gore, a textbook diagram, a metal spaceship instead of the gelatin softgel.
