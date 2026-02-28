from mono import MonoCell
import random

def divide(parent):
    # Deduct division cost
    parent.energy.E -= parent.id.C_divide
    
    # Structure compression before split (placeholder, no compress method yet)
    # parent.structure.compress()  # TODO: implement if needed
    
    # Calculate split
    E_remaining = parent.energy.E
    S_total = parent.structure.size()
    r = parent.id.r
    
    E_p = (1 - r) * E_remaining
    E_c = r * E_remaining
    S_p = int((1 - r) * S_total)
    S_c = int(r * S_total)
    
    # Update parent
    parent.energy.E = E_p
    parent.structure._size = S_p
    
    # Create child
    child = MonoCell(parent.id)
    child.energy.E = E_c
    child.structure._size = S_c
    
    # Inheritance and lineage
    child.parent_id = parent.cell_id
    child.generation = parent.generation + 1
    child.birth_cycle = parent.cycle_count + 1
    child.reproduction_eligible = False
    child.birth_stress_remaining = parent.id.birth_stress_cycles
    
    # Inherit and mutate regulator params (Phase-5)
    child.regulator_params = parent.regulator_params.copy()
    for key in child.regulator_params:
        child.regulator_params[key] += random.gauss(0, parent.id.regulator_mutation_rate)
        child.regulator_params[key] = max(0.01, min(1.0, child.regulator_params[key]))
    
    return child
