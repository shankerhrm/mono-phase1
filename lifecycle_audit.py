#!/usr/bin/env python3
"""
Experiment K: Lifecycle Audit
Track births, deaths, age distribution, and reproduction events to identify structural extinction causes.
"""

import json
import statistics
from phase19_internal_economy import run_evolution

def run_lifecycle_audit():
    """Run diagnostic sweep with detailed lifecycle tracking."""
    
    # Parameters from best performing configuration
    restore_mults = [3.0]
    seeds = range(10)
    total_gens = 5000
    
    results = []
    
    for restore_mult in restore_mults:
        for seed in seeds:
            print(f"Running restore_mult {restore_mult}, seed {seed} ({seed+1}/10)")
            
            # Run evolution with lifecycle tracking
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
            
            # Extract lifecycle data from metrics
            metrics = summary['metrics_per_gen']
            lifecycle_data = []
            
            for gen_data in metrics:
                gen = gen_data['gen']
                pop = gen_data['population']
                
                # Calculate births and deaths from population change
                if gen == 0:
                    births = pop
                    deaths = 0
                else:
                    prev_pop = metrics[gen-1]['population']
                    births = max(0, pop - prev_pop)
                    deaths = max(0, prev_pop - pop)
                
                lifecycle_data.append({
                    'generation': gen,
                    'population': pop,
                    'births': births,
                    'deaths': deaths,
                    'avg_energy': gen_data.get('avg_energy', 0),
                    'avg_age': gen_data.get('avg_age', 0),
                    'reproduction_attempts': gen_data.get('reproduction_attempts', 0),
                    'successful_reproductions': births,
                    'total_energy_gained': gen_data.get('total_extraction', 0) + gen_data.get('total_restoration', 0),
                    'total_energy_spent': gen_data.get('total_energy_spent', 0)
                })
            
            result = {
                'restore_mult': restore_mult,
                'seed': seed,
                'final_gen': summary['final_gen'],
                'survived': summary['survived'],
                'peak_population': summary['peak_population'],
                'extinction_gen': summary['extinction_gen'],
                'min_environmental_quality': summary['min_environmental_quality'],
                'lifecycle_data': lifecycle_data
            }
            
            results.append(result)
    
    # Save results
    with open('lifecycle_audit_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Lifecycle audit complete. Results saved to lifecycle_audit_results.json")
    
    # Analyze results
    analyze_lifecycle_audit(results)

def analyze_lifecycle_audit(results):
    """Analyze lifecycle data to identify extinction patterns."""
    
    print("\n" + "="*60)
    print("LIFECYCLE AUDIT ANALYSIS")
    print("="*60)
    
    survivors = [r for r in results if r['survived']]
    extinct = [r for r in results if not r['survived']]
    
    print(f"Survivors: {len(survivors)}/{len(results)}")
    print(f"Extinct: {len(extinct)}/{len(results)}")
    
    if extinct:
        extinction_gens = [r['extinction_gen'] for r in extinct]
        print(f"Extinction Generations: Mean {statistics.mean(extinction_gens):.1f}, Std {statistics.stdev(extinction_gens):.1f}")
        
        # Analyze extinction patterns
        print("\nExtinction Pattern Analysis:")
        for result in extinct[:3]:  # Show first 3 examples
            gen_data = result['lifecycle_data']
            extinction_gen = result['extinction_gen']
            
            # Look at last 20 generations
            last_gens = gen_data[max(0, extinction_gen-20):extinction_gen+1]
            
            print(f"\nSeed {result['seed']} - Extinction at gen {extinction_gen}:")
            print("Gen | Pop | Births | Deaths | Avg Energy | Repro Attempts")
            print("-" * 55)
            
            for gen in last_gens:
                if gen['generation'] % 2 == 0:  # Show every other generation to save space
                    print(f"{gen['generation']:3d} | {gen['population']:3d} | {gen['births']:6d} | {gen['deaths']:6d} | {gen['avg_energy']:10.2f} | {gen['reproduction_attempts']:13d}")
    
    # Check for age-related patterns
    print("\nAge Distribution Analysis:")
    for result in extinct[:2]:
        gen_data = result['lifecycle_data']
        extinction_gen = result['extinction_gen']
        
        # Find generation where births stopped
        last_birth_gen = 0
        for gen in reversed(gen_data):
            if gen['births'] > 0:
                last_birth_gen = gen['generation']
                break
        
        print(f"Seed {result['seed']}: Last birth at gen {last_birth_gen}, extinction at {extinction_gen} (gap: {extinction_gen - last_birth_gen})")

if __name__ == "__main__":
    run_lifecycle_audit()
