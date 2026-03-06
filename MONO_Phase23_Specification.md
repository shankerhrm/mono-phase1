# MONO Phase-23 Specification: Environment-Coupled Reproduction

## Objective
Couple reproduction probability to environmental quality using quadratic scaling, creating a soft carrying capacity that prevents boom-bust cycles.

## Architecture
- **Quadratic Coupling**: `reproduction_probability *= env_quality²`
- **Threshold Penalty**: `if env_quality < 0.3: probability *= 0.1`
- **Minimum Floor**: `max(reproduction_probability, 0.001)` for rare recovery births
- **Smooth Environmental Dynamics**: K=1.0 equilibrium, 10% base regeneration, no bailout

## Key Result: 27/27 Survival
A full parameter sweep across 27 configurations (depletion: 0.03/0.05/0.07 × regeneration: 0.01/0.02/0.03 × resource: 2.0/3.0/4.0) resulted in **100% survival** for 500+ generations.

| Environment | Equilibrium Pop | Env Quality | Restorer % |
|---|---|---|---|
| Low stress | ~1060 | 2.00 (max) | 28% |
| High stress | ~1207 | 1.28 | 61% |

## Emergent Property: Labor Specialization
Under high stress, 61% of cells adopt restoration behavior vs only 28% in lush environments. This self-organized labor division is a classic ecological negative feedback loop.

## Conclusion
Phase 23 proves that MONO has crossed from "fragile simulation" to "stable ecological system" with emergent carrying capacity and adaptive social behavior.
