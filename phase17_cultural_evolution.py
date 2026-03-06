"""
Phase-17: Minimal Cultural Layer Evolution Experiment

Tests if cultural knowledge persists across deaths and benefits descendants.
Tracks: learning_rate evolution, artifact usage, energy gains.
"""

import json
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell, cultural_pool
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from phase10.observer import Phase10Observer
from phase13.run_phase13 import run_generation

import reproduction.spawn as spawn

# Global environmental quality for niche construction
environmental_quality = 1.0
ENV_MIN = 0.2
ENV_MAX = 2.0
depletion_rate = 0.01
regeneration_rate = 0.005

def create_identity_for_phase17():
    base = {
        'E_i': 18.0, 'E_m': 200, 'E_s': 5, 'E_r': 1000,
        'c_B': 1, 'c_M': 2, 'c_R': 1, 'c_K': 3, 'c_P': 1,
        'burn_weights': (0.5, 0.3, 0.2), 'mutation_rate': 0.105,
        'initial_energy': 50.0, 'basal_burn': 0.5, 'action_cost_multiplier': 1,
        'initial_structure_size': 10, 'decay_rate': 0.05, 'split_ratio': 0.5,
        'E_quiescence': 5, 'S_quiescence': 5, 'S_critical': 8,
        'E_maintenance_min': 10, 'repair_efficiency': 0.8,
        'E_repro': 35.0, 'S_repro': 5, 'r': 0.1, 'C_divide': 5,
        'epsilon_E': 0.5, 'epsilon_S': 0.5, 'stability_window': 5,
        'child_survival_cycles': 5, 'birth_stress_cycles': 2,
        'regulator_alpha': 0.5, 'regulator_beta': 0.3, 'regulator_gamma': 0.2,
        'regulator_mutation_rate': 0.01, 'alpha_O': 100.0, 'tau_max': 100.0,
        'k_coord': 1.0, 'tau_sense': 0.5, 'tau_signal': 0.5, 'tau_act': 1.0,
        'latency_drift_rate': 0.01, 'size_penalty_factor': 0.1,
        'prediction_horizon': 2.0, 'number_of_predictive_modules': 2,
        'arbitration_delay': 1.0, 'module_horizon_adapt_rate': 0.1,
        'global_integrator_capacity': 10.0, 'arbitration_mechanism': 'temporal_sequencing',
        'scene_change_threshold': 0.5, 'scene_min_duration': 5,
        'kappa_pred': 0.0, 'cog_mutation_rate': 0.05, 'structural_mutation_rate': 0.01,
        'base_gating_threshold': 0.5, 'base_arbitration_frequency': 1,
        # Phase-16
        'alpha': 0.2, 'beta': 0.3,
        # Phase-17
        'learning_rate': random.uniform(0.05, 0.25),
        'teaching_efficiency': random.uniform(0.05, 0.25)
    }
    return CoreIdentity(**base)


def safe_mean(x):
    return statistics.mean(x) if x else 0.0


def safe_stdev(x):
    return statistics.stdev(x) if len(x) > 1 else 0.0


def run_generation_phase17(cells, species_memory, generation, observer):
    organism_data, surviving_cells, children = [], [], []
    deaths, repro_attempts, repro_successes, energy_sum = 0, 0, 0, 0.0
    env_params = {'E_i': 18.0, 'basal_burn': 0.5, 'alpha_O': 100.0, 'environmental_quality': environmental_quality}

    # Phase-17 Step 4: Teaching and Learning Phase with Asymmetric Cultural Mutation
    learning_cost = 3.0
    teaching_cost = 1.0
    cultural_mutation_rate = 0.3
    cultural_mutation_size = 0.1
    improvement_bias = 0.9
    artifact_min = 0.5
    artifact_max = 3.0

    naive_cells = [cell for cell in cells if cell.artifact_value is None]
    teachers = [cell for cell in cells if cell.artifact_value is not None and cell.energy.E > teaching_cost]
    taught = set()
    reproducer_artifacts = []

    teaching_events = 0
    self_learning_events = 0

    for learner in naive_cells:
        if teachers:
            teacher = random.choice(teachers)
            if random.random() < teacher.teaching_efficiency:
                teacher.energy.E -= teaching_cost
                learner.energy.E -= learning_cost * 0.5
                teaching_events += 1
                taught.add(learner)

                # Asymmetric cultural mutation
                if random.random() < cultural_mutation_rate:
                    if random.random() < improvement_bias:
                        delta = random.uniform(0, cultural_mutation_size)
                    else:
                        delta = random.uniform(-cultural_mutation_size, 0)
                    new_val = teacher.artifact_value + delta
                    new_val = max(artifact_min, min(artifact_max, new_val))
                else:
                    new_val = teacher.artifact_value

                learner.artifact_value = new_val

    # Self-learning for untaught naive
    for learner in naive_cells:
        if learner not in taught and random.random() < learner.learning_rate and learner.energy.E >= learning_cost:
            learner.energy.E -= learning_cost
            learner.artifact_value = 1.0  # baseline, no mutation
            self_learning_events += 1

    for cell in cells:
        death_reason, child = None, None
        # Run one cycle
        death_reason, log, cycle_child = cycle(
            cell, observer=observer, generation=generation,
            species_memory=species_memory, env_params=env_params,
            organism_data_list=organism_data, panic_state={"state": "CALM", "load": 0.0},
            resource_intake=env_params['E_i']
        )
        if cycle_child: 
            child = cycle_child
        if death_reason: 
            deaths += 1
        else:
            surviving_cells.append(cell)
            energy_sum += cell.energy.E
            if cycle_child:
                repro_successes += 1
                children.append(cycle_child)
                reproducer_artifacts.append(cell.artifact_value)

    # Merge survivors and children
    new_pop = surviving_cells + children

    # Cultural decay
    decay_factor = 0.999
    for cell in new_pop:
        if cell.artifact_value is not None:
            cell.artifact_value *= decay_factor
            cell.artifact_value = max(artifact_min, cell.artifact_value)

    avg_energy = energy_sum / len(surviving_cells) if surviving_cells else 0

    return new_pop, {
        'avg_energy': avg_energy,
        'repro_attempts': repro_attempts,
        'repro_successes': repro_successes,
        'deaths': deaths,
        'teaching_events': teaching_events,
        'self_learning_events': self_learning_events,
        'reproducer_artifacts': reproducer_artifacts
    }


def run_evolution(seed, total_gens=300, target_pop=100):
    random.seed(seed)

    observer = Phase10Observer(seed=seed, env='phase17_cultural')
    sm = SpeciesMemory(alpha=0.1, epsilon=0.1)

    pop = [MonoCell(create_identity_for_phase17())
           for _ in range(target_pop)]

    metrics_per_gen = []

    for gen in range(total_gens):
        observer.set_generation(gen)

        # Run generation
        pop, stats = run_generation_phase17(
            pop, sm, gen, observer
        )

        if not pop:
            print(f"EXTINCTION at gen {gen} for seed {seed}")
            break

        # Collect Phase-17 metrics
        learning_rates = [cell.learning_rate for cell in pop]
        teaching_efficiencies = [cell.teaching_efficiency for cell in pop]
        artifact_values = [cell.artifact_value for cell in pop if cell.artifact_value is not None]
        learned_count = sum(1 for cell in pop if cell.artifact_value is not None)
        avg_energy = stats['avg_energy']

        mean_artifact = safe_mean(artifact_values)
        max_artifact = max(artifact_values) if artifact_values else 0
        variance = safe_stdev(artifact_values)

        # Niche construction: update environmental quality
        global environmental_quality
        depletion = depletion_rate * max(0, mean_artifact - 1.0)
        regeneration = regeneration_rate * (1.0 - environmental_quality)
        environmental_quality += regeneration - depletion
        environmental_quality = max(ENV_MIN, min(ENV_MAX, environmental_quality))

        metrics_per_gen.append({
            'gen': gen,
            'population': len(pop),
            'avg_learning_rate': safe_mean(learning_rates),
            'avg_teaching_efficiency': safe_mean(teaching_efficiencies),
            'mean_artifact_value': mean_artifact,
            'max_artifact_value': max_artifact,
            'artifact_variance': variance,
            'learned_percent': (learned_count / len(pop)) * 100 if pop else 0,
            'avg_energy': avg_energy,
            'teaching_events': stats['teaching_events'],
            'self_learning_events': stats['self_learning_events'],
            'reproducer_artifacts': stats['reproducer_artifacts'],
            'environmental_quality': environmental_quality
        })

    all_reproducer_artifacts = [a for m in metrics_per_gen for a in m['reproducer_artifacts']]

    return {
        'seed': seed,
        'total_gens': len(metrics_per_gen),
        'metrics': metrics_per_gen,
        'final_population': len(pop) if pop else 0,
        'final_avg_learning_rate': metrics_per_gen[-1]['avg_learning_rate'] if metrics_per_gen else 0,
        'final_avg_teaching_efficiency': metrics_per_gen[-1]['avg_teaching_efficiency'] if metrics_per_gen else 0,
        'final_mean_artifact_value': metrics_per_gen[-1]['mean_artifact_value'] if metrics_per_gen else 0,
        'final_max_artifact_value': metrics_per_gen[-1]['max_artifact_value'] if metrics_per_gen else 0,
        'final_artifact_variance': metrics_per_gen[-1]['artifact_variance'] if metrics_per_gen else 0,
        'final_learned_percent': metrics_per_gen[-1]['learned_percent'] if metrics_per_gen else 0,
        'final_avg_energy': metrics_per_gen[-1]['avg_energy'] if metrics_per_gen else 0,
        'all_reproducer_artifacts': all_reproducer_artifacts
    }


def main():
    seeds = [42, 123, 456, 789, 1011]
    results = []

    for seed in seeds:
        print(f"Running seed {seed}...")
        result = run_evolution(seed)
        results.append(result)

    # Save results
    os.makedirs('phase17_artifacts', exist_ok=True)
    with open('phase17_artifacts/cultural_evolution_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Summary
    print("\n=== Phase-17 Step 6: Cultural Niche Construction Results ===")
    avg_final_learning_rates = [r['final_avg_learning_rate'] for r in results]
    avg_final_teaching_efficiencies = [r['final_avg_teaching_efficiency'] for r in results]
    avg_final_mean_artifacts = [r['final_mean_artifact_value'] for r in results]
    avg_final_max_artifacts = [r['final_max_artifact_value'] for r in results]
    avg_final_variances = [r['final_artifact_variance'] for r in results]
    avg_final_learned = [r['final_learned_percent'] for r in results]
    avg_final_energy = [r['final_avg_energy'] for r in results]

    all_reproducer_artifacts = [a for r in results for a in r['all_reproducer_artifacts'] if a is not None]
    avg_reproducer_artifact = safe_mean(all_reproducer_artifacts) if all_reproducer_artifacts else 0

    print(".4f")
    print(".4f")
    print(".4f")
    print(".4f")
    print(".4f")
    print(".1f")
    print(".2f")
    print(".4f")

    # Trajectory plots (use first seed)
    gens = results[0]['metrics']
    learning_trajectory = [m['avg_learning_rate'] for m in gens]
    teaching_trajectory = [m['avg_teaching_efficiency'] for m in gens]
    artifact_trajectory = [m['mean_artifact_value'] for m in gens]
    learned_trajectory = [m['learned_percent'] for m in gens]
    energy_trajectory = [m['avg_energy'] for m in gens]
    environmental_trajectory = [m['environmental_quality'] for m in gens]

    print(f"\nLearning Rate Trajectory (first 10 gens): {learning_trajectory[:10]}")
    print(f"Teaching Efficiency Trajectory (first 10 gens): {teaching_trajectory[:10]}")
    print(f"Mean Artifact Value Trajectory (first 10 gens): {artifact_trajectory[:10]}")
    print(f"Learned % Trajectory (first 10 gens): {learned_trajectory[:10]}")
    print(f"Energy Trajectory (first 10 gens): {energy_trajectory[:10]}")
    print(f"Environmental Quality Trajectory (first 10 gens): {environmental_trajectory[:10]}")


if __name__ == "__main__":
    main()
