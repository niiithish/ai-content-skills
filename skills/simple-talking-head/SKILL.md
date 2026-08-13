---
name: simple-talking-head
description: >
  Write a short raw-iPhone 9:16 talking-head video prompt of a person saying one
  line. No product in hand, one continuous shot, selfie or tripod. Use when the
  user wants a talking video of someone, a woman/man saying a line, a UGC
  talking-head prompt, "she says" / "he says" with no winning ad to remake, or
  runs /simple-talking-head. Triggers: talking video, talking head, woman saying,
  man saying, he says, she says, holding the phone, selfie ugc, tripod talking
  head, no product in hand. Do not use to remake a winning ad, swap a product
  into a reference clip, or write silent cinematic b-roll — those are
  ugc-ad-remake or video-generation.
---

# Simple talking head

Write **one prompt** in a code block and stop. Do not generate the video unless they ask. Do not load **ugc-ad-remake**.

This is a person on camera saying one line. Not a remake. Not a product-in-hands demo.

## Figure out the person

| They give | Do |
|---|---|
| **she / her / woman / girl** | `she says` |
| **he / him / man / guy** | `he says` |
| **an image** | Infer she/he from the photo. Add one identity line: `the [woman/man] from the reference image`. Do not describe the whole face. |
| nothing | Ask once: she or he? If they already gave a line and just want the prompt, default **she**. |

Do not invent a name, age, or wardrobe. The tested lock is `american 20 year old ugc tone` — keep it unless they name a different voice.

## Camera

Pick **one**. Do not mix.

- They say holding the phone / selfie / front camera → **holding the phone**
- Anything else, or they do not say → **tripod**

## Write this (do not rewrite it)

Swap only `[she/he]`, `"[line]"`, and the optional identity line. Leave every lock.

### Holding the phone

```
[optional: the woman/man from the reference image]
natural and realistic arm movements, subtle lean forward, looks directly at the lens the whole time

[she/he] says in an american 20 year old ugc tone:
"[line]"

Ambient Sound. No cuts. No zooms. No transitions. Raw iPhone footage, expressive ugc movements, UGC aesthetic. Vertical 9:16. NO PRODUCT IN HAND. ONE CONTINUOUS SHOT
```

### Not holding the phone (tripod)

```
[optional: the woman/man from the reference image]
Static tripod shot, natural and realistic arm movements, subtle lean forward, looks directly at the lens the whole time

[she/he] says in an american 20 year old ugc tone:
"[line]"

Ambient Sound. No cuts. No zooms. No transitions. Raw iPhone footage, expressive ugc movements, UGC aesthetic. Vertical 9:16. NO PRODUCT IN HAND. ONE CONTINUOUS SHOT
```

If they did not give a line, ask for the line. Do not invent brand copy.

No product in the hands. Talking *about* a product is fine. If they want hands on a product, zip, or a remake of a winning ad → **ugc-ad-remake**.
