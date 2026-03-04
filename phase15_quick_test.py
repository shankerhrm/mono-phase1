"""
Phase-15 Quick Sanity Test
Single-seed validation of physiological load controller.
Fast run (~1–2 minutes).
Tests tunable FP via slow load accumulation/decay.
"""

import random
import statistics
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mono import MonoCell
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from phase10.observer import Phase10Observer
from phase12.stress_index import CompositeStressIndex
from phase15.panic_controller import PhysiologicalController
from phase13.run_phase13 import create_identity_for_env, run_generation, backfill_population


def quick_test():
    seed = 1
    total_gens = 200
    period = 80
    target_pop = 80
    basal_burn = 1.0

    random.seed(seed)

    observer = Phase10Observer(seed=seed, env='phase15_quick')
    sm = SpeciesMemory(alpha=0.1, epsilon=0.1)
    si = CompositeStressIndex()

    # Phase-15 controller params
    pc = PhysiologicalController(
        alpha=0.1,
        beta=0.5,
        activation_level=0.4,
        psi_baseline=0.3
    )

    pop = [MonoCell(create_identity_for_env('A')) for _ in range(target_pop)]

    panic_states = []
    intensities = []
    loads = []
    summer_panic = 0
    summer_total = 0

    for gen in range(total_gens):
        env_type = 'B' if (gen % period) / period >= 0.5 else 'A'
        observer.set_generation(gen)

        # Compute structural integrity for repair capacity
        structural_integrity = statistics.mean([c.structure.size() for c in pop]) if pop else 10.0

        panic_out = pc.get_outputs(si.psi)

        pop, stats = run_generation(
            pop, sm, gen, observer, env_type, panic_state=panic_out, basal_burn=basal_burn
        )

        if len(pop) == 0:
            print("EXTINCTION")
            break

        psi = si.update(
            avg_energy=stats['avg_energy'],
            basal_burn=stats['basal_burn'],
            repro_attempts=stats['repro_attempts'],
            repro_successes=stats['repro_successes'],
            deaths=stats['deaths'],
            population_size=stats['population_size'],
            gamma_variance=stats['gamma_variance']
        )

        # Now update with correct avg_energy
        panic_out = pc.update(psi, avg_energy=stats['avg_energy'], structural_integrity=structural_integrity)

        panic_states.append(panic_out['state'])
        intensities.append(panic_out['intensity'])
        loads.append(panic_out['load'])

        if env_type == 'A':
            summer_total += 1
            if panic_out['state'] != "CALM":
                summer_panic += 1

        pop = backfill_population(pop, target_pop, env_type)

    fp_rate = summer_panic / max(1, summer_total)

    print("\n=== Phase-15 Quick Test Results ===")
    print(f"Final load: {loads[-1]:.3f}")
    print(f"Mean load: {statistics.mean(loads):.3f}")
    print(f"Max load: {max(loads):.3f}")
    print(f"Summer FP rate: {fp_rate:.2%}")
    print(f"Panic generations: {sum(1 for s in panic_states if s != 'CALM')}")
    print("====================================\n")


if __name__ == "__main__":
    quick_test()
