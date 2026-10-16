"""TDD test suite for 3-way setup configuration (Hosted API, Local Ollama, Full RWKV)."""
import os
import unittest
import json
import subprocess
from pathlib import Path

from llm.providers.base import detect_available_provider, ProviderConfig
from core.mindscape_config import resolve as resolve_mindscape_config

RWKV_MODEL_PATH = os.environ.get("RWKV_MODEL_PATH", str(Path.home() / "habitus-ai-experiments" / "habitus-mind" / "models" / "rwkv7-g1j-1.5b-20260831-2c18b29"))


class TestThreeWaySetup(unittest.TestCase):
    def setUp(self):
        self._orig_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._orig_env)

    def test_detect_available_provider_supports_rwkv(self):
        """detect_available_provider must recognize HELIX_PROVIDER=rwkv."""
        os.environ["HELIX_PROVIDER"] = "rwkv"
        os.environ["HELIX_MODEL"] = RWKV_MODEL_PATH
        config = detect_available_provider()
        self.assertIsNotNone(config)
        self.assertEqual(config.provider_type, "rwkv")
        self.assertEqual(config.model, RWKV_MODEL_PATH)

    def test_detect_available_provider_supports_bicameral_rwkv(self):
        """detect_available_provider must recognize HELIX_PROVIDER=bicameral_rwkv."""
        os.environ["HELIX_PROVIDER"] = "bicameral_rwkv"
        os.environ["HELIX_MODEL"] = RWKV_MODEL_PATH
        config = detect_available_provider()
        self.assertIsNotNone(config)
        self.assertEqual(config.provider_type, "rwkv")

    def test_resolve_mindscape_full_rwkv_config(self):
        """resolve() must properly validate and populate a full RWKV setup."""
        raw = {
            "composition": "mindscape",
            "pulse_mode": "standard",
            "local_provider": "rwkv",
            "llm_provider": "rwkv",
            "local_model": RWKV_MODEL_PATH,
            "llm_model": RWKV_MODEL_PATH,
            "local_context_window": 8192,
            "mindscape": {
                "rwkv_model": RWKV_MODEL_PATH,
                "action_intent_source": "bicameral_rwkv",
            },
        }
        resolved = resolve_mindscape_config(raw)
        self.assertEqual(resolved["local_provider"], "rwkv")
        self.assertEqual(resolved["llm_provider"], "rwkv")
        self.assertEqual(resolved["mindscape"]["action_intent_source"], "bicameral_rwkv")

    def test_main_resolve_provider_supports_all_three_modes(self):
        """main.py resolve_main_provider function must dynamically return the right ProviderConfig for all 3 modes."""
        from main import resolve_main_provider

        # Mode 1: Full RWKV Experimental
        rwkv_settings = {
            "local_provider": "rwkv",
            "local_model": RWKV_MODEL_PATH,
            "local_context_window": 8192,
            "mindscape": {"rwkv_model": RWKV_MODEL_PATH},
        }
        cfg_rwkv = {"ollama_url": "http://localhost:11434"}
        p1 = resolve_main_provider(rwkv_settings, cfg_rwkv)
        self.assertEqual(p1.provider_type, "rwkv")
        self.assertEqual(p1.model, RWKV_MODEL_PATH)

        # Mode 2: Local Ollama
        ollama_settings = {
            "local_provider": "ollama",
            "local_model": "granite4.1:8b",
            "local_context_window": 32768,
            "mindscape": {"rwkv_model": RWKV_MODEL_PATH},
        }
        p2 = resolve_main_provider(ollama_settings, cfg_rwkv)
        self.assertEqual(p2.provider_type, "ollama")
        self.assertEqual(p2.model, "granite4.1:8b")

        # Mode 3: Hosted API (when no mindscape settings or API provider configured)
        os.environ["HELIX_PROVIDER"] = "gemini"
        os.environ["GEMINI_API_KEY"] = "fake-test-key-12345"
        p3 = resolve_main_provider(None, {"pulse_mode": "standard"})
        self.assertEqual(p3.provider_type, "gemini")

    def test_setup_py_cli_composition_rwkv(self):
        """setup.py --composition mindscape --provider rwkv must configure rwkv local_provider."""
        config_path = Path(str(Path.home() / "Helix_Live_Test/config/config.json"))
        backup = config_path.read_text()
        try:
            cmd = [
                str(Path.home() / "Helix_Live_Test/venv/bin/python"),
                str(Path.home() / "Helix_Live_Test/setup.py"),
                "--composition", "mindscape",
                "--composition-only",
                "--provider", "rwkv",
                "--rwkv-model", RWKV_MODEL_PATH,
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"setup.py failed: {res.stderr}")
            cfg = json.loads(config_path.read_text())
            self.assertEqual(cfg.get("local_provider"), "rwkv")
            self.assertEqual(cfg.get("mindscape", {}).get("action_intent_source"), "bicameral_rwkv")
        finally:
            config_path.write_text(backup)


if __name__ == "__main__":
    unittest.main()
