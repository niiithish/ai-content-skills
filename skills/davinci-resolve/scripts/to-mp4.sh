#!/bin/bash
# Turn a Resolve export (ProRes/DNxHR .mov) into a client-ready H.264 MP4.
# Usage: to-mp4.sh export.mov final.mp4 [crf]   (crf 18 near-lossless, 20 default, 23 smaller)
set -euo pipefail
[ $# -lt 2 ] && { echo "Usage: to-mp4.sh IN.mov OUT.mp4 [crf]" >&2; exit 1; }
in="$1"; out="$2"; crf="${3:-20}"
ffmpeg -hide_banner -loglevel error -stats -y -i "$in" \
  -c:v libx264 -crf "$crf" -preset slow -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 192k "${out%.mp4}.tmp.mp4"
mv "${out%.mp4}.tmp.mp4" "$out"
ls -lh "$out"
