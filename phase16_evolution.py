"""
Phase-16: Evolvable Stress Phenotypes Evolution Experiment (Corrected)

Fixes:
- Proper rolling 100-gen windows for FP and load
- Single controller update per generation
- Safe extinction handling
- Safe stdev usage
"""

import json
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from phase10.observer import Phase10Observer
from phase12.stress_index import CompositeStressIndex
from phase15.panic_controller import PhysiologicalController
from phase13.oscillator import population_omega_stats
from phase13.run_phase13 import create_identity_for_env, run_generation, backfill_population

import reproduction.spawn as spawn


def safe_mean(x):
    return statistics.mean(x) if x else 0.0


def safe_stdev(x):
    return statistics.stdev(x) if len(x) > 1 else 0.0


def run_evolution(seed, total_gens=1000, period=80, target_pop=80, mutation_scale=1.0, individual_controller=False):
    random.seed(seed)

    # Set mutation rate
    spawn.mutation_rate = 0.01 * mutation_scale

    if individual_controller:
        print("Individual controller mode not implemented.")
        return {
            'seed': seed,
            'total_gens': 0,
            'metrics': [],
            'final_alpha': 0,
            'final_beta': 0,
            'final_ratio': 0,
            'final_fp': 0,
            'final_load': 0,
            'final_omega': 0,
            'final_convergence': 0,
        }

    observer = Phase10Observer(seed=seed, env='phase16_evolution')
    sm = SpeciesMemory(alpha=0.1, epsilon=0.1)
    si = CompositeStressIndex()
    pc = PhysiologicalController(alpha=0.2, beta=0.3,
                                 activation_level=0.3,
                                 psi_baseline=0.2)

    pop = [MonoCell(create_identity_for_env('A'))
           for _ in range(target_pop)]

    metrics_per_100_gens = []

    panic_window = []
    load_window = []

    panic_out = {"state": "CALM", "load": 0.0}
    psi = 0.0

    for gen in range(total_gens):

        env_type = 'B' if (gen % period) / period >= 0.5 else 'A'
        observer.set_generation(gen)

        # --- Run generation using previous panic state ---
        pop, stats = run_generation(
            pop, sm, gen, observer, env_type,
            panic_state=panic_out
        )

        if not pop:
            print(f"EXTINCTION at gen {gen} for seed {seed}")
            break

        # --- Update stress index ---
        psi = si.update(
            avg_energy=stats['avg_energy'],
            basal_burn=1.0,
            repro_attempts=stats['repro_attempts'],
            repro_successes=stats['repro_successes'],
            deaths=stats['deaths'],
            population_size=stats['population_size'],
            gamma_variance=stats['gamma_variance']
        )

        # --- Update controller using updated psi ---
        mean_alpha = safe_mean([c.id.alpha for c in pop])
        mean_beta = safe_mean([c.id.beta for c in pop])

        pc.alpha = mean_alpha
        pc.beta = mean_beta

        panic_out = pc.update(
            psi,
            avg_energy=stats['avg_energy'],
            structural_integrity=safe_mean(
                [c.structure.size() for c in pop]
            )
        )

        panic_window.append(panic_out['state'] != 'CALM')
        load_window.append(panic_out['load'])

        # --- Record every 100 generations ---
        if (gen + 1) % 100 == 0:

            omega_stats = population_omega_stats(pop)

            alphas = [c.id.alpha for c in pop]
            betas = [c.id.beta for c in pop]

            fp_window = sum(panic_window) / len(panic_window)
            mean_load = safe_mean(load_window)

            metrics_per_100_gens.append({
                'gen': gen + 1,
                'mean_alpha': safe_mean(alphas),
                'mean_beta': safe_mean(betas),
                'alpha_beta_ratio':
                    safe_mean(alphas) / safe_mean(betas)
                    if safe_mean(betas) > 0 else 0,
                'fp': fp_window,
                'mean_load': mean_load,
                'omega_mean': omega_stats['mean'],
                'omega_std': omega_stats['std'],
                'convergence': omega_stats['convergence_ratio']
            })

            panic_window.clear()
            load_window.clear()

        # --- Maintain population size ---
        pop = backfill_population(pop, target_pop, env_type)

    # Safe return
    if not metrics_per_100_gens:
        return {
            'seed': seed,
            'total_gens': 0,
            'metrics': [],
            'final_alpha': 0,
            'final_beta': 0,
            'final_ratio': 0,
            'final_fp': 0,
            'final_load': 0,
            'final_omega': 0,
            'final_convergence': 0,
        }

    final = metrics_per_100_gens[-1]

    return {
        'seed': seed,
        'total_gens': final['gen'],
        'metrics': metrics_per_100_gens,
        'final_alpha': final['mean_alpha'],
        'final_beta': final['mean_beta'],
        'final_ratio': final['alpha_beta_ratio'],
        'final_fp': final['fp'],
        'final_load': final['mean_load'],
        'final_omega': final['omega_mean'],
        'final_convergence': final['convergence'],
    }


def main():
    seeds = list(range(1, 6))  # default 5 seeds
    total_gens = 1000
    period = 80

    print(
        f"Starting Phase-16 evolution experiment: "
        f"{total_gens} gens, {len(seeds)} seeds...",
        flush=True
    )

    results = []
    start_time = time.time()

    for seed in seeds:
        print(f"Running seed {seed}...", flush=True)
        r = run_evolution(seed, total_gens, period)
        results.append(r)

        print(
            f"  Seed {seed}: "
            f"Final α={r['final_alpha']:.3f} "
            f"β={r['final_beta']:.3f} "
            f"Ratio={r['final_ratio']:.3f} "
            f"FP={r['final_fp']:.3f} "
            f"Load={r['final_load']:.3f} "
            f"ω={r['final_omega']:.5f} "
            f"Conv={r['final_convergence']:.4f}"
        )

    elapsed = time.time() - start_time
    print(f"\nEvolution experiment completed in {elapsed:.1f}s.")

    # --- Convergence Analysis ---
    final_alphas = [r['final_alpha'] for r in results]
    final_betas = [r['final_beta'] for r in results]
    final_ratios = [r['final_ratio'] for r in results]
    final_fps = [r['final_fp'] for r in results]
    final_loads = [r['final_load'] for r in results]
    final_omegas = [r['final_omega'] for r in results]
    final_convergences = [r['final_convergence'] for r in results]

    print("\nConvergence Analysis:")
    print(f"α mean: {safe_mean(final_alphas):.3f} ± {safe_stdev(final_alphas):.3f}")
    print(f"β mean: {safe_mean(final_betas):.3f} ± {safe_stdev(final_betas):.3f}")
    print(f"α/β ratio mean: {safe_mean(final_ratios):.3f} ± {safe_stdev(final_ratios):.3f}")
    print(f"FP mean: {safe_mean(final_fps):.3f} ± {safe_stdev(final_fps):.3f}")
    print(f"Load mean: {safe_mean(final_loads):.3f} ± {safe_stdev(final_loads):.3f}")
    print(f"ω mean: {safe_mean(final_omegas):.5f} ± {safe_stdev(final_omegas):.5f}")
    print(f"Convergence mean: {safe_mean(final_convergences):.3f} ± {safe_stdev(final_convergences):.3f}")

    if safe_stdev(final_alphas) < 0.05 and safe_stdev(final_betas) < 0.05:
        print("RESULT: Evolution converged to single optimal α/β phenotype.")
    elif safe_stdev(final_ratios) < 0.1:
        print("RESULT: Converged to consistent α/β ratio with variation.")
    else:
        print("RESULT: Polymorphism or unstable evolution detected.")

    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('phase16_artifacts',
                           f'evolution_experiment_{stamp}')
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'evolution_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nArtifacts written to: {out_dir}")


if __name__ == '__main__':
    main()
