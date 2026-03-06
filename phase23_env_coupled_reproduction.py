"""
Phase-23: Environment-Coupled Reproduction Experiment

Tests if quadratic environment-reproduction coupling creates sustainable ecosystems.
Runs 2000 generations and reports population/environmental trajectory.

Key change: reproduction_probability *= env_quality ** 2
"""

import json
import subprocess
import sys
import os

def run_phase23(seed=0, total_gens=2000):
    cmd = [
        sys.executable,
        'phase19_internal_economy.py',
        '--restore_mult', '3.0',
        '--target', '20',
        '--seed', str(seed),
        '--total_gens', str(total_gens),
        '--depletion_rate', '0.05',
        '--regeneration_rate', '0.02'
    ]

    print(f"Running Phase-23: {total_gens}-generation experiment (seed={seed})...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__) or '.')

    if result.returncode != 0:
        print(f"Error running simulation: {result.stderr}")
        return None

    try:
        data = json.loads(result.stdout)
        return data
    except Exception as e:
        print(f"Error parsing output: {e}")
        print(f"Stdout (last 500 chars): {result.stdout[-500:]}")
        print(f"Stderr (last 500 chars): {result.stderr[-500:]}")
        return None


def print_trajectory(data):
    """Print key metrics every 100 generations."""
    metrics = data.get('metrics_per_gen', [])
    summary = data.get('summary', data)

    print("\n=== Phase-23: Environment-Coupled Reproduction ===")
    print(f"Seed: {summary.get('seed', '?')}")
    print(f"Total gens: {summary.get('total_gens', '?')}")
    print(f"Final gen: {summary.get('final_gen', len(metrics)-1)}")
    print(f"Final pop: {summary.get('final_population', '?')}")
    survived = summary.get('survived', len(metrics) >= 2000)
    print(f"Survived: {survived}")
    print()

    print(f"{'Gen':>6} {'Pop':>6} {'Env':>8} {'AvgE':>8} {'Deaths':>7} {'Repros':>7} {'Restorers%':>10}")
    print("-" * 62)

    for i, m in enumerate(metrics):
        if i % 100 == 0 or i == len(metrics) - 1:
            pop = m.get('population', 0)
            env = m.get('environmental_quality', 0)
            avg_e = m.get('avg_energy', 0)
            prop_r = m.get('proportion_restoring', 0)
            repros = m.get('successful_reproductions', 0)
            print(f"{i:>6} {pop:>6} {env:>8.3f} {avg_e:>8.1f} {'':>7} {repros:>7} {prop_r*100:>9.1f}%")

    # Regime classification
    if not survived:
        print(f"\nRegime: COLLAPSE (extinct at gen {summary.get('final_gen', '?')})")
    elif len(metrics) >= 100:
        last_100_pops = [m['population'] for m in metrics[-100:]]
        pop_std = (sum((p - sum(last_100_pops)/len(last_100_pops))**2 for p in last_100_pops) / len(last_100_pops)) ** 0.5
        avg_pop = sum(last_100_pops) / len(last_100_pops)
        cv = pop_std / avg_pop if avg_pop > 0 else 999

        last_100_env = [m.get('environmental_quality', 0) for m in metrics[-100:]]
        avg_env = sum(last_100_env) / len(last_100_env)

        if cv < 0.15 and avg_env > 0.4:
            print(f"\nRegime: EQUILIBRIUM (pop CV={cv:.3f}, avg_env={avg_env:.3f})")
        else:
            print(f"\nRegime: OSCILLATORY (pop CV={cv:.3f}, avg_env={avg_env:.3f})")


if __name__ == "__main__":
    data = run_phase23()
    if data:
        # Handle both direct summary and nested format
        if 'summary' in data:
            print_trajectory(data)
            output = data
        else:
            # Data is the full result from run_evolution
            print_trajectory(data)
            output = data

        with open('phase23_output.json', 'w') as f:
            json.dump(output, f, indent=2)
        print("\nResults saved to phase23_output.json")
    else:
        print("Phase-23 experiment failed.")
