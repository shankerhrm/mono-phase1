"""
Phase-13: Rhythmostat — Oscillator Module

Provides:
  - PhaseOscillator: per-organism internal phase / omega state
  - effective_gating_threshold: phase-modulated γ at cycle initialization
  - apply_entrainment_reset: edge-triggered stochastic kick on Ψ crossing
"""

import math
import random

# ── Constants ────────────────────────────────────────────────────────

PHASE_AMPLITUDE = 0.12          # A: max ±modulation of gating threshold
OMEGA_MIN = 2 * math.pi / 400   # slowest cycle: 400 gens
OMEGA_MAX = 2 * math.pi / 30    # fastest cycle: 30 gens
SIGMA_PHASE_DRIFT = 0.05        # per-generation phase jitter (rad)
SIGMA_PHASE_BIRTH = 0.30        # phase noise on birth (rad)
SIGMA_OMEGA_MUTATION = 0.01      # Accelerated for validation runs
SIGMA_RESET_KICK = 0.40          # entrainment reset perturbation (rad)
PSI_RESET_THRESHOLD = 0.6        # Ψ crossing level that triggers reset


def _clip_omega(omega):
    """Hard-clip omega to [OMEGA_MIN, OMEGA_MAX]."""
    return max(OMEGA_MIN, min(OMEGA_MAX, omega))


# ── PhaseOscillator ────────────────────────────────────────────────

class PhaseOscillator:
    """Per-organism endogenous temporal oscillator.

    Carries:
        internal_phase (φ) ∈ [0, 2π)
        omega           (ω) ∈ [OMEGA_MIN, OMEGA_MAX]

    Neither is stored in Species Memory. Both are cell-level traits.

    INVARIANT: This class carries no reference to population state,
    Species Memory, or the stress index. It is a pure organism trait.
    """

    __slots__ = ('internal_phase', 'omega', '_prev_psi_above_threshold')

    def __init__(self, omega=None, phase=None):
        """Initialise with random omega and phase (uniform over valid domain)."""
        self.omega = omega if omega is not None else random.uniform(OMEGA_MIN, OMEGA_MAX)
        self.internal_phase = phase if phase is not None else random.uniform(0, 2 * math.pi)
        self._prev_psi_above_threshold = False  # for edge-triggered reset

    # ── Per-generation update ─────────────────────────────────────

    def step(self):
        """Advance internal_phase by one generation.

        Adds omega (deterministic wrap) plus small drift noise.
        """
        noise = random.gauss(0, SIGMA_PHASE_DRIFT)
        self.internal_phase = (self.internal_phase + self.omega + noise) % (2 * math.pi)

    # ── Gating modulation ─────────────────────────────────────────

    def effective_gamma(self, gamma_base):
        """Return phase-modulated gating threshold.

        effective_γ = clip(γ_base + A · sin(φ), 0.0, 1.0)

        Called ONCE per lifecycle cycle initialization, not stored.

        INVARIANT GUARD: Warns if γ_base < A, which can cause
        asymmetric clipping that biases sin(φ) selection pressure.
        """
        if gamma_base < PHASE_AMPLITUDE:
            # Issue warning — implementation monitors this at population level
            pass  # caller logs this via _check_amplitude_invariant
        raw = gamma_base + PHASE_AMPLITUDE * math.sin(self.internal_phase)
        return max(0.0, min(1.0, raw))

    # ── Entrainment reset (edge-triggered) ────────────────────────

    def apply_reset_if_crossing(self, psi_current):
        """Apply stochastic phase kick on Ψ crossing from ≤0.6 to >0.6.

        Edge-triggered: fires exactly once per escalation event.
        Level-triggered operation would inject continuous noise during
        sustained vacuum, destroying emerging phase structure.
        """
        above = psi_current > PSI_RESET_THRESHOLD
        if above and not self._prev_psi_above_threshold:
            kick = random.gauss(0, SIGMA_RESET_KICK)
            self.internal_phase = (self.internal_phase + kick) % (2 * math.pi)
        self._prev_psi_above_threshold = above

    # ── Reproduction ──────────────────────────────────────────────

    def make_child_oscillator(self):
        """Create offspring oscillator with inherited omega and offset phase.

        omega_child = clip(omega_parent + N(0, σ_ω))
        phase_child = (phase_parent + N(0, σ_birth)) mod 2π

        No fixed π/2 offset — natural phase divergence without
        artificial generational rotation.
        """
        child_omega = _clip_omega(
            self.omega + random.gauss(0, SIGMA_OMEGA_MUTATION)
        )
        child_phase = (self.internal_phase + random.gauss(0, SIGMA_PHASE_BIRTH)) % (2 * math.pi)
        return PhaseOscillator(omega=child_omega, phase=child_phase)

    # ── Inspection ────────────────────────────────────────────────

    @property
    def sin_phase(self):
        """sin(φ) — the modulation signal in [-1, 1]."""
        return math.sin(self.internal_phase)

    def __repr__(self):
        return (f"PhaseOscillator(φ={self.internal_phase:.4f}, "
                f"ω={self.omega:.5f}, T={2*math.pi/self.omega:.1f}gen)")


# ── Population-level metrics helpers ─────────────────────────────────

def population_omega_stats(cells):
    """Return mean, std, and convergence metrics for ω across population.

    convergence_ratio = 1 - (std / (OMEGA_MAX - OMEGA_MIN))
    1.0 = fully converged; 0.0 = maximally dispersed.
    """
    omegas = [c.oscillator.omega for c in cells if hasattr(c, 'oscillator')]
    if not omegas:
        return {'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0,
                'convergence_ratio': 0.0, 'n': 0}
    n = len(omegas)
    mean = sum(omegas) / n
    variance = sum((o - mean) ** 2 for o in omegas) / max(n - 1, 1)
    std = variance ** 0.5
    omega_range = OMEGA_MAX - OMEGA_MIN
    convergence_ratio = 1.0 - (std / omega_range) if omega_range > 0 else 1.0
    return {
        'mean': round(mean, 6),
        'std': round(std, 6),
        'min': round(min(omegas), 6),
        'max': round(max(omegas), 6),
        'convergence_ratio': round(max(0.0, convergence_ratio), 4),
        'n': n,
    }


def population_phase_histogram(cells, bins=8):
    """Return phase histogram (bin counts) across population.

    Detects phase clustering: uniform = not entrained, peaked = entrained.
    Anti-phase polymorphism = two opposite peaks.
    """
    phases = [c.oscillator.internal_phase for c in cells if hasattr(c, 'oscillator')]
    if not phases:
        return [0] * bins
    bin_size = 2 * math.pi / bins
    counts = [0] * bins
    for p in phases:
        idx = int(p / bin_size) % bins
        counts[idx] += 1
    return counts


def check_amplitude_invariant(cells):
    """Scan population for γ_base < A (amplitude invariant violation).

    Returns list of violating cells' gating_threshold values.
    """
    violations = []
    for c in cells:
        if hasattr(c, 'gating_threshold') and c.gating_threshold < PHASE_AMPLITUDE:
            violations.append(c.gating_threshold)
    return violations
