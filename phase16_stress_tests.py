"""
Phase-16 Stress Tests: Robustness Validation

Tests:
- Mutation sweep: ×0.1, ×1, ×5 mutation rates
- Period sweep: 20, 40, 160, 300 periods
- Individual controller: per-cell α/β (optional, complex)

Core: Parameterized run_evolution, grouped results, extinction tracking.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from phase16_evolution import run_evolution  # Modified to accept params


def run_mutation_sweep(seeds=range(1, 6)):
    """Mutation sweep: vary mutation rate ×0.1, ×1, ×5"""
    mutation_levels = [0.1, 1.0, 5.0]
    results = {"mutation": {}}
    total_runs = 0

    for m in mutation_levels:
        results["mutation"][m] = []
        print(f"\nRunning mutation ×{m}...")
        for seed in seeds:
            print(f"  Seed {seed}...", flush=True)
            r = run_evolution(seed, mutation_scale=m)
            results["mutation"][m].append(r)
            total_runs += 1
            print(f"TOTAL RUNS: {total_runs}")

    return results


def run_period_sweep(seeds=range(1, 6)):
    """Period sweep: 20, 40, 160, 300"""
    periods = [20, 40, 160, 300]
    results = {"period": {}}

    for p in periods:
        results["period"][p] = []
        print(f"\nRunning period {p}...")
        for seed in seeds:
            print(f"  Seed {seed}...")
            r = run_evolution(seed, period=p)
            results["period"][p].append(r)

    return results


def run_individual_controller_test(seeds=range(1, 6)):
    """Individual-level controller (per-cell α/β)"""
    # TODO: Implement after mutation/period validation
    # Requires code changes for per-cell controllers
    print("Individual controller test: Not yet implemented.")
    return {"individual": []}


def analyze_results(results, test_name):
    """Compute grouped statistics"""
    if test_name not in results:
        return

    for key, runs in results[test_name].items():
        if not runs:
            continue

        final_alphas = [r['final_alpha'] for r in runs if r['total_gens'] == 1000]
        final_betas = [r['final_beta'] for r in runs if r['total_gens'] == 1000]
        final_ratios = [r['final_ratio'] for r in runs if r['total_gens'] == 1000]
        final_fps = [r['final_fp'] for r in runs if r['total_gens'] == 1000]
        final_loads = [r['final_load'] for r in runs if r['total_gens'] == 1000]
        final_omegas = [r['final_omega'] for r in runs if r['total_gens'] == 1000]
        final_convergences = [r['final_convergence'] for r in runs if r['total_gens'] == 1000]

        extinctions = len([r for r in runs if r['total_gens'] < 1000])

        print(f"\n{test_name} {key}:")
        print(f"  Extinctions: {extinctions}/5")
        if final_alphas:
            print(f"  α: {sum(final_alphas)/len(final_alphas):.3f} ± { (sum((x - sum(final_alphas)/len(final_alphas))**2 for x in final_alphas)/len(final_alphas))**0.5 :.3f}")
            print(f"  β: {sum(final_betas)/len(final_betas):.3f} ± { (sum((x - sum(final_betas)/len(final_betas))**2 for x in final_betas)/len(final_betas))**0.5 :.3f}")
            print(f"  Ratio: {sum(final_ratios)/len(final_ratios):.3f} ± { (sum((x - sum(final_ratios)/len(final_ratios))**2 for x in final_ratios)/len(final_ratios))**0.5 :.3f}")
            print(f"  FP: {sum(final_fps)/len(final_fps):.3f}")
            print(f"  Load: {sum(final_loads)/len(final_loads):.3f}")
            print(f"  ω: {sum(final_omegas)/len(final_omegas):.5f}")
            print(f"  Conv: {sum(final_convergences)/len(final_convergences):.3f}")


def main():
    print("Phase-16 Stress Tests Starting...")

    all_results = {}

    # Mutation sweep
    print("\n=== MUTATION SWEEP ===")
    mutation_results = run_mutation_sweep()
    all_results.update(mutation_results)
    analyze_results(mutation_results, "mutation")

    # Save intermediate
    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('phase16_stress_artifacts', f'stress_tests_{stamp}')
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'mutation_results.json'), 'w') as f:
        json.dump(mutation_results, f, indent=2)

    print(f"Mutation results saved to {out_dir}")

    # Period sweep
    print("\n=== PERIOD SWEEP ===")
    period_results = run_period_sweep()
    all_results.update(period_results)
    analyze_results(period_results, "period")

    with open(os.path.join(out_dir, 'period_results.json'), 'w') as f:
        json.dump(period_results, f, indent=2)

    print(f"Period results saved to {out_dir}")

    # Individual controller (placeholder)
    # print("\n=== INDIVIDUAL CONTROLLER ===")
    # individual_results = run_individual_controller_test()
    # all_results.update(individual_results)
    # analyze_results(individual_results, "individual")

    # Final save
    with open(os.path.join(out_dir, 'all_stress_results.json'), 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nAll results saved to {out_dir}")


if __name__ == '__main__':
    main()
