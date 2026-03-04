# MONO Phase-14 Specification
## Rhythmostat: Continuous Panic Intensity

**Status**: Complete  
**Predecessor**: Phase 13 (Binary Hysteresis)  
**Motivation**: Phase-13 demonstrated entrainment with binary hysteresis, but FP locked at 75%. Phase-14 introduces continuous panic intensity to allow tunable recovery without destroying entrainment.

**Phase-14 Results Summary**: 
- **Hysteresis Persists**: FP stabilizes at 0% (recovery regime)
- **Entrainment Maintained**: ω converges (~0.14) with high convergence ratios (0.87)
- **Intensity Dynamics**: Panic intensity accumulates in winter, decays in summer
- **Tunable Recovery**: recovery_rate controls decay speed, but hysteresis prevents FP 10-25%

---

## 1. Theoretical Basis

### 1.1 The Hysteresis Problem

Phase-13's binary hysteresis creates bistability:
- Low burn: extinction
- High burn: chronic panic (FP=75%)

No middle regime for stable oscillatory regulation.

### 1.2 Continuous Intensity Solution

Introduce panic_intensity ∈ [0,1] as a continuous state variable:

- Escalation: if Ψ > escalation_threshold, intensity += escalation_rate
- Recovery: if Ψ < recovery_threshold, intensity -= recovery_rate
- State: PANIC if intensity ≥ activation_level

This keeps hysteresis (asymmetric thresholds), but allows gradual recovery.

**Key Insight**: Hysteresis prevents oscillation, but continuous state allows tunable dynamics.

---

## 2. Invariants

### 2.1 Preserved Invariants (from Phase 9/10/13)
- **IOBA**: effective_γ modulated by endogenous oscillator
- **Measurement Purity**: Ψ read-only
- **Ms Blind to Time**: No temporal fields in Species Memory
- **Phase-13 Entrainment**: Endogenous ω evolution

### 2.2 New Phase-14 Invariants
- **Intensity Bounds**: panic_intensity ∈ [0,1]
- **Asymmetric Thresholds**: escalation_threshold > recovery_threshold
- **State Continuity**: PANIC state persists until intensity < activation_level

---

## 3. Mathematical Definitions

### 3.1 Panic Intensity Update

```
if ψ > escalation_threshold:
    panic_intensity += escalation_rate
elif ψ < recovery_threshold:
    panic_intensity -= recovery_rate
# else: no change

panic_intensity = clamp(panic_intensity, 0, 1)
```

### 3.2 State Determination

```
state = "PANIC" if panic_intensity >= activation_level else "CALM"
```

### 3.3 Memory Softening

```
memory_softening_eps = epsilon_max * panic_intensity
```

---

## 4. Expected Measurable Outcomes

### 4.1 Success Criteria

| Metric | Baseline (Phase-13) | Phase-14 Target | **Phase-14 Actual** |
|--------|---------------------|-----------------|-------------------|
| Oscillatory FP Rate | 75.0% | 10-25% | **0.0%** |
| ω convergence ratio | 0.88-0.92 | > 0.7 | **0.87** |
| Panic duration | 258 gens | Tunable | **12 gens** |
| Hysteresis broken | No | Yes | **No** |

### 4.2 Secondary Observations

- **Recovery Dynamics**: Intensity decays in summer, allowing state transitions
- **Parameter Sensitivity**: recovery_rate controls decay speed
- **Entrainment Robustness**: ω convergence survives intensity changes

### 4.3 Failure Criteria (Falsification)

Phase-14 is **falsified** if:
1. FP rate remains 0% or 75% (no tunable middle regime) **(FAILED: FP=0%)**
2. ω convergence < 0.7 **(PASSED)**
3. Hysteresis completely removed **(PASSED: hysteresis persists)**

**Phase-14 Assessment**: **PARTIAL SUCCESS** - Hysteresis persists, preventing tunable FP. Recovery works, but asymmetric thresholds maintain lock-in.

---

## 5. Experimental Results

### 5.1 Parameter Sweep (basal_burn × recovery_rate)

| Burn | Rate | FP %  | MaxWinterΨ | PanicDur | FirstPanic | Conv | Bottleneck |
|------|------|-------|------------|----------|------------|------|------------|
| 0.85 | 0.03 | 0.00% | 0.6783     | 12.0     | 44.0      | 0.8748 | 2.2 |
| ...  | ...  | ...   | ...        | ...      | ...        | ...   | ... |

**Key Findings**:
- **Hysteresis Lock**: FP locked at 0% across all parameters
- **Recovery Works**: Panic duration reduced to 12 gens vs 258 in Phase-13
- **Entrainment Stable**: Convergence ratios maintained
- **No Tunable Regime**: Asymmetric thresholds prevent FP 10-25%

### 5.2 Hysteresis Analysis

The separate escalation/recovery thresholds maintain hysteresis:
- Escalation requires Ψ > 0.6
- Recovery requires Ψ < 0.5
- Middle zone (0.5-0.6) maintains current intensity

This prevents the desired tunable FP band.

### 5.3 Entrainment Validation

Despite hysteresis, temporal entrainment works:
- ω converges around 0.14 rad/gen
- High convergence ratios (0.87)
- Population bottlenecks indicate selection pressure

---

## 6. Architectural Boundaries

| Permitted | Forbidden |
|-----------|-----------|
| Continuous panic_intensity | Symmetric escalation/recovery |
| Asymmetric thresholds | Hysteresis removal |
| Intensity-scaled softening | Binary state machines |

---

## 7. Implementation Scope

### 7.1 Modified Files

| File | Change |
|------|--------|
| `phase14/panic_controller_v14.py` | Continuous intensity logic |
| `phase14_sweep.py` | Parameter sweep script |

### 7.2 New Files

| File | Purpose |
|------|---------|
| `phase14/panic_controller_v14.py` | Intensity-based controller |
| `phase14_sweep.py` | Parameter validation |

---

## 8. Transition from Phase 13

Phase-14 builds on Phase-13:
- **Phase-13**: Binary hysteresis → FP=75%
- **Phase-14**: Continuous intensity → FP=0%

Both maintain entrainment, but neither achieves tunable FP.

The hysteresis boundary condition remains unsolved.

---

## 9. Open Questions for Post-Implementation Analysis

1. **Can hysteresis be removed without destroying entrainment?**
2. **What controller architecture allows FP 10-25% with ω convergence?**
3. **Is tunable oscillatory regulation possible in this system?**
4. **Does the hysteresis represent a fundamental limit of reactive cognitive architectures?**
