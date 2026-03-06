import json
import subprocess
import sys
import os

def run_stability_test():
    print("Starting Phase 24.5 Engine Stability Test (Fixed Env=1.0)...")
    
    # We will use a modified version of the internal economy script or pass params that saturate env
    # For a "Fixed Env" test, we can just set depletion to 0 and regeneration to 1.0
    cmd = [
        sys.executable, 'phase19_internal_economy.py',
        '--seed', '42',
        '--total_gens', '1000',
        '--fixed_env',
        '--max_pop', '200',
        '--target', '100'
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.path.dirname(__file__) or '.')
    
    output_lines = []
    for line in process.stderr:
        print(line, end='', flush=True)  # Print progress
    
    stdout, stderr = process.communicate()
    data = None
    try:
        start = stdout.find('{')
        if start != -1:
            data = json.loads(stdout[start:])
    except json.JSONDecodeError:
        print("Could not parse simulation output.")
        return

    if not data:
        print("No data returned.")
        return

    metrics = data.get('metrics_per_gen', [])
    final_gen = data.get('final_gen', 0)
    survived = data.get('survived', False)
    
    print(f"Simulation completed. Final Generation: {final_gen}, Survived: {survived}")
    
    # 1. Audit Energy Conservation
    total_intake = data.get('total_audit_intake', 0)
    total_burn = data.get('total_audit_burn', 0)
    
    # If metrics exist, we can use them to see reproduction distribution
    if not total_intake and metrics:
        for m in metrics:
            pop_size = m['population']
            total_intake += m.get('avg_intake', 0) * pop_size
            total_burn += m.get('avg_burn', 0) * pop_size
        
    print(f"\n--- Energy Audit ---")
    print(f"Aggregate Intake: {total_intake:.2f}")
    print(f"Aggregate Burn:   {total_burn:.2f}")
    if total_intake >= total_burn:
        print("Status: Energy Surplus (Safe)")
    else:
        # Check if deficit is just split cost/initial E (approx 30 per cell)
        print("Status: Energy Deficit (Check Initial E/Splits)")

    # 2. Birth Distribution
    if metrics:
        births = [m['successful_reproductions'] for m in metrics]
        zero_birth_gens = births.count(0)
        max_births = max(births) if births else 0
        avg_births = sum(births)/len(births) if births else 0
        
        print(f"\n--- Birth Distribution ---")
        print(f"Average Births/Gen: {avg_births:.2f}")
        print(f"Max Births/Gen:     {max_births}")
        print(f"Generations with 0 births: {zero_birth_gens}/{len(metrics)}")
    else:
        print(f"\n--- Birth Distribution ---")
        print(f"Total Audit Reproductions: {data.get('total_audit_repro', 0)}")
    
    # 3. Death Reasons Check (from final metrics or summary)
    print(f"\n--- Death Reasons Audit ---")
    all_reasons = data.get('death_reasons', {}) # Note: I should add this to summary in phase19 if missing
    if not all_reasons and metrics:
        for m in metrics:
            reasons = m.get('death_reasons', {})
            for k, v in reasons.items():
                all_reasons[k] = all_reasons.get(k, 0) + v
            
    if not all_reasons:
        print("No deaths recorded in summary. Checking if metrics exist...")
    else:
        for k, v in all_reasons.items():
            print(f"{k}: {v}")

    if survived and final_gen >= 999:
        print("\n✅ Stability Test PASSED: Engine is micro-stable for 1000 generations.")
    else:
        print("\n❌ Stability Test FAILED: Extinction occurred before 1000 generations.")

if __name__ == "__main__":
    run_stability_test()
