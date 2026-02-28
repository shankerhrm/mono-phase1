from mono import MonoCell
from cell.lifecycle import cycle
from core.identity import CoreIdentity

class World:
    def __init__(self, initial_energy_pool, max_population=None):
        self.energy_pool = initial_energy_pool
        self.cells = []
        self.max_population = max_population
        self.cycle_count = 0

    def add_cell(self, cell):
        if self.max_population is None or len(self.cells) < self.max_population:
            self.cells.append(cell)

    def distribute_energy(self):
        """Distribute energy from pool to cells."""
        num_cells = len(self.cells)
        if num_cells > 0:
            # Assume E_i is the intake per cell, but cap by pool
            energy_per_cell = min(self.energy_pool / num_cells, 10)  # E_i = 10
            for cell in self.cells:
                cell.energy.E += energy_per_cell
            self.energy_pool -= energy_per_cell * num_cells
            # Prevent negative pool
            self.energy_pool = max(0, self.energy_pool)

    def cycle(self):
        """Run one cycle for the world: distribute energy, process cells."""
        self.distribute_energy()
        new_cells = []
        to_remove = []
        logs = []
        for cell in self.cells:
            child, log = cycle(cell)
            logs.append(log)
            if child:
                new_cells.append(child)
            if cell.energy.E <= 0 or cell.structure.size() <= 0:
                to_remove.append(cell)
        for cell in to_remove:
            if cell in self.cells:
                self.cells.remove(cell)
        for cell in new_cells:
            self.add_cell(cell)
        self.cycle_count += 1
        return logs

    def get_population_stats(self):
        """Get stats on population: size, trait distributions."""
        if not self.cells:
            return {}
        alphas = [c.regulator_params['alpha'] for c in self.cells]
        betas = [c.regulator_params['beta'] for c in self.cells]
        gammas = [c.regulator_params['gamma'] for c in self.cells]
        generations = [c.generation for c in self.cells]
        return {
            'population_size': len(self.cells),
            'alpha_mean': sum(alphas) / len(alphas),
            'beta_mean': sum(betas) / len(betas),
            'gamma_mean': sum(gammas) / len(gammas),
            'max_generation': max(generations) if generations else 0,
            'energy_pool': self.energy_pool
        }
