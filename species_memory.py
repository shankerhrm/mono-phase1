"""
INVARIANT:
SpeciesMemory MUST NOT influence runtime behavior.
It may only affect initialization via scalar defaults at reproduction.

Violation of this invariant is a design error, not a bug.
"""

import math
from collections import defaultdict
import random

class SpeciesMemory:
    def __init__(self, alpha=0.01, epsilon=0.1, noise_rate=0.0, drop_params=None):
        self._allowed_keys = (
            'gamma',
            'module_count',
            'tau_budget',
            'energy_ceiling',
        )
        # Ms: expected structural configuration
        # Represent as dict of parameter means
        self.Ms = {
            'gamma': 0.5,  # gating threshold
            'module_count': 3.0,  # architecture
            'tau_budget': 5.0,  # latency
            'energy_ceiling': 10.0  # cost
        }
        self.alpha = alpha  # evolutionary learning rate
        self.epsilon = epsilon  # variance bound
        self.noise_rate = noise_rate  # probability to flip survival
        self.drop_params = drop_params or []  # params to drop in compression
        self._gamma_history = []  # minimal variance tracking (non-executable)

        self._validate_memory_state()

    def _validate_memory_state(self):
        if set(self.Ms.keys()) != set(self._allowed_keys):
            raise ValueError("SpeciesMemory Ms must contain only the allowed scalar keys")
        for k, v in self.Ms.items():
            if not isinstance(v, (int, float)):
                raise TypeError(f"SpeciesMemory Ms values must be scalar numeric; key={k}")

    def compress_phi(self, X_i):
        """
        Compression operator ϕ: preserves structural parameters, weights by survival.
        X_i = (tau_i, E_i, gamma_i, A_i, R_i, S_i)
        Returns: weighted vector or dict
        """
        tau_i, E_i, gamma_i, A_i, R_i, S_i = X_i
        # Apply noise: flip S_i with probability noise_rate
        if random.random() < self.noise_rate:
            S_i = 1 - S_i
        if S_i == 0:
            return None  # only survivors contribute
        # A_i assumed dict: {'module_count': int, 'prediction_horizon': float, etc.}
        phi = {
            'gamma': gamma_i,
            'module_count': A_i.get('module_count', 0),
            'tau_budget': tau_i,
            'energy_ceiling': E_i
        }
        # Drop params for compression loss test
        for param in self.drop_params:
            phi.pop(param, None)
        for k, v in phi.items():
            if not isinstance(v, (int, float)):
                raise TypeError(f"SpeciesMemory compress_phi must output scalar numeric values; key={k}")
        return phi

    def update(self, organism_data):
        """
        organism_data: list of X_i tuples from the generation.
        Update Ms using survivors' compressed data.
        """
        if organism_data is None:
            return
        survivors_phi = []
        for X_i in organism_data:
            phi = self.compress_phi(X_i)
            if phi:
                survivors_phi.append(phi)

        if not survivors_phi:
            return  # no survivors, no update

        # Compute expected phi
        expected_phi = defaultdict(float)
        for phi in survivors_phi:
            for key, val in phi.items():
                expected_phi[key] += val
        for key in expected_phi:
            expected_phi[key] /= len(survivors_phi)

        for key in expected_phi.keys():
            if key not in self._allowed_keys:
                raise ValueError(f"SpeciesMemory update produced forbidden key={key}")

        # Update Ms
        for key in self.Ms:
            if key in expected_phi:
                self.Ms[key] = (1 - self.alpha) * self.Ms[key] + self.alpha * expected_phi[key]

        self._validate_memory_state()

        # Track for variance (simplified)
        if 'gamma' in expected_phi:
            self._gamma_history.append(float(expected_phi['gamma']))
            if len(self._gamma_history) > 50:  # arbitrary window
                self._gamma_history.pop(0)

    def get_variance(self):
        """Simplified variance check on key params."""
        if len(self._gamma_history) < 2:
            return 0
        # Compute variance for one param, e.g., gamma
        mean = sum(self._gamma_history) / len(self._gamma_history)
        var = sum((x - mean)**2 for x in self._gamma_history) / len(self._gamma_history)
        return var

    def check_stability(self):
        """Return True if within bounds."""
        return self.get_variance() < self.epsilon

    def get_defaults(self):
        """Return dict of defaults for new organisms."""
        return self.Ms.copy()

    def soften(self, epsilon, current_phi):
        """Phase-12: Memory softening under panic.

        Ms_new = (1 - ε) * Ms + ε * M_current

        This accelerates prior adaptation without full erasure.
        ε is controlled by the panic controller (quadratic in Ψ).

        INVARIANT: Softening modifies Ms (population prior) only.
        It does not affect runtime behavior (IOBA preserved).

        Args:
            epsilon: Softening rate [0.0, 0.5]. Higher = faster adaptation.
            current_phi: Dict of current generation's survivor statistics.
        """
        if epsilon <= 0.0 or not current_phi:
            return
        epsilon = min(epsilon, 0.5)  # Hard cap
        for key in self.Ms:
            if key in current_phi:
                self.Ms[key] = (1.0 - epsilon) * self.Ms[key] + epsilon * current_phi[key]
        self._validate_memory_state()

