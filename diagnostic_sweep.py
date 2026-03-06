#!/usr/bin/env python3
"""
Diagnostic Sweep: Run MONO with fixed parameters across 100 seeds to characterize collapse behavior.
Logs summary statistics for each seed to analyze extinction patterns.
"""

import subprocess
import json
import sys
import os

def run_diagnostic_sweep():
    """Run diagnostic parameter sweep for Experiment M: Cultural Stability."""
    
    # Parameters for final stability test
    restore_mults = [3.0]
    seeds = range(30)  # Increased for robustness
    total_gens = 10000  # Extended to test long-term stability
    total_runs = len(restore_mults) * len(seeds)
    run_count = 0
    results = []

    for res in restore_mults:
        for seed in seeds:
            run_count += 1
            print(f"Running restore_mult {res}, seed {seed} ({run_count}/{total_runs})")

            cmd = [
                sys.executable,
                'phase19_internal_economy.py',
                '--restore_mult', str(res),
                '--target', '20',
                '--total_gens', str(total_gens),
                '--depletion_rate', '0.005',
                '--regeneration_rate', '0.2',
                '--env_exponent', '0.0',
                '--seed', str(seed)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))

            if result.returncode != 0:
                print(f"Error in restore_mult {res}, seed {seed}: {result.stderr}")
                continue

            try:
                stdout = result.stdout.strip()
                if stdout.startswith("==="):
                    stdout = stdout.split('\n', 1)[1]
                data = json.loads(stdout)
                summary = data
                summary['restore_mult'] = res
                results.append(summary)
            except Exception as e:
                print(f"Error parsing restore_mult {res}, seed {seed}: {e}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")

    # Save results
    with open('diagnostic_sweep_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Sweep complete. Results saved to diagnostic_sweep_results.json")

if __name__ == "__main__":
    run_diagnostic_sweep()
