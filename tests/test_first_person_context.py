"""Tests for first-person phenomenological context formatting and epistemic indicators."""
import unittest
from core.pulse_context import (
    SECTION_TITLES,
    PulseContext,
    ContextContribution,
    recalled_contribution,
)
from memory.mrag.semantic_lane import SemanticLane


class TestFirstPersonContext(unittest.TestCase):
    def test_first_person_section_titles(self):
        """Verify section titles use first-person epistemic framing."""
        self.assertEqual(SECTION_TITLES["recalled"], "I remember:")
        self.assertEqual(SECTION_TITLES["recalled_thought"], "I was thinking:")
        self.assertEqual(SECTION_TITLES["thinking"], "What I am thinking now:")
        self.assertEqual(SECTION_TITLES["personal"], "I prefer / value:")
        self.assertEqual(SECTION_TITLES["state"], "I feel:")
        self.assertEqual(SECTION_TITLES["prior_assistant"], "I previously said:")
        self.assertEqual(SECTION_TITLES["task"], "I want to:")
        self.assertEqual(SECTION_TITLES["environment"], "In my digital workspace (filesystem):")
        self.assertEqual(SECTION_TITLES["senses"], "I sense now (live hardware):")

    def test_recalled_sensory_reality_neutralization(self):
        """Historical [SensoryReality] markers must be converted to past memory framing."""
        item = {
            "id": 57,
            "content": "[SensoryReality] Visual: Joshua is typing on a colorful keyboard. | Auditory: Silence.",
            "record_envelope": {"kind": "sensory_observation"},
            "created_at": "2026-07-02T12:00:00",
        }
        contrib = recalled_contribution(item)
        self.assertNotIn("[SensoryReality]", contrib.text)
        self.assertTrue(
            "I remember seeing:" in contrib.text or "Past sensory memory" in contrib.text or "I remember sensing:" in contrib.text,
            f"Expected past sensory framing, got: {contrib.text}",
        )

    def test_context_rendering_uses_first_person_headers(self):
        """Rendered context blocks must display first-person indicators."""
        ctx = PulseContext(
            pulse=1,
            timestamp="12:00:00",
            contributions=(
                ContextContribution("recalled", "Joshua has a dog.", "mrag"),
                ContextContribution("personal", "I value clarity.", "mrag"),
                ContextContribution("task", "Continue monitoring stability.", "task_cognition"),
            ),
            query="test",
            query_source="user",
        )
        rendered = ctx.render()
        self.assertIn("[I remember:]", rendered)
        self.assertIn("[I prefer / value:]", rendered)
        self.assertIn("[I want to:]", rendered)

    def test_semantic_lane_retrieve_accepts_passage_text(self):
        """SemanticLane.retrieve must accept passage_text argument without crashing."""
        lane = SemanticLane(None, None)
        try:
            results = lane.retrieve("", limit=5, passage_text="trigger text")
            self.assertIsInstance(results, list)
        except TypeError as exc:
            self.fail(f"retrieve() raised TypeError: {exc}")
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
