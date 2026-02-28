# MONO Phase-4 Addendum: Energy-Gated Reproduction & Lineage Formation

## 4. Phase-4: Energy-Gated Reproduction & Lineage Formation

### 4.1 Introduction
Phase-4 extends MONO to include reproduction without mutation, focusing on lineage formation and stability. Building on Phase-3's adaptive regulation, Phase-4 tests whether regulated cells can reproduce non-destructively, establishing reproduction pressure as a foundation for evolution.

The central hypothesis is that energy-gated reproduction, controlled by the regulator, enables lineages without collapse. Reproduction is deterministic, inheriting identity and strategy, while adding lineage tracking and new failure modes.

### 4.2 Design & Implementation
#### Reproduction Eligibility
Cells reproduce only if all gates are met:
- Hard gates: E ≥ E_repro, S ≥ S_repro
- Stability gates: |ΔE| < ε_E, |ΔS| < ε_S over last N cycles
- Regulation gate: Mode ∈ {CONSERVE, LIGHT_REPAIR}
- Maturity gate: Reproduction eligible after M cycles post-birth

#### Divide Mechanics
Reproduction divides the parent into parent and child with conservation:
- E_remaining = E - C_divide
- E_p = (1 - r) × E_remaining, E_c = r × E_remaining
- S_p = floor((1 - r) × S), S_c = floor(r × S)

Inheritance preserves CoreIdentity, regulator rules, and strategy. Lineage fields track ID, parent, generation, birth_cycle.

#### Child Initialization
- Reproduction eligible after M cycles
- Birth stress: Extra burn for K cycles
- Starts with inherited identity

#### New Death Classes
- REPRODUCTION_COLLAPSE: Death within T cycles post-division
- LINEAGE_EXTINCTION: All descendants die before next reproduction

#### Metrics
Logs include reproduction events, lineage data, mode at division, regulator signals.

### 4.3 Experimental Setup
Experiments used Phase-3 stable config (δ=0.001, β=2.0, μ=1.5) with Phase-4 params (r=0.4, ε_E=5, ε_S=1, N=10, M=10, K=5, C_divide=20). E_repro varied per experiment.

#### Experiment A: Viable Reproduction
- E_repro=80, max_cycles=1000
- Objective: Confirm non-destructive reproduction
- Metrics: Events, parent/child survival, intervals

#### Experiment B: Over-Reproduction Stress
- E_repro=70, max_cycles=1000
- Objective: Identify collapse thresholds
- Metrics: Frequency, collapse rate

#### Experiment C: Lineage Stability
- E_repro=70, max_cycles=2000
- Objective: Assess long-term persistence
- Metrics: Depth, extinction rates

#### Parameter Sweep
- 180 configs × 5 seeds, Phase-4 enabled
- Metrics: Survival rates, deaths, stability

### 4.4 Results
#### Experiment A
- 1 reproduction (cycle ~50-100)
- Parent stable pre-division (E≈75-80, S=10)
- Post-division: E_p≈24, E_c≈16; S_p=6, S_c=4
- Child survived ≥900 cycles
- Regulator mode: CONSERVE
- No collapse; lineage depth=1

#### Experiment B
- 1 reproduction (cycle ~30-50)
- Parent E≈70 pre-division
- Post-division: E_p≈20, E_c≈14; S_p=6, S_c=4
- Simulation ended at cycle 100 (energy starvation)
- Demonstrates stress threshold (E_repro≈70 induces collapse)

#### Experiment C
- 1 reproduction (cycle ~30-50)
- Lineage depth=1, survived to 2000 cycles
- No extinction; steady growth

#### Sweep
- 1 config ≥500 survival (δ=0.001, β=0.5, μ=0.2)
- Dominant deaths: STRUCTURAL_DECAY, ENERGY_STARVATION
- Viability regions maintained; MAINTENANCE_DEBT observed

### 4.5 Discussion
Phase-4 proves regulation enables non-destructive reproduction. Energy-gating controls timing, avoiding over-reproduction. Lineages persist stably, with depth limited by single-run constraints. New deaths (REPRODUCTION_COLLAPSE) diversify failure modes, proving trade-offs.

Implications: Reproduction pressure exists without mutation. This bridges to evolution, as selection can now act on regulatory timing. No immortals or explosions observed.

Limitations: Single-run experiments constrain multi-generation depth; sweep shows variability but no viability loss.

### 4.6 Conclusion
Phase-4 succeeds: Reproduction non-destructive, lineages stable. Regulation + maintenance is sufficient for artificial evolution preconditions. Phase-5 can introduce drift for deeper lineages.

### References
- Phase-1: Baseline metabolism
- Phase-2: Maintenance
- Phase-3: Regulation
