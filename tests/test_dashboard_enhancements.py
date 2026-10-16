import json
import unittest
from pathlib import Path
from dashboard.dashboard import create_app, DATA_DIR

class TestDashboardEnhancements(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_status_includes_agent_position(self):
        """Status endpoint should include the agent spatial room / position."""
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("room", data)
        self.assertIn("room_entries", data)

    def test_staging_file_api(self):
        """Dashboard should allow staging a temporary file safely into agent home."""
        # 1. Post a file to stage
        payload = {
            "filename": "test_note.txt",
            "content": "Hello Helix, this is a staged observation."
        }
        res = self.client.post("/api/stage_file", json=payload)
        self.assertEqual(res.status_code, 200)
        ret = res.get_json()
        self.assertTrue(ret.get("ok"))

        # 2. Verify file appears in list of staged files
        res_list = self.client.get("/api/staged_files")
        self.assertEqual(res_list.status_code, 200)
        staged = res_list.get_json().get("staged", [])
        filenames = [f["name"] for f in staged]
        self.assertIn("test_note.txt", filenames)

    def test_modules_api(self):
        """Dashboard should list agent modules and allow safe syntax-checked additions."""
        res = self.client.get("/api/modules")
        self.assertEqual(res.status_code, 200)
        mods = res.get_json().get("modules", [])
        self.assertIsInstance(mods, list)

        # Attempt adding invalid syntax module (should fail safely)
        invalid_payload = {
            "name": "bad_tool.py",
            "code": "def broken(:"
        }
        res_bad = self.client.post("/api/modules", json=invalid_payload)
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn("error", res_bad.get_json())

if __name__ == "__main__":
    unittest.main()
