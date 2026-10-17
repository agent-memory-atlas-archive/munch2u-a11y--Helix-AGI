"""Credential-file parsing shared by wizard views; no environment mutation."""
from pathlib import Path


def read_credentials(path):
    """Keep the wizard's existing double-quote and last-key-wins semantics."""
    path = Path(path)
    credentials = {}
    if path.exists():
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    credentials[key.strip()] = value.strip().strip('"')
    return credentials
