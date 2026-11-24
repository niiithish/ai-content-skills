# FilmCraft CLI & JSON Schema Reference

Exact `filmcraft-cli` schemas and idioms so scripts never fail with `KeyError: 'result'`, `'list' object has no attribute 'get'`, or stale clip IDs.

## Bridge vs. Headless Mode

- **Always prefer `scripts/fc.py`** (`status`, `run`, `swap`, `relink`, `export`). It automatically uses `--bridge 127.0.0.1:9876` when the FilmCraft app has the project open, and `--project P --save` when closed.
- **Bridge token:** `FILMCRAFT_CONTROL_TOKEN` (64 hex chars in `~/.config/filmcraft/control-token`) is required by both `filmcraft-live` and `filmcraft-cli --bridge`. `fc.py` loads it automatically.
- **Never** run `filmcraft-cli --project P --save` while the GUI has `P` open (the GUI's in-memory copy will overwrite your changes, or vice versa).
- **Never** confuse `"update filmcraft"` (update the `.fcproj` timeline) with `scripts/filmcraft-update` (upgrades the FilmCraft app binary).

## Time & Frame Units

- `TPS = 254016000000` ticks per second.
- At **24 fps**: `1 frame = 10584000000` ticks (`TPS // 24`).
- At **30 fps**: `1 frame = 8467200000` ticks (`TPS // 30`).
- Always check the sequence's actual `fps` before computing ticks; **every clip's `start` and `duration` must be an exact integer multiple of `frame_ticks`**.

## Exact `inspect` Output Schemas

`filmcraft-cli --compact --project P inspect <what>` prints **top-level JSON directly** (NOT wrapped in `{"result": ...}`).

### `inspect project`
```json
{
  "path": "/abs/path/to/hook-1.fcproj",
  "dirty": false,
  "activeSequence": 1,
  "root": {
    "name": "hook-1",
    "children": [
      {"item": 12, "name": "clip-1a-v1-1080p.mp4", "type": "video", "path": "/abs/..."},
      {"name": "BinName", "children": [...]}
    ]
  }
}
```
- **Common trap:** Do NOT do `d["result"]` or index `d["items"]` directly — traverse `d["root"]["children"]` recursively (see `fc.media_items()`).

### `inspect sequence`
```json
{
  "id": 13,
  "name": "hook-1",
  "duration": 2243808000000,
  "durationFrames": 265,
  "settings": {
    "width": 1080,
    "height": 1920,
    "frame_rate": {"num": 30, "den": 1},
    "sample_rate": 48000
  },
  "video": [
    {
      "name": "V1",
      "items": [
        {
          "clip": 14,
          "item": 1,
          "name": "clip-1a-v1-1080p.mp4",
          "start": 0,
          "duration": 533433600000,
          "startFrame": 0,
          "endFrame": 63,
          "durationFrames": 63,
          "sourceIn": 25401600000,
          "sourceOut": 558835200000,
          "speed": 1.0,
          "effects": [{"effect": "motion", "enabled": true, "params": {...}}]
        }
      ]
    }
  ],
  "audio": [
    {
      "name": "A1",
      "items": [...]
    }
  ]
}
```
- **Common traps:**
  - Frame rate is under `s["settings"]["frame_rate"]` as `{"num": N, "den": D}` (NOT top-level `s["fps"]`). Compute `fps = fr["num"] / fr["den"]` and `frame_ticks = round(254016000000 / fps)`.
  - `s["video"]` and `s["audio"]` are **lists of track dicts** (0-indexed: `s["video"][0]` is `V1`), NOT dicts keyed by `"V1"`.
  - Track clips live in `track["items"]`, each with integer `"clip"` (timeline clip ID) and `"item"` (project bin item ID).
  - Never pass a bin `item` ID where a timeline `clip` ID is expected (`effects.*`, `timeline.move`, `timeline.trim`, `graphics.set` all take `clip` IDs; `media.replaceFootage` and `timeline.place` take `item` IDs).
  - `graphics.set` ONLY works on graphic/text clips — calling it on a video/image clip fails with `no graphic clip`.

## `run` JSONL Output Schema

`filmcraft-cli ... --compact run cmds.jsonl` prints **one JSON line per command**:
```json
{"line": 1, "id": "timeline.move", "ok": true, "result": {...}}
{"line": 2, "id": "graphics.set", "ok": false, "error": "..."}
```
Always check `all(l.get("ok", True) for l in lines)`. Discover exact params anytime with:
```bash
filmcraft-cli commands <filter>
filmcraft-cli describe <command.id>
```

## Most-Used JSONL Commands

```json
{"id":"media.replaceFootage","params":{"item":ITEM_ID,"path":"/abs/new.mp4"}}
{"id":"clip.rename","params":{"clip":CLIP_ID,"name":"clip-6a-v3-1080p.mp4"}}
{"id":"timeline.move","params":{"moves":[{"clip":CLIP_ID,"track":TRACK_ID,"time":FRAME*TICKS}],"insert":false,"linked":false}}
{"id":"timeline.trim","params":{"clip":CLIP_ID,"edge":"in","mode":"regular","deltaFrames":N}}
{"id":"timeline.delete","params":{"clips":[CLIP_ID],"ripple":false}}
{"id":"effects.setParam","params":{"clip":CLIP_ID,"effect":"motion","param":"scale","value":104.0,"keyframe":true,"time":FRAME*TICKS}}
{"id":"effects.deleteKeyframe","params":{"clip":CLIP_ID,"effect":"motion","param":"scale","mediaTime":TICKS}}
{"id":"file.save","params":{}}
```

## Rendering Check Frames (Without Full Export)

```bash
filmcraft-cli --project edit/hook-1.fcproj render --seconds 12.5 --out /tmp/frame_12_5.png
```
Use `render` to verify cuts, captions, overlays, and color before asking the user to review or export.
