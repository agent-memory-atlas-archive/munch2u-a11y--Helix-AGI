import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_native_dependency import verify_source


class NativeDependencyManifestTests(unittest.TestCase):
    def test_hashes_cover_dirty_source_and_report_missing_and_changed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (source / "module.py").write_bytes(b"recorded bytes")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"native_source": {"files": {
                "module.py": hashlib.sha256(b"recorded bytes").hexdigest()}}}))
            self.assertTrue(verify_source(source, manifest)["matches_recorded_source"])
            (source / "module.py").write_bytes(b"new bytes")
            self.assertFalse(verify_source(source, manifest)["matches_recorded_source"])
            (source / "module.py").unlink()
            self.assertIsNone(verify_source(source, manifest)["mismatches"][0]["actual"])
            self.assertEqual(list(source.iterdir()), [])

    def test_manifest_cannot_read_outside_selected_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"native_source": {"files": {"../outside.py": "hash"}}}))
            with self.assertRaisesRegex(ValueError, "Invalid manifest source path"):
                verify_source(root / "source", manifest)
