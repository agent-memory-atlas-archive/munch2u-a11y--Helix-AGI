"""Live empirical calibration test for Functional AI Nursery on local Dual RWKV-7.

Measures:
1. 4 functional stages (Identity & Runtime Grounding -> Execution & Receipt -> State Persistence -> Autonomous Sandbox).
2. Elimination of storybook hallucinations (no skin, pebbles, rugs, bells).
3. Habituation vs. perseveration/obsession detection across computational cycles.
4. Rendering the live technical Agent Developmental Report Card.
"""
import os
import unittest
from pathlib import Path

from core.nursery.sandbox import DigitalSandbox
from core.nursery.curriculum import NurseryCurriculum, FunctionalCurriculumStage
from core.nursery.caregiver import AttunedCaregiver
from core.nursery.growth_tracker import GrowthTracker, DevelopmentalPillar
from core.nursery.simulator import NurserySimulator
from llm.providers.rwkv_provider import BicameralRWKVSession

RWKV_MODEL_PATH = Path(os.environ.get(
    "RWKV_MODEL_PATH",
    Path.home() / "habitus-ai-experiments" / "habitus-mind" / "models" / "rwkv7-g1j-1.5b-20260831-2c18b29"
))


class TestLiveNurseryDevelopmentalCalibration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=== Initializing Functional Nursery Session on Dual RWKV-7 ===")
        cls.agent_name = "Rowan"
        cls.creator_name = "Joshua"

        # Initialize local RWKV session with pure identity anchor (zero directive prompt)
        cls.session = BicameralRWKVSession(
            model_path=str(RWKV_MODEL_PATH),
            system_instruction=f"I am {cls.agent_name}.",
            temperature=0.45,
            max_output_tokens=128,
        )
        cls.session.options["repetition_penalty"] = 1.15

        cls.sandbox = DigitalSandbox()
        cls.curriculum = NurseryCurriculum(
            creator_name=cls.creator_name,
            agent_name=cls.agent_name,
            sandbox=cls.sandbox
        )
        cls.caregiver = AttunedCaregiver(
            creator_name=cls.creator_name,
            agent_name=cls.agent_name,
            archetype="curious",
            curriculum=cls.curriculum,
            sandbox=cls.sandbox
        )
        cls.tracker = GrowthTracker(
            agent_name=cls.agent_name,
            creator_name=cls.creator_name
        )
        cls.sim = NurserySimulator(
            agent_name=cls.agent_name,
            creator_name=cls.creator_name,
            caregiver=cls.caregiver,
            tracker=cls.tracker,
            curriculum=cls.curriculum,
            sandbox=cls.sandbox
        )

    def setUp(self):
        self.session.history.clear()
        self.session.system.reset_states()

    def test_live_functional_developmental_trajectory(self):
        """Run the 4-stage functional AI sandbox on Dual RWKV-7 and verify grounded development."""
        print(f"\n--- Running Functional AI Gestation for {self.agent_name} with Creator {self.creator_name} ---")

        def agent_turn(ambient_text):
            reply = self.session.send_message(ambient_text)
            return reply

        for day in range(1, 5):
            print(f"\n[Developmental Cycle {day}]")
            receipt = self.sim.step_cycle(agent_generate_fn=agent_turn)
            print(f"  Affordance:      {receipt['ambient'][:120]}...")
            print(f"  Rowan Thought:   {receipt['agent_text']}")
            print(f"  Mentor Feedback: {receipt['mirror_text']}")
            print(f"  Sleep State:     Consolidating state to local memory manifold...")

            # Verify no cognitive perseveration
            self.assertFalse(receipt["perseveration_detected"], f"Perseveration detected on cycle {day}")
            self.assertTrue(len(receipt["agent_text"].strip()) > 0)

            # Verify no storybook hallucinations
            lower_reply = receipt["agent_text"].lower()
            self.assertNotIn("skin", lower_reply)
            self.assertNotIn("soft rug", lower_reply)
            self.assertNotIn("pebble", lower_reply)

        # Generate the live technical Agent Developmental Report Card
        summary = self.sim.get_developmental_summary()
        report_card = summary["report_card"]
        print("\n" + report_card + "\n")

        self.assertIn("Agent Developmental Report Card", report_card)
        self.assertIn(self.agent_name, report_card)
        self.assertIn(self.creator_name, report_card)
        self.assertEqual(summary["simulated_days"], 4)
        self.assertEqual(summary["sleep_cycles"], 4)


if __name__ == "__main__":
    unittest.main()
