import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
import random

def apply_environmental_shock(cell, cycle):
    """Apply shock regime with precursor signals and damage spike."""
    # Precursor phase: anticipatory signal only for predictive organisms
    if 45 <= cycle < 50:
        if len(cell.predictive_modules) > 0:
            cell.accumulated_scene_error += 15.0
            print(f"  Adding precursor error: now {cell.accumulated_scene_error:.1f}/{cell.id.scene_change_threshold}")
    
    # Shock phase: strong damage
    if 50 <= cycle < 60:
        cell.structure._size *= 0.85  # 15% decay per cycle

def test_predictive_shock():
    print("Phase-6.3: Predictive MONO under shock regime")
    identity = CoreIdentity(
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
        E_repro=60,
        S_repro=5,
        r=0.1,
        C_divide=5,
        epsilon_E=2,
        epsilon_S=1,
        stability_window=10,
        child_survival_cycles=20,
        birth_stress_cycles=5,
        regulator_alpha=0.1,
        regulator_beta=0.2,
        regulator_gamma=0.3,
        regulator_mutation_rate=0.01,
        alpha_O=500.0,  # Lower tau_failure for pressure
        tau_max=1000,
        k_coord=0.1,
        tau_sense=0.1,
        tau_signal=0.1,
        tau_act=0.1,
        latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=5,
        number_of_predictive_modules=3,
        arbitration_delay=1,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=30.0,  # Lower threshold for faster switching
        scene_min_duration=3,  # Shorter minimum duration
        kappa_pred=0.5
    )
    cell = MonoCell(identity)
    cell.delay = 0.8
    cell.structure._size = cell.structure.size()
    
    print("INIT STRUCTURE:", cell.structure.size())
    print("INIT DELAY:", cell.delay)
    print("INIT CURRENT SCENE:", cell.current_scene_module)
    
    cycles_survived = 0
    scene_switch_cycle = None
    
    for cycle_num in range(200):
        cell.cycle_count = cycle_num
        death_reason, log, child = cycle(cell, resource_intake=identity.E_i)
        
        # Check for scene switch
        if len(cell.predictive_modules) > 0 and scene_switch_cycle is None and cell.current_scene_module > 0:
            scene_switch_cycle = cycle_num
        
        # Apply environmental shock
        apply_environmental_shock(cell, cycle_num)
        
        # Log key metrics
        if cycle_num in [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]:
            print(f"Cycle {cycle_num}: S={cell.structure.size():.1f}, E={cell.energy.E:.1f}, τ_o={cell.get_tau_organism():.3f}, scene={cell.current_scene_module}, mode={log.get('maintenance_mode', 'N/A')}")
        
        if death_reason or log.get('death'):
            print(f"Death at cycle {cycle_num}: {log.get('death')}")
            print(f"Structure: {cell.structure.size()}, Energy: {cell.energy.E}")
            break
            
        cycles_survived += 1
    
    print(f"Cycles survived: {cycles_survived}")
    if scene_switch_cycle:
        print(f"Scene switch at cycle: {scene_switch_cycle}")
    else:
        print("No scene switch occurred")
    
    return cycles_survived, scene_switch_cycle

def test_reactive_shock():
    print("\nPhase-6.3: Reactive MONO under shock regime")
    identity = CoreIdentity(
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
        E_repro=60,
        S_repro=5,
        r=0.1,
        C_divide=5,
        epsilon_E=2,
        epsilon_S=1,
        stability_window=10,
        child_survival_cycles=20,
        birth_stress_cycles=5,
        regulator_alpha=0.1,
        regulator_beta=0.2,
        regulator_gamma=0.3,
        regulator_mutation_rate=0.01,
        alpha_O=500.0,  # Lower tau_failure for pressure
        tau_max=1000,
        k_coord=0.1,
        tau_sense=0.1,
        tau_signal=0.1,
        tau_act=0.1,
        latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=5,
        number_of_predictive_modules=0,  # No cognition
        arbitration_delay=1,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=50.0,
        scene_min_duration=5,
        kappa_pred=0.0
    )
    cell = MonoCell(identity)
    cell.delay = 0.8
    cell.structure._size = cell.structure.size()
    
    print("INIT STRUCTURE:", cell.structure.size())
    print("INIT DELAY:", cell.delay)
    print("INIT CURRENT SCENE:", cell.current_scene_module)
    
    cycles_survived = 0
    
    for cycle_num in range(200):
        cell.cycle_count = cycle_num
        death_reason, log, child = cycle(cell)
        
        # Apply environmental shock
        apply_environmental_shock(cell, cycle_num)
        
        # Log key metrics
        if cycle_num in [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]:
            print(f"Cycle {cycle_num}: S={cell.structure.size():.1f}, E={cell.energy.E:.1f}, τ_o={cell.get_tau_organism():.3f}, scene={cell.current_scene_module}, mode={log.get('maintenance_mode', 'N/A')}")
        
        if log.get('death'):
            print(f"Death at cycle {cycle_num}: {log.get('death')}")
            print(f"Structure: {cell.structure.size()}, Energy: {cell.energy.E}")
            break
            
        cycles_survived += 1
    
    print(f"Cycles survived: {cycles_survived}")
    
    return cycles_survived, None

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE-6.3: SHOCK-REGIME VALIDATION TEST")
    print("=" * 60)
    
    pred_cycles, pred_switch = test_predictive_shock()
    react_cycles, _ = test_reactive_shock()
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Predictive MONO: {pred_cycles} cycles")
    print(f"Reactive MONO:  {react_cycles} cycles")
    
    if pred_switch:
        print(f"Predictive scene switch: cycle {pred_switch}")
    
    survival_diff = pred_cycles - react_cycles
    print(f"Survival difference: {survival_diff} cycles")
    
    if survival_diff >= 20:
        print("\n✅ PHASE-6 COGNITION VALIDATED")
        print("Prediction provides significant survival advantage under shock")
    elif survival_diff > 0:
        print("\n🟡 PHASE-6 COGNITION PARTIALLY VALIDATED")
        print("Prediction provides modest advantage")
    elif survival_diff < 0:
        print("\n❌ PHASE-6 COGNITION REJECTED")
        print("Prediction is maladaptive under shock conditions")
    else:
        print("\n🟡 PHASE-6 COGNITION NEUTRAL")
        print("No measurable survival difference")
