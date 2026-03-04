# MONO Phase-12 Specification
## Panic Architecture — State-Dependent Evolvability Modulation

### 1. Purpose & Scope

Phase-12 introduces the **Panic Architecture**: a second-order control system that modulates MONO's evolvability based on detected systemic fragility.

Phase-11 revealed the **Hysteresis Lock** — Species Memory cannot adapt under sudden environmental hostility because:
- EMA learning rate (α) is too slow for regime shifts
- IIBA inheritance amplifies the locked prior
- No mechanism detects or responds to population-level energy crisis

Phase-12 solves this by adding:
1. **∇E** — Energy gradient as a pre-mortality leading indicator
2. **Ψ** — Composite Stress Index combining four signals
3. **Panic Controller** — Three-state machine with hysteresis and dwell times
4. **Memory Softening** — Controlled prior loosening (not erasure)
5. **Mutation Amplification** — Bounded hypermutation under panic

Phase-12 introduces **no new organism-level capabilities**. All modulation occurs at the population level (Species Memory, mutation rates). Runtime isolation (IOBA) remains absolute.

### 2. Leading Indicator: Energy Gradient (∇E)

#### 2.1 Definition

$$\nabla E = \frac{\Delta E_{avg}}{\beta_{basal}}$$

Where:
- $\Delta E_{avg}$ = change in population-average energy between generations
- $\beta_{basal}$ = environment's basal burn rate (normalizer)

When $\beta_{basal} = 0$ (forgiving environment), $\nabla E = \Delta E_{avg}$ directly.

#### 2.2 Why ∇E is Architecturally Superior

∇E is:
- **Pre-mortality**: Energy imbalance precedes death
- **Pre-sterility**: Energy deficit precedes reproductive failure
- **Pre-extinction**: Energy collapse precedes population collapse
- **Mechanistic**: Thermodynamic, not demographic

It detects environmental hostility *relative to metabolic demand*, not raw energy decline.

#### 2.3 Smoothing

∇E is computed as an Exponential Moving Average with λ = 0.2:

$$\nabla E_{smooth}(t) = (1 - \lambda) \cdot \nabla E_{smooth}(t-1) + \lambda \cdot \nabla E_{raw}(t)$$

Additionally, a **3-generation persistence check** is applied:
- ∇E is considered "confirmed negative" only if it has been negative for 3 consecutive generations
- This prevents single stochastic bad generations from triggering ALERT

#### 2.4 Second Derivative

The second derivative $\nabla^2 E$ is tracked to distinguish:
- **Persistent decline** ($\nabla^2 E < 0$): accelerating crisis → increase urgency
- **Decelerating decline** ($\nabla^2 E > 0$): possible stabilization → reduce urgency

### 3. Composite Stress Index (Ψ)

$$\Psi = w_1 \cdot \hat{\nabla E} + w_2 \cdot \hat{\Phi} + w_3 \cdot \hat{m} + w_4 \cdot \hat{V}$$

Where:
- $\hat{\nabla E}$ = normalized energy gradient (0 = healthy, 1 = extreme deficit)
- $\hat{\Phi}$ = reproductive failure rate (failed reproductions / attempts)
- $\hat{m}$ = mortality rate (deaths / population)
- $\hat{V} = -\frac{dVar(\Gamma)}{dt}$ = rate of variance collapse (positive = collapsing)

#### 3.1 Weights

| Component | Weight | Rationale |
|-----------|--------|-----------|
| $w_1$ (∇E) | 0.55 | Causal, earliest, thermodynamic |
| $w_2$ (Φ) | 0.20 | Confirmation signal — functional failure |
| $w_3$ (mortality) | 0.10 | Lagging indicator — history, not physics |
| $w_4$ (-dVar/dt) | 0.15 | Structural brittleness — hysteresis lock detector |

#### 3.2 Normalization

Each component is normalized to [0, 1] using sigmoid saturation:

$$\hat{x} = \frac{2}{1 + e^{-k \cdot x}} - 1$$

With component-specific sensitivity $k$.

#### 3.3 Ψ Range

$\Psi \in [0, 1]$ after normalization. Values:
- $\Psi < 0.15$: Healthy — no intervention needed
- $0.15 \leq \Psi < 0.30$: Mild stress — monitoring
- $0.30 \leq \Psi < 0.60$: ALERT — moderate intervention
- $\Psi \geq 0.60$: PANIC — maximum intervention

### 4. Panic Controller (State Machine)

#### 4.1 States

```
CALM ──[Ψ > 0.3 for 3 gens]──► ALERT ──[Ψ > 0.6 for 3 gens]──► PANIC
  ▲                                │                                  │
  │                                │                                  │
  └──[Ψ < 0.15 for 3 gens]────────┘                                  │
  └──[Ψ < 0.40 + 5 gen dwell]────────────────────────────────────────┘
```

#### 4.2 Transition Rules

| From | To | Condition |
|------|----|-----------|
| CALM | ALERT | Ψ > 0.3 for 3 consecutive generations |
| ALERT | PANIC | Ψ > 0.6 for 3 consecutive generations |
| PANIC | ALERT | Ψ < 0.4 AND min 5 generations in PANIC |
| ALERT | CALM | Ψ < 0.15 for 3 consecutive generations |

#### 4.3 Minimum Dwell Times

- **PANIC**: 5 generations minimum before exit
- **CALM re-entry**: 3 generations of Ψ < 0.15 required before returning from ALERT

This prevents oscillatory cycling under borderline Ψ.

#### 4.4 Outputs

| State | mutation_multiplier | memory_softening_ε |
|-------|--------------------|--------------------|
| CALM | 1.0 | 0.0 |
| ALERT | 1.0 + 1.0 × Ψ | ε_max × Ψ² |
| PANIC | 2.0 + 1.0 × Ψ | ε_max × Ψ² |

Where $\epsilon_{max} = 0.5$.

### 5. Memory Softening

#### 5.1 Update Rule

When panic controller provides ε > 0, after the normal EMA update:

$$M_s^{new} = (1 - \epsilon) \cdot M_s + \epsilon \cdot M_{current}$$

Where $M_{current}$ is the current generation's survivor-conditioned statistics.

#### 5.2 Quadratic Scaling

$$\epsilon = \epsilon_{max} \cdot \Psi^2$$

This gives:
- Mild stress (Ψ = 0.3): ε = 0.5 × 0.09 = 0.045 (very mild)
- Moderate stress (Ψ = 0.6): ε = 0.5 × 0.36 = 0.18 (moderate)
- Extreme stress (Ψ = 0.9): ε = 0.5 × 0.81 = 0.405 (strong but bounded)

#### 5.3 Invariant Preservation

Memory softening operates on $M_s$ only — a population-level prior.
It does not:
- Modify runtime behavior
- Inject energy or structure
- Override organism failure
- Change gating thresholds mid-lifecycle

$$\frac{\partial\,\text{Behavior}}{\partial\,\text{Phase12}} = 0 \quad \text{(at runtime)}$$

### 6. Mutation Amplification

#### 6.1 Mechanism

During reproduction, when `panic_state.mutation_multiplier > 1.0`:

$$\sigma_{mut}^{panic} = \sigma_{mut}^{base} \times \min(\text{multiplier}, 3.0)$$

Applied to:
- `cog_mutation_rate` (continuous cognitive traits)
- `structural_mutation_rate` (module add/remove probability)

#### 6.2 Ceiling

Hard ceiling at 3× baseline. Above this:
- Trait space randomization occurs
- Local gradient information is destroyed
- Accumulated adaptations are wasted

The 3× ceiling preserves directed exploration while increasing variance.

### 7. Falsification Criteria

Phase-12 is successful if and only if:

| # | Criterion | Measurement |
|---|-----------|-------------|
| 1 | Recovery latency decreases | Ms.gamma shifts within 50 gens of vacuum (vs 250+ baseline) |
| 2 | Hysteresis lock is broken | Ms.gamma deviates >0.05 from initial 0.500 under vacuum |
| 3 | Adaptation before collapse | Survival rate stabilizes before reaching 0 |
| 4 | No mutational meltdown | In stable regime (Phase A), mutation amplification stays at 1× |
| 5 | False positive rate < 5% | Zero or near-zero panic activations during 500 gens of Environment A |
| 6 | Controlled exit | System returns to CALM after adaptation succeeds in new environment |

If panic only increases noise and death, Phase-12 has built chaos, not regulation.

### 8. What Phase-12 Is (and Is Not)

**Phase-12 IS**:
- State-dependent modulation of evolvability
- Meta-Darwinian: regulates *how strongly* the system adapts
- A controlled phase transition mechanism
- Bounded evolvability amplification

**Phase-12 IS NOT**:
- Anti-Darwinian: organisms still compete and die
- Goal-directed: no utility function, no optimization target
- Intelligent: no learning, no world models, no policies
- Runtime modification: IOBA invariant remains absolute

### 9. Architectural Position

```
Phase 1-6:  Organism-level mechanics (metabolism, structure, cognition)
Phase 7:    Cognitive evolution (heritable cognitive phenotypes)
Phase 8:    Ecological competition (spatial, temporal)
Phase 9:    Population memory (Species Memory, IOBA)
Phase 10:   Invariance verification (measurement-only)
Phase 11:   Inheritance architecture (IIBA, yolk, vacuum)
Phase 12:   Evolvability regulation (panic, stress index, softening)
            ↑
            This is the first cybernetic layer.
```

If Phase-12 works, MONO crosses from passive evolution into regulated adaptability.

### 10. Implementation Boundary

Phase-12 code is contained in the `phase12/` module:
- `stress_index.py` — ∇E, Φ, Ψ computation
- `panic_controller.py` — State machine
- `run_phase12.py` — Experiment runner

Modifications to existing code are minimal:
- `species_memory.py` — `soften()` method added
- `reproduction/spawn.py` — Optional `panic_state` parameter
- `cell/lifecycle.py` — Pass-through of `panic_state`
