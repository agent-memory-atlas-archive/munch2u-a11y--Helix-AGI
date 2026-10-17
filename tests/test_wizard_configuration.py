"""Runtime selection/bootstrap tests without GUI, inference, or credentials."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from core.mindscape_config import defaults
from wizard.configuration import load_wizard_config, select_provider, supported_providers, bootstrap_command


class WizardConfigurationTests(unittest.TestCase):
    def test_rwkv_selection_updates_all_native_model_fields_without_mutating_input(self):
        config = defaults()
        before = deepcopy(config)
        selected = select_provider(config, "bicameral_rwkv", "/chosen/model")
        self.assertEqual(config, before)
        self.assertEqual(selected["llm_provider"], "rwkv")
        self.assertEqual(selected["local_provider"], "rwkv")
        self.assertEqual(selected["llm_model"], "/chosen/model")
        self.assertEqual(selected["mindscape"]["rwkv_model"], "/chosen/model")
        self.assertEqual(selected["task_cognition_mode"], "off")

    def test_native_ollama_keeps_native_checkpoint_and_unsupported_choice_does_not_mutate(self):
        config = defaults()
        selected = select_provider(config, "ollama", "chosen:local")
        self.assertEqual(selected["local_model"], "chosen:local")
        self.assertEqual(selected["mindscape"]["rwkv_model"], config["mindscape"]["rwkv_model"])
        before = deepcopy(config)
        with self.assertRaises(ValueError):
            select_provider(config, "gemini", "model")
        self.assertEqual(config, before)
        self.assertNotIn("openai", supported_providers("helix"))
        self.assertNotIn("alibaba", supported_providers("helix"))

    def test_legacy_configuration_is_not_silently_upgraded_and_tokens_survive_model_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text('{"agent_name":"Existing","llm_provider":"codex_cli","llm_model":""}')
            config = load_wizard_config(path, defaults(), {"HELIX_TELEGRAM_TOKEN": "diagnostic"})
            self.assertEqual(config["composition"], "helix")
            self.assertEqual(config["llm_provider"], "codex_cli")
            edited = select_provider(config, "codex_cli", "")
            self.assertEqual(edited["telegram_token"], "diagnostic")

    def test_defaults_are_independent_and_corrupt_configuration_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            original = defaults()
            first = load_wizard_config(path, original)
            first["mindscape"]["home"] = "changed"
            self.assertNotEqual(load_wizard_config(path, original)["mindscape"]["home"], "changed")
            path.write_text("[]")
            with self.assertRaises(ValueError):
                load_wizard_config(path, original)
            self.assertEqual(path.read_text(), "[]")

    def test_bootstrap_forwards_selected_provider_model_paths_and_no_secrets(self):
        config = defaults()
        config.update(agent_name="A Name", creator_name="Creator", data_dir="/chosen/state",
                      llm_provider="ollama", llm_model="chosen:local", telegram_token="secret-test-only")
        config["mindscape"].update(package_path="/chosen/native", home="/chosen/home")
        command = bootstrap_command(config, Path("/checkout"), "python")
        for arg in ("--composition-only", "--provider=ollama", "--model=chosen:local",
                    "--mightymem-path=/chosen/native", "--agent-home=/chosen/home", "--data-dir=/chosen/state"):
            self.assertIn(arg, command)
        self.assertNotIn("secret-test-only", " ".join(command))

    def test_helix_configuration_only_bootstraps_selected_directory_and_keeps_provider(self):
        import setup
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            credentials = root / "credentials"
            target = root / "selected"
            args = ["setup.py", "--non-interactive", "--composition=helix", "--composition-only",
                    "--agent-name=Selected", "--creator-name=Creator", "--provider=ollama",
                    "--model=chosen:local", "--data-dir=" + str(target)]
            with patch.object(setup, "__file__", str(root / "setup.py")), patch.object(sys, "argv", args), \
                 patch("setup.os.path.expanduser", return_value=str(credentials)):
                setup.main()
            saved = json.loads((root / "config/config.json").read_text())
            self.assertEqual(saved["llm_provider"], "ollama")
            self.assertEqual(saved["llm_model"], "chosen:local")
            self.assertTrue((target / "memory/cognitive_journal.jsonl").is_file())
            self.assertFalse((root / "data/memory").exists())
            self.assertIn("HELIX_PROVIDER=ollama", (credentials / "credentials.env").read_text())
