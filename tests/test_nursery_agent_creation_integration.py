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

    def test_default_gestation_has_no_canned_responses_and_real_sleep(self):
        """When run without external model generator, gestation must NOT return identical canned strings and must write real sleep receipts."""
        result_manifest = run_functional_nursery_gestation(
            self.settings,
            agent_generate_fn=None,  # Tests the default gestation reflex loop
            cycles=4
        )

        data_dir = Path(self.settings["data_dir"])
        journal_file = data_dir / "memory" / "cognitive_journal.jsonl"
        self.assertTrue(journal_file.exists(), "cognitive_journal.jsonl was not written")
        journal_records = [json.loads(l) for l in journal_file.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(len(journal_records), 4)

        # Responses across the 4 cycles must NOT be identical canned strings!
        agent_responses = [r["agent_text"] for r in journal_records]
        self.assertEqual(len(set(agent_responses)), 4, f"Canned responses detected! Responses: {agent_responses}")

        # Real sleep consolidation receipts must exist for all 4 cycles
        receipts_file = data_dir / "memory" / "sleep_consolidation_receipts.jsonl"
        self.assertTrue(receipts_file.exists(), "sleep_consolidation_receipts.jsonl was not written")
        sleep_receipts = [json.loads(l) for l in receipts_file.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(len(sleep_receipts), 4)

        # Real scratchpad file must exist
        scratchpad_file = data_dir / "scratchpad" / "development_notes.md"
        self.assertTrue(scratchpad_file.exists(), "scratchpad/development_notes.md was not written")
        self.assertGreater(len(scratchpad_file.read_text(encoding="utf-8").strip()), 0)


if __name__ == "__main__":
    unittest.main()
