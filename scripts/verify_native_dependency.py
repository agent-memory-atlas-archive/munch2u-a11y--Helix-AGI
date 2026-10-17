#!/usr/bin/env python3
"""Compare a native checkout with recorded source hashes; never import or patch it."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DEFAULT_MANIFEST = ROOT / "documents/audits/2026-10-17-native-body-operational/handoff/composition-manifest.json"


def verify_source(package, manifest):
    package = Path(package).expanduser().resolve()
    expected = json.loads(Path(manifest).read_text())["native_source"]["files"]
    if not isinstance(expected, dict) or not expected:
        raise ValueError("Manifest must contain native_source.files hashes")
    mismatches = []
    for relative, digest in sorted(expected.items()):
        path = (package / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(package):
            raise ValueError(f"Invalid manifest source path: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if actual != digest:
            mismatches.append({"path": relative, "expected": digest, "actual": actual})
    return {"package": str(package), "manifest": str(Path(manifest).resolve()),
            "checked_files": len(expected), "matches_recorded_source": not mismatches,
            "mismatches": mismatches, "scope": "Recorded files only; not a live runtime or weight check"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-path", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    from core.mindscape_config import configured_native_source
    package = args.package_path or configured_native_source()
    try:
        result = verify_source(package, args.manifest)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Recorded native source: {'MATCH' if result['matches_recorded_source'] else 'MISMATCH'} ({result['checked_files']} files)")
        for mismatch in result["mismatches"]:
            print(f"  {mismatch['path']}: {'missing' if mismatch['actual'] is None else 'changed'}")
        print(result["scope"])
    return 0 if result["matches_recorded_source"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
