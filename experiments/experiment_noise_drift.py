#!/usr/bin/env python3
"""
Experiment: Noise-Induced Drift Failure Mode

Introduce survival noise (20% random flips) and reduce population size (N=10 vs N=100).
Measure: Var(Ms) over time, false positive correlations (e.g., τ vs irrelevant parameters).
Expected: drift in low-N runs.
"""

import random
from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from reproduction.spawn import divide

TOP_UP_POLICY = "Phase-9 policy: TOP-UP ON (fixed-size selection microscope; survival_rate = trait viability, not ecosystem persistence)"

def get_identity():
    return CoreIdentity(
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
        base_gating_threshold=3.0, base_arbitration_frequency=1
    )

def run_generation(cells, species_memory, identity, max_cycles=10, organism_data=None):
    surviving_cells = []
    for cell in cells:
        for _ in range(max_cycles):
            death_reason, log, _ = cycle(cell, resource_intake=identity.E_i, organism_data_list=organism_data)
            if death_reason:
                break
        if not death_reason:
            surviving_cells.append(cell)
    if organism_data is not None:
        species_memory.update(organism_data)
    return surviving_cells

def test_population_and_noise(pop_size, noise_rate, total_gens=100):
    species_memory = SpeciesMemory(alpha=0.01, epsilon=0.1, noise_rate=noise_rate)
    identity = get_identity()

    cells = [MonoCell(identity) for _ in range(pop_size)]
    variances = []
    correlations = []  # e.g., gamma vs tau_budget (should be uncorrelated)

    for gen in range(total_gens):
        organism_data = []
        cells = run_generation(cells, species_memory, identity, organism_data=organism_data)
        if not cells:
            print(f"Pop {pop_size}, Noise {noise_rate}: Extinction at gen {gen}.")
            return None

        new_cells = []
        for parent in cells[:pop_size]:
            can_divide = (parent.energy.E > (parent.id.C_divide + parent.id.E_s)) and (parent.structure.size() >= 2)
            if can_divide:
                child = divide(parent, species_defaults=species_memory.get_defaults())
                new_cells.append(child)
            else:
                new_cells.append(parent)
        while len(new_cells) < pop_size:
            new_cells.append(MonoCell(identity))
        cells = new_cells[:pop_size]

        # Measure variance
        var = species_memory.get_variance()
        variances.append(var)

        # False correlation: correlation between gamma and tau_budget
        # Simplified: collect pairs
        gammas = [x[2] for x in organism_data if x[5] == 1]  # gamma for survivors
        taus = [x[0] for x in organism_data if x[5] == 1]  # tau
        if len(gammas) > 1:
            corr = sum((g - sum(gammas)/len(gammas)) * (t - sum(taus)/len(taus)) for g, t in zip(gammas, taus)) / len(gammas)
            correlations.append(corr)
        else:
            correlations.append(0)

    avg_var = sum(variances) / len(variances) if variances else 0
    avg_corr = sum(correlations) / len(correlations) if correlations else 0
    print(f"Pop {pop_size}, Noise {noise_rate}: Avg Var {avg_var:.3f}, Avg False Corr {avg_corr:.3f}")
    return avg_var, avg_corr

def main():
    print(TOP_UP_POLICY)
    configs = [
        (100, 0.0),  # control: large pop, no noise
        (10, 0.0),   # small pop, no noise
        (100, 0.2),  # large pop, noise
        (10, 0.2)    # small pop, noise
    ]
    results = {}
    for pop, noise in configs:
        result = test_population_and_noise(pop, noise)
        results[(pop, noise)] = result
    print("Results:", results)

if __name__ == "__main__":
    main()
