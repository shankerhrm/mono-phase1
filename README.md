# MONO: Monolithic Cell AI System

A deterministic computational model of an artificial cell exploring the boundary conditions for sustained metabolic stability in closed systems. The project spans Phase-1 through Phase-6, progressively introducing complexity from basic metabolism through regulation, reproduction, evolution, and latency-constrained cognition.

## Project Phases

**Phase-1**: Baseline metabolism and viability boundary  
**Phase-2**: Active maintenance as necessary condition for stability  
**Phase-3**: Adaptive regulation via rule-based homeostasis  
**Phase-4**: Energy-gated reproduction & lineage formation  
**Phase-5**: Evolutionary reproduction with heritable traits  
**Phase-6**: Latency-bound organism dynamics and narrative cognition (Current)  

## Documentation

- **Whitepaper**: [whitepaper/whitepaper.md](whitepaper/whitepaper.md) — Phase-1 methodology and baseline results
- **Phase Addendums**:
  - [MONO_Phase2_Addendum.md](MONO_Phase2_Addendum.md) — Maintenance mechanics
  - [MONO_Phase3_Addendum.md](MONO_Phase3_Addendum.md) — Adaptive regulation
  - [MONO_Phase4_Addendum.md](MONO_Phase4_Addendum.md) — Reproduction & lineage
  - [MONO_Phase5_Addendum.md](MONO_Phase5_Addendum.md) — Evolution & mutation
  - [MONO_Phase6_Addendum.md](MONO_Phase6_Addendum.md) — Latency dynamics & cognition
- **Results**: [RESULTS.md](RESULTS.md) — Experimental findings across all phases

## Phase-6: Latency-Bound Organism Dynamics

**Key Innovation**: Time scarcity as primary evolutionary constraint

**Key Findings**:
- Viability governed by strict inequality: τ_organism < τ_failure
- Coordination cost scales logarithmically: τ_coord ∝ log(N)
- Cognitive advantage: **21% survival gain** under environmental shocks (Phase-6.3)
- Conditional adaptivity: Narrative cognition maladaptive in stable regimes, strongly adaptive under pressure
- Emergent architecture: Scene-based temporal sequencing from error-driven arbitration and modular self

## Code

Run experiments with `python experiments/sweep.py` or phase-specific tests in `experiments/`

## Generating PDFs

```bash
# Phase-1 whitepaper
pandoc whitepaper/whitepaper.md -o whitepaper/MONO_Whitepaper_v1.0.pdf --pdf-engine=xelatex

# Phase-6 addendum
pandoc MONO_Phase6_Addendum.md -o MONO_Phase6_Addendum.pdf --pdf-engine=xelatex
```

## License

Code: MIT (see LICENSE)

Whitepaper & Addendums: CC BY 4.0 (see LICENSE-CC-BY-4.0.txt)

## Citation

See CITATION.cff for citation details.
