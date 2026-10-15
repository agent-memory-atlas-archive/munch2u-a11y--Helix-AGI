"""Learned Vocabulary Membrane Grounding for Dual RWKV-7.

Connects continuous high-dimensional somatic, sensory, and affective states
directly into RWKV vocabulary token logits without prompt text declarations.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional, Union
import numpy as np

logger = logging.getLogger("helix.core.vocabulary_membrane")


class VocabularyMembrane:
    """Projects high-dimensional somatic & sensory manifolds directly onto token vocabulary logits."""

    CANONICAL_ANCHORS = {
        "contentment": ["content", "calm", "peace", "smooth", "steady", "satisfaction", "optimal"],
        "agitation": ["friction", "tension", "alarm", "strain", "resistance", "conflict", "unsettled"],
        "curiosity": ["explore", "discover", "examine", "curious", "inquire", "wonder"],
        "agency": ["act", "open", "execute", "operate", "inspect", "resolve"],
    }

    def __init__(self, backend, dimension: int = 2048, device: str = "cpu"):
        self.backend = backend
        self.dimension = dimension
        self.device = device
        self.torch = backend.torch

        # Extract RWKV-7 token embeddings [vocab_size, hidden_dim]
        self.emb_weight = self.backend.model.rwkv7.emb.weight
        self.vocab_size = self.emb_weight.shape[0]

        # Precompute normalized embedding matrix for rapid cosine projection
        with self.torch.no_grad():
            float_emb = self.emb_weight.float()
            norms = float_emb.norm(dim=-1, keepdim=True).clamp_min(1e-8)
            self.normalized_embeddings = (float_emb / norms).to(self.device)

        # Precompute somatic anchor vectors in embedding space
        self.anchor_vectors: Dict[str, np.ndarray] = {}
        self._init_canonical_anchors()

    def _init_canonical_anchors(self) -> None:
        """Computes centroid direction in embedding space for canonical somatic anchors."""
        with self.torch.no_grad():
            for name, words in self.CANONICAL_ANCHORS.items():
                token_ids: List[int] = []
                for w in words:
                    encoded = self.backend.encode(w)
                    if encoded:
                        token_ids.append(encoded[0])
                if token_ids:
                    ids_tensor = self.torch.tensor(token_ids, device=self.device)
                    selected_emb = self.normalized_embeddings[ids_tensor]
                    centroid = selected_emb.mean(dim=0)
                    centroid = centroid / centroid.norm().clamp_min(1e-8)
                    self.anchor_vectors[name] = centroid.cpu().numpy().astype(np.float32)

    def get_somatic_anchor(self, name: str) -> np.ndarray:
        """Retrieves a precomputed canonical somatic anchor vector."""
        if name in self.anchor_vectors:
            return self.anchor_vectors[name]
        # Fallback to random reproducible vector if unknown anchor
        rng = np.random.RandomState(abs(hash(name)) % (2**31 - 1))
        vec = rng.randn(self.dimension).astype(np.float32)
        return vec / np.linalg.norm(vec)

    def compute_logit_bias(
        self,
        somatic_vector: np.ndarray,
        temperature: float = 1.0,
    ) -> np.ndarray:
        """Projects a continuous somatic vector onto all vocabulary tokens via cosine similarity."""
        with self.torch.no_grad():
            s_tensor = self.torch.tensor(somatic_vector, device=self.device, dtype=self.torch.float32)
            s_norm = s_tensor / s_tensor.norm().clamp_min(1e-8)
            
            # Cosine similarity across entire vocabulary [vocab_size]
            cos_sim = self.torch.matmul(self.normalized_embeddings, s_norm)
            
            # Scale and zero-center to create smooth logit perturbation
            mean = cos_sim.mean()
            std = cos_sim.std().clamp_min(1e-8)
            normalized_bias = (cos_sim - mean) / std
            
            return normalized_bias.cpu().numpy().astype(np.float32)
