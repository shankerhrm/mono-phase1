#!/usr/bin/env python3
"""
Analyze Diagnostic Sweep Results
Loads diagnostic_sweep_results.json and computes statistics on collapse behavior.
"""

import json
import statistics
from collections import Counter

def analyze_sweep():
    with open('diagnostic_sweep_results.json', 'r') as f:
        results = json.load(f)

    from collections import defaultdict
    results_by_res = defaultdict(list)
    for s in results:
        results_by_res[s['restore_mult']].append(s)

    print("Diagnostic Sweep Analysis (30 seeds across 3 restore_mult values, 5000 generations)")
    print("=" * 70)

    for res in sorted(results_by_res.keys()):
        res_results = results_by_res[res]
        extinction_gens = [s['final_gen'] for s in res_results]
        peak_pops = [s['peak_population'] for s in res_results]
        min_envs = [s['min_environmental_quality'] for s in res_results]
        restoration_last_10 = [s['total_restoration_last_10'] for s in res_results]
        extraction_last_10 = [s['total_extraction_last_10'] for s in res_results]

        survivors = sum(1 for gen in extinction_gens if gen == 5000)

        print(f"\nRestore Mult {res}:")
        print(f"  Extinction Gens: Mean {statistics.mean(extinction_gens):.1f}, Std {statistics.stdev(extinction_gens):.1f}")
        print(f"  Survivors: {survivors}/10")
        print(f"  Peak Populations: Mean {statistics.mean(peak_pops):.1f}, Std {statistics.stdev(peak_pops):.1f}")
        print(f"  Min Environmental Quality: Mean {statistics.mean(min_envs):.3f}, Std {statistics.stdev(min_envs):.3f}")
        print(f"  Final Mean Artifact X: Mean {statistics.mean([s['final_mean_artifact_x'] for s in res_results]):.3f}")
        print(f"  Final Mean Artifact R: Mean {statistics.mean([s['final_mean_artifact_r'] for s in res_results]):.3f}")
        print(f"  Last 10 Generations Activity: Restoration {statistics.mean(restoration_last_10):.1f}, Extraction {statistics.mean(extraction_last_10):.1f}")

if __name__ == "__main__":
    analyze_sweep()
