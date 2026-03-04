import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from ecology.world import EcologyWorld

def run_test():
    base_id = CoreIdentity(
        E_i=20.0, E_m=200.0, E_s=5, E_r=1000,
        c_B=1, c_M=2, c_R=1, c_K=3, c_P=1.0,
        burn_weights=(0.5, 0.3, 0.2), mutation_rate=0.1,
        initial_energy=100.0, basal_burn=0.5, action_cost_multiplier=1,
        initial_structure_size=10, decay_rate=0.05, split_ratio=0.5,
        E_quiescence=5, S_quiescence=5, S_critical=8,
        E_maintenance_min=5, repair_efficiency=0.8,
        E_repro=120, S_repro=8, r=0.5, C_divide=10.0,
        epsilon_E=50, epsilon_S=10, stability_window=10,
        child_survival_cycles=20, birth_stress_cycles=5,
        regulator_alpha=0.1, regulator_beta=1.0, regulator_gamma=0.3,
        regulator_mutation_rate=0.01, alpha_O=1000.0, tau_max=1000,
        k_coord=0.1, tau_sense=0.1, tau_signal=0.1, tau_act=0.1,
        latency_drift_rate=0.01, size_penalty_factor=0.1,
        prediction_horizon=10.0, number_of_predictive_modules=3,
        arbitration_delay=1.0, module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10, arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=50.0, scene_min_duration=5, kappa_pred=0.5,
        cog_mutation_rate=0.1, structural_mutation_rate=0.05,
        base_gating_threshold=0.5, base_arbitration_frequency=1
    )
    
    world = EcologyWorld(num_zones=1, max_resources_per_zone=500.0, regen_rate=40.0)
    cell = MonoCell(base_id)
    world.add_organism(cell)

    for i in range(4001):
        survivors, children = world.tick()
        for child in children:
            world.add_organism(child)
        pop = sum(len(z.organisms) for z in world.zones)
        if pop == 0:
            print(f"Cycle {i} EXTINCT")
            break
        if i % 50 == 0:
            avg_ph = sum(c.prediction_horizon for c in world.zones[0].organisms) / pop
            print(f"Cycle {i}: Pop {pop}, Avg PH: {avg_ph:.2f}")

run_test()
