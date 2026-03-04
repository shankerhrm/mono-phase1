import sys
import os
import random
import json
import math

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from ecology.world import EcologyWorld

def run_pathology_test(pathology, environment='stable', cycles=300):
    print(f"--- Running Pathology: {pathology} | Env: {environment} ---")
    
    base_id = CoreIdentity(
        E_i=20.0, E_m=200.0, E_s=5, E_r=1000,
        c_B=1, c_M=2, c_R=1, c_K=3, c_P=1.0,
        burn_weights=(0.5, 0.3, 0.2), mutation_rate=0.0,
        initial_energy=150.0, basal_burn=0.5, action_cost_multiplier=1,
        initial_structure_size=10, decay_rate=0.05, split_ratio=0.5,
        E_quiescence=5, S_quiescence=5, S_critical=8,
        E_maintenance_min=5, repair_efficiency=0.8,
        E_repro=120, S_repro=8, r=0.5, C_divide=10.0,
        epsilon_E=50, epsilon_S=10, stability_window=10,
        child_survival_cycles=20, birth_stress_cycles=5,
        regulator_alpha=0.1, regulator_beta=1.0, regulator_gamma=0.3,
        regulator_mutation_rate=0.01, alpha_O=1000.0, tau_max=1000,
        k_coord=0.1, tau_sense=0.1, tau_signal=0.1, tau_act=0.1,
        latency_drift_rate=0.01, size_penalty_factor=0.2,
        prediction_horizon=20.0, number_of_predictive_modules=3,
        arbitration_delay=1.0, module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10, arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=50.0, scene_min_duration=5, kappa_pred=0.5,
        cog_mutation_rate=0.0, structural_mutation_rate=0.0,
        base_gating_threshold=0.5, base_arbitration_frequency=1
    )
    
    # Initialize organism with pathology
    cell = MonoCell(base_id)
    cell.gating_pathology = pathology
    
    # For competitive, use EcologyWorld
    if environment == 'competitive':
        world = EcologyWorld(num_zones=1, max_resources_per_zone=100.0, regen_rate=5.0)
        world.add_organism(cell)
        # Add a "Lean" competitor to force exclusion
        competitor = MonoCell(base_id)
        competitor.module_count = 0
        competitor.gating_threshold = 2.0
        world.add_organism(competitor)
    
    logs = []
    deaths = 0
    total_active = 0
    
    for t in range(cycles):
        # Environment specific damage/resources
        res_intake = base_id.E_i
        res_struct = 0.0
        
        if environment == 'shock' and t % 50 == 0 and t > 0:
            res_struct = -8.0 # sudden damage
            
        if environment == 'competitive':
            survivors, children = world.tick()
            # Find our cell in survivors
            found = False
            for s in survivors:
                if s.cell_id == cell.cell_id:
                    cell = s
                    found = True
                    break
            if not found:
                deaths += 1
                break
            # Use last log from cell history
            logs.append(cell.history[-1])
        else:
            death, log = cycle(cell, resource_intake=res_intake, resource_structure=res_struct)
            logs.append(log)
            if death:
                deaths += 1
                break
                
    # Calculate Metrics
    car = sum(1 for l in logs if l.get('cognitive_active', False)) / max(1, len(logs))
    
    # GER: Damage avoided per metabolic unit
    # Simplified: (Integrated Viability) / (Total Energy Spent)
    total_viability = sum(l.get('viability', 0) for l in logs)
    total_burn = sum(l.get('burn', 0) for l in logs)
    ger = total_viability / max(1, total_burn)
    
    # LMU: Latency margin at thought-onset
    # Mean (tau_failure - tau_org) when cognitive_active == True
    margins = [l['tau_failure'] - l['tau_organism'] for l in logs if l.get('cognitive_active', False)]
    lmu = sum(margins) / len(margins) if margins else 0.0
    
    print(f"RESULTS | Survival: {len(logs)} steps | CAR: {car:.2%} | GER: {ger:.4f} | LMU: {lmu:.2f}")
    
    return {
        "pathology": pathology,
        "environment": environment,
        "survival_steps": len(logs),
        "car": car,
        "ger": ger,
        "lmu": lmu
    }

def run_matrix():
    pathologies = ['hyper', 'hypo', 'oscillatory', 'late', 'none']
    environments = ['stable', 'shock', 'competitive']
    
    results = []
    for env in environments:
        for path in pathologies:
            res = run_pathology_test(path, env)
            results.append(res)
            
    with open("phase7_1_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\nBatch Complete. Results saved to phase7_1_results.json")

if __name__ == "__main__":
    run_matrix()
