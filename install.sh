#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#   Helix‑AGI — Setup Wizard Launcher
#
#   Checks for Python dependencies and launches the setup wizard.
#   Run this from the repository root:
#     chmod +x install.sh && ./install.sh
# ──────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════╗"
echo "║       HELIX‑AGI SETUP WIZARD             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Check Python ──────────────────────────────────────────────
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        if "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' 2>/dev/null; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python 3.11+ is required but not found."
    echo "   Install Python from https://python.org/downloads"
    exit 1
fi

echo "✓ Using $PYTHON ($($PYTHON --version))"

# ── Check virtual environment ─────────────────────────────────
if [ -x "venv/bin/python" ]; then
    echo "✓ Virtual environment found"
    source venv/bin/activate
    PYTHON="$SCRIPT_DIR/venv/bin/python"
elif [ -x ".venv/bin/python" ]; then
    echo "✓ Virtual environment found (.venv)"
    source .venv/bin/activate
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
else
    echo "Creating virtual environment..."
    $PYTHON -m venv venv
    source venv/bin/activate
    PYTHON="$SCRIPT_DIR/venv/bin/python"
    echo "✓ Virtual environment created"
fi

# ── Install dependencies ──────────────────────────────────────
echo ""
echo "Checking dependencies..."
# Only the UI bootstrap is needed to choose a runtime. The wizard installs
# the selected runtime after configuration, with errors reported to the user.
"$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else "The selected virtual environment requires Python 3.11+")'
"$PYTHON" -m pip install --quiet --upgrade pip
"$PYTHON" -m pip install --quiet -r requirements-wizard.txt

echo "✓ Dependencies ready"
echo ""

# ── Launch Wizard ─────────────────────────────────────────────
echo "Launching Helix‑AGI Setup Wizard..."
echo ""
"$PYTHON" -m wizard "$@"
