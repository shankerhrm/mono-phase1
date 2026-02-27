from cell.structure import Structure
from cell.energy import Energy
from core.identity import CoreIdentity
from core.constants import ACTION_B, ACTION_M, ACTION_R, ACTION_K, ACTION_P

def action_B(structure: Structure, energy: Energy, identity: CoreIdentity):
    # Burn evaluation, no energy cost
    return True, 0, ACTION_B

def action_M(structure: Structure, energy: Energy, identity: CoreIdentity):
    cost = identity.c_M * identity.action_cost_multiplier
    if energy.E < cost:
        return False, 0, ACTION_M
    energy.E -= cost
    delta = structure.mutate(identity)
    return True, delta, ACTION_M

def action_R(structure: Structure, energy: Energy, identity: CoreIdentity):
    cost = identity.c_R * identity.action_cost_multiplier
    if energy.E < cost:
        return False, 0, ACTION_R
    energy.E -= cost
    delta = structure.reorganize(identity)
    return True, delta, ACTION_R

def action_K(structure: Structure, energy: Energy, identity: CoreIdentity):
    cost = identity.c_K * identity.action_cost_multiplier
    if energy.E < cost:
        return False, 0, ACTION_K
    energy.E -= cost
    delta = structure.compress(identity)
    return True, delta, ACTION_K

def action_P(structure: Structure, energy: Energy, identity: CoreIdentity):
    # Placeholder for P action (possibly reproduction)
    cost = identity.c_P * identity.action_cost_multiplier
    if energy.E < cost:
        return False, 0, ACTION_P
    energy.E -= cost
    # Some structural change, but placeholder
    return True, 0, ACTION_P
