"""TDD Test Suite asserting Dual RWKV is the main default and foremost documented system."""
import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

class TestDualRWKVDefaults(unittest.TestCase):
    def test_mindscape_config_defaults_to_dual_rwkv(self):
        """core.mindscape_config.defaults() must specify rwkv as primary local provider and bicameral_rwkv action intent."""
        from core.mindscape_config import defaults
        d = defaults(REPO_ROOT)
        self.assertEqual(
            d.get("local_provider"),
            "rwkv",
            "Expected mindscape local_provider to default to 'rwkv'"
        )
        self.assertIn(
            d.get("llm_provider"),
            {"rwkv", "bicameral_rwkv"},
            "Expected mindscape llm_provider to default to 'rwkv' or 'bicameral_rwkv'"
        )
        self.assertIn(
            d["mindscape"].get("action_intent_source"),
            {"bicameral_rwkv", "rwkv_bicameral"},
            "Expected action_intent_source to default to 'bicameral_rwkv'"
        )

    def test_setup_py_defaults_to_dual_rwkv(self):
        """setup.py must present and default to Full Dual RWKV as Option 1 and default local_mode_config provider."""
        setup_text = (REPO_ROOT / "setup.py").read_text(encoding="utf-8")
        # Assert Mode 1 is Full Dual RWKV
        self.assertRegex(
            setup_text,
            r"1\.\s+(?:Full\s+)?Dual\s+RWKV",
            "setup.py must list Full Dual RWKV as option 1 in mode selection"
        )
        # Assert default prompt is [1]
        self.assertIn(
            'Mode (1/2/3/4) [1]',
            setup_text,
            "setup.py must default interactive mode prompt to [1]"
        )

        from setup import local_mode_config
        cfg = local_mode_config()
        self.assertEqual(
            cfg.get("provider"),
            "rwkv",
            "local_mode_config() default provider must be 'rwkv'"
        )

    def test_readme_references_dual_rwkv_foremost(self):
        """README.md must showcase the Dual RWKV (Bicameral RWKV-7) architecture at the top."""
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        top_1000 = readme[:1500]
        self.assertTrue(
            "Dual RWKV" in top_1000 or "Bicameral RWKV" in top_1000,
            "README.md top section must prominently feature Dual RWKV / Bicameral RWKV"
        )
        # TL;DR section must feature Dual RWKV as the primary local architecture
        tldr_pos = readme.find("TL;DR")
        self.assertNotEqual(tldr_pos, -1, "README.md must contain a TL;DR section")
        tldr_chunk = readme[tldr_pos:tldr_pos + 1200]
        self.assertTrue(
            "Dual RWKV" in tldr_chunk or "Bicameral RWKV" in tldr_chunk,
            "README.md TL;DR section must specify Dual RWKV / Bicameral RWKV foremost"
        )


if __name__ == "__main__":
    unittest.main()
