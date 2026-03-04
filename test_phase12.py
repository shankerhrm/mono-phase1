#!/usr/bin/env python3
"""
Phase-12: Unit Tests

Tests for stress index, panic controller, memory softening, and invariant
preservation. Matches existing test style (no pytest dependency).
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from phase12.stress_index import (
    EnergyGradient,
    ReproductiveFailureRate,
    VarianceCollapseRate,
    CompositeStressIndex,
    _sigmoid_normalize,
)
from phase12.panic_controller import PanicController, PanicState
from species_memory import SpeciesMemory


def test_sigmoid_normalize():
    """Sigmoid normalization output is bounded [0, 1]."""
    assert 0.0 <= _sigmoid_normalize(0.0) <= 1.0
    assert _sigmoid_normalize(100.0) > 0.95, "Large positive should saturate near 1"
    assert _sigmoid_normalize(-100.0) < 0.05, "Large negative should saturate near 0"
    assert abs(_sigmoid_normalize(0.0)) < 0.01, "Zero input should be near 0"
    print("PASS: test_sigmoid_normalize")


def test_energy_gradient_computation():
    """Verify ∇E with known data series."""
    eg = EnergyGradient(ema_lambda=0.5, persistence_window=3)

    # Generation 0: init
    eg.update(100.0, basal_burn=2.0)
    assert eg.value == 0.0, "First update should be 0"

    # Generation 1: energy drops — ΔE = -20, normalized by burn=2 → -10
    eg.update(80.0, basal_burn=2.0)
    assert eg.value < 0, f"Expected negative ∇E, got {eg.value}"

    # Generation 2: further drop
    eg.update(60.0, basal_burn=2.0)
    assert eg.value < -1.0, f"Expected strongly negative ∇E, got {eg.value}"

    # Not yet 3 consecutive negatives at gen 2 (only 2 updates after init)
    # After 3 negative updates, should be confirmed
    eg.update(50.0, basal_burn=2.0)
    assert eg.confirmed_negative, "Should be confirmed negative after 3 consecutive"

    print("PASS: test_energy_gradient_computation")


def test_energy_gradient_persistence():
    """Persistence check prevents single-gen noise from confirming."""
    eg = EnergyGradient(ema_lambda=0.5, persistence_window=3)

    eg.update(100.0, basal_burn=1.0)
    eg.update(90.0, basal_burn=1.0)  # negative
    eg.update(95.0, basal_burn=1.0)  # mixed — could reset streak

    # After a recovery, streak should reset
    # The EMA smoothing means the value might still be slightly negative,
    # but if it goes positive the streak breaks
    eg.update(110.0, basal_burn=1.0)  # Strong positive jump
    eg.update(120.0, basal_burn=1.0)  # Another positive
    assert not eg.confirmed_negative, "Positive jumps should break negative streak"

    print("PASS: test_energy_gradient_persistence")


def test_reproductive_failure_rate():
    """Φ computation."""
    rf = ReproductiveFailureRate()
    rf.record_generation(attempts=10, successes=8)
    assert abs(rf.value - 0.2) < 0.01, f"Expected Φ=0.2, got {rf.value}"

    rf.record_generation(attempts=10, successes=0)
    assert abs(rf.value - 1.0) < 0.01, "All failures → Φ=1.0"

    rf.record_generation(attempts=0, successes=0)
    assert rf.value == 0.0, "No attempts → Φ=0"

    print("PASS: test_reproductive_failure_rate")


def test_variance_collapse_rate():
    """Variance collapse rate tracks -dVar/dt."""
    vcr = VarianceCollapseRate(window=5)

    # Variance increasing → collapse rate should be negative (expanding)
    vcr.update(0.1)
    vcr.update(0.2)
    assert vcr.value < 0, f"Increasing variance → negative collapse rate, got {vcr.value}"

    # Variance decreasing → collapse rate should be positive (collapsing)
    vcr.update(0.15)
    assert vcr.value > 0, f"Decreasing variance → positive collapse rate, got {vcr.value}"

    print("PASS: test_variance_collapse_rate")


def test_stress_index_weights():
    """Verify Ψ normalization and bounds."""
    csi = CompositeStressIndex()

    # Gentle update — should be near 0
    psi = csi.update(
        avg_energy=100.0, basal_burn=0.0,
        repro_attempts=10, repro_successes=10,
        deaths=0, population_size=50,
        gamma_variance=0.1,
    )
    assert 0.0 <= psi <= 1.0, f"Ψ should be in [0,1], got {psi}"

    print("PASS: test_stress_index_weights")


def test_stress_index_crisis():
    """Verify Ψ rises under crisis conditions."""
    csi = CompositeStressIndex()

    # Init with healthy values
    for _ in range(5):
        csi.update(
            avg_energy=100.0, basal_burn=0.0,
            repro_attempts=10, repro_successes=10,
            deaths=0, population_size=50,
            gamma_variance=0.1,
        )

    healthy_psi = csi.psi

    # Now introduce crisis: energy drops, deaths, repro failure
    for _ in range(5):
        crisis_psi = csi.update(
            avg_energy=10.0, basal_burn=2.0,
            repro_attempts=10, repro_successes=1,
            deaths=30, population_size=50,
            gamma_variance=0.01,
        )

    assert crisis_psi > healthy_psi, f"Crisis Ψ ({crisis_psi}) should exceed healthy ({healthy_psi})"
    assert crisis_psi > 0.1, f"Crisis Ψ should be non-trivial, got {crisis_psi}"

    print("PASS: test_stress_index_crisis")


def test_panic_state_machine_transitions():
    """Test CALM→ALERT→PANIC with hysteresis."""
    pc = PanicController(
        confirmation_window=3,
        min_dwell_panic=5,
    )

    # Start in CALM
    assert pc.state == PanicState.CALM

    # 3 gens above 0.3 → ALERT
    for gen in range(3):
        result = pc.update(0.35, generation=gen)
    assert result['state'] == 'ALERT', f"Expected ALERT after 3 gens >0.3, got {result['state']}"

    # 3 gens above 0.6 → PANIC
    for gen in range(3, 6):
        result = pc.update(0.65, generation=gen)
    assert result['state'] == 'PANIC', f"Expected PANIC after 3 gens >0.6, got {result['state']}"

    # Must stay in PANIC for at least 5 gens even if Ψ drops
    result = pc.update(0.3, generation=6)
    assert result['state'] == 'PANIC', "Should stay in PANIC (dwell time < 5)"

    # After 5+ gens in PANIC with Ψ < 0.4, should exit to ALERT
    for gen in range(7, 12):
        result = pc.update(0.35, generation=gen)
    assert result['state'] == 'ALERT', f"Expected ALERT after dwell time + low Ψ, got {result['state']}"

    # 3 gens below 0.15 → CALM
    for gen in range(12, 15):
        result = pc.update(0.10, generation=gen)
    assert result['state'] == 'CALM', f"Expected CALM after 3 gens <0.15, got {result['state']}"

    print("PASS: test_panic_state_machine_transitions")


def test_panic_dwell_time():
    """Verify minimum dwell time enforcement in PANIC."""
    pc = PanicController(
        confirmation_window=2,
        min_dwell_panic=5,
    )

    # Rush to PANIC
    for gen in range(2):
        pc.update(0.35, generation=gen)
    for gen in range(2, 4):
        pc.update(0.65, generation=gen)
    assert pc.state == PanicState.PANIC

    # Try to exit immediately — should fail
    for gen in range(4, 7):
        result = pc.update(0.3, generation=gen)
    # Only 3 gens in PANIC — should still be PANIC (need 5)
    assert result['state'] == 'PANIC', f"Should stay in PANIC (only 3 gens), got {result['state']}"

    print("PASS: test_panic_dwell_time")


def test_mutation_multiplier_bounded():
    """Mutation multiplier never exceeds 3×."""
    pc = PanicController(
        confirmation_window=1,
        min_dwell_panic=1,
        mutation_ceiling=3.0,
    )

    # Force into PANIC
    pc.update(0.5, generation=0)  # → ALERT
    pc.update(0.9, generation=1)  # → PANIC

    # At maximum Ψ = 1.0
    result = pc.get_outputs(1.0)
    assert result['mutation_multiplier'] <= 3.0, f"Multiplier {result['mutation_multiplier']} exceeds ceiling"

    # In CALM, multiplier should be 1.0
    pc2 = PanicController()
    result2 = pc2.get_outputs(0.5)
    assert result2['mutation_multiplier'] == 1.0, f"CALM multiplier should be 1.0, got {result2['mutation_multiplier']}"

    print("PASS: test_mutation_multiplier_bounded")


def test_memory_softening_quadratic():
    """ε is quadratic in Ψ and bounded."""
    pc = PanicController(
        confirmation_window=1,
        epsilon_max=0.5,
    )

    # In CALM → ε = 0
    result = pc.get_outputs(0.3)
    assert result['memory_softening_eps'] == 0.0, "CALM should have ε=0"

    # Force to ALERT
    pc.update(0.5, generation=0)

    # At Ψ=0.5: ε = 0.5 * 0.5² = 0.125
    result = pc.get_outputs(0.5)
    expected = 0.5 * (0.5 ** 2)
    assert abs(result['memory_softening_eps'] - expected) < 0.01, \
        f"Expected ε≈{expected}, got {result['memory_softening_eps']}"

    # At Ψ=1.0: ε = 0.5 * 1.0² = 0.5
    result = pc.get_outputs(1.0)
    assert result['memory_softening_eps'] <= 0.5, f"ε should be ≤0.5, got {result['memory_softening_eps']}"

    print("PASS: test_memory_softening_quadratic")


def test_memory_softening_species_memory():
    """Memory softening shifts Ms toward current data."""
    sm = SpeciesMemory(alpha=0.01)
    initial_gamma = sm.Ms['gamma']
    assert initial_gamma == 0.5

    # Soften toward gamma=0.3
    current_phi = {'gamma': 0.3, 'module_count': 2.0, 'tau_budget': 3.0, 'energy_ceiling': 5.0}
    sm.soften(0.4, current_phi)

    # Ms should shift toward 0.3
    new_gamma = sm.Ms['gamma']
    expected = (1 - 0.4) * 0.5 + 0.4 * 0.3  # = 0.42
    assert abs(new_gamma - expected) < 0.001, f"Expected γ≈{expected}, got {new_gamma}"

    # ε=0 should be a no-op
    sm2 = SpeciesMemory()
    before = sm2.Ms.copy()
    sm2.soften(0.0, current_phi)
    assert sm2.Ms == before, "ε=0 should not change Ms"

    # ε > 0.5 should be capped
    sm3 = SpeciesMemory()
    sm3.soften(0.9, current_phi)
    # The cap is 0.5, so: (1-0.5)*0.5 + 0.5*0.3 = 0.4
    capped_gamma = sm3.Ms['gamma']
    expected_capped = (1 - 0.5) * 0.5 + 0.5 * 0.3
    assert abs(capped_gamma - expected_capped) < 0.001, \
        f"ε should be capped at 0.5, expected γ≈{expected_capped}, got {capped_gamma}"

    print("PASS: test_memory_softening_species_memory")


def test_invariant_preservation():
    """Phase 10 IOBA invariant holds: Ms doesn't affect runtime behavior."""
    # The soften() method only modifies Ms (population prior)
    # It does not modify any organism's runtime state
    sm = SpeciesMemory()

    # Verify only allowed keys exist
    sm._validate_memory_state()

    # After softening, keys should still be valid
    sm.soften(0.3, {'gamma': 0.2, 'module_count': 1.0, 'tau_budget': 2.0, 'energy_ceiling': 8.0})
    sm._validate_memory_state()

    # Softening with unknown keys should be safe (ignored)
    sm.soften(0.3, {'gamma': 0.2, 'unknown_key': 999.0})
    sm._validate_memory_state()

    # Verify no policy or executable content in Ms
    for k, v in sm.Ms.items():
        assert isinstance(v, (int, float)), f"Ms[{k}] must be scalar, got {type(v)}"

    print("PASS: test_invariant_preservation")


def test_panic_controller_no_oscillation():
    """Borderline Ψ values should not cause rapid oscillation."""
    pc = PanicController(
        confirmation_window=3,
        min_dwell_panic=5,
    )

    # Oscillate Ψ around alert threshold
    states = []
    for gen in range(30):
        psi = 0.29 if gen % 2 == 0 else 0.31
        result = pc.update(psi, generation=gen)
        states.append(result['state'])

    transitions = sum(1 for i in range(1, len(states)) if states[i] != states[i - 1])
    assert transitions <= 3, f"Too many transitions ({transitions}) under oscillating Ψ"

    print("PASS: test_panic_controller_no_oscillation")


def main():
    tests = [
        test_sigmoid_normalize,
        test_energy_gradient_computation,
        test_energy_gradient_persistence,
        test_reproductive_failure_rate,
        test_variance_collapse_rate,
        test_stress_index_weights,
        test_stress_index_crisis,
        test_panic_state_machine_transitions,
        test_panic_dwell_time,
        test_mutation_multiplier_bounded,
        test_memory_softening_quadratic,
        test_memory_softening_species_memory,
        test_invariant_preservation,
        test_panic_controller_no_oscillation,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
