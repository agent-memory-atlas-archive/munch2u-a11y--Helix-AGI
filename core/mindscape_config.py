"""Shared, explicit composition contract for CLI setup, wizard and main."""
from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def defaults(root=ROOT):
    root = Path(root).resolve()
    default_rwkv_candidates = [
        os.environ.get("RWKV_MODEL_PATH"),
        str(Path.home() / "habitus-ai-experiments/habitus-mind/models/rwkv7-g1j-1.5b-20260831-2c18b29"),
        str(root.parent / "habitus-ai-experiments/habitus-mind/models/rwkv7-g1j-1.5b-20260831-2c18b29"),
        str(Path.home() / "models/rwkv7-g1j-1.5b-20260831-2c18b29"),
        str(root / "models/rwkv7-g1j-1.5b-20260831-2c18b29"),
    ]
    rwkv_path = next((c for c in default_rwkv_candidates if c and Path(c).exists()), default_rwkv_candidates[1])
    default_mightymem_candidates = [
        os.environ.get("MIGHTYMEM_PATH"),
        str(root.parent / "MightyMem"),
        str(Path.home() / "MightyMem"),
        str(Path("/home/nemo/MightyMem")),
    ]
    mightymem_path = next((c for c in default_mightymem_candidates if c and Path(c).exists()), str(root.parent / "MightyMem"))
    return {
        "composition": "mindscape",
        "pulse_mode": "standard",
        "local_provider": "rwkv",
        "local_model": str(rwkv_path),
        "llm_provider": "rwkv",
        "llm_model": str(rwkv_path),
        "local_context_window": 8192,
        "mindscape": {
            "package_path": mightymem_path,
            "rwkv_model": str(rwkv_path),
            "workspace": str(root),
            "home": str(root / "data/agent_home"),
            "modules_require_room": False,
            "device": "cpu",
            "gestation": "if_missing",
            "context_focus_profiles": {},
            "action_intent_source": "native_motor",
            "sensory_interval_seconds": 1.0,
        },
    }


def resolve(config, root=ROOT):
    composition = config.get("composition", "helix")
    if composition not in {"helix", "mindscape"}:
        raise ValueError(f"Unknown composition: {composition!r}; choose mindscape or helix explicitly")
    if composition == "helix":
        return None
    result = defaults(root)
    result.update(config)
    result["mindscape"] = {**defaults(root)["mindscape"], **config.get("mindscape", {})}
    if result.get("pulse_mode") != "standard":
        raise ValueError("Mindscape requires the standard Helix PulseLoop; dual mode is a different composition")
    if result.get("local_provider") not in {"ollama", "rwkv", "bicameral_rwkv"}:
        raise ValueError("Mindscape requires local Ollama or RWKV foreground")
    if result.get("llm_provider", "ollama") not in {"ollama", "rwkv", "bicameral_rwkv"}:
        raise ValueError("Mindscape uses Ollama or RWKV; select composition=helix for a different foreground provider")
    if result["mindscape"]["device"] != "cpu":
        raise ValueError("The native ContinualRwkv joint bridge is CPU-only; select device=cpu")
    if result["mindscape"]["gestation"] not in {"if_missing", "resume_only"}:
        raise ValueError("gestation must be if_missing or resume_only")
    if result["mindscape"]["action_intent_source"] not in {"native_motor", "granite_private", "rwkv_bicameral", "bicameral_rwkv"}:
        raise ValueError("action_intent_source must be native_motor")
    # Migrate old launch files to the body route; speech no longer dispatches.
    result["mindscape"]["action_intent_source"] = "native_motor"
    # The legacy speech-to-task hook belongs to a different action composition.
    result["task_cognition_mode"] = "off"
    if not isinstance(result["mindscape"]["modules_require_room"], bool):
        raise ValueError("modules_require_room must be a boolean")
    import math
    cadence = float(result["mindscape"]["sensory_interval_seconds"])
    if not math.isfinite(cadence) or cadence <= 0:
        raise ValueError("sensory_interval_seconds must be finite and positive (filesystem observation cadence)")
    if int(result["local_context_window"]) <= 0:
        raise ValueError("local_context_window must be positive")
    from core.context_focus import resolve_profiles
    resolve_profiles(result["mindscape"]["context_focus_profiles"])
    for key in ("package_path", "rwkv_model", "workspace", "home"):
        path = Path(result["mindscape"][key]).expanduser()
        if not path.is_absolute():
            path = Path(root) / path
        result["mindscape"][key] = str(path.resolve())
    return result


def activate(config):
    """Validate paths and select the declared source before importing neural code."""
    settings = resolve(config)
    if settings is None:
        return None
    module = settings["mindscape"]
    package = Path(module["package_path"])
    for relative in ("context_loom/engine.py", "habitus_ai/continual_mind.py"):
        if not (package / relative).is_file():
            raise RuntimeError(f"Full mindscape cannot start: missing {package / relative}")
    if not Path(module["rwkv_model"], "model.safetensors.index.json").is_file():
        raise RuntimeError(f"Full mindscape cannot start: RWKV weights missing at {module['rwkv_model']}")
    if not Path(module["workspace"]).is_dir():
        raise RuntimeError(f"Mindscape workspace does not exist: {module['workspace']}")
    from packaging.version import Version
    if Version(importlib.metadata.version("transformers")) < Version("5.15"):
        raise RuntimeError("Pinned RWKV requires transformers>=5.15; install requirements-mindscape.txt in the Helix venv")
    for name in ("context_loom", "habitus_ai"):
        loaded = sys.modules.get(name)
        if loaded and Path(loaded.__file__).resolve().parent != package / name:
            raise RuntimeError(f"{name} was already imported from a different package; restart with the declared composition")
    sys.path[:] = [entry for entry in sys.path if entry != str(package)]
    sys.path.insert(0, str(package))
    importlib.invalidate_caches()
    # Native ContinualMind selects auto internally. Mask compute devices before
    # torch is imported; the audited bridge constructs its tensors on CPU.
    if "torch" in sys.modules and sys.modules["torch"].cuda.is_initialized():
        raise RuntimeError("Restart before loading Mindscape: GPU torch was already initialized")
    for key in ("CUDA_VISIBLE_DEVICES", "HIP_VISIBLE_DEVICES", "ROCR_VISIBLE_DEVICES"):
        os.environ[key] = ""
    os.environ["HELIX_SEMANTIC_STRICT"] = "1"
    if os.environ.get("HELIX_UNIFIED_RAG", "1").lower() in {"0", "false", "no", "off"}:
        raise RuntimeError("Full mindscape requires HELIX_UNIFIED_RAG; mRAG cannot be disabled")
    if os.environ.get("HELIX_OFFICE_FIRST", "0").lower() in {"1", "true", "yes", "on"}:
        raise RuntimeError("Full mindscape uses the standard preconscious route; disable HELIX_OFFICE_FIRST")
    return settings


def local_model_receipt(config):
    """Check the selected local service before creating state or loading weights."""
    import urllib.request
    base = config.get("ollama_url", "http://localhost:11434").rstrip("/")
    rwkv = config['local_provider'] in {'rwkv', 'bicameral_rwkv'}
    names = (os.environ.get("HELIX_SEMANTIC_MODEL", "qwen3-embedding:0.6b"),)
    if not rwkv:
        names = (config['local_model'],) + names
    elif not Path(config['local_model'], 'model.safetensors.index.json').is_file():
        raise RuntimeError('Configured foreground RWKV checkpoint is missing')
    with urllib.request.urlopen(base + "/api/tags") as response:
        available = {row["name"]: row for row in json.load(response)["models"]}
    missing = [name for name in names if name not in available]
    if missing:
        raise RuntimeError(f"Full mindscape cannot start: local models missing: {', '.join(missing)}")
    return {"url": base, "models": [available[name] for name in names],
            'foreground': {'provider': config['local_provider'], 'model': config['local_model']}}


def source_receipt(root):
    root = Path(root).resolve()
    def git(*args):
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    paths = [p for directory in ("core", "memory", "llm", "tools", "brain", "comms", "context_loom", "habitus_ai")
             for p in (root / directory).rglob("*.py")]
    paths += [p for name in ("main.py", "setup.py", "pyproject.toml") if (p := root / name).is_file()]
    return {"root": str(root), "revision": git("rev-parse", "HEAD"),
            "working_tree": git("status", "--short"),
            "files": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}}


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n")
    temporary.replace(path)
