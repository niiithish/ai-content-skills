"""Client for claude_bridge.lua — drives DaVinci Resolve free through in-app Lua.

Requests go in as Lua files that the bridge `dofile`s; replies come back as
prefs files the bridge saves with `fu:SavePrefs`, carrying the JSON reply
hex-encoded in Global.ClaudeBridge.Out. Objects cross as handles, so `ResolveObject` behaves like the
objects Blackmagic's own Python module returns.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import threading
import time
import weakref

HOME = os.path.expanduser("~")
DIR = os.path.join(HOME, ".cache", "claude-resolve-bridge")
BRIDGE_FILE = os.path.join(DIR, "bridge.prefs")
LOCK = os.path.join(DIR, "client.lock")
STATE = os.path.join(DIR, "state.json")
TIMEOUT = float(os.environ.get("CLAUDE_BRIDGE_TIMEOUT", "600"))
# The bridge's value sits in the saved prefs as:  ClaudeBridge = { ... Out = "<hex>" ...
_OUT_RE = re.compile(r'ClaudeBridge\s*=\s*\{[^}]*?\bOut\s*=\s*"([0-9a-zA-Z]*)"', re.S)


class BridgeError(RuntimeError):
    pass


def _lua(value) -> str:
    """Python value -> Lua literal."""
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, ResolveObject):
        return "{__h=%d}" % object.__getattribute__(value, "_h")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return "nil"
        return repr(value)
    if isinstance(value, str):
        out = []
        for byte in value.encode("utf-8"):
            ch = chr(byte)
            if 32 <= byte < 127 and ch not in '"\\':
                out.append(ch)
            else:
                out.append("\\%03d" % byte)
        return '"' + "".join(out) + '"'
    if isinstance(value, (list, tuple)):
        return "{" + ",".join("[%d]=%s" % (i + 1, _lua(v)) for i, v in enumerate(value)) + "}"
    if isinstance(value, dict):
        return "{" + ",".join("[%s]=%s" % (_lua(k), _lua(v)) for k, v in value.items() if v is not None) + "}"
    raise TypeError(f"cannot send {type(value).__name__} to Resolve")


class _Client:
    def __init__(self) -> None:
        os.makedirs(DIR, exist_ok=True)
        self._lock = threading.Lock()
        self._released: list = []
        self._has_cache: dict = {}

    # -- bridge output -----------------------------------------------------

    @staticmethod
    def _read_out(path: str):
        """The Global.ClaudeBridge.Out value from a prefs file the bridge saved."""
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        match = _OUT_RE.search(text)
        return match.group(1) if match else None

    def _current_session(self):
        try:
            value = self._read_out(BRIDGE_FILE)
        except OSError:
            return None
        return value or None

    def _load_state(self):
        try:
            with open(STATE) as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return {}

    def _save_state(self, state) -> None:
        tmp = STATE + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(state, fh)
        os.replace(tmp, STATE)

    def _await_reply(self, out_path: str, deadline: float):
        while True:
            if os.path.exists(out_path):
                try:
                    value = self._read_out(out_path)
                except OSError:
                    value = None
                if value is not None:  # None: file still being written
                    return json.loads(bytes.fromhex(value).decode("utf-8", "replace"))
            if time.monotonic() > deadline:
                raise BridgeError(
                    "no reply from Resolve — is claude_bridge running (Workspace > Scripts > claude_bridge)?"
                )
            time.sleep(0.005)

    # -- requests ------------------------------------------------------------

    def request(self, op: str, timeout: float = TIMEOUT, **fields):
        with self._lock, open(LOCK, "w") as lockfh:
            fcntl.flock(lockfh, fcntl.LOCK_EX)
            state = self._load_state()
            session = self._current_session()
            if session is None:
                raise BridgeError(
                    "claude_bridge is not running — in Resolve: Workspace > Scripts > claude_bridge"
                )
            if state.get("session") != session:
                state = {"session": session, "seq": 1}
                self._has_cache.clear()
            seq = state["seq"]
            body = {"op": op, **fields}
            if self._released:
                body["release"], self._released = self._released, []
            path = os.path.join(DIR, f"{session}_{seq}.lua")
            out_path = os.path.join(DIR, f"{session}_{seq}.out")
            tmp = path + ".tmp"
            with open(tmp, "w") as fh:
                fh.write("return " + _lua(body))
            os.replace(tmp, path)
            try:
                reply = self._await_reply(out_path, time.monotonic() + timeout)
            finally:
                for leftover in (path, out_path):
                    try:
                        os.remove(leftover)
                    except OSError:
                        pass
            self._save_state({"session": session, "seq": seq + 1})
        if not reply.get("ok"):
            raise BridgeError(reply.get("error", "unknown error"))
        return _decode(reply.get("result"))

    def release(self, handle: int) -> None:
        self._released.append(handle)

    def has(self, handle: int, type_name: str, name: str) -> bool:
        key = (type_name, name)
        if key not in self._has_cache:
            self._has_cache[key] = bool(self.request("has", obj=handle, name=name))
        return self._has_cache[key]

    def alive(self) -> bool:
        try:
            self.request("ping", timeout=5)
            return True
        except BridgeError:
            return False


CLIENT = _Client()


def _decode(value):
    if isinstance(value, dict):
        if "__h" in value:
            return ResolveObject(value["__h"], value.get("__n", "Object"))
        if "__t" in value:
            pairs = [(_decode(k), _decode(v)) for k, v in value["__t"]]
            # Resolve tags its array tables with __flags; untagged tables are dicts.
            is_list = any(k == "__flags" for k, _ in pairs)
            pairs = [(k, v) for k, v in pairs if k != "__flags"]
            if is_list:
                return [v for _, v in sorted(pairs, key=lambda p: p[0])]
            return dict(pairs)
    return value


class _Method:
    __slots__ = ("_obj", "_name")

    def __init__(self, obj, name):
        self._obj, self._name = obj, name

    def __call__(self, *args):
        handle = object.__getattribute__(self._obj, "_h")
        return CLIENT.request("call", obj=handle, name=self._name, n=len(args), args=list(args))

    def __repr__(self):
        return f"<Resolve method {self._name}>"


class ResolveObject:
    """Stand-in for an object from Blackmagic's DaVinciResolveScript module."""

    __slots__ = ("_h", "_n", "__weakref__")

    def __init__(self, handle: int, type_name: str):
        object.__setattr__(self, "_h", handle)
        object.__setattr__(self, "_n", type_name)
        if handle:
            weakref.finalize(self, CLIENT.release, handle)

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        handle = object.__getattribute__(self, "_h")
        type_name = object.__getattribute__(self, "_n")
        if name.isupper():  # constants such as EXPORT_EDL
            return CLIENT.request("get", obj=handle, name=name)
        if not CLIENT.has(handle, type_name, name):
            raise AttributeError(f"'{type_name}' object has no attribute '{name}'")
        return _Method(self, name)

    def __repr__(self):
        return f"{object.__getattribute__(self, '_n')} (lua handle {object.__getattribute__(self, '_h')})"

    def __eq__(self, other):
        return isinstance(other, ResolveObject) and object.__getattribute__(other, "_h") == object.__getattribute__(self, "_h")

    def __hash__(self):
        return hash(object.__getattribute__(self, "_h"))

    def __bool__(self):
        return True


def scriptapp(app: str = "Resolve", *_args):
    if not CLIENT.alive():
        return None
    root = ResolveObject(0, "Resolve")
    if app.lower() == "resolve":
        return root
    if app.lower() == "fusion":
        return root.Fusion()
    return None
