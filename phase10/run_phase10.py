import argparse
import csv
import json
import os
import random
import statistics
import time

from core.identity import CoreIdentity
from mono import MonoCell
from cell.lifecycle import cycle
from phase10.observer import Phase10Observer, mutual_information_discrete


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]):
    _ensure_dir(os.path.dirname(path))
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    try:
        return float(statistics.correlation(xs, ys))
    except Exception:
        return 0.0


def _histogram(values: list[float], bins: int = 20):
    if not values:
        return {'bins': [], 'counts': []}
    lo = min(values)
    hi = max(values)
    if hi <= lo:
        return {'bins': [lo, hi], 'counts': [len(values)]}
    width = (hi - lo) / bins
    counts = [0 for _ in range(bins)]
    for v in values:
        idx = int((v - lo) / width)
        if idx >= bins:
            idx = bins - 1
        if idx < 0:
            idx = 0
        counts[idx] += 1
    edges = [lo + i * width for i in range(bins + 1)]
    return {'bins': edges, 'counts': counts}


def _pareto_front(points: list[dict], objectives: list[tuple[str, str]]):
    front = []
    for i, a in enumerate(points):
        dominated = False
        for j, b in enumerate(points):
            if i == j:
                continue
            better_or_equal = True
            strictly_better = False
            for key, direction in objectives:
                av = a.get(key)
                bv = b.get(key)
                if av is None or bv is None:
                    better_or_equal = False
                    break
                if direction == 'max':
                    if bv < av:
                        better_or_equal = False
                        break
                    if bv > av:
                        strictly_better = True
                else:
                    if bv > av:
                        better_or_equal = False
                        break
                    if bv < av:
                        strictly_better = True
            if better_or_equal and strictly_better:
                dominated = True
                break
        if not dominated:
            front.append(a)
    return front


def default_identity() -> CoreIdentity:
    return CoreIdentity(
        E_i=20,
        E_m=200,
        E_s=5,
        E_r=1000,
        c_B=1,
        c_M=2,
        c_R=1,
        c_K=3,
        c_P=1,
        burn_weights=(0.5, 0.3, 0.2),
        mutation_rate=0.1,
        initial_energy=1000,
        basal_burn=0,
        action_cost_multiplier=1,
        initial_structure_size=10,
        decay_rate=0.05,
        split_ratio=0.5,
        E_quiescence=5,
        S_quiescence=5,
        S_critical=8,
        E_maintenance_min=10,
        repair_efficiency=0.8,
        E_repro=60,
        S_repro=5,
        r=0.1,
        C_divide=5,
        epsilon_E=2,
        epsilon_S=1,
        stability_window=10,
        child_survival_cycles=20,
        birth_stress_cycles=5,
        regulator_alpha=0.1,
        regulator_beta=0.2,
        regulator_gamma=0.3,
        regulator_mutation_rate=0.01,
        alpha_O=1000.0,
        tau_max=1000,
        k_coord=0.1,
        tau_sense=0.1,
        tau_signal=0.1,
        tau_act=0.1,
        latency_drift_rate=0.01,
        size_penalty_factor=0.1,
        prediction_horizon=10.0,
        number_of_predictive_modules=3,
        arbitration_delay=1.0,
        module_horizon_adapt_rate=0.1,
        global_integrator_capacity=10.0,
        arbitration_mechanism='temporal_sequencing',
        scene_change_threshold=2.0,
        scene_min_duration=3,
        kappa_pred=0.5,
        cog_mutation_rate=0.1,
        structural_mutation_rate=0.02,
        base_gating_threshold=0.5,
        base_arbitration_frequency=1,
    )


def run_seed(*, seed: int, env: str, cycles: int, initial_pop: int):
    random.seed(seed)
    identity = default_identity()

    observer = Phase10Observer(seed=seed, env=env)

    population: list[MonoCell] = [MonoCell(identity) for _ in range(initial_pop)]

    for t in range(cycles):
        next_population: list[MonoCell] = []
        observer.set_generation(0)

        for cell in population:
            if cell.structure.size() <= 0:
                continue

            species_defaults = {'__observer__': observer}
            death_reason, log, child = cycle(cell, observer=observer, species_defaults=species_defaults)

            if isinstance(death_reason, str):
                continue

            if cell.structure.size() > 0:
                next_population.append(cell)
            if isinstance(child, MonoCell):
                next_population.append(child)

        population = next_population
        if not population:
            break

    return observer


def build_artifacts(observers: list[Phase10Observer], out_dir: str):
    _ensure_dir(out_dir)

    cycle_rows: list[dict] = []
    for obs in observers:
        for tr in obs.cycle_traces:
            cycle_rows.append(
                {
                    'seed': tr.seed,
                    'env': tr.env,
                    'generation': tr.generation,
                    'cell_id': tr.cell_id,
                    'parent_id': '' if tr.parent_id is None else tr.parent_id,
                    'cycle': tr.cycle,
                    'tau_action': tr.tau_action,
                    'tau_cognition': tr.tau_cognition,
                    'cog_invoked': int(tr.cog_invoked),
                    'energy_pre': '' if tr.energy_pre is None else tr.energy_pre,
                    'energy_post': tr.energy_post,
                    'gamma_used': tr.gamma_used,
                    'modules_active': tr.modules_active,
                }
            )

    _write_csv(
        os.path.join(out_dir, 'cycle_traces.csv'),
        cycle_rows,
        [
            'seed',
            'env',
            'generation',
            'cell_id',
            'parent_id',
            'cycle',
            'tau_action',
            'tau_cognition',
            'cog_invoked',
            'energy_pre',
            'energy_post',
            'gamma_used',
            'modules_active',
        ],
    )

    repro_rows: list[dict] = []
    for obs in observers:
        for tr in obs.reproduction_traces:
            repro_rows.append(
                {
                    'seed': tr.seed,
                    'env': tr.env,
                    'generation': tr.generation,
                    'parent_id': tr.parent_id,
                    'child_id': tr.child_id,
                    'species_defaults_applied_json': json.dumps(tr.species_defaults_applied, sort_keys=True),
                    'offspring_initial_params_json': json.dumps(tr.offspring_initial_params, sort_keys=True),
                }
            )

    _write_csv(
        os.path.join(out_dir, 'reproduction_traces.csv'),
        repro_rows,
        [
            'seed',
            'env',
            'generation',
            'parent_id',
            'child_id',
            'species_defaults_applied_json',
            'offspring_initial_params_json',
        ],
    )

    violations = []
    for obs in observers:
        for v in obs.violations:
            violations.append({'seed': obs.seed, 'env': obs.env, **v})

    with open(os.path.join(out_dir, 'violations.json'), 'w', encoding='utf-8') as f:
        json.dump(violations, f, indent=2)

    metrics = {
        'tau_action': [r['tau_action'] for r in cycle_rows if isinstance(r.get('tau_action'), (int, float))],
        'tau_cognition': [r['tau_cognition'] for r in cycle_rows if isinstance(r.get('tau_cognition'), (int, float))],
        'energy_post': [r['energy_post'] for r in cycle_rows if isinstance(r.get('energy_post'), (int, float))],
        'gamma_used': [r['gamma_used'] for r in cycle_rows if isinstance(r.get('gamma_used'), (int, float))],
        'modules_active': [r['modules_active'] for r in cycle_rows if isinstance(r.get('modules_active'), (int, float))],
    }

    corr_rows = []
    mi_rows = []
    keys = list(metrics.keys())
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            xs = metrics[a]
            ys = metrics[b]
            n = min(len(xs), len(ys))
            xs = xs[:n]
            ys = ys[:n]
            corr_rows.append({'x': a, 'y': b, 'pearson': _pearson(xs, ys), 'n': n})
            mi_rows.append({'x': a, 'y': b, 'mi_bits': mutual_information_discrete(xs, ys, bins=10), 'n': n})

    _write_csv(os.path.join(out_dir, 'correlations.csv'), corr_rows, ['x', 'y', 'pearson', 'n'])
    _write_csv(os.path.join(out_dir, 'mutual_information.csv'), mi_rows, ['x', 'y', 'mi_bits', 'n'])

    hist = {k: _histogram(v, bins=20) for k, v in metrics.items()}
    with open(os.path.join(out_dir, 'histograms.json'), 'w', encoding='utf-8') as f:
        json.dump(hist, f, indent=2)

    by_cell: dict[tuple[int, str, int], dict] = {}
    for r in cycle_rows:
        key = (int(r['seed']), str(r['env']), int(r['cell_id']))
        by_cell.setdefault(key, {'seed': r['seed'], 'env': r['env'], 'cell_id': r['cell_id'], 'n': 0, 'tau_sum': 0.0, 'cog_sum': 0.0, 'energy_post_sum': 0.0, 'cog_invoked_sum': 0})
        by_cell[key]['n'] += 1
        by_cell[key]['tau_sum'] += float(r['tau_action'])
        by_cell[key]['cog_sum'] += float(r['tau_cognition'])
        by_cell[key]['energy_post_sum'] += float(r['energy_post'])
        by_cell[key]['cog_invoked_sum'] += int(r['cog_invoked'])

    cell_points = []
    for v in by_cell.values():
        if v['n'] <= 0:
            continue
        cell_points.append(
            {
                'seed': v['seed'],
                'env': v['env'],
                'cell_id': v['cell_id'],
                'lifespan_cycles': v['n'],
                'tau_action_mean': v['tau_sum'] / v['n'],
                'tau_cognition_mean': v['cog_sum'] / v['n'],
                'energy_post_mean': v['energy_post_sum'] / v['n'],
                'cog_invoked_rate': v['cog_invoked_sum'] / v['n'],
            }
        )

    _write_csv(
        os.path.join(out_dir, 'cell_summaries.csv'),
        cell_points,
        ['seed', 'env', 'cell_id', 'lifespan_cycles', 'tau_action_mean', 'tau_cognition_mean', 'energy_post_mean', 'cog_invoked_rate'],
    )

    pareto = _pareto_front(
        cell_points,
        objectives=[('lifespan_cycles', 'max'), ('tau_action_mean', 'min'), ('tau_cognition_mean', 'min')],
    )
    _write_csv(
        os.path.join(out_dir, 'pareto_front.csv'),
        pareto,
        ['seed', 'env', 'cell_id', 'lifespan_cycles', 'tau_action_mean', 'tau_cognition_mean', 'energy_post_mean', 'cog_invoked_rate'],
    )

    summary = {
        'runs': len(observers),
        'cycle_traces': len(cycle_rows),
        'reproduction_traces': len(repro_rows),
        'violations': len(violations),
        'cell_summaries': len(cell_points),
    }
    with open(os.path.join(out_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', type=int, nargs='+', default=[0, 1, 2])
    ap.add_argument('--env', type=str, default='default')
    ap.add_argument('--cycles', type=int, default=200)
    ap.add_argument('--initial-pop', type=int, default=20)
    ap.add_argument('--out-dir', type=str, default='phase10_artifacts')
    args = ap.parse_args()

    stamp = time.strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.join(args.out_dir, f"phase10_{args.env}_{stamp}")

    observers = []
    for seed in args.seeds:
        observers.append(run_seed(seed=seed, env=args.env, cycles=args.cycles, initial_pop=args.initial_pop))

    build_artifacts(observers, out_dir)
    print(f"Phase-10 artifacts written to: {out_dir}")


if __name__ == '__main__':
    main()
