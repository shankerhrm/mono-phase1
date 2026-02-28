from collections import deque
import statistics

class MaintenanceMode:
    CONSERVE = "CONSERVE"
    LIGHT_REPAIR = "LIGHT_REPAIR"
    HEAVY_REPAIR = "HEAVY_REPAIR"
    QUIESCENCE = "QUIESCENCE"

def compute_signals(history):
    """Compute regulator signals from sliding window history."""
    if len(history) < 2:
        return {
            'E_trend': 0,
            'S_trend': 0,
            'E_var': 0,
            'S_var': 0,
            'decay_pressure': 0,
            'burn_pressure': 0
        }
    energies = [log['E'] for log in history]
    structures = [log['structure_size'] for log in history]
    burns = [log['burn'] for log in history]
    
    deltas_E = [energies[i] - energies[i-1] for i in range(1, len(energies))]
    deltas_S = [structures[i] - structures[i-1] for i in range(1, len(structures))]
    
    E_trend = statistics.mean(deltas_E) if deltas_E else 0
    S_trend = statistics.mean(deltas_S) if deltas_S else 0
    E_var = statistics.stdev(deltas_E) if len(deltas_E) > 1 else 0
    S_var = statistics.stdev(deltas_S) if len(deltas_S) > 1 else 0
    decay_pressure = -S_trend  # positive if decaying
    burn_pressure = statistics.mean(burns) if burns else 0
    
    return {
        'E_trend': E_trend,
        'S_trend': S_trend,
        'E_var': E_var,
        'S_var': S_var,
        'decay_pressure': decay_pressure,
        'burn_pressure': burn_pressure
    }

def select_mode(signals, cell):
    """Deterministic rule-based mode selection using cell's heritable params."""
    # Check for quiescence first
    if cell.energy.E < cell.id.E_quiescence and cell.structure.size() < cell.id.S_quiescence:
        return MaintenanceMode.QUIESCENCE
    
    # Regulation rules using heritable params
    alpha = cell.regulator_params['alpha']
    beta = cell.regulator_params['beta']
    gamma = cell.regulator_params['gamma']
    
    if signals['S_trend'] < -alpha and cell.energy.E > cell.id.E_maintenance_min:
        return MaintenanceMode.HEAVY_REPAIR
    elif signals['S_trend'] < -beta:
        return MaintenanceMode.LIGHT_REPAIR
    elif signals['E_trend'] < -gamma:
        return MaintenanceMode.CONSERVE
    else:
        return MaintenanceMode.CONSERVE
