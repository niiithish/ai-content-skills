# Beat map

Load this when a winning ad arrives as a video, screenshots, or a spoken script. Do not write stills or clips until the beat list is agreed, unless the user already has the script and just wants the next still.

## What to steal vs change

Steal:

- spoken cadence and beat order
- camera grammar (waist-up present, zip close-up, overhead pack, side-organizer)
- hand jobs (pinch zip, press sides, point at a pocket, lift by handles)
- when the product opens, turns, or gets a hard cut

Change:

- talent face / body / wardrobe unless they keep the same creator
- product identity, colorway, logo, openings
- nouns the new product or still cannot show
- brand claims that are not true for the new listing

Do not clone trademarks, on-screen usernames, or the original product's logo.

## Break the ad

Number the winning ad as:

| # | Spoken line | Camera | Hands / product state | Still needed | Clip length |
|---|---|---|---|---|---|
| 1 | quoted line | waist-up / zip / overhead / etc | what the hands do | yes/no | 4s or 6s |

Rules:

- one still per distinct camera + product state
- one clip per still unless they asked for a hard cut between two stills
- 4s if the line is about 8 words or fewer; 6s if longer or a 4s take already clipped
- drop a beat if the new product has no matching feature (no fake palettes, no fake extra pouch)
- rewrite a noun rather than forcing the old script onto the new still

## Working script

Keep one spoken script in `scripts/` as the current lines, not the original draft. Update it when a still forces a rewrite.

After clips exist, the transcript in `clips/CLIP_INDEX.txt` is the source of truth, not the user's first paste.

## Project notes to lock early

Write these once and reuse them in every later prompt:

- talent: age, ethnicity label they used, hair, wardrobe
- voice: American English, fast yappy
- product: color, material, openings, exact logo text + metal color
- room: table, wall, light
- engine: Gemini Omni, 720p, 9:16
