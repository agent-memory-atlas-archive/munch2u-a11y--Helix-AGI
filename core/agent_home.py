"""Filesystem home and controller-owned room/module contract.

The home is data, never the source checkout or the neural checkpoint directory.
Module scripts are observed files; only native authorization can activate them.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile


def write_home_json(path, value):
    """Atomic replacement without following a predictable temporary symlink."""
    path = Path(path)
    if path.is_symlink():
        raise PermissionError(f"Controller home file cannot be a symlink: {path}")
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".home-write-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    if path.read_text() != payload:
        raise OSError(f"Home file read-back failed: {path}")


ROOMS = {
    "thinking": "An empty, quiet room for thinking.",
    "modules": "Operational scripts: web_search, web_read and a workshop-scoped terminal.",
    "bedroom": "Sleep and dream through the installed Helix dream engine.",
    "bedroom/closet": "Personal files and things to keep.",
    "workshop": "Experiments and Python scripts. Execution can write only inside this room.",
    "intakes": "Text observations of my surroundings, recorded by the controller.",
}
MODULES = {
    "web_search": {"room": "modules", "parameters": ["query"], "network": True},
    "web_read": {"room": "modules", "parameters": ["url"], "network": True},
    "terminal": {"room": "modules", "parameters": ["command"], "network": False},
    "sleep": {"room": "bedroom", "parameters": [], "network": False},
}


def prepare_home(config, *, state_directory=None):
    root = Path(config["mindscape"]["home"]).resolve()
    source = Path(__file__).resolve().parents[1]
    protected = [source / name for name in ("core", "brain", "memory", "llm", "tools", ".git", "config", "venv")]
    protected += [Path(config["mindscape"][name]).resolve() for name in ("package_path", "rwkv_model")]
    protected.append(Path(state_directory or source / config.get("data_dir", "data") / "mindscape").resolve())
    for path in protected:
        if root.is_relative_to(path) or path.is_relative_to(root):
            raise ValueError(f"Agent home must be separate from source/model/state: {path}")
    for room in ROOMS:
        path = root / room
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            raise PermissionError(f"Home room cannot redirect outside its home: {room}")
        path.mkdir(parents=True, exist_ok=True)
    scripts = {}
    for name, spec in MODULES.items():
        if name == "sleep":
            continue
        payload = (source / "core/home_modules" / f"{name}.py").read_bytes()
        destination = root / spec["room"] / f"{name}.py"
        if destination.is_symlink():
            raise PermissionError(f"Module cannot be a symlink: {name}")
        # Never overwrite an agent's file or silently run a changed built-in.
        if destination.exists() and destination.read_bytes() != payload:
            raise ValueError(f"Installed module differs from shipped script: {destination}")
        if not destination.exists():
            destination.write_bytes(payload)
        scripts[name] = {**spec, "path": str(destination), "sha256": hashlib.sha256(payload).hexdigest()}
    manifest = {"schema": "helix-agent-home-v1", "root": str(root), "rooms": ROOMS,
                "agent_name": config.get("agent_name", "Helix"),
                "modules": {**scripts, "sleep": MODULES["sleep"]},
                "modules_require_room": config["mindscape"]["modules_require_room"],
                "workshop": {"writable_root": str(root / "workshop"), "network": False,
                             "host_filesystem": False, "runtime_limit": None, "output_limit": None}}
    write_home_json(root / "home.json", manifest)
    write_home_json(root / "bedroom/sleep.json", {"module": "sleep", "parameters": {},
               "entrypoint": "installed BackgroundDaemon.run_dream_cycle",
               "execution": "native activate, using the current production memory stores"})
    return manifest
