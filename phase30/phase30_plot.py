import json
import matplotlib.pyplot as plt
import os

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
             return json.load(f)
    return []

def main():
    metrics = load_json("phase30/phase30_metrics.json")
    baseline = load_json("phase30/baseline_metrics.json")
    
    if not metrics:
        print("No evolution metrics found. Run phase30_evolution.py first.")
        return

    generations = [m["generation"] for m in metrics]
    success_rates = [m["success_rate"] * 100 for m in metrics]
    avg_energies = [m["avg_energy"] for m in metrics]
    
    baseline_success = None
    if baseline:
        baseline_success = baseline[-1]["success_rate"] * 100
        print(f"Base Gemini Success Rate: {baseline_success:.2f}%\n")
        
    # --- PLOT 1: ACCURACY GROWTH ---
    plt.figure(figsize=(10, 5))
    plt.plot(generations, success_rates, marker='o', label="MONO Agents", color='b')
    if baseline_success is not None:
        plt.axhline(y=baseline_success, color='r', linestyle='--', label=f"Baseline ({baseline_success:.1f}%)")
        
    plt.title("Phase 30: Task Success Rate Over Time")
    plt.xlabel("Generation")
    plt.ylabel("Success Rate (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("phase30/accuracy_growth.png")
    print("Saved phase30/accuracy_growth.png")
    
    # --- PLOT 2: EFFICIENCY GROWTH ---
    plt.figure(figsize=(10, 5))
    plt.plot(generations, avg_energies, marker='s', label="Avg Agent Energy", color='g')
    plt.title("Phase 30: System Energy Dynamics Over Time")
    plt.xlabel("Generation")
    plt.ylabel("Average Energy Reserves")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("phase30/efficiency_growth.png")
    print("Saved phase30/efficiency_growth.png")
    
    # --- LEADERBOARD ---
    print("\n--- FINAL DOMINANT HEURISTICS LEADERBOARD ---")
    final_dom = metrics[-1].get("dominant_heuristics", [])
    for i, h in enumerate(final_dom, 1):
        print(f"{i}. {h}")
        
if __name__ == "__main__":
    main()
