"""Real Flask route contracts, with all writes isolated from agent data."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import dashboard.dashboard as dashboard
from core.runtime_paths import RuntimePaths


class DashboardRouteTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.paths = RuntimePaths(self.root / "selected-data", self.root / "custom-home")
        paths = patch.object(dashboard, "_selected_paths", return_value=self.paths)
        paths.start()
        self.addCleanup(paths.stop)
        comms = patch("dashboard.dashboard_comms.get_comms")
        comms.start()
        self.addCleanup(comms.stop)
        app = dashboard.create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_canvas_round_trip_uses_selected_data(self):
        result = self.client.post("/api/canvas", json={
            "view_type": "markdown", "title": "Report", "content": "# Ready",
        })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(self.client.get("/api/canvas").get_json()["content"], "# Ready")
        self.assertTrue((self.paths.data / "spatial/agent_canvas.json").is_file())

    def test_bad_canvas_is_rejected_without_writing(self):
        for payload in ([], None, {"metadata": []}, {"content": 17},
                        {"timestamp": True}, {"timestamp": float("inf")},
                        {"content": "x" * 1_000_001}):
            with self.subTest(payload_type=type(payload).__name__):
                response = self.client.post("/api/canvas", data=json.dumps(payload),
                                            content_type="application/json")
                self.assertEqual(response.status_code, 400)
        self.assertFalse(self.paths.data.exists())

    def test_add_module_rejects_empty_invalid_and_duplicate_names(self):
        for payload in ({}, [], {"name": "", "code": "pass"},
                        {"name": ".py", "code": "pass"},
                        {"name": 3, "code": "pass"},
                        {"name": "sample", "code": []},
                        {"name": "sample", "code": "def broken("}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/api/modules", json=payload).status_code, 400)
        self.assertFalse(self.paths.home.exists())
        created = self.client.post("/api/modules", json={"name": "sample", "code": "# original\npass\n"})
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.get_json()["name"], "sample.py")
        collision = self.client.post("/api/modules", json={"name": "sample.py", "code": "# replaced\n"})
        self.assertEqual(collision.status_code, 409)
        source = self.client.get("/api/modules/sample.py")
        self.assertEqual(source.get_json()["code"], "# original\npass\n")

    def test_unreadable_module_does_not_inherit_previous_line_count(self):
        modules = self.paths.home / "modules"
        modules.mkdir(parents=True)
        (modules / "a.py").write_text("# line 1\n# line 2\n")
        (modules / "b.py").write_bytes(b"\xff")
        entries = self.client.get("/api/modules").get_json()["modules"]
        self.assertEqual([item["lines"] for item in entries], [2, 0])
