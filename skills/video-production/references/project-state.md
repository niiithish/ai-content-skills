# Anti-Compaction State (`PROJECT_STATE.json`)

Long video production sessions regularly compact context multiple times. Without a persistent state file on disk, agents forget earlier user rules ("direct 1080p", "from scratch", brand hex colors, cast demographics, before/after arc) and accidentally regenerate already-approved clips.

## Rules

1. **Read `PROJECT_STATE.json` at session start and immediately after any compaction.**
2. **Update it at every gate** (plan approval, sheet approval, still approval, clip approval, engine switch, or new user rule).
3. **Never regenerate any shot ID listed in `approved_stills` or `approved_clips`** unless the user explicitly names that shot for a redo.
4. **Keep `engines` configurable, not hardcoded.** Flow is the primary engine; Seedream 5.5 (1K) via `elevenlabs-creative` is currently strong for realistic human character sheets, and Google's upcoming Flow image model is expected to beat Seedream 5.5 — update `engines.sheets_human` in `PROJECT_STATE.json` when the user switches defaults.

## Schema

```json
{
  "project": "<client>/<video-N>",
  "style": "photoreal | pixar-3d | claymation | talking-head | ai-singing | ai-drama | medical-cgi | hybrid-ugc | storybook-2d",
  "aspect_ratio": "9:16",
  "engines": {
    "sheets_human": "elevenlabs:seedream-5.5-1k | flow:default",
    "sheets_other": "flow:default",
    "stills": "flow:default",
    "clips": "flow:omni-1080p",
    "safety_fallback": "elevenlabs:seedance-2.0-mini-720p | elevenlabs:kling-4.0-1080p | elevenlabs:minimax-h3-max"
  },
  "brand": {
    "name": "Brand Name",
    "cta_hex_bg": "#FAF7F2",
    "cta_hex_text": "#1A1A1A",
    "cta_hex_accent": "#EB8399",
    "logo_path": "../assets/logos/logo.png"
  },
  "cast_locks": {
    "target_demographics": "e.g., white British woman mid-40s (explicitly locked with user)",
    "before_after_arc": "e.g., dull tired skin & light eye bags in shots 1-24; bright glowing skin in shots 25-60"
  },
  "locked_rules": [
    "Direct 1080p clips by default (360p draft only if --draft requested)",
    "Concurrency 10-12 default (never 1-at-a-time unless chaining from previous shot)",
    "From-scratch regeneration only (never feed a broken still/clip back as ref)",
    "Reference-image mode by default (never start-frame unless explicitly requested)"
  ],
  "approved_stills": ["1a", "1b"],
  "approved_clips": ["1a", "1b"],
  "reused_assets": ["../video-1/clips/all/clip-3-v2-1080p.mp4"]
}
```
