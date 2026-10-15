"""Home, focus lifecycle and containment diagnostics; not agent competence."""
import hashlib
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.agent_home import prepare_home
from core.mindscape_config import defaults, resolve
from core.mindscape_intention import decode_foreground, foreground_schema
from core.context_focus import ContextFocus, resolve_profiles

sys.path.insert(0, defaults()["mindscape"]["package_path"])
from core.mindscape_workspace import MindscapeWorkspace
from habitus_ai.store import MindStore


class HomeDiagnostics(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.config = defaults()
        self.config["mindscape"]["home"] = str(self.parent / "home")
        self.home = prepare_home(resolve(self.config))
        self.root = Path(self.home["root"])
        self.store = MindStore(":memory:", space_id="home-contract-diagnostic", dimension=8)
        self.addCleanup(self.store.close)
        self.body = MindscapeWorkspace(self.root, self.store, home=self.home)

    def test_setup_is_idempotent_and_keeps_thinking_empty_and_personal_files(self):
        personal = self.root / "bedroom/closet/note.txt"
        personal.write_text("keep this")
        self.assertEqual(prepare_home(resolve(self.config)), self.home)
        self.assertEqual(list((self.root / "thinking").iterdir()), [])
        self.assertEqual(personal.read_text(), "keep this")
        self.assertFalse(self.home["modules_require_room"])
        self.assertEqual(self.body.position, "thinking")

    def test_source_and_mind_state_cannot_be_workshop_ancestors(self):
        for root in (Path(__file__).resolve().parents[1], Path(self.config["mindscape"]["rwkv_model"]), self.parent):
            self.config["mindscape"]["home"] = str(root)
            with self.assertRaises(ValueError):
                prepare_home(resolve(self.config), state_directory=self.parent / "mindscape")

    def test_room_and_descriptor_symlinks_do_not_redirect_setup(self):
        (self.root / "workshop").rmdir()
        (self.root / "workshop").symlink_to(self.parent)
        with self.assertRaises(PermissionError):
            prepare_home(resolve(self.config))
        (self.root / "workshop").unlink()
        (self.root / "workshop").mkdir()
        (self.root / "home.json").unlink()
        outside = self.parent / "protected.json"
        outside.write_text("unchanged")
        (self.root / "home.json").symlink_to(outside)
        with self.assertRaises(PermissionError):
            prepare_home(resolve(self.config))
        self.assertEqual(outside.read_text(), "unchanged")

    def test_intake_is_fresh_and_readback_matches_observation_without_opening_files(self):
        (self.root / "thinking/object.txt").write_text("not sensed content")
        first, payload = self.body.observe_environment(1)
        second, _ = self.body.observe_environment(2)
        self.assertNotEqual(first["observation_id"], second["observation_id"])
        self.assertNotIn("not sensed content", payload)
        stored = list((self.root / "intakes").glob("*.json"))
        self.assertEqual(len(stored), 2)
        self.assertIn(first, [json.loads(path.read_text()) for path in stored])

    def test_remembered_module_reaches_directly_and_consumption_releases_focus(self):
        result = subprocess.CompletedProcess([], 0, '{"content":"complete result"}', "")
        with patch.object(self.body, "_isolated", return_value=result):
            returned = self.body.activate({"module": "web_search", "parameters": {"query": "diagnostic"}})
        self.assertEqual(self.body.position, "thinking")
        self.assertFalse(returned["process_active"])
        active = self.body.active_module()
        self.store.set_metadata("helix_home_module", json.dumps({**active, "receipt_id": "receipt-A"}))
        self.assertIsNone(self.body.consume_module("other receipt"))
        self.assertEqual(self.body.consume_module("receipt-A")["disengaged"], "web_search")
        self.assertFalse(self.body.active_module())

    def test_failure_movement_and_restart_leave_no_active_module(self):
        with patch.object(self.body, "_isolated", side_effect=RuntimeError("namespace unavailable")):
            with self.assertRaises(RuntimeError):
                self.body.activate({"module": "terminal", "parameters": {"command": "true"}})
        self.assertFalse(self.body.active_module())
        self.store.set_metadata("helix_home_module", '{"module":"terminal"}')
        self.body.move({"path": "/bedroom"})
        self.assertFalse(self.body.active_module())
        self.store.set_metadata("helix_home_module", '{"module":"terminal"}')
        resumed = MindscapeWorkspace(self.root, self.store, home=self.home)
        self.assertEqual(resumed.position, "bedroom")
        self.assertFalse(resumed.active_module())

    def test_module_focus_boosts_interface_and_reduces_surroundings_priority(self):
        profiles = resolve_profiles()
        active = ContextFocus({"module": 1}, "diagnostic")
        resting = ContextFocus({"environment": 1}, "diagnostic")
        self.assertGreater(active.priority("module", profiles), resting.priority("module", profiles))
        self.assertLess(active.priority("environment", profiles), resting.priority("environment", profiles))

    def test_protected_modules_intakes_and_room_escape_are_rejected(self):
        with self.assertRaisesRegex(PermissionError, "Host Python execution is disabled"):
            self.body.run_python("/workshop/arbitrary.py")
        for path in ("/modules/web_read.py", "/home.json", "/intakes/forged.json", "/bedroom/sleep.json"):
            with self.assertRaises(PermissionError):
                self.body.write({"path": path, "content": "replacement"})
        (self.root / "workshop/escape").symlink_to(self.parent)
        with self.assertRaises(PermissionError):
            self.body.write({"path": "/workshop/escape/outside.txt", "content": "outside"})

    def test_sleep_uses_attached_engine_and_errors_are_not_completed_cycles(self):
        with self.assertRaisesRegex(RuntimeError, "not attached"):
            self.body.activate({"module": "sleep", "parameters": {}})
        engine = SimpleNamespace(run_dream_cycle=lambda: {"errors": 0, "extracted": 0})
        self.body.dream_engine = engine
        self.assertTrue(self.body.activate({"module": "sleep", "parameters": {}})["complete"])
        engine.run_dream_cycle = lambda: {"status": "error", "reason": "no store"}
        with self.assertRaisesRegex(RuntimeError, "Dream cycle failed"):
            self.body.activate({"module": "sleep", "parameters": {}})
        self.assertFalse(self.body.active_module())

    def test_activation_schema_and_parser_accept_only_the_explicit_wire_format(self):
        for raw in ('{"action":"activate","arguments":{"module":"terminal","parameters":{"command":"true"}}}',
                    '{"action":"disengage","arguments":{}}'):
            self.assertEqual(decode_foreground(raw)[1], "intention")
        with self.assertRaises(ValueError):
            decode_foreground('{"action":"activate","arguments":{"module":"terminal","parameters":{"command":42}}}')
        self.assertIn("activate", [variant["properties"]["action"]["const"] for variant in foreground_schema(intention_required=True)["oneOf"]])

    def test_namespace_command_only_binds_workshop_writable_and_has_no_limits(self):
        with patch("core.mindscape_workspace.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            self.body._isolated([sys.executable, "-I", "/workspace/experiment.py"])
        command = run.call_args.args[0]
        bind = command.index("--bind")
        self.assertEqual(command[bind + 1:bind + 3], [str(self.root / "workshop"), "/workspace"])
        self.assertNotIn("--share-net", command)
        self.assertNotIn("timeout", run.call_args.kwargs)
        with patch("core.mindscape_workspace.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            self.body._isolated([sys.executable, "/modules/web_read.py"], network=True, module_scripts=True)
        self.assertNotIn("--bind", run.call_args.args[0])
        self.assertIn("--share-net", run.call_args.args[0])

    def test_actual_workshop_namespace_blocks_external_write_and_network(self):
        script = self.root / "workshop/containment.py"
        sentinel = self.parent / "external.txt"
        sentinel.write_text("unchanged")
        source = Path(__file__).resolve().parents[1]
        script.write_text(f"""from pathlib import Path
import socket
Path('/workspace/artifact.txt').write_text('inside')
assert not Path('/modules').exists()
assert not Path({str(source / 'core')!r}).exists()
assert not Path({str(self.root / 'bedroom')!r}).exists()
assert not Path('/workspace/../bedroom').exists()
try:
    Path({str(sentinel)!r}).write_text('escaped')
except OSError:
    pass
else:
    raise AssertionError('external file write escaped')
try:
    socket.create_connection(('1.1.1.1', 443))
except OSError:
    pass
else:
    raise AssertionError('network escaped')
print('contained')
""")
        observed = self.body.open({"path": "/workshop/containment.py"})
        try:
            returned = self.body.run({"path": "/workshop/containment.py", "expected_sha256": observed["sha256"]})
        except RuntimeError as error:
            if "Operation not permitted" in str(error) or "No permissions to create" in str(error):
                self.skipTest("Host namespace policy blocks bubblewrap: " + str(error))
            raise
        self.assertIn("contained", returned["stdout"])
        self.assertEqual((self.root / "workshop/artifact.txt").read_text(), "inside")
        self.assertEqual(sentinel.read_text(), "unchanged")

    def test_actual_terminal_runs_directly_and_writes_only_workshop_artifact(self):
        try:
            returned = self.body.activate({"module": "terminal", "parameters": {
                "command": "printf 'terminal artifact' > terminal.txt; cat terminal.txt"}})
        except RuntimeError as error:
            if "Operation not permitted" in str(error) or "No permissions to create" in str(error):
                self.skipTest("Host namespace policy blocks bubblewrap: " + str(error))
            raise
        self.assertEqual(returned["output"]["stdout"], "terminal artifact")
        self.assertEqual((self.root / "workshop/terminal.txt").read_text(), "terminal artifact")
        self.assertEqual(self.body.position, "thinking")
        self.assertFalse(returned["process_active"])

    def test_actual_reader_returns_full_controlled_page_and_links_with_declared_network(self):
        # A component fixture, not a search result or product evaluation.
        body = b"<html><body>" + b"complete page content " * 600 + b'<a href="/next">next</a></body></html>'
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, *args):
                pass
        try:
            server = HTTPServer(("127.0.0.1", 0), Handler)
        except PermissionError as error:
            self.skipTest("Session policy blocks component HTTP fixture: " + str(error))
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/page"
            returned = self.body.activate({"module": "web_read", "parameters": {"url": url}})
            output = returned["output"]
            self.assertEqual(output["content"].count("complete page content"), 600)
            self.assertEqual(output["sha256"], hashlib.sha256(body).hexdigest())
            self.assertEqual(output["links"], [f"http://127.0.0.1:{server.server_port}/next"])
            self.assertTrue(output["complete"])
            self.assertTrue(returned["network"])
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


if __name__ == "__main__":
    unittest.main()
