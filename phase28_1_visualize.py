import json
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

GRID_SIZE = 50

def generate_spatial_plots(seed):
    filepath = f"phase28_1_results_seed{seed}.json"
    if not os.path.exists(filepath):
        print(f"File {filepath} not found.")
        return
        
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    if len(data) == 0:
        print("Empty data file.")
        return
        
    gens_to_plot = [data[0], data[len(data)//2], data[-1]] # Start, Middle, End
    
    fig, axes = plt.subplots(3, 2, figsize=(10, 15))
    fig.suptitle('Phase 28.1: Spatial Resilience & Correction', fontsize=16)
    
    for i, snapshot in enumerate(gens_to_plot):
        gen = snapshot['generation']
        env_map = np.array(snapshot['env_map'])
        trait_map = np.array(snapshot['trait_map'])
        
        # Mask empty tiles (-1) in trait map with NaN for clean visualization
        trait_masked = np.where(trait_map == -1, np.nan, trait_map)
        
        # Plot Environment
        ax_env = axes[i, 0]
        im_env = ax_env.imshow(env_map, cmap='YlGn', vmin=0.1, vmax=2.0)
        ax_env.set_title(f"Environment Quality (Gen {gen})")
        fig.colorbar(im_env, ax=ax_env, fraction=0.046, pad=0.04)
        
        # Plot Traits
        ax_trait = axes[i, 1]
        im_trait = ax_trait.imshow(trait_masked, cmap='coolwarm', vmin=0.0, vmax=1.0)
        ax_trait.set_title(f"Strategy Traits (Gen {gen})\nBlue=Extract, Red=Restore")
        # Add gray background for empty tiles
        ax_trait.set_facecolor('darkgray')
        fig.colorbar(im_trait, ax=ax_trait, fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.savefig(f"phase28_1_heatmaps_seed{seed}.png", dpi=300)
    plt.close()
    
    # Generate Time Series
    generations = [d['generation'] for d in data]
    pops = [d['population'] for d in data]
    mean_traits = [d['mean_trait'] for d in data]
    var_traits = [d['var_trait'] for d in data]
    depletions = [d['depletion_rate'] for d in data]
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    color = 'tab:green'
    ax1.set_xlabel('Generation')
    ax1.set_ylabel('Env Depletion Rate / Population', color=color)
    ax1.plot(generations, depletions, color='tab:green', label='Depletion Rate', alpha=0.5)
    
    # Scale population for dual axis visualization
    scaled_pop = [p / 2500 for p in pops] # 2500 is max capacity (50x50 at density 1? 10 density is 25000 max)
    ax1.plot(generations, scaled_pop, color='grey', label='Population (Scaled)', alpha=0.9)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Mean Strategy Trait', color=color)
    ax2.plot(generations, mean_traits, color=color, label='Mean Trait')
    ax2.plot(generations, var_traits, color='purple', label='Trait Variance', linestyle='--')
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Phase 28.1 Shock Annotations
    ax2.axvline(x=800, color='black', linestyle=':', linewidth=2, label='K-T Extinction (50% Cull)')
    ax1.axvspan(1100, 1150, color='gold', alpha=0.3, label='Global Famine')
    
    fig.tight_layout()
    plt.title('Phase 28.1: Global Spatial Resilience Dynamics')
    fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
    plt.savefig(f'phase28_1_timeseries_seed{seed}.png', dpi=300)
    plt.close()
    print(f"Visualization complete: phase28_1_heatmaps_seed{seed}.png, phase28_1_timeseries_seed{seed}.png")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    generate_spatial_plots(args.seed)
