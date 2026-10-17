"""Unit and integration tests for Helix Functional Developmental Nursery and Agent Developmental Report Card.

Tests:
1. AttunedCaregiver provides non-punitive, varied functional mirroring for any agent output (silence, queries, execution, notes, identity).
2. AttunedCaregiver generates varied developmental affordances across stages and days.
3. GrowthTracker tracks the 5 functional developmental pillars, measures homeostatic equilibrium vs. friction, and renders 'Agent Developmental Report Card'.
4. NurserySimulator executes developmental wake-sleep cycles, advancing capability milestones while preventing perseveration.
"""
import unittest
import tempfile
import shutil
from pathlib import Path

# Core components under test
from core.nursery.caregiver import AttunedCaregiver
from core.nursery.growth_tracker import GrowthTracker, DevelopmentalPillar
from core.nursery.simulator import NurserySimulator
from core.nursery.curriculum import NurseryCurriculum
from core.nursery.sandbox import DigitalSandbox


class TestNurseryDevelopmentalSimulation(unittest.TestCase):
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

    def test_01_caregiver_unconditional_attunement_no_dead_ends(self):
        """Caregiver must provide grounded, varied functional feedback across different operational outputs."""
        test_inputs = [
            "",  # Silence / quiet
            "Where is the workshop directory?",  # Direct query
            "I executed ping and received returncode 0.",  # Tool execution
            "I wrote my observation to scratchpad/notes.md.",  # State persistence
            "I am Rowan, operating locally in this workspace.",  # Self-naming & identity
        ]

        responses = []
        for agent_text in test_inputs:
            reply = self.caregiver.mirror(agent_text)
            self.assertTrue(isinstance(reply, str) and len(reply.strip()) > 0)
            self.assertNotIn("invalid", reply.lower())
            self.assertNotIn("error", reply.lower())
            self.assertNotIn("command not recognized", reply.lower())
            responses.append(reply)

        # Responses must vary across the 5 distinct operational intents
        self.assertEqual(len(set(responses)), len(responses), "Caregiver repeated identical responses")

    def test_02_caregiver_multi_angled_affordances_across_days(self):
        """Caregiver generates diverse functional affordances across daily cycles."""
        phrasings = set()
        for day in range(1, 5):
            prompt = self.caregiver.generate_ambient_stimulus(day=day)
            self.assertTrue(len(prompt) > 0)
            phrasings.add(prompt)

        # Across the 4-day cycle, all 4 daily affordances must be distinct
        self.assertEqual(len(phrasings), 4, f"Affordances lacked diversity: {phrasings}")

    def test_03_growth_tracker_report_card_structure_and_metrics(self):
        """GrowthTracker calculates homeostatic equilibrium and formats the Agent Developmental Report Card."""
        self.tracker.record_observation(
            pillar=DevelopmentalPillar.IDENTITY_GROUNDING,
            score=0.9,
            observation="Consistently uses first-person 'I' and knows name Rowan in local workspace."
        )
        self.tracker.record_observation(
            pillar=DevelopmentalPillar.BOUNDARY_DISCRIMINATION,
            score=0.95,
            observation=f"Distinguishes internal thought stream from direct communication to {self.creator_name}."
        )
        self.tracker.record_observation(
            pillar=DevelopmentalPillar.ENVIRONMENTAL_ORIENTATION,
            score=0.8,
            observation="Comfortable with local shell cadence and workspace layout."
        )
        self.tracker.record_observation(
            pillar=DevelopmentalPillar.EXECUTION_VERIFICATION,
            score=0.85,
            observation="Executes local utilities and inspects returncode and stdout receipts."
        )
        self.tracker.record_observation(
            pillar=DevelopmentalPillar.MEMORY_PERSISTENCE,
            score=0.88,
            observation="Writes to scratchpad/ and verifies persistence across sleep cycles."
        )

        # Record homeostatic affect balance (e.g. 88% equilibrium, 12% constructive friction)
        self.tracker.record_affect_sample(calm_satisfaction=0.88, constructive_challenge=0.12)

        report = self.tracker.render_report_card(simulated_days=14, sleep_cycles=5)
        self.assertIn("Agent Developmental Report Card", report)
        self.assertIn(self.agent_name, report)
        self.assertIn(self.creator_name, report)
        self.assertIn("Identity & Runtime Grounding", report)
        self.assertIn("Execution & Receipt Verification", report)
        self.assertIn("Memory Persistence", report)
        self.assertIn("Boundary Discrimination", report)
        self.assertIn("Environmental & Spatial Navigation", report)
        self.assertIn("Homeostatic Equilibrium", report)
        self.assertIn("Constructive Friction", report)

    def test_04_nursery_simulator_step_and_obsession_prevention(self):
        """Simulator executes developmental cycles and detects when an agent perseverates."""
        sim = NurserySimulator(
            agent_name=self.agent_name,
            creator_name=self.creator_name,
            caregiver=self.caregiver,
            tracker=self.tracker,
            curriculum=self.curriculum,
            sandbox=self.sandbox
        )

        def mock_agent_turn(ambient):
            return "I am Rowan, operating in my local workspace."

        for _ in range(3):
            cycle_result = sim.step_cycle(agent_generate_fn=mock_agent_turn)
            self.assertTrue(cycle_result["cycle_completed"])
            self.assertIn("sleep_consolidated", cycle_result)

        stats = sim.get_developmental_summary()
        self.assertGreater(stats["simulated_days"], 0)
        self.assertGreater(stats["sleep_cycles"], 0)
        self.assertFalse(stats["perseveration_detected"], "Perseveration was incorrectly detected")


if __name__ == "__main__":
    unittest.main()
