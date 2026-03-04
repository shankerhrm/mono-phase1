import unittest
import math
import random
from phase13.oscillator import PhaseOscillator, OMEGA_MIN, OMEGA_MAX, PHASE_AMPLITUDE, check_amplitude_invariant
from mono import MonoCell
from core.identity import CoreIdentity

def get_test_identity():
    return CoreIdentity(
        E_i=1.0, E_m=10.0, E_s=2.0, E_r=5.0,
        c_B=0.1, c_M=0.2, c_R=0.15, c_K=0.1, c_P=1.0,
        burn_weights=(0.5, 0.3, 0.2), mutation_rate=0.05,
        initial_energy=5.0, basal_burn=0.1, action_cost_multiplier=1.0,
        initial_structure_size=5, decay_rate=0.05, split_ratio=0.5,
        E_quiescence=1.0, S_quiescence=2,
        S_critical=3, E_maintenance_min=2.0, repair_efficiency=0.8,
        E_repro=5.0, S_repro=5, r=0.5, C_divide=1.0,
        epsilon_E=0.1, epsilon_S=0.1, stability_window=5,
        child_survival_cycles=5, birth_stress_cycles=2,
        regulator_alpha=0.5, regulator_beta=0.3, regulator_gamma=0.2,
        regulator_mutation_rate=0.01,
        alpha_O=10.0, tau_max=20.0, k_coord=1.0,
        tau_sense=0.5, tau_signal=0.5, tau_act=1.0, latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=2.0,
        number_of_predictive_modules=3, arbitration_delay=1.0,
        module_horizon_adapt_rate=0.1, global_integrator_capacity=10.0,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=1.0, scene_min_duration=5,
        kappa_pred=0.0,
        cog_mutation_rate=0.05, structural_mutation_rate=0.01,
        base_gating_threshold=0.5, base_arbitration_frequency=1
    )

class TestPhase13(unittest.TestCase):

    def setUp(self):
        # Create a basic identity for testing
        self.identity = get_test_identity()
        random.seed(42)

    def test_oscillator_initialization(self):
        osc = PhaseOscillator()
        self.assertGreaterEqual(osc.omega, OMEGA_MIN)
        self.assertLessEqual(osc.omega, OMEGA_MAX)
        self.assertGreaterEqual(osc.internal_phase, 0)
        self.assertLessEqual(osc.internal_phase, 2 * math.pi)

    def test_oscillator_step(self):
        osc = PhaseOscillator(omega=0.1, phase=0.0)
        # We expect phase + omega + noise. Noise is gauss(0, 0.05)
        # With seed 42, we can check a few steps
        osc.step()
        # phase should be approx 0.1
        self.assertAlmostEqual(osc.internal_phase, 0.1, delta=0.2)
        
        last_phase = osc.internal_phase
        osc.step()
        self.assertAlmostEqual(osc.internal_phase, last_phase + 0.1, delta=0.2)

    def test_effective_gamma(self):
        # Base gating 0.5, Amplitude 0.12
        osc = PhaseOscillator(phase=math.pi/2) # sin(pi/2) = 1
        eff = osc.effective_gamma(0.5)
        self.assertAlmostEqual(eff, 0.5 + 0.12)

        osc = PhaseOscillator(phase=3*math.pi/2) # sin(3pi/2) = -1
        eff = osc.effective_gamma(0.5)
        self.assertAlmostEqual(eff, 0.5 - 0.12)

    def test_gamma_clipping(self):
        # Test clipping at 0 and 1
        osc = PhaseOscillator(phase=math.pi/2)
        eff = osc.effective_gamma(0.95)
        self.assertAlmostEqual(eff, 1.0)

        osc = PhaseOscillator(phase=3*math.pi/2)
        eff = osc.effective_gamma(0.05)
        self.assertAlmostEqual(eff, 0.0)

    def test_omega_inheritance_mutation(self):
        parent = PhaseOscillator(omega=0.1)
        child = parent.make_child_oscillator()
        # omega should be parent.omega + N(0, 0.005)
        self.assertAlmostEqual(child.omega, 0.1, delta=0.03)
        self.assertGreaterEqual(child.omega, OMEGA_MIN)
        self.assertLessEqual(child.omega, OMEGA_MAX)

    def test_phase_inheritance_no_fixed_offset(self):
        parent = PhaseOscillator(phase=1.0)
        # Child phase = (parent.phase + N(0, 0.3)) mod 2pi
        child = parent.make_child_oscillator()
        self.assertAlmostEqual(child.internal_phase, 1.0, delta=1.0)
        # Verifying it doesn't have a fixed pi/2 offset (1.0 + 1.57 = 2.57)
        # With seed 42, first noise is small
        self.assertNotAlmostEqual(child.internal_phase, 1.0 + math.pi/2, delta=0.1)

    def test_entrainment_reset_edge_triggered(self):
        osc = PhaseOscillator(phase=1.0)
        
        # PSI 0.5 -> 0.7: Crossing!
        osc.apply_reset_if_crossing(0.5) # Prev = False
        start_phase = osc.internal_phase
        osc.apply_reset_if_crossing(0.7) # Cross! Kick applied
        self.assertNotEqual(osc.internal_phase, start_phase)
        
        # PSI 0.7 -> 0.8: Sustained, no kick
        mid_phase = osc.internal_phase
        osc.apply_reset_if_crossing(0.8) # Level high, no cross
        self.assertEqual(osc.internal_phase, mid_phase)
        
        # PSI 0.8 -> 0.5: Fall below
        osc.apply_reset_if_crossing(0.5)
        final_phase = osc.internal_phase
        self.assertEqual(final_phase, mid_phase)
        
        # PSI 0.5 -> 0.9: Crossing again!
        osc.apply_reset_if_crossing(0.9)
        self.assertNotEqual(osc.internal_phase, final_phase)

    def test_amplitude_invariant_guard(self):
        cells = []
        for g in [0.5, 0.15, 0.11, 0.05]: # 0.11 and 0.05 are below A=0.12
            cell = MonoCell(self.identity)
            cell.gating_threshold = g
            cells.append(cell)
        
        violations = check_amplitude_invariant(cells)
        self.assertEqual(len(violations), 2)
        self.assertIn(0.11, violations)
        self.assertIn(0.05, violations)

if __name__ == '__main__':
    unittest.main()
