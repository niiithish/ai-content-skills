#!/usr/bin/env bash
# Idempotent cross-agent installer for ai-content-skills (Linux / Arch / Omarchy).
#
# What it does:
#   1. Auto-discovers every flat skills/<name>/SKILL.md in this repo.
#   2. Symlinks each skill into:
#        ~/.agents/skills
#        ~/.claude/skills
#        ~/.gemini/skills
#        ~/.gemini/config/skills
#        ~/.codex/skills
#      Backs up non-symlink collisions cleanly and prunes stale/broken symlinks
#      that pointed into this repo.
#   3. Installs ~/.local/bin wrappers for transcribe, vocals, cartesia, rembg-cutout
#      (using this repo's resolved path) and filmcraft-update if present.
#   4. Installs caption fonts into ~/.local/share/fonts and refreshes fontconfig.
#   5. Checks ~/.claude/CLAUDE.md and ~/.gemini/GEMINI.md for transcribe + cartesia rules.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
BIN_DIR="$HOME/.local/bin"
FONT_DIR="$HOME/.local/share/fonts"
STAMP="$(date +%Y%m%d-%H%M%S)"

TARGET_DIRS=(
  "$HOME/.agents/skills"
  "$HOME/.claude/skills"
  "$HOME/.gemini/skills"
  "$HOME/.gemini/config/skills"
  "$HOME/.codex/skills"
)

if [[ ! -d "$SKILLS_SRC" ]]; then
  echo "ERROR: skills directory not found at $SKILLS_SRC" >&2
  exit 1
fi

# 1. Discover flat skills/<name>/SKILL.md
declare -a SKILLS=()
for d in "$SKILLS_SRC"/*/; do
  [[ -f "${d}SKILL.md" ]] || continue
  SKILLS+=("$(basename "$d")")
done

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  echo "ERROR: no skills found under $SKILLS_SRC" >&2
  exit 1
fi

echo "==> Discovered ${#SKILLS[@]} skills in $REPO_ROOT:"
printf '    %s\n' "${SKILLS[@]}"

# 2. Symlink into every agent harness directory & prune stale repo symlinks
for tdir in "${TARGET_DIRS[@]}"; do
  mkdir -p "$tdir"

  # Prune stale or broken symlinks that belonged to this repo (or broken ../../.agents/skills links)
  for entry in "$tdir"/* "$tdir"/.[!.]*; do
    [[ -L "$entry" ]] || continue
    raw_target="$(readlink "$entry" || true)"
    resolved_target="$(readlink -f "$entry" 2>/dev/null || true)"
    entry_name="$(basename "$entry")"

    is_from_repo=0
    if [[ "$raw_target" == "$REPO_ROOT/skills/"* ]] || [[ "$resolved_target" == "$REPO_ROOT/skills/"* ]]; then
      is_from_repo=1
    elif [[ "$raw_target" == *"/.agents/skills/"* && ! -e "$entry" ]]; then
      is_from_repo=1
    fi

    if [[ $is_from_repo -eq 1 ]]; then
      if [[ ! -f "$SKILLS_SRC/$entry_name/SKILL.md" ]]; then
        echo "  [prune] $entry -> $raw_target"
        rm -f "$entry"
      fi
    fi
  done

  # Link every active skill
  for name in "${SKILLS[@]}"; do
    src="$SKILLS_SRC/$name"
    dst="$tdir/$name"
    if [[ -e "$dst" && ! -L "$dst" ]]; then
      backup="${dst}.bak-${STAMP}"
      echo "  [backup] $dst -> $backup"
      mv "$dst" "$backup"
    fi
    ln -sfn "$src" "$dst"
  done
  echo "  [ok] linked ${#SKILLS[@]} skills into $tdir"
done

# 3. Install ~/.local/bin CLI wrappers (resolved to $REPO_ROOT, zero hardcoded user paths)
mkdir -p "$BIN_DIR"

write_wrapper() {
  local name="$1"
  local content="$2"
  local path="$BIN_DIR/$name"
  printf '%s\n' "$content" > "$path"
  chmod 755 "$path"
  echo "  [bin] installed $path"
}

echo "==> Installing CLI wrappers in $BIN_DIR"

if [[ -f "$SKILLS_SRC/transcribe/scripts/transcribe.py" ]]; then
  write_wrapper "transcribe" "#!/usr/bin/env sh
# Local speech-to-text with word timestamps (Parakeet GPU/CPU + faster-whisper).
PY=\"\$HOME/.local/share/transcribe-venv/bin/python\"
[ -x \"\$PY\" ] || PY=\"python3\"
exec \"\$PY\" \"$SKILLS_SRC/transcribe/scripts/transcribe.py\" \"\$@\""
fi

if [[ -f "$SKILLS_SRC/transcribe/scripts/vocals.py" ]]; then
  write_wrapper "vocals" "#!/usr/bin/env sh
# Local vocal stem separation (MelBand RoFormer on Intel Arc XPU / CPU).
exec python3 \"$SKILLS_SRC/transcribe/scripts/vocals.py\" \"\$@\""
fi

if [[ -f "$SKILLS_SRC/cartesia-tts/scripts/cartesia.py" ]]; then
  write_wrapper "cartesia" "#!/usr/bin/env sh
# Cartesia Sonic 3.6 TTS CLI.
exec python3 \"$SKILLS_SRC/cartesia-tts/scripts/cartesia.py\" \"\$@\""
fi

if [[ -f "$SKILLS_SRC/media-utils/scripts/rembg_cutout.py" ]]; then
  write_wrapper "rembg-cutout" "#!/usr/bin/env sh
# Local background removal wrapper using ~/.local/share/rembg/models.
PY=\"\$HOME/.local/share/rembg-venv/bin/python\"
[ -x \"\$PY\" ] || PY=\"python3\"
exec \"\$PY\" \"$SKILLS_SRC/media-utils/scripts/rembg_cutout.py\" \"\$@\""
fi

# filmcraft-update (check new filmcraft-edit path, then legacy edit-style path)
FC_UPD=""
for cand in \
  "$SKILLS_SRC/filmcraft-edit/scripts/filmcraft-update" \
  "$SKILLS_SRC/filmcraft-edit/scripts/setup/filmcraft-update" \
  "$SKILLS_SRC/edit-style/scripts/setup/filmcraft-update"; do
  if [[ -f "$cand" ]]; then
    FC_UPD="$cand"
    break
  fi
done
if [[ -n "$FC_UPD" ]]; then
  if [[ -e "$BIN_DIR/filmcraft-update" && ! -L "$BIN_DIR/filmcraft-update" ]]; then
    echo "  [keep] existing custom $BIN_DIR/filmcraft-update left untouched (repo copy at $FC_UPD)"
  else
    ln -sfn "$FC_UPD" "$BIN_DIR/filmcraft-update"
    echo "  [bin] linked $BIN_DIR/filmcraft-update -> $FC_UPD"
  fi
fi

# 4. Install caption fonts
if [[ -d "$SKILLS_SRC/captions-filmcraft/fonts" ]]; then
  mkdir -p "$FONT_DIR"
  copied=0
  for font in "$SKILLS_SRC/captions-filmcraft/fonts"/*.ttf "$SKILLS_SRC/captions-filmcraft/fonts"/*.otf; do
    [[ -f "$font" ]] || continue
    cp -u "$font" "$FONT_DIR/"
    copied=$((copied + 1))
  done
  if [[ $copied -gt 0 ]]; then
    echo "==> Installed/updated $copied font(s) in $FONT_DIR"
    if command -v fc-cache >/dev/null 2>&1; then
      fc-cache -f "$FONT_DIR" >/dev/null 2>&1 || true
    fi
  fi
fi

# 5. Remind / check global agent rules (~/.claude/CLAUDE.md and ~/.gemini/GEMINI.md)
echo "==> Checking global agent rules"
check_rule_file() {
  local f="$1"
  if [[ ! -f "$f" ]]; then
    echo "  [note] $f does not exist — consider adding global transcribe + cartesia rules."
    return
  fi
  local missing=()
  grep -qi 'transcribe' "$f" || missing+=("transcribe (local Parakeet STT)")
  grep -qi 'cartesia' "$f" || missing+=("cartesia (Sonic 3.6 TTS)")
  if [[ ${#missing[@]} -eq 0 ]]; then
    echo "  [ok] $f includes both transcribe and cartesia rules."
  else
    echo "  [sync] $f is missing global rule(s): ${missing[*]}"
  fi
}

check_rule_file "$HOME/.claude/CLAUDE.md"
check_rule_file "$HOME/.gemini/GEMINI.md"

echo ""
echo "Done. Run 'bash $REPO_ROOT/scripts/doctor.sh' to verify your environment."
