"""Launch the GUI when available; keep the headless CLI independent of Qt."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys


def graphical_session_available():
    return (not sys.platform.startswith("linux")
            or bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
            or os.environ.get("QT_QPA_PLATFORM") in {"offscreen", "minimal"})


def main():
    if not graphical_session_available() or importlib.util.find_spec("PyQt6") is None:
        command = [sys.executable, str(Path(__file__).resolve().parents[1] / "setup.py")]
        command.extend(arg for arg in sys.argv[1:] if arg != "--wizard")
        return subprocess.run(command, check=False).returncode
    from wizard.app import main as gui_main
    return gui_main()


if __name__ == "__main__":
    raise SystemExit(main())
