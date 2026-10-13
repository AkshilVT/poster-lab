"""Poster Lab storage: saved remixes, uploaded photos, subject cut-outs.

One entry point, `main(op=...)`:
  load    poster            -> the poster's saved changes ({} when none)
  save    poster, data      -> writes them (data = JSON text)
  upload  data              -> stores a data: URL image, returns {"path"}
  cutout  path              -> Apple Vision subject cut-out PNG, returns {"path"}
"""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, ".fused", "data")
CACHE = os.path.join(HERE, ".fused", "cache")
REMIX = os.path.join(DATA, "remix")
UPLOADS = os.path.join(DATA, "uploads")
CUTOUTS = os.path.join(CACHE, "cutouts-v1")
TOOL_SRC = os.path.join(HERE, "tools", "cutout.swift")
TOOL_BIN = os.path.join(CACHE, "bin", "cutout")


def _write(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp-{os.getpid()}"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


def _rel(path: str) -> str:
    return os.path.relpath(path, HERE)


def _inside(path: str) -> str:
    full = os.path.realpath(os.path.join(HERE, path))
    if not full.startswith(os.path.realpath(HERE) + os.sep):
        raise ValueError(f"path outside the app: {path}")
    return full


def _poster_file(poster: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", poster or ""):
        raise ValueError(f"bad poster id: {poster!r}")
    return os.path.join(REMIX, poster + ".json")


def _cutout_tool() -> str:
    """Compile tools/cutout.swift once per machine (≈10 s), cache the binary."""
    if os.path.exists(TOOL_BIN) and os.path.getmtime(TOOL_BIN) >= os.path.getmtime(TOOL_SRC):
        return TOOL_BIN
    swiftc = shutil.which("swiftc") or "/usr/bin/swiftc"
    if not os.path.exists(swiftc):
        raise RuntimeError("Subject cut-outs need Apple's Command Line Tools (xcode-select --install)")
    os.makedirs(os.path.dirname(TOOL_BIN), exist_ok=True)
    tmp = f"{TOOL_BIN}.tmp-{os.getpid()}"
    proc = subprocess.run([swiftc, "-O", "-o", tmp, TOOL_SRC], capture_output=True, text=True, timeout=55)
    if proc.returncode != 0:
        raise RuntimeError("couldn't build the cut-out tool: " + (proc.stderr or proc.stdout)[-400:])
    os.replace(tmp, TOOL_BIN)
    return TOOL_BIN


def _cutout(path: str) -> dict:
    src = _inside(path)
    with open(src, "rb") as f:
        digest = hashlib.sha1(f.read()).hexdigest()[:16]
    out = os.path.join(CUTOUTS, digest + ".png")
    if not os.path.exists(out):
        os.makedirs(CUTOUTS, exist_ok=True)
        tmp = f"{out}.tmp-{os.getpid()}.png"
        proc = subprocess.run([_cutout_tool(), src, tmp], capture_output=True, text=True, timeout=55)
        if proc.returncode == 3:
            raise RuntimeError("no subject found in that photo")
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or "cut-out failed").strip()[-300:])
        os.replace(tmp, out)
    return {"path": _rel(out)}


def main(op: str = "load", poster: str = "", data: str = "", path: str = ""):
    if op == "load":
        file = _poster_file(poster)
        if not os.path.exists(file):
            return {}
        try:
            with open(file, encoding="utf-8") as f:
                remix = json.load(f)
        except (OSError, ValueError):
            return {}
        # a cleared cache drops cut-outs; rebuild any that went missing
        for src in (remix.get("sources") or {}).values():
            cut = src.get("cut")
            if cut and cut.startswith(".fused/cache/") and not os.path.exists(os.path.join(HERE, cut)):
                try:
                    src["cut"] = _cutout(src["src"])["path"]
                except Exception:
                    src["cut"] = None
        return remix

    if op == "save":
        file = _poster_file(poster)
        remix = json.loads(data or "{}")
        if not isinstance(remix, dict):
            raise ValueError("remix must be a JSON object")
        if remix:
            _write(file, json.dumps(remix, indent=1).encode())
        elif os.path.exists(file):
            os.remove(file)
        return {"ok": True}

    if op == "upload":
        m = re.match(r"data:image/(png|jpeg|webp|gif);base64,(.+)$", data or "", re.S)
        if not m:
            raise ValueError("expected a data:image/... URL")
        raw = base64.b64decode(m.group(2))
        ext = {"jpeg": "jpg"}.get(m.group(1), m.group(1))
        out = os.path.join(UPLOADS, hashlib.sha1(raw).hexdigest()[:16] + "." + ext)
        if not os.path.exists(out):
            _write(out, raw)
        return {"path": _rel(out)}

    if op == "cutout":
        return _cutout(path)

    raise ValueError(f"unknown op {op!r}")
