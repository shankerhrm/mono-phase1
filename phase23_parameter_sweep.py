"""
Phase-23 Parameter Sweep: Testing Environment-Coupled Reproduction

Same 27 parameter combinations as Phase-22, but with:
- Env bailout removed
- Quadratic reproduction coupling (env_q ** 2)
- Threshold penalty (env < 0.3 -> *= 0.1)
- Min reproduction floor (0.001)

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
                    '--total_gens', '500',
                    '--depletion_rate', str(dep),
                    '--regeneration_rate', str(reg)
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__) or '.')

                if result.returncode != 0:
                    print(f"Error in run {run_count}: {result.stderr[-200:]}")
                    continue

                try:
                    data = json.loads(result.stdout)

                    # Extract summary metrics
                    summary = {
                        'seed': data.get('seed', 0),
                        'total_gens': data.get('total_gens', 2000),
                        'final_gen': data.get('final_gen', 0),
                        'final_population': data.get('final_population', 0),
                        'survived': data.get('survived', False),
                        'peak_population': data.get('peak_population', 0),
                        'depletion_rate': dep,
                        'regeneration_rate': reg,
                        'restore_mult': res,
                    }

                    # Extract trajectory data (every 100 gens)
                    metrics = data.get('metrics_per_gen', [])
                    if metrics:
                        summary['final_environmental_quality'] = metrics[-1].get('environmental_quality', 0)
                        summary['final_avg_energy'] = metrics[-1].get('avg_energy', 0)
                        summary['final_proportion_restoring'] = metrics[-1].get('proportion_restoring', 0)
                    else:
                        summary['final_environmental_quality'] = data.get('final_environmental_quality', 0)
                        summary['final_avg_energy'] = data.get('final_avg_energy', 0)
                        summary['final_proportion_restoring'] = data.get('final_proportion_restoring', 0)


                        # Population stats for last 100 gens (for regime classification)
                        if metrics:
                            last_n = metrics[-min(100, len(metrics)):]
                            pops = [m['population'] for m in last_n]
                            summary['last_100_avg_pop'] = sum(pops) / len(pops) if pops else 0
                            summary['last_100_min_pop'] = min(pops) if pops else 0
                            summary['last_100_max_pop'] = max(pops) if pops else 0

                            envs = [m.get('environmental_quality', 0) for m in last_n]
                            summary['last_100_avg_env'] = sum(envs) / len(envs) if envs else 0
                        else:
                            summary['last_100_avg_pop'] = data.get('final_population', 0)
                            summary['last_100_avg_env'] = data.get('final_environmental_quality', 0)


                    results.append(summary)
                    status = "SURVIVED" if summary['survived'] else f"EXTINCT@{summary['final_gen']}"
                    print(f"  -> {status}, pop={summary['final_population']}, env={summary.get('final_environmental_quality', 'N/A')}")

                except Exception as e:
                    print(f"Error parsing run {run_count}: {e}")

    with open('phase23_sweep_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nPhase-23 sweep completed. {len(results)}/{total_runs} runs saved to phase23_sweep_results.json")

if __name__ == "__main__":
    run_sweep()
