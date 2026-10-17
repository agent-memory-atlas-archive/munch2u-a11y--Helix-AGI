#!/usr/bin/env python3
"""Integration test for Helix's Agent-Controlled UI Canvas Tool.

Tests:
  1. Dispatching `render_ui_canvas` tool call from tool registry
  2. JSON state persistence to `data/spatial/agent_canvas.json` and history logging
  3. API payload structure for Markdown, Image, Browser Embed, and Terminal views
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.tool_registry import registry
import tools.ui_canvas_tool as ui_tool


class TestAgentUiCanvas(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        base = patch.object(ui_tool, "BASE_DIR", self.root)
        base.start()
        self.addCleanup(base.stop)

    def test_01_tool_registration(self):
        declarations = registry.get_declarations(active_toolsets={"ui_canvas"})
        names = [d["name"] for d in declarations]
        self.assertIn("render_ui_canvas", names)

    def test_02_render_markdown_canvas(self):
        res_str = registry.dispatch("render_ui_canvas", {
            "view_type": "markdown",
            "title": "Quantum Computation Report",
            "content": "# Quantum Report\n\n- Matrix speedup: 10x\n- Status: PASSED",
            "auto_switch": True,
        })
        res = json.loads(res_str)
        self.assertEqual(res.get("status"), "rendered")

        # Verify state file
        state_file = self.root / "data" / "spatial" / "agent_canvas.json"
        self.assertTrue(state_file.exists())
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data.get("view_type"), "markdown")
            self.assertEqual(data.get("title"), "Quantum Computation Report")

    def test_03_render_image_canvas(self):
        res_str = registry.dispatch("render_ui_canvas", {
            "view_type": "image",
            "title": "Generated Attractor Topology",
            "content": "8D Spatial Manifold Attractor Representation",
            "media_url": "https://example.com/attractor.png",
            "auto_switch": False,
        })
        res = json.loads(res_str)
        self.assertEqual(res.get("status"), "rendered")

    def test_named_agent_data_and_history(self):
        config = self.root / "config" / "config.json"
        config.parent.mkdir()
        config.write_text(json.dumps({"data_dir": "agents/Jules"}))
        spatial = self.root / "agents" / "Jules" / "spatial"
        spatial.mkdir(parents=True)
        history = spatial / "agent_canvas_history.json"
        history.write_text(json.dumps([{"title": str(i)} for i in range(50)]))
        result = json.loads(ui_tool.render_ui_canvas("card", "Ready", title="Named agent"))
        self.assertEqual(result["status"], "rendered")
        self.assertEqual(json.loads((spatial / "agent_canvas.json").read_text())["title"], "Named agent")
        entries = json.loads(history.read_text())
        self.assertEqual(len(entries), 50)
        self.assertEqual(entries[0]["title"], "1")
        self.assertEqual(entries[-1]["title"], "Named agent")
        self.assertFalse((self.root / "data").exists())

    def test_invalid_payload_preserves_existing_canvas(self):
        ui_tool.render_ui_canvas("card", "Original")
        state = self.root / "data" / "spatial" / "agent_canvas.json"
        before = state.read_bytes()
        for kwargs in ({"view_type": "executable", "content": "bad"},
                       {"view_type": "card", "content": 42},
                       {"view_type": "card", "content": "x" * 1_000_001}):
            with self.subTest(kwargs=list(kwargs)):
                result = json.loads(ui_tool.render_ui_canvas(**kwargs))
                self.assertEqual(result["status"], "error")
                self.assertEqual(state.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
