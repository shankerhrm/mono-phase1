# Stability & Failure Taxonomy for MONO Phase-1

# import numpy as np

def std(values):
    if not values:
        return 0
    mean = sum(values) / len(values)
    return (sum((x - mean)**2 for x in values) / len(values))**0.5

def slope(values):
    if len(values) < 2:
        return 0
    return (values[-1] - values[0]) / (len(values) - 1)

# Death Classes
class DeathClass:
    ENERGY_STARVATION = "ENERGY_STARVATION"
    STRUCTURAL_DECAY = "STRUCTURAL_DECAY"
    REPRODUCTION_OVERLOAD = "REPRODUCTION_OVERLOAD"
    MAINTENANCE_DEBT = "MAINTENANCE_DEBT"
    REPAIR_OSCILLATION = "REPAIR_OSCILLATION"
    FALSE_STABILITY = "FALSE_STABILITY"
    REPRODUCTION_COLLAPSE = "REPRODUCTION_COLLAPSE"
    LINEAGE_EXTINCTION = "LINEAGE_EXTINCTION"
    MUTATIONAL_INSTABILITY = "MUTATIONAL_INSTABILITY"
    REPRODUCTIVE_STARVATION = "REPRODUCTIVE_STARVATION"
    INHERITED_MAINTENANCE_DEBT = "INHERITED_MAINTENANCE_DEBT"
    ENTROPIC_DRIFT = "ENTROPIC_DRIFT"
    OSCILLATORY_COLLAPSE = "OSCILLATORY_COLLAPSE"
    LATENCY_EXCEEDED = "LATENCY_EXCEEDED"
    COORD_OVERLOAD = "COORD_OVERLOAD"

# Stability Classes
class StabilityClass:
    STATIC_EQUILIBRIUM = "STATIC_EQUILIBRIUM"
    LOW_AMPLITUDE_OSCILLATION = "LOW_AMPLITUDE_OSCILLATION"
    DRIFT_STABLE = "DRIFT_STABLE"
    PSEUDO_STABLE = "PSEUDO_STABLE"

def classify_death(logs):
    """
    Classify the cause of death based on logs.
    Returns DeathClass or None if survived.
    """
    if not logs:
        return None
    final_log = logs[-1]
    lifespan = len(logs)

    # Check final state
    if final_log['E'] <= 0 and final_log['structure_size'] > 0:
        # Energy starvation
        # Check if reproduction overload
        p_actions = [i for i, log in enumerate(logs) if 'P' in log['actions']]
        if p_actions:
            # Check if energy dropped sharply after last P
            last_p = p_actions[-1]
            if last_p < len(logs) - 1:
                e_after = final_log['E']
                e_before = logs[last_p]['E']
                if e_before > 0 and e_after / e_before < 0.3:  # sharp drop
                    return DeathClass.REPRODUCTION_OVERLOAD
        return DeathClass.ENERGY_STARVATION
    elif final_log['structure_size'] <= 0 and final_log['E'] > 0:
        return DeathClass.STRUCTURAL_DECAY
    elif lifespan < 1000:
        # Collapsed before max, classify based on burn trajectory
        burns = [log['burn'] for log in logs]
        if len(burns) > 10:
            # Check for oscillatory
            burn_std = std(burns)
            if burn_std > 1:  # high oscillation
                return DeathClass.OSCILLATORY_COLLAPSE
            # Check for drift: increasing burn
            burn_trend = slope(burns)
            if burn_trend > 0.01:  # increasing
                return DeathClass.ENTROPIC_DRIFT
        # Default to energy if E low
        if final_log['E'] < final_log['structure_size'] * 10:  # arbitrary
            return DeathClass.ENERGY_STARVATION
        else:
            return DeathClass.STRUCTURAL_DECAY
    return None  # survived

    # Phase-2 death classes
    total_maintenance_cost = sum(log.get('maintenance_cost', 0) for log in logs)
    lifespan = len(logs)
    if total_maintenance_cost > lifespan * 10:  # assuming E_i=10
        return DeathClass.MAINTENANCE_DEBT

    maintenance_deltas = [log.get('maintenance_delta', 0) for log in logs]
    if std(maintenance_deltas) > 1 and len(maintenance_deltas) > 10:
        return DeathClass.REPAIR_OSCILLATION

    structures = [log['structure_size'] for log in logs]
    if std(structures) < 1 and logs[-1]['E'] < 20:
        return DeathClass.FALSE_STABILITY

    # Phase-6 death classes
    if 'tau_coord' in final_log and final_log['tau_coord'] > final_log.get('tau_max', float('inf')):
        return DeathClass.COORD_OVERLOAD
    if 'tau_organism' in final_log and 'tau_failure' in final_log and final_log['tau_organism'] > final_log['tau_failure']:
        return DeathClass.LATENCY_EXCEEDED

    return None  # survived

def classify_stability(logs):
    """
    Classify stability if survived or based on trajectory.
    """
    if not logs:
        return None
    lifespan = len(logs)
    burns = [log['burn'] for log in logs]
    energies = [log['E'] for log in logs]
    structures = [log['structure_size'] for log in logs]

    burn_std = std(burns)
    energy_std = std(energies)
    structure_std = std(structures)

    if lifespan < 500:
        return None  # collapsed early, pseudo-stable?
    elif lifespan == 1000:
        # Survived full
        if burn_std < 0.1 and energy_std < 5 and structure_std < 0.5:
            return StabilityClass.STATIC_EQUILIBRIUM
        elif burn_std < 0.5 and energy_std < 20 and structure_std < 2:
            return StabilityClass.LOW_AMPLITUDE_OSCILLATION
        elif abs(structures[-1] - structures[0]) > structures[0] * 0.5:
            return StabilityClass.DRIFT_STABLE
        else:
            return StabilityClass.PSEUDO_STABLE  # survived but unstable
    else:
        # Collapsed after 500
        return StabilityClass.PSEUDO_STABLE
