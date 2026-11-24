#!/usr/bin/env bash
# Speeds the master talking head up (default 1.1x: Aleo video-3, the AI delivery reads slow), voice pitch kept.
# Encodes on the iGPU (h264_vaapi), never libx264. This makes the master *source* file; the edit itself never leaves FilmCraft.
# Usage: speed_up.sh IN.mp4 [SPEED] [OUT.mp4]   (OUT defaults to IN_<SPEED>x.mp4)
set -euo pipefail
IN=$1; S=${2:-1.1}; OUT=${3:-${IN%.mp4}_${S}x.mp4}
ffmpeg -hide_banner -loglevel error -stats -n -vaapi_device /dev/dri/renderD128 -i "$IN" \
  -filter_complex "[0:v]setpts=PTS/$S,fps=24,format=nv12,hwupload[v];[0:a]atempo=$S[a]" -map "[v]" -map "[a]" \
  -c:v h264_vaapi -qp 18 -profile:v high -c:a aac -b:a 192k -movflags +faststart "$OUT"
ffprobe -v error -show_entries stream=codec_name,duration,r_frame_rate -of csv=p=0 "$OUT"
