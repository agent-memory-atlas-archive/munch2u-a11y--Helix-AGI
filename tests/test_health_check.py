"""Tests for the read-only local installation health check."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.run_health_check import Check, collect_checks, exit_code, check_health
from contextlib import redirect_stdout
import io
import json


class HealthCheckTests(unittest.TestCase):
    def test_exit_code_only_fails_on_required_failure(self):
        self.assertEqual(exit_code([Check("optional", "WARN", "missing")]), 0)
        self.assertEqual(exit_code([Check("required", "FAIL", "missing")]), 1)

    def test_apache_license_and_ui_files_are_detected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for relative in (
                "dashboard/dashboard.py",
                "dashboard/dashboard_ui.html",
                "desktop_widget/web/index.html",
                "desktop_widget/web/mascot.js",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("present", encoding="utf-8")
            (root / "LICENSE").write_text("Apache License\nVersion 2.0", encoding="utf-8")

            checks = {check.component: check for check in collect_checks(root)}
            self.assertEqual(checks["Repository license"].status, "PASS")
            self.assertEqual(checks["User interfaces"].status, "PASS")

    def test_failed_preflight_returns_failure_without_readiness_claim(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()) as output:
            status = check_health(Path(directory))
            self.assertEqual(status, 1)
            self.assertNotIn("READY TO LAUNCH", output.getvalue())
            self.assertIn("Preflight failed", output.getvalue())

    def test_invalid_configuration_is_failure_and_does_not_create_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config").mkdir()
            config = root / "config/config.json"
            config.write_text("[]")
            before = sorted(root.rglob("*"))
            checks = collect_checks(root)
            self.assertEqual(next(c.status for c in checks if c.component == "Configuration"), "FAIL")
            self.assertEqual(sorted(root.rglob("*")), before)

    def test_json_output_has_machine_readable_failure_status(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()) as output:
            status = check_health(Path(directory), json_output=True)
            self.assertEqual(json.loads(output.getvalue())["exit_code"], status)
            self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
