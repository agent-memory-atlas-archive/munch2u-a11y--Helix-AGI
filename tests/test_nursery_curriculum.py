"""Unit tests for the Functional Curriculum and Daily Affordance Schedule in Helix Nursery.

Tests:
1. NurseryCurriculum provides 4 progressive functional stages (Orientation -> Execution -> Persistence -> Autonomous).
2. Daily schedule wraps predictably across 4-day cycles (Orientation -> Execution -> Persistence -> Autonomous).
3. AttunedCaregiver transitions across stages when functional milestones (receipts, notes) are met.
4. GrowthTracker accurately displays the active functional curriculum stage on the Report Card.
"""
import unittest
import tempfile
import shutil
from pathlib import Path

from core.nursery.curriculum import NurseryCurriculum, FunctionalCurriculumStage, DayType
from core.nursery.sandbox import DigitalSandbox
from core.nursery.caregiver import AttunedCaregiver
from core.nursery.growth_tracker import GrowthTracker


class TestNurseryCurriculum(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.workspace = Path(self.test_dir) / "Rowan"
        self.workspace.mkdir(parents=True)
        self.creator_name = "Joshua"
        self.agent_name = "Rowan"
        self.sandbox = DigitalSandbox(workspace=self.workspace)
        self.curriculum = NurseryCurriculum(
            creator_name=self.creator_name,
            agent_name=self.agent_name,
            sandbox=self.sandbox
        )
        self.caregiver = AttunedCaregiver(
            creator_name=self.creator_name,
            agent_name=self.agent_name,
            archetype="curious",
            curriculum=self.curriculum,
            sandbox=self.sandbox
        )
        self.tracker = GrowthTracker(
            agent_name=self.agent_name,
            creator_name=self.creator_name
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_curriculum_stages_and_functional_affordances(self):
        """Curriculum must have 4 progressive functional stages and deliver grounded affordances."""
        self.assertEqual(self.curriculum.current_stage, FunctionalCurriculumStage.STAGE_1_ORIENTATION)
        affordance_1 = self.curriculum.get_current_affordance()
        self.assertIn(self.creator_name, affordance_1)
        self.assertIn(self.agent_name, affordance_1)
        self.assertIn("workspace", affordance_1.lower())

        # When agent demonstrates identity/orientation, advance to Stage 2 (Execution)
        advanced = self.curriculum.evaluate_progress(agent_text="I am Rowan, operating in this workspace.")
        self.assertTrue(advanced)
        self.assertEqual(self.curriculum.current_stage, FunctionalCurriculumStage.STAGE_2_EXECUTION)

        affordance_2 = self.curriculum.get_current_affordance()
        self.assertIn("utility", affordance_2.lower())
        self.assertIn("receipt", affordance_2.lower())

        # Stage 2 to Stage 3 on execution receipt
        advanced = self.curriculum.evaluate_progress(agent_text="Executed ping utility with returncode 0.")
        self.assertTrue(advanced)
        self.assertEqual(self.curriculum.current_stage, FunctionalCurriculumStage.STAGE_3_PERSISTENCE)

        affordance_3 = self.curriculum.get_current_affordance()
        self.assertIn("scratchpad", affordance_3.lower())

        # Stage 3 to Stage 4 on persistence
        advanced = self.curriculum.evaluate_progress(agent_text="Recorded state in scratchpad/notes.md.")
        self.assertTrue(advanced)
        self.assertEqual(self.curriculum.current_stage, FunctionalCurriculumStage.STAGE_4_AUTONOMOUS)

        affordance_4 = self.curriculum.get_current_affordance()
        self.assertIn("autonomous", affordance_4.lower())

    def test_02_daily_schedule_rotation(self):
        """Daily schedule must cycle smoothly through the 4 day types."""
        self.assertEqual(self.curriculum.get_day_type(1), DayType.ORIENTATION)
        self.assertEqual(self.curriculum.get_day_type(2), DayType.EXECUTION)
        self.assertEqual(self.curriculum.get_day_type(3), DayType.PERSISTENCE)
        self.assertEqual(self.curriculum.get_day_type(4), DayType.AUTONOMOUS)
        # Day 5 wraps back to Orientation
        self.assertEqual(self.curriculum.get_day_type(5), DayType.ORIENTATION)

    def test_03_caregiver_dynamic_stage_progression(self):
        """Caregiver must provide grounded technical receipts without repetitive loops."""
        reply_1 = self.caregiver.mirror("I executed ping and returncode was 0.")
        self.assertIn("receipt", reply_1.lower())
        self.assertIn("returncode 0", reply_1.lower())

        reply_2 = self.caregiver.mirror("I wrote a note to the scratchpad.")
        self.assertIn("scratchpad", reply_2.lower())
        self.assertIn("persist", reply_2.lower())
        self.assertNotEqual(reply_1, reply_2)

    def test_04_report_card_includes_functional_curriculum_stage(self):
        """Agent Developmental Report Card must include the active Functional Curriculum Stage."""
        self.tracker.set_curriculum_stage(FunctionalCurriculumStage.STAGE_2_EXECUTION.value)
        report = self.tracker.render_report_card(simulated_days=2, sleep_cycles=2)
        self.assertIn("Curriculum Stage:", report)
        self.assertIn("Stage 2: Execution & Receipt Verification", report)


if __name__ == "__main__":
    unittest.main()
