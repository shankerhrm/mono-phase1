"""
Phase-15 Long-Horizon Stability Test

Verify no slow drift toward boundaries, stable load oscillation, maintained ω convergence.

Params: α=0.2, β=0.3, 1500 gens, 10 seeds.
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

def run_single(seed, total_gens=1500, period=80, target_pop=80):
    random.seed(seed)
    observer = Phase10Observer(seed=seed, env='phase15_stability')
    sm = SpeciesMemory(alpha=0.1, epsilon=0.1)
    si = CompositeStressIndex()
    pc = PhysiologicalController(
        alpha=statistics.mean([c.id.alpha for c in pop]) if pop else 0.2,
        beta=statistics.mean([c.id.beta for c in pop]) if pop else 0.3,
        activation_level=0.3, 
        psi_baseline=0.2
    )
    
    pop = [MonoCell(create_identity_for_env('A')) for _ in range(target_pop)]
    
    panic_per_gen = []
    load_per_gen = []
    omega_per_100_gens = []
    
    for gen in range(total_gens):
        env_type = 'B' if (gen % period) / period >= 0.5 else 'A'
        observer.set_generation(gen)
        
        structural_integrity = statistics.mean([c.structure.size() for c in pop]) if pop else 10.0
        
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
        panic_out = pc.update(psi, avg_energy=stats['avg_energy'], structural_integrity=structural_integrity)
        
        panic_per_gen.append(panic_out['state'] != 'CALM')
        load_per_gen.append(panic_out['load'])
        
        # Track ω every 100 gens
        if gen % 100 == 0:
            omega_stats = population_omega_stats(pop)
            omega_per_100_gens.append((gen, omega_stats['mean'], omega_stats['std'], omega_stats['convergence_ratio']))
        
        pop = backfill_population(pop, target_pop, env_type)
    
    # Compute FP in windows
    window_size = 400  # 5 cycles
    fp_windows = []
    for i in range(0, len(panic_per_gen), window_size):
        window = panic_per_gen[i:i+window_size]
        summer_panic = sum(1 for j, p in enumerate(window) if p and ((i+j) % period) / period < 0.5)
        summer_total = sum(1 for j in range(len(window)) if ((i+j) % period) / period < 0.5)
        fp = summer_panic / max(1, summer_total)
        fp_windows.append(round(fp, 4))
    
    load_mean = statistics.mean(load_per_gen) if load_per_gen else 0
    load_std = statistics.stdev(load_per_gen) if len(load_per_gen) > 1 else 0
    
    return {
        'seed': seed,
        'total_gens': len(panic_per_gen),
        'fp_windows': fp_windows,
        'load_mean': round(load_mean, 4),
        'load_std': round(load_std, 4),
        'omega_trajectory': omega_per_100_gens,
        'final_omega': omega_per_100_gens[-1][1] if omega_per_100_gens else 0,
        'final_convergence': omega_per_100_gens[-1][3] if omega_per_100_gens else 0,
    }

def main():
    seeds = list(range(1, 11))  # 10 seeds
    total_gens = 1500
    period = 80
    
    print(f"Starting Phase-15 stability test: 1500 gens, 10 seeds...", flush=True)
    
    results = []
    start_time = time.time()
    
    for seed in seeds:
        print(f"Running seed {seed}...", flush=True)
        r = run_single(seed, total_gens, period)
        results.append(r)
        print(f"  Seed {seed}: FP windows {r['fp_windows']}, load mean {r['load_mean']:.3f}, final ω {r['final_omega']:.5f}, conv {r['final_convergence']:.4f}")
    
    fp_means = [statistics.mean(r['fp_windows']) for r in results if r['fp_windows']]
    print(f"\nFP means per seed: {fp_means}")
    if fp_means:
        mean_fp = statistics.mean(fp_means)
        std_fp = statistics.stdev(fp_means) if len(fp_means) > 1 else 0
        print(f"Mean FP across seeds: {mean_fp:.3f} ± {std_fp:.3f}")
        if std_fp < 0.03:
            print("Rock solid regime.")
        else:
            print("Regime has variation.")
    
    # Aggregate
    fp_windows_all = [r['fp_windows'] for r in results]
    load_means = [r['load_mean'] for r in results]
    final_omegas = [r['final_omega'] for r in results]
    final_convergences = [r['final_convergence'] for r in results]
    
    # Check stability: FP windows should be stable
    stability_check = all(
        max(window) - min(window) < 0.1 for window in fp_windows_all  # Max variation <10%
    )
    
    print(f"\nStability Check: {'PASSED' if stability_check else 'FAILED'}")
    print(f"FP window variation: {[(max(w)-min(w)) for w in fp_windows_all]}")
    print(f"Mean load: {statistics.mean(load_means):.3f} ± {statistics.stdev(load_means):.3f}")
    print(f"Final ω: {statistics.mean(final_omegas):.5f} ± {statistics.stdev(final_omegas):.5f}")
    print(f"Final convergence: {statistics.mean(final_convergences):.3f} ± {statistics.stdev(final_convergences):.3f}")
    
    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('phase15_artifacts', f'stability_test_{stamp}')
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, 'stability_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nArtifacts written to: {out_dir}")

if __name__ == '__main__':
    main()
