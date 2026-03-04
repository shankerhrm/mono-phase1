"""
Phase-16: Evolvable Stress Phenotypes Evolution Experiment

Run evolution for 1000 gens, track convergence of α, β, α/β ratio, FP, load, ω.

Test if evolution discovers optimal interior regime or polymorphism.
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

def run_evolution(seed, total_gens=1000, period=80, target_pop=80):
    random.seed(seed)
    observer = Phase10Observer(seed=seed, env='phase16_evolution')
    sm = SpeciesMemory(alpha=0.1, epsilon=0.1)
    si = CompositeStressIndex()
    
    pop = [MonoCell(create_identity_for_env('A')) for _ in range(target_pop)]
    
    metrics_per_100_gens = []
    
    for gen in range(total_gens):
        env_type = 'B' if (gen % period) / period >= 0.5 else 'A'
        observer.set_generation(gen)
        
        # Compute mean alpha and beta for controller
        mean_alpha = statistics.mean([c.id.alpha for c in pop]) if pop else 0.2
        mean_beta = statistics.mean([c.id.beta for c in pop]) if pop else 0.3
        pc = PhysiologicalController(
            alpha=mean_alpha,
            beta=mean_beta,
            activation_level=0.3, 
            psi_baseline=0.2
        )
        
        panic_per_gen = []
        load_per_gen = []
        
        # Run one generation
        panic_out = pc.get_outputs(si.psi)
        pop, stats = run_generation(pop, sm, gen, observer, env_type, panic_state=panic_out)
        
        if len(pop) == 0:
            print(f"EXTINCTION at gen {gen} for seed {seed}")
            break
        
        psi = si.update(
            avg_energy=stats['avg_energy'],
            basal_burn=1.0,
            repro_attempts=stats['repro_attempts'],
            repro_successes=stats['repro_successes'],
            deaths=stats['deaths'],
            population_size=stats['population_size'],
            gamma_variance=stats['gamma_variance']
        )
        panic_out = pc.update(psi, avg_energy=stats['avg_energy'], structural_integrity=statistics.mean([c.structure.size() for c in pop]) if pop else 10.0)
        
        panic_per_gen.append(panic_out['state'] != 'CALM')
        load_per_gen.append(panic_out['load'])
        
        # Track every 100 gens
        if gen % 100 == 0:
            omega_stats = population_omega_stats(pop)
            alphas = [c.id.alpha for c in pop]
            betas = [c.id.beta for c in pop]
            fp_window = sum(panic_per_gen) / len(panic_per_gen) if panic_per_gen else 0
            mean_load = statistics.mean(load_per_gen) if load_per_gen else 0
            
            metrics_per_100_gens.append({
                'gen': gen,
                'mean_alpha': statistics.mean(alphas),
                'mean_beta': statistics.mean(betas),
                'alpha_beta_ratio': statistics.mean(alphas) / statistics.mean(betas) if statistics.mean(betas) > 0 else 0,
                'fp': fp_window,
                'mean_load': mean_load,
                'omega_mean': omega_stats['mean'],
                'omega_std': omega_stats['std'],
                'convergence': omega_stats['convergence_ratio']
            })
        
        pop = backfill_population(pop, target_pop, env_type)
    
    return {
        'seed': seed,
        'total_gens': len(metrics_per_100_gens) * 100,
        'metrics': metrics_per_100_gens,
        'final_alpha': metrics_per_100_gens[-1]['mean_alpha'] if metrics_per_100_gens else 0,
        'final_beta': metrics_per_100_gens[-1]['mean_beta'] if metrics_per_100_gens else 0,
        'final_ratio': metrics_per_100_gens[-1]['alpha_beta_ratio'] if metrics_per_100_gens else 0,
        'final_fp': metrics_per_100_gens[-1]['fp'] if metrics_per_100_gens else 0,
        'final_load': metrics_per_100_gens[-1]['mean_load'] if metrics_per_100_gens else 0,
        'final_omega': metrics_per_100_gens[-1]['omega_mean'] if metrics_per_100_gens else 0,
        'final_convergence': metrics_per_100_gens[-1]['convergence'] if metrics_per_100_gens else 0,
    }

def main():
    seeds = list(range(1, 11))  # 10 seeds
    total_gens = 1000
    period = 80
    
    print(f"Starting Phase-16 evolution experiment: 1000 gens, 10 seeds...", flush=True)
    
    results = []
    start_time = time.time()
    
    for seed in seeds:
        print(f"Running seed {seed}...", flush=True)
        r = run_evolution(seed, total_gens, period)
        results.append(r)
        print(f"  Seed {seed}: Final α={r['final_alpha']:.3f} β={r['final_beta']:.3f} Ratio={r['final_ratio']:.3f} FP={r['final_fp']:.3f} Load={r['final_load']:.3f} ω={r['final_omega']:.5f} Conv={r['final_convergence']:.4f}")
    
    elapsed = time.time() - start_time
    print(f"\nEvolution experiment completed in {elapsed:.1f}s.")
    
    # Analyze convergence
    final_alphas = [r['final_alpha'] for r in results]
    final_betas = [r['final_beta'] for r in results]
    final_ratios = [r['final_ratio'] for r in results]
    final_fps = [r['final_fp'] for r in results]
    final_loads = [r['final_load'] for r in results]
    final_omegas = [r['final_omega'] for r in results]
    final_convergences = [r['final_convergence'] for r in results]
    
    alpha_std = statistics.stdev(final_alphas) if len(final_alphas) > 1 else 0
    beta_std = statistics.stdev(final_betas) if len(final_betas) > 1 else 0
    ratio_std = statistics.stdev(final_ratios) if len(final_ratios) > 1 else 0
    
    print(f"\nConvergence Analysis:")
    print(f"α mean: {statistics.mean(final_alphas):.3f} ± {alpha_std:.3f}")
    print(f"β mean: {statistics.mean(final_betas):.3f} ± {beta_std:.3f}")
    print(f"α/β ratio mean: {statistics.mean(final_ratios):.3f} ± {ratio_std:.3f}")
    print(f"FP mean: {statistics.mean(final_fps):.3f} ± {statistics.stdev(final_fps):.3f}")
    print(f"Load mean: {statistics.mean(final_loads):.3f} ± {statistics.stdev(final_loads):.3f}")
    print(f"ω mean: {statistics.mean(final_omegas):.5f} ± {statistics.stdev(final_omegas):.5f}")
    print(f"Convergence mean: {statistics.mean(final_convergences):.3f} ± {statistics.stdev(final_convergences):.3f}")
    
    if alpha_std < 0.05 and beta_std < 0.05:
        print("RESULT: Evolution converged to single optimal α/β phenotype.")
    elif ratio_std < 0.1:
        print("RESULT: Evolution converged to consistent α/β ratio with some variation.")
    else:
        print("RESULT: Polymorphism or unstable evolution detected.")
    
    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('phase16_artifacts', f'evolution_experiment_{stamp}')
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, 'evolution_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nArtifacts written to: {out_dir}")

if __name__ == '__main__':
    main()
