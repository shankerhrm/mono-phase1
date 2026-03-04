# MONO Phase-11 Specification
## Initialization-Inheritance Bias Architecture (IIBA)

### 1. Purpose & Scope

Phase-11 extends the Initialization-Only Bias Architecture (IOBA, Phase-9) into a richer inheritance model. Where IOBA allows Species Memory to bias offspring via scalar defaults, Phase-11 introduces:

1. **IIBA Hybrid Inheritance**: Offspring initialization is a weighted blend of Species Memory and parental phenotype.
2. **Yolk Strategy**: Energy endowment at birth scales with environmental hostility.
3. **Vacuum Ecology**: A harsh scarcity regime designed to stress-test all preceding invariants.

Phase-11 introduces no new runtime control paths. All modifications operate exclusively at reproduction/initialization boundaries.

### 2. Architecture: IIBA Hybrid Inheritance

#### 2.1 Inheritance Function

$$\Gamma_{child} = 0.7 \cdot M_s(\gamma) + 0.3 \cdot \Gamma_{parent}$$

Where:
- $M_s(\gamma)$ is the Species Memory gating threshold prior
- $\Gamma_{parent}$ is the parent's current gating threshold
- The 70/30 split ensures population-level memory dominates while preserving parental signal

#### 2.2 Lineage Isolation Rule

> **Invariant**: Child inherits biases, not memory. Species Memory is initialized from $M_s$, not from the parent's runtime state.

This rule prevents:
- Direct parental policy transfer (forbidden by Phase-9 constraints)
- Lineage-specific memory channels (would violate IOBA)
- Parent-child coupling beyond scalar bias initialization

#### 2.3 IOBA Preservation

IIBA is a strict extension of IOBA:

$$\frac{\partial\,\theta_{runtime}}{\partial\,M_s} = 0 \quad \text{(unchanged)}$$

The only change is the source of $\theta_{init}$:

| Phase | Init Source |
|-------|-----------|
| Phase-9 (IOBA) | $\theta_{init} \leftarrow M_s$ |
| Phase-11 (IIBA) | $\theta_{init} \leftarrow 0.7 \cdot M_s + 0.3 \cdot \theta_{parent}$ |

Runtime isolation remains absolute.

### 3. Yolk Strategy

#### 3.1 Motivation

In hostile environments with high basal burn, offspring face immediate energy crisis at birth. The Yolk Strategy provides survival runway proportional to environmental metabolic cost.

#### 3.2 Yolk Computation

$$E_{yolk} = 50 \cdot \beta_{env}$$

Where $\beta_{env}$ is the environment's basal burn rate.

#### 3.3 Reproduction Gate

Reproduction requires the parent to fund both division cost and yolk:

$$E_{parent} > E_{repro} + E_{yolk}$$

If insufficient:
- Reproduction is **aborted** (returns `None`)
- Parent retains all energy
- No partial reproduction or deferred spawning

#### 3.4 Child Energy Initialization

$$E_{child,0} = E_{yolk}$$

The child begins life with the yolk endowment, not a fraction of the parent's energy. This replaces the split-ratio energy transfer for environments where `env_params` is provided.

### 4. Vacuum Ecology (Environment B)

#### 4.1 Parameters

| Parameter | Env A (Forgiving) | Env B (Vacuum) |
|-----------|-------------------|----------------|
| $E_i$ (energy intake) | 30.0 | 0.1 |
| $\beta$ (basal burn) | 0.0 | 2.0 |
| $\alpha_O$ (failure latency) | 2000.0 | 0.5 |
| $k_{coord}$ | 0.5 | 0.001 |
| Initial energy | 50.0 | 150.0 |
| $E_{repro}$ | 60 | 100 |
| Mutation rate | 0.105 | 0.20 |

#### 4.2 Ecological Characteristics

Environment B is a **metabolic vacuum**:
- Energy intake is negligible ($E_i = 0.1$)
- Basal burn is aggressive ($\beta = 2.0$)
- Failure latency is extremely tight ($\alpha_O = 0.5$)
- Coordination cost is near-zero ($k_{coord} = 0.001$)

This creates conditions where:
- Most organisms die within 5–10 cycles
- Reproduction is rare and expensive ($E_{repro} = 100$, yolk = $50 \times 2.0 = 100$)
- Only organisms with low metabolic overhead and fast reflexes survive

#### 4.3 Entropy Floor

In Environment B, mutation rate is elevated to 0.20 (vs 0.105 baseline). This prevents:
- Premature convergence under strong selection
- Diversity collapse from bottleneck effects
- Population lock into a single suboptimal phenotype

### 5. Experimental Results (Regime Flip A→B)

#### 5.1 Setup

- Seed: 42
- Generations A: 500 (forgiving regime)
- Generations B: 250 (vacuum stress)
- Target population: 50
- Species Memory α: 0.1

#### 5.2 Observed Phenomena

**Hysteresis Lock (Confirmed)**:
- $M_s(\gamma)$ remains at 0.500–0.501 throughout 250 generations of vacuum
- Species Memory cannot adapt because α = 0.1 is insufficient to overcome the EMA inertia when survivor statistics are noisy

**Survival Crisis**:
- Survival rate drops to 0.2–0.6 in Environment B
- Sustained crisis without recovery — organisms die faster than memory can adapt

**Cognition Spike**:
- 67–71% cognitive invocation rate during crisis (vs ~30% in calm)
- Validates Phase-7.1: cognition activates under survival pressure

**No Beneficial Mutation Fixation**:
- Offspring gamma remains at 0.500 via IIBA inheritance
- Lock prevents exploration of lower gamma values that might improve survival

#### 5.3 Hysteresis Lock Diagnosis

The lock arises from:
1. **Slow α**: EMA with α=0.1 requires ~50 consistent samples to shift meaningfully
2. **Noisy survivors**: Under vacuum, survivor gamma values are stochastic, not directional
3. **IIBA amplification**: 70% weight on locked $M_s$ dominates the 30% parental signal
4. **No feedback mechanism**: Nothing in Phases 1–11 can detect and respond to the lock

> This is the direct motivation for Phase-12 (Panic Architecture).

### 6. Implementation Summary

| Component | File | Change |
|-----------|------|--------|
| IIBA Inheritance | `phase10/observer.py` | `offspring_gamma = 0.7 * Ms.gamma + 0.3 * parent.gamma` |
| Yolk Strategy | `reproduction/spawn.py` | `E_yolk = 50 * basal_burn`; reproduction gate; child energy init |
| Vacuum Ecology | `experiments/run_regime_flip.py` | Environment B parameters; elevated mutation rate |
| Lineage Tracking | `mono.py` | `lineage_id` field for IIBA lineage monitoring |

### 7. Invariants Preserved

All Phase-10 invariants remain valid:

- **Runtime Isolation**: $I(B_t; M_s) = 0$ — IIBA modifies only $\theta_{init}$
- **IOBA**: $\partial\theta_{runtime}/\partial M_s = 0$ — runtime behavior independent of $M_s$
- **No-Free-Cognition**: Cognition cost structure unchanged
- **Measurement Purity**: Phase-10 observers unmodified

### 8. Transition to Phase-12

Phase-11 reveals a fundamental limitation: **Hysteresis Lock**.

Under vacuum stress:
- Species Memory cannot adapt fast enough
- IIBA inheritance amplifies the lock
- No mechanism exists to detect or respond to systemic failure

Phase-12 introduces the **Panic Architecture**:
- ∇E (energy gradient) as a leading indicator of environmental hostility
- Composite Stress Index (Ψ) for multi-signal threat assessment
- State-dependent modulation of evolvability (mutation amplitude, memory flexibility)
- Controlled hysteresis breaking without catastrophic forgetting

Phase-12 transforms MONO from passive evolutionary drift to **cybernetic self-regulation**.
