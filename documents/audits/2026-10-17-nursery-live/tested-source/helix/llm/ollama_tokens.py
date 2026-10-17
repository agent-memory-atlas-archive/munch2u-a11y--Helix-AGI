"""Count the installed Granite model's actual vocabulary and chat template.

Only vocabulary is loaded from the GGUF. No alternate inference model is run.
Unsupported templates fail explicitly instead of substituting a regex estimate.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


GRANITE_TEMPLATE_SHA256 = "89a0ab46e638b17149f5a596060e815cb019117e9c7f745aa8861a02d63d66ef"


class ProviderContextExceeded(ValueError):
    pass


class OllamaTokenCounter:
    def __init__(self, model: str, *, models_root=None):
        if "/" in model or ".." in model:
            raise ValueError("Local tokenizer currently supports installed library model names")
        name, separator, tag = model.partition(":")
        tag = tag if separator else "latest"
        roots = ([Path(models_root)] if models_root else
                 [Path(os.environ["OLLAMA_MODELS"])] if os.environ.get("OLLAMA_MODELS") else
                 [Path.home() / ".ollama/models", Path("/usr/share/ollama/.ollama/models")])
        relative = Path("manifests/registry.ollama.ai/library") / name / tag
        root = next((root for root in roots if (root / relative).is_file()), None)
        if root is None:
            raise FileNotFoundError(f"Installed Ollama model manifest unavailable for exact token counting: {model}")
        raw_manifest = (root / relative).read_bytes()
        manifest = json.loads(raw_manifest)
        layers = {entry["mediaType"]: entry for entry in manifest["layers"]}
        model_layer = layers["application/vnd.ollama.image.model"]
        template_layer = layers["application/vnd.ollama.image.template"]
        template_path = root / "blobs" / template_layer["digest"].replace(":", "-")
        template_hash = hashlib.sha256(template_path.read_bytes()).hexdigest()
        if template_hash != GRANITE_TEMPLATE_SHA256:
            raise ValueError(f"Unsupported chat template for exact token counting: {model} ({template_hash})")
        from llama_cpp import Llama
        self._vocabulary = Llama(
            model_path=str(root / "blobs" / model_layer["digest"].replace(":", "-")),
            vocab_only=True, verbose=False,
        )
        self.model = model
        self.model_digest = hashlib.sha256(raw_manifest).hexdigest()
        self.identity = f"ollama-gguf:{model_layer['digest']}:template:{template_hash}"
        self.provenance = {"model": model, "manifest_sha256": self.model_digest,
                           "model_blob": model_layer["digest"], "template_sha256": template_hash,
                           "models_root": str(root), "vocab_only": True}

    def count(self, text: str) -> int:
        return len(self._vocabulary.tokenize(text.encode("utf-8"), add_bos=False, special=True))

    @staticmethod
    def render_messages(messages):
        # Exact expansion of the pinned installed template for schema-free
        # system/user/assistant messages. Tool/image/document modes need their
        # own checked renderer; never silently estimate those requests.
        if not messages or messages[0].get("role") != "system":
            raise ValueError("Expected initial system instruction")
        parts = []
        for index, message in enumerate(messages):
            role, content = message.get("role"), message.get("content")
            if role not in {"system", "user", "assistant"} or not isinstance(content, str):
                raise ValueError("Unsupported message shape for the installed chat template")
            if set(message) - {"role", "content"}:
                raise ValueError("Token accounting requires an explicit renderer for additional message fields")
            if index == 0 and not content:
                continue
            parts.append(f"<|start_of_role|>{role}<|end_of_role|>{content}<|end_of_text|>\n")
        if messages[-1]["role"] != "assistant":
            parts.append("<|start_of_role|>assistant<|end_of_role|>")
        return "".join(parts)

    def count_messages(self, messages):
        return self.count(self.render_messages(messages))

    def check_request(self, messages, context_tokens):
        count = self.count_messages(messages)
        # One generation token must physically fit. This is not an output cap;
        # incomplete generation must be reported at the actual provider boundary.
        if count >= context_tokens:
            raise ProviderContextExceeded(
                f"Complete provider request needs {count} input tokens against a "
                f"{context_tokens}-token context; no complete response is available")
        return {"prompt_tokens": count, "context_tokens": context_tokens,
                "available_generation_tokens": context_tokens - count,
                "token_counter": self.identity, "input_truncated": False}
