#!/usr/bin/env python3
"""
Phase 16 Stress Test Visualization
Generates plots showing evolutionary convergence and robustness of α/β phenotypes
"""

import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def load_results():
    """Load stress test results from artifacts"""
    base_path = Path("phase16_stress_artifacts/stress_tests_20260304_172053")

    with open(base_path / "mutation_results.json", 'r') as f:
        mutation_data = json.load(f)

    with open(base_path / "period_results.json", 'r') as f:
        period_data = json.load(f)

    return mutation_data, period_data

def plot_mutation_convergence(mutation_data):
    """Plot α/β convergence across mutation scales"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Phase 16: Mutation Sweep - Evolutionary Convergence', fontsize=16, fontweight='bold')

    scales = ['0.1', '1.0', '5.0']

    for i, scale in enumerate(scales):
        ax = axes[i//2, i%2]
        scale_data = mutation_data["mutation"][scale]

        alphas = []
        betas = []
        ratios = []
        fps = []

        for seed_data in scale_data:
            final_metrics = seed_data["metrics"][-1]  # Last generation
            alphas.append(final_metrics["mean_alpha"])
            betas.append(final_metrics["mean_beta"])
            ratios.append(final_metrics["alpha_beta_ratio"])
            fps.append(final_metrics["fp"])

        # Plot final values
        ax.scatter(alphas, betas, alpha=0.7, s=50, label=f'α/β points (scale {scale}×)')
        ax.scatter([np.mean(alphas)], [np.mean(betas)], color='red', s=100,
                  marker='*', label='Mean attractor')
        ax.set_xlabel('α (Stress Sensitivity)')
        ax.set_ylabel('β (Repair Efficiency)')
        ax.set_title(f'Mutation Scale {scale}× (n=5 seeds)')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Add text annotation
        ax.text(0.05, 0.95, '.3f',
               transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Attractor analysis
    ax = axes[1, 1]
    all_alphas = []
    all_betas = []
    for scale in scales:
        for seed_data in mutation_data["mutation"][scale]:
            final = seed_data["metrics"][-1]
            all_alphas.append(final["mean_alpha"])
            all_betas.append(final["mean_beta"])

    ax.scatter(all_alphas, all_betas, alpha=0.6, s=30, c='blue', label='All final points')
    ax.scatter([np.mean(all_alphas)], [np.mean(all_betas)], color='red', s=150,
              marker='*', label='Global attractor')
    ax.axhline(y=0.3, color='green', linestyle='--', alpha=0.5, label='β=0.3')
    ax.axvline(x=0.2, color='orange', linestyle='--', alpha=0.5, label='α=0.2')
    ax.set_xlabel('α (Stress Sensitivity)')
    ax.set_ylabel('β (Repair Efficiency)')
    ax.set_title('Global Attractor Analysis (15 runs)')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig('phase16_mutation_convergence.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_period_adaptation(period_data):
    """Plot environmental adaptation across periods"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Phase 16: Period Sweep - Environmental Adaptation', fontsize=16, fontweight='bold')

    periods = ['20', '40', '160', '300']

    # Period vs FP rate
    ax = axes[0, 0]
    period_nums = [int(p) for p in periods]
    mean_fps = []
    std_fps = []

    for period in periods:
        fps = [seed["final_fp"] for seed in period_data["period"][period]]
        mean_fps.append(np.mean(fps))
        std_fps.append(np.std(fps))

    ax.errorbar(period_nums, mean_fps, yerr=std_fps, fmt='o-', capsize=5,
               linewidth=2, markersize=8, color='blue')
    ax.set_xlabel('Environment Period (generations)')
    ax.set_ylabel('False Positive Rate')
    ax.set_title('FP Rate vs Environment Period')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)

    # Period vs Load
    ax = axes[0, 1]
    mean_loads = []
    std_loads = []

    for period in periods:
        loads = [seed["final_load"] for seed in period_data["period"][period]]
        mean_loads.append(np.mean(loads))
        std_loads.append(np.std(loads))

    ax.errorbar(period_nums, mean_loads, yerr=std_loads, fmt='s-', capsize=5,
               linewidth=2, markersize=8, color='red')
    ax.set_xlabel('Environment Period (generations)')
    ax.set_ylabel('Mean Physiological Load')
    ax.set_title('Load vs Environment Period')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)

    # Alpha/Beta stability across periods
    ax = axes[1, 0]
    alphas = []
    betas = []
    labels = []

    for period in periods:
        for seed in period_data["period"][period]:
            alphas.append(seed["final_alpha"])
            betas.append(seed["final_beta"])
            labels.append(f'P{period}')

    scatter = ax.scatter(alphas, betas, c=[int(l[1:]) for l in labels],
                        cmap='viridis', alpha=0.7, s=40)
    ax.scatter([0.2], [0.3], color='red', s=200, marker='*', label='Universal Attractor')
    ax.set_xlabel('α (Stress Sensitivity)')
    ax.set_ylabel('β (Repair Efficiency)')
    ax.set_title('α/β Stability Across Periods')
    ax.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax, label='Period')

    # Convergence vs Period
    ax = axes[1, 1]
    mean_convs = []
    std_convs = []

    for period in periods:
        convs = [seed["final_convergence"] for seed in period_data["period"][period]]
        mean_convs.append(np.mean(convs))
        std_convs.append(np.std(convs))

    ax.errorbar(period_nums, mean_convs, yerr=std_convs, fmt='^-', capsize=5,
               linewidth=2, markersize=8, color='green')
    ax.set_xlabel('Environment Period (generations)')
    ax.set_ylabel('Omega Convergence Ratio')
    ax.set_title('Synchronization vs Environment Period')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('phase16_period_adaptation.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_evolution_trajectory(mutation_data):
    """Plot evolution trajectory for one representative run"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Phase 16: Representative Evolution Trajectory', fontsize=16, fontweight='bold')

    # Use first seed from 1.0x scale
    sample_data = mutation_data["mutation"]["1.0"][0]
    metrics = sample_data["metrics"]

    gens = [m["gen"] for m in metrics]
    alphas = [m["mean_alpha"] for m in metrics]
    betas = [m["mean_beta"] for m in metrics]
    ratios = [m["alpha_beta_ratio"] for m in metrics]
    fps = [m["fp"] for m in metrics]
    loads = [m["mean_load"] for m in metrics]
    omegas = [m["omega_mean"] for m in metrics]
    convs = [m["convergence"] for m in metrics]

    # Alpha/Beta evolution
    ax = axes[0, 0]
    ax.plot(gens, alphas, 'b-', linewidth=2, label='α (stress sensitivity)')
    ax.plot(gens, betas, 'r-', linewidth=2, label='β (repair efficiency)')
    ax.axhline(y=0.2, color='blue', linestyle='--', alpha=0.5, label='Final α=0.2')
    ax.axhline(y=0.3, color='red', linestyle='--', alpha=0.5, label='Final β=0.3')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Parameter Value')
    ax.set_title('α/β Evolution Trajectory')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Ratio evolution
    ax = axes[0, 1]
    ax.plot(gens, ratios, 'g-', linewidth=2)
    ax.axhline(y=0.6667, color='green', linestyle='--', alpha=0.5, label='Final ratio=0.667')
    ax.set_xlabel('Generation')
    ax.set_ylabel('α/β Ratio')
    ax.set_title('Regulatory Ratio Evolution')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Performance metrics
    ax = axes[1, 0]
    ax.plot(gens, fps, 'purple', linewidth=2, label='FP Rate')
    ax.plot(gens, loads, 'orange', linewidth=2, label='Mean Load')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Performance Metric')
    ax.set_title('System Performance Evolution')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Convergence metrics
    ax = axes[1, 1]
    ax.plot(gens, omegas, 'cyan', linewidth=2, label='Omega Mean')
    ax.plot(gens, convs, 'magenta', linewidth=2, label='Convergence Ratio')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Synchronization Metric')
    ax.set_title('Population Synchronization')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig('phase16_evolution_trajectory.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Generate all Phase 16 visualizations"""
    print("Loading Phase 16 stress test results...")
    mutation_data, period_data = load_results()

    print("Generating mutation convergence plots...")
    plot_mutation_convergence(mutation_data)

    print("Generating period adaptation plots...")
    plot_period_adaptation(period_data)

    print("Generating evolution trajectory plots...")
    plot_evolution_trajectory(mutation_data)

    print("Visualizations saved as PNG files:")
    print("- phase16_mutation_convergence.png")
    print("- phase16_period_adaptation.png")
    print("- phase16_evolution_trajectory.png")

if __name__ == "__main__":
    main()
