"""Offscreen widget regressions; no model, live service, installer, or real credentials."""
from copy import deepcopy
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt6.QtTest import QTest
from core.mindscape_config import defaults
from wizard.configuration import PROVIDER_LABELS


class WizardRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_default_configuration_agrees_on_native_provider(self):
        from wizard.app import DEFAULT_CONFIG
        self.assertEqual(DEFAULT_CONFIG["llm_provider"], "rwkv")
        self.assertEqual(DEFAULT_CONFIG["local_provider"], "rwkv")
        self.assertEqual(DEFAULT_CONFIG["task_cognition_mode"], "off")

    def test_models_tab_keeps_rwkv_despite_stale_credentials_and_saves_same_choice(self):
        from wizard.models_tab import ModelsTab
        config = defaults()
        config.update(llm_model="/chosen/model", local_model="/chosen/model", telegram_token="keep-me")
        context = SimpleNamespace(config=config, _write_credentials=Mock())
        with patch("wizard.models_tab._load_existing_creds", return_value={"HELIX_PROVIDER": "gemini"}):
            tab = ModelsTab(context)
        self.addCleanup(tab.deleteLater)
        self.assertEqual(tab.provider_combo.currentText(), "rwkv")
        self.assertEqual(tab.model_combo.currentText(), "/chosen/model")
        self.assertEqual(tab.provider_combo.findText("gemini"), -1)
        with patch("wizard.app.save_config"), patch("wizard.models_tab.QMessageBox.information"):
            tab._save_settings()
        saved = context._write_credentials.call_args.kwargs["config"]
        self.assertEqual(saved["llm_provider"], "rwkv")
        self.assertEqual(saved["mindscape"]["rwkv_model"], "/chosen/model")
        self.assertEqual(saved["telegram_token"], "keep-me")

    def test_unsupported_saved_provider_is_visible_and_cannot_be_saved_silently(self):
        from wizard.models_tab import ModelsTab
        context = SimpleNamespace(config={"composition":"helix","llm_provider":"openai"}, _write_credentials=Mock())
        before = deepcopy(context.config)
        with patch("wizard.models_tab._load_existing_creds", return_value={}):
            tab = ModelsTab(context)
        self.addCleanup(tab.deleteLater)
        self.assertEqual(tab.provider_combo.currentText(), "openai")
        with patch("wizard.models_tab.QMessageBox.warning") as warning:
            tab._save_settings()
        warning.assert_called_once()
        context._write_credentials.assert_not_called()
        self.assertEqual(context.config, before)

    def test_credentials_page_can_select_legacy_composition_instead_of_a_dead_provider_path(self):
        from wizard.pages.credentials import CredentialsPage
        context = SimpleNamespace(config=defaults(), next_page=Mock(), prev_page=Mock())
        with patch("wizard.pages.credentials._load_existing_creds", return_value={}):
            page = CredentialsPage(context)
        self.addCleanup(page.deleteLater)
        self.assertEqual(page._get_provider(), "rwkv")
        page.composition_combo.setCurrentIndex(page.composition_combo.findData("helix"))
        page.provider_combo.setCurrentText(PROVIDER_LABELS["gemini"])
        page.gemini_key.setText("diagnostic-only")
        with patch("wizard.pages.credentials.QMessageBox.warning") as warning:
            page._save_and_next()
        warning.assert_not_called()
        self.assertEqual(context.config["composition"], "helix")
        self.assertEqual(context.config["llm_provider"], "gemini")
        context.next_page.assert_called_once()

    def test_install_failure_keeps_timer_owned_and_never_bootstraps(self):
        from wizard.app import HelixApp
        window = QMainWindow()
        self.addCleanup(window.deleteLater)
        window.config = defaults()
        window._finish_after_install = Mock()
        process = Mock(stdout=iter(["install failed"]), returncode=1)
        with patch("wizard.app.subprocess.Popen", return_value=process):
            HelixApp._install_dependencies(window)
            QTest.qWait(500)
        self.assertFalse(window._install_timer.isActive())
        window._finish_after_install.assert_not_called()
        for dialog in window.findChildren(QDialog):
            dialog.close()
