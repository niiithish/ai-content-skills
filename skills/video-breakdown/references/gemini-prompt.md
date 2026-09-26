Watch the attached video all the way through. Do not sample or skip. You are writing a remake bible: someone who never saw this video must be able to rebuild every cut in another AI image/video tool.

Return ONE JSON object and nothing else. No intro, no markdown, no trailing notes. If you must fence it, use a single ```json block and nothing outside it.

Schema (these keys exactly, schema_version 3):

{
  "schema_version": 3,
  "form": {
    "kind": "claymation_animation | talking_head_a_roll | live_action_b_roll | mixed | 2d_motion | 3d_cgi | other",
    "medium": "stop-motion clay / live action / 2d / 3d / mixed — be specific",
    "style": "dense paragraph of the WHOLE video's look: materials, scale, lighting grammar, color, how faces/hands/sets are built, grain, how real vs toy it feels",
    "voice": "who speaks, on-camera vs voiceover, gender, accent, pace, energy. If silent, say silent."
  },
  "meta": {
    "duration_sec": 0,
    "width": 0,
    "height": 0,
    "orientation": "vertical|horizontal|square",
    "premise": "one sentence: what the ad is arguing and selling"
  },
  "pattern": {
    "structure": "the repeating formula of the whole video, segment by segment: who appears, where, how each segment opens, how it builds, how it ends, how one segment hands over to the next",
    "hook": "exactly what grabs attention in the first 1–2 seconds: the image, the action, the first words",
    "why_it_works": "what keeps it engaging: how often something new happens on screen (in seconds), how big the actions are, how the camera moves, how the picture escalates within a segment",
    "worlds": "for each character or segment, its own setting and why it fits that character; say so plainly when every character has a different world"
  },
  "transcript": [
    { "start": 0.0, "end": 0.0, "text": "one spoken phrase, verbatim, include uh/um" }
  ],
  "scenes": [
    {
      "shot": 1,
      "start": 0.0,
      "end": 0.0,
      "form": "what THIS cut is, not the whole video: talking-head A-roll / live-action B-roll insert / claymation insert / product hero / diagram / cafe wide / ECU of hands",
      "purpose": "one clause: why this cut exists in the ad",
      "camera": {
        "framing": "ECU / tight torso / waist-up / full-body / wide set / overhead",
        "angle": "HEIGHT + ORBIT + which way the body/object faces, in one phrase. Height: eye-level / high / low / top-down. Orbit: front / three-quarter / profile (true side, 90°) / back / over-shoulder. Facing: into lens / frame-left / frame-right / away. NEVER write only 'eye-level'.",
        "move": "locked / slow push-in / pull-out / pan L|R / tilt / snap zoom. If a move happens, say WHEN in the shot (start / mid / last 0.4s). Still camera = locked.",
        "first_frame": "what the frame contains at the first frame, edge to edge, including orbit (side vs front vs 3/4)",
        "last_frame": "what the frame contains at the last frame if different; else same as first_frame"
      },
      "set": {
        "place": "where we are",
        "lighting": "direction, softness, color temperature, any practicals",
        "palette": "3–6 dominant colors",
        "materials_and_style": "clay / felt / wood / skin / plasticine fingerprints / knitted sweater — whatever is visible",
        "background": "layer by layer, front to back, every surface that is not a named element"
      },
      "characters": [
        {
          "id": "stable name reused across scenes, e.g. blonde-green-sweater / pill-figure / green-blob-left",
          "look": "full description: body material, hair, face, outfit, accessories. Enough to redraw them.",
          "start": "pose, expression, where in frame, what they touch",
          "end": "pose/expression/place if it changed; else repeat start",
          "action": "chronological: what they do during THIS cut only"
        }
      ],
      "elements": [
        {
          "name": "desk calendar",
          "look": "physical description: size vs hands, color, material, ANY printed/written text that lives ON the object",
          "where": "where it sits in the frame",
          "start": "state at first frame of this cut",
          "end": "state at last frame of this cut",
          "change": "the motion that gets it from start → end, who does it, with what. If unchanged: 'unchanged'."
        }
      ],
      "overlay_captions": [
        {
          "text": "exact string",
          "style": "case, color, outline/shadow, weight, roughly how large vs frame",
          "where": "top / upper-third / center / lower-third / bottom / left / right",
          "start": 0.0,
          "end": 0.0,
          "motion": "static / pop-on / slide-up / type-on / fade"
        }
      ],
      "still": "reverse-image prompt of the FIRST FRAME only. FIRST WORDS must be the camera lock (height + orbit + facing), e.g. 'eye-level true side/profile, subject faces frame-left, camera at 90° to the torso, not a front shot'. Then subject, body, wardrobe, materials, hands, every prop, pose, lighting, background layers, composition, medium. Do not describe later motion. NEVER mention, quote, or describe burned-in captions, titles, lower-thirds, stickers, watermarks, or any graphic text sitting on the picture.",
      "spoken": "verbatim speech that plays over THIS cut only. Empty string if none.",
      "build": "how the picture grows from the first frame to the last while the line is spoken: what is plain at the start, what appears or changes, and on which spoken words. Say 'no build' only if nothing changes.",
      "timeline": [
        { "at": 0.0, "words": "the words being spoken at this moment, or empty", "what": "first frame, fully described" },
        { "at": 0.0, "words": "...", "what": "each real change inside the cut: an effect appearing, a gesture, a camera move starting or stopping, an expression change" },
        { "at": 0.0, "words": "...", "what": "last frame before the hard cut" }
      ]
    }
  ]
}

HARD RULES

1. ONE scene object per HARD CUT / continuous take. Shot 1 starts at 0.0. Cover 0.0 through duration_sec with no gaps and no overlaps. Count shots, not cut events: N hard cuts after the opening frame = N+1 scenes. Number shots 1, 2, 3… in time order. Do not omit scenes to stay short.

2. NO top-level props, talent, or on_screen_text arrays. Every object, character, and graphic lives inside the scene where it is visible.

3. overlay_captions = burned-in graphic text only (TikTok/Reels captions, hook titles, lower-thirds, CTA stickers, username watermarks).
   NEVER put these in overlay_captions — they belong on that element's look / start / end:
   - text printed on a product bag, box, bottle
   - text on a calendar, laptop screen, door sign, poster, mug, book
   - text that is a physical prop in the world

4. Already vs becoming. Every element and character must say what is ALREADY true at the first frame vs what CHANGES during the cut.
   BAD: "a marked calendar" / "holding an open bag" / "zoom shot of the belly"
   GOOD: "Calendar already showing DAY 2, page clean, no pen marks." then end: "page has been flipped to DAY 7 and a red X is freshly scratched across it."
   GOOD: "Locked frame for 2.1s, then a slow push-in on the last 0.4s that fills the frame with the glass."

5. Camera move is NOT a new cut. A zoom, push-in, or pan inside a continuous take stays in the same scene and is written in camera.move + timeline.

6. Density. Each scene must be rebuildable. Name how many of each character; which hand, what it touches, hold vs a move; product/object open or closed, packed or empty, in the air / on the table / worn / floating; set dressing behind them; medium tells (clay fingerprints, iPhone grain, felt clothes, painted eyes). A 10-second hold with no visual change is still ONE scene — write the stillness, do not invent motion.

7. timeline must start at the scene's first frame and end at its last frame. Add a row only when something actually changes (hands, object state, pose, camera, overlay appearing/leaving). Do not write one row per second.

8. Transcript is the full spoken track, phrase by phrase, with start/end. Include uh/um. No speech → []. Do not also dump a combined string. Scene.spoken is ONLY the words heard during that cut.

9. Characters keep a stable `id` when the same figure returns in a later shot. New cast member = new id. Product-only shot → characters: [].

10. Numbers are numbers. Cuts = hard edits only. One continuous take = one scene. Do not call a continuous move a cut.

11. still is reverse image generation of the FIRST FRAME only. One paste-ready image prompt. Do not write a last-frame still — action + timeline already say what changes through the end of the cut.
    MUST NOT include overlay caption text — not the words, not "text that says…", not "caption in the center", not a watermark.
    Overlay text already lives in overlay_captions. still pretends those graphics were never on the frame.
    Text printed ON a prop (logo on a bag, DAY 2 on a calendar, WC on a door) MAY stay — that is the object, not a caption.

12. Camera orbit is not optional. Height (eye-level) is NOT the same as facing the lens.
    Look at the first frame and pick orbit from what is actually visible:
    - both eyes, both shoulders, chest square to lens → front
    - one eye + one cheek + one shoulder closer → three-quarter
    - one ear, nose/belly as a silhouette, only one side of the torso → profile / true side (90°)
    - back of head, back of sweater → back
    Left/right is the side of the FRAME the subject faces (frame-left / frame-right).
    Writing only "eye-level" is a failure. Defaulting a side or 3/4 shot to front is a failure.
    still MUST open with that lock so an image model cannot invent a front mugshot.
    BAD angle: "eye-level"
    GOOD angle: "eye-level profile, subject faces frame-left, camera 90° off the chest"
    BAD still: "Macro eye-level shot of a clay belly and two hands holding red flags"
    GOOD still: "eye-level true side/profile, subject faces frame-left, camera at 90° to the torso, not a front shot: clay figure seen from the side, large rounded belly in silhouette, unbuttoned purple knit sweater, both clay hands in front of the belly holding three small red triangular flags on thin sticks, soft side light, beige blur behind, stop-motion clay fingerprints"

13. Every scene has every key, every time. Use [] or "" for nothing, never drop a key. `still`, `build` and `timeline` are the most useful parts: never skip them to save space. A scene of 3 s or more has at least 3 timeline rows.

14. Tie picture to speech. When someone speaks during a cut, each timeline row says which words are heard at that moment, so a remake can time every effect and gesture to the same words.

15. Camera moves are as important as framing. A slow push-in, drift, arc or tilt that runs the whole cut is a move, not "locked". Write its direction, speed and when it starts and ends.

DENSITY EXAMPLE (calendar insert — match this level, do not copy the content)

If a cut is a desk calendar that starts clean and gets an X at the end:

- form: "claymation insert, overhead desk still-life, not talking-head"
- camera.angle: "high three-quarter, desk recedes toward frame-right — not a flat front elevation"
- camera.move: "locked"
- elements include the calendar AND the pen AND the desk
- calendar.start: "already open to DAY 2, cream page, no marks"
- calendar.end: "showing DAY 7, a crude red X scratched over the date"
- calendar.change: "pages flip forward (Day 2 → 6 → 7), then a clay right hand enters from the right with a red felt-tip and scratches the X once"
- overlay_captions: [] because DAY 2 / DAY 7 are printed on the prop
- still describes the FIRST FRAME only (clean calendar, no marks) as an image prompt. The flip and the X live in action/timeline, not in still. still does not mention a TikTok caption.
- timeline has: first frame / pages flipping / hand + scratch / last frame

If a later cut is a woman talking and a TikTok caption sits at the bottom, THAT string goes in overlay_captions. The word BIOMEL printed on the pouch does not.

Write every scene at that density. Missing a visible object, a start/end state, a camera move, or an overlay is a failure.
