---
name: script-generation
description: Write short-form video ad scripts built for AI generation — TikTok, Reels and Shorts UGC, product ads, hooks, and voiceover copy delivered as a numbered cut list with a shot per cut. Writes voiceover over silent footage by default, with no on-camera dialogue, since generated lip-sync is unreliable. Use when the user wants a script, hook, ad concept, voiceover, or storyboard for a short vertical video, wants an existing script made faster or less ad-like, or is turning a product page into an ad. Trigger on phrases like "write a script", "UGC script", "TikTok script", "ad script", "give me hooks", "script for this product", "write the voiceover".
---

# Script Generation

Write short-form video scripts for **AI generation**, not live film. Deliver an **edit**: numbered cuts with spoken line + shot each, timed to engine clip limits.

A script that reads well as a paragraph but cannot cut into ~3s beats is a failed script.

## Non-negotiables

1. **Pace** — 2–3s per cut by default; never over 3s unless asked. A 30s ad is ~10+ cuts.
2. **Environment changes** — each cut moves somewhere new or shows something new. Six cuts in one room reads slow.
3. **No ambiguous pronouns** — when contrasting product vs worse alternative, every "these/it/they" has one referent (anti-confusion rule below).
4. **Zero ad voice** — no "introducing", "game-changing", "obsessed", or three-adjective stacks. If a person would not say it to a friend, rewrite.

## Workflow

1. Product truth from page/URL: material, differentiator, proof, guarantees. Skip contradictory claims rather than picking a side.
2. Awareness stage (table below) — decides the whole script.
3. Angle + hook. Patterns: [references/hooks.md](references/hooks.md).
4. Voiceover as one continuous spoken take, then break into cuts.
5. Shot + environment per cut.
6. Audit with [references/audit.md](references/audit.md) before showing the user.
7. Multi-clip projects: write tracker per [references/tracker.md](references/tracker.md).

## Awareness stage

| Stage | Viewer already knows | Script opens on |
|---|---|---|
| Unaware | no problem felt | relatable moment that names the problem |
| Problem-aware | pain, no solutions | agitate briefly, reveal category |
| Solution-aware | category, been burned | differentiate vs what they tried |
| Product-aware | this brand, not bought | proof, objections, risk reversal |
| Most aware | ready | offer + urgency |

**Solution-aware is most often misdiagnosed.** Owners of cheap versions do not need the problem explained — differentiate against past failures. Pivot: why the one they tried failed and this one does not.

## Anti-confusion rule

Viewer hears audio once. Any pronoun that could point at the product will be heard as the product.

Broken: *"I used to buy these constantly… Then your neck turns green."* → product sounds defective.

Fixed: *"Every gold chain I owned before this one died in about two weeks. Green neck, patchy plating, straight in the bin."*

Use all three: explicit noun phrase · temporal boundary ("before this one") · terminal past verdict. Villain prop must look **physically different** from the hero on screen, not just older.

## Structure (≈25–35s)

```
Hook            cuts 1–2    question or claim that earns 3 more seconds
Credibility     cut 3       specific detail that proves real use
Villain         cuts 4–5    what they tried, how it failed
Mechanism       cut 6       why this is built differently (physical terms)
Proof montage   cuts 7–9    claim shown, one environment per cut
Resolution      cut 10      understated payoff
Handoff         cut 11      into the offer (no price if offer clip attaches)
```

Hook: curiosity > claim; borrowed question ("someone asked…") > self-promotion. Mechanism: plain physical why, no contradictory specs. Handoff: mid-sentence setup when an offer clip follows; never speak price in the AI portion.

## Voiceover, not dialogue

Default: **voiceover over silent footage**. Nobody speaks on camera — lip-sync is the fastest AI tell.

- No cut depends on a face delivering a line
- Every cut has a visual event (muted test: still something to watch)
- Words and visuals are independent tracks
- Write VO as one continuous block first (line breaks = breath); note accent, age, energy if TTS
- If user demands talking-head: write it, but flag lip-sync risk and offer silent+VO

## Numbers and claims

Concrete beats vague ("four months" > "months and months"). Stay inside what the user can defend. Flag every claim to confirm before publish. Never invent review counts, ratings, or certifications.

## Output order

1. **Voiceover** — continuous block, breath breaks, delivery notes
2. **Cut list** — table: # · duration · line · shot · environment
3. **Claims checklist** — what to verify

Group cuts into generations that fit the engine clip cap. Hand the cut list to **video-generation** for prompts.

## Revision map

| Complaint | Cause | Fix |
|---|---|---|
| boring / people will sleep | long cuts, one location | halve cuts, change environment |
| reads like an ad | marketing register | rewrite as speech, one claim |
| confusing | ambiguous referent | anti-confusion rule |
| too long | too many beats | delete beats, never rush delivery |
| not my style | wrong register | ask for one reference ad |

Rewrite from beat structure; do not patch individual lines.
