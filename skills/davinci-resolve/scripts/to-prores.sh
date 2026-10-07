#!/bin/bash
# Convert videos into ProRes 422 LT .mov files that free DaVinci Resolve on Linux can read
# (it can't decode H.264/H.265/AAC). Audio, if any, becomes PCM; pass --no-audio to drop it.
# Runs several files at once (-j, default half the cores) because one ProRes encode can't fill the CPU.
# prores_aw, not prores_ks: same ProRes LT, ~3x faster to encode (1.4 s vs 4.4 s for a 4 s 1080x1920 clip).
# Usage: to-prores.sh [--no-audio] [-j N] -o OUT_DIR file1.mp4 [file2.mp4 ...]
set -euo pipefail
audio=(-c:a pcm_s16le)
out=""
jobs_n=$(( $(nproc) / 2 > 0 ? $(nproc) / 2 : 1 ))
while [ $# -gt 0 ]; do
  case "$1" in
    --no-audio) audio=(-an); shift ;;
    -o) out="$2"; shift 2 ;;
    -j) jobs_n="$2"; shift 2 ;;
    *) break ;;
  esac
done
[ -z "$out" ] || [ $# -eq 0 ] && { echo "Usage: to-prores.sh [--no-audio] [-j N] -o OUT_DIR files..." >&2; exit 1; }
mkdir -p "$out"

convert() {
  local f="$1" name
  name="$(basename "${f%.*}").mov"
  ffmpeg -hide_banner -loglevel error -y -i "$f" \
    -c:v prores_aw -profile:v 1 -pix_fmt yuv422p10le -vendor apl0 \
    "${audio[@]}" "$out/$name.tmp.mov" && mv "$out/$name.tmp.mov" "$out/$name" && echo "done $name"
}

start=$SECONDS; fail=0
for f in "$@"; do
  name="$(basename "${f%.*}").mov"
  [ -s "$out/$name" ] && { echo "skip $name (exists)"; continue; }
  convert "$f" &
  while [ "$(jobs -rp | wc -l)" -ge "$jobs_n" ]; do wait -n || fail=1; done
done
while [ "$(jobs -rp | wc -l)" -gt 0 ]; do wait -n || fail=1; done
echo "converted in $((SECONDS - start)) s"
exit $fail
