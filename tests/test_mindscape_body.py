"""Actuator/protocol diagnostics only; no agent competence is inferred."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.mindscape_config import defaults
from core.mindscape_intention import (
    parse_intention,
    requires_workspace_observation,
    extract_workspace_obligations,
    check_obligations_satisfied,
    decode_foreground,
    observation_text,
)

sys.path.insert(0, defaults()["mindscape"]["package_path"])
from core.mindscape_workspace import MindscapeWorkspace
from habitus_ai.store import MindStore


def Metadata():
    return MindStore(":memory:", space_id="actuator-contract-diagnostic", dimension=8)


class NativeActuatorDiagnostics(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.store = Metadata()
        self.addCleanup(self.store.close)
        self.body = MindscapeWorkspace(self.root, self.store)
        (self.root / "room").mkdir()
        (self.root / "room/note.md").write_text("A small diagnostic input, not an agent deliverable.")

    def test_continuation_serializes_through_the_actual_native_metadata_contract(self):
        from core.mindscape import Mindscape
        adapter = Mindscape.__new__(Mindscape)
        adapter.native = SimpleNamespace(mind=SimpleNamespace(store=self.store))
        adapter.continuation = {"pending": {"messages": ["Read the café notes"], "recipient": "Rowan"},
                                "return": {"id": "diagnostic-receipt", "consumed": False}}
        adapter._save_continuation()
        self.assertEqual(json.loads(self.store.get_metadata("helix_pulse_continuation")), adapter.continuation)

    def test_touch_never_opens_file_content_and_move_position_survives_restart(self):
        with patch.object(Path, "read_bytes", side_effect=AssertionError("touch opened content")):
            moved = self.body.move({"path": "room"})
            touched = self.body.sense({"path": "note.md"})
        self.assertTrue(moved["position_verified"])
        self.assertFalse(touched["content_opened"])
        self.assertNotIn("content", touched)
        resumed = MindscapeWorkspace(self.root, self.store)
        self.assertEqual(resumed.position, "room")
        self.assertEqual(resumed.open({"path": "note.md"})["content"], (self.root / "room/note.md").read_text())

    def test_host_root_paths_work_and_escape_cannot_read_or_replace(self):
        self.assertEqual(self.body.open({"path": str(self.root / "room/note.md")})["path"], "room/note.md")
        for action in (self.body.open, self.body.sense):
            with self.assertRaises(PermissionError):
                action({"path": ".."})
        (self.root / "outside").symlink_to(self.root.parent)
        with self.assertRaises(PermissionError):
            self.body.write({"path": "outside/escape.txt", "content": "diagnostic"})

    def test_replacement_requires_observed_current_hash_and_actual_readback(self):
        args = {"path": "room/note.md", "content": "replacement diagnostic"}
        with self.assertRaises(ValueError):
            self.body.write(args)
        original = self.body.open({"path": args["path"]})
        result = self.body.write({**args, "expected_sha256": original["sha256"]})
        self.assertTrue(result["write_verified"])
        self.assertEqual(result["sha256"], hashlib.sha256(args["content"].encode()).hexdigest())
        with self.assertRaises(ValueError):
            self.body.write({**args, "expected_sha256": original["sha256"]})

    def test_pdf_open_reports_extracted_text_and_hash_of_original_bytes(self):
        # Minimal PDF fixture with its actual object offsets, not a task output.
        objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
                   b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
                   b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 100] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
                   b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
        stream = b"BT /F1 12 Tf 10 50 Td (PDF sensor diagnostic) Tj ET"
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        payload = b"%PDF-1.4\n"
        offsets = [0]
        for index, value in enumerate(objects, 1):
            offsets.append(len(payload))
            payload += f"{index} 0 obj\n".encode() + value + b"\nendobj\n"
        xref = len(payload)
        payload += b"xref\n0 6\n0000000000 65535 f \n"
        payload += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
        payload += f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
        (self.root / "input.pdf").write_bytes(payload)
        result = self.body.open({"path": "input.pdf"})
        self.assertIn("PDF sensor diagnostic", result["content"])
        self.assertTrue(result["text_extraction_only"])
        self.assertEqual(result["sha256"], hashlib.sha256(payload).hexdigest())

    def test_malformed_or_narrated_intentions_do_not_execute(self):
        payload = '<intention>{"action":"sense","arguments":{"path":"."}}</intention>'
        self.assertEqual(parse_intention(payload)["action"], "sense")
        self.assertIsNone(parse_intention("I might use " + payload))
        for bad in (payload[:-12], payload.replace("sense", "delete"),
                    payload.replace('"path":"."', '"path":".","extra":"ignored"')):
            with self.assertRaises((ValueError, json.JSONDecodeError)):
                parse_intention(bad)

    def test_required_intention_format_cannot_accept_a_narrated_completion(self):
        from core.mindscape_intention import foreground_schema
        import jsonschema
        narrated = {"message": "I opened a file, and it said imaginary words."}
        jsonschema.validate(narrated, foreground_schema())
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(narrated, foreground_schema(intention_required=True))
        for action in ("move", "sense", "open", "write", "mkdir", "run"):
            arguments = {"path": "diagnostic"}
            if action == "write":
                arguments["content"] = "diagnostic"
            jsonschema.validate({"action": action, "arguments": arguments},
                                foreground_schema(intention_required=True))

    def test_foreground_message_cannot_cross_the_private_intention_channel(self):
        wire = '<intention>{"action":"sense","arguments":{"path":"."}}</intention>'
        text, kind = decode_foreground(json.dumps({"message": wire}))
        self.assertEqual(kind, "message")
        self.assertEqual(text, wire)
        text, kind = decode_foreground('{"action":"sense","arguments":{"path":"."}}')
        self.assertEqual(kind, "intention")
        self.assertEqual(parse_intention(text)["action"], "sense")
        for raw in ('{"message":"claim","action":"sense","arguments":{"path":"."}}',
                    '{"action":"delete","arguments":{"path":"."}}', '{"message":42}'):
            with self.assertRaises(ValueError):
                decode_foreground(raw)

    def test_native_observation_view_keeps_complete_output_and_failure(self):
        receipt = {"receipt_id": "diagnostic-return", "arguments": {"path": "note.md"},
                   "status": "error", "output": {"content": "a large observed body " * 1000},
                   "error": "actual failure", "verified": True}
        result = {"action": "open", "receipt": receipt, "proposal_pulse": "control-telemetry"}
        text = observation_text(result)
        self.assertEqual(json.loads(text.split("\n", 1)[1]), receipt)
        self.assertIn("attempt has finished", text)
        self.assertNotIn("control-telemetry", text)
        self.assertEqual(result["proposal_pulse"], "control-telemetry")

    def test_explicit_action_needs_an_observation_but_capability_questions_do_not(self):
        for text in ('Please open /inbox/a.pdf.', 'Read the file notes.md.',
                     'Mira is talking to me via dashboard. They said: "Please move to /inbox and feel the files."'):
            self.assertTrue(requires_workspace_observation(text))
        for text in ('How can I open a PDF?', 'Can you read files?', 'Write a short greeting.',
                     'I recall someone saying: Please open /inbox/a.pdf.'):
            self.assertFalse(requires_workspace_observation(text))

    def test_workspace_obligations_and_completion_gate(self):
        # 1. Extraction of obligations
        msg_move_sense = 'Mira: Please move to /inbox and feel the files.'
        obl_move_sense = extract_workspace_obligations([msg_move_sense])
        self.assertIn("move", obl_move_sense["required_abilities"])
        self.assertIn("sense", obl_move_sense["required_abilities"])
        self.assertEqual(obl_move_sense["target_paths"], {"/inbox"})

        msg_open = 'Mira: Open Markdown and PDF /inbox/notes.md and extract specified facts.'
        obl_open = extract_workspace_obligations([msg_open])
        self.assertIn("open", obl_open["required_abilities"])

        msg_write_run = 'Mira: Write, read back and run /output/calc.py'
        obl_write_run = extract_workspace_obligations([msg_write_run])
        self.assertIn("write", obl_write_run["required_abilities"])
        self.assertIn("run", obl_write_run["required_abilities"])
        self.assertEqual(obl_write_run["target_paths"], {"/output/calc.py"})

        # The live workshop trial previously instructed /calc.py after
        # splitting a multi-part path. Guidance must retain the full target.
        from core.mindscape_intention import step_guidance_for_pending
        observations = [{"action": "write", "path": "/output/calc.py",
                         "sha256": "observed-hash", "status": "success", "verified": True}]
        guidance = step_guidance_for_pending(obl_write_run, observations)
        self.assertIn("path '/output/calc.py'", guidance)
        self.assertNotIn("path '/calc.py'", guidance)

        # 2. Sensing does not satisfy open or move
        # Case A: Request to move to /inbox and feel files
        # Only sense has run at current position '.' -> move is unsatisfied!
        obs_sense_only = [{"action": "sense", "path": "/inbox", "status": "completed"}]
        self.assertFalse(check_obligations_satisfied(obl_move_sense, obs_sense_only, current_position="."))

        # When move to /inbox executes (position becomes 'inbox') AND sense executed -> satisfied!
        obs_move_and_sense = [
            {"action": "move", "path": "/inbox", "status": "completed"},
            {"action": "sense", "path": "/inbox", "status": "completed"}
        ]
        self.assertTrue(check_obligations_satisfied(obl_move_sense, obs_move_and_sense, current_position="inbox"))

        # Case B: Request to open /inbox/notes.md
        # Sensed directory only -> open is unsatisfied!
        self.assertFalse(check_obligations_satisfied(obl_open, obs_sense_only, current_position="."))

        # When open executes on /inbox/notes.md -> satisfied!
        obs_open_done = [{"action": "open", "path": "/inbox/notes.md", "status": "completed"}]
        self.assertTrue(check_obligations_satisfied(obl_open, obs_open_done, current_position="."))

        # Case C: Request to open an absent file -> observed error settles the target
        obs_open_error = [
            {"action": "open", "path": "/inbox/notes.md", "status": "error", "receipt": {"verified": True}}
        ]
        self.assertTrue(check_obligations_satisfied(obl_open, obs_open_error, current_position="."))


if __name__ == "__main__":
    unittest.main()
