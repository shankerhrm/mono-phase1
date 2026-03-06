import subprocess
import json

# Run diagnostic with environmental coupling
result = subprocess.run([
    'python', 'phase19_internal_economy.py',
    '--restore_mult', '3.0',
    '--target', '20',
    '--seed', '0'
], capture_output=True, text=True)

if result.returncode == 0:
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        output = '\n'.join(lines[1:])  # Skip the title line
    else:
        output = lines[0] if lines else ''
    print("Stderr:", result.stderr)
    try:
        data = json.loads(output)
        print("Diagnostic Run: Seed 42, restore_mult=3.0, target=20")
        print("Summary keys:", list(data['summary'].keys()))
        print("Final gen:", data['summary'].get('final_gen', 'missing'))
        print("Extinct:", data['summary']['extinct'])
        print("\nPer-gen data (first 20 gens):")
        for i, gen_data in enumerate(data['gen_data'][:5]):  # First 5 gens
            print(f"Gen {gen_data['gen']}: keys {list(gen_data.keys())}")
        print("\nFull gen_data logged to diagnostic_output.json")
        with open('diagnostic_output.json', 'w') as f:
            json.dump(data['gen_data'], f, indent=2)
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        print("Stdout len:", len(output))
else:
    print("Error:", result.stderr)
