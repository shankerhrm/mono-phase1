# MONO Phase-24 Specification: Engine Stability & Asynchronous Reproduction

## Objective
Fix three critical cell engine bugs that caused guaranteed extinction at ~20 generations regardless of environmental conditions.

## Bug Fixes

### 1. Orphaned Maintenance Loop
- **Problem**: `perform_maintenance()` was never called in the active lifecycle. Structure could only decay.
- **Fix**: Restored the maintenance call in `cell/lifecycle.py`, enabling cells to repair structural damage.

### 2. Double Energy Deduction
- **Problem**: Actions deducted energy twice — once via `cell.energy.E -= cost` and again via `energy.update(C_t)`.
- **Fix**: Separated `logged_action_cost` from `C_t` to prevent double-counting.

### 3. Synchronized Reproduction Collapse
- **Problem**: All cells reproduced simultaneously → energy crash → death wave → extinction spiral.
- **Fix**: Added `maturity_age = 4`, `reproduction_cooldown = 3`, and randomized initial `cycle_count` to de-synchronize reproduction.

## Verification
- **1000-generation stability test**: Zero structural deaths confirmed.
- **Phase 23 sweep**: 27/27 survival after applying all fixes.

## Conclusion
Phase 24 repairs transformed the cell engine from "guaranteed extinction at gen 20" to "structurally immortal" — the prerequisite for meaningful ecological and evolutionary dynamics.
