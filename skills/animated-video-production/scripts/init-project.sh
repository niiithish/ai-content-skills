#!/usr/bin/env bash
# Set up (or update) an animated video project.
#
#   init-project.sh /abs/client-folder [video-1]
#   init-project.sh /abs/client-folder video-2 --update-scripts
#
# Creates, without overwriting anything that exists:
#   AGENTS.md                     client rules + brief digest (from the template)
#   brief/                        the client's brief files go here
#   characters/ environments/ props/   reference sheets, shared by every video
#   video-N/SHOT-LIST.md          story lock, timed to the voiceover
#   video-N/project.conf          PRO_ACCOUNT for 1080p finals, batch pacing
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

made() { echo "created $1"; }
put() {  # put SRC DEST: copy only when DEST is missing
  if [[ ! -e "$2" ]]; then cp "$1" "$2"; made "${2#$ROOT/}"; fi
}

mkdir -p "$ROOT"/{brief,characters,environments,props} \
         "$VIDEO"/{scenes,clips,edit,review,scripts}

put "$SKILL/templates/AGENTS.md" "$ROOT/AGENTS.md"
put "$SKILL/templates/SHOT-LIST.md" "$VIDEO/SHOT-LIST.md"

for m in scenes/stills-batch.json clips/clips-batch.json; do
  [[ -e "$VIDEO/$m" ]] || { printf '{\n  "jobs": []\n}\n' > "$VIDEO/$m"; made "$VIDEO_NAME/$m"; }
done

if [[ ! -e "$VIDEO/project.conf" ]]; then
  cat > "$VIDEO/project.conf" <<EOF
# Paid Flow account used for 1080p finals (the upsample is free only on a paid plan).
PRO_ACCOUNT=${FLOW_PRO_ACCOUNT:-}
# flow batch pacing
CONCURRENCY=3
RPM=6
EOF
  made "$VIDEO_NAME/project.conf"
fi

if [[ ! -e "$VIDEO/scripts/make.py" || $UPDATE == 1 ]]; then
  cp "$SKILL/scripts/make.py" "$VIDEO/scripts/make.py"
  chmod +x "$VIDEO/scripts/make.py"
  echo "wrote   $VIDEO_NAME/scripts/make.py"
fi

cat <<EOF

Project: $ROOT
Video:   $VIDEO
Run tools with:  $VIDEO/scripts/make.py status
EOF
