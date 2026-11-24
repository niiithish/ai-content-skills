#!/usr/bin/env bash
# One-time setup: FilmCraft opens with its control port, and the filmcraft MCP drives that live app
# instead of a hidden headless copy (whose stale project overwrote the user's saved edits).
set -euo pipefail
PORT="${FILMCRAFT_CONTROL_PORT:-9876}"

# 0. Control token: FilmCraft refuses its bridge without FILMCRAFT_CONTROL_TOKEN (64 hex chars).
TOKEN="$HOME/.config/filmcraft/control-token"
mkdir -p "$(dirname "$TOKEN")"
[[ -s $TOKEN ]] || (umask 077; python3 -c "import secrets; print(secrets.token_hex(32))" > "$TOKEN")
chmod 600 "$TOKEN"

APP="$HOME/.local/opt/filmcraft-gpu/filmcraft"
[[ -x $APP ]] || APP="$(command -v filmcraft || true)"
[[ -n $APP ]] || { echo "filmcraft binary not found on PATH or ~/.local/opt/filmcraft-gpu/filmcraft" >&2; exit 1; }

mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/filmcraft-live" <<EOS
#!/bin/sh
FILMCRAFT_CONTROL_TOKEN="\$(cat "\$HOME/.config/filmcraft/control-token")" exec "$APP" --control "\${FILMCRAFT_CONTROL_PORT:-$PORT}" "\$@"
EOS
chmod 755 "$HOME/.local/bin/filmcraft-live"

# Update any existing user desktop launchers
for d in "$HOME"/.local/share/applications/*filmcraft*.desktop; do
  [[ -f $d ]] && sed -i -E "s|^Exec=[^ ]*filmcraft( --control [0-9]+)? |Exec=$HOME/.local/bin/filmcraft-live |" "$d"
done

# 1. Launcher override (optional if desktop entry exists)
SRC=""
for f in /usr/share/applications/ai.storyteller.filmcraft.desktop /opt/filmcraft/share/applications/ai.storyteller.filmcraft.desktop; do
  [[ -f $f ]] && { SRC=$f; break; }
done
if [[ -n $SRC ]]; then
  DST="$HOME/.local/share/applications/ai.storyteller.filmcraft.desktop"
  mkdir -p "$(dirname "$DST")"
  sed -E "s|^Exec=filmcraft |Exec=$HOME/.local/bin/filmcraft-live |" "$SRC" > "$DST"
  update-desktop-database "$(dirname "$DST")" 2>/dev/null || true
  echo "launcher: $(grep ^Exec= "$DST")"
else
  echo "note: system FilmCraft .desktop entry not found; launch FilmCraft with 'filmcraft-live <project.fcproj>'"
fi

# 2. MCP in bridge mode (supports Claude Code if installed; prints generic config for other agents)
CLI="$(command -v filmcraft-cli || echo /opt/filmcraft/bin/filmcraft-cli)"
TOKEN_VAL="$(cat "$TOKEN")"
if command -v claude >/dev/null 2>&1; then
  claude mcp remove filmcraft -s user >/dev/null 2>&1 || true
  claude mcp add -s user -e FILMCRAFT_CONTROL_TOKEN="$TOKEN_VAL" filmcraft -- "$CLI" mcp --bridge "127.0.0.1:$PORT"
  echo "Claude MCP: filmcraft -> $CLI mcp --bridge 127.0.0.1:$PORT (restart Claude Code)"
else
  echo "note: 'claude' CLI not found; skipping Claude MCP registration."
fi

cat <<EOF
Generic MCP config (for Codex / Gemini / Antigravity):
  command: $CLI
  args:    ["mcp", "--bridge", "127.0.0.1:$PORT"]
  env:     FILMCRAFT_CONTROL_TOKEN=<contents of $TOKEN>
Reopen FilmCraft via 'filmcraft-live' (or the app launcher) so it listens on 127.0.0.1:$PORT.
EOF
