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
    ENTROPIC_DRIFT = "ENTROPIC_DRIFT"
    OSCILLATORY_COLLAPSE = "OSCILLATORY_COLLAPSE"

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
