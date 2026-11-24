---
name: elevenlabs-creative
description: >
  Multi-engine image, video, and voice-cleanup workflows via ElevenLabs Creative (MCP or web): Seedream 5.5 (1K) for realistic human character sheets, Seedance 2.0 Mini / Kling 4.0 (1080p) / MiniMax H3 Max as fallbacks when Google Flow blocks or blurs a shot, and Voice Isolator for talking-head audio cleanup. Use when routing realistic human sheets, Flow UNSAFE_GENERATION / blur fallbacks, or talking-head voice isolation. Not for primary Google Flow runs (use flow) or Cartesia TTS voiceovers (use cartesia-tts).
compatibility: Requires ElevenLabs Creative MCP (or web access) and cloudflared for serving local reference images.
metadata:
  author: ai-content-skills
  version: "1.0"
---

# ElevenLabs Creative (Multi-Engine Fallback & Voice Isolator)

Google Flow (`flow`) is our primary engine. Use ElevenLabs Creative when a project routes specific shots here or when Flow blocks/blurs a shot.

## When to Use Which Model

| Task | Model | Notes |
|---|---|---|
| Realistic human character sheets & hero stills | **Seedream 5.5 (1K)** | Configurable preference — Google's upcoming Flow image model is expected to supersede Seedream 5.5 for human sheets once released. |
| Flow policy-blocked scenes (beds, skin/cellulite, intimacy, children-adjacent) | **Seedance 2.0 Mini** | Primary video fallback when Flow returns `UNSAFE_GENERATION`. |
| Product label / text fidelity shots | **Kling 4.0 (1080p)** | Use when Flow blurs or garbles small bottle/packaging text. |
| Complex physical motion fallback | **MiniMax H3 Max** | Alternative video fallback when Flow or Seedance physics break. |
| Talking-head audio cleanup (room noise / music removal) | **Voice Isolator** | Standard cleanup pass before re-muxing talking-head audio for FilmCraft. |

## Hard Credit & Quality Locks (Non-Negotiable)

1. **NEVER auto-route or spend ElevenLabs credits without explicit user confirmation**:
   - ElevenLabs is significantly more expensive than Flow. Never fall back to ElevenLabs automatically when Flow blocks or blurs a shot — first report which shots failed (with credit estimate via `estimate_only: true` when applicable) and wait for the user to approve, or only run when the user explicitly says to use ElevenLabs.
2. **ALWAYS set explicit aspect ratio AND `quantity=1`**:
   - ElevenLabs Creative defaults to **`aspect_ratio: auto`** and **`quantity: 4`**, silently burning 4× credits per call.
   - Every image or video node MUST explicitly pass `aspect_ratio` (e.g., `"9:16"` for vertical ads) and `quantity: 1` unless the user explicitly asks for multiple variants.
3. **From-scratch regeneration**: Never feed a broken generation (photoshopped product, warped anatomy, bad gaze) back as a reference image to "fix" it. Regenerate from scratch using the clean original character/product sheet and a simplified prompt.
4. **Verify before downloading finals**: Inspect outputs before attaching them to downstream video nodes or FilmCraft timelines.

## Passing Local Reference Images (`cloudflared` Quick Tunnel)

ElevenLabs Creative MCP requires public HTTPS URLs for reference images. Serve only the specific folder needed via a short-lived `cloudflared` quick tunnel, then tear both processes down immediately after upload:

```bash
# 1. Start a local read-only HTTP server in the reference folder
python3 -m http.server 18765 --bind 127.0.0.1 --directory /ABS/path/to/refs &
HTTP_PID=$!

# 2. Expose via cloudflared quick tunnel (capture the trycloudflare.com URL from stderr)
cloudflared tunnel --url http://127.0.0.1:18765 > /tmp/cf-tunnel.log 2>&1 &
CF_PID=$!
sleep 3
grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cf-tunnel.log | head -n 1

# 3. Attach reference URLs (e.g. https://<sub >.trycloudflare.com/hero-sheet.png)
# 4. Always clean up immediately once ElevenLabs finishes ingesting the file:
kill "$CF_PID" "$HTTP_PID" 2>/dev/null
```

- Never leave a tunnel or HTTP server running after the reference upload finishes.
- Only serve the specific reference directory (never `$HOME` or a whole client root).
- URL-encode spaces in filenames or use hyphenated names (`hero-sheet.png`).

## Voice Isolator Round-Trip (Talking Heads)

1. Export or concatenate the raw talking-head audio track (`ALL_combined.mp3` or per-clip MP3s).
2. Run through ElevenLabs **Voice Isolator** (remove background noise and music while preserving vocal cadence).
3. Verify exact duration matches the source before muxing back (no sample-rate drift or robotic stretching).
4. Hand off the isolated track to `filmcraft-edit` / `captions-filmcraft`.

## VPN & Cloudflare 403 Troubleshooting

- **HTTP 403 / Cloudflare challenge / auth drop**:
  1. Check if a VPN is active — pause the VPN or switch to a clean residential/standard exit node.
  2. Avoid firing rapid unthrottled bursts of MCP node calls; batch cleanly and wait for node completion.
  3. If the MCP session token expired, notify the user to re-authenticate ElevenLabs rather than looping retries.
  4. If a `trycloudflare.com` URL returns 403/502, verify `HTTP_PID` is still alive on `127.0.0.1:18765` and wait 2–3 s for DNS propagation before attaching the URL.
