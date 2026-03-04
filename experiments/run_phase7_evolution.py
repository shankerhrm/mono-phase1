import sys
import os
import json
import random
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle

def run_evolution(regime="stable", generations=50, cycles_per_gen=150, initial_pop=10):
    print(f"--- Starting Phase-7 Evolution ({regime.upper()} Regime) ---")
    
    base_id = CoreIdentity(
        E_i=20, E_m=200, E_s=5, E_r=1000,
        c_B=1, c_M=2, c_R=1, c_K=3, c_P=1,
        burn_weights=(0.5, 0.3, 0.2),
        mutation_rate=0.1,
        initial_energy=1000,
        basal_burn=0,
        action_cost_multiplier=1,
        initial_structure_size=10,
        decay_rate=0.05,
        split_ratio=0.5,
        E_quiescence=5,
        S_quiescence=5,
        S_critical=8,
        E_maintenance_min=10,
        repair_efficiency=0.8,
        E_repro=150,
        S_repro=10,
        r=0.5,
        C_divide=10.0,
        epsilon_E=5,
        epsilon_S=2,
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
        prediction_horizon=10.0, # Initial "high" thinking
        number_of_predictive_modules=3, # Initial "complex" structure
        arbitration_delay=1.0,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10.0,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=2.0,
        scene_min_duration=3,
        kappa_pred=0.5,
        # Phase-7 Config
        cog_mutation_rate=0.1,
        structural_mutation_rate=0.02,
        base_gating_threshold=0.5,
        base_arbitration_frequency=1
    )

    # Initialize Seed Population
    population = [MonoCell(base_id) for _ in range(initial_pop)]
    history = []

    for gen in range(generations):
        # Apply environmental constraints for this generation
        gen_survivors = []
        gen_children = []
        
        # Generation loop over time (cycles)
        for t in range(cycles_per_gen):
            next_step_population = []
            for cell in population:
                if cell.structure.size() <= 0:
                    continue # Dead
                
                # Apply Regime Shocks
                if regime == "shock":
                    # Sudden massive damage every 40 cycles (simulate predictable threat)
                    if t % 40 == 38: # Anticipatory cue (simulated by structure degradation starting slightly early)
                        cell.structure._size -= cell.structure.size() * 0.1
                    elif t % 40 == 0 and t > 0: # Actual shock impact
                        cell.structure._size -= cell.structure.size() * 0.4
                elif regime == "deceptive":
                    if random.random() < 0.1: # 10% chance of random noise damage
                        cell.structure._size -= random.uniform(0, cell.structure.size() * 0.15)
                # Stable regime does nothing extra
                
                death_reason, log, child = cycle(cell)
                if cell.cell_id == 8 or cell.cell_id == 14:
                    with open("cell_trace.txt", "a") as f:
                        f.write(f"Cycle {t} [Cell {cell.cell_id}]: E={cell.energy.E:.2f}, S={cell.structure.size()}, logs={log.get('actions', [])}\n")
                if isinstance(death_reason, str):
                    with open("death_log.txt", "a") as f:
                        f.write(f"Gen {gen}, Cycle {t}, cell {cell.cell_id} died of {death_reason}. E: {cell.energy.E:.2f}, S: {cell.structure.size():.2f}\n")
                next_step_population.append(cell)
                if isinstance(child, MonoCell):
                    next_step_population.append(child)
                    gen_children.append(child)
            population = next_step_population
                    
        # Filter survivors (must be alive at end of gen or have reproduced)
        next_gen_parents = [c for c in population if c.structure.size() > 0]
        
        # Keep population bounded and prevent extinction loops for the script
        if len(next_gen_parents) > 50:
             # Selection based roughly on highest structural integrity
             next_gen_parents.sort(key=lambda x: x.structure.size(), reverse=True)
             next_gen_parents = next_gen_parents[:50]
        elif len(next_gen_parents) == 0:
             print(f"Gen {gen}: Population Extinct!")
             break
             
        # Record population phenotypes
        avg_horizon = sum(c.prediction_horizon for c in next_gen_parents) / len(next_gen_parents)
        avg_modules = sum(c.module_count for c in next_gen_parents) / len(next_gen_parents)
        avg_gating = sum(c.gating_threshold for c in next_gen_parents) / len(next_gen_parents)
        avg_f_arb = sum(c.arbitration_frequency for c in next_gen_parents) / len(next_gen_parents)
        
        print(f"Gen {gen} | Pop: {len(next_gen_parents)} | Modules: {avg_modules:.2f} | Horizon: {avg_horizon:.2f} | Gating: {avg_gating:.2f} | f_arb: {avg_f_arb:.2f}")

        history.append({
            "generation": gen,
            "population_size": len(next_gen_parents),
            "avg_prediction_horizon": avg_horizon,
            "avg_module_count": avg_modules,
            "avg_gating_threshold": avg_gating,
            "avg_arbitration_frequency": avg_f_arb
        })

        population = next_gen_parents

    # Dump results
    with open(f"phase7_results_{regime}.json", "w") as f:
        json.dump(history, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        reg = sys.argv[1]
    else:
        reg = "stable"
    run_evolution(regime=reg)
