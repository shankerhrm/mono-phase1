"""
Phase-14: Intensity-Based Panic Controller

Continuous panic intensity system for calibrated recovery dynamics.

panic_intensity ∈ [0,1] accumulates escalation and decays with recovery.
State determined by activation_level threshold.
Memory softening scales with intensity.

This upgrades from binary hysteresis to continuous stress integration.
"""

class PanicController:
    """Continuous panic intensity controller.

    Parameters:
        panic_threshold: Ψ value above which escalation occurs
        escalation_rate: Rate to increase panic_intensity when above threshold
        recovery_rate: Rate to decrease panic_intensity when below threshold
        activation_level: Intensity level required for PANIC state
        epsilon_max: Maximum memory softening epsilon
        mutation_ceiling: Maximum mutation multiplier
    """

    def __init__(
        self,
        panic_threshold=0.55,
        escalation_rate=0.15,
        recovery_rate=0.01,
        activation_level=0.3,
        escalation_threshold=0.6,
        recovery_threshold=0.5,
        epsilon_max=0.5,
        mutation_ceiling=3.0,
    ):
        self.panic_threshold = panic_threshold
        self.escalation_rate = escalation_rate
        self.recovery_rate = recovery_rate
        self.activation_level = activation_level
        self.escalation_threshold = escalation_threshold
        self.recovery_threshold = recovery_threshold
        self.epsilon_max = epsilon_max
        self.mutation_ceiling = mutation_ceiling

        self.panic_intensity = 0.0
        self.state = "CALM"

    def update(self, psi, generation=None):
        """Update panic intensity based on current Ψ.

        Returns dict with current state, panic_intensity, memory_softening_eps.
        """
        if psi > self.escalation_threshold:
            self.panic_intensity += self.escalation_rate
        elif psi < self.recovery_threshold:
            self.panic_intensity -= self.recovery_rate
        # else no change

        # Clamp to [0, 1]
        self.panic_intensity = max(0.0, min(1.0, self.panic_intensity))

        # Determine state
        if self.panic_intensity >= self.activation_level:
            self.state = "PANIC"
        else:
            self.state = "CALM"

        return self.get_outputs(psi)

    def get_outputs(self, psi):
        """Compute control outputs based on current state and Ψ.

        Returns:
            dict with keys: state, panic_intensity, mutation_multiplier, memory_softening_eps
        """
        psi_clamped = max(0.0, min(1.0, psi))

        # Mutation multiplier (state-based, as in Phase-12)
        if self.state == "CALM":
            mutation_multiplier = 1.0
        elif self.state == "ALERT":
            mutation_multiplier = 1.0 + 1.0 * psi_clamped
        else:  # PANIC
            mutation_multiplier = 2.0 + 1.0 * psi_clamped

        # Enforce ceiling
        mutation_multiplier = min(mutation_multiplier, self.mutation_ceiling)

        # Memory softening ε — scales with panic_intensity
        memory_softening_eps = self.epsilon_max * self.panic_intensity

        return {
            'state': self.state,
            'panic_intensity': self.panic_intensity,
            'mutation_multiplier': mutation_multiplier,
            'memory_softening_eps': memory_softening_eps,
        }
