"""
Analyze Phase-22 Parameter Sweep Results

Classifies each parameter set into ecological regimes:
- Collapse: extinction
- Oscillatory: survival with fluctuating dynamics
- Equilibrium: survival with stable population/env
"""

import json

def analyze_sweep():
    with open('phase22_sweep_results.json', 'r') as f:
        results = json.load(f)

    regimes = {
        'collapse': [],
        'oscillatory': [],
        'equilibrium': []
    }

    for res in results:
        dep = res['depletion_rate']
        reg = res['regeneration_rate']
        res_mult = res['restore_mult']
        extinct = res['extinct']
        final_pop = res['final_population']
        final_env = res.get('final_environmental_quality', 0)  # Assuming added in summary

        key = f"dep={dep}, reg={reg}, res={res_mult}"

        if extinct or final_pop == 0:
            regimes['collapse'].append(key)
        elif final_env > 0.5 and final_pop > 80:  # Arbitrary thresholds
            regimes['equilibrium'].append(key)
        else:
            regimes['oscillatory'].append(key)

    print("Phase-22 Ecological Regimes:")
    print(f"Collapse ({len(regimes['collapse'])} sets): {regimes['collapse']}")
    print(f"Oscillatory ({len(regimes['oscillatory'])} sets): {regimes['oscillatory']}")
    print(f"Equilibrium ({len(regimes['equilibrium'])} sets): {regimes['equilibrium']}")

    print("\nDetailed Results:")
    for res in results:
        print(f"Params: dep={res['depletion_rate']}, reg={res['regeneration_rate']}, res={res['restore_mult']} -> Extinct: {res['extinct']}, Final Pop: {res['final_population']}, Final Env: {res.get('final_environmental_quality', 'N/A')}")

if __name__ == "__main__":
    analyze_sweep()
