"""Installation profiles retain the existing full stack and a lighter UI entry."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def requirements(path):
    result = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("-r "):
            result |= requirements(path.parent / line[3:])
        elif line and not line.startswith("#"):
            result.add(line)
    return result


class DependencyProfileTests(unittest.TestCase):
    def test_full_profile_preserves_existing_requirements(self):
        previous = set(["google-genai>=1.0.0","anthropic>=0.90.0","openai>=1.0.0","chromadb>=0.4.0","sentence-transformers>=2.2.0","numpy>=1.24.0","scipy>=1.10.0","umap-learn>=0.5.0","hdbscan>=0.8.0","faiss-cpu>=1.8.0","spacy>=3.7.0","tiktoken>=0.5.0","python-telegram-bot>=21.0","google-api-python-client>=2.0.0","google-auth-httplib2>=0.1.0","google-auth-oauthlib>=1.0.0","duckduckgo-search>=8.0.0","beautifulsoup4>=4.12.0","playwright>=1.40.0","llama-cpp-python>=0.2.0","ollama>=0.1.0","faster-whisper>=1.0.0","piper-tts>=1.2.0","sounddevice>=0.4.0","opencv-python>=4.8.0","python-dotenv>=1.0.0","pyyaml>=6.0","psutil>=5.9.0","requests>=2.31.0","flask>=3.0.0","PyQt6>=6.6.0","PyQt6-WebEngine>=6.6.0"])
        self.assertTrue(previous <= requirements(ROOT / "requirements.txt"))

    def test_wizard_does_not_install_native_cloud_audio_or_browser_backends(self):
        ui = requirements(ROOT / "requirements-wizard.txt")
        self.assertIn("PyQt6>=6.6.0", ui)
        for prefix in ("torch", "transformers", "llama-cpp", "google-genai", "faster-whisper", "playwright"):
            self.assertFalse(any(line.startswith(prefix) for line in ui), prefix)
        self.assertIn("transformers==5.17.0", requirements(ROOT / "requirements-mindscape.txt"))

    def test_headless_launch_forwards_cli_arguments_and_failure_without_importing_qt(self):
        from wizard import __main__ as launcher
        with patch.object(launcher, "graphical_session_available", return_value=False), \
             patch.object(sys, "argv", ["wizard", "--wizard", "--non-interactive"]), \
             patch.object(launcher.subprocess, "run", return_value=SimpleNamespace(returncode=7)) as run:
            self.assertEqual(launcher.main(), 7)
        self.assertIn("--non-interactive", run.call_args.args[0])
        self.assertNotIn("--wizard", run.call_args.args[0])

    def test_installer_retains_valid_shell_syntax(self):
        subprocess.run(["bash", "-n", str(ROOT / "install.sh")], check=True)
