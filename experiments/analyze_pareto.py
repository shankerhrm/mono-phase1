import csv
import json
from collections import defaultdict, Counter

# Read reproduction_traces.csv
reproductions = []
with open('regime_flip_artifacts/reproduction_traces.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        reproductions.append(row)

# Read history.json for Ms evolution
with open('regime_flip_history.json', 'r') as f:
    history = json.load(f)

# Count reproductions per lineage_id (using parent_id as proxy)
lineage_counts = Counter()
lineage_gammas = defaultdict(list)
for rep in reproductions:
    lineage_id = rep['parent_id']  # Using parent_id as lineage proxy
    lineage_counts[lineage_id] += 1
    params = json.loads(rep['offspring_initial_params_json'])
    gamma = float(params['gamma'])
    lineage_gammas[lineage_id].append(gamma)

# Top 3 lineages
top_lineages = lineage_counts.most_common(3)
print("Top 3 Lineages by Reproduction Count:")
for lineage, count in top_lineages:
    avg_gamma = sum(lineage_gammas[lineage]) / len(lineage_gammas[lineage])
    print(f"Lineage {lineage}: {count} reproductions, Avg Inherited Gamma: {avg_gamma:.3f}")

# Global Ms average in B gens
b_gens = [entry for entry in history if entry['env'] == 'B']
if b_gens:
    ms_gammas = [entry['Ms']['gamma'] for entry in b_gens]
    avg_ms_gamma = sum(ms_gammas) / len(ms_gammas)
    print(f"\nGlobal Ms Gamma Average in B: {avg_ms_gamma:.3f}")
    print(f"Ms Gamma Range in B: {min(ms_gammas):.3f} to {max(ms_gammas):.3f}")
else:
    print("No B gens found in history.")
