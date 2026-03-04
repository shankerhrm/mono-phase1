# MONO Phase-8 Specification
## Competitive Ecology Under Latency-Bound Constraints

### Phase-8 Objective

Phase-8 introduces multi-organism competition to test whether latency-optimized cognition remains evolutionarily stable in the presence of other agents competing for shared, finite resources.

The goal is not to reward aggression or intelligence directly, but to observe which cognitive strategies persist under:
- resource contention
- interference
- indirect competition
- extinction pressure

Phase-8 asks a single question:
**Does adaptive control of cognition remain advantageous when other organisms exist?**

---

## Core Principle

No explicit fitness function is introduced.

Selection emerges only from:
1. survival
2. reproduction
3. resource access
4. latency failure

---

## Environment Model

### Shared World
- Discrete time cycles (same as prior phases).
- Finite resource field $R(t)$.
- Environmental decay continues ($\tau_{failure}$ still applies per organism).

### Resources
Each resource unit provides:
- Energy intake ($\Delta E$)
- Optional structural stabilization ($\Delta S$)

Resources regenerate at a fixed or stochastic rate. Scarcity is real.

---

## Organism Interaction Rules

### 1. Resource Competition (Primary)
Resources are non-exclusive. Multiple organisms may attempt to consume the same resource.

**Rule:**
If two organisms target the same resource:
$$\text{winner} = \text{argmin}(\tau_{organism})$$

This immediately links:
- cognition overhead
- coordination delay
- survival outcome

*(No combat required.)*

### 2. Interference via Latency Shadowing
Organisms increase effective coordination costs for nearby organisms by:
- occupying resource-rich zones
- triggering environmental perturbations
- forcing reactive coordination

This creates implicit pressure without explicit attacks.

### 3. No Direct Attacks (Initially)
Phase-8 explicitly forbids hardcoded aggression.

**Why:**
- Attacks introduce artificial dominance mechanics.
- Early biological competition was indirect.
- Latency competition is more fundamental.

*(Direct antagonism can be Phase-9.)*

---

## Reproduction Under Competition

Reproduction rules from Phase-7 remain, with one addition:

### Competitive Reproduction Constraint
Reproduction only succeeds if:
$$\tau_{organism} \ll \tau_{failure} \quad \text{AND} \quad \rho_{local\_resource} > \rho_{min}$$

This prevents runaway replication and forces:
- timing awareness
- ecological sensitivity

Children inherit:
- cognitive traits
- regulator parameters
- energy/structure split as before

---

## Population Dynamics

### Carrying Capacity
Population size is not capped explicitly. Instead, it emerges from:
- resource regeneration rate
- average latency overhead
- structural decay

Overpopulation causes extinction naturally.

### Selection Pressures Introduced
Phase-8 introduces four orthogonal pressures:

| Pressure | Selects For |
| :--- | :--- |
| Resource scarcity | Low-latency action |
| Competition | Efficient cognition gating |
| Environmental decay | Structural robustness |
| Crowding | Reduced coordination overhead |

---

## Expected Emergent Phenomena

### 1. Cognitive Stratification
Populations should split into:
- reflex-dominant scavengers
- predictive specialists
- low-cognition opportunists

*No design enforces this — it must emerge.*

### 2. Evolutionary Suppression of Excess Thought
Overthinking organisms should:
- arrive late
- lose resources
- fail reproduction
- go extinct

This is the key Phase-8 validation.

### 3. Latency Arms Races (Without Violence)
Prediction depth increases only if it improves arrival timing. Otherwise, it is selected against.

---

## Phase-8 Success Criteria

Phase-8 is successful if:
- ✅ Populations stabilize without manual tuning.
- ✅ Cognitive traits diverge across niches.
- ✅ Reflex-only organisms outperform thinkers in stable niches.
- ✅ Predictive organisms dominate in volatile niches.
- ✅ No single architecture universally dominates.

Failure modes include:
- universal extinction
- runaway intelligence
- trivial dominance strategies

---

## Instrumentation & Metrics

Track per generation:
- Population size
- Mean $\tau_{organism}$
- Mean `prediction_horizon`
- Mean `gating_threshold`
- Resource utilization efficiency
- Extinction rate per phenotype

*No leaderboard. Only lineage persistence matters.*

---

## Phase-8 Boundary Conditions

Phase-8 does not include:
- explicit combat
- communication between organisms
- cooperation
- deception between agents

*These are deferred intentionally.*

---

## Scientific Claim of Phase-8

If Phase-8 behaves as predicted, MONO demonstrates:

> **Intelligence is not a competitive advantage by default — it is an ecological specialization constrained by time.**

This moves MONO from organism simulation to evolutionary ecology.

### Phase-9 Preview (Optional)
Only after Phase-8 stabilizes:
- signaling
- cooperation
- deception
- coalition dynamics

*But Phase-8 must prove competition without intent first.*
