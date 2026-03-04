# MONO: Monolithic Cell AI System

**Repository:** [github.com/shankerhrm/mono-phase1](https://github.com/shankerhrm/mono-phase1.git)

A deterministic computational model of an artificial cell exploring the boundary conditions for sustained metabolic stability in closed systems. The project spans Phase-1 through Phase-6, progressively introducing complexity from basic metabolism through regulation, reproduction, evolution, and latency-constrained cognition.

## Project Phases

**Phase-1**: Baseline metabolism and viability boundary  
**Phase-2**: Active maintenance as necessary condition for stability  
**Phase-3**: Adaptive regulation via rule-based homeostasis  
**Phase-4**: Energy-gated reproduction & lineage formation  
**Phase-5**: Evolutionary reproduction with heritable traits  
**Phase-6**: Latency-bound organism dynamics and narrative cognition  
**Phase-7**: Cognitive evolution — mutable gating, modular prediction, arbitration  
**Phase-8**: Competitive ecology — resource zones, latency shadowing, spatial competition  
**Phase-9**: Species Memory — cross-generational trait priors under IOBA constraints  
**Phase-10**: Observability & invariance validation — falsifiable architecture verification  
**Phase-11**: IIBA — Initialization-Inheritance Bias Architecture, yolk strategy, vacuum ecology  
**Phase-12**: Panic Architecture — state-dependent evolvability modulation (Current)  

## Documentation

- **Whitepaper**: [whitepaper/whitepaper.md](whitepaper/whitepaper.md) — Phase-1 methodology and baseline results
- **Phase Addendums & Specifications**:
  - [MONO_Phase2_Addendum.md](MONO_Phase2_Addendum.md) — Maintenance mechanics
  - [MONO_Phase3_Addendum.md](MONO_Phase3_Addendum.md) — Adaptive regulation
  - [MONO_Phase4_Addendum.md](MONO_Phase4_Addendum.md) — Reproduction & lineage
  - [MONO_Phase5_Addendum.md](MONO_Phase5_Addendum.md) — Evolution & mutation
  - [MONO_Phase6_Addendum.md](MONO_Phase6_Addendum.md) — Latency dynamics & cognition
  - [MONO_Phase7_Addendum.md](MONO_Phase7_Addendum.md) — Cognitive evolution
  - [MONO_Phase8_Specification.md](MONO_Phase8_Specification.md) — Competitive ecology
  - [MONO_Phase9_Specification.md](MONO_Phase9_Specification.md) — Species Memory (IOBA)
  - [MONO_Phase10_Specification.md](MONO_Phase10_Specification.md) — Observability & invariance
  - [MONO_Phase11_Specification.md](MONO_Phase11_Specification.md) — IIBA & vacuum ecology
  - [MONO_Phase12_Specification.md](MONO_Phase12_Specification.md) — Panic Architecture
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
