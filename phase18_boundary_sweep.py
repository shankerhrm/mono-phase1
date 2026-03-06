import multiprocessing
import json
import os
from phase18_cultural_evolution import run_evolution

def run_single_experiment(params):
    depletion, restore_mult, seed = params
    try:
        result = run_evolution(
            seed=seed,
            total_gens=500,
            depletion_rate=depletion,
            regeneration_rate=0.01,
            env_exponent=2.0,
            restore_mult=restore_mult
        )
        return {
            'depletion': depletion,
            'restore_mult': restore_mult,
            'seed': seed,
            'result': result
        }
    except Exception as e:
        return {
            'depletion': depletion,
            'restore_mult': restore_mult,
            'seed': seed,
            'error': str(e)
        }

def main():
    depletions = [round(0.08 + i * 0.005, 3) for i in range(9)]  # 0.08 to 0.12
    restore_mults = [round(0.15 + i * 0.01, 2) for i in range(11)]  # 0.15 to 0.25

    param_combinations = []
    for dep in depletions:
        for rm in restore_mults:
            for seed in range(1):  # Reduced for testing
                param_combinations.append((dep, rm, seed))

    print(f"Total runs: {len(param_combinations)}")

    results = []
    for params in param_combinations:
        result = run_single_experiment(params)
        results.append(result)
        if len(results) % 10 == 0:
            print(f"Completed {len(results)} runs")

    # Save results
    os.makedirs('phase18_sweep', exist_ok=True)
    with open('phase18_sweep/sweep_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Sweep completed. Results saved to phase18_sweep/sweep_results.json")

if __name__ == "__main__":
    main()
