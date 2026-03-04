import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
import random

def test_empty():
    print("Test 1: Empty universe (no delay, no damage)")
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
        alpha_O=1000.0,
        tau_max=1000,
        k_coord=0.1,
        tau_sense=0.1,
        tau_signal=0.1,
        tau_act=0.1,
        latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=5,
        number_of_predictive_modules=0,  # Disable cognition
        arbitration_delay=1,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=50.0,
        scene_min_duration=5
    )
    cell = MonoCell(identity)
    cell.delay = 0.0  # No delay
    print("INIT STRUCTURE:", cell.structure.size())
    print("INIT STRUCTURE TYPE:", type(cell.structure.size()))
    print("INIT TAU FAILURE:", cell.get_tau_failure())
    print("INIT DELAY:", cell.delay)
    print("INIT CURRENT SCENE:", cell.current_scene_module)
    cycles_survived = 0
    for cycle_num in range(200):
        cell.cycle_count = cycle_num
        death_reason, log, child = cycle(cell)
        if child or death_reason or log.get('death'):
            break
        if cycle_num < 5:
            print(f"Cycle {cycle_num}: tau_organism {cell.get_tau_organism():.3f}, structure {cell.structure.size():.3f}")
        cycles_survived += 1
    print(f"Cycles survived: {cycles_survived}")

def test_delay():
    print("\nTest 2: Delay only (no damage)")
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
        alpha_O=1000.0,
        tau_max=1000,
        k_coord=0.1,
        tau_sense=0.1,
        tau_signal=0.1,
        tau_act=0.1,
        latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=5,
        number_of_predictive_modules=0,
        arbitration_delay=1,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=50.0,
        scene_min_duration=5
    )
    cell = MonoCell(identity)
    cell.delay = 0.5  # Delay only
    print("INIT STRUCTURE:", cell.structure.size())
    print("INIT STRUCTURE TYPE:", type(cell.structure.size()))
    print("INIT TAU FAILURE:", cell.get_tau_failure())
    print("INIT DELAY:", cell.delay)
    print("INIT CURRENT SCENE:", cell.current_scene_module)
    cycles_survived = 0
    for cycle_num in range(200):
        if cycle_num < 3:
            print("TAU_COORD:", cell.tau_coord, "TAU_ORGANISM:", cell.get_tau_organism(), "STRUCTURE:", cell.structure.size())
        cell.cycle_count = cycle_num
        death_reason, log, child = cycle(cell)
        if child or death_reason or log.get('death'):
            break
        cycles_survived += 1
    print(f"Cycles survived: {cycles_survived}")

def test_damage():
    print("\nTest 3: Slow damage (delay + gradual structure loss)")
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
        alpha_O=1000.0,
        tau_max=1000,
        k_coord=0.1,
        tau_sense=0.1,
        tau_signal=0.1,
        tau_act=0.1,
        latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=5,
        number_of_predictive_modules=0,
        arbitration_delay=1,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=50.0,
        scene_min_duration=5
    )
    cell = MonoCell(identity)
    cell.delay = 0.5  # Delay + damage
    cycles_survived = 0
    for cycle_num in range(200):
        cell.cycle_count = cycle_num
        death_reason, log, child = cycle(cell)
        if child or death_reason or log.get('death'):
            break
        if cycle_num < 5:
            print(f"Cycle {cycle_num}: tau_organism {cell.get_tau_organism():.3f}, structure {cell.structure.size():.3f}")
        cycles_survived += 1
        if cycle_num >= 0:  # Start immediately
            cell.structure._size = max(0, cell.structure._size - 0.05)
    print(f"Cycles survived: {cycles_survived}")

def test_predictive():
    print("\nTest Predictive MONO (cognition enabled)")
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
        alpha_O=1000.0,
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
        scene_change_threshold=50.0,
        scene_min_duration=5,
        kappa_pred=0.5
    )
    cell = MonoCell(identity)
    cell.delay = random.uniform(0.8, 1.2)
    cell.structure._size = cell.structure.size()
    print("INIT STRUCTURE:", cell.structure.size())
    print("INIT DELAY:", cell.delay)
    print("INIT CURRENT SCENE:", cell.current_scene_module)
    cycles_survived = 0
    for cycle_num in range(200):
        cell.cycle_count = cycle_num
        death_reason, log, child = cycle(cell)
        if log.get('death'):
            print(f"Death at cycle {cycle_num}: {log.get('death')}")
            print(f"Structure: {cell.structure.size()}, Energy: {cell.energy.E}")
            break
        if cycle_num < 3:
            print("TAU_COORD:", cell.tau_coord, "TAU_ORGANISM:", cell.get_tau_organism(), "STRUCTURE:", cell.structure.size())
        if cycle_num >= 40:
            damage_rate = 0.05 * (cell.structure.size() / 10.0)
            cell.structure._size = max(0, cell.structure._size - damage_rate)
        cycles_survived += 1
    print(f"Cycles survived: {cycles_survived}")

def test_reactive():
    print("\nTest Reactive MONO (no cognition)")
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
        alpha_O=1000.0,
        tau_max=1000,
        k_coord=0.1,
        tau_sense=0.1,
        tau_signal=0.1,
        tau_act=0.1,
        latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=5,
        number_of_predictive_modules=0,
        arbitration_delay=1,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=50.0,
        scene_min_duration=5
    )
    cell = MonoCell(identity)
    cell.delay = random.uniform(0.8, 1.2)
    cell.structure._size = cell.structure.size()
    print("INIT STRUCTURE:", cell.structure.size())
    print("INIT DELAY:", cell.delay)
    print("INIT CURRENT SCENE:", cell.current_scene_module)
    cycles_survived = 0
    for cycle_num in range(200):
        cell.cycle_count = cycle_num
        death_reason, log, child = cycle(cell)
        if log.get('death'):
            print(f"Death at cycle {cycle_num}: {log.get('death')}")
            print(f"Structure: {cell.structure.size()}, Energy: {cell.energy.E}")
            break
        if cycle_num < 3:
            print("TAU_COORD:", cell.tau_coord, "TAU_ORGANISM:", cell.get_tau_organism(), "STRUCTURE:", cell.structure.size())
        if cycle_num >= 40:
            damage_rate = 0.05 * (cell.structure.size() / 10.0)
            cell.structure._size = max(0, cell.structure._size - damage_rate)
        cycles_survived += 1
    print(f"Cycles survived: {cycles_survived}")

if __name__ == "__main__":
    test_predictive()
    test_reactive()
