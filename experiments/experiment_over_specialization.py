#!/usr/bin/env python3
"""
Experiment: Over-Specialization Failure Mode

Run stable environment for 100 generations to converge Ms.
Abruptly shift to shock regime (high resource variance).
Measure: survival drop, cognition re-emergence delay, Γ relaxation time.
Expected: initial failure if lock-in occurs.
"""

import random
from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from reproduction.spawn import divide

def get_identity_for_environment(env='stable'):
    """Return CoreIdentity adjusted for environment."""
    decay = 0.2 if env == 'shock' else 0.05
    E_i = 0.5 if env == 'shock' else 1.0
    drift = 0.05 if env == 'shock' else 0.01
    base = CoreIdentity(
        E_i=E_i, E_m=10.0, E_s=2.0, E_r=5.0,
        c_B=0.1, c_M=0.2, c_R=0.15, c_K=0.1, c_P=1.0,
        burn_weights=(0.5, 0.3, 0.2), mutation_rate=0.05,
        initial_energy=5.0, basal_burn=0.1, action_cost_multiplier=1.0,
        initial_structure_size=5, decay_rate=decay, split_ratio=0.5,
        E_quiescence=1.0, S_quiescence=2,
        S_critical=3, E_maintenance_min=2.0, repair_efficiency=0.8,
        E_repro=5.0, S_repro=5, r=0.5, C_divide=1.0,
        epsilon_E=0.1, epsilon_S=0.1, stability_window=5,
        child_survival_cycles=5, birth_stress_cycles=2,
        regulator_alpha=0.5, regulator_beta=0.3, regulator_gamma=0.2,
        regulator_mutation_rate=0.01,
        alpha_O=10.0, tau_max=20.0, k_coord=1.0,
        tau_sense=0.5, tau_signal=0.5, tau_act=1.0, latency_drift_rate=drift,
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

def main():
    species_memory = SpeciesMemory(alpha=0.01, epsilon=0.1)
    identity_stable = get_identity_for_environment('stable')
    identity_shock = get_identity_for_environment('shock')

    # Phase 1: Stable environment for 100 generations
    cells = [MonoCell(identity_stable) for _ in range(20)]
    for gen in range(100):
        organism_data = []
        cells = run_generation(cells, species_memory, identity_stable, organism_data=organism_data)
        if not cells:
            print("Extinction in stable phase.")
            return
        # Spawn next gen
        new_cells = []
        for parent in cells[:20]:  # limit population
            child = divide(parent, species_defaults=species_memory.get_defaults())
            new_cells.append(child)
        cells = new_cells
        print(f"Stable Gen {gen}: {len(cells)} cells, Gamma: {species_memory.Ms['gamma']:.3f}")

    # Phase 2: Shock environment for 50 generations
    print("Switching to shock environment.")
    initial_gamma = species_memory.Ms['gamma']
    for gen in range(50):
        organism_data = []
        cells = run_generation(cells, species_memory, identity_shock, organism_data=organism_data)
        if not cells:
            print(f"Extinction at shock gen {gen}.")
            return
        new_cells = []
        for parent in cells[:20]:
            child = divide(parent, species_defaults=species_memory.get_defaults())
            new_cells.append(child)
        cells = new_cells
        current_gamma = species_memory.Ms['gamma']
        print(f"Shock Gen {gen}: {len(cells)} cells, Gamma: {current_gamma:.3f}")
        if current_gamma < initial_gamma * 0.9:  # arbitrary re-emergence threshold
            print(f"Cognition re-emerged at gen {gen}")
            break

if __name__ == "__main__":
    main()
