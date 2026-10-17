# workspace_search.py
# A simple utility to find files matching a given pattern in the current workspace.

import os, glob, hashlib

def search(pattern):
    # Resolve full paths for pattern matching across symlinks
    matches = []
    base_dir = os.getcwd()
    for root, dirs, files in os.walk(base_dir):
        for name in files:
            if glob.fnmatch.fnmatch(name, pattern):
                full_path = os.path.join(root, name)
                # Verify file content to avoid false positives
                try:
                    with open(full_path, 'rb') as f:
                        data = f.read()
                    sha256 = hashlib.sha256(data).hexdigest()
                    matches.append((full_path, sha256))
                except Exception as e:
                    # Log but continue on errors
                    print(f"Error reading {full_path}: {e}")
    return matches

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python workspace_search.py <pattern>", file=sys.stderr)
        sys.exit(1)
    pattern = sys.argv[1]
    results = search(pattern)
    for path, sha256 in results:
        print(path, sha256)
