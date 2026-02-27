from mono import MonoCell
from reproduction.mutation import compress_and_mutate
from cell.energy import Energy

def reproduce(parent):
    assert parent.energy.E >= parent.id.E_r

    parent.energy.E -= parent.id.c_P * parent.id.action_cost_multiplier

    child_structure = compress_and_mutate(parent.structure, parent.id)

    child_energy_value = parent.id.E_r * parent.id.split_ratio

    child_energy = Energy(child_energy_value, parent.id)

    return MonoCell(
        identity=parent.id,
        structure=child_structure,
        energy=child_energy
    )
