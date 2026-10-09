#!/bin/bash
# Turn Resolve exports (ProRes/DNxHR .mov) into client-ready H.264 MP4s, one at a time.
# Intel Quick Sync first (~8x faster than x264 slow on an Iris Xe, SSIM 0.99), x264 veryfast without a GPU.
# Length is the video stream's (a looped or longer input can't stretch it); PCM audio becomes AAC 192k.
# Usage: to-mp4.sh export.mov final.mp4 [quality]   (quality 18 near-lossless, 20 default, 23 smaller)
#        to-mp4.sh -d OUT_DIR a.mov b.mov ...       (each to OUT_DIR/<name>.mp4)
set -euo pipefail
one() {
  local in="$1" out="$2" q="${3:-20}" dur tmp
  dur=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$in" | head -1)
  tmp="${out%.mp4}.tmp.mp4"
  if ! ffmpeg -hide_banner -loglevel error -stats -y -init_hw_device qsv=hw -filter_hw_device hw -i "$in" \
       -vf "format=nv12,hwupload=extra_hw_frames=64" -c:v h264_qsv -global_quality "$q" -preset slow \
       -map 0:v:0 -map 0:a? -t "$dur" -c:a aac -b:a 192k -movflags +faststart "$tmp" 2>/dev/null; then
    ffmpeg -hide_banner -loglevel error -stats -y -i "$in" -map 0:v:0 -map 0:a? -t "$dur" \
      -c:v libx264 -crf "$q" -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$tmp"
  fi
  mv "$tmp" "$out"
  ls -lh "$out"
}
if [ "${1:-}" = "-d" ]; then
  d="$2"; shift 2; mkdir -p "$d"
  for f in "$@"; do b=$(basename "${f%.*}"); one "$f" "$d/$b.mp4"; done
else
  [ $# -lt 2 ] && { echo "Usage: to-mp4.sh IN.mov OUT.mp4 [quality] | to-mp4.sh -d DIR files..." >&2; exit 1; }
  one "$@"
fi
