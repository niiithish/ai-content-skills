# Tracker

Only when producing a multi-clip AI cut list. Skip this file for a spoken UGC script.

For projects with more than a couple of clips, keep one markdown file at the project root. Update it in the same turn as the work it records.

## Template

```markdown
# [Brand] — [Product] · AI UGC Ad

[Aspect ratio] [platform]. [N] generations (~[N]s) handing off to [ending].
Voiceover generated separately and laid over silent video.

## Product facts

- [spec from product page]
- NOTE: [source contradiction, if any, and how the script avoids it]

## Voiceover — [status], ~[N]s

Delivery: [accent, age, energy, tool settings]. Line breaks are breath pauses.

> [line]
>
> [line]

### Claims to verify before publishing

- [ ] [claim]

## Image assets

| # | Asset | Used by | Status |
|---|---|---|---|
| 1 | Character sheet | all | done |
| 2 | Product sheet | all | done |
| 3 | [environment] sheet | gen [X] | todo |

## Video clips

Hard rule: no single cut longer than [N] seconds.

| Gen | Cut | Beat | Environment | Len | Prompt | Generated | Approved |
|---|---|---|---|---|---|---|---|
| A | 1 | [beat] | [env] | 3s | todo | | |

### VO over cuts

| VO line | Cut |
|---|---|
| "[line]" | 1 |

## Continuity locks

Restate in every video prompt:

- [wardrobe]
- [product placement]
- [hair, light direction, anything that drifts]
```

## Status values

`todo` · `written` · `generated` · `approved` · `regenerate — [reason]`

Always record the reason: `regenerate — came out 16:9` helps the next session; bare `regenerate` does not.
