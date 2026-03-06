"""
Phase-21: Adaptive Environmental Sensing

Runs a 1000-generation experiment to test if environmental sensitivity allows evolution of sustainability.

Adds environment_sensitivity trait that modifies p_restore based on env_quality.
"""

import json
import subprocess
import sys
import os

def run_phase21():
    cmd = [
        sys.executable,
        'phase19_internal_economy.py',
        '--restore_mult', '3.0',
        '--target', '20',
        '--seed', '0'
    ]

    print("Running Phase-21: 1000-generation experiment with environmental sensing...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))

    if result.returncode != 0:
        print(f"Error running simulation: {result.stderr}")
        return None

    try:
        # The last line should be the JSON output
        lines = result.stdout.strip().split('\n')
        json_output = lines[-1]
        data = json.loads(json_output)
        return data
    except Exception as e:
        print(f"Error parsing output: {e}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        return None

if __name__ == "__main__":
    data = run_phase21()
    if data:
        with open('phase21_output.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Phase-21 results saved to phase21_output.json")
    else:
        print("Failed to run Phase-21")
