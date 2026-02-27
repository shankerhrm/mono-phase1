import sys
sys.path.insert(0, '.')
import random
from mono import MonoCell
from cell.lifecycle import cycle
from metrics.logger import Logger
from core.identity import CoreIdentity

# Base parameters
base_params = {
    'E_i': 10, 'E_m': 1000, 'E_s': 50, 'E_r': 200,
    'c_B': 0, 'c_M': 5, 'c_R': 5, 'c_K': 5, 'c_P': 20,
    'burn_weights': (0.1, 0.1, 0.1),
    'mutation_rate': 0.1,
    'initial_energy': 100, 'basal_burn': 1, 'action_cost_multiplier': 1,
    'initial_structure_size': 10, 'decay_rate': 0.05, 'split_ratio': 0.5
}

# Group parameters
groups = {
    'A': {'mutation_rate': 0, 'E_r': 10000},  # Baseline Survival
    'B': {'mutation_rate': 0.05},  # Reproduction Stress
    'C': {'decay_rate': 0.1, 'c_R': 10},  # Structural Fragility
    'D': {'basal_burn': 3, 'mutation_rate': 0.1}  # Chaos Edge
}

max_cycles = 1000
runs_per_group = 30

for group_name, group_params in groups.items():
    for run in range(runs_per_group):
        # Set seed for determinism
        random.seed(run)
        # Create identity
        params = base_params.copy()
        params.update(group_params)
        identity = CoreIdentity(**params)
        # Create cell
        cell = MonoCell(identity)
        # Logger
        logger = Logger(f'snapshots/lineage_{group_name}_{run}.json')
        # Run
        for t in range(max_cycles):
            child, log_entry = cycle(cell)
            logger.log(log_entry)
            if cell.energy.E <= 0 or cell.structure.size() <= 0:
                break
            if child:
                cell = child
        logger.save()

print("Lineage experiments completed")
