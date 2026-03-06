# MONO Phase-18 Addendum: Socio-Ecological Feedback with Extraction/Restoration Artifacts

## Objective
Map the socio-ecological phase space of a single species with two cultural traits (extraction A_x, restoration A_r), heritable action propensity p_restore, and environmental feedback (depletion from extraction, regeneration from restoration with diminishing returns).

## Experiment
Parameters varied: depletion rate (0.08–0.12), restoration energy multiplier (0.15–0.25).

Fixed: regeneration rate 0.01, environmental exponent 2.0, cultural decay 0.999.

1 seed per cell (initial test; full multi-seed runs will refine boundaries).

## Regime Classification
| Regime | Description | Parameter Region | Characteristics |
|--------|-------------|------------------|----------------|
| I | Stable extraction dominance | Depletion ≤0.09 (all restore_mult) or depletion 0.10–0.12 with restore_mult ≥0.20 | Environment stabilizes at degraded level (~0.8), proportion restoring low/stable, p_restore ~0.5, no variance |
| II | Oscillatory (damped) | Depletion 0.10–0.12 with restore_mult 0.15–0.21 | Early oscillations (prop_restore 0.01–0.35), env fluctuates, then damps to Regime I |
| III | Collapse | Depletion ≥0.11 with restore_mult ≤0.18 | Extinction by gen 90–276, env collapses to 0 |

## Key Insights
- The system exhibits degraded sustainability—a stable but low-environment equilibrium is the dominant outcome.
- Oscillations are transient; no persistent cycles emerged in this single-seed sweep (multi-seed might reveal rare persistent cases).
- Collapse requires extreme stress—high depletion combined with very low restoration reward.
- No specialisation: p_restore variance = 0 across all runs; individuals do not diverge into pure extractors or restorers under current pressures.

## Conclusion
Phase-18 successfully demonstrates socio-ecological feedback and a clear boundary between sustainable degradation and collapse. The architecture is sound and ready for the next layer: division of labour and internal trade.
