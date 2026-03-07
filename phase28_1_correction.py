import json
import math
import argparse
import random
import statistics
import sys
import os

# Ensure we can import from core framework
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.identity import CoreIdentity
from mono import MonoCell, cultural_pool
from cell.lifecycle import cycle
from phase10.observer import Phase10Observer

# --- Phase 28 Spatial Engine Constants ---
GRID_SIZE = 50
MAX_CELLS_PER_TILE = 10
MIGRATION_RATE = 0.02
BASAL_METABOLISM = 2.0
MAX_AGE = 200
ENV_MAX = 2.0
ENV_MIN = 0.1

def create_spatial_identity():
    """Generates a base identity for cells entering the spatial grid."""
    base = {
        'E_i': 30.0, 'E_m': 200, 'E_s': 5, 'E_r': 1000,
        'c_B': 1, 'c_M': 2, 'c_R': 1, 'c_K': 3, 'c_P': 1,
        'burn_weights': (0.5, 0.3, 0.2), 'mutation_rate': 0.105,
        'initial_energy': 80.0, 'basal_burn': 0.3, 'action_cost_multiplier': 1,
        'initial_structure_size': 20, 'decay_rate': 0.02, 'split_ratio': 0.5,
        'E_quiescence': 5, 'S_quiescence': 5, 'S_critical': 8,
        'E_maintenance_min': 10, 'repair_efficiency': 0.8,
        'E_repro': 25.0, 'S_repro': 1.0, 'r': 0.3, 'C_divide': 5,
        'epsilon_E': 0.5, 'epsilon_S': 0.5, 'stability_window': 5,
        'child_survival_cycles': 5, 'birth_stress_cycles': 2,
        'regulator_alpha': 0.1, 'regulator_beta': 0.05, 'regulator_gamma': 0.2,
        'regulator_mutation_rate': 0.01, 'alpha_O': 100.0, 'tau_max': 100.0,
        'k_coord': 1.0, 'tau_sense': 0.5, 'tau_signal': 0.5, 'tau_act': 1.0,
        'latency_drift_rate': 0.01, 'size_penalty_factor': 0.1,
        'prediction_horizon': 2.0, 'number_of_predictive_modules': 2,
        'arbitration_delay': 1.0, 'module_horizon_adapt_rate': 0.1,
        'global_integrator_capacity': 10.0, 'arbitration_mechanism': 'temporal_sequencing',
        'scene_change_threshold': 0.5, 'scene_min_duration': 5,
        'kappa_pred': 0.0, 'cog_mutation_rate': 0.05, 'structural_mutation_rate': 0.01,
        'base_gating_threshold': 0.5, 'base_arbitration_frequency': 1,
        'strategy_trait': random.choice([0, 1]),  # 0 = extractor, 1 = restorer
        'learning_rate': random.uniform(0.05, 0.25),
        'teaching_efficiency': random.uniform(0.05, 0.25),
        'p_restore': random.uniform(0.05, 0.95),
        'environment_sensitivity': random.uniform(0, 1),
        'trade_propensity': random.uniform(0.0, 1.0),
    }
    identity = CoreIdentity(**base)
    return identity

def init_grid():
    """Initializes the 2D grid containing the two-layer environment."""
    grid = []
    for x in range(GRID_SIZE):
        row = []
        for y in range(GRID_SIZE):
            row.append({
                'env_quality': 1.0,  # Climate/Damage state
                'resource_pool': 10.0, # Harvestable energy
                'cells': []           # Inhabitants
            })
        grid.append(row)
    return grid

def get_neighbors(x, y, radius=1):
    """Returns a list of (nx, ny) grid coordinates within a Moore neighborhood."""
    neighbors = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                neighbors.append((nx, ny))
    return neighbors

def safe_mean(x):
    return statistics.mean(x) if x else 0.0

def safe_stdev(x):
    return statistics.stdev(x) if len(x) > 1 else 0.0

def get_empty_neighbor_tile(grid, x, y):
    """Finds an adjacent tile that has not reached MAX_CELLS_PER_TILE."""
    neighbors = get_neighbors(x, y, radius=1)
    random.shuffle(neighbors)
    for nx, ny in neighbors:
        if len(grid[nx][ny]['cells']) < MAX_CELLS_PER_TILE:
            return (nx, ny)
    return None # completely surrounded by dense tiles

def run_spatial_generation(grid, all_cells, gen, base_depletion, regen_rate):
    """Executes a single generation across the spatial engine."""
    # 1. Shuffle all cells to remove update bias (Asynchronous Updating)
    random.shuffle(all_cells)
    
    # Track statistics
    stats = {
        'births': 0, 'deaths': 0, 'migrations': 0, 
        'total_extraction': 0, 'total_restoration': 0,
        'extractors': 0, 'restorers': 0,
        'teaching_events': 0, 'learning_events': 0
    }
    
    new_children = []
    surviving_cells = []
    
    # Action Constants
    learning_cost = 3.0
    teaching_cost = 1.0
    restore_mult = 0.2
    
    # 2. Process each cell individually
    for cell in all_cells:
        x, y = cell.pos_x, cell.pos_y
        tile = grid[x][y]
        local_neighbors = get_neighbors(x, y, radius=1)
        
        # Build list of all neighborhood cells
        neighborhood_cells = []
        for nx, ny in local_neighbors:
            neighborhood_cells.extend(grid[nx][ny]['cells'])
        
        # --- Local Cultural Teaching / Learning ---
        # If I don't know something, find a teacher in my neighborhood
        if cell.artifact_x is None or cell.artifact_r is None:
            # Try self-learning first (low prob)
            if cell.energy.E > 18.0 and random.random() < 0.1:
                cell.energy.E -= learning_cost
                cell.artifact_x = 1.0
                cell.artifact_r = 1.0
                stats['learning_events'] += 1
            else:
                # Find local teacher
                potential_teachers = [c for c in neighborhood_cells if c != cell and c.artifact_x is not None and c.artifact_r is not None and c.energy.E > teaching_cost]
                if potential_teachers:
                    teacher = random.choice(potential_teachers)
                    if random.random() < teacher.teaching_efficiency:
                        teacher.energy.E -= teaching_cost
                        cell.energy.E -= learning_cost * 0.5
                        # Learn
                        cell.artifact_x = teacher.artifact_x
                        cell.artifact_r = teacher.artifact_r
                        stats['teaching_events'] += 1

        # --- Local Resource Action (Extraction vs Restoration) ---
        if cell.artifact_x is not None and cell.artifact_r is not None:
             base_p_restore = 0.5 + 0.5 * cell.id.strategy_trait 
             p_restore_effective = base_p_restore + cell.environment_sensitivity * (1 - tile['env_quality'])
             p_restore_effective = max(0, min(1, p_restore_effective))
             
             if random.random() < p_restore_effective:
                 # Restorer
                 stats['restorers'] += 1
                 # Repairing logic (uses energy, raises tile env_quality indirectly)
                 env_factor = max(0.3, tile['env_quality'])
                 gain = 30.0 * restore_mult * cell.artifact_r * env_factor
                 # Restoring restores the TILE env quality immediately in Spatial Model
                 tile['env_quality'] = min(ENV_MAX, tile['env_quality'] + 0.05 * cell.artifact_r)
                 cell.energy.E += gain * 0.5
                 stats['total_restoration'] += gain
             else:
                 # Extractor
                 stats['extractors'] += 1
                 if tile['resource_pool'] > 0:
                     gain = min(tile['resource_pool'], 30.0 * cell.artifact_x * tile['env_quality'])
                     tile['resource_pool'] -= gain
                     cell.energy.E += gain
                     stats['total_extraction'] += gain
                     # Extraction damages local env quality
                     tile['env_quality'] = max(ENV_MIN, tile['env_quality'] - 0.02 * cell.artifact_x)

        # --- Basal Metabolism ---
        cell.energy.E -= BASAL_METABOLISM
        cell.cycle_count += 1
        
        # --- Survival and Reproduction ---
        if cell.energy.E > 0 and cell.cycle_count <= MAX_AGE:
            surviving_cells.append(cell)
            
            # Repro check
            if cell.energy.E > 120 and (cell.cycle_count - getattr(cell, 'last_reproduction_gen', 0)) > 5:
                cell.energy.E -= 50
                cell.last_reproduction_gen = cell.cycle_count
                
                # Clone cell
                child_id = create_spatial_identity()
                
                # Inherit traits perfectly by explicitly calling object.__setattr__ since it's frozen
                object.__setattr__(child_id, 'strategy_trait', cell.id.strategy_trait)
                object.__setattr__(child_id, 'learning_rate', cell.id.learning_rate)
                object.__setattr__(child_id, 'p_restore', cell.id.p_restore)
                object.__setattr__(child_id, 'environment_sensitivity', cell.id.environment_sensitivity)
                
                # Mutate slightly (Phase 28.1 Mutation-Selection Balance)
                if random.random() < 0.1:
                    mutated = max(0, min(1, child_id.strategy_trait + random.uniform(-0.02, 0.02)))
                    object.__setattr__(child_id, 'strategy_trait', mutated)
                
                child = MonoCell(child_id)
                child.lineage_id = getattr(cell, 'lineage_id', id(cell.id)) # Inherit lineage tracking on cell
                child.energy.E = 40
                child.cycle_count = 0
                
                # Inherit culture
                child.artifact_x = cell.artifact_x
                child.artifact_r = cell.artifact_r
                
                # Spatial placement: Try to place locally. Spill if full.
                if len(tile['cells']) < MAX_CELLS_PER_TILE:
                    child.pos_x, child.pos_y = x, y
                else:
                    spill = get_empty_neighbor_tile(grid, x, y)
                    if spill:
                        child.pos_x, child.pos_y = spill[0], spill[1]
                    else:
                        child = None # Suppressed by density
                
                if child:
                    new_children.append(child)
                    stats['births'] += 1
        else:
            stats['deaths'] += 1
            
        # --- Migration ---
        # Active cells can move
        if cell in surviving_cells and random.random() < MIGRATION_RATE:
            nx = x + random.choice([-1, 0, 1])
            ny = y + random.choice([-1, 0, 1])
            
            # Bounding
            nx = max(0, min(GRID_SIZE - 1, nx))
            ny = max(0, min(GRID_SIZE - 1, ny))
            
            if (nx != x or ny != y) and len(grid[nx][ny]['cells']) < MAX_CELLS_PER_TILE:
                # Execute move
                cell.pos_x, cell.pos_y = nx, ny
                stats['migrations'] += 1

    # 3. Environment Update Layer
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            tile = grid[x][y]
            # Environmental decay from global climate pressure
            tile['env_quality'] = max(ENV_MIN, tile['env_quality'] - base_depletion)
            
            # Regeneration of resource pool based on current env quality (Two-Layer model)
            tile['resource_pool'] += regen_rate * tile['env_quality']
            
            # Logistic recovery of env quality toward 1.0
            K = 1.0
            r_base = 0.05
            logistic = r_base * tile['env_quality'] * (1.0 - tile['env_quality'] / K)
            tile['env_quality'] = min(ENV_MAX, max(ENV_MIN, tile['env_quality'] + logistic))
            
            # Cap resources
            tile['resource_pool'] = min(50.0, tile['resource_pool'])
            
            # Clear cell array, we will rebuild it
            tile['cells'] = []

    # Merge population and re-index into grid
    final_pop = surviving_cells + new_children
    for c in final_pop:
        grid[c.pos_x][c.pos_y]['cells'].append(c)
        
    return final_pop, stats

def run_spatial_experiment(seed, total_gens=1500, init_pop=500):
    random.seed(seed)
    grid = init_grid()
    population = []
    
    # Randomly scatter initial population
    for _ in range(init_pop):
        c = MonoCell(create_spatial_identity())
        c.cycle_count = random.randint(0, 10)
        c.pos_x = random.randint(0, GRID_SIZE - 1)
        c.pos_y = random.randint(0, GRID_SIZE - 1)
        grid[c.pos_x][c.pos_y]['cells'].append(c)
        population.append(c)
        
    metrics_log = []
    
    for gen in range(total_gens):
        # Base environmental oscillator
        dep_rate = 0.05 + 0.03 * math.sin(2 * math.pi * gen / 400.0)
        regen_rate = 5.0
        
        # --- Phase 28.1 Global Famine (Gen 1100-1150) ---
        if 1100 <= gen <= 1150:
            regen_rate = 0.2  # Near zero regeneration simulates deep famine

        # --- Phase 28.1 Catastrophic Shock (Gen 800) ---
        if gen == 800:
            print(f"Gen 800: K-T EXTINCTION EVENT! Culling 50% of the population...")
            survivors = random.sample(population, len(population) // 2)
            dead_cells = set(population) - set(survivors)
            for c in dead_cells:
                if c in grid[c.pos_x][c.pos_y]['cells']:
                    grid[c.pos_x][c.pos_y]['cells'].remove(c)
            population = list(survivors)
        
        population, stats = run_spatial_generation(grid, population, gen, dep_rate, regen_rate)
        
        if not population:
            print(f"Gen {gen}: EXTINCTION", file=sys.stderr)
            break
            
        if gen % 10 == 0:
            traits = [c.id.strategy_trait for c in population]
            avg_trait = safe_mean(traits)
            var_trait = safe_stdev(traits)
            
            # Compute Spatial Grid Heatmaps
            env_map = np.zeros((GRID_SIZE, GRID_SIZE))
            trait_map = np.zeros((GRID_SIZE, GRID_SIZE))
            
            for x in range(GRID_SIZE):
                for y in range(GRID_SIZE):
                    env_map[x, y] = grid[x][y]['env_quality']
                    cell_traits = [c.id.strategy_trait for c in grid[x][y]['cells']]
                    if cell_traits:
                        trait_map[x, y] = safe_mean(cell_traits)
                    else:
                        trait_map[x, y] = -1 # Empty tile marker
                        
            metrics_log.append({
                'generation': gen,
                'population': len(population),
                'depletion_rate': dep_rate,
                'mean_trait': avg_trait,
                'var_trait': var_trait,
                'births': stats['births'],
                'deaths': stats['deaths'],
                'migrations': stats['migrations'],
                'env_map': env_map.tolist(),
                'trait_map': trait_map.tolist()
            })
            
            print(f"Gen {gen}: Pop {len(population)} | Trait {avg_trait:.2f} (var {var_trait:.2f}) | EnvDep {dep_rate:.3f} | Migrations {stats['migrations']}")

    with open(f'phase28_1_results_seed{seed}.json', 'w') as f:
        json.dump(metrics_log, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--gens', type=int, default=1500)
    args = parser.parse_args()
    
    import numpy as np  # Required for heatmaps formatting
    run_spatial_experiment(args.seed, args.gens)
