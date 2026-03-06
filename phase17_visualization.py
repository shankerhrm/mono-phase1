#!/usr/bin/env python3
"""
Phase 17 Cultural Niche Construction Visualization
Generates plots showing cultural evolution and ecological feedback
"""

import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def load_results():
    """Load Phase 17 results"""
    with open("phase17_artifacts/cultural_evolution_results.json", 'r') as f:
        data = json.load(f)
    return data

def plot_artifact_trajectory(data):
    """Plot cultural artifact accumulation"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot for each seed
    for result in data:
        gens = [m['gen'] for m in result['metrics']]
        artifacts = [m['mean_artifact_value'] for m in result['metrics']]
        ax.plot(gens, artifacts, alpha=0.7, linewidth=1)

    # Plot average
    max_gens = max(len(r['metrics']) for r in data)
    avg_artifacts = []
    for gen in range(max_gens):
        gen_values = [r['metrics'][gen]['mean_artifact_value'] for r in data if gen < len(r['metrics'])]
        if gen_values:
            avg_artifacts.append(np.mean(gen_values))
        else:
            avg_artifacts.append(np.nan)

    ax.plot(range(max_gens), avg_artifacts, 'r-', linewidth=3, label='Average across seeds')

    ax.set_xlabel('Generation')
    ax.set_ylabel('Mean Artifact Value')
    ax.set_title('Phase 17: Cultural Artifact Accumulation (Ratchet Effect)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Baseline')

    plt.tight_layout()
    plt.savefig('phase17_artifact_trajectory.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_environmental_decline(data):
    """Plot environmental quality decline"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot for each seed
    for result in data:
        gens = [m['gen'] for m in result['metrics']]
        envs = [m['environmental_quality'] for m in result['metrics']]
        ax.plot(gens, envs, alpha=0.7, linewidth=1)

    # Plot average
    max_gens = max(len(r['metrics']) for r in data)
    avg_envs = []
    for gen in range(max_gens):
        gen_values = [r['metrics'][gen]['environmental_quality'] for r in data if gen < len(r['metrics'])]
        if gen_values:
            avg_envs.append(np.mean(gen_values))
        else:
            avg_envs.append(np.nan)

    ax.plot(range(max_gens), avg_envs, 'b-', linewidth=3, label='Average environmental quality')

    ax.set_xlabel('Generation')
    ax.set_ylabel('Environmental Quality')
    ax.set_title('Phase 17: Environmental Decline (Niche Construction Feedback)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axhline(y=1.0, color='green', linestyle='--', alpha=0.5, label='Initial quality')

    plt.tight_layout()
    plt.savefig('phase17_environmental_decline.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_coevolution_trajectory(data):
    """Plot gene-culture coevolution dynamics"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Phase 17: Gene-Culture Coevolution Dynamics', fontsize=16, fontweight='bold')

    # Use surviving seed (last one) as representative
    result = data[-1]  # Last seed survived
    metrics = result['metrics']

    gens = [m['gen'] for m in metrics]
    learning_rates = [m['avg_learning_rate'] for m in metrics]
    teaching_efficiencies = [m['avg_teaching_efficiency'] for m in metrics]
    artifacts = [m['mean_artifact_value'] for m in metrics]
    energies = [m['avg_energy'] for m in metrics]

    # Learning rate evolution
    ax = axes[0, 0]
    ax.plot(gens, learning_rates, 'b-', linewidth=2)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Learning Rate')
    ax.set_title('Genetic Evolution: Learning Rate')
    ax.grid(True, alpha=0.3)

    # Teaching efficiency evolution
    ax = axes[0, 1]
    ax.plot(gens, teaching_efficiencies, 'r-', linewidth=2)
    ax.set_xlabel('Generation')
    ax.set_ylabel('Teaching Efficiency')
    ax.set_title('Genetic Evolution: Teaching Efficiency')
    ax.grid(True, alpha=0.3)

    # Artifact vs Energy
    ax = axes[1, 0]
    ax.plot(gens, artifacts, 'g-', linewidth=2, label='Mean Artifact')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Artifact Value / Energy', color='g')
    ax.tick_params(axis='y', labelcolor='g')
    ax.grid(True, alpha=0.3)

    ax2 = ax.twinx()
    ax2.plot(gens, energies, 'orange', linewidth=2, label='Avg Energy')
    ax2.set_ylabel('Average Energy', color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')
    ax.set_title('Cultural Fitness Impact')

    # Combined trajectory
    ax = axes[1, 1]
    ax.plot(gens, learning_rates, 'b-', linewidth=2, label='Learning Rate')
    ax.plot(gens, teaching_efficiencies, 'r-', linewidth=2, label='Teaching Efficiency')
    ax.plot(gens, [a - 1.0 for a in artifacts], 'g-', linewidth=2, label='Artifact Bonus')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Trait Values')
    ax.set_title('Multi-Level Coevolution')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig('phase17_coevolution_trajectory.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all Phase 17 visualizations"""
    print("Loading Phase 17 results...")
    data = load_results()

    print("Generating artifact trajectory plot...")
    plot_artifact_trajectory(data)

    print("Generating environmental decline plot...")
    plot_environmental_decline(data)

    print("Generating coevolution trajectory plot...")
    plot_coevolution_trajectory(data)

    print("Visualizations saved as PNG files:")
    print("- phase17_artifact_trajectory.png")
    print("- phase17_environmental_decline.png")
    print("- phase17_coevolution_trajectory.png")

if __name__ == "__main__":
    main()
