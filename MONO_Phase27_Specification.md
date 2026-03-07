# MONO Phase-27 Specification: Oscillating Climate Evolution

## Objective
Test if MONO can survive non-stationary environments and whether evolutionary tracking (trait oscillation, polymorphism, or evolutionary memory) emerges when faced with cyclic environmental pressures.

## Environment Oscillation (Smooth Sine Wave)
Instead of a hard step-function shock, the environment will experience a smooth sine-wave oscillation. Biology rarely faces perfect step functions, and continuous shifts reveal the exact evolutionary lag.

`depletion_rate(gen) = base + amplitude * math.sin(2 * math.pi * gen / period)`
*   `base` = 0.10
*   `amplitude` = 0.05
*   `period` = 400 generations

## Metrics to Track
1.  `env_quality`: The ecological state history.
2.  `population`: To track boom/bust cycles or extinction events.
3.  `mean_strategy_trait`: The primary heritable trait dictating survival strategy.
4.  `strategy_trait_variance`: To measure selection pressure intensity.
5.  `trait_lag`: `abs(mean_strategy_trait - optimal_strategy(env_quality))` to measure evolutionary response latency.
6.  `trait_histogram`: Detect structural polymorphism (niches). Multiple peaks guarantee distinct strategies are coexisting peacefully.
7.  `lineage_diversity`: The number of unique genetic lineages surviving.
8.  `proportion_restoring`: Proportion of individuals executing the restorer behavior.

## Expected Scientific Outcomes
After running the oscillating environment, the population should fall into one of three buckets:
*   **Case A (Adaptive Tracking)**: `strategy_trait` oscillates continuously following the environment. `trait_lag` remains stably small. The population is resilient.
*   **Case B (Generalist Evolution)**: `strategy_trait` converges to the middle and stabilizes. Variance is small. The organism has compromised to survive all conditions without mutating continuously.
*   **Case C (Polymorphism)**: Two stable strategy clusters emerge (`trait_histogram` splits into two discrete peaks). A high overall variance indicates stable coexistence of fast exploiters and slow restorers.
