"""
Phase 26: Permanent Climate Shift — Darwinian Evolution Test
=============================================================
Phase 25 proved that SHORT environmental shocks trigger behavioral
adaptation but NOT genetic evolution (Case 1: Reactive Homeostasis).

Phase 26 introduces a PERMANENT climate change:
  Gen 0-200:    Baseline (normal dynamics) — establish genetic baseline
  Gen 200+:     PERMANENT SHIFT — depletion_rate *= 8.0 forever

With 1300+ generations of sustained pressure, behavioral buffering alone
should be insufficient. Only genetically superior lineages (higher 
strategy_trait, higher environment_sensitivity) should dominate over time.

This tests the biological rule:
  Short stress  → physiology adapts (behavior)
  Long stress   → evolution adapts (genetics)
"""

import json
import subprocess
import sys
import os
import statistics
import re
import threading

SEEDS = [0, 1, 2, 3, 4]
TOTAL_GENS = 1500
SHIFT_GEN = 200  # Permanent shift starts early to maximize selection time

# Environment params
BASE_DEP = 0.05
BASE_REG = 0.01
SHIFT_DEP_MULT = 3.0  # Phase-27: Gentler ramp (0.05→0.15) for evolutionary rescue
MAX_POP = 300


def run_single_seed(seed):
    """Run a single simulation with permanent climate shift (no recovery)."""
    cmd = [
        sys.executable, 'phase19_internal_economy.py',
        '--seed', str(seed),
        '--total_gens', str(TOTAL_GENS),
        '--depletion_rate', str(BASE_DEP),
        '--regeneration_rate', str(BASE_REG),
        '--max_pop', str(MAX_POP),
        '--target', '20',
        '--shock_start', str(SHIFT_GEN),
        '--shock_end', str(TOTAL_GENS + 1),  # Never recovers
        '--shock_dep_mult', str(SHIFT_DEP_MULT),
        '--include_metrics',
    ]

    print(f"  Running seed {seed}...", flush=True)

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=os.path.dirname(__file__) or '.'
    )

    def stream_stderr(pipe):
        for line in pipe:
            line_stripped = line.strip()
            if "⚡" in line_stripped or "🌱" in line_stripped or "EXTINCTION" in line_stripped:
                print(f"    {line_stripped}", flush=True)
                continue
            match = re.match(r'^Gen (\d+):', line_stripped)
            if match:
                gen_num = int(match.group(1))
                if gen_num % 200 == 0:
                    print(f"    [gen {gen_num}/{TOTAL_GENS}]", flush=True)

    stderr_thread = threading.Thread(target=stream_stderr, args=(process.stderr,), daemon=True)
    stderr_thread.start()

    stdout, _ = process.communicate()
    stderr_thread.join(timeout=5)

    data = None
    try:
        start = stdout.find('{')
        if start != -1:
            data = json.loads(stdout[start:])
    except json.JSONDecodeError:
        print(f"  PARSE ERROR", flush=True)
        return None

    if not data:
        print(f"  NO DATA", flush=True)
        return None

    survived = data.get('survived', False)
    final_pop = data.get('final_population', 0)
    print(f"  -> {'SURVIVED' if survived else 'EXTINCT'} (pop={final_pop})", flush=True)
    return data


def analyze_phase(metrics, start_gen, end_gen, label):
    """Extract average metrics for a specific generation window."""
    window = [m for m in metrics if start_gen <= m['gen'] < end_gen]
    if not window:
        return None
    return {
        'label': label,
        'gens': f"{start_gen}-{end_gen}",
        'avg_pop': statistics.mean([m['population'] for m in window]),
        'avg_env': statistics.mean([m['environmental_quality'] for m in window]),
        'avg_prop_restoring': statistics.mean([m['proportion_restoring'] for m in window]),
        'avg_strategy_trait': statistics.mean([m.get('mean_strategy_trait', 0) for m in window]),
        'var_strategy_trait': statistics.mean([m.get('var_strategy_trait', 0) for m in window]),
        'avg_env_sensitivity': statistics.mean([m.get('mean_env_sensitivity', 0) for m in window]),
        'var_env_sensitivity': statistics.mean([m.get('var_env_sensitivity', 0) for m in window]),
        'avg_p_restore': statistics.mean([m.get('mean_p_restore', 0) for m in window]),
        'avg_lineage_diversity': statistics.mean([m.get('lineage_diversity', 0) for m in window]),
    }


def print_phase_table(phases):
    header = f"{'Phase':<20} {'Gens':<12} {'Pop':>6} {'Env':>6} {'%Rest':>6} {'StratT':>7} {'VarST':>7} {'EnvSen':>7} {'VarES':>7} {'pRest':>7} {'Lineage':>8}"
    print(header)
    print("-" * len(header))
    for p in phases:
        if p is None:
            continue
        print(f"{p['label']:<20} {p['gens']:<12} {p['avg_pop']:>6.0f} {p['avg_env']:>6.3f} {p['avg_prop_restoring']:>6.3f} {p['avg_strategy_trait']:>7.4f} {p['var_strategy_trait']:>7.4f} {p['avg_env_sensitivity']:>7.4f} {p['var_env_sensitivity']:>7.4f} {p['avg_p_restore']:>7.4f} {p['avg_lineage_diversity']:>8.1f}")


def determine_evolution(baseline, early_shift, late_shift):
    """Determine if permanent shift caused genetic evolution."""
    if baseline is None or late_shift is None:
        return "INCONCLUSIVE", []

    signals = []

    # Behavioral response
    if late_shift['avg_prop_restoring'] > baseline['avg_prop_restoring'] + 0.05:
        signals.append("✔ Behavioral adaptation sustained (restorers increased)")
    else:
        signals.append("✘ No sustained behavioral change")

    # Genetic shifts (the key test)
    trait_shift = late_shift['avg_strategy_trait'] - baseline['avg_strategy_trait']
    if abs(trait_shift) > 0.02:
        signals.append(f"✔ GENETIC SHIFT: strategy_trait shifted by {trait_shift:+.4f} (EVOLVED)")
    else:
        signals.append(f"✘ No genetic shift in strategy_trait ({trait_shift:+.4f})")

    sens_shift = late_shift['avg_env_sensitivity'] - baseline['avg_env_sensitivity']
    if abs(sens_shift) > 0.02:
        signals.append(f"✔ GENETIC SHIFT: env_sensitivity shifted by {sens_shift:+.4f} (EVOLVED)")
    else:
        signals.append(f"✘ No genetic shift in env_sensitivity ({sens_shift:+.4f})")

    # Variance change (selection sweep)
    var_decrease = baseline['var_strategy_trait'] - late_shift['var_strategy_trait']
    if var_decrease > 0.01:
        signals.append(f"✔ SELECTION SWEEP: trait variance decreased by {var_decrease:+.4f}")
    else:
        signals.append(f"✘ No selection sweep ({var_decrease:+.4f})")

    # Population change (carrying capacity shift)
    if late_shift['avg_pop'] < baseline['avg_pop'] * 0.7:
        signals.append(f"✔ POPULATION BOTTLENECK: {baseline['avg_pop']:.0f} → {late_shift['avg_pop']:.0f}")

    # Lineage diversity reduction
    if late_shift['avg_lineage_diversity'] < baseline['avg_lineage_diversity'] * 0.5:
        signals.append(f"✔ LINEAGE BOTTLENECK: diversity {baseline['avg_lineage_diversity']:.0f} → {late_shift['avg_lineage_diversity']:.0f}")

    # Verdict
    genetic_shifts = sum(1 for s in signals if "GENETIC SHIFT" in s)
    if genetic_shifts >= 1:
        return "🧬 CASE 2 — DARWINIAN EVOLUTION DETECTED", signals
    else:
        return "CASE 1 — REACTIVE HOMEOSTASIS (no evolution)", signals


def run_permanent_shift_test():
    print("=" * 70)
    print("Phase 26: Permanent Climate Shift — Darwinian Evolution Test")
    print("=" * 70)
    print(f"Seeds: {SEEDS}")
    print(f"Timeline: baseline(0-{SHIFT_GEN}) → PERMANENT shift({SHIFT_GEN}-{TOTAL_GENS})")
    print(f"Shift: depletion_rate {BASE_DEP} → {BASE_DEP * SHIFT_DEP_MULT} (forever)")
    print()

    all_results = []
    for seed in SEEDS:
        result = run_single_seed(seed)
        if result:
            all_results.append(result)

    if not all_results:
        print("All seeds failed!")
        return

    survived = sum(1 for r in all_results if r.get('survived', False))
    print(f"\nSurvival: {survived}/{len(all_results)} seeds")

    # Analyze across 4 time windows
    all_phases = {'baseline': [], 'early_shift': [], 'mid_shift': [], 'late_shift': []}
    for result in all_results:
        metrics = result.get('metrics_per_gen', [])
        if not metrics:
            continue
        b = analyze_phase(metrics, 100, SHIFT_GEN, "Pre-Shift Baseline")
        es = analyze_phase(metrics, SHIFT_GEN, SHIFT_GEN + 300, "Early Shift")
        ms = analyze_phase(metrics, 700, 1000, "Mid Shift")
        ls = analyze_phase(metrics, 1200, TOTAL_GENS, "Late Shift (Final)")

        for key, phase in [('baseline', b), ('early_shift', es), ('mid_shift', ms), ('late_shift', ls)]:
            if phase:
                all_phases[key].append(phase)

    def avg_phases(phase_list):
        if not phase_list:
            return None
        keys = ['avg_pop', 'avg_env', 'avg_prop_restoring', 'avg_strategy_trait',
                'var_strategy_trait', 'avg_env_sensitivity', 'var_env_sensitivity',
                'avg_p_restore', 'avg_lineage_diversity']
        result = {'label': phase_list[0]['label'], 'gens': phase_list[0]['gens']}
        for k in keys:
            values = [p[k] for p in phase_list if k in p]
            result[k] = statistics.mean(values) if values else 0
        return result

    avg_b = avg_phases(all_phases['baseline'])
    avg_es = avg_phases(all_phases['early_shift'])
    avg_ms = avg_phases(all_phases['mid_shift'])
    avg_ls = avg_phases(all_phases['late_shift'])

    print(f"\n{'=' * 70}")
    print(f"AVERAGED RESULTS ACROSS {len(all_results)} SEEDS")
    print(f"{'=' * 70}\n")

    print_phase_table([avg_b, avg_es, avg_ms, avg_ls])

    print()
    case, signals = determine_evolution(avg_b, avg_es, avg_ls)

    print(f"{'=' * 70}")
    print(f"EVOLUTIONARY ANALYSIS (Permanent Climate Shift)")
    print(f"{'=' * 70}")
    for s in signals:
        print(f"  {s}")
    print()
    print(f"  VERDICT: {case}")
    print(f"{'=' * 70}")

    output = {
        'experiment': 'Phase 26: Permanent Climate Shift',
        'seeds': SEEDS,
        'survived': survived,
        'total_seeds': len(SEEDS),
        'shift_gen': SHIFT_GEN,
        'shift_dep_mult': SHIFT_DEP_MULT,
        'verdict': case,
        'signals': signals,
        'phase_averages': {
            'baseline': avg_b,
            'early_shift': avg_es,
            'mid_shift': avg_ms,
            'late_shift': avg_ls,
        }
    }

    with open('phase26_permanent_shift_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to phase26_permanent_shift_results.json")


if __name__ == '__main__':
    run_permanent_shift_test()
