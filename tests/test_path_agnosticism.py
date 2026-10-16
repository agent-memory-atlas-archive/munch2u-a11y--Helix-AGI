import os
import re
from pathlib import Path

def test_production_and_scripts_paths_are_agnostic():
    """Verify that core production files, setup, key scripts, and tests do not hardcode /home/nemo."""
    repo_root = Path(__file__).resolve().parent.parent
    critical_files = [
        "llm/providers/base.py",
        "main.py",
        "setup.py",
        "scripts/run_health_check.py",
        "scripts/live_interactive_agent_session.py",
        "scripts/mrag_port_parity.py",
    ]
    # Add all test python files
    for test_file in (repo_root / "tests").glob("*.py"):
        if test_file.name != "test_path_agnosticism.py":
            critical_files.append(f"tests/{test_file.name}")

    violations = []
    for rel_path in critical_files:
        full_path = repo_root / rel_path
        if not full_path.exists():
            continue
        content = full_path.read_text(encoding="utf-8")
        matches = [m.start() for m in re.finditer(r"/home/nemo", content)]
        if matches:
            violations.append(f"{rel_path}: contains {len(matches)} occurrences of /home/nemo")
    
    assert not violations, "Hardcoded /home/nemo paths found in critical files:\n" + "\n".join(violations)

if __name__ == "__main__":
    test_production_and_scripts_paths_are_agnostic()
    print("ALL CODE AND TEST PATHS ARE FULLY AGNOSTIC")
