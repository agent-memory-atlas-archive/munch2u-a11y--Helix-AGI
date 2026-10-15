"""Terminal inside the workshop namespace; no host environment or filesystem."""
import json
import subprocess
import sys


if __name__ == "__main__":
    args = json.load(sys.stdin)
    result = subprocess.run(["/bin/bash", "--noprofile", "--norc", "-c", args["command"]],
                            capture_output=True, text=True, cwd="/workspace")
    print(json.dumps({"stdout": result.stdout, "stderr": result.stderr,
                      "return_code": result.returncode, "complete": True}))
    sys.exit(result.returncode)
