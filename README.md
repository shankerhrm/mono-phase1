# MONO: Monolithic Cell AI System

**Repository:** [github.com/shankerhrm/mono-phase1](https://github.com/shankerhrm/mono-phase1.git)

A deterministic computational model of an artificial cell exploring the boundary conditions for sustained metabolic stability in closed systems. The project spans Phase-1 through Phase-6, progressively introducing complexity from basic metabolism through regulation, reproduction, evolution, and latency-constrained cognition.

## Project Phases

**Phase-1**: Baseline metabolism and viability boundary  
**Phase-2**: Active maintenance as necessary condition for stability  
**Phase-3**: Adaptive regulation via rule-based homeostasis  
**Phase-4**: Energy-gated reproduction & lineage formation  
**Phase-5**: Evolutionary reproduction with heritable traits  
**Phase-6**: Latency-bound organism dynamics and narrative cognition (Current)  
**Phase-7**: Evolution of cognitive efficiency (Proposed)  

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

## Extending to Full Academic Paper

The project includes a comprehensive framework for expanding Phase-6 into a full-length journal paper:

**[MONO_Extended_Paper_Outline.md](MONO_Extended_Paper_Outline.md)** — Framework for optional extended sections:
- Reproduction under shock regimes
- Evolution of cognitive efficiency (Phase-7)
- Scaling laws across size classes  
- Comparison to biological nervous systems
- Formal proofs of stability bounds

**[MONO_Phase7_Addendum.md](MONO_Phase7_Addendum.md)** — Phase-7 placeholder (Evolution of cognitive efficiency):
- Heritable mutations in cognitive parameters
- Population evolution of prediction strategies
- Evolutionary landscape mapping
- Empirical predictions and timeline

**Choose your publication path**:
- **Conference submission** (quick, 6,000 words): Use Phase-6 Addendum as-is
- **Journal paper** (comprehensive, 15,000–20,000 words): Implement Sections 3–4 of Extended Outline (6–8 weeks)
- **Full treatment** (20,000+ words): Add Phase-7 experiments + formal proofs (3–4 months)

## License

Code: MIT (see LICENSE)

Whitepaper & Addendums: CC BY 4.0 (see LICENSE-CC-BY-4.0.txt)

## Citation

See CITATION.cff for citation details.
