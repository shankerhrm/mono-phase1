"""
Phase-12: Multi-Seed Robustness Validation

Runs Phase-12 across 20+ seeds with three experimental conditions:
  1. Sharp flip (A→B at varied gen)
  2. Gradual transition (A→B linearly interpolated over 50 gens)
  3. Oscillatory (A→B→A→B every 150 gens)

Produces aggregate statistics and per-seed falsification results.

Usage:
  cd D:\\Techbilla\\development\\platform\\mono-phase1
  python phase12/run_multiseed.py
"""

import concurrent.futures
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


# ── Environment helpers ──────────────────────────────────────────────

ENV_A = {'E_i': 30.0, 'basal_burn': 0.0, 'alpha_O': 2000.0}
ENV_B = {'E_i': 0.1, 'basal_burn': 2.0, 'alpha_O': 0.5}


def interpolate_env(env_a, env_b, t):
    """Linear interpolation between two environments, t in [0, 1]."""
    return {k: env_a[k] * (1 - t) + env_b[k] * t for k in env_a}


def create_identity(env_params, mutation_rate=None):
    """Create a CoreIdentity from env_params dict."""
    base = {
        'E_m': 200, 'E_s': 5, 'E_r': 1000,
        'c_B': 1, 'c_M': 2, 'c_R': 1, 'c_K': 3, 'c_P': 1,
        'burn_weights': (0.5, 0.3, 0.2),
        'mutation_rate': mutation_rate if mutation_rate is not None else 0.105,
        'initial_energy': 50 if env_params['basal_burn'] < 1.0 else 150,
        'basal_burn': env_params.get('basal_burn', 0),
        'action_cost_multiplier': 1, 'initial_structure_size': 10,
        'decay_rate': 0.05, 'split_ratio': 0.5,
        'E_quiescence': 5, 'S_quiescence': 5,
        'S_critical': 8, 'E_maintenance_min': 10, 'repair_efficiency': 0.8,
        'E_repro': 60 if env_params['basal_burn'] < 1.0 else 100,
        'S_repro': 5, 'r': 0.1, 'C_divide': 5,
        'epsilon_E': 2, 'epsilon_S': 1, 'stability_window': 10,
        'child_survival_cycles': 20, 'birth_stress_cycles': 5,
        'regulator_alpha': 0.1, 'regulator_beta': 0.2, 'regulator_gamma': 0.3,
        'regulator_mutation_rate': 0.01,
        'alpha_O': env_params.get('alpha_O', 1000.0),
        'tau_max': 1000,
        'k_coord': 0.5 if env_params['basal_burn'] < 1.0 else 0.001,
        'tau_sense': 0.1, 'tau_signal': 0.1, 'tau_act': 0.1,
        'latency_drift_rate': 0.01, 'size_penalty_factor': 0.1,
        'prediction_horizon': 10.0, 'number_of_predictive_modules': 3,
        'arbitration_delay': 1.0, 'module_horizon_adapt_rate': 0.1,
        'global_integrator_capacity': 10.0,
        'arbitration_mechanism': 'temporal_sequencing',
        'scene_change_threshold': 2.0, 'scene_min_duration': 3,
        'kappa_pred': 0.5,
        'cog_mutation_rate': 0.1, 'structural_mutation_rate': 0.02,
        'base_gating_threshold': 0.5, 'base_arbitration_frequency': 1,
        'E_i': env_params.get('E_i', 30.0),
    }
    return CoreIdentity(**base)


# ── Simulation core ──────────────────────────────────────────────────

def run_generation(cells, species_memory, generation, observer, env_params,
                   max_cycles=50, panic_state=None):
    """Run one generation. Returns survivors + stats dict."""
    organism_data = []
    surviving = []
    children = []
    repro_attempts = 0
    repro_successes = 0
    deaths = 0
    energy_sum = 0.0
    energy_count = 0

    for cell in cells:
        death_reason = None
        child = None
        for _ in range(max_cycles):
            death_reason, log, child = cycle(
                cell, observer=observer,
                species_defaults={'__observer__': observer},
                generation=generation, species_memory=species_memory,
                env_params=env_params, organism_data_list=organism_data,
                panic_state=panic_state,
            )
            if death_reason:
                deaths += 1
                break

        if not death_reason:
            surviving.append(cell)
            energy_sum += cell.energy.E
            energy_count += 1
        if child:
            children.append(child)
            repro_successes += 1
        if cell.reproduction_eligible:
            repro_attempts += 1

    surviving.extend(children)
    avg_energy = energy_sum / max(energy_count, 1)
    gamma_vals = [c.gating_threshold for c in surviving]
    gamma_var = statistics.variance(gamma_vals) if len(gamma_vals) >= 2 else 0.0

    species_memory.update(organism_data)
    observer.emit_lineage_drift_violations()

    return surviving, {
        'avg_energy': avg_energy, 'deaths': deaths,
        'population_size': len(cells), 'survivors': len(surviving),
        'repro_attempts': repro_attempts, 'repro_successes': repro_successes,
        'gamma_variance': gamma_var,
        'ms_gamma': species_memory.Ms.get('gamma', 0.5),
        'basal_burn': env_params.get('basal_burn', 0.0),
    }


def backfill(cells, target, env_params):
    """Top up population to target size."""
    while len(cells) < target:
        ident = create_identity(env_params,
                                mutation_rate=0.20 if env_params['basal_burn'] >= 1.0 else None)
        c = MonoCell(ident)
        c.lineage_id = str(random.randint(1000, 9999))
        if env_params['basal_burn'] >= 1.0:
            c.gating_threshold = max(0.0, min(1.0,
                c.gating_threshold + random.gauss(-0.1, 0.20)))
        cells.append(c)
    return cells


# ── Scenario schedulers ──────────────────────────────────────────────

def sharp_flip_schedule(gen, flip_gen, total_gens):
    """Returns env_params for a sharp A→B flip."""
    return ENV_A.copy() if gen < flip_gen else ENV_B.copy()


def gradual_transition_schedule(gen, flip_gen, transition_width, total_gens):
    """Linear interpolation A→B over transition_width gens starting at flip_gen."""
    if gen < flip_gen:
        return ENV_A.copy()
    elif gen >= flip_gen + transition_width:
        return ENV_B.copy()
    else:
        t = (gen - flip_gen) / transition_width
        return interpolate_env(ENV_A, ENV_B, t)


def oscillatory_schedule(gen, period, total_gens):
    """Alternate A→B every 'period' gens."""
    cycle_pos = (gen // period) % 2
    return ENV_B.copy() if cycle_pos == 1 else ENV_A.copy()


# ── Single-seed runner ───────────────────────────────────────────────

def run_single(seed, scenario, total_gens, target_pop=50, **scenario_kwargs):
    """Run one seed under a given scenario. Returns falsification dict."""
    random.seed(seed)
    observer = Phase10Observer(seed=seed, env=f'multiseed_{scenario}')
    sm = SpeciesMemory(alpha=0.1, epsilon=0.1)
    si = CompositeStressIndex()
    pc = PanicController()

    pop = [MonoCell(create_identity(ENV_A)) for _ in range(target_pop)]
    fp_count = 0
    first_deviation_gen = None
    ms_gamma_initial = 0.5

    for gen in range(total_gens):
        # Determine environment
        if scenario == 'sharp':
            env = sharp_flip_schedule(gen, scenario_kwargs['flip_gen'], total_gens)
        elif scenario == 'gradual':
            env = gradual_transition_schedule(gen, scenario_kwargs['flip_gen'],
                                              scenario_kwargs.get('width', 50), total_gens)
        elif scenario == 'oscillatory':
            env = oscillatory_schedule(gen, scenario_kwargs.get('period', 150), total_gens)
        else:
            env = ENV_A.copy()

        observer.set_generation(gen)
        panic_out = pc.get_outputs(si.psi)
        pop, stats = run_generation(pop, sm, gen, observer, env, panic_state=panic_out)

        psi = si.update(
            avg_energy=stats['avg_energy'], basal_burn=stats['basal_burn'],
            repro_attempts=stats['repro_attempts'],
            repro_successes=stats['repro_successes'],
            deaths=stats['deaths'], population_size=stats['population_size'],
            gamma_variance=stats['gamma_variance'],
        )
        panic_out = pc.update(psi, generation=gen)

        eps = panic_out['memory_softening_eps']
        if eps > 0:
            cur = {
                'gamma': sum(c.gating_threshold for c in pop) / max(len(pop), 1),
                'module_count': sum(c.module_count for c in pop) / max(len(pop), 1),
                'tau_budget': sum(c.get_tau_organism() for c in pop) / max(len(pop), 1),
                'energy_ceiling': sum(c.energy.E for c in pop) / max(len(pop), 1),
            }
            sm.soften(eps, cur)

        # Track false positives — only count gens where env is A-like
        is_env_a = (env.get('basal_burn', 0) < 0.5)
        if is_env_a and panic_out['state'] != 'CALM':
            fp_count += 1

        # Track first ms.gamma deviation
        if first_deviation_gen is None and abs(stats['ms_gamma'] - ms_gamma_initial) > 0.05:
            first_deviation_gen = gen

        pop = backfill(pop, target_pop, env)

    # Count total A-regime gens for FP rate
    total_a_gens = 0
    for g in range(total_gens):
        if scenario == 'sharp':
            e = sharp_flip_schedule(g, scenario_kwargs['flip_gen'], total_gens)
        elif scenario == 'gradual':
            e = gradual_transition_schedule(g, scenario_kwargs['flip_gen'],
                                            scenario_kwargs.get('width', 50), total_gens)
        elif scenario == 'oscillatory':
            e = oscillatory_schedule(g, scenario_kwargs.get('period', 150), total_gens)
        else:
            e = ENV_A.copy()
        if e.get('basal_burn', 0) < 0.5:
            total_a_gens += 1

    fp_rate = fp_count / max(total_a_gens, 1)

    # First ALERT and PANIC times
    first_alert = None
    first_panic = None
    for t in pc.transition_log:
        if t['to'] == 'ALERT' and first_alert is None:
            first_alert = t['generation']
        if t['to'] == 'PANIC' and first_panic is None:
            first_panic = t['generation']

    return_to_calm = any(t['to'] == 'CALM' for t in pc.transition_log
                         if t['generation'] is not None)

    return {
        'seed': seed,
        'scenario': scenario,
        'total_gens': total_gens,
        'false_positive_rate': round(fp_rate, 4),
        'first_alert_gen': first_alert,
        'first_panic_gen': first_panic,
        'first_deviation_gen': first_deviation_gen,
        'final_ms_gamma': round(sm.Ms.get('gamma', 0.5), 4),
        'final_state': pc.state.value,
        'return_to_calm': return_to_calm,
        'lock_broken': abs(sm.Ms.get('gamma', 0.5) - ms_gamma_initial) > 0.05,
        'total_transitions': len(pc.transition_log),
        **{k: v for k, v in scenario_kwargs.items()},
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    seeds = list(range(1, 26))  # 25 seeds
    total_gens = 750
    results = []

    scenarios = [
        # Sharp flips at different times
        *[{'scenario': 'sharp', 'flip_gen': fg} for fg in [300, 500, 600]],
        # Gradual transition
        {'scenario': 'gradual', 'flip_gen': 500, 'width': 50},
        # Oscillatory
        {'scenario': 'oscillatory', 'period': 150},
    ]

    total_runs = len(seeds) * len(scenarios)
    print(f"Starting {total_runs} simulations using multiprocessing...")

    tasks = []
    for sc in scenarios:
        scenario_name = sc['scenario']
        sc_kwargs = {k: v for k, v in sc.items() if k != 'scenario'}
        for seed in seeds:
            tasks.append((seed, scenario_name, total_gens, 50, sc_kwargs))

    # Run in parallel
    completed = 0
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(run_single, t[0], t[1], t[2], target_pop=t[3], **t[4]): t
            for t in tasks
        }
        for future in concurrent.futures.as_completed(futures):
            r = future.result()
            results.append(r)
            completed += 1
            print(f"[{completed:3d}/{total_runs}] seed={r['seed']:2d} {r['scenario'][:10]:10} "
                  f"→ FP={r['false_positive_rate']:.2%}  lock_broken={int(r['lock_broken'])}  "
                  f"Ms.γ={r['final_ms_gamma']:.4f}  state={r['final_state']}")

    elapsed = time.time() - start_time
    print(f"\nAll {total_runs} runs completed in {elapsed:.1f}s.")

    # ── Aggregate Analysis ────────────────────────────────────────────

    print("\n" + "=" * 80)
    print("PHASE-12 MULTI-SEED ROBUSTNESS REPORT")
    print("=" * 80)

    for sc in scenarios:
        scenario_name = sc['scenario']
        sc_kwargs = {k: v for k, v in sc.items() if k != 'scenario'}
        subset = [r for r in results if r['scenario'] == scenario_name
                  and all(r.get(k) == v for k, v in sc_kwargs.items())]

        print(f"\n── {scenario_name.upper()} {sc_kwargs} ({len(subset)} seeds) ──")

        fp_rates = [r['false_positive_rate'] for r in subset]
        lock_broken = [r['lock_broken'] for r in subset]
        final_gammas = [r['final_ms_gamma'] for r in subset]
        alert_delays = [r['first_alert_gen'] - sc_kwargs.get('flip_gen', 0)
                        for r in subset if r['first_alert_gen'] is not None
                        and 'flip_gen' in sc_kwargs]

        print(f"  False positive rate:  mean={statistics.mean(fp_rates):.2%}  "
              f"max={max(fp_rates):.2%}")
        print(f"  Lock broken:         {sum(lock_broken)}/{len(lock_broken)} "
              f"({sum(lock_broken)/len(lock_broken):.0%})")
        print(f"  Final Ms.γ:          mean={statistics.mean(final_gammas):.4f}  "
              f"std={statistics.stdev(final_gammas) if len(final_gammas) > 1 else 0:.4f}")
        if alert_delays:
            print(f"  Alert delay (gens):  mean={statistics.mean(alert_delays):.1f}  "
                  f"median={statistics.median(alert_delays):.1f}")

    # ── Save ──────────────────────────────────────────────────────────
    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join('phase12_artifacts', f'multiseed_{stamp}')
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'all_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    # Summary table
    summary = {
        'timestamp': stamp,
        'total_seeds': len(seeds),
        'total_scenarios': len(scenarios),
        'total_runs': total_runs,
        'scenarios': {},
    }
    for sc in scenarios:
        scenario_name = sc['scenario']
        sc_kwargs = {k: v for k, v in sc.items() if k != 'scenario'}
        key = f"{scenario_name}_{sc_kwargs}"
        subset = [r for r in results if r['scenario'] == scenario_name
                  and all(r.get(k) == v for k, v in sc_kwargs.items())]
        fp_rates = [r['false_positive_rate'] for r in subset]
        lock_broken = [r['lock_broken'] for r in subset]
        final_gammas = [r['final_ms_gamma'] for r in subset]
        summary['scenarios'][key] = {
            'fp_rate_mean': round(statistics.mean(fp_rates), 4),
            'fp_rate_max': round(max(fp_rates), 4),
            'lock_broken_pct': round(sum(lock_broken) / len(lock_broken), 4),
            'final_gamma_mean': round(statistics.mean(final_gammas), 4),
            'final_gamma_std': round(statistics.stdev(final_gammas) if len(final_gammas) > 1 else 0, 4),
        }

    with open(os.path.join(out_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nArtifacts written to: {out_dir}")


if __name__ == '__main__':
    main()
