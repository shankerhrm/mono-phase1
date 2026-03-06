import multiprocessing
import json
import os
import subprocess
import sys

def run_single_experiment(params):
    restore_mult, exchange_rate, seed = params
    try:
        # Run the simulation
        result = subprocess.run([
            sys.executable, 'phase19_internal_economy.py',
            '--restore_mult', str(restore_mult),
            '--exchange_rate', str(exchange_rate),
            '--seed', str(seed)
        ], capture_output=True, text=True, timeout=1000)  # 16 min timeout

        if result.returncode == 0:
            output = result.stdout.strip()
            try:
                data = json.loads(output)
                return {
                    'restore_mult': restore_mult,
                    'exchange_rate': exchange_rate,
                    'seed': seed,
                    'result': data
                }
            except json.JSONDecodeError as e:
                return {
                    'restore_mult': restore_mult,
                    'exchange_rate': exchange_rate,
                    'seed': seed,
                    'error': f"JSON decode error: {e}, stdout len: {len(output)}"
                }
        else:
            return {
                'restore_mult': restore_mult,
                'exchange_rate': exchange_rate,
                'seed': seed,
                'error': result.stderr
            }
    except Exception as e:
        return {
            'restore_mult': restore_mult,
            'exchange_rate': exchange_rate,
            'seed': seed,
            'error': str(e)
        }

def main():
    restore_mults = [1.0, 1.5, 2.0, 2.5, 3.0]
    exchange_rates = [1.0, 2.0, 3.0]

    param_combinations = []
    for rm in restore_mults:
        for er in exchange_rates:
            for seed in range(10):  # 10 seeds per combination
                param_combinations.append((rm, er, seed))

    print(f"Total runs: {len(param_combinations)}")

    results = []
    for i, params in enumerate(param_combinations):
        result = run_single_experiment(params)
        results.append(result)
        if (i + 1) % 10 == 0:
            print(f"Completed {i + 1} runs")

    # Save results
    os.makedirs('phase19_sweep', exist_ok=True)
    with open('phase19_sweep/sensitivity_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Sensitivity sweep completed. Results saved to phase19_sweep/sensitivity_results.json")

if __name__ == "__main__":
    main()
