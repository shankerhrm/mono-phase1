import subprocess, sys, json, os

cmd = [sys.executable, 'phase19_internal_economy.py', '--seed', '0', '--total_gens', '30', 
       '--depletion_rate', '0.03', '--regeneration_rate', '0.01', '--restore_mult', '2.0', '--target', '50']
result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__) or '.')
data = json.loads(result.stdout)

m = data.get('metrics_per_gen', [])
lines = []
lines.append(f"{'gen':>4} {'pop':>5} {'births':>6} {'deaths':>6} {'net':>5} {'env':>6} {'avgE':>7} {'avgAge':>6} {'reasons':>35}")
lines.append("-" * 120)
for x in m:
    gen = x['gen']
    pop = x['population']
    births = x['successful_reproductions']
    deaths = x.get('deaths', 0)
    net = births - deaths
    env = x['environmental_quality']
    avg_e = x['avg_energy']
    avg_age = x.get('avg_age', 0)
    reasons = x.get('death_reasons', {})
    reasons_str = json.dumps(reasons)
    lines.append(f"{gen:>4} {pop:>5} {births:>6} {deaths:>6} {net:>+5} {env:>6.3f} {avg_e:>7.1f} {avg_age:>6.1f} {reasons_str:>35}")

lines.append(f"\nFinal gen: {data.get('final_gen')}, Peak: {data.get('peak_population')}")

with open('tmp_bd_balance.txt', 'w') as f:
    f.write('\n'.join(lines))
print("Saved to tmp_bd_balance.txt")
