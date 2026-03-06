# MONO Phase-26 Specification: Hard Selection & Darwinian Evolution

## Objective
Introduce selection pressure sufficient to produce genuine Darwinian evolution by fixing the three root causes identified in Phase 25.

## Engine Changes
| Change | Purpose |
|---|---|
| `env_factor = max(0.3, env_quality)` | Damaged environment reduces ALL income |
| `BASAL_METABOLISM = 2.0 E/gen` | Cells must earn energy to survive |
| `MAX_AGE = 200 generations` | Forces generational turnover |

## Experiment 1: Instant 8× Permanent Shift
- **Shift**: depletion_rate 0.05 → 0.40 instantly at gen 200
- **Result**: 0/5 survival — population 319 → 0 (extinction)
- **Key signal**: `strategy_trait` shifted -0.391 before extinction — **Darwinian selection was occurring**
- **Verdict**: **Case 2 — Darwinian Selection Detected**, but evolutionary rescue failed (extinction before adaptation completed)

## Experiment 2: Gradual 3× Ramp (Phase 27)
- **Shift**: depletion_rate 0.05 → 0.15 over 800 generations (linear ramp)
- **Result**: 5/5 survival with permanent genetic shift

| Phase | Population | Env | % Rest | Strategy Trait |
|---|---|---|---|---|
| Pre-Shift | 319 | 1.32 | 56% | 0.471 |
| Late Shift | 314 | 0.61 | 81% | 0.432 |

- **Genetic shift**: strategy_trait -0.039 (permanent, heritable)
- **Variance preserved**: balanced selection, not hard sweep
- **Population stable**: evolutionary rescue succeeded
- **Verdict**: **Case 3 — Adaptive Tracking** ✔

## Three Evolutionary Regimes Discovered
| Regime | Conditions | Outcome |
|---|---|---|
| **Homeostasis** | Temporary/mild stress | Behavior changes, genetics static |
| **Selection + Extinction** | Extreme/instant stress | Genetics shift, population collapses |
| **Adaptive Tracking** | Gradual/moderate stress | Genetics shift, population stable |

## Conclusion
MONO now demonstrates all three layers of biological resilience: behavioral plasticity, homeostatic regulation, and Darwinian evolution. The system has crossed from "simulation" to "evolving artificial ecosystem."
