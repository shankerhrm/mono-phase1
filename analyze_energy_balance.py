import json

with open('diagnostic_output.json', 'r') as f:
    gen_data = json.load(f)

print("Energy Balance Analysis: Seed 42, restore_mult=3.0, target=20")
print("Gen | Pop | Env_Q | Total_Extract | Total_Restore | Difference | Ratio (E/R)")
print("-" * 80)

extraction_always_greater = True
for gen in gen_data[:50]:  # First 50 gens
    extract = gen['total_extraction']
    restore = gen['total_restoration']
    diff = extract - restore
    ratio = extract / restore if restore > 0 else float('inf')
    if extract <= restore:
        extraction_always_greater = False
    print(f"{gen['gen']:3} | {gen['population']:3} | {gen['environmental_quality']:.3f} | {extract:12.2f} | {restore:12.2f} | {diff:10.2f} | {ratio:8.2f}")

print("\nExtraction always > Restoration?", extraction_always_greater)

# Last 10 gens before extinction
print("\nLast 10 gens before extinction:")
for gen in gen_data[-10:]:
    extract = gen['total_extraction']
    restore = gen['total_restoration']
    diff = extract - restore
    ratio = extract / restore if restore > 0 else float('inf')
    print(f"Gen {gen['gen']}: Extract {extract:.2f}, Restore {restore:.2f}, Diff {diff:.2f}, Ratio {ratio:.2f}")

print("\nConclusion: If extraction > restoration consistently, extinction is mathematically guaranteed.")
