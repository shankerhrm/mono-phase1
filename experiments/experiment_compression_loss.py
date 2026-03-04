#!/usr/bin/env python3
"""
Experiment: Compression Loss Failure Mode

Modify ϕ to drop subsets of parameters (e.g., ignore R_i or E_i).
Compare survival in mixed environments.
Measure: gating accuracy, energy efficiency.
Expected: degraded performance in cost-sensitive scenarios.
"""

import random
from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from reproduction.spawn import divide

TOP_UP_POLICY = "Phase-9 policy: TOP-UP ON (fixed-size selection microscope; survival_rate = trait viability, not ecosystem persistence)"

def get_identity(env='mixed'):
    base = CoreIdentity(
        E_i=1.0, E_m=10.0, E_s=2.0, E_r=5.0,
        c_B=0.1, c_M=0.2, c_R=0.15, c_K=0.1, c_P=1.0,
        burn_weights=(0.5, 0.3, 0.2), mutation_rate=0.05,
        initial_energy=5.0, basal_burn=0.1, action_cost_multiplier=1.0,
        initial_structure_size=5, decay_rate=0.05, split_ratio=0.5,
        E_quiescence=1.0, S_quiescence=2,
        S_critical=3, E_maintenance_min=2.0, repair_efficiency=0.8,
        E_repro=5.0, S_repro=5, r=0.5, C_divide=1.0,
        epsilon_E=0.1, epsilon_S=0.1, stability_window=5,
        child_survival_cycles=5, birth_stress_cycles=2,
        regulator_alpha=0.5, regulator_beta=0.3, regulator_gamma=0.2,
        regulator_mutation_rate=0.01,
        alpha_O=10.0, tau_max=20.0, k_coord=1.0,
        tau_sense=0.5, tau_signal=0.5, tau_act=1.0, latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=2.0,
        number_of_predictive_modules=3, arbitration_delay=1.0,
        module_horizon_adapt_rate=0.1, global_integrator_capacity=10.0,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=1.0, scene_min_duration=5,
        kappa_pred=0.0,
        cog_mutation_rate=0.05, structural_mutation_rate=0.01,
        base_gating_threshold=0.5, base_arbitration_frequency=1
    )
    return base

def run_generation(cells, species_memory, env, max_cycles=10, organism_data=None):
    surviving_cells = []
    efficiencies = []
    for cell in cells:
        # Create identity with variation for mixed
        if env == 'mixed':
            E_i = random.uniform(0.5, 1.5)
            decay_rate = random.uniform(0.03, 0.07)
            identity = CoreIdentity(
                E_i=E_i, E_m=10.0, E_s=2.0, E_r=5.0,
                c_B=0.1, c_M=0.2, c_R=0.15, c_K=0.1, c_P=1.0,
                burn_weights=(0.5, 0.3, 0.2), mutation_rate=0.05,
                initial_energy=5.0, basal_burn=0.1, action_cost_multiplier=1.0,
                initial_structure_size=5, decay_rate=decay_rate, split_ratio=0.5,
                E_quiescence=1.0, S_quiescence=2,
                S_critical=3, E_maintenance_min=2.0, repair_efficiency=0.8,
                E_repro=5.0, S_repro=5, r=0.5, C_divide=1.0,
                epsilon_E=0.1, epsilon_S=0.1, stability_window=5,
                child_survival_cycles=5, birth_stress_cycles=2,
                regulator_alpha=0.5, regulator_beta=0.3, regulator_gamma=0.2,
                regulator_mutation_rate=0.01,
                alpha_O=10.0, tau_max=20.0, k_coord=1.0,
                tau_sense=0.5, tau_signal=0.5, tau_act=1.0, latency_drift_rate=0.01,
                size_penalty_factor=0.1,
                prediction_horizon=2.0,
                number_of_predictive_modules=3, arbitration_delay=1.0,
                module_horizon_adapt_rate=0.1, global_integrator_capacity=10.0,
                arbitration_mechanism='temporal_sequencing',
                scene_change_threshold=1.0, scene_min_duration=5,
                kappa_pred=0.0,
                cog_mutation_rate=0.05, structural_mutation_rate=0.01,
                base_gating_threshold=3.0, base_arbitration_frequency=1
            )
        else:
            identity = get_identity(env)
        for _ in range(max_cycles):
            death_reason, log, _ = cycle(cell, resource_intake=identity.E_i, organism_data_list=organism_data)
            if death_reason:
                break
        if not death_reason:
            surviving_cells.append(cell)
            efficiencies.append(cell.energy.E)  # efficiency proxy
    if organism_data is not None:
        species_memory.update(organism_data)
    return surviving_cells, efficiencies

def test_drop_params(drop_list, total_gens=50):
    species_memory = SpeciesMemory(alpha=0.01, epsilon=0.1, drop_params=drop_list)

    cells = [MonoCell(get_identity()) for _ in range(20)]
    survival_rates = []
    avg_efficiencies = []

    for gen in range(total_gens):
        organism_data = []
        cells, effs = run_generation(cells, species_memory, 'mixed', organism_data=organism_data)
        if not cells:
            print(f"Drop {drop_list}: Extinction at gen {gen}.")
            return None

        survival_rate = len(cells) / 20.0
        survival_rates.append(survival_rate)
        avg_eff = sum(effs) / len(effs) if effs else 0
        avg_efficiencies.append(avg_eff)

        new_cells = []
        for parent in cells[:20]:
            can_divide = (parent.energy.E > (parent.id.C_divide + parent.id.E_s)) and (parent.structure.size() >= 2)
            if can_divide:
                child = divide(parent, species_defaults=species_memory.get_defaults())
                new_cells.append(child)
            else:
                new_cells.append(parent)
        while len(new_cells) < 20:
            new_cells.append(MonoCell(get_identity()))
        cells = new_cells[:20]

    avg_survival = sum(survival_rates) / len(survival_rates)
    avg_efficiency = sum(avg_efficiencies) / len(avg_efficiencies)
    print(f"Drop {drop_list}: Avg Survival {avg_survival:.3f}, Avg Efficiency {avg_efficiency:.3f}")
    return avg_survival, avg_efficiency

def main():
    print(TOP_UP_POLICY)
    drop_configs = [
        [],  # full
        ['energy_ceiling'],  # drop cost
        ['tau_budget'],  # drop latency
        ['gamma'],  # drop gating
        ['module_count']  # drop architecture
    ]
    results = {}
    for drop in drop_configs:
        result = test_drop_params(drop)
        results[str(drop)] = result
    print("Results:", results)

if __name__ == "__main__":
    main()
