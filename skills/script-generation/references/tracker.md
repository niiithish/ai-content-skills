# Tracker

For any project spanning more than a couple of clips, write a single markdown file at the project root and keep it current as work progresses. It survives context loss, prevents regenerating approved clips, and gives the user one place to see what is left.

Update it in the same turn as the work it records. A stale tracker is worse than none.

## Template

```markdown
# [Brand] — [Product] · AI UGC Ad

[Aspect ratio] [platform]. [N] generations (~[N]s) handing off to [ending].
Voiceover generated separately and laid over silent video.

## Product facts

- [spec, sourced from the product page]
- NOTE: [any contradiction in the source, and how the script avoids it]

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

Use `todo`, `written`, `generated`, `approved`, or `regenerate — [reason]`. Recording the reason matters: "regenerate — came out 16:9" tells the next session exactly what to fix, while "regenerate" does not.
