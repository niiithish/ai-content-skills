#!/usr/bin/env bash
# Build 2fps contact sheets: 12 stills per image = 6 seconds of video.
# Usage: contact-sheets.sh /abs/path/to/video.mp4 [outdir]
set -euo pipefail

VIDEO="${1:?usage: contact-sheets.sh /abs/path/to/video.mp4 [outdir]}"
test -f "$VIDEO" || { echo "not a file: $VIDEO" >&2; exit 1; }

OUT="${2:-/tmp/video-breakdown-$$}"
FPS=2
CHUNK=12
COLS=4
THUMB_W=360
FONT=""
for f in \
  /usr/share/fonts/noto/NotoSans-Regular.ttf \
  /usr/share/fonts/TTF/DejaVuSans.ttf \
  /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf; do
  if [[ -f "$f" ]]; then FONT="$f"; break; fi
done

mkdir -p "$OUT/thumbs" "$OUT/labeled" "$OUT/sheets"
rm -f "$OUT/thumbs"/*.jpg "$OUT/labeled"/*.jpg "$OUT/sheets"/*.jpg "$OUT/manifest.tsv"

ffmpeg -y -i "$VIDEO" -vf "fps=${FPS},scale=${THUMB_W}:-2" -q:v 3 \
  "$OUT/thumbs/f_%04d.jpg" >/dev/null 2>&1

shopt -s nullglob
thumbs=( "$OUT/thumbs"/f_*.jpg )
if (( ${#thumbs[@]} == 0 )); then
  echo "no frames extracted from $VIDEO" >&2
  exit 1
fi

label_time() {
  python3 -c "t=($1-1)/${FPS}; m=int(t)//60; s=t%60; print(f'{m}:{s:04.1f}')"
}

i=1
for src in "${thumbs[@]}"; do
  printf -v idx '%04d' "$i"
  ts="$(label_time "$i")"
  if [[ -n "$FONT" ]]; then
    magick "$src" -background '#111114' -fill white -font "$FONT" -pointsize 22 \
      label:"${ts}" -gravity center -append "$OUT/labeled/${idx}.jpg"
  else
    magick "$src" -background '#111114' -fill white -pointsize 22 \
      label:"${ts}" -gravity center -append "$OUT/labeled/${idx}.jpg"
  fi
  i=$((i + 1))
done

n=${#thumbs[@]}
sheet=1
start=1
while (( start <= n )); do
  end=$(( start + CHUNK - 1 ))
  if (( end > n )); then end=$n; fi
  count=$(( end - start + 1 ))
  rows=$(( (count + COLS - 1) / COLS ))
  printf -v sidx '%02d' "$sheet"
  args=()
  for (( i=start; i<=end; i++ )); do
    printf -v idx '%04d' "$i"
    args+=( "$OUT/labeled/${idx}.jpg" )
  done
  body="$OUT/sheets/body_${sidx}.jpg"
  dest="$OUT/sheets/sheet_${sidx}.jpg"
  magick montage "${args[@]}" -tile "${COLS}x${rows}" -geometry +12+12 \
    -background '#0e0e10' "$body"
  t0="$(label_time "$start")"
  t1="$(label_time "$end")"
  if [[ -n "$FONT" ]]; then
    magick "$body" -gravity north -background '#0e0e10' -splice 0x56 \
      -fill '#f4f4f5' -font "$FONT" -pointsize 20 \
      -annotate +0+16 "${t0} – ${t1}   ·   ${count} stills   ·   ${FPS} fps   ·   ${COLS} across" \
      "$dest"
  else
    magick "$body" "$dest"
  fi
  rm -f "$body"
  # start_sec end_sec as decimals for the agent
  python3 -c "print(f'{($start-1)/${FPS}:.1f}\t{( $end-1)/${FPS}:.1f}')" \
    | { read s e; printf '%s\t%s\t%s\t%s\t%s\n' "$dest" "$s" "$e" "$count" "${t0}-${t1}" >> "$OUT/manifest.tsv"; }
  start=$(( end + 1 ))
  sheet=$(( sheet + 1 ))
done

echo "OUT=$OUT"
echo "FRAMES=$n"
echo "SHEETS=$((sheet - 1))"
echo "MANIFEST=$OUT/manifest.tsv"
echo "---"
cat "$OUT/manifest.tsv"
