# MONO Phase-2 Addendum: Active Maintenance as a Necessary Condition for Artificial Metabolism Stability

## 2. Phase-2: Active Maintenance as a Necessary Condition for Artificial Metabolism Stability

### 2.1 Introduction
Phase-1 established that closed artificial metabolism fails to sustain stability under any parameter range, dying primarily from STRUCTURAL_DECAY or ENERGY_STARVATION. Phase-2 introduces active maintenance, a bounded mechanism for structural repair, to test whether maintenance, not intelligence, is the missing ingredient for persistence.

The hypothesis is that reactive, rule-based maintenance counteracts decay without violating identity invariants or energy conservation. This mirrors cellular homeostasis, extending Phase-1's deterministic actions.

### 2.2 Design & Implementation
#### Maintenance Engine (ME)
- **Inputs:** S(t), E(t), δ
- **Outputs:** Repair action R_m, Cost C_m, Structural gain ΔS_m
- **Rules:** Reactive thresholds (S < S_critical and E > E_maintenance_min)
- **Repair Model:** ΔS_m = α × C_m × (1 - S / S_max), with α = repair_efficiency
- **Energy Accounting:** C_m deducted from E, no net energy gain

#### Quiescence Integration
Quiescence (E < E_quiescence and S < S_quiescence) skips actions but includes maintenance and burn.

#### Lifecycle Update
Cycle order: Basal Burn → Structural Decay → Maintenance → Action Execution → Reproduction → Death Check.

Maintenance is applied after decay, before actions.

#### Taxonomy Updates
New death classes: MAINTENANCE_DEBT (repair cost exceeds intake), REPAIR_OSCILLATION (over-repair cycles), FALSE_STABILITY (decay masked until collapse).

#### Experimental Setup
Parameter sweep: 180 configs (6 δ × 6 β × 5 μ) × 5 seeds, with maintenance enabled. Metrics: lifespan, death classification, stability classes.

### 2.3 Results
#### Sweep Outcomes
- Dominant deaths: STRUCTURAL_DECAY (high δ/β), ENERGY_STARVATION (low μ)
- New deaths: MAINTENANCE_DEBT observed in repair-intensive configs
- Stability classes: PSEUDO_STABLE dominant; LOW_AMPLITUDE_OSCILLATION in viable regions
- Key finding: One configuration (δ=0.001, β=2.0, μ=1.5) achieved survival ≥500 cycles
- Viability region expanded marginally compared to Phase-1 (0 survival)

#### Comparative Analysis
- Phase-1: No survival ≥500
- Phase-2: Partial success in low-decay, high-burn configs
- Maintenance cost sustainable in stable regions; oscillatory collapse reduced

### 2.4 Discussion
Phase-2 demonstrates active maintenance enables persistence in marginal conditions, proving it is a necessary (though insufficient) condition. The survival in δ=0.001, β=2.0, μ=1.5 shows maintenance stabilizes high-burn metabolism against decay.

New death modes (MAINTENANCE_DEBT) introduce meaningful trade-offs, distinguishing Phase-2 from mechanical failure. However, viability remains narrow, indicating regulation (Phase-3) is required for broader stability.

Implications: Maintenance shifts MONO from passive decay to active homeostasis, a critical step toward life-like autonomy.

Limitations: Sweep deterministic; no learning; maintenance fixed, not adaptive.

### 2.5 Conclusion
Phase-2 succeeds partially: Maintenance enables survival in specific niches. This boundary condition justifies Phase-3's regulation. Without maintenance, evolution is impossible; with it, control becomes essential.

### References
- Phase-1: Closed metabolism baseline
- Phase-3: Adaptive regulation extension
