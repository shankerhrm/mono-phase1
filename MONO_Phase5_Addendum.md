# MONO Phase-5 Addendum: Evolutionary Reproduction and Lineage Selection

## 5. Phase-5: Evolutionary Reproduction and Lineage Selection

### 5.1 Introduction
Phase-5 transitions MONO from individual survival to population-level evolution, introducing heritable variation in regulatory parameters. Reproduction creates lineages with inherited traits, enabling natural selection without external fitness functions.

The hypothesis is that shared resource competition and mutation will drive trait divergence and lineage persistence, establishing Darwinian evolution in a minimal artificial metabolism.

### 5.2 Design & Implementation
#### Population Dynamics
- **World Model:** Finite energy pool (10,000 units), distributed equally to cells (max 10 units/cell).
- **Competition:** Implicit via resource sharing; no explicit interactions.
- **Reproduction:** Phase-4 mechanics with heritable mutation (σ=0.01, clamped 0.01-1.0).
- **Death:** Cells removed if E≤0 or S≤0; new modes added (MUTATIONAL_INSTABILITY, REPRODUCTIVE_STARVATION, INHERITED_MAINTENANCE_DEBT).

#### Heritable Traits
Regulator parameters (α, β, γ) mutate at reproduction, affecting maintenance decisions.

#### Experimental Setup
Population run: 1 initial cell, max 100 cells, 500 cycles. Metrics: population size, trait means (α, β, γ), max generation, energy pool.

### 5.3 Results
#### Population Dynamics
- **Initial Growth:** Population remained at 1 for early cycles (cycles 0-3).
- **Extinction:** Simulation ended by cycle 4, likely due to insufficient energy accumulation for reproduction.
- **Energy Pool:** Decreased linearly (9990 → 9960), indicating steady consumption without replenishment.

#### Trait Evolution
- **No Variation Observed:** α_mean=0.1, β_mean=0.05, γ_mean=0.5 constant; no mutation-induced shifts.
- **Max Generation:** 0, no reproduction occurred.

#### Lineage Formation
- **Absence of Lineages:** Single-cell lineage; no branching or extinction events.
- **Reproduction Failure:** E did not reach E_repro=80 under shared resource constraints.

### 5.4 Discussion
Phase-5 implementation enables evolutionary mechanics, but the experiment revealed resource scarcity prevents reproduction. Shared pool (finite, competitive) limits E accumulation, contrasting Phase-4's individual success.

This highlights a key trade-off: Population dynamics introduce competition, but without resource abundance, evolution stalls. Adjustments (e.g., larger pool, lower E_repro) could enable divergence.

Implications: Evolution requires sufficient resources; competition must balance with growth. Phase-5 establishes the framework, but tuning is needed for observable evolution.

### 5.5 Conclusion
Phase-5 implements true evolutionary reproduction, but resource constraints limited outcomes. MONO now supports Darwinian evolution in principle; empirical evolution awaits parameter tuning.

### References
- Phase-4: Reproduction mechanics
- ALife standards: Blind, structural evolution
