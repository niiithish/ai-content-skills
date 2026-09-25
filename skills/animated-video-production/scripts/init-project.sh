#!/usr/bin/env bash
# Set up (or update) an animated video project.
#
#   init-project.sh /abs/client-folder [video-1]
#   init-project.sh /abs/client-folder video-2 --update-scripts
#   init-project.sh /abs/client/video-2 .     a standalone video: everything below goes in that
#                                             one folder (a client whose videos share nothing)
#
# Creates, without overwriting anything that exists:
#   AGENTS.md                     client rules, look, sheets, decisions (from the template)
#   brief/                        the client's brief files go here
#   characters/ environments/ props/   reference sheets, shared by every video
#   video-N/project.conf          batch pacing
#   video-N/scenes/stills-batch.json   video-N/clips/clips-batch.json
#   video-N/edit/ video-N/review/
#   video-N/scripts/make.py       copied from the skill (--update-scripts refreshes it)
set -euo pipefail

ROOT="${1:?usage: init-project.sh /abs/client-folder [video-N] [--update-scripts]}"
VIDEO_NAME="${2:-video-1}"
UPDATE=0
[[ "${3:-}" == "--update-scripts" || "${2:-}" == "--update-scripts" ]] && UPDATE=1
[[ "$VIDEO_NAME" == "--update-scripts" ]] && VIDEO_NAME=video-1

SKILL=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$ROOT"
ROOT=$(cd "$ROOT" && pwd)
VIDEO="$ROOT/$VIDEO_NAME"
REL="$VIDEO_NAME/"
[[ "$VIDEO_NAME" == "." ]] && VIDEO="$ROOT" && REL=""

made() { echo "created $1"; }
put() {  # put SRC DEST: copy only when DEST is missing
  if [[ ! -e "$2" ]]; then cp "$1" "$2"; made "${2#$ROOT/}"; fi
}

mkdir -p "$ROOT"/{brief,characters,environments,props} \
         "$VIDEO"/{scenes,clips,edit,review,scripts}

put "$SKILL/templates/AGENTS.md" "$ROOT/AGENTS.md"
[[ -e "$VIDEO/PLAN.md" ]] || echo "note: no PLAN.md yet in $VIDEO: plan the video with the video-plan skill first"

for m in scenes/stills-batch.json clips/clips-batch.json; do
  [[ -e "$VIDEO/$m" ]] || { printf '{\n  "jobs": []\n}\n' > "$VIDEO/$m"; made "$REL$m"; }
done

if [[ ! -e "$VIDEO/project.conf" ]]; then
  cat > "$VIDEO/project.conf" <<EOF
# flow batch pacing (flow itself picks free accounts for stills and drafts, paid ones for finals)
CONCURRENCY=3
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
