"""Creation, credentials and native seed diagnostics, not agent evaluation."""
import contextlib
from dataclasses import asdict
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.agent_creation import (ARCHETYPES, clean_name, creation_settings, native_seed,
                                 provision_creation, validate_channel, verify_native_profile)
from core.mindscape_config import defaults, resolve, ROOT
from bootstrap import BootstrapContext, build_seed_bundle

sys.path.insert(0, defaults()["mindscape"]["package_path"])


class CreationDiagnostics(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = {**defaults(self.root), "agent_name": "Nova", "creator_name": "Morgan",
                       "agent_archetype": "curious", "primary_channel": "dashboard"}

    def test_named_home_is_isolated_from_named_persistent_mind_and_preserves_files(self):
        settings = resolve(creation_settings(self.config, root=self.root), root=self.root)
        manifest = provision_creation(settings)
        self.assertEqual(Path(manifest["home"]).name, "Nova")
        self.assertEqual(Path(manifest["data_dir"]).name, "Nova")
        self.assertNotEqual(Path(manifest["home"]), Path(manifest["data_dir"]))
        self.assertEqual(manifest["native_seed"], {"human_name": "Morgan", "agent_name": "Nova", "taste_schema": "curious"})
        note = Path(manifest["home"], "bedroom/closet/keep.txt")
        note.write_text("keep")
        provision_creation(settings)
        self.assertEqual(note.read_text(), "keep")
        self.assertEqual(json.loads(Path(manifest["data_dir"], "creation.json").read_text()), manifest)

    def test_invalid_names_and_archetypes_fail_before_writing(self):
        for name in ("", ".", "..", "../elsewhere", "A/B", "A\\B", "A\nB", "A\x00B"):
            with self.assertRaises(ValueError):
                clean_name(name)
        self.assertEqual(clean_name("  Nova 星  "), "Nova 星")
        with self.assertRaises(ValueError):
            creation_settings({**self.config, "agent_archetype": "invented"}, root=self.root)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_existing_identity_cannot_be_regestated_with_another_archetype(self):
        settings = resolve(creation_settings(self.config, root=self.root), root=self.root)
        provision_creation(settings)
        with self.assertRaisesRegex(ValueError, "different identity or archetype"):
            creation_settings({**settings, "agent_archetype": "builder"}, root=self.root)
        changed_name = creation_settings({**settings, "agent_name": "Atlas"}, root=self.root)
        self.assertEqual(Path(changed_name["data_dir"]).name, "Atlas")
        self.assertEqual(Path(changed_name["mindscape"]["home"]).name, "Atlas")

    def test_primary_channel_requires_enabled_complete_credentials(self):
        selected = {**self.config, "primary_channel": "telegram"}
        with self.assertRaises(ValueError):
            validate_channel(selected)
        selected["telegram_enabled"] = True
        with self.assertRaises(ValueError):
            validate_channel(selected, {})
        self.assertEqual(validate_channel(selected, {"HELIX_TELEGRAM_TOKEN": "diagnostic-only"}), "telegram")
        settings = resolve(creation_settings(selected, root=self.root, credentials={"HELIX_TELEGRAM_TOKEN": "diagnostic-only"}), root=self.root)
        manifest = provision_creation(settings)
        self.assertEqual(manifest["primary_channel"], "telegram")
        self.assertNotIn("diagnostic-only", json.dumps(manifest))

    def test_native_checkpoint_identity_is_checked_readonly_before_creation(self):
        data = self.root / "existing"
        checkpoint = data / "mindscape/joint/checkpoint"
        checkpoint.mkdir(parents=True)
        with sqlite3.connect(checkpoint / "mind.sqlite") as database:
            database.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
            database.execute("INSERT INTO metadata VALUES (?, ?)", ("gestation_profile", json.dumps({
                "human_name": "Morgan", "agent_name": "OtherAgent", "taste_schema": "builder"})))
        (checkpoint.parent / "LATEST.json").write_text('{"checkpoint":"checkpoint"}')
        before = (checkpoint / "mind.sqlite").read_bytes()
        with self.assertRaisesRegex(ValueError, "existing native mind"):
            creation_settings({**self.config, "data_dir": str(data)}, root=self.root)
        self.assertEqual(before, (checkpoint / "mind.sqlite").read_bytes())

    def test_bootstrap_records_configured_primary_channel_without_claiming_connection(self):
        bundle = build_seed_bundle(BootstrapContext("Nova", "Morgan", "standard", "friendly",
                                                  channels=["Dashboard", "Telegram"], primary_channel="Telegram"))
        text = "\n".join(item["content"] for item in bundle["memories"])
        self.assertIn("main channel was configured as Telegram", text)
        self.assertIn("verify which routes", text)

    def test_cli_creation_uses_real_setup_pipeline_without_model_inference(self):
        import setup
        config = defaults()
        argv = ["setup.py", "--non-interactive", "--composition", "mindscape",
                "--agent-name", "Nova", "--creator-name", "Morgan", "--archetype", "builder",
                "--primary-channel", "dashboard", "--mightymem-path", config["mindscape"]["package_path"],
                "--rwkv-model", config["mindscape"]["rwkv_model"], "--workspace", str(self.root),
                "--local-context-window", "16384"]
        credentials = self.root / "credentials"
        def expand(value):
            if value == "~/.config/helix":
                return str(credentials)
            return str(self.root / "no-integration")
        with patch.object(setup, "__file__", str(self.root / "setup.py")), patch.object(sys, "argv", argv), \
                patch("setup.os.path.expanduser", side_effect=expand), contextlib.redirect_stdout(io.StringIO()):
            setup.main()
        saved = json.loads((self.root / "config/config.json").read_text())
        self.assertEqual(saved["agent_archetype"], "builder")
        self.assertEqual(saved["local_context_window"], 16384)
        self.assertEqual(Path(saved["mindscape"]["home"]).name, "Nova")
        beliefs = list(Path(saved["data_dir"], "beliefs").glob("*.json"))
        self.assertTrue(beliefs)
        self.assertIn("Nova", "\n".join(path.read_text() for path in beliefs))
        self.assertTrue(Path(saved["data_dir"], "memory/cognitive_journal.jsonl").exists())
        self.assertFalse(Path(saved["data_dir"], "mindscape/joint/LATEST.json").exists())
        self.assertEqual((credentials / "credentials.env").stat().st_mode & 0o777, 0o600)

    def test_native_gestation_creates_real_identity_taste_and_output_prior_edges(self):
        # Actual native gestation on a small isolated graph is a component
        # diagnostic. It is not the RWKV/cortex/foreground product trial.
        from habitus_ai.pipeline import BaseAgenticMemoryRAG
        from habitus_ai.gestation import gestate, load_profile, TASTE_SCHEMAS
        from habitus_ai.types import GraphSide
        from habitus_ai.graph import OUTPUT_NODE_IDS
        for schema in ARCHETYPES:
            with self.subTest(schema=schema), BaseAgenticMemoryRAG(self.root / f"{schema}.sqlite") as mind:
                before = {trunk: mind.store.find_edge(GraphSide.OUTPUT, "SELF", node).log_strength
                          for trunk, node in OUTPUT_NODE_IDS.items()}
                config = {**self.config, "agent_archetype": schema}
                profile = gestate(mind, **native_seed(config), model_backend="component-diagnostic", model_name="no model inference")
                self.assertEqual(load_profile(mind), profile)
                self.assertTrue(verify_native_profile(profile, config)["verified"])
                self.assertEqual(mind.store.get_record("gestation:self-identity").text, "My name is Nova.")
                self.assertIsNotNone(mind.store.get_record("gestation:taste:" + schema))
                for trunk, bias in TASTE_SCHEMAS[schema].output_biases.items():
                    edge = mind.store.find_edge(GraphSide.OUTPUT, "SELF", OUTPUT_NODE_IDS[trunk])
                    self.assertAlmostEqual(edge.log_strength - before[trunk], bias)
                with self.assertRaises(ValueError):
                    gestate(mind, **native_seed(config), model_name="no inference")

    def test_native_constructor_rejects_an_invalid_seed_before_loading_weights(self):
        from habitus_ai.continual_mind import ContinualMind
        with self.assertRaisesRegex(ValueError, "unknown gestation taste"):
            ContinualMind(model=self.root / "missing-model", directory=self.root / "not-created",
                          workspace=self.root, gestation_seed={"human_name": "Morgan", "agent_name": "Nova", "taste_schema": "invented"})
        self.assertFalse((self.root / "not-created").exists())


class WizardCreationDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_identity_and_channel_pages_persist_user_choices_and_named_home(self):
        from wizard.pages.agent_info import AgentInfoPage
        from wizard.pages.credentials import CredentialsPage
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as directory:
            config = defaults(Path(directory))
            config.update(ai_assist=False, data_dir="data")
            wizard = SimpleNamespace(config=config, next_page=Mock(), prev_page=Mock())
            identity = AgentInfoPage(wizard)
            identity.agent_name.setText("UI Nova")
            identity.creator_name.setText("Morgan")
            identity.archetype_combo.setCurrentIndex(identity.archetype_combo.findData("deliberate"))
            with patch("wizard.pages.agent_info.ROOT", Path(directory)):
                identity._save_and_next()
            self.assertEqual(wizard.config["agent_archetype"], "deliberate")
            self.assertEqual(Path(wizard.config["mindscape"]["home"]).name, "UI Nova")
            with patch("wizard.pages.credentials._load_existing_creds", return_value={}):
                credentials = CredentialsPage(wizard)
            credentials.telegram_check.setChecked(True)
            credentials.telegram_token.setText("diagnostic-not-a-real-token")
            credentials.primary_channel.setCurrentIndex(credentials.primary_channel.findData("telegram"))
            with patch("wizard.pages.credentials.QMessageBox.warning") as warning:
                credentials._save_and_next()
            warning.assert_not_called()
            self.assertEqual(wizard.config["primary_channel"], "telegram")
            self.assertTrue(wizard.config["telegram_enabled"])
            wizard.next_page.assert_called()
            identity.deleteLater()
            credentials.deleteLater()

    def test_wizard_stores_tokens_privately_and_forwards_actual_creation_choices(self):
        from wizard import app
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = creation_settings({**defaults(root), "agent_name": "Nova", "creator_name": "Morgan",
                                        "agent_archetype": "builder", "primary_channel": "telegram",
                                        "telegram_enabled": True, "telegram_token": "diagnostic-only-token"}, root=root)
            context = SimpleNamespace(config=config)
            credential_path = root / "credentials/credentials.env"
            with patch.object(app, "CONFIG_DIR", root / "config"), patch.object(app, "CONFIG_PATH", root / "config/config.json"), \
                    patch.object(app, "CRED_DIR", credential_path.parent), patch.object(app, "CRED_PATH", credential_path), \
                    patch.object(app, "BASE_DIR", root):
                app.save_config(config)
                app.HelixApp._write_credentials(context)
                self.assertNotIn("diagnostic-only-token", (root / "config/config.json").read_text())
                self.assertIn("HELIX_TELEGRAM_TOKEN=diagnostic-only-token", credential_path.read_text())
                self.assertEqual(credential_path.stat().st_mode & 0o777, 0o600)
                with patch("subprocess.run") as run:
                    self.assertTrue(app.HelixApp._run_bootstrap(context))
                command = run.call_args.args[0]
                self.assertIn("--archetype=builder", command)
                self.assertIn("--primary-channel=telegram", command)
                self.assertIn("--data-dir=" + config["data_dir"], command)
                self.assertNotIn("diagnostic-only-token", " ".join(command))


if __name__ == "__main__":
    unittest.main()
