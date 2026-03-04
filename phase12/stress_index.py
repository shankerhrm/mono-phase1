"""
Phase-12: Stress Index Module

Computes the Composite Stress Index (Ψ) from four signals:
  ∇E  — energy gradient (leading indicator)
  Φ   — reproductive failure rate
  m   — mortality rate
  V   — rate of variance collapse (-dVar(Γ)/dt)

Ψ = w1·∇E_hat + w2·Φ_hat + w3·m_hat + w4·V_hat

All components normalized to [0, 1] via sigmoid saturation.

INVARIANT: This module is read-only. It observes population statistics
and produces scalar outputs. It does not modify organism state.
"""

import math
from collections import deque


def _sigmoid_normalize(x, k=5.0):
    """Normalize x to [0, 1] using sigmoid saturation.

    k controls sensitivity: higher k = faster saturation.
    """
    return max(0.0, min(1.0, 2.0 / (1.0 + math.exp(-k * x)) - 1.0))


class EnergyGradient:
    """Tracks per-generation average energy and computes ∇E.

    ∇E = ΔE_avg / max(basal_burn, 1.0)

    Smoothed via EMA with λ=0.2.
    Persistence check: ∇E must be negative for 3 consecutive generations
    before it is considered "confirmed negative."
    """

    def __init__(self, ema_lambda=0.2, persistence_window=3):
        self.ema_lambda = ema_lambda
        self.persistence_window = persistence_window

        self._prev_avg_energy = None
        self._grad_e_smooth = 0.0
        self._grad_e_prev_smooth = 0.0  # for second derivative
        self._negative_streak = 0
        self._history = deque(maxlen=50)

    def update(self, avg_energy, basal_burn=0.0):
        """Update with current generation's average energy.

        Returns raw ∇E (before persistence filtering).
        """
        if self._prev_avg_energy is None:
            self._prev_avg_energy = avg_energy
            return 0.0

        delta_e = avg_energy - self._prev_avg_energy
        normalizer = max(basal_burn, 10.0)
        grad_e_raw = delta_e / normalizer

        # EMA smoothing
        self._grad_e_prev_smooth = self._grad_e_smooth
        self._grad_e_smooth = (
            (1.0 - self.ema_lambda) * self._grad_e_smooth
            + self.ema_lambda * grad_e_raw
        )

        # Persistence tracking
        if self._grad_e_smooth < 0:
            self._negative_streak += 1
        else:
            self._negative_streak = 0

        self._prev_avg_energy = avg_energy
        self._history.append(self._grad_e_smooth)
        return grad_e_raw

    @property
    def value(self):
        """Current smoothed ∇E value."""
        return self._grad_e_smooth

    @property
    def confirmed_negative(self):
        """True if ∇E has been negative for persistence_window generations."""
        return self._negative_streak >= self.persistence_window

    @property
    def second_derivative(self):
        """∇²E — acceleration of energy change."""
        return self._grad_e_smooth - self._grad_e_prev_smooth

    def normalized(self, k=1.0):
        """Return ∇E normalized to [0, 1] where 1 = extreme deficit.

        We negate so that negative gradient (bad) → positive stress signal.
        """
        if not self.confirmed_negative:
            # If not persistently negative, dampen the signal
            return _sigmoid_normalize(-self._grad_e_smooth * 0.3, k)
        return _sigmoid_normalize(-self._grad_e_smooth, k)


class ReproductiveFailureRate:
    """Tracks Φ = failed_reproductions / max(attempts, 1)."""

    def __init__(self):
        self._attempts = 0
        self._failures = 0
        self._phi = 0.0

    def record_generation(self, attempts, successes):
        """Update with this generation's reproduction results."""
        self._attempts = max(attempts, 0)
        failures = max(0, attempts - successes)
        self._failures = failures
        self._phi = failures / max(attempts, 1)

    @property
    def value(self):
        return self._phi

    def normalized(self, k=5.0):
        """Φ normalized to [0, 1]."""
        return _sigmoid_normalize(self._phi, k)


class VarianceCollapseRate:
    """Tracks -dVar(Γ)/dt from gamma variance history.

    Positive output = variance is collapsing (bad).
    """

    def __init__(self, window=10):
        self._variance_history = deque(maxlen=window)
        self._dvar_dt = 0.0

    def update(self, gamma_variance):
        """Update with current generation's gamma variance."""
        self._variance_history.append(gamma_variance)
        if len(self._variance_history) >= 2:
            # Rate of change of variance
            dvar = self._variance_history[-1] - self._variance_history[-2]
            self._dvar_dt = -dvar  # Negate: collapsing variance → positive signal
        else:
            self._dvar_dt = 0.0

    @property
    def value(self):
        """Positive = variance collapsing, negative = variance expanding."""
        return self._dvar_dt

    def normalized(self, k=10.0):
        """Collapse rate normalized to [0, 1]."""
        return _sigmoid_normalize(self._dvar_dt, k)


class CompositeStressIndex:
    """Ψ — weighted combination of four stress signals.

    Ψ = w1·∇E + w2·Φ + w3·m + w4·V

    Normalized to [0, 1].
    """

    DEFAULT_WEIGHTS = {
        'energy_gradient': 0.55,
        'reproductive_failure': 0.20,
        'mortality': 0.10,
        'variance_collapse': 0.15,
    }

    def __init__(self, weights=None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.energy_gradient = EnergyGradient(ema_lambda=0.2, persistence_window=3)
        self.reproductive_failure = ReproductiveFailureRate()
        self.variance_collapse = VarianceCollapseRate(window=10)

        self._mortality_rate = 0.0
        self._psi = 0.0
        self._components = {}
        self._history = deque(maxlen=100)

    def update(self, *, avg_energy, basal_burn, repro_attempts, repro_successes,
               deaths, population_size, gamma_variance):
        """Compute Ψ from current generation statistics.

        Returns Ψ value in [0, 1].
        """
        # Update component trackers
        self.energy_gradient.update(avg_energy, basal_burn)
        self.reproductive_failure.record_generation(repro_attempts, repro_successes)
        self.variance_collapse.update(gamma_variance)

        # Mortality
        self._mortality_rate = deaths / max(population_size, 1)

        # Normalized components — use reduced k to avoid false positives
        # in stable environments where small noise produces non-zero signals.
        # Dead-zone offset subtracts baseline noise floor before normalization.
        grad_e_norm = self.energy_gradient.normalized(k=1.0)
        phi_norm = self.reproductive_failure.normalized(k=3.0)
        mort_norm = _sigmoid_normalize(self._mortality_rate - 0.10, k=3.0)  # 10% baseline mortality dead-zone
        var_norm = self.variance_collapse.normalized(k=10.0)

        # Store for inspection
        self._components = {
            'energy_gradient': grad_e_norm,
            'reproductive_failure': phi_norm,
            'mortality': mort_norm,
            'variance_collapse': var_norm,
        }

        # Weighted sum
        w = self.weights
        self._psi = (
            w['energy_gradient'] * grad_e_norm
            + w['reproductive_failure'] * phi_norm
            + w['mortality'] * mort_norm
            + w['variance_collapse'] * var_norm
        )

        # Clamp to [0, 1]
        self._psi = max(0.0, min(1.0, self._psi))
        self._history.append(self._psi)

        return self._psi

    @property
    def psi(self):
        """Current Ψ value."""
        return self._psi

    @property
    def components(self):
        """Dict of individual normalized component values."""
        return self._components.copy()

    @property
    def history(self):
        """Recent Ψ history."""
        return list(self._history)
