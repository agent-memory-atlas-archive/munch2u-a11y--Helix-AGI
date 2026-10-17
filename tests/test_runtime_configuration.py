"""Configuration checks without importing a model or the external native package."""
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.mindscape_config import activate_native_source, configured_native_source, defaults, resolve
from core.model_paths import default_native_source, default_rwkv_model, RWKV_CHECKPOINT


class RuntimeConfigurationTests(unittest.TestCase):
    def test_native_task_override_is_rejected_but_legacy_configuration_is_unchanged(self):
        with patch.dict(os.environ, {"HELIX_TASK_COGNITION": "active"}):
            with self.assertRaisesRegex(ValueError, "HELIX_TASK_COGNITION=off"):
                resolve(defaults())
            self.assertIsNone(resolve({"composition": "helix", "task_cognition_mode": "active"}))

    def test_custom_sources_use_one_resolver_without_creating_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "external"
            package.mkdir()
            model = root / RWKV_CHECKPOINT
            model.mkdir()
            with patch.dict(os.environ, {"MIGHTYMEM_PATH": str(package), "RWKV_MODEL_PATH": str(model)}):
                self.assertEqual(default_native_source(root), str(package))
                self.assertEqual(configured_native_source(root), package)
                self.assertEqual(default_rwkv_model(root), str(model))
                self.assertEqual(defaults(root)["mindscape"]["rwkv_model"], str(model))

    def test_selected_source_rejects_poisoned_submodule_before_mutating_import_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ("context_loom/engine.py", "habitus_ai/continual_mind.py"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            previous = list(sys.path)
            with patch.dict(sys.modules, {"habitus_ai.foreign": SimpleNamespace(__file__="/unselected/habitus_ai/foreign.py")}):
                with self.assertRaisesRegex(RuntimeError, "different package"):
                    activate_native_source(root)
            self.assertEqual(sys.path, previous)

    def test_missing_source_is_explicit_and_does_not_fall_back_to_audit_snapshots(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "Native source missing"):
                activate_native_source(directory)


class TestGroupInventoryTests(unittest.TestCase):
    def test_unclassified_modules_fail_and_frozen_snapshots_are_excluded(self):
        import json
        from tests.run_all_tests import classified_groups
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tests").mkdir()
            (root / "tests/test_groups.json").write_text(json.dumps({"groups": {"offline": {"paths": []}}}))
            frozen = root / "documents/audits/frozen/test_evidence.py"
            frozen.parent.mkdir(parents=True)
            frozen.touch()
            classified_groups(root)
            (root / "tests/test_new.py").touch()
            with self.assertRaisesRegex(ValueError, "unclassified=.*test_new"):
                classified_groups(root)
