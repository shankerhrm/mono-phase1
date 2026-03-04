#!/usr/bin/env python3
"""
Experiment: Under-Adaptation Failure Mode

Oscillate environment every 50 generations (stable ↔ shock).
Vary α (0.001 to 0.1).
Measure: correlation between Ms(t) and current environment survival.
Expected: low α shows persistent lag in module pruning.
"""

import random
from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from reproduction.spawn import divide

TOP_UP_POLICY = "Phase-9 policy: TOP-UP ON (fixed-size selection microscope; survival_rate = trait viability, not ecosystem persistence)"

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
        base_gating_threshold=3.0, base_arbitration_frequency=1
    )
    return base

def run_generation(cells, species_memory, identity, max_cycles=10, organism_data=None):
    surviving_cells = []
    for cell in cells:
        death_reason = None
        for _ in range(max_cycles):
            death_reason, log, _ = cycle(
                cell,
                resource_intake=identity.E_i,
                organism_data_list=organism_data,
            )
            if death_reason:
                break
        if not death_reason:
            surviving_cells.append(cell)
    if organism_data is not None:
        species_memory.update(organism_data)
    return surviving_cells

def test_alpha(alpha_value, total_gens=200, switch_every=50):
    species_memory = SpeciesMemory(alpha=alpha_value, epsilon=0.1)
    identity_stable = get_identity_for_environment('stable')
    identity_shock = get_identity_for_environment('shock')

    cells = [MonoCell(identity_stable) for _ in range(20)]
    correlations = []
    module_counts = []

    for gen in range(total_gens):
        env = 'shock' if (gen // switch_every) % 2 == 1 else 'stable'
        identity = identity_shock if env == 'shock' else identity_stable

        organism_data = []
        cells = run_generation(cells, species_memory, identity, organism_data=organism_data)
        if not cells:
            print(f"Alpha {alpha_value}: Extinction at gen {gen}.")
            return None

        new_cells = []
        for parent in cells[:20]:
            can_divide = (parent.energy.E > (parent.id.C_divide + parent.id.E_s)) and (parent.structure.size() >= 2)
            if can_divide:
                child = divide(parent, species_defaults=species_memory.get_defaults())
                new_cells.append(child)
            else:
                new_cells.append(parent)
        while len(new_cells) < 20:
            new_cells.append(MonoCell(identity))
        cells = new_cells[:20]

        # Measure correlation: simplified as survival rate vs expected module_count for env
        # Expected: lower module_count in stable
        survival_rate = len(cells) / 20.0
        expected_module = 2.0 if env == 'stable' else 4.0  # arbitrary
        actual_module = species_memory.Ms['module_count']
        correlation = 1.0 - abs(actual_module - expected_module) / expected_module  # simple proxy
        correlations.append(correlation)
        module_counts.append(actual_module)

    avg_correlation = sum(correlations) / len(correlations)
    print(f"Alpha {alpha_value}: Avg Correlation {avg_correlation:.3f}, Final Module Count {species_memory.Ms['module_count']:.1f}")
    return avg_correlation

def main():
    print(TOP_UP_POLICY)
    alphas = [0.001, 0.01, 0.05, 0.1]
    results = {}
    for alpha in alphas:
        result = test_alpha(alpha)
        results[alpha] = result
    print("Results:", results)

if __name__ == "__main__":
    main()
