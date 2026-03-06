#!/usr/bin/env python3
"""
Experiment L: Reproduction Debug Analysis
Track reproduction reasons to identify why reproduction stops after generation 13.
"""

import json
import statistics
from phase19_internal_economy import run_evolution

def run_reproduction_debug():
    """Run diagnostic sweep with reproduction reason tracking."""
    
    # Parameters from best performing configuration
    restore_mults = [3.0]
    seeds = range(3)  # Just 3 seeds for debugging
    total_gens = 100  # Shorter run to focus on early generations
    
    results = []
    
    for restore_mult in restore_mults:
        for seed in seeds:
            print(f"Running restore_mult {restore_mult}, seed {seed} ({seed+1}/3)")
            
            # Run evolution with reproduction debugging
            summary = run_evolution(
                total_gens=total_gens,
                seed=seed,
                dep_rate=0.005,
                reg_rate=0.2,
                env_exponent=0.0,
                restore_mult=restore_mult,
                trade_cost=1.0,
                exchange_rate=1.0,
                target=20
            )
            
            # Extract reproduction reason data
            metrics = summary['metrics_per_gen']
            repro_debug_data = []
            
            for gen_data in metrics:
                gen = gen_data['gen']
                pop = gen_data['population']
                repro_reasons = gen_data.get('reproduction_reasons', {})
                
                repro_debug_data.append({
                    'generation': gen,
                    'population': pop,
                    'reproduction_reasons': repro_reasons,
                    'eligible_count': repro_reasons.get('eligible', 0),
                    'mode_blocked_count': repro_reasons.get('mode_blocked', 0),
                    'tau_blocked_count': repro_reasons.get('tau_blocked', 0),
                    'energy_low_count': repro_reasons.get('energy_low', 0),
                    'structure_low_count': repro_reasons.get('structure_low', 0),
                    'probability_blocked_count': repro_reasons.get('probability_blocked', 0),
                    'threshold_blocked_count': repro_reasons.get('threshold_blocked', 0)
                })
            
            result = {
                'restore_mult': restore_mult,
                'seed': seed,
                'final_gen': summary['final_gen'],
                'survived': summary['survived'],
                'peak_population': summary['peak_population'],
                'repro_debug_data': repro_debug_data
            }
            
            results.append(result)
    
    # Save results
    with open('reproduction_debug_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Reproduction debug complete. Results saved to reproduction_debug_results.json")
    
    # Analyze results
    analyze_reproduction_debug(results)

def analyze_reproduction_debug(results):
    """Analyze reproduction reason data to identify the blocking cause."""
    
    print("\n" + "="*70)
    print("REPRODUCTION DEBUG ANALYSIS")
    print("="*70)
    
    for result in results:
        print(f"\nSeed {result['seed']} Analysis:")
        print("Gen | Pop | Eligible | ModeBlocked | TauBlocked | EnergyLow | StructureLow")
        print("-" * 75)
        
        repro_data = result['repro_debug_data']
        
        # Show key generations
        key_gens = [0, 5, 10, 13, 15, 20, 30, 50]
        for gen_data in repro_data:
            if gen_data['generation'] in key_gens or gen_data['generation'] <= 20:
                print(f"{gen_data['generation']:3d} | {gen_data['population']:3d} | "
                      f"{gen_data['eligible_count']:8d} | "
                      f"{gen_data['mode_blocked_count']:10d} | "
                      f"{gen_data['tau_blocked_count']:9d} | "
                      f"{gen_data['energy_low_count']:9d} | "
                      f"{gen_data['structure_low_count']:11d}")
        
        # Find when reproduction stops
        last_eligible_gen = 0
        for gen_data in repro_data:
            if gen_data['eligible_count'] > 0:
                last_eligible_gen = gen_data['generation']
        
        print(f"\nLast eligible reproduction at generation: {last_eligible_gen}")
        
        # Show the blocking reason after reproduction stops
        for gen_data in repro_data:
            if gen_data['generation'] > last_eligible_gen and gen_data['generation'] <= last_eligible_gen + 5:
                reasons = gen_data['reproduction_reasons']
                if reasons:
                    main_reason = max(reasons.keys(), key=lambda k: reasons[k])
                    print(f"Gen {gen_data['generation']}: Main blocking reason = {main_reason} ({reasons[main_reason]} cells)")
                break

if __name__ == "__main__":
    run_reproduction_debug()
