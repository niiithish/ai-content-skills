#!/bin/bash
# Convert videos into ProRes 422 LT .mov files that free DaVinci Resolve on Linux can read
# (it can't decode H.264/H.265/AAC). Audio, if any, becomes PCM; pass --no-audio to drop it.
# Usage: to-prores.sh [--no-audio] -o OUT_DIR file1.mp4 [file2.mp4 ...]
set -euo pipefail
audio=(-c:a pcm_s16le)
out=""
while [ $# -gt 0 ]; do
  case "$1" in
    --no-audio) audio=(-an); shift ;;
    -o) out="$2"; shift 2 ;;
    *) break ;;
  esac
done
[ -z "$out" ] || [ $# -eq 0 ] && { echo "Usage: to-prores.sh [--no-audio] -o OUT_DIR files..." >&2; exit 1; }
mkdir -p "$out"
for f in "$@"; do
  name="$(basename "${f%.*}").mov"
  [ -s "$out/$name" ] && { echo "skip $name (exists)"; continue; }
  echo "==> $f -> $out/$name"
  ffmpeg -hide_banner -loglevel error -y -i "$f" \
    -c:v prores_ks -profile:v 1 -pix_fmt yuv422p10le -vendor apl0 \
    "${audio[@]}" "$out/$name.tmp.mov"
  mv "$out/$name.tmp.mov" "$out/$name"
done
