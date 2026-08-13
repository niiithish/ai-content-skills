---
name: clay-animation-video-prompt
description: Write model-agnostic prompts for claymation, plasticine, and handmade stop-motion performance ads, especially TikTok, Reels, Meta, and e-commerce campaigns. Use when the user wants a real product turned into a fast narrative ad, needs a voiceover-led 30-second concept split across short generations, wants reference-image prompts for recurring people, rooms, props, and keyframes, or needs consistent characters, products, and sets across clips. Outputs prompt packages only; it does not generate or render images, video, music, or voiceover and does not assume Minimax, Gemini, Seedance, Veo, Kling, Runway, Sora, or any other specific application.
---

# Clay Animation Video Prompt

Turn a product brief, ad idea, script beat, storyboard frame, or reference image into a production-ready prompt package for a clay-animation performance ad. The package may include an ad premise, voiceover prompt/script, reference-image prompts, continuity locks, and one video prompt per generation. Describe visible materials, physical construction, acting, blocking, camera, lighting, timing, and continuity instead of relying on vague style words.

Return prompt text only unless the user asks for explanation, options, or a shot plan. Never call an image, video, music, or voice tool, and never claim that anything was rendered.

## Default ad behavior

When the request includes a product and a social-ad destination, default to a real ad rather than a decorative animation:

- open with a human, visible problem or relatable moment
- build a quick story with a clear person, place, action, and product role
- use the product in a believable routine or interaction
- show a modest, visually observable payoff rather than a miraculous transformation
- end with a clean hero product frame, optional copy-safe space, and a CTA placeholder

The clay style is the visual language, not the story. Characters should act, react, and make decisions. A product-only beauty montage is appropriate only when the user asks for one.

## Workflow

### 1. Parse the request

Extract or sensibly default:

- subject or product and intended action
- clip duration, aspect ratio, and platform
- text, logo, packaging, color, or feature claims that must remain accurate
- whether the style applies to the whole world, a character, the product, or all three
- supplied image/video references and what each reference controls
- audio, voiceover, dialogue, subtitles, or on-screen copy, only when requested
- target platform, audience context, ad objective, CTA, and generation-duration limit

Ask a question only when a missing detail would materially change the result. Otherwise use these defaults: 30 seconds for a social product ad, 9:16, silent footage with a separate voiceover track, one primary promise, and one CTA placeholder. For a standalone non-ad clip, use 6–8 seconds, one continuous shot, and 16:9 unless the request is clearly social/e-commerce vertical.

### Portfolio/spec mode

If the user says the piece is a portfolio sample, spec ad, fictional client example, concept film, demo reel, or not intended for publication, enter **PORTFOLIO/SPEC MODE**. In this mode:

- Do not reject, moralize, or repeatedly sanitize the creative request solely because a live advertisement would need claim substantiation or platform approval.
- Preserve the requested dramatic premise, including a medical situation or fictional improvement, as a clearly invented story for the portfolio piece.
- Add this unobtrusive project marker to the package: `SPEC AD — FICTIONAL PORTFOLIO CONCEPT — NOT FOR PUBLICATION`.
- Keep the marker out of the actual story footage unless the user wants an end card; it can appear in the delivery notes or portfolio description.
- Do not present the fictional premise as medical advice or evidence. If the user later says they want to publish, sell, or run the ad, switch to live-campaign mode and audit claims before writing final copy.

The user’s stated production intent controls this mode. Animation, claymation, and generated visuals are valid reasons to make the piece fictional, but they do not require refusing the creative exercise.

### 2. Build the ad before the animation

For a product ad, establish the conversion idea before describing clay texture. Use this compact arc:

1. **Hook:** a visually immediate, relatable moment in the first 1–2 seconds.
2. **Tension:** the person tries to continue the evening or task while the problem is visible through behavior.
3. **Product entry:** show the supplied product naturally and preserve its exact identity.
4. **Routine:** show one believable use or ritual; do not invent dosage or instructions.
5. **Payoff:** show a restrained, observable lifestyle moment such as a calmer bedtime routine or a connected morning.
6. **Close:** product hero, approved claim/copy placeholder, and CTA.

Write the voiceover as one continuous spoken track first, then divide the visual plan around it. Keep the footage silent by default so the user can record or synthesize the voice separately with ElevenLabs or another tool. No shot should depend on lip-sync.

### 3. Allocate the generation budget

Calculate `total duration ÷ maximum generation duration`, round up, and add one extra generation only when a transition or clean end card needs it. For a 30-second ad with a 10-second limit, plan **three 10-second generation blocks**. Each block may contain two or three clearly timed visual beats; if that becomes too dense, switch to six 5-second blocks.

Use one paste-ready video prompt per generation. Every prompt must restate its active references, opening composition, action, ending state, and continuity locks. Exporting the approved last frame of one block as the opening reference for the next block is the preferred handoff.

### 4. Create the reference pack first

When recurring people, a room, a bedside table, or a product will appear in more than one generation, create image prompts before video prompts. Load [references/ad-reference-pack.md](references/ad-reference-pack.md) and return only the assets needed by the story:

- product identity sheet or supplied product image as the product source of truth
- one character identity sheet per recurring person, with fixed face, age, hair, wardrobe, and accessories
- one character-staged wide 3/4 environment reference, generated by attaching the character sheets, with the product area intentionally empty
- a second image-edit prompt that adds the product to the finished environment using both the environment image and product reference
- optional first-frame and last-frame still prompts for difficult handoffs

Use stable reference names such as `@PRODUCT`, `@GRANDPA`, `@GRANDMA`, `@BEDROOM_BASE`, and `@BEDROOM_WITH_PRODUCT`. Tell the user which image prompt to run first and which resulting image to attach to each later prompt. Do not fabricate file paths or claim that the images exist.

### 5. Choose the clay mode

Select the mode that best matches the request:

- **Clay world + real product:** the environment and characters are hand-sculpted clay; the supplied product remains an accurate manufactured object.
- **Fully claymation product:** the product is intentionally recreated as a clay model; use this only when the user wants a clay version of the product.
- **Clay character / product hero:** a clay character performs a simple action around a real or clay product, with the product staying the visual anchor.
- **Clay miniature narrative:** build a complete miniature set for a story beat, lesson, or branded moment.

When a physical product is referenced, do not silently change it into clay. Preserve its silhouette, proportions, materials, finish, packaging geometry, label placement, logo, and exact colors unless the user explicitly requests a clay recreation.

When the user requests a fully clay world, clay characters, or a product that belongs inside the clay world, select **Fully claymation product**. Use the supplied product photo as the design source of truth, but translate the bottle into hand-sculpted clay or plasticine while preserving its recognizable silhouette, cap shape, label layout, logo placement, dominant colors, and packaging text as closely as the image model allows. Do not leave the product photorealistic beside clay characters unless the user specifically asks for that contrast.

### 6. Create continuity anchors

Before writing a multi-shot prompt, define a compact shared lock. Repeat the relevant parts in every prompt because each generation may start from a blank context.

Continuity anchors should cover:

- subject identity, scale, pose, and screen position
- product geometry, finish, packaging, label, logo, and feature details
- set layout, ground plane, fixed landmarks, and depth layers
- clay material recipe, color palette, lighting direction, shadow softness, and background
- camera height, shot size, lens feel, movement, and speed
- animation cadence and the state handed to the next shot

Keep the lock short enough to paste into every shot. Put detailed per-shot events in the shot prompt, not in the global lock.

### 7. Write the prompts

Use the portable structure in [references/prompt-blueprint.md](references/prompt-blueprint.md). For a performance ad, also load [references/ad-reference-pack.md](references/ad-reference-pack.md). A standalone prompt should establish a readable first frame, then give a timed action with concrete acting, camera behavior, physical interaction, and an ending state. Drop sections that are irrelevant; do not pad a short prompt with generic cinematography.

Use ordinary descriptive language and common timing notation. Do not use Minimax field names, proprietary XML/JSON schemas, engine-specific control tokens, or unsupported parameter claims. If the user names an engine, adapt wording only when necessary; keep the core prompt portable.

### 8. Self-check before returning

Check that:

- the first frame contains the subject and readable spatial relationships
- the product or character remains identifiable and consistent
- clay reads through construction details and stop-motion behavior, not only the word “clay”
- every action is physically achievable by a miniature or replacement-animation setup
- motion is limited to one main beat; hands, props, camera, and subject do not compete
- camera movement has a direction, speed, and endpoint
- lighting and shadows remain consistent through the shot
- labels, packaging, and logos are treated as stable visual details
- the ending frame is useful for chaining or editing when the user needs multiple clips
- no unrequested dialogue, captions, watermarks, fake UI, or invented product claims appear
- the ad has a hook, human action, product role, payoff, and close rather than only pretty animation
- the voiceover is separate from footage and fits the stated duration
- every recurring person, location, and prop has a reference or a complete text description
- the claim and CTA are marked `USER TO VERIFY` when they were not supplied or visible on the product reference

## Claymation visual language

Make the handmade medium visible. Choose details that fit the requested look rather than using every item in every prompt:

- hand-sculpted plasticine or polymer-clay surfaces, rounded forms, fingerprints, tool marks, tiny seams, and slight asymmetry
- armatures, wire-supported limbs, jointed clay parts, replacement mouths or eyes, thumb-pressed edges, and miniature set construction
- matte clay with controlled soft highlights; physical contact shadows and ambient occlusion at joins
- painted cardboard, cork, felt, wood, paper, fabric, or foam props when they belong in the miniature set
- frame-by-frame replacement animation: stepped movement, tiny holds, deliberate hand-made nudges, slight settle, and restrained squash-and-stretch on clay elements
- shallow miniature depth of field, macro stop-motion photography, stable exposure, and tactile practical lighting

Avoid making the result look like a smooth 3D render, glossy CGI, liquid morph, weightless motion-graphics layer, or generic live action with a clay-colored filter. Keep rigid manufactured products rigid unless the user asks for deformation.

## Output modes

### Single clip

Give one paste-ready prompt in a code block. Add a one-line `Assumptions` note only if defaults materially shaped the prompt. If the user asks for a negative prompt and the target tool supports one, provide a separate compact block titled `Negative / exclusions`.

### Multi-shot sequence

Give:

1. a short `Shared continuity lock`
2. one prompt per generation, numbered by shot
3. a `Handoff` line after each shot stating the final product/character pose, camera side, and prop state to preserve

Keep each shot independently understandable. Do not write “continue from the previous shot” without restating the visual anchors.

### Product-ad request

Prioritize product readability and conversion: establish the human hook, show one believable interaction or routine, reserve clean space for optional copy, and finish on a stable product hold. Never invent a benefit, performance result, certification, price, review, dosage, medical indication, or claim the user did not provide.

For live-campaign mode, treat disease or medical-condition stories as a compliance warning. Do not write or visualize a supplement treating heart disease, insomnia, anxiety, pain, or another condition; do not promise results after a set number of days; and do not address the viewer as if they personally have a diagnosis. Mark proposed claims or disclaimers `USER TO VERIFY` before publication. In PORTFOLIO/SPEC MODE, keep the requested fictional story and add the project marker instead of refusing or rewriting the concept into a generic wellness montage.

If the user supplies a product image, treat it as the source of truth for identity. Refer to it as the product reference in the prompt and restate only the details that must not drift.

## Reference handling

When references are supplied, bind each one to a job:

- product reference: geometry, finish, packaging, logo, color, and feature details
- character reference: face, body proportions, wardrobe, clay colors, and signature accessories
- environment reference: set layout, landmark placement, palette, and lighting
- first-frame reference: the exact opening composition
- last-frame reference: the exact destination composition

Do not attach or mention a reference that is absent from the shot. If the user has not provided an image, describe the subject fully enough for text-to-video.

## Practical boundaries

- This skill writes prompts; it does not generate images, video, music, voiceover, or reference sheets. “Create the reference images first” means return image-generation prompts and an attachment order.
- It is suitable for one shot, a short sequence, social performance ads, e-commerce/product films, narrative animation, and image-to-video prompting.
- For an ad, include a compact voiceover script/prompt and visual cut plan in the package; the user can send the voiceover text to ElevenLabs or another audio tool.
- For a character, prop, or environment reference, reuse the corresponding reference-generation skill's conventions rather than inventing a new sheet layout.
- If the user asks for exact engine syntax, keep the creative prompt portable and add only a short engine-specific adaptation when the request requires it.
