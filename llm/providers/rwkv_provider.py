"""Bicameral RWKV-7 Chat Session Provider."""
from __future__ import annotations

import json
import hashlib
import time
from llm.rwkv_tokens import RWKVTokenCounter
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
        max_output_tokens: int | None = None,
        backend=None,
        options: Optional[Dict[str, Any]] = None,
    ):
        self.model_path = Path(model_path) if model_path else None
        self.model = str(self.model_path)
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
        model_str = str(self.model_path) if self.model_path else "."
        self.context_counter = RWKVTokenCounter(self.system.backend.encode, model_str)
        self.last_context_receipt = {}
        self.last_context_output_kind = None
        self.last_contemplation = ""
        self._pending_context_response = None

    def _generate(self, message):
        messages = self.context_messages(message)
        receipt = self.context_counter.check_request(messages, int(self.options.get('input_context_tokens', 8192)))
        prompt = self.context_counter.render_messages(messages)
        receipt.update(model=self.model, device=str(self.system.device),
                       prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(), started_at=time.time())
        sensory = self.options.pop('current_sensory_items', [])
        for item in sensory:
            self.system.sensory_observe(item['text'])
        receipt['sensory_admissions'] = sensory
        self.last_contemplation = ''
        self.last_context_output_kind = None
        progress_path = self.options.get('generation_progress_path')
        if progress_path:
            def progress(value):
                from core.mindscape_config import write_json
                write_json(Path(progress_path), {**value, 'time': time.time(), 'status': 'incomplete',
                                                'prompt_sha256': receipt['prompt_sha256']})
            self.system.generation_progress = progress
        raw = self.system.generate_language(
            prompt, max_new_tokens=self.max_output_tokens, temperature=self.temperature,
            coupling_gain=float(self.options.get('coupling_gain', 0.15)),
            membrane_state=self.options.get('membrane_state'),
            membrane_gain=float(self.options.get('membrane_gain', 0.0)),
            repetition_penalty=float(self.options.get('repetition_penalty', 1.15)))
        generation = dict(getattr(self.system, 'last_generation_receipt', {}) or {})
        if 'prompt_tokens' not in generation:
            generation['prompt_tokens'] = receipt['prompt_tokens']
            generation['generated_tokens'] = len(raw) if raw else 0
            generation['done_reason'] = 'eos'
        elif generation['prompt_tokens'] != receipt['prompt_tokens']:
            raise RuntimeError('RWKV request accounting differs from evaluated input')
        from core.mindscape_intention import extract_contemplation_and_actualization
        contemplation, actualized = extract_contemplation_and_actualization(raw)
        self.last_contemplation = contemplation
        receipt.update(generation, raw_foreground=raw, contemplation=contemplation,
                       completed_at=time.time(), evaluated_prompt_tokens=generation['prompt_tokens'])
        self._last_token_count = receipt['prompt_tokens'] + receipt['generated_tokens']
        self.last_context_receipt = receipt
        if progress_path:
            from core.mindscape_config import write_json
            write_json(Path(progress_path), {**receipt, 'status': 'complete'})
        return raw, actualized

    def send_message(self, message):
        raw, actualized = self._generate(message)
        if not actualized:
            raise RuntimeError('RWKV produced only private contemplation; no public reply completed')
        self.history.extend([{'role': 'user', 'content': message}, {'role': 'assistant', 'content': actualized}])
        return actualized

    def send_context(self, message):
        raw, actualized = self._generate(message)
        if self.context_decoder:
            thought, kind = self.context_decoder(raw)
            if kind == 'contemplation':
                thought = '[thought] ' + (self.last_contemplation or '(quiet reflection)')
            self.last_context_output_kind = kind
        else:
            thought = actualized or ('[thought] ' + (self.last_contemplation or '(quiet reflection)'))
        self.last_context_receipt['output_kind'] = self.last_context_output_kind
        self._pending_context_response = thought
        return thought

    def finish_context(self, current_messages: List[str], response: str, *, delivered: bool) -> None:
        if response != self._pending_context_response:
            raise ValueError("No matching completed RWKV response to commit")
        self.history.extend({"role": "user", "content": msg} for msg in current_messages)
        if delivered:
            self.history.append({"role": "assistant", "content": response})
        self._pending_context_response = None

    def pulse_input_allowance(self) -> int:
        remaining = int(self.options.get("input_context_tokens", 8192)) - self.context_counter.count_messages(self.context_messages(""))
        if remaining <= 0:
            raise RuntimeError("Configured RWKV input allowance exhausted; no history was clipped")
        return remaining

    def covered_source_hashes(self) -> set:
        import hashlib
        return {hashlib.sha256(item["content"].encode()).hexdigest() for item in self.history}

    def get_history_size(self) -> int:
        return sum(len(item.get("content", "")) for item in self.history)

    def context_messages(self, message):
        return ([{'role': 'system', 'content': self.system_instruction}]
                + [dict(item) for item in self.history]
                + ([{'role': 'user', 'content': message}] if message else []))

    def _build_prompt(self, current_message):
        return self.context_counter.render_messages(self.context_messages(current_message))

    def get_last_token_count(self):
        return getattr(self, '_last_token_count', 0)

    def get_history(self):
        return [dict(item) for item in self.history]

    def close(self):
        self.system = None

    def cancel_pending(self):
        self.system.cancel_event.set()
