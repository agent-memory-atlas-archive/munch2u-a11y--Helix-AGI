"""Bicameral RWKV-7 Chat Session Provider."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from core.bicameral_rwkv import BicameralRWKV
from llm.providers.base import ChatSession

logger = logging.getLogger("helix.llm.providers.rwkv")


class BicameralRWKVSession(ChatSession):
    def __init__(
        self,
        model_path: str,
        system_instruction: str = "",
        temperature: float = 0.7,
        max_output_tokens: int = 512,
        backend=None,
        options: Optional[Dict[str, Any]] = None,
    ):
        self.model_path = Path(model_path) if model_path else None
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.options = options or {}
        self.history: List[Dict[str, str]] = []

        # Instantiate or bind BicameralRWKV
        self.system = BicameralRWKV(
            model_path=self.model_path,
            device="cpu",
            backend=backend,
        )
        self.context_format = None
        self.context_decoder = None
        self.context_counter = None
        self.last_context_receipt = {}
        self.last_context_output_kind = None
        self.last_contemplation = ""
        self._pending_context_response = None

    def send_message(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        prompt = self._build_prompt(message)
        raw_output = self.system.generate_language(
            prompt,
            max_new_tokens=self.max_output_tokens,
            temperature=self.temperature,
            coupling_gain=float(self.options.get("coupling_gain", 0.15)),
            membrane_state=self.options.get("membrane_state"),
            membrane_gain=float(self.options.get("membrane_gain", 0.0)),
            repetition_penalty=float(self.options.get("repetition_penalty", 1.15)),
        )
        from core.mindscape_intention import extract_contemplation_and_actualization
        contemplation, actualized = extract_contemplation_and_actualization(raw_output)
        if contemplation:
            self.last_contemplation = contemplation

        reply = actualized if actualized else raw_output
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def send_context(self, message: str) -> str:
        prompt = self._build_prompt(message)
        raw_output = self.system.generate_language(
            prompt,
            max_new_tokens=self.max_output_tokens,
            temperature=self.temperature,
            coupling_gain=float(self.options.get("coupling_gain", 0.15)),
            membrane_state=self.options.get("membrane_state"),
            membrane_gain=float(self.options.get("membrane_gain", 0.0)),
            repetition_penalty=float(self.options.get("repetition_penalty", 1.15)),
        )
        from core.mindscape_intention import extract_contemplation_and_actualization
        contemplation, actualized = extract_contemplation_and_actualization(raw_output)
        if contemplation:
            self.last_contemplation = contemplation

        thought = raw_output
        self.last_context_output_kind = None
        if self.context_decoder is not None:
            try:
                thought, self.last_context_output_kind = self.context_decoder(raw_output)
            except Exception as exc:
                logger.debug("Foreground decode fallback: %s", exc)
        else:
            thought = actualized if actualized else raw_output

        self._pending_context_response = thought
        return thought

    def finish_context(self, current_messages: List[str], response: str, *, delivered: bool) -> None:
        self.history.extend({"role": "user", "content": msg} for msg in current_messages)
        if delivered:
            self.history.append({"role": "assistant", "content": response})
        self._pending_context_response = None

    def pulse_input_allowance(self) -> int:
        return 8192

    def covered_source_hashes(self) -> set:
        import hashlib
        return {hashlib.sha256(item["content"].encode()).hexdigest() for item in self.history}

    def get_history_size(self) -> int:
        return sum(len(item.get("content", "")) for item in self.history)

    def _build_prompt(self, current_message: str) -> str:
        parts = []
        if self.system_instruction:
            parts.append(f"System: {self.system_instruction}")
        for item in self.history:
            role = "User" if item["role"] == "user" else "Assistant"
            parts.append(f"{role}: {item['content']}")
        parts.append(f"User: {current_message}\nAssistant:")
        return "\n\n".join(parts)
