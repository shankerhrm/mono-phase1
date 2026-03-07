import argparse
import json
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
import sys
import threading

SEEDS = [42]
TOTAL_GENS = 1500

def optimal_strategy(env_quality):
    """
    Approximation: when env_quality is high (abundant), strategy 0 (extractor) is optimal.
    When env_quality is low (scarce), strategy 1 (restorer) is optimal.
    """
    return max(0.0, min(1.0, 1.0 - env_quality))

def run_single_seed(seed, period):
    """Run a single simulation."""
    cmd = [
        sys.executable, 'phase19_internal_economy.py',
        '--seed', str(seed),
        '--total_gens', str(TOTAL_GENS),
        '--max_pop', '300',
        '--include_metrics',
    ]
    
    # We must patch phase19_internal_economy.py runtime to use the sine wave.
    # We'll pass an argument to trigger Phase 27 sine-wave mode.
    cmd.extend(['--oscillate_climate', '--oscillation_period', str(period)])

    print(f"  Running seed {seed} with period {period}...", flush=True)

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=os.path.dirname(__file__) or '.'
    )

    def stream_stderr(pipe):
        for line in pipe:
            line_stripped = line.strip()
            if "EXTINCTION" in line_stripped:
                print(f"    {line_stripped}", flush=True)

    stderr_thread = threading.Thread(target=stream_stderr, args=(process.stderr,), daemon=True)
    stderr_thread.start()

    stdout, _ = process.communicate()
    stderr_thread.join(timeout=5)

    data = None
    try:
        start = stdout.find('{')
        if start != -1:
            data = json.loads(stdout[start:])
    except json.JSONDecodeError:
        print("  PARSE ERROR", flush=True)
        return None

    if not data:
        print("  NO DATA", flush=True)
        return None

    return data

def run_experiment(period):
    prefix = f"phase27_fast" if period != 400.0 else "phase27"
    for seed in SEEDS:
        data = run_single_seed(seed, period)
        if not data or not data.get('metrics_per_gen'):
            print(f"Seed {seed} failed to produce usable metrics.")
            continue
            
        metrics = data['metrics_per_gen']
        
        generations = []
        env_qualities = []
        depletion_rates = []
        populations = []
        mean_strategy_traits = []
        strategy_variances = []
        lineage_diversities = []
        restoring_fractions = []
        trait_lags = []
        
        # We need the underlying strategy_trait distribution. Since phase19 output
        # doesn't natively dump histograms every run, we expect the modified script
        # to provide `strategy_histogram` within each gen.
        histograms = []
        
        for m in metrics:
            gen = m['gen']
            env_q = m['environmental_quality']
            pop = m['population']
            mean_st = m.get('mean_strategy_trait', 0.5)
            st_var = m.get('var_strategy_trait', 0.0)
            
            # Reconstruction of sine wave depletion
            dep = 0.10 + 0.05 * math.sin(2 * math.pi * gen / period)
            
            t_lag = abs(mean_st - optimal_strategy(env_q))
            
            generations.append(gen)
            env_qualities.append(env_q)
            depletion_rates.append(dep)
            populations.append(pop)
            mean_strategy_traits.append(mean_st)
            strategy_variances.append(st_var)
            lineage_diversities.append(m.get('lineage_diversity', 0))
            restoring_fractions.append(m.get('proportion_restoring', 0))
            trait_lags.append(t_lag)
            
            hist = m.get('strategy_histogram', [0]*20)
            histograms.append(hist)
            
        output = {
            "generation": generations,
            "env_quality": env_qualities,
            "depletion_rate": depletion_rates,
            "population": populations,
            "mean_strategy_trait": mean_strategy_traits,
            "strategy_variance": strategy_variances,
            "lineage_diversity": lineage_diversities,
            "restoring_fraction": restoring_fractions,
            "trait_lag": trait_lags,
            "extinction_generation": data.get('extinction_gen', None)
        }
        
        with open(f'{prefix}_results_seed{seed}.json', 'w') as f:
            json.dump(output, f, indent=2)
            
        # Visualization 1: Environment vs Trait
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        color = 'tab:green'
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Env Quality / Optimal Trait', color=color)
        ax1.plot(generations, env_qualities, color=color, label='Env Quality', alpha=0.6)
        
        # Plot optimal strategy based on env quality
        optimal_st = [optimal_strategy(e) for e in env_qualities]
        ax1.plot(generations, optimal_st, color='tab:blue', linestyle='--', label='Optimal Trait', alpha=0.5)
        ax1.tick_params(axis='y', labelcolor=color)
        
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Mean Strategy Trait', color=color)
        ax2.plot(generations, mean_strategy_traits, color=color, label='Actual Mean Trait')
        ax2.tick_params(axis='y', labelcolor=color)
        
        fig.tight_layout()
        plt.title(f'Phase 27: Environment vs Trait (Period {period})')
        fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
        plt.savefig(f'{prefix}_env_vs_trait.png', dpi=300)
        plt.close()
        
        # Visualization 2: Population
        plt.figure(figsize=(12, 4))
        plt.plot(generations, populations, color='black')
        plt.fill_between(generations, populations, color='gray', alpha=0.3)
        plt.title(f'Phase 27: Population Dynamics (Period {period})')
        plt.xlabel('Generation')
        plt.ylabel('Population')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{prefix}_population.png', dpi=300)
        plt.close()
        
        # Visualization 3: Trait Variance and Polymorphism Heatmap
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        ax1.plot(generations, strategy_variances, color='purple')
        ax1.set_title(f'Phase 27: Strategy Trait Variance (Period {period})')
        ax1.set_ylabel('Variance')
        ax1.grid(True, alpha=0.3)
        
        # Histogram Heatmap Plot
        hist_array = np.array(histograms).T # transpose for generation on x-axis
        cax = ax2.imshow(hist_array, aspect='auto', origin='lower', cmap='plasma', 
                         extent=[0, max(generations), 0, 1])
        ax2.set_title('Phase 27: Trait Polymorphism Waterfall (Binned 0 to 1)')
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Strategy Trait Value')
        fig.colorbar(cax, ax=ax2, label='Cell Count')
        
        plt.tight_layout()
        plt.savefig(f'{prefix}_trait_variance.png', dpi=300)
        plt.close()
        
        print(f"Results for seed {seed} saved and visualized successfully.")
        
        # Basic Evaluation
        mean_var = np.mean(strategy_variances[len(strategy_variances)//2:])
        mean_lag = np.mean(trait_lags[len(trait_lags)//2:])
        
        print("\n--- Phase 27 Conclusion Estimate ---")
        if np.corrcoef(mean_strategy_traits[-400:], optimal_st[-400:])[0,1] > 0.4 and mean_lag < 0.2:
            print("Verdict: Case A — Adaptive Tracking detected! Trait strongly correlates with environment.")
        elif mean_var > 0.1:
            print("Verdict: Case C — Polymorphism detected! High sustained variance implies divergent clustering.")
        else:
            print("Verdict: Case B — Generalist Evolution. The population converged to a stable middle ground.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Phase-27 Oscillating Climate Evolution Test')
    parser.add_argument('--period', type=float, default=400.0, help='Oscillation period for environmental cycle')
    args = parser.parse_args()
    
    run_experiment(args.period)
