import sys
sys.path.insert(0, '.')
import os
import json
from collections import defaultdict
from metrics.taxonomy import classify_death, classify_stability, DeathClass, StabilityClass
from metrics.plots import plot_group_overlay

def analyze_experiments():
    groups = ['A', 'B', 'C', 'D']
    results = {}

    for group in groups:
        group_logs = []
        death_counts = defaultdict(int)
        stability_counts = defaultdict(int)
        lifespans = []

        for run in range(30):
            filename = f'snapshots/lineage_{group}_{run}.json'
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    logs = json.load(f)
                group_logs.append((run, logs))
                lifespans.append(len(logs))

                death_class = classify_death(logs)
                if death_class:
                    death_counts[death_class] += 1

                stability_class = classify_stability(logs)
                if stability_class:
                    stability_counts[stability_class] += 1

        results[group] = {
            'death_counts': dict(death_counts),
            'stability_counts': dict(stability_counts),
            'avg_lifespan': sum(lifespans) / len(lifespans) if lifespans else 0,
            'group_logs': group_logs
        }

        print(f'Group {group}:')
        print(f'  Death Classes: {death_counts}')
        print(f'  Stability Classes: {stability_counts}')
        print(f'  Avg Lifespan: {results[group]["avg_lifespan"]}')

        if group_logs:
            plot_group_overlay(group_logs, f'Group {group}')

    # Identify thresholds: groups with high stability
    stable_groups = [g for g, r in results.items() if r['stability_counts'].get(StabilityClass.STATIC_EQUILIBRIUM, 0) + r['stability_counts'].get(StabilityClass.LOW_AMPLITUDE_OSCILLATION, 0) > 15]  # >50%
    print(f'Critical Threshold Groups (high stability): {stable_groups}')

    return results

if __name__ == '__main__':
    analyze_experiments()
