#!/usr/bin/env bash
# Puts the voice-changed / isolated audio (from ElevenLabs) back under the master talking head: picture copied as-is,
# the new audio as AAC 320k. Check that both durations match (printed) before going on.
# Usage: mux_voice.sh MASTER.mp4 VOICE.mp3 [OUT.mp4]   (OUT defaults to MASTER_isolated.mp4)
set -euo pipefail
IN=$1; A=$2; OUT=${3:-${IN%.mp4}_isolated.mp4}
ffmpeg -hide_banner -loglevel error -n -i "$IN" -i "$A" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k \
  -movflags +faststart "$OUT"
ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 "$OUT"
