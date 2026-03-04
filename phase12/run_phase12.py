"""
Phase-12: Panic Architecture Experiment Runner

Runs the regime-flip experiment (A→B) with the Panic Architecture active,
then compares recovery latency against the Phase-11 baseline.

Falsification criteria:
  1. Recovery latency decreases (Ms.gamma shifts within 50 gens vs 250+)
  2. Hysteresis lock is broken (Ms.gamma deviates >0.05 from 0.500)
  3. Adaptation occurs before population collapse
  4. No sustained mutation meltdown in stable regimes
  5. False positive rate <5% in Phase A
  6. Controlled exit — system returns to CALM after adaptation

Usage:
  cd D:\\Techbilla\\development\\platform\\mono-phase1
  python phase12/run_phase12.py --seed 42 --generations-a 500 --generations-b 250
"""

import argparse
import json
import os
import random
import statistics
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from phase10.observer import Phase10Observer
from phase12.stress_index import CompositeStressIndex
from phase12.panic_controller import PanicController


def create_identity_for_env(env_type, mutation_rate=None):
    """Create CoreIdentity matching Phase-11 regime flip parameters."""
    base = {
        'E_m': 200, 'E_s': 5, 'E_r': 1000,
        'c_B': 1, 'c_M': 2, 'c_R': 1, 'c_K': 3, 'c_P': 1,
        'burn_weights': (0.5, 0.3, 0.2),
        'mutation_rate': mutation_rate if mutation_rate is not None else 0.105,
        'initial_energy': 50, 'basal_burn': 0,
        'action_cost_multiplier': 1, 'initial_structure_size': 10,
        'decay_rate': 0.05, 'split_ratio': 0.5,
        'E_quiescence': 5, 'S_quiescence': 5,
        'S_critical': 8, 'E_maintenance_min': 10, 'repair_efficiency': 0.8,
        'E_repro': 60, 'S_repro': 5, 'r': 0.1, 'C_divide': 5,
        'epsilon_E': 2, 'epsilon_S': 1, 'stability_window': 10,
        'child_survival_cycles': 20, 'birth_stress_cycles': 5,
        'regulator_alpha': 0.1, 'regulator_beta': 0.2, 'regulator_gamma': 0.3,
        'regulator_mutation_rate': 0.01,
        'alpha_O': 1000.0, 'tau_max': 1000,
        'k_coord': 0.1, 'tau_sense': 0.1, 'tau_signal': 0.1, 'tau_act': 0.1,
        'latency_drift_rate': 0.01, 'size_penalty_factor': 0.1,
        'prediction_horizon': 10.0, 'number_of_predictive_modules': 3,
        'arbitration_delay': 1.0, 'module_horizon_adapt_rate': 0.1,
        'global_integrator_capacity': 10.0,
        'arbitration_mechanism': 'temporal_sequencing',
        'scene_change_threshold': 2.0, 'scene_min_duration': 3,
        'kappa_pred': 0.5,
        'cog_mutation_rate': 0.1, 'structural_mutation_rate': 0.02,
        'base_gating_threshold': 0.5, 'base_arbitration_frequency': 1,
    }

    if env_type == 'A':
        base.update({
            'E_i': 30, 'alpha_O': 2000.0, 'k_coord': 0.5,
        })
    elif env_type == 'B':
        base.update({
            'E_i': 0.1, 'basal_burn': 2.0, 'alpha_O': 0.5,
            'k_coord': 0.001, 'initial_energy': 150.0, 'E_repro': 100,
        })

    return CoreIdentity(**base)


def get_env_params(env_type):
    """Return env_params dict for a given environment type."""
    if env_type == 'A':
        return {'E_i': 30.0, 'basal_burn': 0.0, 'alpha_O': 2000.0}
    else:
        return {'E_i': 0.1, 'basal_burn': 2.0, 'alpha_O': 0.5}


def run_generation(cells, species_memory, generation, observer, env_type,
                   max_cycles=50, panic_state=None):
    """Run one generation and return survivors + statistics."""
    organism_data = []
    surviving_cells = []
    children = []
    repro_attempts = 0
    repro_successes = 0
    deaths = 0
    energy_sum = 0.0
    energy_count = 0

    env_params = get_env_params(env_type)

    for cell in cells:
        for cycle_num in range(max_cycles):
            death_reason, log, child = cycle(
                cell,
                observer=observer,
                species_defaults={'__observer__': observer},
                generation=generation,
                species_memory=species_memory,
                env_params=env_params,
                organism_data_list=organism_data,
                panic_state=panic_state,
            )
            if death_reason:
                deaths += 1
                break

        if not death_reason:
            surviving_cells.append(cell)
            energy_sum += cell.energy.E
            energy_count += 1

        if child:
            children.append(child)
            repro_successes += 1

        # Count any cell that survived long enough to be eligible as an attempt
        if cell.reproduction_eligible:
            repro_attempts += 1

    # Include children in survivors
    surviving_cells.extend(children)

    avg_energy = energy_sum / max(energy_count, 1)
    gamma_values = [c.gating_threshold for c in surviving_cells]
    gamma_variance = (
        statistics.variance(gamma_values) if len(gamma_values) >= 2 else 0.0
    )

    species_memory.update(organism_data)
    observer.emit_lineage_drift_violations()

    stats = {
        'avg_energy': avg_energy,
        'deaths': deaths,
        'population_size': len(cells),
        'survivors': len(surviving_cells),
        'repro_attempts': repro_attempts,
        'repro_successes': repro_successes,
        'gamma_variance': gamma_variance,
        'ms_gamma': species_memory.Ms.get('gamma', 0.5),
        'basal_burn': env_params.get('basal_burn', 0.0),
    }

    return surviving_cells, stats


def create_next_generation(surviving_cells, target_pop, env_type):
    """Backfill population to target size with fresh cells."""
    new_cells = surviving_cells.copy()
    while len(new_cells) < target_pop:
        mutation_rate = 0.20 if env_type == 'B' else None
        fresh_id = create_identity_for_env(env_type, mutation_rate=mutation_rate)
        fresh_cell = MonoCell(fresh_id)
        fresh_cell.lineage_id = str(random.randint(1000, 9999))
        if env_type == 'B':
            cog_mut_rate = 0.20
            fresh_cell.gating_threshold = max(
                0.0, min(1.0, fresh_cell.gating_threshold + random.gauss(-0.1, cog_mut_rate))
            )
        new_cells.append(fresh_cell)
    return new_cells


def run_phase12(seed=42, generations_a=500, generations_b=250, target_pop=50):
    """Run the full Phase-12 experiment with Panic Architecture."""

    random.seed(seed)
    observer = Phase10Observer(seed=seed, env='phase12_panic')

    # Initialize components
    species_memory = SpeciesMemory(alpha=0.1, epsilon=0.1)
    stress_index = CompositeStressIndex()
    panic_controller = PanicController()

    # Initialize population in Environment A
    initial_id = create_identity_for_env('A')
    population = [MonoCell(initial_id) for _ in range(target_pop)]

    history = []
    total_gens = generations_a + generations_b

    # Track false positive activations in Phase A
    phase_a_panic_activations = 0

    for gen in range(total_gens):
        env_type = 'A' if gen < generations_a else 'B'
        observer.set_generation(gen)

        # Get panic state from controller
        panic_output = panic_controller.get_outputs(stress_index.psi)

        # Run generation
        population, stats = run_generation(
            population, species_memory, gen, observer, env_type,
            panic_state=panic_output,
        )

        survival_rate = len(population) / target_pop

        # Compute stress index
        psi = stress_index.update(
            avg_energy=stats['avg_energy'],
            basal_burn=stats['basal_burn'],
            repro_attempts=stats['repro_attempts'],
            repro_successes=stats['repro_successes'],
            deaths=stats['deaths'],
            population_size=stats['population_size'],
            gamma_variance=stats['gamma_variance'],
        )

        # Update panic controller
        panic_output = panic_controller.update(psi, generation=gen)

        # Apply memory softening if epsilon > 0
        eps = panic_output['memory_softening_eps']
        if eps > 0:
            # Current generation's survivor statistics
            current_phi = {
                'gamma': sum(c.gating_threshold for c in population) / max(len(population), 1),
                'module_count': sum(c.module_count for c in population) / max(len(population), 1),
                'tau_budget': sum(c.get_tau_organism() for c in population) / max(len(population), 1),
                'energy_ceiling': sum(c.energy.E for c in population) / max(len(population), 1),
            }
            species_memory.soften(eps, current_phi)

        # Track false positives in Phase A
        if env_type == 'A' and panic_output['state'] != 'CALM':
            phase_a_panic_activations += 1

        # Backfill population
        population = create_next_generation(population, target_pop, env_type)

        # Record history
        entry = {
            'generation': gen,
            'env': env_type,
            'survival_rate': survival_rate,
            'psi': psi,
            'panic_state': panic_output['state'],
            'mutation_multiplier': panic_output['mutation_multiplier'],
            'memory_softening_eps': panic_output['memory_softening_eps'],
            'ms_gamma': stats['ms_gamma'],
            'avg_energy': stats['avg_energy'],
            'gamma_variance': stats['gamma_variance'],
            'deaths': stats['deaths'],
            'repro_attempts': stats['repro_attempts'],
            'repro_successes': stats['repro_successes'],
            'grad_e': stress_index.energy_gradient.value,
            'grad_e_confirmed_negative': stress_index.energy_gradient.confirmed_negative,
            'stress_components': stress_index.components,
        }
        history.append(entry)

        if gen % 50 == 0:
            print(
                f"Gen {gen:4d} [{env_type}] | "
                f"Ψ={psi:.3f} {panic_output['state']:5s} | "
                f"Ms.γ={stats['ms_gamma']:.4f} | "
                f"Surv={survival_rate:.2f} | "
                f"mut×{panic_output['mutation_multiplier']:.1f} | "
                f"ε={panic_output['memory_softening_eps']:.3f}"
            )

    # === Falsification Analysis ===
    print("\n" + "=" * 70)
    print("PHASE-12 FALSIFICATION ANALYSIS")
    print("=" * 70)

    # 1. Detection: Did ∇E spike at regime flip?
    flip_gens = [h for h in history if h['generation'] in range(generations_a, generations_a + 20)]
    if flip_gens:
        max_grad = min(h['grad_e'] for h in flip_gens)
        print(f"\n[1] ∇E at flip: min={max_grad:.4f} (should be strongly negative)")

    # 2. Recovery latency: When did Ms.gamma first deviate >0.05 from 0.500?
    first_deviation_gen = None
    for h in history:
        if h['generation'] >= generations_a:
            if abs(h['ms_gamma'] - 0.500) > 0.05:
                first_deviation_gen = h['generation'] - generations_a
                break
    if first_deviation_gen is not None:
        print(f"[2] Ms.gamma deviation >0.05: gen {first_deviation_gen} after flip (target: <50, baseline: 250+)")
    else:
        print(f"[2] Ms.gamma deviation >0.05: NOT REACHED (hysteresis lock persists)")

    # 3. Panic activation timing
    first_alert = None
    first_panic = None
    for trans in panic_controller.transition_log:
        if trans['to'] == 'ALERT' and first_alert is None:
            first_alert = trans['generation']
        if trans['to'] == 'PANIC' and first_panic is None:
            first_panic = trans['generation']

    if first_alert is not None:
        delay_alert = first_alert - generations_a if first_alert >= generations_a else first_alert
        print(f"[3] First ALERT: gen {first_alert} ({delay_alert} gens {'after' if first_alert >= generations_a else 'before'} flip)")
    if first_panic is not None:
        delay_panic = first_panic - generations_a if first_panic >= generations_a else first_panic
        print(f"    First PANIC: gen {first_panic} ({delay_panic} gens {'after' if first_panic >= generations_a else 'before'} flip)")

    # 4. False positive rate in Phase A
    fp_rate = phase_a_panic_activations / max(generations_a, 1)
    print(f"[4] False positive rate in Phase A: {fp_rate:.2%} (target: <5%)")

    # 5. Final state
    final_state = history[-1]['panic_state'] if history else 'UNKNOWN'
    final_gamma = history[-1]['ms_gamma'] if history else 0.5
    print(f"[5] Final state: {final_state}, Ms.γ={final_gamma:.4f}")

    # 6. Controlled exit check
    return_to_calm = any(
        t['to'] == 'CALM' and t['generation'] is not None and t['generation'] > generations_a
        for t in panic_controller.transition_log
    )
    print(f"[6] Return to CALM after panic: {'YES' if return_to_calm else 'NO'}")

    # === Output Artifacts ===
    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('phase12_artifacts', f'phase12_seed{seed}_{stamp}')
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'stress_history.json'), 'w') as f:
        json.dump(history, f, indent=2)

    with open(os.path.join(out_dir, 'panic_transitions.json'), 'w') as f:
        json.dump(panic_controller.transition_log, f, indent=2)

    falsification = {
        'seed': seed,
        'generations_a': generations_a,
        'generations_b': generations_b,
        'grad_e_at_flip': min(h['grad_e'] for h in flip_gens) if flip_gens else None,
        'first_deviation_gen': first_deviation_gen,
        'first_alert_gen': first_alert,
        'first_panic_gen': first_panic,
        'false_positive_rate': fp_rate,
        'final_state': final_state,
        'final_ms_gamma': final_gamma,
        'return_to_calm': return_to_calm,
        'total_transitions': len(panic_controller.transition_log),
    }
    with open(os.path.join(out_dir, 'falsification.json'), 'w') as f:
        json.dump(falsification, f, indent=2)

    print(f"\nArtifacts written to: {out_dir}")

    return history, falsification


def main():
    ap = argparse.ArgumentParser(description='Phase-12 Panic Architecture Experiment')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--generations-a', type=int, default=500)
    ap.add_argument('--generations-b', type=int, default=250)
    ap.add_argument('--target-pop', type=int, default=50)
    args = ap.parse_args()

    run_phase12(
        seed=args.seed,
        generations_a=args.generations_a,
        generations_b=args.generations_b,
        target_pop=args.target_pop,
    )


if __name__ == '__main__':
    main()
