"""
Phase 25: Environmental Shock Test
===================================
Tests whether MONO demonstrates true Darwinian evolution (Case 2)
or merely reactive behavioral equilibrium (Case 1).

Timeline:
  Gen 0-400:   Baseline (normal dynamics)
  Gen 400:     SHOCK — depletion_rate *= 3.0
  Gen 400-700: Stress period (high depletion persists)
  Gen 700:     RECOVERY — depletion_rate returns to original
  Gen 700-1500: Post-recovery observation

Runs 5 seeds and averages results.
Tracks behavioral (proportion_restoring) AND genetic 
(strategy_trait, environment_sensitivity) metrics to separate 
reaction from evolution.
"""

import json
import subprocess
import sys
import os
import statistics

SEEDS = [0, 1, 2, 3, 4]
TOTAL_GENS = 1500
SHOCK_START = 400
SHOCK_END = 700

# Baseline params (same as Phase 23 mid-range)
BASE_DEP = 0.05
BASE_REG = 0.01
SHOCK_DEP_MULT = 8.0  # Phase-26: 8x depletion to force mortality & selection pressure
MAX_POP = 300  # Cap population for tractable run time


def run_single_seed(seed):
    """Run a single 1500-gen simulation, injecting shock via modified depletion."""
    # We'll run in two stages to change depletion_rate mid-simulation
    # But since run_evolution resets state, we need to modify the engine
    # Instead, we'll add shock support directly to the CLI
    
    cmd = [
        sys.executable, 'phase19_internal_economy.py',
        '--seed', str(seed),
        '--total_gens', str(TOTAL_GENS),
        '--depletion_rate', str(BASE_DEP),
        '--regeneration_rate', str(BASE_REG),
        '--max_pop', str(MAX_POP),
        '--target', '20',
        '--shock_start', str(SHOCK_START),
        '--shock_end', str(SHOCK_END),
        '--shock_dep_mult', str(SHOCK_DEP_MULT),
        '--include_metrics',
    ]
    
    print(f"  Running seed {seed}...", flush=True)
    
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
        text=True, cwd=os.path.dirname(__file__) or '.'
    )
    
    # Read stderr in real-time for progress without blocking stdout
    import threading
    import re
    def stream_stderr(pipe):
        for line in pipe:
            line_stripped = line.strip()
            # Show shock/recovery markers
            if "⚡" in line_stripped or "🌱" in line_stripped or "EXTINCTION" in line_stripped:
                print(f"    {line_stripped}", flush=True)
                continue
            # Show progress every 100 generations
            match = re.match(r'^Gen (\d+):', line_stripped)
            if match:
                gen_num = int(match.group(1))
                if gen_num % 100 == 0:
                    print(f"    [gen {gen_num}/{TOTAL_GENS}]", flush=True)

    stderr_thread = threading.Thread(target=stream_stderr, args=(process.stderr,), daemon=True)
    stderr_thread.start()
    
    # communicate() handles buffer flushing internally to prevent deadlocks
    stdout, _ = process.communicate()
    stderr_thread.join(timeout=5)
    
    data = None
    try:
        start = stdout.find('{')
        if start != -1:
            data = json.loads(stdout[start:])
    except json.JSONDecodeError:
        print(f" PARSE ERROR")
        return None
    
    if not data:
        print(f" NO DATA")
        return None
    
    survived = data.get('survived', False)
    final_pop = data.get('final_population', 0)
    print(f" {'SURVIVED' if survived else 'EXTINCT'} (pop={final_pop})")
    
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
        'avg_strategy_trait': statistics.mean([m['mean_strategy_trait'] for m in window]),
        'var_strategy_trait': statistics.mean([m['var_strategy_trait'] for m in window]),
        'avg_env_sensitivity': statistics.mean([m['mean_env_sensitivity'] for m in window]),
        'var_env_sensitivity': statistics.mean([m['var_env_sensitivity'] for m in window]),
        'avg_p_restore': statistics.mean([m.get('mean_p_restore', 0) for m in window]),
        'avg_lineage_diversity': statistics.mean([m.get('lineage_diversity', 0) for m in window]),
    }


def print_phase_table(phases):
    """Print a formatted comparison table across phases."""
    header = f"{'Phase':<18} {'Gens':<10} {'Pop':>6} {'Env':>6} {'%Rest':>6} {'StratT':>7} {'VarST':>7} {'EnvSen':>7} {'VarES':>7} {'pRest':>7} {'Lineage':>8}"
    print(header)
    print("-" * len(header))
    for p in phases:
        if p is None:
            continue
        print(f"{p['label']:<18} {p['gens']:<10} {p['avg_pop']:>6.0f} {p['avg_env']:>6.3f} {p['avg_prop_restoring']:>6.3f} {p['avg_strategy_trait']:>7.4f} {p['var_strategy_trait']:>7.4f} {p['avg_env_sensitivity']:>7.4f} {p['var_env_sensitivity']:>7.4f} {p['avg_p_restore']:>7.4f} {p['avg_lineage_diversity']:>8.1f}")


def determine_evolution_case(baseline, stress, post_recovery):
    """Determine if the system shows Case 1 (reactive) or Case 2 (evolutionary)."""
    if baseline is None or stress is None or post_recovery is None:
        return "INCONCLUSIVE", []
    
    signals = []
    
    # Check 1: Did behavior change during shock?
    if stress['avg_prop_restoring'] > baseline['avg_prop_restoring'] + 0.05:
        signals.append("✔ Behavioral response to shock (restorers increased)")
    else:
        signals.append("✘ No behavioral response to shock")
    
    # Check 2: Did strategy_trait shift permanently?
    trait_shift = post_recovery['avg_strategy_trait'] - baseline['avg_strategy_trait']
    if abs(trait_shift) > 0.02:
        signals.append(f"✔ GENETIC SHIFT: strategy_trait shifted by {trait_shift:+.4f} (PERMANENT)")
    else:
        signals.append(f"✘ No permanent genetic shift in strategy_trait ({trait_shift:+.4f})")
    
    # Check 3: Did env_sensitivity shift permanently?
    sens_shift = post_recovery['avg_env_sensitivity'] - baseline['avg_env_sensitivity']
    if abs(sens_shift) > 0.02:
        signals.append(f"✔ GENETIC SHIFT: env_sensitivity shifted by {sens_shift:+.4f} (PERMANENT)")
    else:
        signals.append(f"✘ No permanent genetic shift in env_sensitivity ({sens_shift:+.4f})")
    
    # Check 4: Did variance decrease (selection sweep)?
    var_decrease = baseline['var_strategy_trait'] - post_recovery['var_strategy_trait']
    if var_decrease > 0.01:
        signals.append(f"✔ SELECTION SWEEP: strategy_trait variance decreased by {var_decrease:+.4f}")
    else:
        signals.append(f"✘ No selection sweep detected in variance ({var_decrease:+.4f})")
    
    # Check 5: Lineage bottleneck
    if stress['avg_lineage_diversity'] < baseline['avg_lineage_diversity'] * 0.7:
        signals.append(f"✔ LINEAGE BOTTLENECK: diversity dropped from {baseline['avg_lineage_diversity']:.0f} to {stress['avg_lineage_diversity']:.0f}")
    
    # Check 6: Ecological resilience basin (population returns to ~similar level)
    pop_ratio = post_recovery['avg_pop'] / baseline['avg_pop'] if baseline['avg_pop'] > 0 else 0
    if 0.7 < pop_ratio < 1.3:
        signals.append(f"✔ RESILIENCE BASIN: population returned to attractor ({post_recovery['avg_pop']:.0f} vs baseline {baseline['avg_pop']:.0f})")
    elif post_recovery['avg_pop'] > 0:
        signals.append(f"⚠ Population settled at NEW level ({post_recovery['avg_pop']:.0f} vs baseline {baseline['avg_pop']:.0f}) — possible niche construction")
    
    # Determine case
    genetic_shifts = sum(1 for s in signals if "GENETIC SHIFT" in s)
    if genetic_shifts >= 1:
        return "CASE 2 — EVOLUTIONARY ADAPTATION (Darwinian selection detected)", signals
    else:
        return "CASE 1 — REACTIVE HOMEOSTASIS (behavioral only, no evolution)", signals


def run_shock_test():
    print("=" * 70)
    print("Phase 25: Environmental Shock Test")
    print("=" * 70)
    print(f"Seeds: {SEEDS}")
    print(f"Timeline: baseline(0-{SHOCK_START}) → shock({SHOCK_START}-{SHOCK_END}) → recovery({SHOCK_END}-{TOTAL_GENS})")
    print(f"Shock: depletion_rate {BASE_DEP} → {BASE_DEP * SHOCK_DEP_MULT}")
    print()
    
    all_results = []
    for seed in SEEDS:
        result = run_single_seed(seed)
        if result:
            all_results.append(result)
    
    if not all_results:
        print("All seeds failed!")
        return
    
    survived_count = sum(1 for r in all_results if r.get('survived', False))
    print(f"\nSurvival: {survived_count}/{len(all_results)} seeds survived")
    
    # Aggregate metrics across seeds  
    # For seeds that have full metrics, analyze phase windows
    all_phases = {'baseline': [], 'early_stress': [], 'late_stress': [], 'early_recovery': [], 'late_recovery': []}
    
    for result in all_results:
        metrics = result.get('metrics_per_gen', [])
        if not metrics:
            continue
        
        b = analyze_phase(metrics, 300, SHOCK_START, "Baseline")
        es = analyze_phase(metrics, SHOCK_START, SHOCK_START + 100, "Early Stress")
        ls = analyze_phase(metrics, SHOCK_END - 100, SHOCK_END, "Late Stress")
        er = analyze_phase(metrics, SHOCK_END, SHOCK_END + 200, "Early Recovery")
        lr = analyze_phase(metrics, TOTAL_GENS - 300, TOTAL_GENS, "Late Recovery")
        
        for key, phase in [('baseline', b), ('early_stress', es), ('late_stress', ls), ('early_recovery', er), ('late_recovery', lr)]:
            if phase:
                all_phases[key].append(phase)
    
    # Average across seeds
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
    
    avg_baseline = avg_phases(all_phases['baseline'])
    avg_early_stress = avg_phases(all_phases['early_stress'])
    avg_late_stress = avg_phases(all_phases['late_stress'])
    avg_early_recovery = avg_phases(all_phases['early_recovery'])
    avg_late_recovery = avg_phases(all_phases['late_recovery'])
    
    print(f"\n{'=' * 70}")
    print(f"AVERAGED RESULTS ACROSS {len(all_results)} SEEDS")
    print(f"{'=' * 70}")
    print()
    
    print_phase_table([avg_baseline, avg_early_stress, avg_late_stress, avg_early_recovery, avg_late_recovery])
    
    # Determine Case 1 vs Case 2
    print()
    case, signals = determine_evolution_case(avg_baseline, avg_late_stress, avg_late_recovery)
    
    print(f"{'=' * 70}")
    print(f"EVOLUTIONARY ANALYSIS")
    print(f"{'=' * 70}")
    for s in signals:
        print(f"  {s}")
    print()
    print(f"  VERDICT: {case}")
    print(f"{'=' * 70}")
    
    # Save results
    output = {
        'seeds': SEEDS,
        'survived': survived_count,
        'total_seeds': len(SEEDS),
        'shock_start': SHOCK_START,
        'shock_end': SHOCK_END,
        'shock_dep_mult': SHOCK_DEP_MULT,
        'verdict': case,
        'signals': signals,
        'phase_averages': {
            'baseline': avg_baseline,
            'early_stress': avg_early_stress,
            'late_stress': avg_late_stress,
            'early_recovery': avg_early_recovery,
            'late_recovery': avg_late_recovery,
        }
    }
    
    with open('phase25_shock_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to phase25_shock_results.json")


if __name__ == '__main__':
    run_shock_test()
