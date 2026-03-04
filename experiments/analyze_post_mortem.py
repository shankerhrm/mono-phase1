import json
import csv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_csv(path):
    with open(path, 'r') as f:
        return list(csv.DictReader(f))

def analyze_post_mortem(artifacts_dir, gens_range=(501, 510)):
    print("=== Post-Mortem Analysis: Gens 501-510 (Regime Flip Recovery) ===")

    # Load artifacts
    summary = load_json(os.path.join(artifacts_dir, 'summary.json'))
    history_path = os.path.join(os.path.dirname(artifacts_dir), 'regime_flip_history.json')
    if os.path.exists(history_path):
        history = load_json(history_path)
    else:
        history = []

    violations = load_json(os.path.join(artifacts_dir, 'violations.json'))
    cycle_traces = load_csv(os.path.join(artifacts_dir, 'cycle_traces.csv'))
    repro_traces = load_csv(os.path.join(artifacts_dir, 'reproduction_traces.csv'))

    # Filter for gens 501-510
    target_gens = set(range(gens_range[0], gens_range[1] + 1))

    # History summary
    print("\n--- Generation Summary ---")
    for entry in history:
        if entry['generation'] in target_gens:
            print(f"Gen {entry['generation']} ({entry['env']}): Survival {entry['survival_rate']:.2f}, Ms gamma: {entry['Ms'].get('gamma', 0):.3f}, Avg Tau: {entry['avg_tau']:.3f}")

    # Ms evolution
    print("\n--- Ms Evolution ---")
    prev_gamma = None
    for entry in history:
        if entry['generation'] in target_gens:
            gamma = entry['Ms'].get('gamma', 0)
            if prev_gamma is not None:
                delta = gamma - prev_gamma
                print(f"Gen {entry['generation']}: Gamma {gamma:.3f} (Δ {delta:+.3f})")
            else:
                print(f"Gen {entry['generation']}: Gamma {gamma:.3f}")
            prev_gamma = gamma

    # Reproduction analysis
    print("\n--- Reproduction Analysis ---")
    gen_repros = {}
    for r in repro_traces:
        gen = int(r['generation'])
        if gen in target_gens:
            gen_repros.setdefault(gen, []).append(r)

    for gen in sorted(target_gens):
        repros = gen_repros.get(gen, [])
        if repros:
            gammas = [float(r['offspring_initial_params_json'].split('"gamma": ')[1].split(',')[0]) for r in repros]
            avg_gamma = sum(gammas) / len(gammas)
            print(f"Gen {gen}: {len(repros)} reproductions, Avg offspring gamma: {avg_gamma:.3f}")
            # Check for mutants (gamma < 0.4 or something, assuming base 0.5)
            mutants = [g for g in gammas if g < 0.45]
            if mutants:
                print(f"  Mutants detected: {len(mutants)} with gamma < 0.45")
        else:
            print(f"Gen {gen}: 0 reproductions")

    # Cycle traces: cognition spikes
    print("\n--- Cognition Activity ---")
    gen_cycles = {}
    for c in cycle_traces:
        gen = int(c['generation'])
        if gen in target_gens:
            gen_cycles.setdefault(gen, []).append(c)

    for gen in sorted(target_gens):
        cycles = gen_cycles.get(gen, [])
        if cycles:
            cog_invoked = sum(1 for c in cycles if c['cog_invoked'] == '1')
            total_cycles = len(cycles)
            rate = cog_invoked / total_cycles if total_cycles > 0 else 0
            print(f"Gen {gen}: {cog_invoked}/{total_cycles} cycles with cognition ({rate:.2%})")
        else:
            print(f"Gen {gen}: 0 cycles")

    # Violations
    print("\n--- Violations ---")
    gen_violations = {}
    for v in violations:
        gen = v.get('generation', -1)
        if gen in target_gens:
            gen_violations.setdefault(gen, []).append(v)

    for gen in sorted(target_gens):
        vs = gen_violations.get(gen, [])
        if vs:
            print(f"Gen {gen}: {len(vs)} violations")
            for v in vs:
                print(f"  {v['code']}: {v['message']}")
        else:
            print(f"Gen {gen}: 0 violations")

    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    analyze_post_mortem('regime_flip_artifacts')
