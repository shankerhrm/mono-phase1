# MONO Phase 28.1: Evolutionary Correction & Resilience Testing

## Objective
Phase 28 proved that the spatial engine can achieve an Evolutionarily Stable Strategy (ESS) and geographic stability over 1500 generations. However, the exact convergence of the population's strategy trait (variance dropping to zero) presents a long-term risk of **Evolutionary Stagnation**. 

Phase 28.1 will introduce controlled volatility to ensure the ecosystem maintains dynamic adaptability and tests its resilience to massive shocks.

## Core Implementations

### 1. Mutation-Selection Balance (Genetic Drift)
- **Problem**: Complete trait fixation leaves the population helpless if the environment changes fundamentally. 
- **Solution**: Enforce a probabilistic minimum mutation variance.
- **Mechanism**: During reproduction, 90% of inheritance is exact, but 10% of the time, apply a baseline genetic drift to the offspring's `strategy_trait` (`±0.02`). This maintains a stable variance without causing chaotic instability.

### 2. The Catastrophic Shock (K-T Event Test)
- **Problem**: Does the spatial clustering architecture allow for rapid recovery following a mass extinction event?
- **Mechanism**: At Generation 800, instantly eradicate 50% of the active population at random. 
- **Expected Observation**: We map the spatial recovery as isolated surviving clusters expand outward to reclaim empty territory. We also watch the Trait Mean/Variance to see if the extinction dislodges the original Evolutionarily Stable Strategy (ESS).

### 3. Global Famine (Resource Collapse Test)
- **Problem**: Test ecosystem resilience against prolonged environmental rather than population shock.
- **Mechanism**: Between generation 1100 and 1150, the environmental regeneration rate is globally suppressed to near zero.
- **Expected Observation**: Track the population dip, trait shift, and post-famine recovery time.
