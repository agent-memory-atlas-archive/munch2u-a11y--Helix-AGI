"""Test separation of unconstrained internal <think> stream from foreground actualization."""
import unittest
from unittest.mock import MagicMock
from core.mindscape_intention import decode_foreground, parse_intention
from llm.providers.rwkv_provider import BicameralRWKVSession


class TestThoughtActualizationSeparation(unittest.TestCase):
    def test_decode_foreground_separates_think_and_speech(self):
        raw = (
            "<think>\n"
            "I am analyzing the sensory telemetry.\n"
            "Everything is operating within nominal thresholds.\n"
            "</think>\n"
            "Telemetry verified. All submersibles are synchronized."
        )
        msg, kind = decode_foreground(raw)
        self.assertEqual(kind, "message")
        self.assertEqual(msg, "Telemetry verified. All submersibles are synchronized.")
        self.assertNotIn("<think>", msg)
        self.assertNotIn("</think>", msg)

    def test_decode_foreground_separates_think_and_action(self):
        raw = (
            "<think>\n"
            "User requested reading a file. I should generate an open action.\n"
            "</think>\n"
            '{"action": "open", "arguments": {"path": "/tmp/test.json"}}'
        )
        wire, kind = decode_foreground(raw)
        self.assertEqual(kind, "intention")
        parsed = parse_intention(wire)
        self.assertEqual(parsed["action"], "open")
        self.assertEqual(parsed["arguments"]["path"], "/tmp/test.json")

    def test_decode_foreground_autonomous_contemplation_only(self):
        raw = (
            "<think>\n"
            "Internal pulse: reviewing memory records and sensor state. No outward action required.\n"
            "</think>"
        )
        msg, kind = decode_foreground(raw)
        self.assertEqual(kind, "contemplation")
        self.assertEqual(msg, "")

    def test_decode_foreground_empty_or_role_echo_degrades_to_contemplation(self):
        # When RWKV outputs pure role headers or empty strings, it must degrade
        # to quiet contemplation instead of raising ValueError and crashing pulse loop.
        for raw in ["Assistant:", "Helix:", "AI:", "", "   \n\t  ", "<think></think>", "Assistant: \n\n"]:
            msg, kind = decode_foreground(raw)
            self.assertEqual(kind, "contemplation", f"Failed for raw={repr(raw)}")
            self.assertEqual(msg, "", f"Failed for raw={repr(raw)}")

    def test_session_send_context_on_role_echo_produces_quiet_thought(self):
        mock_backend = MagicMock()
        mock_backend.embedding_dimension = 2048
        mock_backend.torch = MagicMock()
        mock_backend.device = "cpu"
        mock_backend.encode.return_value = [1, 2, 3]
        
        session = BicameralRWKVSession(
            model_path="/tmp",
            backend=mock_backend,
        )
        session.system.last_generation_receipt = {
            'prompt_tokens': 3,
            'generated_tokens': 1,
            'done_reason': 'conversation_boundary',
        }
        session.context_decoder = decode_foreground
        # Simulate model outputting only role header Assistant: (the exact crash in audit)
        session.system.generate_language = MagicMock(return_value="Assistant:")
        
        thought = session.send_context("hello")
        self.assertTrue(thought.startswith("[thought]"), f"Expected [thought], got {repr(thought)}")
        self.assertEqual(session.last_context_output_kind, "contemplation")

    def test_session_captures_last_contemplation_and_clean_speech(self):
        # Mock backend / system to avoid loading full model weights for unit verification
        mock_backend = MagicMock()
        mock_backend.embedding_dimension = 2048
        mock_backend.torch = MagicMock()
        mock_backend.device = "cpu"
        mock_backend.encode.return_value = [1, 2, 3]
        
        session = BicameralRWKVSession(
            model_path="/tmp",
            backend=mock_backend,
        )
        session.system.last_generation_receipt = {
            'prompt_tokens': 3,
            'generated_tokens': 10,
            'done_reason': 'eos',
        }
        # Mock generate_language to simulate RWKV outputting <think> followed by speech
        session.system.generate_language = MagicMock(return_value=(
            "<think>\n"
            "Deliberating on the user's question about acoustic latency...\n"
            "</think>\n"
            "Assistant: Acoustic latency typically increases with depth and salinity gradients."
        ))

        reply = session.send_message("What about acoustic latency?")
        
        # 1. Returned reply should be clean foreground speech without <think> or 'Assistant:' prefix
        self.assertNotIn("<think>", reply)
        self.assertNotIn("</think>", reply)
        self.assertFalse(reply.startswith("Assistant:"))
        self.assertIn("Acoustic latency typically increases", reply)

        # 2. session.last_contemplation should hold the raw deliberative thought
        self.assertTrue(hasattr(session, "last_contemplation"))
        self.assertIn("Deliberating on the user's question", session.last_contemplation)

        # 3. Conversation history should store clean speech, not internal <think>
        self.assertEqual(session.history[-1]["role"], "assistant")
        self.assertNotIn("<think>", session.history[-1]["content"])
        self.assertIn("Acoustic latency typically increases", session.history[-1]["content"])


if __name__ == "__main__":
    unittest.main()
