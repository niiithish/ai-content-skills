#!/usr/bin/env bash
# Set up (or update) a video project, any style.
#
#   init-project.sh /abs/client-folder video-1 --style photoreal
#   init-project.sh /abs/client-folder video-2 --update-scripts
#   init-project.sh /abs/client/video-2 . --style animated
#                                 a standalone video: everything below goes in that one folder
#                                 (a client whose videos share nothing)
#
# --style animated|photoreal names the style skill in a new AGENTS.md (default animated).
#
# Creates, without overwriting anything that exists:
#   AGENTS.md                     client rules, look, sheets, decisions (from the template)
#   brief/                        the client's brief files go here
#   assets/characters/ assets/environments/ assets/props/   reference sheets, shared by every video
#   video-N/project.conf          batch pacing
#   video-N/scenes/stills-batch.json   video-N/clips/clips-batch.json
#   video-N/edit/ review/ deliverables/ .flow/   (.flow/ holds flow state and batch logs)
#   video-N/scripts/make.py       copied from the skill (--update-scripts refreshes it)
set -euo pipefail

ROOT=""; VIDEO_NAME=""; UPDATE=0; STYLE=animated
while [[ $# -gt 0 ]]; do
  case "$1" in
    --update-scripts) UPDATE=1 ;;
    --style) STYLE="${2:?--style needs animated or photoreal}"; shift ;;
    *) if [[ -z "$ROOT" ]]; then ROOT="$1"; elif [[ -z "$VIDEO_NAME" ]]; then VIDEO_NAME="$1"; fi ;;
  esac
  shift
done
[[ -n "$ROOT" ]] || { echo "usage: init-project.sh /abs/client-folder [video-N|.] [--style animated|photoreal] [--update-scripts]" >&2; exit 2; }
[[ "$STYLE" == animated || "$STYLE" == photoreal ]] || { echo "--style is animated or photoreal" >&2; exit 2; }
VIDEO_NAME="${VIDEO_NAME:-video-1}"

SKILL=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$ROOT"
ROOT=$(cd "$ROOT" && pwd)
VIDEO="$ROOT/$VIDEO_NAME"
REL="$VIDEO_NAME/"
[[ "$VIDEO_NAME" == "." ]] && VIDEO="$ROOT" && REL=""

made() { echo "created $1"; }

mkdir -p "$ROOT"/brief "$ROOT"/assets/{characters,environments,props} \
         "$VIDEO"/{scenes,clips,edit,review,scripts,deliverables,.flow}

if [[ ! -e "$ROOT/AGENTS.md" ]]; then
  sed "s/{{STYLE}}/$STYLE/g" "$SKILL/templates/AGENTS.md" > "$ROOT/AGENTS.md"
  made AGENTS.md
fi
[[ -e "$VIDEO/PLAN.md" ]] || echo "note: no PLAN.md yet in $VIDEO: plan the video with the video-plan skill first"

for m in scenes/stills-batch.json clips/clips-batch.json; do
  [[ -e "$VIDEO/$m" ]] || { printf '{\n  "jobs": []\n}\n' > "$VIDEO/$m"; made "$REL$m"; }
done

if [[ ! -e "$VIDEO/project.conf" ]]; then
  cat > "$VIDEO/project.conf" <<EOF
# flow batch pacing (flow itself picks free accounts for stills and drafts, paid ones for finals)
CONCURRENCY=5
RPM=6
EOF
  made "${REL}project.conf"
fi

if [[ ! -e "$VIDEO/scripts/make.py" || $UPDATE == 1 ]]; then
  cp "$SKILL/scripts/make.py" "$VIDEO/scripts/make.py"
  chmod +x "$VIDEO/scripts/make.py"
  echo "wrote   ${REL}scripts/make.py"
fi

cat <<EOF

Project: $ROOT
Video:   $VIDEO
Run tools with:  $VIDEO/scripts/make.py status
EOF
