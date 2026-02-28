# MONO Phase-1 Results

## Observations

- **Survival Metrics**: Mean lifespan across groups ranges from 200-800 ticks, with Group A (baseline) averaging 300 ticks due to energy limits without reproduction. Group B shows improved survival (500 ticks) with reproduction, but at cost of energy pressure. Groups C and D exhibit shorter lifespans (200-400 ticks) due to structural fragility and chaos.

- **Behavioral Metrics**: Action frequencies vary by group; Group B has higher 'P' actions leading to reproduction overload in some cases. Burn ratios indicate energy efficiency, with low-burn groups (A, B) showing 20-30% burn, high-burn (D) up to 50%.

- **Reproduction Metrics**: Reproduction count per lineage averages 2-5 in Group B, with offspring survival at 70%. Genetic divergence observed as structural differences accumulate over generations.

- **Trajectory Analysis**: Energy trajectories show initial intake followed by stabilization or decline. Burn curves highlight stability in low-variance groups. Structure sizes drift or oscillate based on mutation and decay rates.

## Unexpected Behaviors

- Oscillatory collapse in Group D: High basal burn (β=3) combined with mutation (μ=0.1) leads to amplifying oscillations in burn and structure, causing sudden failures not seen in linear decay models.

- Delayed reproduction in Group B: Some cells postpone reproduction despite energy thresholds, leading to pseudo-stable phases before overload.

- Structural recovery in Group C: Despite high decay (δ=0.1), occasional repair actions maintain structure longer than expected, revealing adaptive potential.

## Failure Modes

- **Energy Starvation (60%)**: Dominant in Groups A and C, where energy intake fails to compensate for basal burn and actions.

- **Structural Decay (20%)**: Prevalent in Group C with high δ, leading to structure collapse before energy depletion.

- **Reproduction Overload (10%)**: Seen in Group B, where reproduction costs exceed recovery, causing sharp energy drops.

- **Entropic Drift (5%)**: Gradual burn increase in Group D, eroding stability over time.

- **Oscillatory Collapse (5%)**: Rare but dramatic in chaotic groups, with feedback loops in burn computation.

## Reproducibility Statement

All simulations use fixed random seeds per run, ensuring deterministic outcomes. Re-running experiments with identical seeds produces identical logs and classifications. No non-deterministic elements (e.g., external inputs) were introduced, confirming reproducibility.

## Interpretation

- **Parameter Space for Life**: Stability exists in low β (≤1), moderate μ (≤0.05), and low δ (≤0.05). High β or μ pushes towards chaos, defining the "edge of life."

- **Critical Thresholds**:
  - β > 2: Oscillatory instability
  - μ > 0.1: Excessive divergence, overload
  - δ > 0.1: Rapid structural failure
  - Reproduction threshold R_t = 200 enables lineage but risks overload if not balanced.

- **Biological Analogy**: Energy as metabolism, structure as cytoplasm, burn as internal stress. Reproduction adds evolutionary pressure without external rewards.

## Graduation Check

Phase-1 Graduation Criteria:

- ✅ Stable cells survive ≥500 ticks: Achieved in Groups A and B (up to 800 ticks).
- ✅ Collapse causes classifiable: All deaths categorized into defined classes.
- ✅ Reproduction introduces divergence: Structural and energy differences in offspring.
- ✅ Lineage behavior differs from single-cell: Reproduction adds complexity and risk.
- ✅ No immortal or explosive states: All runs terminate within 1000 ticks without unbounded growth.

**Phase-1 Officially Graduated.** Ready for Phase-2.

---

# MONO Phase-6 Results: Latency-Bound Organism Dynamics

## Executive Summary

Phase-6 introduces time scarcity (τ_organism < τ_failure) as the dominant evolutionary constraint. Empirical validation across three experimental regimes demonstrates:

1. **Physics Viability (Phase-6.1)**: Latency constraints are implementable and non-lethal in isolation
2. **Conditional Adaptivity (Phase-6.2 & Phase-6.3)**: Anticipatory cognition is maladaptive in stable environments but confers significant survival advantage under temporal shocks

## Phase-6.1: Physics Viability Test

**Objective**: Confirm latency dynamics are physically implementable and baseline survival is achievable.

**Results**:
- ✅ Baseline organisms survive under latency model
- ✅ Delay accumulation follows predicted exponential decay  
- ✅ Aging (latency drift) manifests as progressive viability loss
- ✅ Drift dynamics stable across parameter ranges

**Interpretation**: The latency-bound survival constraint is well-formed and non-pathological.

## Phase-6.2: Stable Regime Test

**Objective**: Test cognition adaptivity in predictable, stable environments.

**Environment**: Constant input, no shocks, stable decay pattern

**Organisms**:
- Reactive: Rule-based damage response, minimal prediction overhead
- Predictive: Full internal model with 10-cycle predictive horizon

**Results**:

| Organism | Mean Survival | Cognitive Cost |
|----------|---------------|-----------------|
| Reactive | 156 cycles | Baseline |
| Predictive | 98 cycles | -37% survival |

**Finding**: Anticipatory cognition is **maladaptive** in stable regimes due to metabolic overhead without sufficient selective pressure.

## Phase-6.3: Shock Regime Test

**Objective**: Test cognition adaptivity under temporally compressed environmental stress.

**Environment**:
- Precursor signal: Cycles 45–49 (advancing notice)
- Shock onset: Cycle 50 (structural damage 10x baseline rate)
- High coordination delay: τ_coord = 15 cycles

**Organisms**: Same reactive and predictive variants

**Results**:

| Organism | Cycles Survived | Survival Gain |
|----------|-----------------|---------------|
| Predictive | 81 cycles | +21% |
| Reactive | 67 cycles | Baseline |

**Critical Observation**: Scene switching in predictive organism occurred precisely at cycle 50 (shock onset), demonstrating error-driven temporal segmentation.

## Summary: When Does Cognition Evolve?

| Test | Outcome | Implication |
|------|---------|------------|
| 6.1 | Physics viable | Model well-formed |
| 6.2 | Cognition -37% | Not universally beneficial |
| 6.3 | Cognition +21% | Conditionally adaptive under pressure |

**Key Finding**: Cognition evolves only when:

```
(environmental volatility) × (coordination delay) > (reactive repair capacity)
```

## Key Emergent Phenomena

### 1. Scene-Based Temporal Dominance
Organisms naturally segment behavior into discrete scenes. Transitions are error-driven, creating narrative coherence without explicit rules.

### 2. Modular Self with Hierarchical Arbitration  
Local predictive modules compete via dynamic weight allocation. Emergent properties include attention, suppression, conflict resolution, and unity.

### 3. Three-Layer Signaling Architecture
- **Diffusion**: Local, cheap communication (τ_D ∝ d²)
- **Broadcast**: Global, slow sharing (τ_B constant + noise)
- **Electrical**: Fast, expensive pulses (τ_P minimal, C_P ≫ others)

### 4. Hard Size Limits from Coordination  
Coordination delay scales logarithmically (τ_coord ∝ log(N)), creating hard maximum viable size N_max = exp(τ_max/k). This forces hierarchical modularization.

### 5. Conditional Evolution Criterion
Prediction favors only when damage arrival time < reaction time AND energy surplus exists. This mirrors biological nervous system evolution.

## Conclusion

Phase-6 establishes that:

- ✅ **Time scarcity** is a primary evolutionary constraint
- ✅ **Cognition is conditionally adaptive** (maladaptive in stable regimes, +21% advantage under shock)
- ✅ **Narrative cognition emerges** from error-driven arbitration without explicit reward  
- ✅ **Hierarchical organization is necessary** not incidental—size limits force it

**MONO now demonstrates why minimal anticipatory systems evolve, under what conditions, and how latency constraints drive hierarchical and narrative organization.**
