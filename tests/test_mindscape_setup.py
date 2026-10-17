"""Implementation diagnostics; no model behavior or product score is asserted."""
import json
from pathlib import Path
import tempfile
import unittest

from core.mindscape import projection
from core.mindscape_config import defaults, resolve, activate, write_json


class CompositionContractTests(unittest.TestCase):
    def test_legacy_config_is_explicitly_separate(self):
        self.assertIsNone(resolve({"local_provider": "ollama"}))

    def test_typo_cannot_silently_launch_a_smaller_system(self):
        with self.assertRaisesRegex(ValueError, "Unknown composition"):
            resolve({"composition": "mindscpae"})

    def test_full_defaults_select_all_local_sources(self):
        config = resolve(defaults())
        self.assertEqual(config["composition"], "mindscape")
        self.assertEqual(config["local_provider"], "rwkv")
        self.assertTrue(Path(config["mindscape"]["rwkv_model"]).is_absolute())

    def test_dual_mode_cannot_silently_replace_full_composition(self):
        with self.assertRaisesRegex(ValueError, "standard Helix"):
            resolve({**defaults(), "pulse_mode": "dual"})

    def test_remote_provider_cannot_replace_local_foreground(self):
        with self.assertRaisesRegex(ValueError, "local Ollama"):
            resolve({**defaults(), "local_provider": "gemini"})

    def test_wizard_foreground_cannot_disagree_with_composition(self):
        with self.assertRaisesRegex(ValueError, "Mindscape uses Ollama"):
            resolve({**defaults(), "llm_provider": "gemini"})

    def test_missing_package_fails_before_neural_initialization(self):
        config = defaults()
        with tempfile.TemporaryDirectory() as directory:
            config["mindscape"]["package_path"] = directory
            with self.assertRaisesRegex(RuntimeError, "missing"):
                activate(config)

    def test_checkpoint_policy_is_validated(self):
        config = defaults()
        config["mindscape"]["gestation"] = "ignore-corruption"
        with self.assertRaisesRegex(ValueError, "gestation"):
            resolve(config)

    def test_private_thought_does_not_become_a_fact(self):
        item = projection({"id": "mem_1", "content": "I opened the file successfully.", "memory_type": "thought"})
        self.assertEqual(item["evidence_status"], "private")
        self.assertEqual(item["kind"], "thought")

    def test_success_label_does_not_verify_historical_action(self):
        item = projection({"id": "mem_1", "content": "success", "record_kind": "tool_result", "status": "verified"})
        self.assertEqual(item["evidence_status"], "unverified")

    def test_source_identity_and_versions_survive_projection(self):
        first = projection({"id": "belief-1", "content": "Banner is red"})
        repeat = projection({"id": "belief-1", "content": "Banner is red"})
        corrected = projection({"id": "belief-1", "content": "Banner is blue"})
        self.assertEqual(first["id"], repeat["id"])
        self.assertNotEqual(first["id"], corrected["id"])
        self.assertEqual(first["source_id"], corrected["source_id"])

    def test_human_input_keeps_reported_status(self):
        item = projection({"id": "mem_2", "content": "Banner is amber",
                           "record_envelope": {"record_kind": "inbound_message"}})
        self.assertEqual(item["evidence_status"], "user_reported")

    def test_atomic_receipt_rejects_nonfinite_state(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "receipt.json"
            write_json(target, {"status": "valid"})
            with self.assertRaises(ValueError):
                write_json(target, {"state": float("nan")})
            self.assertEqual(json.loads(target.read_text()), {"status": "valid"})


if __name__ == "__main__":
    unittest.main()
