# MONO: Latency-Aware Autonomous Systems Architecture

**Repository:** [github.com/shankerhrm/mono-phase1](https://github.com/shankerhrm/mono-phase1.git)

A research framework exploring the intersection of evolutionary biology, cognitive science, and artificial intelligence through evolutionary mechanisms. MONO investigates how autonomous systems can develop temporal awareness, adaptive decision-making, and robust behavior under uncertainty via heritable traits and natural selection.

Phase-27 focus: Darwinian evolution confirmed via adaptive tracking of environmental change, utilizing evolvable stress phenotypes, basal metabolism, and age-based generational turnover.

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
**Phase-18**: Socio-Ecological Feedback — extraction/restoration artifacts with environmental feedback  
**Phase-19**: Internal Economy — localized extraction/restoration trade and cultural transmission  
**Phase-20**: Individual Learning — running averages & dynamic market pricing  
**Phase-21**: Adaptive Sensing — environment-driven behavioral adaptation  
**Phase-22**: Resource Competition — density-dependent carrying capacity discovery  
**Phase-23**: Ecological Stability — environment-coupled quadratic reproduction  
**Phase-24**: Engine Immortalization — asynchronous reproduction and structural maintenance fixes  
**Phase-25**: Resilience Basin — testing reactive homeostasis vs evolution under shock  
**Phase-26**: Hard Selection — basal metabolism, age-based death, and extinction dynamics  
**Phase-27**: Adaptive Tracking — Darwinian evolution confirmed under gradual climate ramp (Current)

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
  - [MONO_Phase19_Addendum.md](MONO_Phase19_Addendum.md) — Internal Economy
  - [MONO_Phase20_Addendum.md](MONO_Phase20_Addendum.md) — Individual Learning
  - [MONO_Phase21_Addendum.md](MONO_Phase21_Addendum.md) — Adaptive Sensing
  - [MONO_Phase22_Addendum.md](MONO_Phase22_Addendum.md) — Resource Competition
  - [MONO_Phase23_Specification.md](MONO_Phase23_Specification.md) — Ecological Stability
  - [MONO_Phase24_Specification.md](MONO_Phase24_Specification.md) — Engine Stability
  - [MONO_Phase25_Specification.md](MONO_Phase25_Specification.md) — Shock Test & Resilience Basin
  - [MONO_Phase26_Specification.md](MONO_Phase26_Specification.md) — Evolution & Adaptive Tracking (Covers Phases 26-27)
- **Results**: [RESULTS.md](RESULTS.md) — Experimental findings across all phases

## Phase-27: Darwinian Evolution Confirmed

**Key Innovation**: Achieved true Darwinian evolution by escaping perfect homeostasis. Solved the "Invincible Restorer" paradox and implemented basal metabolism (2.0 E/gen) alongside age-based generational turnover (MAX_AGE=200).

**Key Findings**:
- **Three Evolutionary Regimes Discovered:**
  1. **Reactive Homeostasis (Case 1)**: Temporary 3× shock. Behavior shifts to restore the environment (56% → 82%), returning to the baseline Resilience Basin (~328 pop) post-shock. No permanent genetic change.
  2. **Selection + Extinction (Case 2)**: Permanent 8× instant shock. Population collapses (319 → 0) due to extreme environmental pressure. Darwinian selection occurs (genetic trait shift of -0.391) but evolutionary rescue fails.
  3. **Adaptive Tracking (Case 3)**: Permanent 3× gradual ramp. Population survives (319 → 314) successfully tracking the changing environment. Significant behavioral plasticity (81% restorer) prevents a death spiral, enabling a permanent genetic shift (-0.039) over 1500 generations.
- **Engine Stability:** Reached 100% survival and stable carrying capacity (~1100 pop in lush conditions) prior to shocks through repairing asynchronous reproduction and maintenance loops.

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
