import json
import statistics

def safe_mean(x):
    return statistics.mean(x) if x else 0.0

def safe_stdev(x):
    return statistics.stdev(x) if len(x) > 1 else 0.0

def analyze_env_coupling():
    with open('phase20_env_sweep/env_coupling_results.json', 'r') as f:
        results = json.load(f)
    print(f"Total results loaded: {len(results)}")

    # Debug errors
    for res in results:
        if 'error' in res:
            print(f"Error in result: {res['error']}")

    # Group by restore_mult
    groups = {}
    for res in results:
        if 'error' in res:
            continue
        key = res['restore_mult']
        if key not in groups:
            groups[key] = []
        groups[key].append(res)

    summary = {}
    for rm, group in groups.items():
        total = len(group)
        extinct_count = sum(1 for r in group if r['result']['summary']['extinct'])
        p_extinct = extinct_count / total
        
        if extinct_count < total:
            # Only compute survival stats for non-extinct runs
            non_extinct = [r for r in group if not r['result']['summary']['extinct']]
            mean_survival = safe_mean([r['result']['summary']['final_gen'] for r in non_extinct])
            mean_p_restore = safe_mean([r['result']['summary']['mean_p_restore'] for r in non_extinct])
            variance_p_restore = safe_stdev([r['result']['summary']['mean_p_restore'] for r in non_extinct])
            trade_events = safe_mean([r['result']['summary']['trade_events'] for r in non_extinct])
            food_ratio = safe_mean([r['result']['summary']['food_ratio'] for r in non_extinct])
        else:
            mean_survival = 0.0
            mean_p_restore = 0.0
            variance_p_restore = 0.0
            trade_events = 0.0
            food_ratio = 0.0
        
        summary[str(rm)] = {
            'restore_mult': rm,
            'p_extinct': p_extinct,
            'mean_survival': mean_survival,
            'mean_p_restore': mean_p_restore,
            'variance': variance_p_restore,
            'trade_events': trade_events,
            'food_ratio': food_ratio,
            'total_runs': total,
            'extinct_runs': extinct_count
        }
    
    # Print formatted summary
    print("\nPhase-20 Environmental Coupling Sweep Summary")
    print("restore_mult | p_extinct | mean_survival | mean_p_restore | variance | trade_events | food_ratio")
    print("-" * 95)
    for rm, stats in sorted(summary.items()):
        print(f"{stats['restore_mult']:11.1f} | {stats['p_extinct']:8.2f} | {stats['mean_survival']:12.1f} | {stats['mean_p_restore']:13.3f} | {stats['variance']:8.4f} | {stats['trade_events']:11.2f} | {stats['food_ratio']:10.3f}")
    
    # Save summary
    with open('phase20_env_sweep/env_coupling_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("\nSummary saved to phase20_env_sweep/env_coupling_summary.json")

if __name__ == "__main__":
    analyze_env_coupling()
