import copy
from cell.structure import Structure
from core.identity import CoreIdentity

def compress_and_mutate(parent_structure: Structure, identity: CoreIdentity):
    # Create a new structure based on parent
    child_structure = Structure()
    # Copy graph
    child_structure.graph = copy.deepcopy(parent_structure.graph)
    # Compress
    child_structure.compress(identity)
    # Mutate
    child_structure.mutate(identity)
    return child_structure
