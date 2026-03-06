"""
Phase-22 Parameter Sweep: Finding Sustainable Ecological Regimes

Sweeps depletion_rate, regeneration_rate, restore_mult to identify:
- Sustainable Equilibrium (stable population/env)
- Oscillatory Ecosystem (cycles)
- Collapse (extinction)

Runs 2000 generations per parameter set.
"""

import json
import subprocess
import sys
import os

def run_sweep():
    depletion_rates = [0.03, 0.05, 0.07]
    regeneration_rates = [0.01, 0.02, 0.03]
    restore_mults = [2.0, 3.0, 4.0]

    results = []

    total_runs = len(depletion_rates) * len(regeneration_rates) * len(restore_mults)
    run_count = 0

    for dep in depletion_rates:
        for reg in regeneration_rates:
            for res in restore_mults:
                run_count += 1
                print(f"Running {run_count}/{total_runs}: dep={dep}, reg={reg}, res={res}")

                cmd = [
                    sys.executable,
                    'phase19_internal_economy.py',
                    '--restore_mult', str(res),
                    '--target', '20',
                    '--seed', '0',
                    '--depletion_rate', str(dep),
                    '--regeneration_rate', str(reg)
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))

                if result.returncode != 0:
                    print(f"Error in run {run_count}: {result.stderr}")
                    continue

                try:
                    lines = result.stdout.strip().split('\n')
                    # Skip the title line, the rest is JSON
                    json_lines = lines[1:]
                    json_output = '\n'.join(json_lines)
                    data = json.loads(json_output)
                    summary = data['summary']
                    summary['depletion_rate'] = dep
                    summary['regeneration_rate'] = reg
                    summary['restore_mult'] = res
                    results.append(summary)
                except Exception as e:
                    print(f"Error parsing run {run_count}: {e}")
                    print(f"Stdout: {result.stdout}")
                    print(f"Stderr: {result.stderr}")

    with open('phase22_sweep_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Phase-22 sweep completed. Results saved to phase22_sweep_results.json")

if __name__ == "__main__":
    run_sweep()
