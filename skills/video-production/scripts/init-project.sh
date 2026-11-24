#!/usr/bin/env bash
# Set up (or update) a video project in any style.
#
#   init-project.sh /abs/client-folder video-1 --style photoreal
#   init-project.sh /abs/client-folder video-2 --update-scripts
#   init-project.sh /abs/client/video-2 . --style pixar-3d
#
# Supported --style values:
#   photoreal | pixar-3d | claymation | talking-head | ai-singing |
#   ai-drama | medical-cgi | hybrid-ugc | storybook-2d
#   (aliases: animated -> pixar-3d, clay -> claymation)
#
# Creates, without overwriting anything that exists:
#   AGENTS.md                         client rules, look, sheets, decisions
#   brief/                            client brief files
#   assets/characters/ environments/ props/
#   video-N/PROJECT_STATE.json        anti-compaction state & engine config
#   video-N/project.conf              batch concurrency & RPM
#   video-N/scenes/stills-batch.json  video-N/clips/clips-batch.json
#   video-N/edit/ review/ deliverables/ .flow/
#   video-N/scripts/make.py           copied from the skill (--update-scripts refreshes it)
set -euo pipefail

ROOT=""; VIDEO_NAME=""; UPDATE=0; STYLE=photoreal
while [[ $# -gt 0 ]]; do
  case "$1" in
    --update-scripts) UPDATE=1 ;;
    --style) STYLE="${2:?--style requires a style name}"; shift ;;
    *) if [[ -z "$ROOT" ]]; then ROOT="$1"; elif [[ -z "$VIDEO_NAME" ]]; then VIDEO_NAME="$1"; fi ;;
  esac
  shift
done

# Backward-compatible aliases
[[ "$STYLE" == "animated" ]] && STYLE="pixar-3d"
[[ "$STYLE" == "clay" ]] && STYLE="claymation"

[[ -n "$ROOT" ]] || { echo "usage: init-project.sh /abs/client-folder [video-N|.] [--style STYLE] [--update-scripts]" >&2; exit 2; }
case "$STYLE" in
  photoreal|pixar-3d|claymation|talking-head|ai-singing|ai-drama|medical-cgi|hybrid-ugc|storybook-2d) ;;
  *) echo "unsupported --style '$STYLE'. Use: photoreal, pixar-3d, claymation, talking-head, ai-singing, ai-drama, medical-cgi, hybrid-ugc, storybook-2d" >&2; exit 2 ;;
esac

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
[[ "$STYLE" == "talking-head" || "$STYLE" == "hybrid-ugc" ]] && mkdir -p "$VIDEO"/audio/{original,voice-changed}
[[ "$STYLE" == "ai-singing" ]] && mkdir -p "$VIDEO"/song "$VIDEO"/voiceover/slices

if [[ ! -e "$ROOT/AGENTS.md" ]]; then
  sed "s/{{STYLE}}/$STYLE/g" "$SKILL/templates/AGENTS.md" > "$ROOT/AGENTS.md"
  made AGENTS.md
fi

if [[ ! -e "$VIDEO/PROJECT_STATE.json" ]]; then
  PROJ_LABEL="$(basename "$ROOT")/$VIDEO_NAME"
  sed -e "s|\"<client>/<video-N>\"|\"$PROJ_LABEL\"|g" \
      -e "s|\"photoreal\"|\"$STYLE\"|g" \
      "$SKILL/templates/PROJECT_STATE.json" > "$VIDEO/PROJECT_STATE.json"
  made "${REL}PROJECT_STATE.json"
fi

[[ -e "$VIDEO/PLAN.md" ]] || echo "note: no PLAN.md yet in $VIDEO: plan the video with the video-plan skill first"

for m in scenes/stills-batch.json clips/clips-batch.json; do
  [[ -e "$VIDEO/$m" ]] || { printf '{\n  "jobs": []\n}\n' > "$VIDEO/$m"; made "$REL$m"; }
done

if [[ ! -e "$VIDEO/project.conf" ]]; then
  cat > "$VIDEO/project.conf" <<EOF
# Flow batch pacing (default concurrency 10-12; never 1-at-a-time unless chaining)
CONCURRENCY=10
RPM=12
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
Style:   $STYLE (references/styles/$STYLE.md)
Run tools with:  $VIDEO/scripts/make.py status
EOF
