import math
from cell.actions import action_B, action_M, action_R, action_K
from cell.burn import compute_burn
from reproduction.spawn import divide
from cell.maintenance import perform_maintenance
from cell.regulator import compute_signals, select_mode, MaintenanceMode

def adapt_structure(cell):
    actions = []
    # Try M
    success, delta, symbol = action_M(cell.structure, cell.energy, cell.id)
    if success:
        actions.append((symbol, delta))
    # Try R
    success, delta, symbol = action_R(cell.structure, cell.energy, cell.id)
    if success:
        actions.append((symbol, delta))
    return actions

def cycle(cell):
    # Sense and regulate
    signals = compute_signals(cell.history)
    mode = select_mode(signals, cell)
    
    # Phase-6: Update time state and check for time-based death
    skip_failure_checks = cell.cycle_count < 1
    cell.update_coordination_delay()
    cell.accumulated_latency_drift += cell.id.latency_drift_rate
    
    # Invariants
    assert isinstance(cell.structure.size(), (int, float))
    assert not math.isnan(cell.structure.size())
    assert cell.get_tau_organism() >= 0
    assert not math.isnan(cell.get_tau_organism())
    
    # if not skip_failure_checks:
    #     if cell.tau_coord > cell.id.tau_max:
    #         death_reason = "COORD_OVERLOAD"
    #         log = {
    #             "cycle": cell.cycle_count,
    #             "E": cell.energy.E,
    #             "structure_size": cell.structure.size(),
    #             "actions": [],
    #             "tau_coord": cell.tau_coord,
    #             "tau_organism": cell.get_tau_organism(),
    #             "tau_failure": cell.get_tau_failure(),
    #             "tau_max": cell.id.tau_max,
    #             "viability": cell.get_viability(),
    #             "death": death_reason
    #         }
    #         cell.history.append(log)
    #         return death_reason, log
    #     
    #     if cell.get_tau_organism() > cell.get_tau_failure():
    #         death_reason = "LATENCY_EXCEEDED"
    #         log = {
    #             "cycle": cell.cycle_count,
    #             "E": cell.energy.E,
    #             "structure_size": cell.structure.size(),
    #             "actions": [],
    #             "tau_coord": cell.tau_coord,
    #             "tau_organism": cell.get_tau_organism(),
    #             "tau_failure": cell.get_tau_failure(),
    #             "tau_max": cell.id.tau_max,
    #             "viability": cell.get_viability(),
    #             "death": death_reason
    #         }
    #         cell.history.append(log)
    #         return death_reason, log
    
    # Update reproduction eligibility
    if not cell.reproduction_eligible and cell.cycle_count >= cell.birth_cycle + cell.id.child_survival_cycles:
        cell.reproduction_eligible = True
    
    if mode == MaintenanceMode.QUIESCENCE:
        cell.quiescent = True
        # Apply burn and decay
        extra_burn = cell.id.basal_burn if cell.birth_stress_remaining > 0 else 0
        cell.energy.update(0, extra_burn)  # no action cost
        if cell.birth_stress_remaining > 0:
            cell.birth_stress_remaining -= 1
        decay_delta = cell.structure.decay(cell.id.decay_rate)
        maintenance_delta, maintenance_cost = perform_maintenance(cell, mode)
        # Compute burn
        S = cell.structure.size()
        oscillation = abs(decay_delta + maintenance_delta)
        burn = compute_burn(decay_delta + maintenance_delta, S, oscillation, 0, cell.id)
        # Check for death in quiescence
        # if cell.energy.E < cell.id.E_quiescence:
        #     death_reason = "ENERGY_EXHAUSTED"
        #     log = {
        #         "cycle": cell.cycle_count,
        #         "E": cell.energy.E,
        #         "structure_size": S,
        #         "actions": [],
        #         "tau_coord": cell.tau_coord,
        #         "tau_organism": cell.get_tau_organism(),
        #         "tau_failure": cell.get_tau_failure(),
        #         "tau_max": cell.id.tau_max,
        #         "viability": cell.get_viability(),
        #         "death": death_reason
        #     }
        #     cell.history.append(log)
        #     return death_reason, log
        # Log
        log = {
            "cycle": getattr(cell, 'cycle_count', 0),
            "E": cell.energy.E,
            "C": 0,
            "burn": burn,
            "structure_size": S,
            "actions": [],
            "maintenance_cost": maintenance_cost,
            "maintenance_delta": maintenance_delta,
            "maintenance_mode": mode,
            "regulator_signals": signals,
            "regulator_params": cell.regulator_params,
            "reproduced": False,
            "child_id": None,
            "tau_coord": cell.tau_coord,
            "tau_organism": cell.get_tau_organism(),
            "tau_failure": cell.get_tau_failure(),
            "tau_max": cell.id.tau_max,
            "viability": cell.get_viability()
        }
        cell.cycle_count += 1
        cell.history.append(log)
        # Structural failure check
        if cell.structure.size() <= 0:
            log['death'] = "STRUCTURAL_COLLAPSE"
            return "STRUCTURAL_COLLAPSE", log
        return None, log

    else:
        cell.quiescent = False
        # Normal cycle
        actions_taken = []
        total_delta_S = 0
        C_t = 0

        # 1. Burn evaluation (B)
        success, delta, symbol = action_B(cell.structure, cell.energy, cell.id)
        if success:
            actions_taken.append(symbol)
            total_delta_S += delta

        # 2. Scarcity rules
        if cell.energy.E < cell.id.E_s:
            success, delta, symbol = action_K(cell.structure, cell.energy, cell.id)
            if success:
                actions_taken.append(symbol)
                total_delta_S += delta
                C_t += cell.id.c_K * cell.id.action_cost_multiplier
        else:
            # adapt_structure
            adapt_actions = adapt_structure(cell)
            for symbol, delta in adapt_actions:
                actions_taken.append(symbol)
                total_delta_S += delta
                if symbol == 'M':
                    C_t += cell.id.c_M * cell.id.action_cost_multiplier
                elif symbol == 'R':
                    C_t += cell.id.c_R * cell.id.action_cost_multiplier
                elif symbol == 'K':
                    C_t += cell.id.c_K * cell.id.action_cost_multiplier

        # 3. Reproduction eligibility
        eligible = cell.reproduction_eligible and cell.energy.E >= cell.id.E_repro and cell.structure.size() >= cell.id.S_repro
        if eligible and len(cell.history) >= cell.id.stability_window:
            # Check stability
            recent = list(cell.history)[-cell.id.stability_window:]
            deltas_E = [recent[i]['E'] - recent[i-1]['E'] for i in range(1, len(recent))]
            deltas_S = [recent[i]['structure_size'] - recent[i-1]['structure_size'] for i in range(1, len(recent))]
            stable_E = all(abs(d) < cell.id.epsilon_E for d in deltas_E)
            stable_S = all(abs(d) < cell.id.epsilon_S for d in deltas_S)
            eligible = eligible and stable_E and stable_S
            # Check regulation mode
            eligible = eligible and mode in [MaintenanceMode.CONSERVE, MaintenanceMode.LIGHT_REPAIR]
        
        child = divide(cell) if eligible else None
        if child:
            actions_taken.append('P')
            # C_divide already deducted in divide

        # 4. Energy update
        extra_burn = cell.id.basal_burn if cell.birth_stress_remaining > 0 else 0
        cell.energy.update(C_t, extra_burn)
        if cell.birth_stress_remaining > 0:
            cell.birth_stress_remaining -= 1

        # 5. Structural decay
        decay_delta = cell.structure.decay(cell.id.decay_rate)
        total_delta_S += decay_delta

        # 5.5 Maintenance
        maintenance_delta, maintenance_cost = perform_maintenance(cell, mode)
        total_delta_S += maintenance_delta

        # Phase-6E: Check for scene change based on total error
        total_error = abs(total_delta_S) + (cell.energy.E - cell.id.E_m) / cell.id.E_m if cell.id.E_m > 0 else 0
        cell.check_scene_change(total_error)

        # 6. Compute burn
        S = cell.structure.size()
        oscillation = abs(total_delta_S)
        burn = compute_burn(total_delta_S, S, oscillation, C_t, cell.id)

        # 7. Log metrics
        log = {
            "cycle": getattr(cell, 'cycle_count', 0),
            "E": cell.energy.E,
            "C": C_t,
            "burn": burn,
            "structure_size": S,
            "actions": actions_taken,
            "maintenance_cost": maintenance_cost,
            "maintenance_delta": maintenance_delta,
            "maintenance_mode": mode,
            "regulator_signals": signals,
            "regulator_params": cell.regulator_params,
            "reproduced": child is not None,
            "child_id": child.cell_id if child else None,
            "tau_coord": cell.tau_coord,
            "tau_organism": cell.get_tau_organism(),
            "tau_failure": cell.get_tau_failure(),
            "tau_max": cell.id.tau_max,
            "viability": cell.get_viability()
        }

        # Increment cycle
        cell.cycle_count += 1
        cell.history.append(log)

        # Structural failure check
        if cell.structure.size() <= 0:
            log['death'] = "STRUCTURAL_COLLAPSE"
            return "STRUCTURAL_COLLAPSE", log

        return child, log
