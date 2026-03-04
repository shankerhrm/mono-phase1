import json
import os
import random
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from reproduction.spawn import divide
from phase10.observer import Phase10Observer

def create_identity_for_env(env_type: str, mutation_rate=None):
    base = {
        'E_m': 200,
        'E_s': 5,
        'E_r': 1000,
        'c_B': 1,
        'c_M': 2,
        'c_R': 1,
        'c_K': 3,
        'c_P': 1,
        'burn_weights': (0.5, 0.3, 0.2),
        'mutation_rate': mutation_rate if mutation_rate is not None else 0.105,  # Increased by 5% for entropy floor
        'initial_energy': 50,  # Reduced for vacuum stress
        'basal_burn': 0,
        'action_cost_multiplier': 1,
        'initial_structure_size': 10,
        'decay_rate': 0.05,
        'split_ratio': 0.5,
        'E_quiescence': 5,
        'S_quiescence': 5,
        'S_critical': 8,
        'E_maintenance_min': 10,
        'repair_efficiency': 0.8,
        'E_repro': 60,
        'S_repro': 5,
        'r': 0.1,
        'C_divide': 5,
        'epsilon_E': 2,
        'epsilon_S': 1,
        'stability_window': 10,
        'child_survival_cycles': 20,
        'birth_stress_cycles': 5,
        'regulator_alpha': 0.1,
        'regulator_beta': 0.2,
        'regulator_gamma': 0.3,
        'regulator_mutation_rate': 0.01,
        'alpha_O': 1000.0,
        'tau_max': 1000,
        'k_coord': 0.1,
        'tau_sense': 0.1,
        'tau_signal': 0.1,
        'tau_act': 0.1,
        'latency_drift_rate': 0.01,
        'size_penalty_factor': 0.1,
        'prediction_horizon': 10.0,
        'number_of_predictive_modules': 3,
        'arbitration_delay': 1.0,
        'module_horizon_adapt_rate': 0.1,
        'global_integrator_capacity': 10.0,
        'arbitration_mechanism': 'temporal_sequencing',
        'scene_change_threshold': 2.0,
        'scene_min_duration': 3,
        'kappa_pred': 0.5,
        'cog_mutation_rate': 0.1,
        'structural_mutation_rate': 0.02,
        'base_gating_threshold': 0.5,
        'base_arbitration_frequency': 1,
    }

    if env_type == 'A':  # High energy, high latency
        base.update({
            'E_i': 30,  # High energy
            'alpha_O': 2000.0,  # High latency
            'k_coord': 0.5,
        })
    elif env_type == 'B':  # Vacuum Test - Phase-11
        base.update({
            'E_i': 0.1,  # Scarcity (P_intake)
            'basal_burn': 2.0,  # High burn
            'alpha_O': 0.5,  # Aggressive failure latency
            'k_coord': 0.001,  # Fragile coordination
            'initial_energy': 150.0,  # Realistic runway
            'E_repro': 100,  # High wealth requirement
        })

    return CoreIdentity(**base)

def run_generation(cells, species_memory, generation, observer, max_cycles=50):
    organism_data = []
    surviving_cells = []
    env = 'A' if generation < 500 else 'B'
    env_params = {
        'E_i': 30.0 if env == 'A' else 0.1,
        'basal_burn': 0.0 if env == 'A' else 2.0,
        'alpha_O': 2000.0 if env == 'A' else 0.5
    }
    for cell in cells:
        for cycle_num in range(max_cycles):
            death_reason, log, child = cycle(cell, observer=observer, species_defaults={'__observer__': observer}, generation=generation, species_memory=species_memory, env_params=env_params, organism_data_list=organism_data)
            if death_reason:
                break
        if not death_reason:
            surviving_cells.append(cell)
        if child:
            surviving_cells.append(child)
    species_memory.update(organism_data)
    observer.emit_lineage_drift_violations()
    return surviving_cells

def create_next_generation(surviving_cells, species_memory, target_pop=50, safeguard=False):
    new_cells = surviving_cells.copy()
    while len(new_cells) < target_pop:
        env = 'A' if len(surviving_cells) > 0 else 'B'
        mutation_rate = 0.20 if env == 'B' else None
        fresh_id = create_identity_for_env(env, mutation_rate=mutation_rate)
        fresh_cell = MonoCell(fresh_id)
        fresh_cell.lineage_id = str(random.randint(1000,9999))
        # Mutate fresh cells to introduce variation
        if env == 'B':
            cog_mut_rate = mutation_rate
            fresh_cell.prediction_horizon = max(0.0, fresh_cell.prediction_horizon + random.gauss(0, cog_mut_rate * 2))
            fresh_cell.scene_threshold = max(0.01, fresh_cell.scene_threshold + random.gauss(0, cog_mut_rate))
            fresh_cell.gating_threshold = max(0.0, min(1.0, fresh_cell.gating_threshold + random.gauss(-0.1, cog_mut_rate)))
            if random.random() < cog_mut_rate:
                fresh_cell.arbitration_frequency = max(1, fresh_cell.arbitration_frequency + random.choice([-1, 1]))
            if random.random() < fresh_id.structural_mutation_rate:
                fresh_cell.module_count = max(0, fresh_cell.module_count + random.choice([-1, 1]))
            fresh_cell.predictive_modules = [
                {'horizon': fresh_cell.prediction_horizon, 'error': 0.0, 'weight': 1.0 / max(1, fresh_cell.module_count)}
                for _ in range(fresh_cell.module_count)
            ]
        new_cells.append(fresh_cell)
    return new_cells

def run_regime_flip(seed=42, generations_a=500, generations_b=250, target_pop=50):
    random.seed(seed)
    observer = Phase10Observer(seed=seed, env='regime_flip')
    low_pop_gens = 0  # For dynamic entropy floor

    # Initialize Species Memory with higher alpha for faster adaptation
    species_memory = SpeciesMemory(alpha=0.1, epsilon=0.1)

    # Start in Environment A
    initial_id = create_identity_for_env('A')
    population = [MonoCell(initial_id) for _ in range(target_pop)]

    history = []

    # Phase A: Long Calm
    for gen in range(generations_a):
        observer.set_generation(gen)
        population = run_generation(population, species_memory, gen, observer)
        survival_rate = len(population) / target_pop
        population = create_next_generation(population, species_memory, target_pop)
        history.append({
            'generation': gen,
            'env': 'A',
            'Ms': species_memory.Ms.copy(),
            'survival_rate': survival_rate,
            'avg_tau': sum(c.get_tau_organism() for c in population) / len(population) if population else 0,
            'population_size': len(population)
        })
        if gen % 50 == 0:
            print(f"A Gen {gen}: Survival {survival_rate:.2f}, Ms gamma: {species_memory.Ms.get('gamma', 0):.3f}")

    # Phase B: Flash Shift
    for gen in range(generations_a, generations_a + generations_b):
        observer.set_generation(gen)
        population = run_generation(population, species_memory, gen, observer)
        survival_rate = len(population) / target_pop
        if survival_rate < 0.1:
            low_pop_gens += 1
        else:
            low_pop_gens = 0
        population = create_next_generation(population, species_memory, target_pop, safeguard=(low_pop_gens >= 5))
    # Update Ms with fresh cells' gamma for Founder Effect
    for cell in population:
        if hasattr(cell, 'gating_threshold'):
            gamma_i = cell.gating_threshold
            species_memory.update([(0, 0, gamma_i, {}, 0, 0)])
        history.append({
            'generation': gen,
            'env': 'B',
            'Ms': species_memory.Ms.copy(),
            'survival_rate': survival_rate,
            'avg_tau': sum(c.get_tau_organism() for c in population) / len(population) if population else 0,
            'population_size': len(population)
        })
        if gen % 50 == 0:
            print(f"B Gen {gen}: Survival {survival_rate:.2f}, Ms gamma: {species_memory.Ms.get('gamma', 0):.3f}")

    # Output artifacts
    from phase10.run_phase10 import build_artifacts
    build_artifacts([observer], 'regime_flip_artifacts')

    with open('regime_flip_history.json', 'w') as f:
        json.dump(history, f, indent=2)

    print("Regime flip experiment completed. Artifacts in regime_flip_artifacts/")

if __name__ == "__main__":
    run_regime_flip()
