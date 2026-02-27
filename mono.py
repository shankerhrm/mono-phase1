from core.identity import CoreIdentity
from cell.structure import Structure
from cell.energy import Energy

class MonoCell:
    def __init__(self, identity: CoreIdentity, structure: Structure = None, energy: Energy = None):
        self.id = identity
        self.structure = structure or Structure(identity.initial_structure_size)
        self.energy = energy or Energy(identity.initial_energy, identity)
        self.cycle_count = 0
        self.quiescent = False
