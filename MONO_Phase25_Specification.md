# MONO Phase-25 Specification: Environmental Shock Test

## Objective
Determine whether MONO exhibits true Darwinian evolution (Case 2) or merely reactive homeostasis (Case 1) under environmental crisis.

## Experiment Design
- **Timeline**: baseline(0-400) → shock(400-700) → recovery(700-1500)
- **Shock**: depletion_rate tripled (0.05 → 0.15)
- **Seeds**: 5 independent runs for statistical robustness
- **Metrics**: Behavioral (proportion_restoring), Genetic (strategy_trait, env_sensitivity, variance), Ecological (population, lineage_diversity)

## Result: Case 1 — Reactive Homeostasis

| Phase | Population | % Restorers | Strategy Trait |
|---|---|---|---|
| Baseline | 329 | 56% | 0.4861 |
| Shock | 328 | 82% | 0.4862 |
| Recovery | 328 | 56% | 0.4862 |

- **Behavior changed** (56% → 82% restorers) but **reverted** after recovery
- **Genetics unchanged** — zero permanent trait shift
- **Resilience Basin confirmed**: population attractor at ~328

## Root Causes Identified
1. **"Invincible Restorer"**: `env_factor = 3.0 - env_quality` gave restorers MORE energy in bad environments
2. **Zero basal metabolism**: Resting cost ≈ 0, enabling infinite survivability
3. **No aging**: No generational turnover to create ecological slots

## Conclusion
MONO is a perfectly stable homeostatic machine. To reach evolution, the system requires hard selection pressure where behavioral adaptation alone is insufficient.
