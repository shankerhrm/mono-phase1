"""
Phase-12: Panic Controller

Three-state machine governing MONO's evolvability response to stress:

    CALM ──[Ψ > 0.3 × 3 gens]──► ALERT ──[Ψ > 0.6 × 3 gens]──► PANIC
      ▲                              │                                │
      └──[Ψ < 0.15 × 3 gens]────────┘                                │
      └──[Ψ < 0.4 + 5 gen dwell]─────────────────────────────────────┘

Outputs:
    mutation_multiplier  — scales cog_mutation_rate [1.0, 3.0]
    memory_softening_eps — ε for Ms softening [0.0, 0.5], quadratic in Ψ

INVARIANT: This module does not modify organism runtime state.
It produces scalar control signals consumed at the population level only.
"""

from enum import Enum


class PanicState(Enum):
    CALM = 'CALM'
    ALERT = 'ALERT'
    PANIC = 'PANIC'


class PanicController:
    """State machine for panic regulation.

    Transition thresholds:
        CALM  → ALERT:  Ψ > 0.3 for confirmation_window gens
        ALERT → PANIC:  Ψ > 0.6 for confirmation_window gens
        PANIC → ALERT:  Ψ < 0.4 AND min_dwell_panic gens in PANIC
        ALERT → CALM:   Ψ < 0.15 for confirmation_window gens

    Outputs are computed based on current state and Ψ value.
    """

    def __init__(
        self,
        alert_threshold=0.3,
        panic_threshold=0.6,
        exit_panic_threshold=0.4,
        exit_alert_threshold=0.15,
        confirmation_window=3,
        min_dwell_panic=5,
        min_dwell_calm=3,
        epsilon_max=0.5,
        mutation_ceiling=3.0,
    ):
        self.alert_threshold = alert_threshold
        self.panic_threshold = panic_threshold
        self.exit_panic_threshold = exit_panic_threshold
        self.exit_alert_threshold = exit_alert_threshold
        self.confirmation_window = confirmation_window
        self.min_dwell_panic = min_dwell_panic
        self.min_dwell_calm = min_dwell_calm
        self.epsilon_max = epsilon_max
        self.mutation_ceiling = mutation_ceiling

        self._state = PanicState.CALM
        self._gens_in_state = 0
        self._consecutive_above_alert = 0
        self._consecutive_above_panic = 0
        self._consecutive_below_exit_alert = 0
        self._consecutive_below_exit_panic = 0

        self._transition_log = []

    def update(self, psi, generation=None):
        """Process one generation's Ψ value and update state.

        Returns dict with current state, mutation_multiplier, memory_softening_eps.
        """
        self._gens_in_state += 1

        # Track consecutive threshold crossings
        if psi > self.alert_threshold:
            self._consecutive_above_alert += 1
        else:
            self._consecutive_above_alert = 0

        if psi > self.panic_threshold:
            self._consecutive_above_panic += 1
        else:
            self._consecutive_above_panic = 0

        if psi < self.exit_alert_threshold:
            self._consecutive_below_exit_alert += 1
        else:
            self._consecutive_below_exit_alert = 0

        if psi < self.exit_panic_threshold:
            self._consecutive_below_exit_panic += 1
        else:
            self._consecutive_below_exit_panic = 0

        # State transitions
        prev_state = self._state

        if self._state == PanicState.CALM:
            if self._consecutive_above_alert >= self.confirmation_window:
                self._transition(PanicState.ALERT, generation)

        elif self._state == PanicState.ALERT:
            if self._consecutive_above_panic >= self.confirmation_window:
                self._transition(PanicState.PANIC, generation)
            elif self._consecutive_below_exit_alert >= self.confirmation_window:
                self._transition(PanicState.CALM, generation)

        elif self._state == PanicState.PANIC:
            if (self._consecutive_below_exit_panic >= 1
                    and self._gens_in_state >= self.min_dwell_panic):
                self._transition(PanicState.ALERT, generation)

        return self.get_outputs(psi)

    def _transition(self, new_state, generation=None):
        """Record state transition."""
        self._transition_log.append({
            'from': self._state.value,
            'to': new_state.value,
            'generation': generation,
            'gens_in_prev_state': self._gens_in_state,
        })
        self._state = new_state
        self._gens_in_state = 0

    def get_outputs(self, psi):
        """Compute control outputs based on current state and Ψ.

        Returns:
            dict with keys: state, mutation_multiplier, memory_softening_eps
        """
        psi_clamped = max(0.0, min(1.0, psi))

        # Mutation multiplier
        if self._state == PanicState.CALM:
            mutation_multiplier = 1.0
        elif self._state == PanicState.ALERT:
            mutation_multiplier = 1.0 + 1.0 * psi_clamped
        else:  # PANIC
            mutation_multiplier = 2.0 + 1.0 * psi_clamped

        # Enforce ceiling
        mutation_multiplier = min(mutation_multiplier, self.mutation_ceiling)

        # Memory softening ε — quadratic in Ψ
        if self._state == PanicState.CALM:
            memory_softening_eps = 0.0
        else:
            memory_softening_eps = self.epsilon_max * (psi_clamped ** 2)

        return {
            'state': self._state.value,
            'mutation_multiplier': mutation_multiplier,
            'memory_softening_eps': memory_softening_eps,
        }

    @property
    def state(self):
        return self._state

    @property
    def transition_log(self):
        return list(self._transition_log)

    @property
    def gens_in_state(self):
        return self._gens_in_state
