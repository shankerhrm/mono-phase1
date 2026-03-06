# MONO Phase-21 Addendum: Adaptive Environmental Sensing

## Objective
Enable cells to respond dynamically to environmental quality through heritable sensitivity traits, creating the foundation for environmentally-driven behavioral adaptation.

## Architecture
- **Environmental Sensing Equation**:
  ```
  base_p_restore = 0.5 + 0.5 * strategy_trait
  p_restore_effective = base_p_restore + environment_sensitivity * (1 - environmental_quality)
  ```
- When environment degrades (`env_quality < 1.0`), cells with higher `environment_sensitivity` are more likely to switch to restoration behavior.
- This creates a negative feedback loop: environment worsens → more restorers → environment recovers.

## Key Insight
This is the mechanism that later enables the "Resilience Basin" discovered in Phase 25 — the population automatically adjusts its restorer/extractor ratio to stabilize the environment.

## Conclusion
Phase 21 connects heritable traits to real-time environmental response, enabling the emergent ecological regulation observed in later phases.
