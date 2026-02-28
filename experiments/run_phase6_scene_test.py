#!/usr/bin/env python3
"""
Phase-6 Test 1: Narrative Scene Formation

Tests whether temporal sequencing + error-triggered scene change produces discrete scenes.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle

def run_phase6_scene_test():
    # Phase-6 identity parameters
    identity = CoreIdentity(
        E_i=20, E_m=200, E_s=5, E_r=1000,
        c_B=1, c_M=2, c_R=1, c_K=3, c_P=1,
        burn_weights=(0.5, 0.3, 0.2),
        mutation_rate=0.1,
        initial_energy=150,
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
        S_repro=12,
        r=0.5,
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
        alpha_O=0.1,  # environmental decay rate
        tau_max=1000,   # max coord delay
        k_coord=0.1,  # coord scaling
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
        scene_min_duration=5
    )

    cell = MonoCell(identity)
    logs = []
    scenes = []
    current_scene = {
        'start_cycle': 0,
        'dominant_module': cell.current_scene_module,
        'errors': []
    }

    for cycle_num in range(60):
        cell.cycle_count = cycle_num
        # Simulate prediction errors (dummy)
        for i, module in enumerate(cell.predictive_modules):
            # Stable environment: low error
            base_error = 0.5 + i * 0.2  # different baselines
            if cycle_num > 50:
                # Perturbation: increase error for module 1
                if i == 1:
                    base_error += 3.0
            module['error'] = base_error

        # Check scene change
        total_error = sum(module['error'] for module in cell.predictive_modules)
        scene_changed = cell.check_scene_change(total_error)
        print(f"Cycle {cycle_num}: total_error {total_error:.2f}, scene_changed {scene_changed}")

        # Run cycle
        child, log = cycle(cell)
        if child:
            break  # reproduction not handled

        # Log the cycle
        log = {
            "cycle": cycle_num,
            "E": cell.energy.E,
            "structure_size": cell.structure.size(),
            "actions": log['actions'],
            "scene_changed": scene_changed,
            "total_error": total_error,
            "current_scene_module": cell.current_scene_module,
            "accumulated_scene_error": cell.accumulated_scene_error
        }
        logs.append(log)

        # Update current scene
        current_scene['errors'].append(total_error)

        # Handle scene change
        if scene_changed:
            end_cycle = cycle_num
            mean_error = sum(current_scene['errors']) / len(current_scene['errors']) if current_scene['errors'] else 0
            error_trend = '↑' if len(current_scene['errors']) > 1 and current_scene['errors'][-1] > current_scene['errors'][0] else '↓' if len(current_scene['errors']) > 1 and current_scene['errors'][-1] < current_scene['errors'][0] else '='
            scenes.append({
                'start_cycle': current_scene['start_cycle'],
                'end_cycle': end_cycle,
                'dominant_module': current_scene['dominant_module'],
                'mean_error': mean_error,
                'error_trend': error_trend
            })
            # Start new scene
            current_scene = {
                'start_cycle': cycle_num + 1,
                'dominant_module': cell.current_scene_module,
                'errors': []
            }

        if log.get('death'):
            break

    # Close the last scene
    mean_error = sum(current_scene['errors']) / len(current_scene['errors']) if current_scene['errors'] else 0
    error_trend = '↑' if len(current_scene['errors']) > 1 and current_scene['errors'][-1] > current_scene['errors'][0] else '↓' if len(current_scene['errors']) > 1 and current_scene['errors'][-1] < current_scene['errors'][0] else '='
    scenes.append({
        'start_cycle': current_scene['start_cycle'],
        'end_cycle': cycle_num,
        'dominant_module': current_scene['dominant_module'],
        'mean_error': mean_error,
        'error_trend': error_trend
    })

    # Save logs
    with open('phase6_scene_test.json', 'w') as f:
        json.dump({'logs': logs, 'scenes': scenes}, f, indent=2)

    print("Phase-6 Scene Test completed. Logs saved to phase6_scene_test.json")

if __name__ == "__main__":
    run_phase6_scene_test()
