# The master still

One still (`scenes/scene-1/scene-1-vN.jpg`) holds the speaker, her clothes, the set, the mic, the light and the exact crop. Every talking clip is generated from it, so everything that must never drift is decided here. Write it with `photoreal-video-production`'s still blueprint (`real_world_still` JSON) and add what follows.

## Ingredients

- **@image1, identity only.** An approved face of the speaker (Aleo video-3: the doctor from `upwork-calvin/video-10/scenes/scene-2a/scene-2a-v12`). Say what to take (face, hair, skin) and what not to (its doors, framing, pose, light).
- **@image2, the client's reference video frame**, for framing, camera distance, set, light and mic layout only. Name what must not come across: the reference person (her hair, glasses, face), any caption box or text.

This is the one still that may take a reference frame: there's no sheet for a set seen in one framing.

## What the prompt must pin down

- **Canvas numbers**, measured on the reference frame: top of head ~14% down, eyes ~33% down, face large and centred, shoulders out of frame, the mic and pop filter filling the bottom ~30%. Without numbers the model adds headroom.
- **Where the mic sits** (pop filter slightly left of centre, gooseneck from frame right, mic top cut by the bottom edge). The clip prompt then says it never moves.
- **Clothes with nothing readable**: a plain coat, no embroidery; a badge turned ~40° away so only a blur of print shows. Readable text drifts from clip to clip and can name a real person.
- **Hands out of frame** in the still; the clips bring them in.
- **Mouth open mid-word, looking into the lens**, warm and earnest: a still of someone *talking*, not posing.
- **Light from objects in the room** (window behind on one side, soft frontal daylight from the phone side), neutral daylight, real skin, no beauty filter.
- **Negatives**: captions or any text, a readable badge, the reference person's look, the identity ref's set, a phone/ring light in frame, wide framing or headroom, hands holding anything, waxy skin, colour casts, CGI.

The full Aleo prompt is `upwork-max/video-3/scenes/scene-1/prompts/scene-1-v1.md`: copy its structure and swap the person, set and clothes.

## Gate

Show it in the chat and wait for approval. Look at it at phone size: is the face large enough to read emotion under a 720×500 insert box sitting over the mic area (y ~1240–1740 on 1080×1920)? The insert box covers the mic and chest, never the face, so the eyes must sit in the top 40%.
