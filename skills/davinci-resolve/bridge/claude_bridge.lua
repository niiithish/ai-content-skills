-- claude_bridge.lua — lets an outside process drive DaVinci Resolve (free) through Lua.
--
-- Resolve free 21.1+ refuses external scripting and no longer runs Python from the
-- Scripts menu, and in-app Lua has no io/require/sockets. What it does have:
--   in:  dofile()        — the client writes each request as a Lua file
--   out: fu:SavePrefs()  — writes the prefs, including our hex-encoded reply,
--                          to a file the client picks up (printerr to the log
--                          is buffered for seconds, so it is not used)
-- Run from Workspace > Scripts > claude_bridge. Client: resolve_lua_bridge.py.

local HOME = os.getenv("HOME")
local DIR = HOME .. "/.cache/claude-resolve-bridge/"
local SESSION = (bmd.createuuid():gsub("[^%w]", ""))
local POLL = 0.02

local handles = { [0] = resolve }
local next_handle = 1

local function register(obj)
  local id = next_handle
  next_handle = id + 1
  handles[id] = obj
  return id
end

local function type_name(v)
  return (tostring(v):match("^([%w_]+)")) or type(v)
end

local escapes = { ['"'] = '\\"', ["\\"] = "\\\\", ["\n"] = "\\n", ["\r"] = "\\r", ["\t"] = "\\t" }
local function json_string(s)
  return '"' .. s:gsub('[%c"\\]', function(c)
    return escapes[c] or string.format("\\u%04x", c:byte())
  end) .. '"'
end

local encode
function encode(v, depth)
  depth = depth or 0
  local t = type(v)
  if v == nil then return "null"
  elseif t == "boolean" then return tostring(v)
  elseif t == "number" then
    if v ~= v or v == math.huge or v == -math.huge then return "null" end
    if v == math.floor(v) and math.abs(v) < 2^53 then return string.format("%d", v) end
    return string.format("%.17g", v)
  elseif t == "string" then return json_string(v)
  elseif t == "table" then
    if depth > 64 then return "null" end
    local parts = {}
    for k, val in pairs(v) do
      parts[#parts + 1] = "[" .. encode(k, depth + 1) .. "," .. encode(val, depth + 1) .. "]"
    end
    return '{"__t":[' .. table.concat(parts, ",") .. "]}"
  elseif t == "function" then return "null"
  else
    return '{"__h":' .. register(v) .. ',"__n":' .. json_string(type_name(v)) .. "}"
  end
end

local function decode_arg(v)
  if type(v) ~= "table" then return v end
  if v.__h then return handles[v.__h] end
  local out = {}
  for k, val in pairs(v) do out[k] = decode_arg(val) end
  return out
end

local function hex(s)
  return (s:gsub(".", function(c) return string.format("%02x", c:byte()) end))
end

-- Writes `value` to `path` as the prefs key Global.ClaudeBridge.Out, then clears it
-- so replies never linger in Fusion's saved prefs.
local function emit(path, value)
  fu:SetPrefs("Global.ClaudeBridge.Out", value)
  fu:SavePrefs(path)
  fu:SetPrefs("Global.ClaudeBridge.Out", "")
end

local function reply(seq, body)
  emit(DIR .. SESSION .. "_" .. seq .. ".out", hex(body))
end

local function fail(msg)
  return '{"ok":false,"error":' .. json_string(tostring(msg)) .. "}"
end

local running = true

local function handle(req)
  if type(req) ~= "table" then return fail("request is not a table") end
  for _, id in ipairs(req.release or {}) do
    if id ~= 0 then handles[id] = nil end
  end
  local op = req.op
  if op == "ping" then
    return '{"ok":true,"result":' .. json_string(SESSION) .. "}"
  elseif op == "shutdown" then
    running = false
    return '{"ok":true,"result":true}'
  elseif op == "release" then
    return '{"ok":true,"result":true}'
  end
  local obj = handles[req.obj or 0]
  if obj == nil then return fail("stale handle " .. tostring(req.obj)) end
  if op == "has" then
    local ok, member = pcall(function() return obj[req.name] end)
    return '{"ok":true,"result":' .. tostring(ok and member ~= nil) .. "}"
  elseif op == "get" then
    local ok, val = pcall(function() return obj[req.name] end)
    if not ok then return fail(val) end
    return '{"ok":true,"result":' .. encode(val) .. "}"
  elseif op == "call" then
    local args = decode_arg(req.args or {})
    local n = req.n or 0
    local ok, res = pcall(function()
      return obj[req.name](obj, unpack(args, 1, n))
    end)
    if not ok then return fail(res) end
    return '{"ok":true,"result":' .. encode(res) .. "}"
  end
  return fail("unknown op " .. tostring(op))
end

-- Only the newest bridge serves; an older one sees the change and bows out.
fu:SetPrefs("Global.ClaudeBridge.Active", SESSION)
emit(DIR .. "bridge.prefs", SESSION)
local seq, ticks = 1, 0
while running do
  ticks = ticks + 1
  if ticks % 50 == 0 and fu:GetPrefs("Global.ClaudeBridge.Active") ~= SESSION then break end
  local path = DIR .. SESSION .. "_" .. seq .. ".lua"
  if bmd.fileexists(path) then
    local ok, req = pcall(dofile, path)
    local body
    if ok then
      local hok, res = pcall(handle, req)
      body = hok and res or fail(res)
    else
      body = fail("bad request file: " .. tostring(req))
    end
    reply(seq, body)
    seq = seq + 1
  else
    bmd.wait(POLL)
  end
end
if fu:GetPrefs("Global.ClaudeBridge.Active") == SESSION then
  fu:SetPrefs("Global.ClaudeBridge.Active", "")
  emit(DIR .. "bridge.prefs", "")
end
