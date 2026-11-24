#!/usr/bin/env bash
# Environment & portability health check for ai-content-skills.
# Emits PASS / WARN / FAIL with exact actionable fix commands.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

if [[ -t 1 ]]; then
  G=$'\e[32m'; Y=$'\e[33m'; R=$'\e[31m'; B=$'\e[1m'; N=$'\e[0m'
else
  G=''; Y=''; R=''; B=''; N=''
fi

pass() { PASS_COUNT=$((PASS_COUNT + 1)); printf "${G}[PASS]${N} %s\n" "$1"; }
warn() { WARN_COUNT=$((WARN_COUNT + 1)); printf "${Y}[WARN]${N} %s\n" "$1"; [[ -n "${2:-}" ]] && printf "       fix: %s\n" "$2"; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf "${R}[FAIL]${N} %s\n" "$1"; [[ -n "${2:-}" ]] && printf "       fix: %s\n" "$2"; }

section() { printf "\n${B}=== %s ===${N}\n" "$1"; }

# 1. Skill symlinks across all agent harnesses
section "1. Skill Symlinks"
declare -a SKILLS=()
for d in "$SKILLS_SRC"/*/; do
  [[ -f "${d}SKILL.md" ]] && SKILLS+=("$(basename "$d")")
done

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  fail "No skills found under $SKILLS_SRC"
else
  pass "Found ${#SKILLS[@]} flat skill(s) in repo"
fi

HARNESS_DIRS=(
  "$HOME/.agents/skills"
  "$HOME/.claude/skills"
  "$HOME/.gemini/skills"
  "$HOME/.gemini/config/skills"
  "$HOME/.codex/skills"
)

for hdir in "${HARNESS_DIRS[@]}"; do
  missing=()
  for s in "${SKILLS[@]}"; do
    p="$hdir/$s"
    if [[ ! -L "$p" ]] || [[ "$(readlink -f "$p" 2>/dev/null || true)" != "$SKILLS_SRC/$s" ]]; then
      missing+=("$s")
    fi
  done
  if [[ ${#missing[@]} -eq 0 ]]; then
    pass "$hdir: all ${#SKILLS[@]} skills linked"
  else
    warn "$hdir: ${#missing[@]} missing/drifted (${missing[*]})" "bash $REPO_ROOT/scripts/install.sh"
  fi
done

# 2. Core CLI tools & Intel Arc GPU acceleration
section "2. CLI Tools & GPU Acceleration"

check_cmd() {
  local cmd="$1"
  local level="$2"
  local fix="$3"
  if command -v "$cmd" >/dev/null 2>&1; then
    pass "$cmd -> $(command -v "$cmd")"
  elif [[ "$level" == "fail" ]]; then
    fail "$cmd not found on PATH" "$fix"
  else
    warn "$cmd not found on PATH" "$fix"
  fi
}

check_cmd python3       fail "sudo pacman -S python"
check_cmd ffmpeg        fail "sudo pacman -S ffmpeg"
check_cmd flow          fail "uv tool install --editable ~/Work/labflow"
check_cmd filmcraft-cli warn "Install FilmCraft or run filmcraft-update"
check_cmd transcribe    fail "bash $REPO_ROOT/scripts/install.sh"
check_cmd vocals        warn "bash $REPO_ROOT/scripts/install.sh"
check_cmd cartesia      warn "bash $REPO_ROOT/scripts/install.sh"
check_cmd rembg-cutout  warn "bash $REPO_ROOT/scripts/install.sh"
check_cmd cloudflared   warn "sudo pacman -S cloudflared  (needed for local image tunnels to ElevenLabs)"
check_cmd chromium      warn "sudo pacman -S chromium     (needed for video-plan PDF export)"
check_cmd magick        warn "sudo pacman -S imagemagick"

# Intel VA-API check
if [[ -e /dev/dri/renderD128 ]]; then
  if command -v ffmpeg >/dev/null 2>&1 && grep -q 'h264_vaapi' <<< "$(ffmpeg -hide_banner -encoders 2>/dev/null || true)"; then
    pass "VA-API render node (/dev/dri/renderD128) + ffmpeg h264_vaapi available"
  else
    warn "/dev/dri/renderD128 exists, but ffmpeg h264_vaapi encoder not detected" "sudo pacman -S ffmpeg libva-utils intel-media-driver"
  fi
else
  warn "/dev/dri/renderD128 not present (no Intel/AMD VA-API GPU node)" "Ensure GPU driver (intel-media-driver) is loaded"
fi

# 3. Local models, venvs & private credentials
section "3. Models, Venvs & Configs"

check_path() {
  local p="$1"
  local label="$2"
  local level="$3"
  local fix="$4"
  if [[ -e "$p" ]]; then
    pass "$label ($p)"
  elif [[ "$level" == "fail" ]]; then
    fail "$label missing ($p)" "$fix"
  else
    warn "$label missing ($p)" "$fix"
  fi
}

check_path "$HOME/.local/share/parakeet-cpp/bin/parakeet-cli" "Parakeet Vulkan CLI" warn "Restore ~/.local/share/parakeet-cpp or see docs/new-ssd-migration.md"
check_path "$HOME/.local/share/transcribe-venv/bin/python"    "Transcribe Python venv" warn "uv venv ~/.local/share/transcribe-venv --python 3.12 && uv pip install -p ~/.local/share/transcribe-venv 'onnx-asr[hub]' onnxruntime faster-whisper numpy"
check_path "$HOME/.local/share/separate-models"               "MelBand RoFormer vocal models" warn "Restore ~/.local/share/separate-models or run 'vocals' once to download"
check_path "$HOME/.local/share/separate-xpu-venv/bin/python"  "Vocal separation XPU venv" warn "Create ~/.local/share/separate-xpu-venv with PyTorch XPU + audio-separator"
check_path "$HOME/.local/share/rembg/models"                  "rembg cutout models" warn "Restore ~/.local/share/rembg/models (birefnet-general, isnet-general-use)"
check_path "$HOME/.config/cartesia/api_key"                   "Cartesia API key" warn "Save key to ~/.config/cartesia/api_key (chmod 600)"
check_path "$HOME/.config/labflow"                            "Labflow profiles/config" warn "Restore ~/.config/labflow or run 'flow account add'"
check_path "$HOME/.config/filmcraft/control-token"            "FilmCraft bridge token" warn "bash $SKILLS_SRC/filmcraft-edit/scripts/setup.sh"

# 4. Fonts & Global Rules
section "4. Fonts & Global Rules"

if command -v fc-list >/dev/null 2>&1; then
  FONTS_LIST="$(fc-list 2>/dev/null || true)"
  if grep -qi 'TikTok' <<< "$FONTS_LIST" && grep -qi 'Montserrat' <<< "$FONTS_LIST"; then
    pass "Caption fonts installed (TikTok Sans + Montserrat)"
  else
    warn "Missing TikTok Sans or Montserrat in fontconfig" "bash $REPO_ROOT/scripts/install.sh"
  fi
else
  warn "fc-list not found; cannot verify installed fonts" "sudo pacman -S fontconfig"
fi

for rfile in "$HOME/.claude/CLAUDE.md" "$HOME/.gemini/GEMINI.md"; do
  if [[ -f "$rfile" ]] && grep -qi 'transcribe' "$rfile" && grep -qi 'cartesia' "$rfile"; then
    pass "Global rules synced in $rfile"
  else
    warn "Global rules incomplete/missing in $rfile (expected transcribe + cartesia)" "Sync ~/.claude/CLAUDE.md and ~/.gemini/GEMINI.md"
  fi
done

# Summary
printf "\n${B}Summary:${N} ${G}%d PASS${N} | ${Y}%d WARN${N} | ${R}%d FAIL${N}\n" "$PASS_COUNT" "$WARN_COUNT" "$FAIL_COUNT"
if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
fi
exit 0
