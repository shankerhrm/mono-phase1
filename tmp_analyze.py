import json

with open('tmp_bd_balance.json', 'r', encoding='utf-16') as f:
    text = f.read()
    data = json.loads(text[text.find('{'):])

print(f"{'gen':>4} {'pop':>5} {'births':>6} {'deaths':>6} {'env':>6} {'avgE':>6} {'avgAge':>6} {'p_rest':>6}")
print("-" * 60)
for x in data.get('metrics_per_gen', []):
    gen = x['gen']
    pop = x['population']
    births = x['successful_reproductions']
    deaths = x.get('deaths', 0)
    env = x['environmental_quality']
    avg_e = x['avg_energy']
    avg_age = x.get('avg_age', 0)
    p_rest = x.get('proportion_restoring', 0)
    print(f"{gen:>4} {pop:>5} {births:>6} {deaths:>6} {env:>6.3f} {avg_e:>6.1f} {avg_age:>6.1f} {p_rest:>6.2f}")
