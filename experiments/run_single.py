import sys
sys.path.insert(0, '.')
import random
from mono import MonoCell
from cell.lifecycle import cycle
from metrics.logger import Logger
from core.identity import CoreIdentity

# Default identity with example parameters
identity = CoreIdentity(
    E_i=10, E_m=1000, E_s=50, E_r=200,
    c_B=0, c_M=5, c_R=5, c_K=5, c_P=20,
    burn_weights=(0.1, 0.1, 0.1),
    mutation_rate=0.1,
    initial_energy=100, basal_burn=1, action_cost_multiplier=1,
    initial_structure_size=10, decay_rate=0.05, split_ratio=0.5
)

random.seed(42)
cell = MonoCell(identity)
logger = Logger('experiments/single_run.json')
max_cycles = 1000

for t in range(max_cycles):
    child, log_entry = cycle(cell)
    logger.log(log_entry)
    if cell.energy.E <= 0 or cell.structure.size() <= 0:
        break
    if child:
        cell = child

logger.save()
print("Single run completed")
