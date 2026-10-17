"""Read-only paths for one selected agent; never infer identity by directory order."""
from __future__ import annotations
from contextlib import closing
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class RuntimePaths:
    data: Path
    home: Path

    @classmethod
    def from_config(cls, config, *, root, default_data=None):
        root = Path(root).resolve()
        def absolute(value):
            path = Path(value).expanduser()
            return (path if path.is_absolute() else root / path).resolve()
        data = absolute(config.get("data_dir") or default_data or "data")
        home = absolute(config.get("mindscape", {}).get("home") or data / "agent_home")
        return cls(data, home)

    def latest_checkpoint(self):
        joint = self.data / "mindscape/joint"
        pointer = joint / "LATEST.json"
        if pointer.exists():
            value = json.loads(pointer.read_text(encoding="utf-8"))
            selected = value["checkpoint"]
            if not isinstance(selected, str) or not selected or Path(selected).is_absolute():
                raise ValueError("Invalid native checkpoint location")
            checkpoint = (joint / selected).resolve()
            if not checkpoint.is_relative_to(joint.resolve()) or checkpoint == joint.resolve():
                raise ValueError("Invalid native checkpoint location")
            if not (checkpoint / "mind.sqlite").is_file():
                raise ValueError("Selected native checkpoint database is missing")
            return checkpoint
        # Compatibility for an explicitly selected older single-checkpoint store.
        return joint if (joint / "mind.sqlite").is_file() else None

    def workspace_position(self):
        checkpoint = self.latest_checkpoint()
        if checkpoint is None:
            return "."
        database = (checkpoint / "mind.sqlite").resolve()
        with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as connection:
            row = connection.execute("SELECT value FROM metadata WHERE key='agent_workspace_position'").fetchone()
        return str(row[0]) if row and row[0] else "."
