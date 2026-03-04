"""
Phase-14: Parameter Sweep for Intensity-Based Panic Controller

Sweeps basal_burn and recovery_rate to find tunable FP regime.
Tests whether gradual recovery produces stable oscillatory entrainment.

Tracks:
 - ω convergence, FP rate, panic intensity, bottleneck depth
"""

import concurrent.futures
import json
import os
import random
import statistics
import sys
import time
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from phase10.observer import Phase10Observer
from phase12.stress_index import CompositeStressIndex
from phase14.panic_controller_v14 import PanicController
from phase13.oscillator import population_omega_stats, population_phase_histogram
from phase13.run_phase13 import create_identity_for_env, get_env_params, run_generation, backfill_population

def run_single(seed, total_gens, period=80, target_pop=100, basal_burn=1.0, recovery_rate=0.05):
    random.seed(seed)
    observer = Phase10Observer(seed=seed, env='phase14_sweep')
    sm = SpeciesMemory(alpha=0.1, epsilon=0.1)
    si = CompositeStressIndex()
    pc = PanicController(
        panic_threshold=0.55,
        escalation_rate=0.15,
        recovery_rate=recovery_rate,
        activation_level=0.3,
        escalation_threshold=0.6,
        recovery_threshold=0.5
    )
    
    pop = [MonoCell(create_identity_for_env('A')) for _ in range(target_pop)]
    
    energies = []
    panic_per_gen = []
    min_energy = float('inf')
    max_energy = float('-inf')
    psi_list = []
    
    first_panic_gen = None
    panic_duration = 0
    winter_psi_peaks = []
    
    fp_count = 0
    total_calm_gens = 0
    min_pop_recorded = target_pop
    
    ms_gamma_initial = 0.5
    
    for gen in range(total_gens):
        env_type = 'B' if (gen % period) / period >= 0.5 else 'A'
        observer.set_generation(gen)
        
        panic_out = pc.update(si.psi, generation=gen)
        pop, stats = run_generation(pop, sm, gen, observer, env_type, panic_state=panic_out, basal_burn=basal_burn)
        
        energies.append(stats['avg_energy'])
        min_energy = min(min_energy, stats['avg_energy'])
        max_energy = max(max_energy, stats['avg_energy'])
        panic_per_gen.append(panic_out['state'] != 'CALM')
        
        if len(pop) == 0:
            print(f"EXTINCTION at gen {gen} for seed {seed}")
            break
        
        # Track minimum population BEFORE backfill (bottleneck depth)
        min_pop_recorded = min(min_pop_recorded, len(pop))
        
        psi = si.update(
            avg_energy=stats['avg_energy'], basal_burn=stats['basal_burn'],
            repro_attempts=stats['repro_attempts'], repro_successes=stats['repro_successes'],
            deaths=stats['deaths'], population_size=stats['population_size'],
            gamma_variance=stats['gamma_variance']
        )
        psi_list.append(psi)
        
        if panic_out['state'] != 'CALM':
            panic_duration += 1
            if first_panic_gen is None:
                first_panic_gen = gen
        
        if env_type == 'B':
            winter_psi_peaks.append(psi)
        
        eps = panic_out['memory_softening_eps']
        if eps > 0 and len(pop) > 0:
            cur = {
                'gamma': sum(c.gating_threshold for c in pop) / len(pop),
                'module_count': sum(c.module_count for c in pop) / len(pop),
            }
            sm.soften(eps, cur)
            
        if env_type == 'A':
            total_calm_gens += 1
            if panic_out['state'] != 'CALM': 
                fp_count += 1
                
        pop = backfill_population(pop, target_pop, env_type)

    max_winter_psi = max(winter_psi_peaks) if winter_psi_peaks else 0
    omega_stats = population_omega_stats(pop)
    fp_rate = fp_count / max(total_calm_gens, 1)

    mean_energy = statistics.mean(energies) if energies else 0
    std_energy = statistics.stdev(energies) if len(energies) > 1 else 0
    pct_below_062 = sum(1 for e in energies if e < 0.62) / len(energies) if energies else 0
    total_panic_gens = sum(panic_per_gen)
    winter_cycles = sum(1 for gen in range(len(panic_per_gen)) if (gen % period) / period >= 0.5)
    panic_in_winter = sum(panic_per_gen[gen] for gen in range(len(panic_per_gen)) if (gen % period) / period >= 0.5)

    mean_psi = statistics.mean(psi_list) if psi_list else 0
    std_psi = statistics.stdev(psi_list) if len(psi_list) > 1 else 0
    pct_psi_above_062 = sum(1 for p in psi_list if p > 0.62) / len(psi_list) if psi_list else 0
    min_psi = min(psi_list) if psi_list else 0
    max_psi = max(psi_list) if psi_list else 0

    return {
        'seed': seed,
        'period': period,
        'total_gens': total_gens,
        'bottleneck_depth': min_pop_recorded,
        'false_positive_rate': round(fp_rate, 4),
        'final_omega_mean': round(omega_stats['mean'], 6),
        'final_omega_std': round(omega_stats['std'], 6),
        'convergence_ratio': round(omega_stats['convergence_ratio'], 4),
        'final_ms_gamma': round(sm.Ms.get('gamma', 0.5), 4),
        'lock_broken': abs(sm.Ms.get('gamma', 0.5) - ms_gamma_initial) > 0.05,
        'first_panic_gen': first_panic_gen,
        'panic_duration': panic_duration,
        'max_winter_psi': round(max_winter_psi, 4),
    }

def main():
    basal_burn_values = [0.85, 0.95, 1.05]
    recovery_rate_values = [0.03, 0.05, 0.08]
    seeds = list(range(1, 6))  # 5 seeds per combination
    total_gens = 300
    period = 80
    target_pop = 80

    print(f"Starting Phase-14 sweep: {len(basal_burn_values)} burns × {len(recovery_rate_values)} rates × {len(seeds)} seeds...", flush=True)
    
    sweep_results = {}
    start_time = time.time()
    
    for bb in basal_burn_values:
        for rr in recovery_rate_values:
            key = (bb, rr)
            print(f"\n--- Basal Burn: {bb}, Recovery Rate: {rr} ---", flush=True)
            results = []
            for seed in seeds:
                print(f"Starting seed {seed}...", flush=True)
                r = run_single(seed, total_gens, period, target_pop, bb, rr)
                results.append(r)
                print(f"  Seed {seed}: ω={r['final_omega_mean']:.5f} FP={r['false_positive_rate']:.2%} min_pop={r['bottleneck_depth']:3d}")

            # Aggregate for this combination
            fp_rates = [r['false_positive_rate'] for r in results]
            bottlenecks = [r['bottleneck_depth'] for r in results]
            omega_means = [r['final_omega_mean'] for r in results]
            convergences = [r['convergence_ratio'] for r in results]
            max_winter_psis = [r['max_winter_psi'] for r in results]
            first_panic_gens = [r['first_panic_gen'] for r in results if r['first_panic_gen'] is not None]
            panic_durations = [r['panic_duration'] for r in results]

            omega_std = statistics.stdev(omega_means) if len(omega_means) > 1 else 0.0
            sweep_results[key] = {
                'omega_mean': round(statistics.mean(omega_means), 5),
                'omega_std': round(omega_std, 5),
                'fp_mean': round(statistics.mean(fp_rates), 4),
                'convergence_mean': round(statistics.mean(convergences), 4),
                'bottleneck_mean': round(statistics.mean(bottlenecks), 2),
                'max_winter_psi_mean': round(statistics.mean(max_winter_psis), 4),
                'first_panic_gen_mean': round(statistics.mean(first_panic_gens), 1) if first_panic_gens else None,
                'panic_duration_mean': round(statistics.mean(panic_durations), 1),
                'results': results
            }
            
            first_panic_str = f"{sweep_results[key]['first_panic_gen_mean']:.1f}" if sweep_results[key]['first_panic_gen_mean'] is not None else 'None'
            print(f"  Aggregate: FP={sweep_results[key]['fp_mean']:.2%} MaxWinterΨ={sweep_results[key]['max_winter_psi_mean']:.4f} PanicDur={sweep_results[key]['panic_duration_mean']:.1f} FirstPanic={first_panic_str} Conv={sweep_results[key]['convergence_mean']:.4f} Bottleneck={sweep_results[key]['bottleneck_mean']:.1f}")

    elapsed = time.time() - start_time
    print(f"\nSweep completed in {elapsed:.1f}s.")

    # Summary table
    print("\n" + "=" * 90)
    print("PHASE-14 PARAMETER SWEEP SUMMARY")
    print("=" * 90)
    print("Burn | Rate | FP %  | MaxWinterΨ | PanicDur | FirstPanic | Conv | Bottleneck")
    print("-" * 80)
    for bb in basal_burn_values:
        for rr in recovery_rate_values:
            sr = sweep_results[(bb, rr)]
            first_panic_str = f"{sr['first_panic_gen_mean']:.1f}" if sr['first_panic_gen_mean'] is not None else 'None'
            print(f" {bb:.2f} | {rr:.2f} | {sr['fp_mean']:.2%} | {sr['max_winter_psi_mean']:.4f} | {sr['panic_duration_mean']:.1f} | {first_panic_str} | {sr['convergence_mean']:.4f} | {sr['bottleneck_mean']:.1f}")

    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('phase14_artifacts', f'parameter_sweep_{stamp}')
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'sweep_summary.json'), 'w') as f:
        json.dump(sweep_results, f, indent=2)

    print(f"\nArtifacts written to: {out_dir}")

if __name__ == '__main__':
    main()
