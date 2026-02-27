from cell.actions import action_B, action_M, action_R, action_K
from cell.burn import compute_burn
from reproduction.spawn import reproduce

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
    # Try K
    success, delta, symbol = action_K(cell.structure, cell.energy, cell.id)
    if success:
        actions.append((symbol, delta))
    return actions

def maybe_reproduce(cell):
    if cell.energy.E >= cell.id.E_r:
        child = reproduce(cell)
        return child
    return None

def cycle(cell):
    # Check for quiescence
    if cell.energy.E < cell.id.E_quiescence and cell.structure.size() < cell.id.S_quiescence:
        cell.quiescent = True
        # No actions, but apply burn and decay
        cell.energy.update(0)  # no action cost
        decay_delta = cell.structure.decay(cell.id.decay_rate)
        # Compute burn
        S = cell.structure.size()
        oscillation = abs(decay_delta)
        burn = compute_burn(decay_delta, S, oscillation, 0, cell.id)
        # Log
        log = {
            "cycle": getattr(cell, 'cycle_count', 0),
            "E": cell.energy.E,
            "C": 0,
            "burn": burn,
            "structure_size": S,
            "actions": []
        }
        cell.cycle_count += 1
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
        child = maybe_reproduce(cell)
        if child:
            actions_taken.append('P')
            C_t += cell.id.c_P * cell.id.action_cost_multiplier

        # 4. Energy update
        cell.energy.update(C_t)

        # 5. Structural decay
        decay_delta = cell.structure.decay(cell.id.decay_rate)
        total_delta_S += decay_delta

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
            "actions": actions_taken
        }

        # Increment cycle
        cell.cycle_count += 1

        return child, log
