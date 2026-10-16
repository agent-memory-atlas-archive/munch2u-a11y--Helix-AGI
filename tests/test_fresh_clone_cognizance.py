"""TDD tests for fresh clone zero-friction startup and cognitive grounding."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.mindscape_config import defaults
from core.agent_creation import creation_settings
from setup import upsert_env_values, main as setup_main


class TestFreshCloneStartup(unittest.TestCase):
    def test_setup_accepts_archetype_channel_and_data_dir(self):
        """setup.py must accept --archetype, --primary-channel, and --data-dir."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data/agents/Aura"
            argv = [
                "setup.py",
                "--non-interactive",
                "--composition=mindscape",
                "--composition-only",
                "--agent-name=Aura",
                "--creator-name=Dev",
                "--archetype=builder",
                "--primary-channel=dashboard",
                f"--data-dir={data_dir}",
            ]
            with patch("sys.argv", argv), patch("setup.__file__", str(root / "setup.py")):
                setup_main()

            config_file = root / "config/config.json"
            self.assertTrue(config_file.exists(), "config.json was not written")
            saved = json.loads(config_file.read_text())
            self.assertEqual(saved.get("agent_name"), "Aura")
            self.assertEqual(saved.get("agent_archetype"), "builder")
            self.assertEqual(saved.get("primary_channel"), "dashboard")
            self.assertEqual(str(saved.get("data_dir")), str(data_dir))

    def test_credential_permissions_are_strict(self):
        """upsert_env_values must ensure credentials file has 0o600 permissions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_file = Path(temp_dir) / "credentials.env"
            upsert_env_values(cred_file, {"KEY": "VALUE"})
            mode = cred_file.stat().st_mode & 0o777
            self.assertEqual(mode, 0o600)

    def test_system_instruction_explicitly_anchors_name_and_creator(self):
        """PulseLoop system instruction must explicitly anchor agent and creator identity."""
        from core.pulse_loop import PulseLoop
        loop = object.__new__(PulseLoop)
        loop.mindscape = None
        loop._task_cognition = None
        loop.beliefs = MagicMock()
        loop.beliefs.get_category.return_value = [
            {"id": "premise_1", "content": "I am Aura, created by Dev."}
        ]
        loop.config = {"agent_name": "Aura", "creator_name": "Dev"}
        instruction = loop._build_system_instruction()
        self.assertIn("Aura", instruction)
        self.assertIn("Dev", instruction)


    def test_empty_belief_store_auto_seeds_default_identity(self):
        """main.py setup_helix must auto-seed default premises if belief store is empty."""
        from bootstrap.seed_builder import BootstrapContext, write_seed_data
        from memory.belief_store import BeliefStore
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            store = BeliefStore(str(data_dir / "beliefs"))
            self.assertEqual(store.get_stats().get("premises", 0), 0)
            ctx = BootstrapContext(
                agent_name="Echo",
                creator_name="Tester",
                profile="standard",
                personality="curious",
                wake_time="08:00",
                sleep_time="23:00",
                channels=["dashboard"],
            )
            write_seed_data(data_dir, ctx, overwrite=False)
            stats = store.get_stats()
            self.assertGreater(stats.get("premises", 0), 0)
            premises = store.get_category("premises")
            self.assertTrue(any("Echo" in p.get("content", "") for p in premises))

if __name__ == "__main__":
    unittest.main()
