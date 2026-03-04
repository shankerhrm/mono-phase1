import sys
import os
import json
import random

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from ecology.world import EcologyWorld

def run_ecology(cycles=3000, num_zones=50, max_res=500.0, regen=40.0, initial_pop=50):
    print(f"--- Starting Phase-8 Ecology Simulation ---")
    
    # Base prior setup
    base_id = CoreIdentity(
        E_i=20.0, E_m=200.0, E_s=5, E_r=1000,
        c_B=1, c_M=2, c_R=1, c_K=3, c_P=1.0,
        burn_weights=(0.5, 0.3, 0.2),
        mutation_rate=0.1,
        initial_energy=100.0,
        basal_burn=0.5,
        action_cost_multiplier=1,
        initial_structure_size=10,
        decay_rate=0.05,
        split_ratio=0.5,
        E_quiescence=5,
        S_quiescence=5,
        S_critical=8,
        E_maintenance_min=5,
        repair_efficiency=0.8,
        E_repro=120,
        S_repro=8,
        r=0.5,
        C_divide=10.0,
        epsilon_E=50,
        epsilon_S=10,
        stability_window=10,
        child_survival_cycles=20,
        birth_stress_cycles=5,
        regulator_alpha=0.1,
        regulator_beta=1.0,
        regulator_gamma=0.3,
        regulator_mutation_rate=0.01,
        alpha_O=1000.0,
        tau_max=1000,
        k_coord=0.1,
        tau_sense=0.1,
        tau_signal=0.1,
        tau_act=0.1,
        latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=10.0, 
        number_of_predictive_modules=3,
        arbitration_delay=1.0,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=50.0,
        scene_min_duration=5,
        kappa_pred=0.5,
        cog_mutation_rate=0.1,
        structural_mutation_rate=0.05,
        base_gating_threshold=0.5,
        base_arbitration_frequency=1
    )
    
    world = EcologyWorld(num_zones=num_zones, max_resources_per_zone=max_res, regen_rate=regen)
    
    # Initialize mixed cognitive population to seed the ecology
    for i in range(initial_pop):
        cell = MonoCell(base_id)
        # Introduce genetic variance
        cell.prediction_horizon = random.uniform(0.0, 20.0)
        cell.module_count = random.randint(0, 5)
        cell.gating_threshold = random.uniform(0.1, 1.0)
        world.add_organism(cell)
        
    history = []
    
    for t in range(cycles):
        # Tick the world
        survivors, children = world.tick()
        
        # Add new births to the world (random zone placement)
        for child in children:
            world.add_organism(child)
            
        if t % 20 == 0:
            all_cells = [c for z in world.zones for c in z.organisms]
            above_repro = [c for c in all_cells if c.energy.E > 120]
            if all_cells:
                print(f"Cycle {t} | Pop: {len(all_cells)} | Above Repro: {len(above_repro)} | Min E: {min(c.energy.E for c in all_cells):.1f} | Max E: {max(c.energy.E for c in all_cells):.1f}")
        
        pop_size = sum(len(z.organisms) for z in world.zones)
        
        if t % 50 == 0:
            if pop_size > 0:
                all_cells = [c for z in world.zones for c in z.organisms]
                avg_ph = sum(c.prediction_horizon for c in all_cells) / pop_size
                avg_mc = sum(c.module_count for c in all_cells) / pop_size
                avg_gt = sum(c.gating_threshold for c in all_cells) / pop_size
                avg_tau = sum(c.tau_coord for c in all_cells) / pop_size
                
                print(f"Cycle {t} | Pop: {pop_size} | Modules: {avg_mc:.2f} | Horizon: {avg_ph:.2f} | Gating: {avg_gt:.2f} | Tau: {avg_tau:.2f}")
                
                history.append({
                    "cycle": t,
                    "population_size": pop_size,
                    "avg_prediction_horizon": avg_ph,
                    "avg_module_count": avg_mc,
                    "avg_gating_threshold": avg_gt,
                    "avg_tau": avg_tau
                })
            else:
                print(f"Cycle {t}: Population Extinct!")
                # Get the last cell that died this cycle from death log (if any, although we don't have direct access here)
                for failed in children: # children variable actually contains dead string in world.py? No, all_children is a list of MonoCell
                    pass
                break
                
    with open("phase8_ecology_results.json", "w") as f:
        json.dump(history, f, indent=4)
        
    print("Simulation Complete. Results saved to phase8_ecology_results.json")

if __name__ == "__main__":
    run_ecology()
