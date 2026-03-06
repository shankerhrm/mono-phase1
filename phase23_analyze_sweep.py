"""
Analyze Phase-23 Parameter Sweep Results

Classifies each parameter set into ecological regimes and compares with Phase-22 baseline.
"""

import json
import os

def analyze_sweep():
    with open('phase23_sweep_results.json', 'r') as f:
        results = json.load(f)

    regimes = {
        'collapse': [],
        'oscillatory': [],
        'equilibrium': []
    }

    print("=" * 80)
    print("Phase-23 Ecological Regime Analysis (Environment-Coupled Reproduction)")
    print("=" * 80)
    print()
    print(f"{'Params':<30} {'Regime':<14} {'Pop':>6} {'Env':>6} {'Gen':>6} {'Peak':>6}")
    print("-" * 80)

    for res in results:
        dep = res['depletion_rate']
        reg = res['regeneration_rate']
        res_mult = res['restore_mult']
        survived = res.get('survived', False)
        final_pop = res['final_population']
        final_gen = res['final_gen']
        final_env = res.get('final_environmental_quality', 0)
        peak_pop = res.get('peak_population', 0)
        avg_pop_last = res.get('last_100_avg_pop', 0)
        avg_env_last = res.get('last_100_avg_env', 0)

        key = f"dep={dep}, reg={reg}, res={res_mult}"

        if not survived or final_pop == 0:
            regime = 'collapse'
            regimes['collapse'].append(key)
        elif avg_env_last > 0.4 and avg_pop_last > 30:
            # Check population variance for oscillatory vs equilibrium
            pop_range = res.get('last_100_max_pop', 0) - res.get('last_100_min_pop', 0)
            cv = pop_range / avg_pop_last if avg_pop_last > 0 else 999
            if cv < 0.5:
                regime = 'equilibrium'
                regimes['equilibrium'].append(key)
            else:
                regime = 'oscillatory'
                regimes['oscillatory'].append(key)
        else:
            regime = 'oscillatory'
            regimes['oscillatory'].append(key)

        print(f"{key:<30} {regime.upper():<14} {final_pop:>6} {final_env:>6.3f} {final_gen:>6} {peak_pop:>6}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Collapse:    {len(regimes['collapse'])}/27")
    print(f"  Oscillatory: {len(regimes['oscillatory'])}/27")
    print(f"  Equilibrium: {len(regimes['equilibrium'])}/27")
    print(f"  Survived:    {len(regimes['oscillatory']) + len(regimes['equilibrium'])}/27")
    print()

    # Compare with Phase-22
    print("Phase-22 baseline: 27/27 COLLAPSE (0 survived)")
    survived_count = len(regimes['oscillatory']) + len(regimes['equilibrium'])
    if survived_count >= 10:
        print(f"Phase-23 result:   {survived_count}/27 SURVIVED ✓ PASS (target: ≥10)")
    else:
        print(f"Phase-23 result:   {survived_count}/27 SURVIVED ✗ FAIL (target: ≥10)")

    # Parameter sensitivity
    print()
    print("=" * 80)
    print("PARAMETER SENSITIVITY")
    print("=" * 80)

    for param_name, param_key in [('depletion_rate', 'depletion_rate'), ('regeneration_rate', 'regeneration_rate'), ('restore_mult', 'restore_mult')]:
        by_param = {}
        for r in results:
            val = r[param_key]
            survived = r.get('survived', False) and r['final_population'] > 0
            by_param.setdefault(val, {'survived': 0, 'total': 0, 'gens': []})
            by_param[val]['total'] += 1
            by_param[val]['gens'].append(r['final_gen'])
            if survived:
                by_param[val]['survived'] += 1

        print(f"\n  {param_name}:")
        for val in sorted(by_param):
            d = by_param[val]
            avg_gen = sum(d['gens']) / len(d['gens'])
            print(f"    {val}: {d['survived']}/{d['total']} survived, avg_gen={avg_gen:.0f}")


if __name__ == "__main__":
    analyze_sweep()
