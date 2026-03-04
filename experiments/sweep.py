import sys
sys.path.insert(0, '.')
import random
from collections import defaultdict
from mono import MonoCell
from cell.lifecycle import cycle
from core.identity import CoreIdentity
from metrics.taxonomy import classify_death, classify_stability

def mean(values):
    return sum(values) / len(values) if values else 0

def std(values):
    if not values:
        return 0
    mean_val = mean(values)
    return (sum((x - mean_val)**2 for x in values) / len(values))**0.5

# Parameter lists
decay_rates = [0.001, 0.002, 0.004, 0.008, 0.016, 0.032]
basal_burns = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0]
action_multipliers = [0.2, 0.5, 1.0, 1.5, 2.0]

# Base parameters with reproduction disabled
base_params = {
    'E_i': 10, 'E_m': 1000, 'E_s': 50, 'E_r': 10000,  # High E_r to disable reproduction
    'c_B': 0, 'c_M': 5, 'c_R': 5, 'c_K': 5, 'c_P': 20,
    'burn_weights': (0.1, 0.1, 0.1),
    'mutation_rate': 0.1,
    'initial_energy': 100, 'basal_burn': 1, 'action_cost_multiplier': 1,
    'initial_structure_size': 10, 'decay_rate': 0.05, 'split_ratio': 0.5,
    'E_quiescence': 20, 'S_quiescence': 3,
    'S_critical': 5, 'E_maintenance_min': 20, 'repair_efficiency': 0.5,
    'E_repro': 150, 'S_repro': 8, 'r': 0.4, 'C_divide': 20,
    'epsilon_E': 5, 'epsilon_S': 1, 'stability_window': 10,
    'child_survival_cycles': 10, 'birth_stress_cycles': 5,
    'regulator_alpha': 0.1, 'regulator_beta': 0.05, 'regulator_gamma': 0.5, 'regulator_mutation_rate': 0.01,
    'alpha_O': 1000.0,
    'tau_max': 1000,
    'k_coord': 0.1,
    'tau_sense': 0.1,
    'tau_signal': 0.1,
    'tau_act': 0.1,
    'latency_drift_rate': 0.01,
    'size_penalty_factor': 0.1,
    'prediction_horizon': 5.0,
    'number_of_predictive_modules': 0,
    'arbitration_delay': 1.0,
    'module_horizon_adapt_rate': 0.1,
    'global_integrator_capacity': 10.0,
    'arbitration_mechanism': 'temporal_sequencing',
    'scene_change_threshold': 50.0,
    'scene_min_duration': 5
}

results = []

for decay in decay_rates:
    for burn in basal_burns:
        for mult in action_multipliers:
            params = base_params.copy()
            params['decay_rate'] = decay
            params['basal_burn'] = burn
            params['action_cost_multiplier'] = mult
            identity = CoreIdentity(**params)

            runs_data = []
            for seed in range(5):
                random.seed(seed)
                cell = MonoCell(identity)
                logs = []
                for t in range(1000):
                    death_reason, log_entry, child = cycle(cell)
                    logs.append(log_entry)
                    if cell.energy.E <= 0 or cell.structure.size() <= 0:
                        break
                lifespan = len(logs)
                death_class = classify_death(logs)
                stability_class = classify_stability(logs)
                energies = [log['E'] for log in logs]
                structures = [log['structure_size'] for log in logs]
                energy_mean = mean(energies)
                energy_var = std(energies)**2
                structure_mean = mean(structures)
                structure_var = std(structures)**2
                runs_data.append({
                    'lifespan': lifespan,
                    'death_class': death_class,
                    'stability_class': stability_class,
                    'energy_mean': energy_mean,
                    'energy_var': energy_var,
                    'structure_mean': structure_mean,
                    'structure_var': structure_var
                })

            # Compute per config
            survival_count = sum(1 for r in runs_data if r['lifespan'] >= 500)
            survival_pct = survival_count / 5 * 100
            death_counts = defaultdict(int)
            stability_counts = defaultdict(int)
            for r in runs_data:
                if r['death_class']:
                    death_counts[r['death_class']] += 1
                if r['stability_class']:
                    stability_counts[r['stability_class']] += 1
            dominant_death = max(death_counts, key=death_counts.get) if death_counts else None
            dominant_stability = max(stability_counts, key=stability_counts.get) if stability_counts else None

            results.append({
                'decay_rate': decay,
                'basal_burn': burn,
                'action_multiplier': mult,
                'survival_pct': survival_pct,
                'dominant_death': dominant_death,
                'dominant_stability': dominant_stability,
                'runs_data': runs_data
            })

# Print the table
print("δ\tβ\tμ\tsurvival%\tdominant_death\tdominant_stability")
for r in results:
    print(f"{r['decay_rate']}\t{r['basal_burn']}\t{r['action_multiplier']}\t{r['survival_pct']}\t{r['dominant_death']}\t{r['dominant_stability']}")

# Identify key configurations
survived_500 = [r for r in results if any(run['lifespan'] >= 500 for run in r['runs_data'])]
nearly_survived = [r for r in results if any(300 <= run['lifespan'] < 500 for run in r['runs_data']) and not any(run['lifespan'] >= 500 for run in r['runs_data'])]
surprising_failures = [r for r in results if r['decay_rate'] <= 0.004 and r['basal_burn'] <= 1.0 and r['action_multiplier'] <= 0.5 and r['survival_pct'] == 0]

print("\nConfiguration with survival ≥500:")
if survived_500:
    r = survived_500[0]
    print(f"δ={r['decay_rate']}, β={r['basal_burn']}, μ={r['action_multiplier']}")

print("\nConfiguration with survival ≥300 (nearly survived):")
if nearly_survived:
    r = nearly_survived[0]
    print(f"δ={r['decay_rate']}, β={r['basal_burn']}, μ={r['action_multiplier']}")

print("\nSurprising failure (low params but no survival):")
if surprising_failures:
    r = surprising_failures[0]
    print(f"δ={r['decay_rate']}, β={r['basal_burn']}, μ={r['action_multiplier']}")
