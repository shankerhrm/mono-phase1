import json
import matplotlib.pyplot as plt
import numpy as np

def generate_plots():
    # Load phase diagram data
    try:
        with open('phase18_sweep/phase_diagram.json', 'r') as f:
            phase_data = json.load(f)
    except Exception as e:
        print(f"Error loading phase diagram data: {e}")
        return

    # Extract unique depletions (x-axis) and restore_mults (y-axis)
    dep_str = set()
    rm_str = set()
    for key in phase_data.keys():
        try:
            # phase_data keys are strings representing tuples like "(0.08, 0.15)"
            key_tuple = eval(key)
            dep_str.add(key_tuple[0])
            rm_str.add(key_tuple[1])
        except Exception:
            pass

    depletions = sorted(list(dep_str))
    restore_mults = sorted(list(rm_str))

    # Initialize grid
    regime_grid = np.zeros((len(restore_mults), len(depletions)))
    
    # Map regimes to numbers for plotting
    regime_map = {'I': 0, 'II': 1, 'III': 2, '?': -1}
    
    for i, dep in enumerate(depletions):
        for j, rm in enumerate(restore_mults):
            key = str((dep, rm))
            if key in phase_data:
                regime = phase_data[key].get('regime', '?')
                regime_grid[j, i] = regime_map.get(regime, -1)

    # Plot Regime Diagram
    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = plt.cm.get_cmap('viridis', 3)
    cax = ax.imshow(regime_grid, origin='lower', cmap=cmap, aspect='auto')
    
    # Set ticks
    ax.set_xticks(np.arange(len(depletions)))
    ax.set_yticks(np.arange(len(restore_mults)))
    ax.set_xticklabels([f"{d:.3f}" for d in depletions])
    ax.set_yticklabels([f"{r:.2f}" for r in restore_mults])
    
    # Add colorbar
    cbar = fig.colorbar(cax, ticks=[0.33, 1.0, 1.66])
    cbar.ax.set_yticklabels(['Stable (I)', 'Oscillatory (II)', 'Collapse (III)'])
    
    ax.set_xlabel("Depletion Rate")
    ax.set_ylabel("Restoration Multiplier")
    ax.set_title("Phase 18: Socio-Ecological Regimes")
    
    plt.tight_layout()
    plt.savefig('phase18_regime_diagram.png', dpi=300)
    print("Generated phase18_regime_diagram.png")
    
    # Load sweep results to plot trajectories
    try:
        with open('phase18_sweep/sweep_results.json', 'r') as f:
            sweep_results = json.load(f)
    except Exception as e:
        print(f"Error loading sweep results data: {e}")
        return
        
    # Find a representative oscillatory run (Regime II)
    rep_run = None
    for res in sweep_results:
        if 'error' in res:
            continue
        key_str = str((res['depletion'], res['restore_mult']))
        if key_str in phase_data and phase_data[key_str].get('regime') == 'II':
            rep_run = res
            break
            
    # If no oscillatory run found, just pick the first successful one
    if not rep_run:
        for res in sweep_results:
            if 'error' not in res and not res['result']['summary'].get('extinct', True):
                rep_run = res
                break
        
        # If no surviving runs either, just pick the first one regardless to get a plot
        if not rep_run and sweep_results:
            rep_run = sweep_results[0]
                
    if not rep_run:
        print("No successful runs found to plot trajectories.")
        return
        
    gen_data = rep_run['result']['gen_data']
    gens = [g['gen'] for g in gen_data]
    
    # Plot Proportion Restoring
    prop_restoring = [g.get('proportion_restoring', 0) for g in gen_data]
    
    plt.figure(figsize=(10, 6))
    plt.plot(gens, prop_restoring, color='blue', linewidth=2)
    plt.xlabel('Generation')
    plt.ylabel('Proportion Restoring')
    plt.title(f"Restoration Dynamics (Depletion: {rep_run['depletion']:.3f}, RM: {rep_run['restore_mult']:.2f})")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('phase18_proportion_restoring.png', dpi=300)
    print("Generated phase18_proportion_restoring.png")
    
    # Plot Environmental Trajectory
    env_quality = [g['environmental_quality'] for g in gen_data]
    
    plt.figure(figsize=(10, 6))
    plt.plot(gens, env_quality, color='green', linewidth=2)
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Initial Quality')
    plt.xlabel('Generation')
    plt.ylabel('Environmental Quality')
    plt.title(f"Environmental Feedback (Depletion: {rep_run['depletion']:.3f}, RM: {rep_run['restore_mult']:.2f})")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('phase18_environmental_trajectory.png', dpi=300)
    print("Generated phase18_environmental_trajectory.png")

if __name__ == "__main__":
    generate_plots()
