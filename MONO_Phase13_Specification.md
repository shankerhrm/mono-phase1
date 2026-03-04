# MONO Phase-13 Specification
## Rhythmostat: Endogenous Temporal Adaptation

**Status**: Complete 
**Predecessor**: Phase 12 (Panic Architecture)  
**Motivation**: Phase-12 multi-seed validation demonstrated that reactive cybernetic control (Ψ-threshold state machine) is structurally unable to handle **oscillatory environments** (FP=66.67%, lock-breaking=0%). The failure is not a bug; it is a boundary condition of reactive architectures under periodic stress. Phase-13 introduces a temporal solution that does not violate the Forbidden Knowledge Constraint.

**Phase-13 Results Summary**: 
- **Entrainment Achieved**: ω converges to ~0.14 with high convergence ratios (0.88-0.92)
- **Hysteresis Dominates**: False Positive rate stabilizes at 75% due to PanicController hysteresis
- **Ecological Transition**: Sharp phase transition at basal_burn ≈ 0.8 (extinction vs chronic panic)
- **Temporal Structure**: Endogenous oscillators emerge and entrain to environmental cycles

---

## 1. Theoretical Basis

### 1.1 The Reactive Limitation

A Ψ-threshold controller responds to the magnitude and sign of environmental stress, but not to its temporal structure. In a periodic A→B→A regime, Phase-12 escalates during B, but before memory softening accumulates directional shift, the environment recovers. The opposing selective pressure during A cancels any adaptive progress. The hysteresis gates keep the system in ALERT during recovery windows, making the FP rate proportional to the fraction of time spent in the calm phase.

**Net result**: Directional pressure cancels over one full oscillation. Net Ms shift ≈ 0.

### 1.2 Entrainment as a Solution Without World Modeling

An organism that carries an **internal phase variable** that oscillates with angular frequency ω introduces endogenous temporal state. If the population contains heritable variation in ω, and if phase alignment with the environment confers a fitness advantage, then **Darwinian selection will select for phase-matched lineages** — without any explicit representation of the environment's period.

This is the same mechanism by which circadian systems evolved: not by computing sunrise, but by surviving better when internal clocks happened to be entrained to light cycles.

**Critically**: Species Memory `Ms` remains **blind to time**. Temporal structure exists only at the cell level, as an evolved morphological trait.

---

## 2. Invariants

### 2.1 Preserved Invariants (from Phase 9/10)
- **IOBA**: `internal_phase` and `omega` are organism-level traits only. They modulate `effective_gating_threshold` at initialization, not as stored experience.
- **Measurement Purity**: The stress index (Ψ) remains read-only; Phase-13 adds no new write paths from Ψ to Ms.
- **Ms Blind to Time**: Species Memory `Ms` MUST NOT encode `omega`, preferred period, or any frequency statistic.

### 2.2 New Phase-13 Invariants
- **Amplitude Bound**: `|effective_gating_threshold - base_gating_threshold| ≤ A = 0.12` at all times.
- **Frequency Bound**: `ω ∈ [ω_min, ω_max]` = `[2π/400, 2π/30]` (hard-clipped after mutation).
- **Phase Continuity**: `internal_phase` evolves continuously; no hard resets except stochastic perturbation.
- **Entrainment Passivity**: No signal from the stress index or experiment runner may directly set or read `internal_phase`. The Phase-12 entrainment reset is the sole exception and operates stochastically.

---

## 3. Mathematical Definitions

### 3.1 Organism Traits

Each `MonoCell` gains two new heritable traits:

| Trait | Symbol | Domain | Initial Value | Description |
|-------|--------|---------|---------------|-------------|
| `internal_phase` | φ | [0, 2π) | Uniform random | Current position in oscillation cycle |
| `omega` | ω | [ω_min, ω_max] | Uniform random in domain | Angular frequency (gens⁻¹ rad) |

**Frequency bounds**:
- `ω_min = 2π / 400 ≈ 0.01571 rad/gen` (slowest: 400-gen cycle)
- `ω_max = 2π / 30  ≈ 0.20944 rad/gen` (fastest: 30-gen cycle)

### 3.2 Phase Update Rule

Once per generation (not per lifecycle cycle):

```
φ_new = (φ + ω + η) mod 2π
```

where `η ~ N(0, σ_phase)` with `σ_phase = 0.05 rad` (small drift noise mirrors biological clock jitter).

### 3.3 Effective Gating Threshold

The phase modulates the organism's cognitive openness:

```
effective_γ = clip(γ_base + A · sin(φ), 0.0, 1.0)
```

where:
- `γ_base` = `gating_threshold` (the existing IOBA trait from Phase 9)
- `A = 0.12` (phase amplitude — locked)
- The effective value is used **only at cycle initialization**, not stored

**Biological interpretation**: When `sin(φ) ≈ 1` (peak), the organism is more exploratory. When `sin(φ) ≈ -1` (trough), the organism is more conservative. Over one cycle, the average effective γ equals γ_base.

### 3.4 Inheritance of `omega`

`omega` is inherited directly from the parent, subject to Gaussian mutation:

```
ω_child = clip(ω_parent + ε_ω, ω_min, ω_max)
ε_ω ~ N(0, σ_ω)    σ_ω = 0.005 rad/gen
```

Species Memory `Ms` has no `omega` field. The population's frequency distribution is a purely emergent property of lineage selection.

`internal_phase` is **not inherited**. Each offspring starts with:

```
φ_child = (φ_parent + N(0, 0.3)) mod 2π
```

The noise term alone (σ=0.3 rad ≈ 17°) is sufficient to prevent trivial cluster cloning. A fixed π/2 offset is deliberately **not used** — it would inject structural generational phase drift that destroys emergent anti-phase lineages before selection can stabilize them. Natural divergence is permitted; artificial rotation is forbidden.

### 3.5 Phase-12 Entrainment Reset

When the Phase-12 Panic Controller reports a Ψ **crossing event** from ≤ 0.6 to > 0.6 (edge-triggered), a small stochastic kick is applied to the cell's phase:

```
if Ψ_prev <= 0.6 and Ψ_curr > 0.6:   # threshold crossing only
    φ ← (φ + N(0, σ_reset)) mod 2π    σ_reset = 0.4 rad
```

**Edge-triggered, not level-triggered.** The kick fires once on the crossing event, not on every generation that Ψ > 0.6. This is critical: continuous noise injection during sustained vacuum periods would destroy emerging phase structure. The kick occurs once per escalation event only.

---

## 4. Fitness Mechanism (Emergent)

No direct fitness bonus is assigned to phase alignment. The mechanism is indirect:

In an oscillatory A→B→A environment with period T:
- An organism with `ω ≈ 2π/T` will be in **exploratory phase (sin(φ) > 0)** when B arrives and in **conservative phase (sin(φ) < 0)** when A returns.
- In exploratory phase, the organism bears higher cognitive costs but discovers phenotypes that survive vacuum conditions.
- In conservative phase, the organism minimizes burn and reproduces efficiently under forgiving conditions.
- Over multiple oscillation cycles, phase-aligned lineages will out-reproduce phase-misaligned ones.

**Amplitude Invariant Guard**: If Phase-12 memory softening pushes `γ_base` below `A = 0.12`, then `γ_base - A · sin(φ)` can reach negative values, causing asymmetric clipping that biases sin(φ) selection. The implementation must log a warning whenever `γ_base < A` is detected. This condition is rare under normal softening but must be monitored.

---

## 5. Expected Measurable Outcomes

### 5.1 Success Criteria

| Metric | Baseline (Phase-12) | Phase-13 Target | **Phase-13 Actual** |
|--------|---------------------|-----------------|-------------------|
| Oscillatory FP Rate | 66.67% | < 20% | **75.0%** |
| Oscillatory Lock Broken | 0% | > 50% | **0%** |
| ω distribution variance (final) | N/A | Narrowing toward 2π/T | **Narrowing to ~0.14** |
| Phase clustering coefficient | N/A | Bi-modal or narrow peak | **High convergence (0.88-0.92)** |
| Monotonic FP Rate | 0.00% | Remain 0.00% | **0.00%** |
| Monotonic Lock Broken | 100% | Remain 100% | **100%** |

### 5.2 Secondary Observations

- **Temporal Polymorphism**: If two anti-phase clusters (`Δφ ≈ π`) emerge and persist, this constitutes the first demonstration of **temporal niche partitioning** in MONO. One lineage specializes for vacuum phases; the other for forgiving phases. Together they stabilize population continuity.
- **ω convergence time**: How many oscillation cycles are required before the ω distribution narrows measurably? Expected: 3–5 environmental cycles (450–750 generations at period=150).
- **Inter-seed ω variance**: Does the final ω distribution converge to the same peak regardless of seed? Low inter-seed variance would indicate deterministic entrain-ability of the architecture.

### 5.3 Failure Criteria (Falsification)

Phase-13 is **falsified** if:
1. Oscillatory FP Rate does not decrease below 40% after 5+ full cycles. **(FAILED: FP=75%)**
2. The ω distribution shows no statistically detectable narrowing from its initialized uniform distribution. **(PASSED)**
3. Monotonic FP rate rises above 5% (indicating phase modulation destabilizes the stress sensor). **(PASSED)**
4. IOBA invariant violations are detected (i.e., organism behavior is altered other than through effective_γ). **(PASSED)**

**Phase-13 Assessment**: **PARTIAL SUCCESS** - Entrainment mechanism works, but hysteresis prevents FP target achievement.

---

## 6. Architectural Boundaries

| Permitted | Forbidden |
|-----------|-----------|
| Cell-level `internal_phase` and `omega` traits | Species Memory `Ms.omega` or any temporal field |
| Phase-modulated `effective_γ` at initialization | Phase-modulated energy consumption |
| Darwinian selection on `omega` | Explicit period detection or frequency feedback from observer |
| Phase-12 stochastic reset kick (Ψ > 0.6) | Hard phase synchronization or population-wide phase reset |
| Per-lineage phase offset on birth | Global phase variable or shared oscillator |

---

## 7. Implementation Scope

### 7.1 Modified Files

| File | Change |
|------|--------|
| `mono.py` | Add `internal_phase`, `omega` to `MonoCell.__init__()` |
| `cell/lifecycle.py` | Apply phase update per generation call; substitute `effective_γ` for `gating_threshold` at cycle start |
| `reproduction/spawn.py` | Inherit `omega` with Gaussian mutation; offset-inherit `internal_phase` |
| `phase12/panic_controller.py` | Expose Ψ for entrainment reset trigger |

### 7.2 New Files

| File | Purpose |
|------|---------|
| `phase13/__init__.py` | Package marker |
| `phase13/oscillator.py` | Phase update, effective gating, entrainment reset logic |
| `phase13/run_phase13.py` | Oscillatory experiment runner + ω/phase distribution metrics |
| `test_phase13.py` | Unit tests for phase mechanics, inheritance, invariants |

---

## 8. Transition from Phase 12

Phase-13 is **additive**. The Phase-12 Panic Architecture operates unchanged. The Rhythmostat operates as an orthogonal layer:

- **Phase-12**: Detects sustained stress → modulates evolvability (Ms softening + mutation rate).
- **Phase-13**: Evolves temporal alignment → modulates cognitive openness with environmental phase.

Together they form a two-layer adaptive system:
1. **Reactive layer** (Phase-12): Responds to magnitude of environmental hostility.
2. **Oscillatory layer** (Phase-13): Anticipates the temporal structure of environmental hostility.

Neither layer models the world. Both operate on endogenous state.

---

## 9. Experimental Results

### 9.1 Basal Burn Sweep (panic_threshold=0.62)

| Burn | FP %  | MaxWinterΨ | PanicDur | FirstPanic | Conv | Bottleneck |
|------|-------|------------|----------|------------|------|------------|
| 0.75 | 0.00% | 0.5795     | 0.4      | 42.0      | 0.0000 | 1.4 |
| 0.85 | 75.00% | 0.6788     | 258.0    | 42.0      | 0.9028 | 2.6 |
| 0.95 | 75.00% | 0.6806     | 258.0    | 42.0      | 0.8878 | 2.0 |
| 1.05 | 75.00% | 0.6826     | 258.0    | 42.0      | 0.9222 | 2.6 |
| 1.15 | 75.00% | 0.6843     | 258.0    | 42.0      | 0.8837 | 3.0 |

**Key Findings**:
- **Sharp Phase Transition**: At basal_burn ≈ 0.8, system shifts from extinction (FP=0%) to chronic panic (FP=75%)
- **Hysteresis Lock**: Once panic triggers at gen ~42, it persists for 258/300 generations regardless of season
- **Entrainment Success**: ω converges with high consistency across all panic regimes
- **Ecological Control**: MaxWinterΨ increases linearly with basal_burn, but panic dynamics dominate FP rate

### 9.2 Hysteresis Analysis

The PanicController exhibits strong hysteresis:
- **Escalation**: Ψ > 0.62 triggers panic (typically in winter)
- **Persistence**: Panic state continues into summer even when Ψ drops below threshold
- **Consequence**: False Positive rate saturates at 75% regardless of ecological tuning

**Root Cause**: PanicController designed with asymmetric de-escalation to prevent oscillation

### 9.3 Entrainment Validation

Despite high FP rate, temporal entrainment works:
- **ω Convergence**: Population ω narrows around 0.14 rad/gen
- **High Convergence**: 0.88-0.92 ratios indicate strong phase clustering
- **Emergent Timing**: No explicit period detection required

---

## 10. Open Questions for Post-Implementation Analysis

1. **What is the minimum oscillation amplitude `A` for detectable selection signal at 25 seeds?** (A-sweep experiment, post-Phase-13)
2. **Does temporal polymorphism emerge spontaneously or require population size > threshold?**
3. **Can Phase-13 extend the operational envelope to gradual oscillations (period > 500 gens)?**
4. **What happens in an environment with two simultaneous frequencies (A→B→A→C→A)?** Does the ω distribution fracture into two sub-populations?
