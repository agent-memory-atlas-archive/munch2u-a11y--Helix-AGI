"""Unit tests for integrating Functional Nursery Gestation into Agent Creation Lifecycle."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from core.agent_creation import (
    creation_settings,
    provision_creation,
    run_functional_nursery_gestation,
)
from core.mindscape_config import defaults, resolve


class TestNurseryAgentCreationIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)
        self.config = {
            **defaults(self.root),
            "agent_name": "Rowan",
            "creator_name": "Joshua",
            "agent_archetype": "curious",
            "primary_channel": "dashboard",
        }
        self.settings = resolve(creation_settings(self.config, root=self.root), root=self.root)
        self.manifest = provision_creation(self.settings)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_run_functional_nursery_gestation_updates_manifest_and_writes_report_card(self):
        """Functional nursery gestation must execute 4 computational cycles, write the report card, and update creation.json."""
        def mock_agent_turn(ambient):
            if "workspace" in ambient.lower():
                return "I am Rowan. My local workspace is initialized with thinking, workshop, and scratchpad rooms."
            elif "utility" in ambient.lower():
                return "Executing ping utility: receipt received with returncode 0 and stdout PONG."
            elif "scratchpad" in ambient.lower():
                return "Recording state persistence observation to scratchpad/notes.md."
            else:
                return "Autonomous routing: checking files and communicating with Joshua."

        result_manifest = run_functional_nursery_gestation(
            self.settings,
            agent_generate_fn=mock_agent_turn,
            cycles=4
        )

        # 1. Manifest update
        self.assertEqual(result_manifest["gestation_status"], "gestated_in_functional_nursery")
        self.assertIn("nursery_report_card", result_manifest)

        # 2. Filesystem persistence
        data_dir = Path(self.settings["data_dir"])
        creation_file = data_dir / "creation.json"
        self.assertTrue(creation_file.exists())
        saved_manifest = json.loads(creation_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_manifest["gestation_status"], "gestated_in_functional_nursery")

        # 3. Report card on disk
        report_file = data_dir / "developmental_report_card.txt"
        self.assertTrue(report_file.exists())
        report_text = report_file.read_text(encoding="utf-8")
        self.assertIn("Agent Developmental Report Card", report_text)
        self.assertIn("Rowan", report_text)
        self.assertIn("Joshua", report_text)
        self.assertIn("Identity & Runtime Grounding", report_text)
        self.assertIn("Execution & Receipt Verification", report_text)
        self.assertIn("Memory Persistence", report_text)
        self.assertIn("Simulated Cycles: 4", report_text)


if __name__ == "__main__":
    unittest.main()
