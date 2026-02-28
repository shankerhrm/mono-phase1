from core.identity import CoreIdentity
from cell.structure import Structure
from cell.energy import Energy
from collections import deque
import itertools
import math

cell_id_counter = itertools.count(1)

class MonoCell:
    def __init__(self, identity: CoreIdentity, structure: Structure = None, energy: Energy = None):
        self.id = identity
        self.structure = structure or Structure(max(int(identity.initial_structure_size), 1))
        self.energy = energy or Energy(identity.initial_energy, identity)
        self.cycle_count = 0
        self.quiescent = False
        self.history = deque(maxlen=20)
        # Lineage tracking (Phase-4)
        self.cell_id = next(cell_id_counter)
        self.parent_id = None
        self.generation = 0
        self.birth_cycle = 0
        # Reproduction eligibility
        self.reproduction_eligible = True
        # Birth stress
        self.birth_stress_remaining = 0
        # Regulator parameters (Phase-5, heritable)
        self.regulator_params = {
            'alpha': identity.regulator_alpha,
            'beta': identity.regulator_beta,
            'gamma': identity.regulator_gamma
        }

        # Phase-6 time state
        self.tau_coord = identity.tau_sense + identity.tau_signal + identity.tau_act  # base coordination delay
        self.accumulated_latency_drift = 0.0
        self.last_coord_calc_cycle = 0
        self.size_at_last_calc = self.structure.size()
        self.delay = 0.0  # for artificial delay injection()

        # Phase-6D modular self
        self.predictive_modules = [
            {'horizon': identity.prediction_horizon, 'error': 0.0, 'weight': 1.0 / identity.number_of_predictive_modules}
            for _ in range(identity.number_of_predictive_modules)
        ]
        self.global_arbitrator = {'capacity_used': 0.0, 'arbitration_delay': identity.arbitration_delay}

        # Phase-6E scene and conflict resolution
        self.current_scene_module = 0
        self.scene_start_cycle = 0
        self.accumulated_scene_error = 0.0
        self.scene_threshold = identity.scene_change_threshold

        # Sanity guards
        assert isinstance(self.structure.size(), (int, float))

    def update_coordination_delay(self):
        """Update coordination delay based on current size and module."""
        self.tau_coord = max(0, self.id.k_coord * math.log(max(self.structure.size(), 0.001)) + self.id.tau_sense + self.id.tau_signal + self.id.tau_act * (1 - self.current_scene_module * 0.2) + self.delay)
        self.last_coord_calc_cycle = self.cycle_count
        self.size_at_last_calc = self.structure.size()

        # Sanity guards
        assert isinstance(self.structure.size(), (int, float))

    def get_tau_organism(self):
        """Total organism response latency."""
        return self.tau_coord + self.accumulated_latency_drift

    def get_tau_failure(self):
        """Environmental decay clock."""
        return self.id.alpha_O * self.structure.size()

    def get_viability(self):
        """Phase-6 viability function."""
        tau_o = self.get_tau_organism()
        tau_f = self.get_tau_failure()
        return math.exp(-max(0, tau_o - tau_f))

    def check_scene_change(self, total_error):
        """Check for event-driven scene change based on error threshold."""
        if len(self.predictive_modules) == 0:
            return False
        if self.cycle_count - self.scene_start_cycle < self.id.scene_min_duration:
            return False
        self.accumulated_scene_error += total_error
        if self.accumulated_scene_error > self.id.scene_change_threshold:
            self.accumulated_scene_error = 0.0
            self.current_scene_module = (self.current_scene_module + 1) % len(self.predictive_modules)
            self.scene_start_cycle = self.cycle_count
            self.update_coordination_delay()  # Update delay immediately on module switch
            print(f"SCENE SWITCH at cycle {self.cycle_count}: module {self.current_scene_module}")
            return True
        return False
