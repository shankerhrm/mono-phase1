# MONO Phase-22 Addendum: Resource Competition & Environmental Dynamics

## Objective
Introduce population-dependent resource competition and refine environmental dynamics to create density-dependent carrying capacity.

## Architecture
- **Resource Competition**: `resource_per_agent = environmental_quality / population_size`
- **Environmental Dynamics**: Smooth population-coupled model replacing wild-oscillation bailout system
  - Per-cell depletion: `depletion_rate × population × 0.1`
  - Regeneration: `regeneration_rate × (K - env_quality)` with K=1.0
- **Quadratic Reproduction Coupling**: `repro_prob *= env_quality²`

## Results
- Initial parameter sweep: 100% extinction at generation 20 across all configurations.
- Root cause identified: pre-existing cell death spiral independent of environment.
- This led directly to the Phase 23-24 engine stability investigation.

## Conclusion
Phase 22 exposed fundamental cell engine bugs (orphaned maintenance, double energy deduction) that had been masked by earlier unstable environmental models. Fixing these bugs was the critical turning point for MONO's stability.
