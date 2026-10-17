"""Selected-agent paths and UI operations, isolated from real agent data."""
from contextlib import ExitStack
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

from core.runtime_paths import RuntimePaths
from core.agent_creation import creation_settings, provision_creation
from core.mindscape_config import defaults, resolve
import dashboard.dashboard as dashboard
import dashboard.dashboard_comms as dashboard_comms
import setup


class RuntimePathTests(unittest.TestCase):
    def test_relative_home_is_root_relative_and_no_agent_is_chosen_by_glob(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = RuntimePaths.from_config({"data_dir": "data/agents/A", "mindscape": {"home": "data/homes/A"}}, root=root)
            self.assertEqual(paths.home, root / "data/homes/A")
            self.assertEqual(paths.data, root / "data/agents/A")
            self.assertEqual(paths.workspace_position(), ".")
            self.assertFalse((root / "data").exists())

    def test_latest_pointer_selects_database_readonly_and_bad_pointer_cannot_fall_back(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = RuntimePaths(root / "state", root / "home")
            checkpoint = paths.data / "mindscape/joint/checkpoint-2"
            checkpoint.mkdir(parents=True)
            database = checkpoint / "mind.sqlite"
            with sqlite3.connect(database) as connection:
                connection.execute("CREATE TABLE metadata (key TEXT, value TEXT)")
                connection.execute("INSERT INTO metadata VALUES ('agent_workspace_position', 'workshop')")
            pointer = checkpoint.parent / "LATEST.json"
            pointer.write_text('{"checkpoint":"checkpoint-2"}')
            before = hashlib.sha256(database.read_bytes()).hexdigest()
            self.assertEqual(paths.workspace_position(), "workshop")
            self.assertEqual(hashlib.sha256(database.read_bytes()).hexdigest(), before)
            pointer.write_text('{"checkpoint":"../../outside"}')
            with self.assertRaisesRegex(ValueError, "Invalid native checkpoint"):
                paths.workspace_position()

    def test_dashboard_uses_same_selected_home_for_room_upload_modules_and_motor(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            config = {"data_dir": "state/A", "mindscape": {"home": "homes/A"}}
            paths = RuntimePaths.from_config(config, root=root)
            paths.home.mkdir(parents=True)
            (paths.home / "home.json").write_text('{"rooms":{"thinking":"quiet"},"modules":{}}')
            other = root / "state/agent_home/modules"
            other.mkdir(parents=True)
            (other / "untouched.py").write_text("other agent")
            stack.enter_context(patch.object(dashboard, "BASE_DIR", root))
            stack.enter_context(patch.object(dashboard, "_read_config", return_value=config))
            stack.enter_context(patch.object(dashboard_comms, "_instance", dashboard_comms.DashboardComms(root / "messages.json")))
            client = dashboard.create_app().test_client()
            self.assertEqual(client.get("/api/modules").get_json(), {"modules": []})
            self.assertFalse((paths.home / "modules").exists())
            self.assertEqual(client.post("/api/stage_file", json={"filename": "note.txt", "content": "selected"}).status_code, 200)
            self.assertEqual((paths.home / "staging/note.txt").read_text(), "selected")
            self.assertEqual(client.post("/api/modules", json={"name": "local.py", "code": "value = 1"}).status_code, 200)
            self.assertTrue((paths.home / "modules/local.py").exists())
            self.assertEqual((other / "untouched.py").read_text(), "other agent")
            self.assertEqual(client.get("/api/status").get_json()["rooms"], {"thinking": "quiet"})
            mind = paths.data / "mindscape"
            mind.mkdir(parents=True)
            (mind / "motor-state.json").write_text('{"status":"selected-agent","jobs":[]}')
            self.assertEqual(client.get("/api/motor").get_json()["status"], "selected-agent")

    def test_cli_provisions_identity_and_keeps_custom_home_on_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            custom_home = root / "custom-home"
            credentials = root / "credentials"
            argv = ["setup.py", "--non-interactive", "--composition", "mindscape", "--composition-only",
                    "--agent-name", "Aura", "--creator-name", "Dev", "--archetype", "builder",
                    "--agent-home", str(custom_home)]
            def without_weights(config):
                return resolve(config, root=root)
            with patch.object(setup, "__file__", str(root / "setup.py")), patch.object(sys, "argv", argv), \
                 patch("core.mindscape_config.activate", side_effect=without_weights), \
                 patch("setup.os.path.expanduser", return_value=str(credentials)), patch("sys.stdout", new=io.StringIO()):
                setup.main()
                note = custom_home / "bedroom/closet/personal.txt"
                note.write_text("keep")
                setup.main()
            manifest = json.loads((root / "data/agents/Aura/creation.json").read_text())
            self.assertEqual(manifest["home"], str(custom_home))
            self.assertEqual(manifest["native_seed"]["agent_name"], "Aura")
            self.assertEqual(note.read_text(), "keep")
            self.assertFalse((root / "data/agents/Aura/mindscape/joint/LATEST.json").exists())
            config = json.loads((root / "config/config.json").read_text())
            self.assertEqual(config["local_provider"], "rwkv")

    def test_existing_home_identity_is_validated_before_cli_can_overwrite_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = {**defaults(root), "agent_name": "Aura", "creator_name": "Dev"}
            first = resolve(creation_settings(config, root=root), root=root)
            provision_creation(first)
            identity = Path(first["mindscape"]["home"]) / "identity.json"
            before = identity.read_bytes()
            with self.assertRaisesRegex(ValueError, "different identity"):
                creation_settings({**config, "agent_name": "Other"}, root=root, home=identity.parent)
            self.assertEqual(identity.read_bytes(), before)
