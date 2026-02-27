# Plots for Burn / Energy / Structure curves

def mean(values):
    return sum(values) / len(values) if values else 0

def plot_experiment(logs, title="MONO Run"):
    """
    Plot Energy, Burn, and Structure trajectories.
    Assumes matplotlib is available.
    """
    try:
        import matplotlib.pyplot as plt
        cycles = [log['cycle'] for log in logs]
        energies = [log['E'] for log in logs]
        burns = [log['burn'] for log in logs]
        structures = [log['structure_size'] for log in logs]

        plt.figure(figsize=(10, 6))
        plt.subplot(3, 1, 1)
        plt.plot(cycles, energies)
        plt.title(f'Energy Trajectory - {title}')
        plt.ylabel('Energy')

        plt.subplot(3, 1, 2)
        plt.plot(cycles, burns)
        plt.title(f'Burn - {title}')
        plt.ylabel('Burn')

        plt.subplot(3, 1, 3)
        plt.plot(cycles, structures)
        plt.title(f'Structure Size - {title}')
        plt.ylabel('Structure Size')
        plt.xlabel('Cycle')

        plt.tight_layout()
        plt.show()
    except ImportError:
        print("Matplotlib not available. Printing text summary.")
        print(f"Experiment: {title}")
        print("Cycle\tEnergy\tBurn\tStructure")
        for log in logs:
            print(f"{log['cycle']}\t{log['E']}\t{log['burn']}\t{log['structure_size']}")

def plot_group_overlay(group_logs, title):
    """
    Plot overlay of multiple runs for a group, with average curves.
    group_logs: list of (run_id, logs_list)
    """
    try:
        import matplotlib.pyplot as plt
        # import numpy as np

        plt.figure(figsize=(12, 8))

        # Energy subplot
        plt.subplot(3, 1, 1)
        all_e = []
        for run_id, logs in group_logs:
            e = [log['E'] for log in logs]
            plt.plot(e, alpha=0.3, color='blue', linewidth=0.5)
            all_e.append(e)
        if all_e:
            min_len = min(len(e) for e in all_e)
            avg_e = [mean([e[i] for e in all_e if i < len(e)]) for i in range(min_len)]
            plt.plot(avg_e, color='blue', linewidth=2, label='Average')
        plt.title(f'Energy Trajectories - {title}')
        plt.ylabel('Energy')
        plt.legend()

        # Burn subplot
        plt.subplot(3, 1, 2)
        all_b = []
        for run_id, logs in group_logs:
            b = [log['burn'] for log in logs]
            plt.plot(b, alpha=0.3, color='red', linewidth=0.5)
            all_b.append(b)
        if all_b:
            min_len = min(len(b) for b in all_b)
            avg_b = [mean([b[i] for b in all_b if i < len(b)]) for i in range(min_len)]
            plt.plot(avg_b, color='red', linewidth=2, label='Average')
        plt.title(f'Burn Trajectories - {title}')
        plt.ylabel('Burn')
        plt.legend()

        # Structure subplot
        plt.subplot(3, 1, 3)
        all_s = []
        for run_id, logs in group_logs:
            s = [log['structure_size'] for log in logs]
            plt.plot(s, alpha=0.3, color='green', linewidth=0.5)
            all_s.append(s)
        if all_s:
            min_len = min(len(s) for s in all_s)
            avg_s = [mean([s[i] for s in all_s if i < len(s)]) for i in range(min_len)]
            plt.plot(avg_s, color='green', linewidth=2, label='Average')
        plt.title(f'Structure Trajectories - {title}')
        plt.ylabel('Structure Size')
        plt.xlabel('Cycle')
        plt.legend()

        plt.tight_layout()
        plt.show()
    except ImportError:
        print("Matplotlib not available. Cannot plot overlay.")
