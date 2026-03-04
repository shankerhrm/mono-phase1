"""
Phase-13: run_phase13.py — Oscillatory Validation Experiment

Validation of emergent temporal entrainment in periodic environments.
Demonstrates successful ω convergence (~0.14) with high convergence ratios (0.88-0.92)
but FP rate saturates at 75% due to PanicController hysteresis.

Key Results:
- Entrainment mechanism works: ω narrows from uniform to ~0.14 rad/gen
- Hysteresis prevents FP target: panic persists into summer causing 75% FP
- Sharp ecological transition at basal_burn ≈ 0.8 (extinction vs chronic panic)
- Phase clustering achieved despite high stress levels
"""

import os
import sys
import json
import time
import math
import random
import statistics
import argparse
from datetime import datetime

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from phase10.observer import Phase10Observer
from phase12.stress_index import CompositeStressIndex
from phase12.panic_controller import PanicController
from phase13.oscillator import population_omega_stats, population_phase_histogram

def create_identity_for_env(env_type):
    base = {
        'E_i': 10, # Base value
        'E_m': 200, 'E_s': 5, 'E_r': 1000,
        'c_B': 1, 'c_M': 2, 'c_R': 1, 'c_K': 3, 'c_P': 1,
        'burn_weights': (0.5, 0.3, 0.2), 'mutation_rate': 0.105,
        'initial_energy': 120, 'basal_burn': 0, 'action_cost_multiplier': 1,
        'initial_structure_size': 10, 'decay_rate': 0.05, 'split_ratio': 0.5,
        'E_quiescence': 5, 'S_quiescence': 5, 'S_critical': 8,
        'E_maintenance_min': 10, 'repair_efficiency': 0.8,
        'E_repro': 130, 'S_repro': 5, 'r': 0.1, 'C_divide': 5,
        'epsilon_E': 2, 'epsilon_S': 1, 'stability_window': 10,
        'child_survival_cycles': 20, 'birth_stress_cycles': 5,
        'regulator_alpha': 0.1, 'regulator_beta': 0.2, 'regulator_gamma': 0.3,
        'regulator_mutation_rate': 0.01, 'alpha_O': 1000.0, 'tau_max': 1000,
        'k_coord': 0.1, 'tau_sense': 0.1, 'tau_signal': 0.1, 'tau_act': 0.1,
        'latency_drift_rate': 0.01, 'size_penalty_factor': 0.1,
        'prediction_horizon': 10.0, 'number_of_predictive_modules': 3,
        'arbitration_delay': 1.0, 'module_horizon_adapt_rate': 0.1,
        'global_integrator_capacity': 10.0, 'kappa_pred': 0.5,
        'cog_mutation_rate': 0.1, 'structural_mutation_rate': 0.02,
        'base_gating_threshold': 0.5, 'base_arbitration_frequency': 1,
        'arbitration_mechanism': 'temporal_sequencing',
        'scene_change_threshold': 2.0,
        'scene_min_duration': 3,
    }
    if env_type == 'A':
        base.update({'E_i': 35, 'alpha_O': 2000.0, 'k_coord': 0.5})
    elif env_type == 'B':
        base.update({'E_i': 0.1, 'basal_burn': 2.2, 'alpha_O': 10.0, 'initial_energy': 120, 'E_repro': 130})
    return CoreIdentity(**base)

def get_env_params(env_type, basal_burn=1.0):
    if env_type == 'A':
        return {'E_i': 35.0, 'basal_burn': 0.0, 'alpha_O': 2000.0}
    else:
        return {'E_i': 0.5, 'basal_burn': basal_burn, 'alpha_O': 10.0}

def run_generation(cells, species_memory, generation, observer, env_type, max_cycles=50, panic_state=None, basal_burn=1.0):
    organism_data, surviving_cells, children = [], [], []
    deaths, repro_attempts, repro_successes, energy_sum = 0, 0, 0, 0.0
    env_params = get_env_params(env_type, basal_burn)

    for cell in cells:
        death_reason, child = None, None
        for cycle_num in range(max_cycles):
            death_reason, log, cycle_child = cycle(
                cell, observer=observer, generation=generation,
                species_memory=species_memory, env_params=env_params,
                organism_data_list=organism_data, panic_state=panic_state,
                resource_intake=env_params['E_i']
            )
            if cycle_child: child = cycle_child
            if death_reason: 
                deaths += 1
                break
        if not death_reason:
            surviving_cells.append(cell)
            energy_sum += cell.energy.E
        if child:
            children.append(child)
            repro_successes += 1
        if cell.reproduction_eligible:
            repro_attempts += 1

    surviving_cells.extend(children)
    species_memory.update(organism_data)
    
    stats = {
        'avg_energy': energy_sum / max(len(surviving_cells), 1),
        'deaths': deaths, 'population_size': len(cells),
        'survivors': len(surviving_cells), 'repro_attempts': repro_attempts,
        'repro_successes': repro_successes, 'basal_burn': env_params.get('basal_burn', 0.0),
        'ms_gamma': species_memory.Ms.get('gamma', 0.5),
        'gamma_variance': statistics.variance([c.gating_threshold for c in surviving_cells]) if len(surviving_cells) >= 2 else 0.001
    }
    return surviving_cells, stats

def backfill_population(surviving_cells, target_pop, env_type):
    if not surviving_cells:
        return [MonoCell(create_identity_for_env(env_type)) for _ in range(target_pop)]
    if len(surviving_cells) > target_pop:
        return random.sample(surviving_cells, target_pop)
    new_cells = surviving_cells.copy()
    while len(new_cells) < target_pop:
        parent = random.choice(surviving_cells)
        child = MonoCell(parent.id)
        child.gating_threshold = parent.gating_threshold
        child.oscillator = parent.oscillator.make_child_oscillator()
        new_cells.append(child)
    return new_cells

def run_phase13(args):
    random.seed(args.seed)
    observer = Phase10Observer(seed=args.seed, env='phase13_control')
    species_memory = SpeciesMemory(alpha=0.1, epsilon=0.1)
    stress_index, panic_controller = CompositeStressIndex(), PanicController()
    population = [MonoCell(create_identity_for_env('A')) for _ in range(args.target_pop)]
    history, total_calm_gens, false_positives = [], 0, 0
    
    print(f"Phase-13 Control: Seed={args.seed}, Period={args.period}, TargetPop={args.target_pop}")

    for gen in range(args.generations):
        env_type = 'B' if (gen % args.period) / args.period >= 0.5 else 'A'
        observer.set_generation(gen)
        panic_output = panic_controller.get_outputs(stress_index.psi)
        
        population, stats = run_generation(population, species_memory, gen, observer, env_type, panic_state=panic_output)
        psi = stress_index.update(
            avg_energy=stats['avg_energy'], basal_burn=stats['basal_burn'],
            repro_attempts=stats['repro_attempts'], repro_successes=stats['repro_successes'],
            deaths=stats['deaths'], population_size=stats['population_size'],
            gamma_variance=stats['gamma_variance']
        )
        panic_output = panic_controller.update(psi, generation=gen)
        
        if env_type == 'A':
            total_calm_gens += 1
            if panic_output['state'] != 'CALM': false_positives += 1
        
        omega_stats = population_omega_stats(population)
        if gen % 50 == 0:
            print(f"Gen {gen:4d} [{env_type}] | Ψ={psi:.3f} | ω_mean={omega_stats['mean']:.5f} | Pop={len(population)} Ms.γ={stats['ms_gamma']:.4f}")

        population = backfill_population(population, args.target_pop, env_type)
        history.append({'gen': gen, 'psi': psi, 'omega_stats': omega_stats})

    # Saving artifacts logic...
    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('phase13_artifacts', f'control_seed{args.seed}_{stamp}')
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'summary.json'), 'w') as f:
        json.dump({'seed': args.seed, 'omega_mean': history[-1]['omega_stats']['mean'], 'fp_rate': false_positives/max(1, total_calm_gens)}, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--generations', type=int, default=1000)
    parser.add_argument('--period', type=int, default=80)
    parser.add_argument('--target-pop', type=int, default=100)
    run_phase13(parser.parse_args())
