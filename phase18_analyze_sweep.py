import json
import numpy as np
from collections import defaultdict

def detrend_env(env_series):
    # Simple linear detrend
    x = np.arange(len(env_series))
    slope = np.polyfit(x, env_series, 1)[0]
    return env_series - slope * x

def compute_autocorr(series, lag):
    if len(series) < lag + 1:
        return 0
    return np.corrcoef(series[:-lag], series[lag:])[0,1]

def classify_regime(result):
    summary = result['result']['summary']
    gen_data = result['result']['gen_data']
    if summary['extinct']:
        return 'III'  # Collapse

    # Last 300 gens or all if less
    env_series = [g['environmental_quality'] for g in gen_data[-300:]]
    if len(env_series) < 10:
        return 'I'  # Stable

    detrended = detrend_env(env_series)
    std_dev = np.std(detrended)
    max_autocorr = max(abs(compute_autocorr(detrended, lag)) for lag in range(1, min(51, len(detrended)//2)))

    if max_autocorr > 0.3 and std_dev > 0.05:
        return 'II'  # Oscillatory
    else:
        return 'I'  # Stable

def main():
    with open('phase18_sweep/sweep_results.json', 'r') as f:
        results = json.load(f)

    print(f"Total results loaded: {len(results)}")

    # Group by depletion and restore_mult
    grouped = defaultdict(list)
    for res in results:
        if 'error' in res:
            print(f"Error in result: {res['error']}")
            continue
        key = (res['depletion'], res['restore_mult'])
        grouped[key].append(res)

    print(f"Number of groups: {len(grouped)}")

    phase_diagram = {}
    for key, group in grouped.items():
        depletion, restore_mult = key
        extinct_count = sum(1 for r in group if r['result']['summary']['extinct'])
        p_extinct = extinct_count / len(group)

        surviving = []
        oscillatory_count = 0

        if p_extinct >= 0.5:
            regime = 'III'
        else:
            surviving = [r for r in group if not r['result']['summary']['extinct']]
            oscillatory_count = sum(1 for r in surviving if classify_regime(r) == 'II')
            if oscillatory_count / len(surviving) > 0.5:
                regime = 'II'
            else:
                regime = 'I'

        phase_diagram[key] = {
            'regime': regime,
            'p_extinct': p_extinct,
            'oscillatory_fraction': oscillatory_count / len(surviving) if surviving else 0
        }

    # Print text-based diagram
    depletions = sorted(set(k[0] for k in phase_diagram))
    restore_mults = sorted(set(k[1] for k in phase_diagram))

    print("Phase-18 Boundary Map (Regime: I=Stable, II=Oscillatory, III=Collapse)")
    print("Depletion \\ Restore_mult", end=" ")
    for rm in restore_mults:
        print("2.0f", end=" ")
    print()
    for dep in depletions:
        print("1.3f", end=" ")
        for rm in restore_mults:
            regime = phase_diagram.get((dep, rm), {}).get('regime', '?')
            print(regime, end="  ")
        print()

    # Save detailed results
    phase_diagram_str_keys = {str(k): v for k, v in phase_diagram.items()}
    with open('phase18_sweep/phase_diagram.json', 'w') as f:
        json.dump(phase_diagram_str_keys, f, indent=2)

    print("Phase diagram saved to phase18_sweep/phase_diagram.json")

if __name__ == "__main__":
    main()
