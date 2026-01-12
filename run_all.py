import sys
import subprocess
from pathlib import Path

#!/usr/bin/env python3

ROOT = Path(__file__).parent
CANDIDATES = {
    1: ["1_get_representations.py"],
    2: ["2_get_adjacency_matrices.py"],
    3: ["3_get_centralities.py"],
    4: ["4_get_heatmap.py"],
}

def find_script(step):
    for name in CANDIDATES[step]:
        p = ROOT / name
        if p.exists():
            return p
    return None

def run_script(path):
    print(f"Running: {path.name}")
    result = subprocess.run([sys.executable, str(path)])
    if result.returncode != 0:
        print(f"Script {path.name} ended, code: {result.returncode}")
        sys.exit(result.returncode)

def main():
    for i in range(1, 5):
        script = find_script(i)
        if not script:
            print(f"No script for step {i}")
            sys.exit(1)
        run_script(script)
    print("All steps ended OK.")

if __name__ == "__main__":
    main()