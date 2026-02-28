def check_maintenance_needed(cell):
    """Check if maintenance is needed based on structural and energy thresholds."""
    return cell.structure.size() < cell.id.S_critical and cell.energy.E > cell.id.E_maintenance_min

from cell.regulator import MaintenanceMode

def perform_maintenance(cell, mode):
    """Perform maintenance based on regulator-selected mode."""
    if mode == MaintenanceMode.CONSERVE:
        return 0.0, 0.0
    elif mode == MaintenanceMode.LIGHT_REPAIR:
        cost = 5.0
    elif mode == MaintenanceMode.HEAVY_REPAIR:
        cost = 15.0
    else:
        return 0.0, 0.0  # QUIESCENCE or invalid
    
    # Compute delta
    max_S = cell.id.initial_structure_size
    current_S = cell.structure.size()
    repair_efficiency = cell.id.repair_efficiency * (1 + cell.current_scene_module * 0.2) * (1 + 0.1 * cell.current_scene_module if len(cell.predictive_modules) > 0 else 1)
    delta_S = repair_efficiency * cost * (1 - current_S / max_S)
    
    # Ensure energy sufficient
    if cell.energy.E < cost:
        return 0.0, 0.0
    
    cell.energy.E -= cost
    # Update structure size, clamped to max
    new_S = current_S + delta_S
    cell.structure._size = min(max_S, new_S)
    return delta_S, cost
