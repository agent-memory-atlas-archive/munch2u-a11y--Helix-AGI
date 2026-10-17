#!/usr/bin/env python3
"""Read-only installation preflight; never loads models or creates agent state."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import importlib.util
import json
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


@dataclass(frozen=True)
class Check:
    component: str
    status: str
    detail: str


def exit_code(checks):
    return int(any(check.status == "FAIL" for check in checks))


def collect_checks(root=REPO_ROOT):
    """Inspect the selected installation without importing providers or neural code."""
    root = Path(root).resolve()
    checks = [Check("Python", "PASS" if sys.version_info >= (3, 11) else "FAIL", sys.version.split()[0])]
    license_path = root / "LICENSE"
    apache = license_path.is_file() and "Apache License" in license_path.read_text(encoding="utf-8")
    checks.append(Check("Repository license", "PASS" if apache else "FAIL", "Apache License required"))
    ui = ("dashboard/dashboard.py", "dashboard/dashboard_ui.html",
          "desktop_widget/web/index.html", "desktop_widget/web/mascot.js")
    missing_ui = [name for name in ui if not (root / name).is_file()]
    checks.append(Check("User interfaces", "FAIL" if missing_ui else "PASS", ", ".join(missing_ui) or "Dashboard and widget present"))
    config_path = root / "config/config.json"
    if not config_path.is_file():
        checks.append(Check("Configuration", "WARN", "Not configured; run the setup wizard or CLI"))
        config = {}
    else:
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if not isinstance(config, dict):
                raise ValueError("configuration must be an object")
            from core.mindscape_config import resolve
            config = resolve(config, root=root) or config
            checks.append(Check("Configuration", "PASS", config.get("composition", "helix")))
        except (OSError, ValueError, TypeError, KeyError) as error:
            checks.append(Check("Configuration", "FAIL", str(error)))
            return checks
    dependencies = ["numpy", "yaml", "flask", "dotenv", "requests"]
    if config.get("composition") == "mindscape":
        dependencies += ["torch", "transformers", "safetensors", "packaging"]
        module = config["mindscape"]
        source = Path(module["package_path"])
        required = ("context_loom/engine.py", "habitus_ai/continual_mind.py", "habitus_ai/rwkv7_language.py")
        absent = [name for name in required if not (source / name).is_file()]
        checks.append(Check("Native source", "FAIL" if absent else "PASS", ", ".join(absent) or str(source)))
        model = Path(module["rwkv_model"])
        try:
            index = json.loads((model / "model.safetensors.index.json").read_text(encoding="utf-8"))
            shards = set(index["weight_map"].values())
            if not shards or any(not (model / name).resolve().is_relative_to(model.resolve()) or
                                 not (model / name).is_file() for name in shards):
                raise ValueError("missing or invalid checkpoint shards")
            checks.append(Check("RWKV checkpoint", "PASS", f"Index and {len(shards)} shards present; weights not loaded"))
        except (OSError, ValueError, KeyError, TypeError) as error:
            checks.append(Check("RWKV checkpoint", "FAIL", str(error)))
        checks.append(Check("Workshop sandbox", "PASS" if shutil.which("bwrap") else "FAIL",
                            "Bubblewrap executable required; namespace permissions need an operational check"))
        checks.append(Check("Embedding service", "WARN", "Ollama/qwen3-embedding availability not probed by this offline preflight"))
    missing = [name for name in dependencies if importlib.util.find_spec(name) is None]
    checks.append(Check("Python dependencies", "FAIL" if missing else "PASS", ", ".join(missing) or "Selected preflight imports available"))
    return checks


def check_health(root=REPO_ROOT, *, json_output=False):
    checks = collect_checks(root)
    if json_output:
        print(json.dumps({"checks": [asdict(check) for check in checks], "exit_code": exit_code(checks)}, indent=2))
    else:
        for check in checks:
            print(f"{check.status:4}  {check.component}: {check.detail}")
        print("Preflight failed; resolve required failures." if exit_code(checks) else
              "Offline preflight complete; live services and runtime behavior remain unverified.")
    return exit_code(checks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return check_health(args.root, json_output=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
