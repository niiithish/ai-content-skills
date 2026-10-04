#!/bin/bash
# One-time setup: lets an agent drive FREE DaVinci Resolve 21.1+ on Linux through
# samuelgursky/davinci-resolve-mcp. Free 21.1+ blocks external scripting, so the MCP's
# Resolve module is swapped for a shim that talks to a Lua script running inside Resolve.
set -euo pipefail
here="$(cd "$(dirname "$0")/../bridge" && pwd)"
mcp="$HOME/.local/share/davinci-resolve-mcp"
lib=/opt/resolve/libs/Fusion/fusionscript.so

# 1. The Lua side, run from Workspace > Scripts > claude_bridge.
scripts="$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Utility"
mkdir -p "$scripts" "$HOME/.cache/claude-resolve-bridge"
cp "$here/claude_bridge.lua" "$scripts/"

# 2. The MCP server, if missing.
if [ ! -f "$mcp/src/server.py" ]; then
  git clone --depth 1 https://github.com/samuelgursky/davinci-resolve-mcp "$mcp"
fi
if [ ! -x "$mcp/venv/bin/python" ]; then
  python3 -m venv "$mcp/venv"
  "$mcp/venv/bin/pip" install -q -r "$mcp/requirements.txt"
fi

# 3. The Python shim the server imports instead of Resolve's own module.
mkdir -p "$mcp/lua_bridge/Modules"
cp "$here/resolve_lua_bridge.py" "$here/DaVinciResolveScript.py" "$mcp/lua_bridge/Modules/"

echo "Installed. Register the MCP with your agent:"
echo
echo "  Claude Code:"
echo "    claude mcp add davinci-resolve -s user -e RESOLVE_SCRIPT_API=$mcp/lua_bridge -e RESOLVE_SCRIPT_LIB=$lib -- $mcp/venv/bin/python $mcp/src/server.py"
echo "  Codex:"
echo "    codex mcp add davinci-resolve --env RESOLVE_SCRIPT_API=$mcp/lua_bridge --env RESOLVE_SCRIPT_LIB=$lib -- $mcp/venv/bin/python $mcp/src/server.py"
echo
echo "Then in Resolve: Workspace > Scripts > claude_bridge (once per Resolve launch)."
