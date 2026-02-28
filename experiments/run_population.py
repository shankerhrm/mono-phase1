import sys
sys.path.insert(0, '.')
import random
from mono import MonoCell
from experiments.world import World
from metrics.logger import Logger
from core.identity import CoreIdentity

# Phase-5 config with evolution
identity = CoreIdentity(
    E_i=10, E_m=1000, E_s=50, E_r=10000,
    c_B=0, c_M=5, c_R=5, c_K=5, c_P=20,
    burn_weights=(0.1, 0.1, 0.1),
    mutation_rate=0.1,
    initial_energy=50, basal_burn=2.0, action_cost_multiplier=1.5,
    initial_structure_size=10, decay_rate=0.001, split_ratio=0.5,
    E_quiescence=20, S_quiescence=3,
    S_critical=5, E_maintenance_min=20, repair_efficiency=0.5,
    E_repro=80, S_repro=8, r=0.4, C_divide=20,
    epsilon_E=5, epsilon_S=1, stability_window=10,
    child_survival_cycles=10, birth_stress_cycles=5,
    regulator_alpha=0.1, regulator_beta=0.05, regulator_gamma=0.5, regulator_mutation_rate=0.01
)

random.seed(42)

# Create world with shared energy pool
world = World(initial_energy_pool=10000, max_population=100)  # Finite pool, cap population

# Add initial cell
initial_cell = MonoCell(identity)
world.add_cell(initial_cell)

# Logger for world stats
logger = Logger('experiments/evolution_run.json')
max_cycles = 500

for t in range(max_cycles):
    logs = world.cycle()
    stats = world.get_population_stats()
    stats['cycle'] = t
    logger.log(stats)
    if stats.get('population_size', 0) == 0:
        break  # Extinction

logger.save()
print("Evolution run completed")
