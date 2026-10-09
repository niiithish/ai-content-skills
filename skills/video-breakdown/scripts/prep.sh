#!/usr/bin/env bash
# Everything mechanical a breakdown needs, in one command, written next to the video:
#   <stem>.txt / .words.json / .srt   word-timed transcript (transcribe skill)
#   cuts.txt                          hard cuts, one time in seconds per line (scene score > 0.3)
#   sheets/                           2 fps contact sheets, 12 frames (6 s) each, plus manifest.tsv
#   specs.txt                         size, fps, length, words, words per minute, cuts, average shot
# Usage: prep.sh /abs/path/to/video.mp4
set -euo pipefail
V="${1:?usage: prep.sh /abs/path/to/video.mp4}"
test -f "$V" || { echo "not a file: $V" >&2; exit 1; }
D="$(cd "$(dirname "$V")" && pwd)"; S="$(basename "${V%.*}")"
HERE="$(cd "$(dirname "$0")" && pwd)"
TR=""
for t in "$HERE/../../transcribe/scripts/transcribe.py" "$HOME/.claude/skills/transcribe/scripts/transcribe.py"; do
  [ -f "$t" ] && { TR="$t"; break; }
done

if [ -n "$TR" ] && [ ! -s "$D/$S.words.json" ]; then
  python3 "$TR" "$V" --srt --out-dir "$D" > "$D/transcribe.log" 2>&1 &
  tpid=$!
fi
ffmpeg -hide_banner -i "$V" -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 \
  | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 > "$D/cuts.txt" &
cpid=$!
bash "$HERE/contact-sheets.sh" "$V" "$D/sheets" > "$D/sheets.out"
wait $cpid
[ -n "${tpid:-}" ] && { wait $tpid || echo "transcribe failed: see $D/transcribe.log" >&2; }

read -r w h fps < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$V" | tr ',' ' ')
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
words=$( [ -s "$D/$S.txt" ] && wc -w < "$D/$S.txt" || echo "?")
cuts=$(wc -l < "$D/cuts.txt")
python3 - "$w" "$h" "$fps" "$dur" "$words" "$cuts" > "$D/specs.txt" <<'EOF'
import sys
w, h, fps, dur, words, cuts = sys.argv[1:]
n, d = fps.split("/"); dur = float(dur); shots = int(cuts) + 1
print(f"Size     {w}x{h}, {float(n)/float(d):.3g} fps")
print(f"Length   {dur:.1f} s")
if words != "?":
    print(f"Words    {words} spoken (~{int(words) / dur * 60:.0f} wpm)")
print(f"Shots    {shots} hard cuts+1 (average {dur / shots:.1f} s a shot; whip pans and dissolves may hide more)")
EOF
cat "$D/specs.txt"
echo "transcript $D/$S.srt"
echo "cuts       $D/cuts.txt"
echo "sheets     $(grep -o 'SHEETS=[0-9]*' "$D/sheets.out" | cut -d= -f2) in $D/sheets/sheets: read every one, in order"
