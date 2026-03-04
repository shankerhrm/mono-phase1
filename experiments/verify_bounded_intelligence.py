import sys
import os
import random
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ecology.world import EcologyWorld
from mono import MonoCell
from core.identity import CoreIdentity

def verify_bounded_intelligence():
    print("--- Generating Bounded Intelligence Verification Logs ---")
    
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
    
    # Large world, limited regen to force competition
    world = EcologyWorld(num_zones=20, max_resources_per_zone=200.0, regen_rate=15.0)
    
    # Seed population with polar phenotypes: "Smart" (high cost) and "Lean" (low cost)
    for i in range(25):
        # Lean phenotype
        cell = MonoCell(base_id)
        cell.module_count = 0
        cell.gating_threshold = 2.0
        world.add_organism(cell)
        
    for i in range(25):
        # "Smart" phenotype (high overhead)
        cell = MonoCell(base_id)
        cell.module_count = 5
        cell.gating_threshold = 0.1
        world.add_organism(cell)
        
    death_stats = {"lean": 0, "smart": 0}
    
    print(f"Cycle | Lean Pop | Smart Pop | Lean Deaths | Smart Deaths")
    
    for t in range(301):
        survivors, children = world.tick()
        for child in children:
            world.add_organism(child)
            
        # Count current pops
        all_cells = [c for z in world.zones for c in z.organisms]
        lean_count = len([c for c in all_cells if c.module_count <= 1])
        smart_count = len([c for c in all_cells if c.module_count >= 4])
        
        # We also need to capture deaths from the world (which doesn't return them directly in a categorized way)
        # But we can infer population collapse.
        
        if t % 50 == 0:
            print(f"{t:5} | {lean_count:8} | {smart_count:9} | N/A | N/A")
            
    print("\nFinal Verification Log:")
    print(f"Survivors: {len(all_cells)}")
    print(f"Lean Ratio: {lean_count/max(1, len(all_cells)):.2%}")
    print(f"Smart Ratio: {smart_count/max(1, len(all_cells)):.2%}")
    
    if lean_count > smart_count:
        print("\nCONCLUSION: Bounded intelligence confirmed. High-overhead cognitive phenotypes were outcompeted.")
    else:
        print("\nCONCLUSION: Inconclusive or unexpected dominance.")

if __name__ == "__main__":
    verify_bounded_intelligence()
