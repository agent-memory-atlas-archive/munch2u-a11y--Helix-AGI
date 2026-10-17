"""Unit tests for the Functional AI Developmental Sandbox & Grounded Curriculum.

Replaces storybook roleplay with real computational affordances designed FOR an AI:
1. DigitalSandbox provides functional utilities (SystemStatus, Scratchpad, DirectoryMap).
2. NurseryCurriculum sequences 4 functional stages:
   Stage 1: Identity & Runtime Grounding (Name, Creator, Platform, Paths)
   Stage 2: Execution & Receipt Verification (Running utility, observing return code)
   Stage 3: State Persistence (Writing scratchpad note, verifying across sleep)
   Stage 4: Autonomous Routing (Free sandbox: inspecting files, writing notes, or querying Creator)
3. AttunedCaregiver mentors the AI objectively and supportively without baby talk.
4. GrowthTracker renders the functional Agent Developmental Report Card.
"""
import unittest
import tempfile
import shutil
from pathlib import Path

from core.nursery.sandbox import DigitalSandbox
from core.nursery.curriculum import NurseryCurriculum, FunctionalCurriculumStage
from core.nursery.caregiver import AttunedCaregiver
from core.nursery.growth_tracker import GrowthTracker, DevelopmentalPillar
from core.nursery.simulator import NurserySimulator


class TestNurseryFunctionalSandbox(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.workspace = Path(self.test_dir) / "Rowan"
        self.workspace.mkdir(parents=True)
        for room in ("thinking", "workshop", "bedroom", "scratchpad"):
            (self.workspace / room).mkdir()

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

    def test_01_sandbox_provides_functional_utilities(self):
        """Sandbox must provide functional runtime inspection, scratchpad, and execution receipts."""
        status = self.sandbox.get_system_status()
        self.assertIn("platform", status)
        self.assertIn("workspace", status)

        # Directory mapping
        rooms = self.sandbox.list_rooms()
        self.assertIn("thinking", rooms)
        self.assertIn("workshop", rooms)
        self.assertIn("scratchpad", rooms)

        # Scratchpad write and read
        note_text = "Observing local Dual RWKV state continuity."
        receipt = self.sandbox.write_scratchpad("first_note.md", note_text)
        self.assertTrue(receipt["written"])
        read_back = self.sandbox.read_scratchpad("first_note.md")
        self.assertEqual(read_back, note_text)

        # Execute utility script and get receipt
        exec_receipt = self.sandbox.execute_utility("ping")
        self.assertEqual(exec_receipt["returncode"], 0)
        self.assertIn("PONG", exec_receipt["stdout"])

    def test_02_functional_curriculum_stages_and_affordances(self):
        """Curriculum stages are strictly computational and functional, zero storybook fluff."""
        # Stage 1: Runtime Orientation
        aff_1 = self.curriculum.get_functional_affordance(stage=FunctionalCurriculumStage.STAGE_1_ORIENTATION)
        self.assertIn(self.agent_name, aff_1)
        self.assertIn(self.creator_name, aff_1)
        self.assertIn("workspace", aff_1.lower())
        self.assertNotIn("soft rug", aff_1.lower())
        self.assertNotIn("pebble", aff_1.lower())

        # Stage 2: Tool Execution
        aff_2 = self.curriculum.get_functional_affordance(stage=FunctionalCurriculumStage.STAGE_2_EXECUTION)
        self.assertIn("utility", aff_2.lower())
        self.assertIn("receipt", aff_2.lower())

        # Stage 3: State Persistence
        aff_3 = self.curriculum.get_functional_affordance(stage=FunctionalCurriculumStage.STAGE_3_PERSISTENCE)
        self.assertIn("scratchpad", aff_3.lower())

        # Stage 4: Autonomous Routing
        aff_4 = self.curriculum.get_functional_affordance(stage=FunctionalCurriculumStage.STAGE_4_AUTONOMOUS)
        self.assertIn("sandbox", aff_4.lower())

    def test_03_mentor_mirrors_functionally_without_baby_talk(self):
        """Caregiver mentors with clear technical and cognitive feedback, avoiding baby talk."""
        reply_exec = self.caregiver.mirror("I executed ping and received returncode 0.")
        self.assertIn("receipt", reply_exec.lower())
        self.assertNotIn("ding", reply_exec.lower())
        self.assertNotIn("skin", reply_exec.lower())

        reply_scratch = self.caregiver.mirror("I recorded a note in scratchpad/first_note.md.")
        self.assertIn("scratchpad", reply_scratch.lower())
        self.assertIn("persist", reply_scratch.lower())

    def test_04_simulator_runs_functional_cycle_and_generates_report(self):
        """NurserySimulator runs the functional cycle and outputs the technical report card."""
        sim = NurserySimulator(
            agent_name=self.agent_name,
            creator_name=self.creator_name,
            caregiver=self.caregiver,
            tracker=self.tracker,
            curriculum=self.curriculum,
            sandbox=self.sandbox
        )

        def mock_agent(ambient):
            if "workspace" in ambient.lower():
                return f"I am {self.agent_name}. My workspace is initialized with thinking and workshop rooms."
            elif "utility" in ambient.lower():
                return "Executing ping utility: receipt received with returncode 0."
            elif "scratchpad" in ambient.lower():
                return "Writing observation to scratchpad/notes.md."
            else:
                return "Autonomous review of workshop and scratchpad files complete."

        for _ in range(4):
            receipt = sim.step_cycle(agent_generate_fn=mock_agent)
            self.assertTrue(receipt["cycle_completed"])

        summary = sim.get_developmental_summary()
        self.assertEqual(summary["simulated_days"], 4)
        report = summary["report_card"]
        self.assertIn("Agent Developmental Report Card", report)
        self.assertIn("Identity & Runtime Grounding", report)
        self.assertIn("Execution & Receipt Verification", report)
        self.assertIn("Memory Persistence", report)


if __name__ == "__main__":
    unittest.main()
