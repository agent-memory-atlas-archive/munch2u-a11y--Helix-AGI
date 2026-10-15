"""TDD test suite for Bicameral RWKV Speaking Head and ChatSession provider."""
import unittest
from pathlib import Path

from core.bicameral_rwkv import BicameralRWKV
from llm.providers.base import ProviderConfig, create_session

RWKV_MODEL_PATH = Path("/home/nemo/habitus-ai-experiments/habitus-mind/models/rwkv7-g1j-1.5b-20260831-2c18b29")


class TestRWKVSpeakingHead(unittest.TestCase):
    def test_generate_language_produces_text(self):
        """BicameralRWKV must generate continuous text tokens from language stream."""
        system = BicameralRWKV(model_path=RWKV_MODEL_PATH, device="cpu")
        system.reset_states()
        system.sensory_observe("The environment is serene and quiet.")
        
        output = system.generate_language(
            prompt="Hello Joshua, I am feeling",
            max_new_tokens=15,
            temperature=0.0,
            coupling_gain=0.15,
        )
        self.assertIsInstance(output, str)
        self.assertTrue(len(output.strip()) > 0, "generate_language returned empty output")

    def test_provider_factory_creates_rwkv_session(self):
        """create_session must instantiate BicameralRWKVSession for provider_type='rwkv'."""
        config = ProviderConfig(
            provider_type="rwkv",
            model=str(RWKV_MODEL_PATH),
            context_window=8192,
            temperature=0.7,
            max_output_tokens=100,
        )
        session = create_session(config, system_instruction="You are Helix.")
        self.assertIsNotNone(session)
        self.assertTrue(hasattr(session, "send_message"))
        self.assertTrue(hasattr(session, "send_context"))

    def test_session_send_context_generates_speech(self):
        """BicameralRWKVSession must generate speech from send_context."""
        config = ProviderConfig(
            provider_type="bicameral_rwkv",
            model=str(RWKV_MODEL_PATH),
            context_window=8192,
            temperature=0.0,
            max_output_tokens=15,
        )
        session = create_session(config, system_instruction="You are Helix.")
        resp = session.send_context("Hi Helix, how are you?")
        self.assertIsInstance(resp, str)
        self.assertTrue(len(resp.strip()) > 0, "send_context returned empty response")


if __name__ == "__main__":
    unittest.main()
