#!/usr/bin/env bash
# One-time setup: FilmCraft opens with its control port, and the filmcraft MCP drives that live app
# instead of a hidden headless copy (whose stale project overwrote the user's saved edits).
set -euo pipefail
PORT="${FILMCRAFT_CONTROL_PORT:-9876}"
SRC=""
for f in /usr/share/applications/ai.storyteller.filmcraft.desktop /opt/filmcraft/share/applications/ai.storyteller.filmcraft.desktop; do
  [[ -f $f ]] && { SRC=$f; break; }
done
[[ -n $SRC ]] || { echo "FilmCraft's desktop entry not found; is FilmCraft installed?" >&2; exit 1; }

# 1. Launcher override (a user entry with the same name wins over the system one)
DST="$HOME/.local/share/applications/ai.storyteller.filmcraft.desktop"
mkdir -p "$(dirname "$DST")"
sed -E "s|^Exec=filmcraft |Exec=filmcraft --control $PORT |" "$SRC" > "$DST"
update-desktop-database "$(dirname "$DST")" 2>/dev/null || true
echo "launcher: $(grep ^Exec= "$DST")"

# 2. MCP in bridge mode (user scope); Claude Code must be restarted to pick it up
CLI="$(command -v filmcraft-cli || echo /opt/filmcraft/bin/filmcraft-cli)"
claude mcp remove filmcraft -s user >/dev/null 2>&1 || true
claude mcp add -s user filmcraft -- "$CLI" mcp --bridge "127.0.0.1:$PORT"
echo "MCP: filmcraft -> $CLI mcp --bridge 127.0.0.1:$PORT (restart Claude Code)"
echo "Reopen FilmCraft from the launcher so it listens on $PORT."
