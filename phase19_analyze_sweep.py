import json
import statistics

def safe_mean(x):
    return statistics.mean(x) if x else 0.0

def safe_stdev(x):
    return statistics.stdev(x) if len(x) > 1 else 0.0

def analyze_sweep():
    with open('phase19_sweep/sensitivity_results.json', 'r') as f:
        results = json.load(f)
    print(f"Total results loaded: {len(results)}")

    # Debug errors
    for res in results:
        if 'error' in res:
            print(f"Error in result: {res['error']}")

    # Group by restore_mult and trade_cost
    groups = {}
    for res in results:
        if 'error' in res:
            continue
        key = (res['restore_mult'], res['exchange_rate'])
        if key not in groups:
            groups[key] = []
        groups[key].append(res)

    summary = {}
    for key, group in groups.items():
        rm, tc = key
        str_key = f"{rm}_{tc}"
        total = len(group)
        extinct_count = sum(1 for r in group if r['result']['summary']['extinct'])
        p_extinct = extinct_count / total if total > 0 else 0

        surviving = [r for r in group if not r['result']['summary']['extinct']]
        survival_times = [r['result']['summary']['total_gens'] for r in group if not r['result']['summary']['extinct']]
        mean_survival = safe_mean(survival_times) if survival_times else 0

        final_p_restores = [r['result']['summary']['final_mean_p_restore'] for r in surviving]
        mean_final_p_restore = safe_mean(final_p_restores)

        variances = [r['result']['summary']['final_p_restore_variance'] for r in surviving]
        mean_variance = safe_mean(variances)

        trade_events = []
        food_ratios = []
        for r in surviving:
            gen_data = r['result']['gen_data']
            if gen_data:
                last_100 = gen_data[-100:] if len(gen_data) >= 100 else gen_data
                trade_events.extend([g['trade_events'] for g in last_100])
                food_ratios.extend([g['mean_food'] / (g['mean_repair'] + 1e-6) for g in last_100])

        mean_trade_events = safe_mean(trade_events) if trade_events else 0
        mean_food_ratio = safe_mean(food_ratios) if food_ratios else 0

        summary[str_key] = {
            'restore_mult': rm,
            'trade_cost': tc,
            'p_extinct': p_extinct,
            'mean_survival_time': mean_survival,
            'mean_final_p_restore': mean_final_p_restore,
            'mean_p_restore_variance': mean_variance,
            'mean_trade_events_per_gen': mean_trade_events,
            'mean_food_to_repair_ratio': mean_food_ratio,
            'sample_size': total
        }

    print(f"Number of groups: {len(groups)}")

    # Print summary table
    print("Phase-19 Sensitivity Sweep Summary")
    print("restore_mult | trade_cost | p_extinct | mean_survival | mean_p_restore | variance | trade_events | food_ratio")
    print("-" * 100)
    for rm in sorted(set(k[0] for k in groups)):
        for tc in sorted(set(k[1] for k in groups)):
            if (rm, tc) in groups:
                s = summary[f"{rm}_{tc}"]
                print(f"{rm:.2f} | {tc:.1f} | {s['p_extinct']:.2f} | {s['mean_survival_time']:.1f} | {s['mean_final_p_restore']:.3f} | {s['mean_p_restore_variance']:.4f} | {s['mean_trade_events_per_gen']:.2f} | {s['mean_food_to_repair_ratio']:.1f}")

    # Save detailed summary
    with open('phase19_sweep/sweep_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print("Summary saved to phase19_sweep/sweep_summary.json")

if __name__ == "__main__":
    analyze_sweep()
