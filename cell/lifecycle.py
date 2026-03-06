import math
import random
from cell.actions import action_B, action_M, action_R, action_K
from cell.burn import compute_burn
from reproduction.spawn import divide
from cell.maintenance import perform_maintenance
from cell.regulator import compute_signals, select_mode, MaintenanceMode
from phase13.oscillator import check_amplitude_invariant
from mono import cultural_pool

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

def cycle(cell, resource_intake=None, resource_structure=0.0, local_resource_density=1.0, organism_data_list=None, observer=None, species_defaults=None, skip_failure_checks=False, generation=None, species_memory=None, env_params=None, panic_state=None):
    # Phase-13: Advance endogenous oscillator once per generation (per cycle call).
    if hasattr(cell, 'oscillator'):
        psi_current = panic_state.get('psi', 0.0) if isinstance(panic_state, dict) else 0.0
        cell.oscillator.apply_reset_if_crossing(psi_current)
        cell.oscillator.step()

    # Sense and regulate
    signals = compute_signals(cell.history)
    mode = select_mode(signals, cell)
    
    # Define common variables for logging
    E_i_env = env_params.get('E_i', cell.id.E_i) if env_params else cell.id.E_i
    R_i = resource_intake if resource_intake is not None else E_i_env
    A_i = {
        'module_count': cell.module_count,
        'prediction_horizon': cell.prediction_horizon,
        'arbitration_frequency': cell.arbitration_frequency
    }
    
    # Preliminary tau calculation for failure check
    prelim_tau = cell.id.k_coord * math.log(max(cell.structure.size(), 0.001)) + cell.id.tau_sense + cell.id.tau_signal + cell.id.tau_act + cell.delay
    alpha_O_env = env_params.get('alpha_O', cell.id.alpha_O) if env_params else cell.id.alpha_O
    if prelim_tau > alpha_O_env:
        death_reason = "LATENCY_EXCEEDED"
        log = {
            "cycle": cell.cycle_count, "E": cell.energy.E, "structure_size": cell.structure.size(),
            "burn": 0, "death": death_reason
        }
        cell.history.append(log)
        return death_reason, log, None
    
    if mode == MaintenanceMode.QUIESCENCE:
        cell.quiescent = True
        cell.energy.update(0, intake=0, extra_burn=0)
        cell.structure.decay(cell.id.decay_rate)
        cell.cycle_count += 1
        S = cell.structure.size()
        log = {"cycle": cell.cycle_count, "E": cell.energy.E, "structure_size": S, "burn": 0, "mode": "QUIESCENCE"}
        cell.history.append(log)
        if cell.energy.E <= 0 or S <= 0:
            death_reason = "ENERGY_DEPLETION" if cell.energy.E <= 0 else "STRUCTURAL_COLLAPSE"
            if organism_data_list is not None:
                organism_data_list.append((cell.get_tau_organism(), cell.energy.E, cell.gating_threshold, A_i, R_i, 0))
            return death_reason, log, None
        return (None, log, None)

    # Active Cycle
    cell.quiescent = False
    actions_taken = []
    total_delta_S = 0
    C_t = 0
    logged_action_cost = 0  # Phase 24 fix: track structural action costs separately from C_t

    # Phase-13: Pre-calculate effective gating threshold
    g_thresh = cell.gating_threshold
    if hasattr(cell, 'oscillator'):
        g_thresh = cell.oscillator.effective_gamma(g_thresh)

    # 1. Structural Maintenance
    decay_delta = cell.structure.decay(cell.id.decay_rate)
    total_delta_S += decay_delta
    
    # Actually perform maintenance based on mode
    repair_delta, repair_cost = perform_maintenance(cell, mode)
    if repair_delta > 0:
        actions_taken.append('B')  # Record repair as 'B'
        total_delta_S += repair_delta
        logged_action_cost += repair_cost

    # 2. Scarcity/Adaptation
    if cell.energy.E < cell.id.E_s:
        success, delta, symbol = action_K(cell.structure, cell.energy, cell.id)
        if success:
            actions_taken.append(symbol)
            total_delta_S += delta
            logged_action_cost += cell.id.c_K * cell.id.action_cost_multiplier
    else:
        adapt_actions = adapt_structure(cell)
        for symbol, delta in adapt_actions:
            actions_taken.append(symbol)
            total_delta_S += delta
            logged_action_cost += getattr(cell.id, f'c_{symbol}') * cell.id.action_cost_multiplier

    # 3. Gating Decision (Pure Architecture)
    S = cell.structure.size()
    E_raw = 1.0 * abs(total_delta_S) + 0.5 * abs(cell.energy.E - cell.last_E_t)
    cell.last_E_t = cell.energy.E
    cell.sustained_error = (1 - 0.3) * cell.sustained_error + 0.3 * E_raw
    
    module_penalty = math.log(max(cell.module_count, 1)) if cell.module_count > 0 else 0
    base_log = math.log(max(S, 0.001))
    tau_predictive = (cell.id.k_coord * base_log) + cell.id.tau_sense + cell.id.tau_signal + cell.id.tau_act + (cell.id.size_penalty_factor * module_penalty) + cell.delay
    
    # Cognitive engagement check
    stage1_open = E_raw > g_thresh
    stage2_open = cell.sustained_error > (g_thresh * 0.8)
    cognitive_engagement = (stage1_open or stage2_open) and (cell.get_tau_failure() - tau_predictive > 0.5)

    if cognitive_engagement:
        C_t += (cell.prediction_horizon * 0.1) + (cell.module_count * 0.5)
        cell.update_coordination_delay()
    else:
        cell.tau_coord = prelim_tau

    # 4. Energy update (Cognitive Foraging Reward)
    extra_burn = env_params.get('basal_burn', cell.id.basal_burn) if env_params else cell.id.basal_burn
    final_intake = R_i if cognitive_engagement else (R_i * 0.5)  # Phase-24: 50% survival foraging
    # Phase-18: Environmental quality affects foraging
    final_intake *= env_params.get('environmental_quality', 1.0)
    
    cell.energy.update(C_t, intake=final_intake, extra_burn=extra_burn)

    # 5. Reproduction
    eligible = False
    repro_reason = None
    
    if cell.energy.E > cell.id.E_repro and S >= cell.id.S_repro:
        mode_eligible = mode in [MaintenanceMode.CONSERVE, MaintenanceMode.LIGHT_REPAIR]
        tau_eligible = cell.get_tau_failure() - cell.get_tau_organism() > 0.5
        
        # Phase-24: Maturity age — cells must mature before reproducing
        maturity_age = 4
        maturity_eligible = cell.cycle_count >= maturity_age
        
        # Phase-24: Reproduction cooldown — prevent synchronized bursts
        reproduction_cooldown = 3
        cooldown_eligible = (cell.cycle_count - getattr(cell, 'last_reproduction_gen', -999)) >= reproduction_cooldown
        
        reproduction_probability = cell.id.reproduction_probability
        # Phase-23: Environment-coupled reproduction (carrying capacity)
        env_q = env_params.get('environmental_quality', 1.0) if env_params else 1.0
        env_q = min(env_q, 1.0)  # Clamp: env > 1.0 gives no bonus
        reproduction_probability *= env_q ** 2  # Quadratic coupling: early slowdown
        if env_q < 0.3:
            reproduction_probability *= 0.1  # Severe penalty in degraded environments
        reproduction_probability = max(reproduction_probability, 0.001)  # Allow rare recovery births
        # Add variability to reproduction threshold
        repro_threshold = cell.id.E_repro * random.uniform(0.7, 1.3)
        
        # Energy-based population regulation
        if organism_data_list:
            total_energy = sum(org[1] for org in organism_data_list)  # Sum energy of all organisms
            avg_energy = total_energy / len(organism_data_list)
            # Reduce reproduction probability if average energy is low
            if avg_energy < 50:
                reproduction_probability *= (avg_energy / 50)
        
        # Debug reproduction eligibility
        if not maturity_eligible:
            repro_reason = "immature"
        elif not cooldown_eligible:
            repro_reason = "cooldown"
        elif not mode_eligible:
            repro_reason = "mode_blocked"
        elif not tau_eligible:
            repro_reason = "tau_blocked"
        elif random.random() >= reproduction_probability:
            repro_reason = "probability_blocked"
        elif cell.energy.E <= repro_threshold:
            repro_reason = "threshold_blocked"
        else:
            eligible = True
            repro_reason = "eligible"
            cell.last_reproduction_gen = cell.cycle_count  # Phase-24: track for cooldown
    else:
        if cell.energy.E <= cell.id.E_repro:
            repro_reason = "energy_low"
        elif S < cell.id.S_repro:
            repro_reason = "structure_low"
    
    # Log reproduction reason (only for debugging)
    if hasattr(cell, 'repro_debug'):
        cell.repro_debug.append(repro_reason)
    else:
        cell.repro_debug = [repro_reason]
    
    child = divide(cell, species_defaults=species_defaults, species_memory=species_memory, env_params=env_params, panic_state=panic_state) if eligible else None
    if child: actions_taken.append('P')

    # 6. Death checks
    if cell.energy.E <= 0 or cell.structure.size() <= 0:
        death_reason = "ENERGY_DEPLETION" if cell.energy.E <= 0 else "STRUCTURAL_COLLAPSE"
        log = {
            "cycle": cell.cycle_count, "E": cell.energy.E, "structure_size": cell.structure.size(),
            "burn": extra_burn + C_t + logged_action_cost, "death": death_reason
        }
        if organism_data_list is not None:
             organism_data_list.append((cell.get_tau_organism(), cell.energy.E, cell.gating_threshold, A_i, R_i, 0))
        return death_reason, log, None

    # 7. Logging
    log = {
        "cycle": cell.cycle_count,
        "E": cell.energy.E,
        "burn": extra_burn + C_t + logged_action_cost,
        "intake": final_intake,
        "structure_size": S,
        "actions": actions_taken,
        "cognitive_active": cognitive_engagement,
        "E_raw": E_raw,
        "tau_coord": cell.tau_coord,
        "tau_organism": cell.get_tau_organism(),
        "tau_failure": cell.get_tau_failure()
    }
    cell.cycle_count += 1
    cell.history.append(log)
    if organism_data_list is not None:
        organism_data_list.append((cell.get_tau_organism(), cell.energy.E, cell.gating_threshold, A_i, R_i, 1))

    return None, log, child
