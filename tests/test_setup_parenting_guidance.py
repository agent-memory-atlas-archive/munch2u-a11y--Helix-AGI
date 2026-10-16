import re
from pathlib import Path

def test_parenting_guidance_present_in_setup_and_wizard():
    """Verify that developmental growth/parenting guidance is explicitly documented in setup and wizard."""
    repo_root = Path(__file__).resolve().parent.parent
    
    # 1. Check setup.py
    setup_text = (repo_root / "setup.py").read_text(encoding="utf-8")
    assert "DEVELOPMENTAL" in setup_text or "Parenting" in setup_text or "parenting" in setup_text.lower(), "setup.py must contain developmental parenting guidance"
    assert "sensory shock" in setup_text.lower() or "dump" in setup_text.lower(), "setup.py must warn against dumping files into agent environment"

    # 2. Check wizard/pages/welcome.py
    welcome_text = (repo_root / "wizard/pages/welcome.py").read_text(encoding="utf-8")
    assert "Developmental" in welcome_text or "Growth" in welcome_text or "Nurturing" in welcome_text, "welcome.py must highlight developmental nurturing"
    assert "dump" in welcome_text.lower(), "welcome.py must explain not to dump unstructured data"

if __name__ == "__main__":
    test_parenting_guidance_present_in_setup_and_wizard()
    print("PARENTING GUIDANCE TEST PASSED")
