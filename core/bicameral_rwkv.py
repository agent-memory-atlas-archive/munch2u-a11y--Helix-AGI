"""Bicameral Unified-Stream Multi-RWKV System.

Couples an embodied sensory-motor stream and a cognitive-language stream
sharing a single frozen RWKV-7 neural foundation, utilizing an internal
manifold Translator Bridge (Corpus Callosum) for continuous non-linguistic
sensory guidance and cognitive motor feedback.
"""
from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

# Ensure MightyMem package is available for habitus_ai imports
MIGHTYMEM_PATH = Path("/home/nemo/MightyMem").resolve()
if str(MIGHTYMEM_PATH) not in sys.path:
    sys.path.insert(0, str(MIGHTYMEM_PATH))

from habitus_ai.rwkv7_language import Rwkv7Backend


class BicameralTranslatorBridge:
    """Manifold Translator Bridge connecting Sensory and Language representation spaces.

    Acts as an internal neural Corpus Callosum: translates raw sensory-motor topologies
    into semantic continuous guidance fields, and translates cognitive attention back
    into sensory-motor readiness.
    """

    def __init__(self, dimension: int, torch_module, device):
        self.dimension = dimension
        self.torch = torch_module
        self.device = device

        # Structured linear orthogonal projection seeds for cross-manifold alignment
        # (Preserves continuous topology while mapping across functional coordinate frames)
        rng = np.random.RandomState(42)
        q_s2l, _ = np.linalg.qr(rng.randn(dimension, dimension))
        q_l2s, _ = np.linalg.qr(rng.randn(dimension, dimension))

        self.w_sensory_to_lang = self.torch.tensor(
            q_s2l, device=self.device, dtype=self.torch.float32
        )
        self.w_lang_to_sensory = self.torch.tensor(
            q_l2s, device=self.device, dtype=self.torch.float32
        )

    def translate_sensory_to_language(self, sensory_vector: np.ndarray) -> np.ndarray:
        """Translates a raw sensory state manifold vector into a language guidance vector."""
        with self.torch.no_grad():
            s = self.torch.tensor(sensory_vector, device=self.device, dtype=self.torch.float32)
            s_norm = s / s.norm().clamp_min(1.0)
            # Projected translation
            translated = self.torch.matmul(s_norm, self.w_sensory_to_lang)
            translated = translated / translated.norm().clamp_min(1.0)
            return translated.cpu().numpy()

    def translate_language_to_sensory(self, language_vector: np.ndarray) -> np.ndarray:
        """Translates cognitive attention into a sensory-motor feedback vector."""
        with self.torch.no_grad():
            l = self.torch.tensor(language_vector, device=self.device, dtype=self.torch.float32)
            l_norm = l / l.norm().clamp_min(1.0)
            translated = self.torch.matmul(l_norm, self.w_lang_to_sensory)
            translated = translated / translated.norm().clamp_min(1.0)
            return translated.cpu().numpy()


class BicameralRWKV:
    """Manages two recurrent state tensors (Sensory and Language) over a shared RWKV-7 model."""

    def __init__(self, model_path: Path | None = None, device: str = "cpu", backend=None):
        self.model_path = Path(model_path).resolve() if model_path else None
        self.device_name = device
        # Initialize frozen pretrained RWKV-7 backend or reuse existing
        if backend is not None:
            self.backend = backend
        else:
            if not self.model_path:
                raise ValueError("model_path is required when backend is not provided")
            self.backend = Rwkv7Backend(self.model_path, device=device)
        self.torch = self.backend.torch
        self.device = self.backend.device
        self.model = self.backend.model
        self.tokenizer = self.backend.tokenizer
        self.hidden_size = self.backend.embedding_dimension

        # Instantiate the Translator Bridge
        self.bridge = BicameralTranslatorBridge(self.hidden_size, self.torch, self.device)

        # Instantiate Vocabulary Membrane
        from core.vocabulary_membrane import VocabularyMembrane
        self.membrane = VocabularyMembrane(self.backend, self.hidden_size, self.device)

        # Allocate separate recurrent states
        self.sensory_state = None
        self.language_state = None
        self.reset_states()

    def reset_states(self):
        """Reallocates pristine zero-state recurrent tensors for both streams."""
        with self.torch.no_grad():
            self.sensory_state = self.model.rwkv7.allocate_state(1, self.device, self.torch.bfloat16)
            self.language_state = self.model.rwkv7.allocate_state(1, self.device, self.torch.bfloat16)

    def sensory_observe(self, text: str) -> None:
        """Processes continuous sensory or environmental observations into the sensory state."""
        ids = self.backend.encode(text)
        if not ids:
            return
        with self.torch.inference_mode():
            result = self.model(
                input_ids=self.torch.tensor([ids], device=self.device),
                state=self.sensory_state,
                use_cache=True,
                logits_to_keep=1
            )
            self.sensory_state = result.state

    def get_sensory_state_vector(self) -> np.ndarray:
        """Extracts the top-layer recurrent attention vector representing the sensory manifold."""
        with self.torch.no_grad():
            attention, _, _ = self.sensory_state.read(len(self.sensory_state.layers) - 1)
            return attention[0].detach().float().cpu().numpy()

    def get_language_state_vector(self) -> np.ndarray:
        """Extracts the top-layer recurrent attention vector representing cognitive state."""
        with self.torch.no_grad():
            attention, _, _ = self.language_state.read(len(self.language_state.layers) - 1)
            return attention[0].detach().float().cpu().numpy()

    def step_language(self, prompt: str, coupling_gain: float = 0.0) -> np.ndarray:
        """Steps the language model on prompt, optionally modulated by translated sensory state."""
        ids = self.backend.encode(prompt)
        if not ids:
            raise ValueError("Prompt cannot be empty")

        with self.torch.inference_mode():
            if coupling_gain <= 0.0:
                result = self.model(
                    input_ids=self.torch.tensor([ids], device=self.device),
                    state=self.language_state,
                    use_cache=True,
                    logits_to_keep=1
                )
            else:
                # Embed the input token sequence
                token_tensor = self.torch.tensor([ids], device=self.device)
                embeds = self.model.rwkv7.emb(token_tensor).float()

                # Extract sensory continuous vector and translate via Translator Bridge
                raw_sensory = self.get_sensory_state_vector()
                translated_guidance = self.bridge.translate_sensory_to_language(raw_sensory)
                guidance_tensor = self.torch.tensor(
                    translated_guidance, device=self.device, dtype=self.torch.float32
                )

                # Inject translated sensory residual perturbation without any text
                gain = float(coupling_gain)
                norm_embeds = embeds.norm(dim=-1, keepdim=True)
                embeds = (embeds + gain * norm_embeds * guidance_tensor).to(self.model.rwkv7.emb.weight.dtype)

                result = self.model(
                    inputs_embeds=embeds,
                    state=self.language_state,
                    use_cache=True,
                    logits_to_keep=1
                )

            self.language_state = result.state
            logits = result.logits[0, -1].detach().float().cpu().numpy()
            return logits

    def generate_language(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.85,
        coupling_gain: float = 0.15,
        membrane_state: str | np.ndarray | None = None,
        membrane_gain: float = 0.0,
        repetition_penalty: float = 1.0,
        stop_sequences: tuple[str, ...] = ("<|endoftext|>", "\n\nUser:", "\n\nAssistant:", "\n\n[Pulse"),
        reset_state: bool = True,
    ) -> str:
        """Autoregressively generate language tokens, steered by sensory continuous state and vocabulary membrane."""
        if reset_state:
            self.language_state = None
        logits = self.step_language(prompt, coupling_gain=coupling_gain)
        generated_ids: list[int] = []
        eos_id = getattr(self.backend, "eos_token_id", 0)

        # Precompute vocabulary membrane logit bias if enabled
        membrane_bias = None
        if membrane_gain > 0.0 and membrane_state is not None:
            if isinstance(membrane_state, str):
                s_vec = self.membrane.get_somatic_anchor(membrane_state)
            else:
                s_vec = membrane_state
            membrane_bias = self.membrane.compute_logit_bias(s_vec)

        stopped = False
        text_so_far = ""

        for _ in range(max_new_tokens):
            effective_logits = logits.copy()
            if membrane_bias is not None:
                effective_logits = effective_logits + float(membrane_gain) * membrane_bias

            if repetition_penalty != 1.0 and generated_ids:
                recent_ids = set(generated_ids[-32:])
                for past_id in recent_ids:
                    if effective_logits[past_id] > 0:
                        effective_logits[past_id] /= repetition_penalty
                    else:
                        effective_logits[past_id] *= repetition_penalty

            if temperature <= 0.0:
                next_id = int(np.argmax(effective_logits))
            else:
                scaled = effective_logits / max(temperature, 1e-5)
                scaled -= np.max(scaled)
                probs = np.exp(scaled) / np.sum(np.exp(scaled))
                if top_p < 1.0:
                    sorted_indices = np.argsort(probs)[::-1]
                    sorted_probs = probs[sorted_indices]
                    cumulative_probs = np.cumsum(sorted_probs)
                    cutoff_index = int(np.searchsorted(cumulative_probs, top_p))
                    candidates = sorted_indices[:max(1, cutoff_index + 1)]
                    c_probs = probs[candidates]
                    c_probs /= np.sum(c_probs)
                    next_id = int(np.random.choice(candidates, p=c_probs))
                else:
                    next_id = int(np.random.choice(len(probs), p=probs))

            if next_id == eos_id:
                break
            generated_ids.append(next_id)

            # Check stop sequences
            text_so_far = self.backend.decode(generated_ids)
            stopped = False
            for stop in stop_sequences:
                if stop in text_so_far:
                    text_so_far = text_so_far.split(stop, 1)[0]
                    stopped = True
                    break
            if stopped:
                break

            # Forward step single next_id
            with self.torch.inference_mode():
                result = self.model(
                    input_ids=self.torch.tensor([[next_id]], device=self.device),
                    state=self.language_state,
                    use_cache=True,
                    logits_to_keep=1,
                )
                self.language_state = result.state
                logits = result.logits[0, -1].detach().float().cpu().numpy()

        # Closed-loop cognitive feedback into sensory state
        self.feedback_language_to_sensory(feedback_gain=0.15)
        return text_so_far.strip() if stopped else self.backend.decode(generated_ids).strip()

    def feedback_language_to_sensory(self, feedback_gain: float = 0.15) -> None:
        """Modulates sensory state with continuous cognitive feedback vector via Translator Bridge."""
        if feedback_gain <= 0.0:
            return
        with self.torch.no_grad():
            raw_lang = self.get_language_state_vector()
            translated_feedback = self.bridge.translate_language_to_sensory(raw_lang)
            feedback_tensor = self.torch.tensor(
                translated_feedback, device=self.device, dtype=self.torch.float32
            )

            # Modulate sensory state top-layer attention tensor in-place
            layer_idx = len(self.sensory_state.layers) - 1
            attn, ffn, wkv = self.sensory_state.read(layer_idx)
            
            # Blend feedback directly into attention shift slot
            modulated_attn = (attn.float() + feedback_gain * attn.float().norm().clamp_min(1.0) * feedback_tensor).to(attn.dtype)
            self.sensory_state.write(layer_idx, modulated_attn, ffn, wkv)
