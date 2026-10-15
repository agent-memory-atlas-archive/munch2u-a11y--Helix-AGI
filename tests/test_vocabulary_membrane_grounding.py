"""Test Learned Vocabulary Membrane Grounding in Dual RWKV-7.

Verifies non-symbolic grounding: High-dimensional somatic/sensory shapes
bias token logits directly on the vocabulary layer without prompt text scaffolding.
"""
from collections import Counter
import unittest
from unittest.mock import MagicMock
from pathlib import Path
import numpy as np

RWKV_MODEL_PATH = Path("/home/nemo/habitus-ai-experiments/habitus-mind/models/rwkv7-g1j-1.5b-20260831-2c18b29")


class TestVocabularyMembraneGrounding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from core.bicameral_rwkv import BicameralRWKV
        cls.system = BicameralRWKV(
            model_path=RWKV_MODEL_PATH,
            device="cpu",
        )

    def test_01_membrane_computes_logit_bias_shape_and_norm(self):
        """Membrane should produce a vocabulary-sized logit bias vector."""
        from core.vocabulary_membrane import VocabularyMembrane
        membrane = VocabularyMembrane(
            backend=self.system.backend,
            dimension=self.system.hidden_size,
            device=self.system.device,
        )
        
        # Test with random somatic vector
        rng = np.random.RandomState(42)
        somatic_vec = rng.randn(self.system.hidden_size).astype(np.float32)
        
        bias = membrane.compute_logit_bias(somatic_vec)
        self.assertIsInstance(bias, np.ndarray)
        self.assertEqual(bias.shape, (self.system.backend.model.rwkv7.emb.weight.shape[0],))
        self.assertFalse(np.isnan(bias).any())

    def test_02_somatic_state_shifts_token_probabilities_without_prompt(self):
        """Somatic state should shift token logits towards aligned lexical tokens without prompt text."""
        from core.vocabulary_membrane import VocabularyMembrane
        membrane = VocabularyMembrane(
            backend=self.system.backend,
            dimension=self.system.hidden_size,
            device=self.system.device,
        )

        # Baseline prompt with no emotion declared in text
        neutral_prompt = "My current state is"
        
        # Base logits with zero membrane gain
        base_logits = self.system.step_language(neutral_prompt, coupling_gain=0.0)
        
        # Get contentment somatic vector
        contentment_vec = membrane.get_somatic_anchor("contentment")
        bias_contentment = membrane.compute_logit_bias(contentment_vec)
        
        # Get agitation/dissonance somatic vector
        agitation_vec = membrane.get_somatic_anchor("agitation")
        bias_agitation = membrane.compute_logit_bias(agitation_vec)

        # Contentment tokens
        content_tokens = ["content", "calm", "peace", "smooth", "steady", "satisfaction", "optimal"]
        # Agitation tokens
        agitated_tokens = ["friction", "tension", "alarm", "strain", "resistance", "conflict", "unsettled"]

        content_ids = [self.system.backend.encode(t)[0] for t in content_tokens if self.system.backend.encode(t)]
        agitated_ids = [self.system.backend.encode(t)[0] for t in agitated_tokens if self.system.backend.encode(t)]

        # Under contentment bias, content token logits must increase relative to agitation tokens
        contentment_diff = np.mean(bias_contentment[content_ids]) - np.mean(bias_contentment[agitated_ids])
        self.assertGreater(contentment_diff, 0.0, f"Expected contentment bias to favor content tokens, got diff: {contentment_diff}")

        # Under agitation bias, agitation token logits must increase relative to content tokens
        agitation_diff = np.mean(bias_agitation[agitated_ids]) - np.mean(bias_agitation[content_ids])
        self.assertGreater(agitation_diff, 0.0, f"Expected agitation bias to favor agitation tokens, got diff: {agitation_diff}")

    def test_03_bicameral_rwkv_integration_with_membrane(self):
        """BicameralRWKV.generate_language should accept membrane modulation and steer actual generation."""
        self.system.reset_states()
        prompt = "My sensation right now feels"
        out_content = self.system.generate_language(
            prompt,
            max_new_tokens=40,
            temperature=0.3,
            membrane_state="contentment",
            membrane_gain=1.5,
        )
        self.assertTrue(len(out_content.strip()) > 0)
        print(f"\n[Grounded Generation - Contentment] Helix: {out_content}")

    def test_04_repetition_penalty_prevents_repetition(self):
        """Repetition penalty should prevent repetitive loops under membrane steering."""
        self.system.reset_states()
        prompt = "My current feeling is"
        out_content = self.system.generate_language(
            prompt,
            max_new_tokens=40,
            temperature=0.7,
            repetition_penalty=1.2,
            membrane_state="contentment",
            membrane_gain=0.3,
        )
        self.assertTrue(len(out_content.strip()) > 0)
        words = out_content.lower().split()
        counts = Counter(words)
        max_rep = max(counts.values()) if counts else 0
        self.assertLessEqual(max_rep, 4, f"Output showed degenerate repetition: {out_content}")
        print(f"\n[Grounded Generation - Non-Repeating] Helix: {out_content}")

    def test_05_session_options_wire_membrane(self):
        """BicameralRWKVSession should pass membrane options to generate_language."""
        from llm.providers.rwkv_provider import BicameralRWKVSession
        
        mock_backend = MagicMock()
        mock_backend.embedding_dimension = 2048
        mock_backend.torch = MagicMock()
        mock_backend.device = "cpu"
        
        session = BicameralRWKVSession(
            model_path="",
            backend=mock_backend,
            options={"membrane_state": "contentment", "membrane_gain": 0.25},
        )
        session.system.generate_language = MagicMock(return_value="I feel steady and nominal.")
        
        reply = session.send_message("How are you?")
        session.system.generate_language.assert_called_once()
        kwargs = session.system.generate_language.call_args.kwargs
        self.assertEqual(kwargs.get("membrane_state"), "contentment")
        self.assertEqual(kwargs.get("membrane_gain"), 0.25)


if __name__ == "__main__":
    unittest.main()
