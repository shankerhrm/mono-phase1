#!/usr/bin/env python3
"""
Experiment: Bias Amplification Failure Mode

Seed initial population with skewed architectures (80% high-module).
Track diversity over generations.
Measure: entropy of A_i in survivors.
Expected: monotonic decline in low-diversity runs.
"""

import random
import math
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
        number_of_predictive_modules=5, arbitration_delay=1.0,  # high default
        module_horizon_adapt_rate=0.1, global_integrator_capacity=10.0,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=1.0, scene_min_duration=5,
        kappa_pred=0.0,
        cog_mutation_rate=0.05, structural_mutation_rate=0.01,
        base_gating_threshold=0.5, base_arbitration_frequency=1
    )

def create_skewed_population(size, high_fraction=0.8):
    """Create population with high_fraction having high module_count."""
    cells = []
    identity = get_identity()
    for i in range(size):
        cell = MonoCell(identity)
        if random.random() < high_fraction:
            cell.module_count = 5  # high
        else:
            cell.module_count = 1  # low
        cell.predictive_modules = [{'horizon': cell.prediction_horizon, 'error': 0.0, 'weight': 1.0 / cell.module_count} for _ in range(cell.module_count)]
        cells.append(cell)
    return cells

def calculate_entropy(module_counts):
    """Shannon entropy of module_count distribution."""
    if not module_counts:
        return 0
    freq = {}
    for m in module_counts:
        freq[m] = freq.get(m, 0) + 1
    total = len(module_counts)
    entropy = 0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

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

def test_bias_amplification(total_gens=50):
    species_memory = SpeciesMemory(alpha=0.01, epsilon=0.1)
    identity = get_identity()

    cells = create_skewed_population(20, 0.8)
    entropies = []

    for gen in range(total_gens):
        organism_data = []
        cells = run_generation(cells, species_memory, identity, organism_data=organism_data)
        if not cells:
            print("Extinction.")
            return None

        # Calculate entropy of module_count in survivors
        module_counts = [cell.module_count for cell in cells]
        entropy = calculate_entropy(module_counts)
        entropies.append(entropy)

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

    avg_entropy = sum(entropies) / len(entropies)
    final_entropy = entropies[-1] if entropies else 0
    print(f"Bias Amp: Avg Entropy {avg_entropy:.3f}, Final Entropy {final_entropy:.3f}")
    return avg_entropy, final_entropy

def main():
    print(TOP_UP_POLICY)
    result = test_bias_amplification()
    print("Result:", result)

if __name__ == "__main__":
    main()
