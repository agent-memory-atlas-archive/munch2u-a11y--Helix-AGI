"""Shared default discovery for explicitly configured native sources and weights."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
RWKV_CHECKPOINT = "rwkv7-g1j-1.5b-20260831-2c18b29"


def default_rwkv_model(root=ROOT):
    root = Path(root).resolve()
    candidates = [os.environ.get("RWKV_MODEL_PATH"),
                  str(Path.home() / "habitus-ai-experiments/habitus-mind/models" / RWKV_CHECKPOINT),
                  str(root.parent / "habitus-ai-experiments/habitus-mind/models" / RWKV_CHECKPOINT),
                  str(Path.home() / "models" / RWKV_CHECKPOINT),
                  str(root / "models" / RWKV_CHECKPOINT)]
    return next((candidate for candidate in candidates if candidate and Path(candidate).exists()), candidates[1])


def default_native_source(root=ROOT):
    root = Path(root).resolve()
    candidates = [os.environ.get("MIGHTYMEM_PATH"), str(root.parent / "MightyMem"), str(Path.home() / "MightyMem")]
    return next((candidate for candidate in candidates if candidate and Path(candidate).exists()), candidates[1])
