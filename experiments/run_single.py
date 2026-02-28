import sys
sys.path.insert(0, '.')
import random
from mono import MonoCell
from cell.lifecycle import cycle
from metrics.logger import Logger
from core.identity import CoreIdentity

# Default identity with example parameters
identity = CoreIdentity(
    E_i=10, E_m=1000, E_s=50, E_r=10000,  # High E_r to disable reproduction
    c_B=0, c_M=5, c_R=5, c_K=5, c_P=20,
    burn_weights=(0.1, 0.1, 0.1),
    mutation_rate=0.1,
    initial_energy=100, basal_burn=2.0, action_cost_multiplier=1.5,  
    initial_structure_size=10, decay_rate=0.001, split_ratio=0.5,  
    E_quiescence=20, S_quiescence=3,
    S_critical=5, E_maintenance_min=20, repair_efficiency=0.5,
    E_repro=70, S_repro=8, r=0.4, C_divide=20,
    epsilon_E=5, epsilon_S=1, stability_window=10,
    child_survival_cycles=10, birth_stress_cycles=5,
    regulator_alpha=0.1, regulator_beta=0.05, regulator_gamma=0.5, regulator_mutation_rate=0.01
)

random.seed(42)
cell = MonoCell(identity)
logger = Logger('experiments/single_run.json')
max_cycles = 2000

for t in range(max_cycles):
    child, log_entry = cycle(cell)
    logger.log(log_entry)
    if cell.energy.E <= 0 or cell.structure.size() <= 0:
        break
    if child:
        cell = child

logger.save()
print("Single run completed")
