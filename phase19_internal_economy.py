"""
Phase-17: Minimal Cultural Layer Evolution Experiment

Tests if cultural knowledge persists across deaths and benefits descendants.
Tracks: learning_rate evolution, artifact usage, energy gains.
"""

import json
import os
import random
import statistics
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.identity import CoreIdentity
from mono import MonoCell, cultural_pool
from cell.lifecycle import cycle
from species_memory import SpeciesMemory
from phase10.observer import Phase10Observer
from phase13.run_phase13 import run_generation

import reproduction.spawn as spawn

# Global environmental quality for niche construction
environmental_quality = 1.0
ENV_MIN = 0.1  # Floor to prevent total collapse
ENV_MAX = 2.0
depletion_rate = 0.005  # Reduced for balance
regeneration_rate = 0.2  # Increased

# Phase-20: Market prices
price_food = 1.0
price_repair = 1.0

def create_identity_for_phase19():
    base = {
        'E_i': 30.0, 'E_m': 200, 'E_s': 5, 'E_r': 1000,
        'c_B': 1, 'c_M': 2, 'c_R': 1, 'c_K': 3, 'c_P': 1,
        'burn_weights': (0.5, 0.3, 0.2), 'mutation_rate': 0.105,
        'initial_energy': 80.0, 'basal_burn': 0.3, 'action_cost_multiplier': 1,
        'initial_structure_size': 20, 'decay_rate': 0.02, 'split_ratio': 0.5,  # Phase-24: larger structure + slower decay
        'E_quiescence': 5, 'S_quiescence': 5, 'S_critical': 8,
        'E_maintenance_min': 10, 'repair_efficiency': 0.8,
        'E_repro': 25.0, 'S_repro': 1.0, 'r': 0.3, 'C_divide': 5,  # Phase-24: r=0.3 for viable offspring
        'epsilon_E': 0.5, 'epsilon_S': 0.5, 'stability_window': 5,
        'child_survival_cycles': 5, 'birth_stress_cycles': 2,
        'regulator_alpha': 0.1, 'regulator_beta': 0.05, 'regulator_gamma': 0.2,  # Phase 24: lowered to allow repair detection
        'regulator_mutation_rate': 0.01, 'alpha_O': 100.0, 'tau_max': 100.0,
        'k_coord': 1.0, 'tau_sense': 0.5, 'tau_signal': 0.5, 'tau_act': 1.0,
        'latency_drift_rate': 0.01, 'size_penalty_factor': 0.1,
        'prediction_horizon': 2.0, 'number_of_predictive_modules': 2,
        'arbitration_delay': 1.0, 'module_horizon_adapt_rate': 0.1,
        'global_integrator_capacity': 10.0, 'arbitration_mechanism': 'temporal_sequencing',
        'scene_change_threshold': 0.5, 'scene_min_duration': 5,
        'kappa_pred': 0.0, 'cog_mutation_rate': 0.05, 'structural_mutation_rate': 0.01,
        'base_gating_threshold': 0.5, 'base_arbitration_frequency': 1,
        'strategy_trait': random.choice([0, 1]),  # 0 = extractor, 1 = restorer
        # Phase-17/18
        'learning_rate': random.uniform(0.05, 0.25),
        'teaching_efficiency': random.uniform(0.05, 0.25),
        # Phase-18
        'p_restore': random.uniform(0.05, 0.95),  # Phase-25: widened from [0.3,0.7] for evolutionary specialization
        # Phase-19
        'trade_propensity': random.uniform(0.0, 1.0),
        # Phase-21: Environmental sensing
        'environment_sensitivity': random.uniform(0, 1)
    }
    return CoreIdentity(**base)


def safe_mean(x):
    return statistics.mean(x) if x else 0.0


def safe_stdev(x):
    return statistics.stdev(x) if len(x) > 1 else 0.0


def run_generation_phase19(cells, species_memory, generation, observer, depletion_rate, regeneration_rate, env_exponent, restore_mult, trade_cost, exchange_rate, target, fixed_env=False, max_pop=1000):
    organism_data, surviving_cells, children = [], [], []
    deaths, repro_attempts, repro_successes, energy_sum = 0, 0, 0, 0.0
    env_params = {'E_i': 30.0, 'basal_burn': 0.3, 'alpha_O': 100.0, 'environmental_quality': environmental_quality, 'fixed_env': fixed_env, 'max_pop': max_pop}

    # Phase-18: Teaching and Learning Phase with Two Artifacts
    learning_cost = 3.0
    teaching_cost = 1.0
    cultural_mutation_rate = 0.15  # Balanced for stability
    cultural_mutation_size = 0.2  # Increased for stronger innovation
    improvement_bias = 0.85  # Slightly reduced for stability

    total_extraction = 0.0
    total_restoration = 0.0
    artifact_min = 0.5
    artifact_max = 3.0

    # Phase-22: Resource competition
    resource_per_agent = environmental_quality / max(len(cells), 1)

    naive_cells = [cell for cell in cells if cell.artifact_x is None or cell.artifact_r is None]
    teachers = [cell for cell in cells if cell.artifact_x is not None and cell.artifact_r is not None and cell.energy.E > teaching_cost]
    taught = set()
    reproducer_artifacts = []

    teaching_events = 0
    self_learning_events = 0

    for learner in naive_cells:
        if teachers:
            teacher = random.choice(teachers)
            if random.random() < teacher.teaching_efficiency:
                teacher.energy.E -= teaching_cost
                learner.energy.E -= learning_cost * 0.5
                teaching_events += 1
                taught.add(learner)

                # Choose artifact to teach randomly
                artifact_type = random.choice(['x', 'r'])
                if artifact_type == 'x':
                    # Mutate extraction artifact
                    if random.random() < cultural_mutation_rate:
                        if random.random() < improvement_bias:
                            delta = random.uniform(0, cultural_mutation_size)
                        else:
                            delta = random.uniform(-cultural_mutation_size, 0)
                        new_val = teacher.artifact_x + delta
                        new_val = max(artifact_min, min(artifact_max, new_val))
                    else:
                        new_val = teacher.artifact_x
                    learner.artifact_x = new_val
                    learner.artifact_r = teacher.artifact_r  # copy unchanged
                else:
                    # Mutate restoration artifact
                    if random.random() < cultural_mutation_rate:
                        if random.random() < improvement_bias:
                            delta = random.uniform(0, cultural_mutation_size)
                        else:
                            delta = random.uniform(-cultural_mutation_size, 0)
                        new_val = teacher.artifact_r + delta
                        new_val = max(artifact_min, min(artifact_max, new_val))
                    else:
                        new_val = teacher.artifact_r
                    learner.artifact_r = new_val
                    learner.artifact_x = teacher.artifact_x  # copy unchanged

    # Self-learning for untaught naive
    for learner in naive_cells:
        if learner not in taught:
            # Learn extraction if not known
            if learner.energy.E > 18.0 and random.random() < 0.1:
                learner.energy.E -= learning_cost
                learner.artifact_x = 1.0
                self_learning_events += 1
            # Learn restoration if not known
            if learner.artifact_r is None and random.random() < learner.learning_rate:
                learner.energy.E -= learning_cost
                learner.artifact_r = 1.0
                self_learning_events += 1

    # Phase-20: Action Phase - Extraction or Restoration with learned preferences
    extractors = []
    restorers = []
    for cell in cells:
        if cell.artifact_x is not None and cell.artifact_r is not None:
            # Phase-21: Adaptive environmental sensing with strategy bias
            base_p_restore = 0.5 + 0.5 * cell.id.strategy_trait  # 0.5 for extractor, 1.0 for restorer
            p_restore_effective = base_p_restore + cell.environment_sensitivity * (1 - environmental_quality)
            p_restore_effective = max(0, min(1, p_restore_effective))
            
            if random.random() < p_restore_effective:
                restorers.append(cell)
                # Phase-26: Damaged environment reduces ALL energy, creating selection pressure
                env_factor = max(0.3, environmental_quality)  # Poor env = less energy for everyone
                energy_gain = env_params['E_i'] * restore_mult * cell.artifact_r * cell.restoration_bonus * env_factor
                cell.repair += energy_gain
                cell.restoration_bonus += 0.05
                total_restoration += energy_gain
                # Update learning
                cell.avg_restore_gain = 0.9 * cell.avg_restore_gain + 0.1 * energy_gain
                total_restoration += energy_gain
            else:
                extractors.append(cell)
                energy_gain = env_params['E_i'] * cell.artifact_x * environmental_quality * cell.extraction_bonus
                cell.food += energy_gain
                cell.extraction_bonus += 0.05
                # Update learning
                cell.avg_extract_gain = 0.9 * cell.avg_extract_gain + 0.1 * energy_gain
                total_extraction += energy_gain

    # Bonus decay
    for cell in cells:
        cell.extraction_bonus = max(1.0, cell.extraction_bonus * 0.99)
        cell.restoration_bonus = max(1.0, cell.restoration_bonus * 0.99)

    # Phase-20: Market trade
    global price_food, price_repair
    target_food = target
    target_repair = target
    total_sold_food = 0
    total_bought_repair = 0
    trade_events = 0
    
    for cell in cells:
        import math
        trade_prob = 1 / (1 + math.exp(-cell.avg_trade_gain))
        if random.random() < trade_prob:
            # Sell food if surplus
            if cell.food > target_food:
                surplus = cell.food - target_food
                energy_gain = surplus * price_food
                cell.energy.E += energy_gain
                cell.food = target_food
                total_sold_food += surplus
                trade_events += 1
                cell.avg_trade_gain = 0.9 * cell.avg_trade_gain + 0.1 * energy_gain
            
            # Buy repair if deficit and have energy
            if cell.repair < target_repair and cell.energy.E > 0:
                deficit = target_repair - cell.repair
                energy_cost = deficit * price_repair
                if energy_cost <= cell.energy.E:
                    cell.energy.E -= energy_cost
                    cell.repair = target_repair
                    total_bought_repair += deficit
                    trade_events += 1
                    cell.avg_trade_gain = 0.9 * cell.avg_trade_gain - 0.1 * energy_cost
    
    # Update prices
    if total_sold_food > 0:
        excess_food_supply = total_sold_food - total_bought_repair  # approximation
        price_food *= (1 + 0.1 * excess_food_supply / total_sold_food)
        price_food = max(0.5, min(5.0, price_food))
    if total_bought_repair > 0:
        excess_repair_supply = total_bought_repair - total_sold_food  # approximation
        price_repair *= (1 + 0.1 * excess_repair_supply / total_bought_repair)
        price_repair = max(0.5, min(5.0, price_repair))

    # Add resource contribution to energy with better conversion
    for cell in cells:
        # Convert repair energy to usable energy
        if cell.repair > 20:
            conversion = cell.repair * 0.3
            cell.energy.E += conversion
            cell.repair *= 0.7
        # Add food energy
        cell.energy.E += cell.food * 0.5

    death_reasons = {}
    total_burn = 0.0
    total_intake = 0.0

    # Phase-27: Basal metabolism — every cell pays survival cost each generation
    # This is the Second Law of Thermodynamics: life must burn energy to exist
    BASAL_METABOLISM = 2.0
    for cell in cells:
        cell.energy.E -= BASAL_METABOLISM
    
    # Phase 24.5: Check if we are over population cap
    max_pop = env_params.get('max_pop', 1000)
    over_cap = len(cells) >= max_pop

    for cell in cells:
        death_reason, child = None, None
        # Run one cycle
        death_reason, log, cycle_child = cycle(
            cell, observer=observer, generation=generation,
            species_memory=species_memory, env_params=env_params,
            organism_data_list=organism_data, panic_state={"state": "CALM", "load": 0.0},
            resource_intake=env_params['E_i']
        )
        if over_cap:
            cycle_child = None  # Suppress reproduction if over cap
        if cycle_child: 
            child = cycle_child
        
        # Phase-27: Age-based death — forces generational turnover
        MAX_AGE = 200
        if not death_reason and cell.cycle_count > MAX_AGE:
            death_reason = "SENESCENCE"
        
        if death_reason: 
            deaths += 1
            death_reasons[death_reason] = death_reasons.get(death_reason, 0) + 1
            # Add final burn for deaths
            if log:
                total_burn += log.get('burn', 0)
                total_intake += log.get('intake', 0)
        else:
            surviving_cells.append(cell)
            energy_sum += cell.energy.E
            if log:
                total_burn += log.get('burn', 0)
                total_intake += log.get('intake', 0)
            if cycle_child:
                repro_successes += 1
                children.append(cycle_child)
                reproducer_artifacts.append((cell.artifact_x, cell.artifact_r))

    # Merge survivors and children
    new_pop = surviving_cells + children

    # Cultural decay
    decay_factor = 0.99995
    for cell in new_pop:
        if cell.artifact_x is not None:
            cell.artifact_x *= decay_factor
            cell.artifact_x = max(artifact_min, cell.artifact_x)
        if cell.artifact_r is not None:
            cell.artifact_r *= decay_factor
            cell.artifact_r = max(artifact_min, cell.artifact_r)

    # Cultural mutation on all artifacts
    for cell in new_pop:
        if cell.artifact_x is not None:
            if random.random() < cultural_mutation_rate:
                if random.random() < improvement_bias:
                    cell.artifact_x += random.uniform(0, cultural_mutation_size)
                else:
                    cell.artifact_x -= random.uniform(0, cultural_mutation_size)
                cell.artifact_x = max(artifact_min, min(artifact_max, cell.artifact_x))
        if cell.artifact_r is not None:
            if random.random() < cultural_mutation_rate:
                if random.random() < improvement_bias:
                    cell.artifact_r += random.uniform(0, cultural_mutation_size)
                else:
                    cell.artifact_r -= random.uniform(0, cultural_mutation_size)
                cell.artifact_r = max(artifact_min, min(artifact_max, cell.artifact_r))

    avg_energy = energy_sum / len(surviving_cells) if surviving_cells else 0

    stats = {
        'avg_energy': safe_mean([cell.energy.E for cell in cells]),
        'repro_attempts': repro_attempts,
        'repro_successes': repro_successes,
        'deaths': deaths,
        'teaching_events': teaching_events,
        'self_learning_events': self_learning_events,
        'reproducer_artifacts': reproducer_artifacts,
        'extractors': extractors,
        'restorers': restorers,
        'total_extraction': total_extraction,
        'total_restoration': total_restoration,
        'total_burn': total_burn,
        'total_intake': total_intake,
        'proportion_restoring': len(restorers) / len(cells) if cells else 0,
        'trade_events': trade_events,
        'death_reasons': death_reasons
    }

    print(f"Gen {generation}: Total extraction: {total_extraction}, total restoration: {total_restoration}", file=sys.stderr)

    return new_pop, stats


def run_evolution(seed, total_gens=500, target_pop=100, dep_rate=0.15, reg_rate=0.005, env_exponent=2.0, restore_mult=0.2, trade_cost=1.0, exchange_rate=1.0, target=10, fixed_env=False, max_pop=1000, shock_start=None, shock_end=None, shock_dep_mult=1.0, include_metrics=False):
    global depletion_rate, regeneration_rate, environmental_quality, price_food, price_repair
    depletion_rate = dep_rate
    regeneration_rate = reg_rate
    environmental_quality = 1.0  # Phase-23: Reset env state for each run
    price_food = 1.0
    price_repair = 1.0
    random.seed(seed)

    observer = Phase10Observer(seed=seed, env='phase18_cultural')
    sm = SpeciesMemory(alpha=0.1, epsilon=0.1)

    pop = [MonoCell(create_identity_for_phase19())
           for _ in range(target_pop)]
    
    # Phase-24: Stagger initial ages to prevent synchronized reproduction
    for i, cell in enumerate(pop):
        cell.cycle_count = random.randint(0, 7)  # Random maturity ages
        cell.last_reproduction_gen = cell.cycle_count - random.randint(3, 6)  # Varied cooldown

    metrics_per_gen = []

    for gen in range(total_gens):
        observer.set_generation(gen)
        
        # Phase-25: Environmental shock injection (instant or gradual ramp)
        if shock_start is not None and shock_end is not None:
            if gen == shock_start:
                if shock_end > total_gens:
                    # Gradual ramp mode: linearly increase over ramp_duration
                    ramp_duration = 800  # gens to reach full shift
                    progress = min(1.0, (gen - shock_start) / ramp_duration)
                    depletion_rate = dep_rate + (dep_rate * shock_dep_mult - dep_rate) * progress
                    print(f"⚡ RAMP START at gen {gen}: depletion_rate = {depletion_rate:.4f}", file=sys.stderr)
                else:
                    depletion_rate = dep_rate * shock_dep_mult
                    print(f"⚡ SHOCK at gen {gen}: depletion_rate = {depletion_rate:.4f}", file=sys.stderr)
            elif shock_end > total_gens and shock_start < gen:
                # Gradual ramp: update depletion each gen
                ramp_duration = 800
                progress = min(1.0, (gen - shock_start) / ramp_duration)
                depletion_rate = dep_rate + (dep_rate * shock_dep_mult - dep_rate) * progress
            elif gen == shock_end:
                depletion_rate = dep_rate
                print(f"🌱 RECOVERY at gen {gen}: depletion_rate = {depletion_rate:.4f}", file=sys.stderr)

        # Run generation
        pop, stats = run_generation_phase19(
            pop, sm, gen, observer, depletion_rate, regeneration_rate, env_exponent, restore_mult, trade_cost, exchange_rate, target, fixed_env=fixed_env, max_pop=max_pop
        )
        
        # But we need it in run_generation for env_params? 
        # Actually it's simpler if we just force it in the loop here if fixed_env is set.
        if fixed_env:
            environmental_quality = 1.0

        extractors = stats['extractors']
        restorers = stats['restorers']

        if not pop:
            print(f"EXTINCTION at gen {gen} for seed {seed}", file=sys.stderr)
            break

        # Collect Phase-19 metrics
        learning_rates = [cell.learning_rate for cell in pop]
        teaching_efficiencies = [cell.teaching_efficiency for cell in pop]
        artifact_x_values = [cell.artifact_x for cell in pop if cell.artifact_x is not None]
        artifact_r_values = [cell.artifact_r for cell in pop if cell.artifact_r is not None]
        p_restore_values = [cell.p_restore for cell in pop]
        food_values = [cell.food for cell in pop]
        repair_values = [cell.repair for cell in pop]
        energy_values = [cell.energy.E for cell in pop]
        
        # Phase-25: Genetic composition tracking for evolutionary analysis
        strategy_traits = [cell.id.strategy_trait for cell in pop]
        env_sensitivities = [cell.environment_sensitivity for cell in pop]
        
        # Lifecycle tracking
        ages = [cell.cycle_count for cell in pop]
        avg_age = safe_mean(ages)
        max_age = max(ages) if ages else 0
        min_age = min(ages) if ages else 0
        total_energy = sum(energy_values)
        learned_count = sum(1 for cell in pop if cell.artifact_x is not None and cell.artifact_r is not None)
        avg_energy = stats['avg_energy']
        
        # Track reproduction reasons
        repro_reasons = {}
        for cell in pop:
            if hasattr(cell, 'repro_debug') and cell.repro_debug:
                reason = cell.repro_debug[-1]
                repro_reasons[reason] = repro_reasons.get(reason, 0) + 1

        mean_artifact_x = safe_mean(artifact_x_values)
        mean_artifact_r = safe_mean(artifact_r_values)
        mean_p_restore = safe_mean(p_restore_values)
        p_restore_variance = safe_stdev(p_restore_values)
        mean_food = safe_mean(food_values)
        mean_repair = safe_mean(repair_values)
        
        # Phase-25: Evolutionary metrics
        mean_strategy_trait = safe_mean(strategy_traits)
        var_strategy_trait = safe_stdev(strategy_traits)
        mean_env_sensitivity = safe_mean(env_sensitivities)
        var_env_sensitivity = safe_stdev(env_sensitivities)
        
        # Phase-25: Lineage diversity (unique parent lineages)
        lineage_ids = set()
        for cell in pop:
            lineage_ids.add(getattr(cell.id, 'lineage_id', id(cell)))
        lineage_diversity = len(lineage_ids)

        # Phase-23/24: Smooth environmental dynamics that scale stably with population
        n_pop = len(pop)
        
        # Per-cell base depletion is much smaller to allow larger populations
        base_depletion = depletion_rate * n_pop * 0.005 
        extraction_depletion = depletion_rate * sum(max(0, ind.artifact_x - 1.0) for ind in extractors) * 0.01
        depletion = base_depletion + extraction_depletion
        
        # Restoration linearly adds to environment, no wild 1/env scaling
        regeneration = regeneration_rate * sum(ind.artifact_r for ind in restorers) * 0.05
        
        # Logistic recovery: env recovers toward K when below, decays when above
        K = 1.0
        r_base = 0.1  # 10% recovery rate per generation toward K
        logistic = r_base * environmental_quality * (1.0 - environmental_quality / K)
        
        environmental_quality += logistic + regeneration - depletion
        if fixed_env:
            environmental_quality = 1.0
        else:
            environmental_quality = max(ENV_MIN, min(ENV_MAX, environmental_quality))
        # Phase-23: No bailout — carrying capacity via env-coupled reproduction

        metrics_per_gen.append({
            'gen': gen,
            'population': len(pop),
            'avg_learning_rate': safe_mean(learning_rates),
            'avg_teaching_efficiency': safe_mean(teaching_efficiencies),
            'mean_artifact_x': mean_artifact_x,
            'mean_artifact_r': mean_artifact_r,
            'mean_p_restore': mean_p_restore,
            'p_restore_variance': p_restore_variance,
            'mean_food': mean_food,
            'mean_repair': mean_repair,
            'learned_percent': (learned_count / len(pop)) * 100 if pop else 0,
            'avg_energy': avg_energy,
            'avg_burn': stats['total_burn'] / len(pop) if pop else 0,
            'avg_intake': stats['total_intake'] / len(pop) if pop else 0,
            'teaching_events': stats['teaching_events'],
            'self_learning_events': stats['self_learning_events'],
            'reproducer_artifacts': stats['reproducer_artifacts'],
            'environmental_quality': environmental_quality,
            'proportion_restoring': stats['proportion_restoring'],
            'trade_events': stats['trade_events'],
            'total_energy': total_energy,
            'total_extraction': stats['total_extraction'],
            'total_restoration': stats['total_restoration'],
            'avg_age': avg_age,
            'max_age': max_age,
            'min_age': min_age,
            'reproduction_attempts': stats['repro_attempts'],
            'successful_reproductions': stats['repro_successes'],
            'deaths': stats['deaths'],
            'death_reasons': stats.get('death_reasons', {}),
            'reproduction_reasons': repro_reasons,
            'total_restoration': stats['total_restoration'],
            # Phase-25: Evolutionary metrics
            'mean_strategy_trait': mean_strategy_trait,
            'var_strategy_trait': var_strategy_trait,
            'mean_env_sensitivity': mean_env_sensitivity,
            'var_env_sensitivity': var_env_sensitivity,
            'lineage_diversity': lineage_diversity,
        })

    all_reproducer_artifacts = [a for m in metrics_per_gen for a in m['reproducer_artifacts']]

    # Phase 24.5: Calculate aggregate summary for quick audit
    total_audit_intake = sum(m['avg_intake'] * m['population'] for m in metrics_per_gen)
    total_audit_burn = sum(m['avg_burn'] * m['population'] for m in metrics_per_gen)
    total_audit_repro = sum(m['successful_reproductions'] for m in metrics_per_gen)

    summary = {
        'seed': seed,
        'total_gens': total_gens,
        'final_gen': len(metrics_per_gen) - 1,
        'final_population': len(pop) if pop else 0,
        'survived': len(metrics_per_gen) == total_gens and len(pop) > 0,
        'extinction_gen': len(metrics_per_gen) - 1 if len(metrics_per_gen) < total_gens else None,
        'peak_population': max(m['population'] for m in metrics_per_gen) if metrics_per_gen else 0,
        'min_environmental_quality': min(m['environmental_quality'] for m in metrics_per_gen) if metrics_per_gen else 0,
        'total_audit_intake': total_audit_intake,
        'total_audit_burn': total_audit_burn,
        'total_audit_repro': total_audit_repro,
        'total_restoration_last_10': sum(m['total_restoration'] for m in metrics_per_gen[-10:]) if len(metrics_per_gen) >= 10 else 0,
        'total_extraction_last_10': sum(m['total_extraction'] for m in metrics_per_gen[-10:]) if len(metrics_per_gen) >= 10 else 0,
        'final_mean_artifact_x': metrics_per_gen[-1]['mean_artifact_x'] if metrics_per_gen else 0,
        'final_mean_artifact_r': metrics_per_gen[-1]['mean_artifact_r'] if metrics_per_gen else 0,
        'final_environmental_quality': metrics_per_gen[-1]['environmental_quality'] if metrics_per_gen else 0,
        'final_avg_energy': metrics_per_gen[-1]['avg_energy'] if metrics_per_gen else 0,
        'final_proportion_restoring': metrics_per_gen[-1]['proportion_restoring'] if metrics_per_gen else 0,
        # 'metrics_per_gen': metrics_per_gen  # Phase 24.5: Exclude massive list in large runs to avoid slowdown
    }
    
    # Include full metrics for short runs or when explicitly requested (e.g. shock test)
    if total_gens <= 200 or include_metrics:
        summary['metrics_per_gen'] = metrics_per_gen


    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Phase-19 Internal Economy Simulation')
    print("\n=== Phase-20: Individual Learning + Market Trade Results ===", file=sys.stderr)
    parser.add_argument('--restore_mult', type=float, default=0.2, help='Restoration energy multiplier')
    parser.add_argument('--target', type=int, default=10, help='Target resource level for trade')
    parser.add_argument('--trade_cost', type=float, default=1.0, help='Energy cost per trade')
    parser.add_argument('--exchange_rate', type=float, default=1.0, help='Food per repair in trade')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--total_gens', type=int, default=500, help='Total generations')
    parser.add_argument('--depletion_rate', type=float, default=0.15, help='Environmental depletion rate')
    parser.add_argument('--regeneration_rate', type=float, default=0.005, help='Environmental regeneration rate')
    parser.add_argument('--env_exponent', type=float, default=2.0, help='Environmental exponent for density dependence')
    parser.add_argument('--fixed_env', action='store_true', help='Force environment to 1.0 every generation')
    parser.add_argument('--max_pop', type=int, default=1000, help='Maximum population limit')
    # Phase-25: Shock test parameters
    parser.add_argument('--shock_start', type=int, default=None, help='Generation to start environmental shock')
    parser.add_argument('--shock_end', type=int, default=None, help='Generation to end environmental shock')
    parser.add_argument('--shock_dep_mult', type=float, default=1.0, help='Depletion rate multiplier during shock')
    parser.add_argument('--include_metrics', action='store_true', help='Force include per-gen metrics in output')
    args = parser.parse_args()

    result = run_evolution(
        seed=args.seed,
        restore_mult=args.restore_mult,
        trade_cost=args.trade_cost,
        exchange_rate=args.exchange_rate,
        target=args.target,
        dep_rate=args.depletion_rate,
        reg_rate=args.regeneration_rate,
        env_exponent=args.env_exponent,
        total_gens=args.total_gens,
        fixed_env=args.fixed_env,
        max_pop=args.max_pop,
        shock_start=args.shock_start,
        shock_end=args.shock_end,
        shock_dep_mult=args.shock_dep_mult,
        include_metrics=args.include_metrics,
    )

    # Output result as JSON for sweep collection
    print(json.dumps(result, indent=2))
