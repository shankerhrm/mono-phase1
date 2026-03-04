"""
INVARIANT:
SpeciesMemory MUST NOT influence runtime behavior.
It may only affect initialization via scalar defaults at reproduction.

Violation of this invariant is a design error, not a bug.
"""

mutation_rate = 0.01  # Global for stress tests
import random
import dataclasses

from mono import MonoCell

def divide(parent, species_defaults=None, generation=None, species_memory=None, env_params=None, panic_state=None):
    if species_defaults is not None and not isinstance(species_defaults, dict):
        raise TypeError("species_defaults must be a dict of scalar defaults (not a SpeciesMemory object)")
    observer = None
    if isinstance(species_defaults, dict) and '__observer__' in species_defaults:
        observer = species_defaults.get('__observer__')
        species_defaults = {k: v for k, v in species_defaults.items() if k != '__observer__'}
    
    # Phase-11: Yolk Strategy
    if env_params is not None:
        E_yolk = 50 * env_params.get('basal_burn', 0.0)
        if parent.energy.E <= (parent.id.E_repro + E_yolk):
            return None  # Reproduction aborted due to insufficient energy
        # Deduct reproduction cost + yolk
        parent.energy.E -= (parent.id.C_divide + E_yolk)
        child_initial_energy = E_yolk
    else:
        # Phase-10 behavior: no yolk
        parent.energy.E -= parent.id.C_divide
        child_initial_energy = 0.0  # Or handle as before, but for Phase-11, env_params should be provided
    
    # Structure compression before split (placeholder, no compress method yet)
    # parent.structure.compress()  # TODO: implement if needed
    
    # Calculate split
    E_remaining = parent.energy.E
    S_total = parent.structure.size()
    r = parent.id.r
    
    E_p = (1 - r) * E_remaining
    E_c = r * E_remaining
    S_p = int((1 - r) * S_total)
    S_c = int(r * S_total)
    
    # Update parent
    parent.energy.E = E_p
    parent.structure._size = S_p
    
    # Create child
    child = MonoCell(parent.id)
    child.energy.E = child_initial_energy  # Phase-11: yolk endowment
    child.structure._size = S_c

    # Phase-16: Mutate evolvable stress phenotypes
    child.id = dataclasses.replace(parent.id, 
        alpha=max(0.01, min(1.0, parent.id.alpha + random.gauss(0, mutation_rate))),
        beta=max(0.01, min(1.0, parent.id.beta + random.gauss(0, mutation_rate)))
    )
    
    # Cost of Mutation: high mutation_rate penalizes offspring energy
    if parent.id.mutation_rate > 0.10:
        child.energy.E *= 0.8
    
    # Inheritance and lineage
    child.parent_id = parent.cell_id
    child.lineage_id = parent.lineage_id if hasattr(parent, 'lineage_id') else str(parent.cell_id)
    child.generation = parent.generation + 1
    child.birth_cycle = parent.cycle_count + 1
    child.reproduction_eligible = False
    child.birth_stress_remaining = parent.id.birth_stress_cycles
    
    # Inherit and mutate regulator params (Phase-5)
    child.regulator_params = parent.regulator_params.copy()
    for key in child.regulator_params:
        child.regulator_params[key] += random.gauss(0, parent.id.regulator_mutation_rate)
        child.regulator_params[key] = max(0.01, min(1.0, child.regulator_params[key]))
        
    # Phase-7/9: Inherit Cognitive Phenotypes (spawn/init bias only)
    # NOTE: Do not pass SpeciesMemory objects into lifecycle; only pass scalar defaults.
    if species_defaults:
        child.module_count = int(species_defaults.get('module_count', parent.module_count))
        child.gating_threshold = float(species_defaults.get('gamma', parent.gating_threshold))
    else:
        child.module_count = parent.module_count
        child.gating_threshold = parent.gating_threshold

    child.prediction_horizon = parent.prediction_horizon
    child.scene_threshold = parent.scene_threshold
    child.arbitration_frequency = parent.arbitration_frequency

    if observer is not None:
        try:
            observer.record_reproduction(
                parent=parent,
                child=child,
                generation=generation,
                species_memory=species_memory,
                species_defaults_applied=species_defaults,
                yolk_size=E_yolk if env_params else 0.0,
            )
        except Exception:
            pass
    
    # Phase-7/12: Mutate Cognitive Phenotypes (Continuous)
    # Phase-12: Apply panic mutation multiplier if in ALERT/PANIC state
    mutation_multiplier = 1.0
    if panic_state and isinstance(panic_state, dict):
        mutation_multiplier = min(panic_state.get('mutation_multiplier', 1.0), 3.0)
    
    cog_mut_rate = parent.id.cog_mutation_rate * mutation_multiplier
    struct_mut_rate = parent.id.structural_mutation_rate * mutation_multiplier
    
    child.prediction_horizon = max(0.0, child.prediction_horizon + random.gauss(0, cog_mut_rate * 2))
    child.scene_threshold = max(0.01, child.scene_threshold + random.gauss(0, cog_mut_rate))
    child.gating_threshold = max(0.0, child.gating_threshold + random.gauss(0, cog_mut_rate))
    
    # Arbitration frequency mutates discretely
    if random.random() < cog_mut_rate:
        child.arbitration_frequency = max(1, child.arbitration_frequency + random.choice([-1, 1]))
        
    # Phase-7: Mutate Cognitive Architecture (Structural)
    if random.random() < struct_mut_rate:
        child.module_count = max(0, child.module_count + random.choice([-1, 1]))
    
    # Reset tracking state for child
    child.predictive_modules = [
        {'horizon': child.prediction_horizon, 'error': 0.0, 'weight': 1.0 / max(1, child.module_count)}
        for _ in range(child.module_count)
    ]

    # Phase-13: Inherit temporal oscillator (omega + phase offset) from parent.
    # omega mutates per PhaseOscillator.make_child_oscillator().
    # Species Memory Ms has no omega field — temporal structure is cell-level only.
    if hasattr(parent, 'oscillator'):
        child.oscillator = parent.oscillator.make_child_oscillator()

    return child
