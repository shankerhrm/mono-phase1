"""
Phase-15: Physiological Load Controller

Slow physiological burden accumulation for tunable oscillatory regulation.

L(t) accumulates positive stress, decays with repair capacity.
Panic intensity derived from L.
Breaks boundary attractors with biological inertia.
"""

class PhysiologicalController:
    """Controller with slow physiological load integration.

    Parameters:
        alpha: Accumulation rate for positive stress
        beta: Decay rate with repair capacity
        activation_level: Load threshold for PANIC state
        psi_baseline: Baseline stress level
        epsilon_max: Maximum memory softening
        mutation_ceiling: Maximum mutation multiplier
    """

    def __init__(
        self,
        alpha=0.1,
        beta=0.5,
        activation_level=0.4,
        psi_baseline=0.3,
        epsilon_max=0.5,
        mutation_ceiling=3.0,
    ):
        self.alpha = alpha
        self.beta = beta
        self.activation_level = activation_level
        self.psi_baseline = psi_baseline
        self.epsilon_max = epsilon_max
        self.mutation_ceiling = mutation_ceiling

        self.load = 0.0
        self.state = "CALM"

    def update(self, psi, avg_energy, structural_integrity):
        """Update physiological load based on stress and repair capacity.

        Returns dict with state, intensity, load, mutation_multiplier, memory_softening_eps.
        """
        # Accumulation from positive stress
        stress_signal = max(0.0, psi - self.psi_baseline)
        self.load += self.alpha * stress_signal

        # Decay with repair capacity
        repair_capacity = 0.001 * avg_energy + 0.002 * structural_integrity
        self.load -= self.beta * repair_capacity

        # Clamp
        self.load = max(0.0, min(1.0, self.load))

        # Derive panic intensity from load
        panic_intensity = self.load

        # State determination
        state = "PANIC" if self.load >= self.activation_level else "CALM"

        # Outputs
        if state == "CALM":
            mutation_multiplier = 1.0
        else:  # PANIC
            mutation_multiplier = 2.0 + 1.0 * psi  # Simplified, scale with stress

        mutation_multiplier = min(mutation_multiplier, self.mutation_ceiling)

        memory_softening_eps = self.epsilon_max * panic_intensity

        return {
            'state': state,
            'intensity': panic_intensity,
            'load': self.load,
            'mutation_multiplier': mutation_multiplier,
            'memory_softening_eps': memory_softening_eps,
        }

    def get_outputs(self, psi):
        """Compute control outputs based on current state and Ψ.

        Returns:
            dict with keys: state, intensity, load, mutation_multiplier, memory_softening_eps
        """
        psi_clamped = max(0.0, min(1.0, psi))

        # Mutation multiplier (state-based)
        if self.state == "CALM":
            mutation_multiplier = 1.0
        else:  # PANIC
            mutation_multiplier = 2.0 + 1.0 * psi_clamped

        mutation_multiplier = min(mutation_multiplier, self.mutation_ceiling)

        memory_softening_eps = self.epsilon_max * self.load

        return {
            'state': self.state,
            'intensity': self.load,
            'load': self.load,
            'mutation_multiplier': mutation_multiplier,
            'memory_softening_eps': memory_softening_eps,
        }
