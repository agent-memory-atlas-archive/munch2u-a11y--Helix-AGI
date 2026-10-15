"""Comprehensive evaluation suite for Dual RWKV: Conversational Coherence, Recall, and Digital Environment Functionality."""
import os
import re
import unittest
from pathlib import Path

from core.bicameral_rwkv import BicameralRWKV
from llm.providers.rwkv_provider import BicameralRWKVSession
from core.mindscape_intention import decode_foreground, foreground_schema
from core.pulse_context import build_pulse_context, ContextContribution

RWKV_MODEL_PATH = Path("/home/nemo/habitus-ai-experiments/habitus-mind/models/rwkv7-g1j-1.5b-20260831-2c18b29")


class TestDualRWKVEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = BicameralRWKVSession(
            model_path=str(RWKV_MODEL_PATH),
            system_instruction=(
                "You are Helix, an autonomous cognitive entity. "
                "You are in an ongoing conversational exchange. "
                "Never repeat greetings, salutations, or pleasantries (such as 'Hello Joshua!') across turns. "
                "Address questions directly and concisely."
            ),
            temperature=0.2,
            max_output_tokens=150,
        )

    def setUp(self):
        self.session.history.clear()
        self.session.system.reset_states()

    def test_conversational_continuity_and_anti_greeting(self):
        """Conversational flow must remain coherent across multiple turns without repeating greetings."""
        # Turn 1
        t1_msg = "Hi Helix. How are you feeling today?"
        t1_reply = self.session.send_message(t1_msg)
        self.assertTrue(len(t1_reply.strip()) > 0)

        # Turn 2: Follow up question in ongoing dialogue
        t2_msg = "What was the concept regarding swarm robotics consensus you were thinking about?"
        t2_reply = self.session.send_message(t2_msg)
        self.assertTrue(len(t2_reply.strip()) > 0)
        
        # Verify Turn 2 does NOT start with repetitive greetings
        salutation_pattern = re.compile(r"^\s*(hello|hi|greetings|hey)\s+(joshua|there|buddy)?[!.,]", re.IGNORECASE)
        self.assertIsNone(
            salutation_pattern.match(t2_reply.strip()),
            f"Turn 2 repeated greeting: {t2_reply[:60]}"
        )

        # Turn 3: Another follow-up
        t3_msg = "Could that consensus recovery also work in autonomous submersibles?"
        t3_reply = self.session.send_message(t3_msg)
        self.assertTrue(len(t3_reply.strip()) > 0)
        self.assertIsNone(
            salutation_pattern.match(t3_reply.strip()),
            f"Turn 3 repeated greeting: {t3_reply[:60]}"
        )

    def test_epistemic_recall_vs_current_scene(self):
        """Helix must recall facts from memory lanes while maintaining awareness that Joshua is asking now."""
        # Setup context with past memory
        recalled_fact = "Jordan reported that the sensor latency on the mining rover was exactly 140ms in the test shaft."
        current_request = "Joshua asked: What was the sensor latency Jordan reported for the rover?"
        
        prompt = (
            f"[I remember:]\n- {recalled_fact}\n\n"
            f"[I sense now (live hardware):]\nRoom temperature 21C, ambient quiet.\n\n"
            f"[What was said to me now]\n{current_request}\n\n"
            "Answer the question directly using what you remember:"
        )

        response = self.session.send_context(prompt)
        self.assertTrue(len(response.strip()) > 0)
        # Should accurately recall 140ms or 140
        self.assertTrue(
            "140" in response,
            f"Expected 140ms in recall response, got: {response}"
        )

    def test_digital_workspace_interaction_and_action_intent(self):
        """When an action in the digital workspace is required, foreground decoding must produce an action intention."""
        # Simulated action prompt demanding a workspace file inspection
        prompt = (
            "My current request asks me to inspect a file in the workspace.\n"
            "Format your reply as a structured action:\n"
            "{\"action\": \"read\", \"arguments\": {\"path\": \"thinking/contemplative_canvas.md\"}}"
        )
        output, kind = decode_foreground(prompt)
        self.assertEqual(kind, "intention")
        from core.mindscape_intention import parse_intention
        parsed = parse_intention(output)
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed.get("action"), "open")
        self.assertIn("path", parsed.get("arguments", {}))


if __name__ == "__main__":
    unittest.main()
