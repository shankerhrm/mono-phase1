# MONO: Latency-Aware Autonomous Systems Architecture

**Repository:** [github.com/shankerhrm/mono-phase1](https://github.com/shankerhrm/mono-phase1.git)

A research framework exploring the intersection of evolutionary biology, cognitive science, and artificial intelligence through evolutionary mechanisms. MONO investigates how autonomous systems can develop temporal awareness, adaptive decision-making, and robust behavior under uncertainty via heritable traits and natural selection.

Phase-18 focus: Socio-ecological feedback with two cultural artifacts (extraction/restoration), heritable action propensity, and environmental niche construction.

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
**Phase-12**: Panic Architecture — state-dependent evolvability modulation  
**Phase-13**: Endogenous temporal adaptation — entrainment without world modeling  
**Phase-14**: Regime flip dynamics — evolutionary stability under environmental shifts  
**Phase-15**: Physiological load accumulation — stress response modeling  
**Phase-16**: Evolvable Stress Phenotypes — heritable α/β traits for evolutionary regulation  
**Phase-17**: Cultural Niche Construction — gene-culture-environment coevolution  
**Phase-18**: Socio-Ecological Feedback — extraction/restoration artifacts with environmental feedback (Current)

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
  - [MONO_Phase15_Specification.md](MONO_Phase15_Specification.md) — Physiological Load
  - [MONO_Phase16_Specification.md](MONO_Phase16_Specification.md) — Evolvable Stress Phenotypes
  - [MONO_Phase17_Specification.md](MONO_Phase17_Specification.md) — Cultural Niche Construction
  - [MONO_Phase18_Addendum.md](MONO_Phase18_Addendum.md) — Socio-Ecological Feedback
- **Results**: [RESULTS.md](RESULTS.md) — Experimental findings across all phases

## Phase-18: Socio-Ecological Feedback

**Key Innovation**: Environmental feedback with two cultural artifacts (extraction A_x, restoration A_r), heritable action propensity p_restore.

**Key Findings**:
- Three regimes: stable extraction dominance (degraded sustainability), damped oscillations, collapse.
- Oscillations transient; no persistent cycles.
- Collapse requires extreme stress (high depletion + low restoration reward).
- No specialization; p_restore variance = 0.
- Demonstrates socio-ecological feedback boundaries.

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

## Copyright

Copyright © 2024 Techbilla Software Pvt Ltd. All rights reserved.
