# MONO Phase-9 Specification
## Species Memory Under Latency-First Cognition

### Phase-9 Objective

Phase-9 introduces **Species Memory** as an adaptive, cross-generational summary of which organism-level cognitive traits remain viable under selection pressure.

The goal is not to “design intelligence”, but to test whether the system can:
- accumulate stable trait priors from survival outcomes
- distribute those priors to offspring
- avoid pathological memory dynamics (drift, hysteresis, bias collapse)

Phase-9 asks a single question:
**Can trait-level evolutionary memory improve long-horizon viability without collapsing into runaway specialization or noise drift?**

### Architecture Name: Initialization-Only Bias Architecture (IOBA)

MONO implements an **Initialization-Only Bias Architecture (IOBA)**, in which population-level memory influences only initial parameterization at reproduction and has zero runtime access to organism decision processes.

Definition:

An Initialization-Only Bias Architecture is an adaptive system where Species Memory may bias offspring initialization via scalar defaults, but is structurally prohibited from influencing lifecycle execution, cognition, or action selection.

---

## Core Mathematical Object

Species Memory is defined as an expectation over survivor-conditioned organism features:

$$M_s(t) = \mathbb{E}[\phi(A, \Gamma, \tau, E, R, S) \mid S=1]$$

Where $\phi(\cdot)$ extracts a feature vector from organism execution and $S \in \{0,1\}$ denotes per-cycle survival.

### Update Rule

For each component $k$ in the memory vector:

$$M_{s,k}(t+1) = (1-\alpha)\,M_{s,k}(t) + \alpha\,\mu_k(t)$$

Where $\mu_k(t)$ is the aggregate statistic of the survivor-conditioned sample at time $t$.

---

## Architecture: Three-Layer Memory Pipeline

### Layer 1 — Organism Logging
Each organism emits per-cycle features:
- $\tau_i$ (organism latency)
- $E_i$ (energy)
- $\Gamma_i$ (gating threshold)
- $A_i$ (architecture traits; e.g. `module_count`, `prediction_horizon`, `arbitration_frequency`)
- $R_i$ (resource intake proxy)
- $S_i$ (survival flag)

### Layer 2 — Species Aggregation
A central accumulator updates $M_s$ using survivor-conditioned samples, with optional:
- smoothing ($\alpha$)
- noise injection (for stress testing)
- compression / dropout of channels (for ablation)

### Layer 3 — Offspring Distribution
On reproduction, children inherit defaults from $M_s$ (then mutate locally).

---

## Species Memory: Forbidden Knowledge Constraints (Non-Negotiable)

Species Memory ($M_s$) exists to accelerate selection without replacing cognition.

Core principle:
$$M_s \not\Rightarrow \text{Action}$$
Only:
$$M_s \Rightarrow \text{Parameter Bias}$$

### 1) $M_s$ must not learn policies

Forbidden:
- state→action mappings
- control flow
- executable scripts / decision trees

Formal constraint:
$$M_s \cap \Pi = \emptyset$$
where $\Pi$ is the set of executable policies.

Enforcement:
- $M_s$ outputs only scalar parameter fields (no discrete conditionals)
- no branching logic or executable representations in memory state

### 2) $M_s$ must not store world models

Forbidden:
- predictive state-transition models
- causal chains and forward simulation operators

Formal constraint:
$$M_s \not\approx \hat{S}_{t+1}$$
Species Memory cannot represent or predict future states.

Enforcement:
- no temporal sequence storage for behavior
- compression operator $\phi$ is lossy and must not preserve temporal order

### 3) $M_s$ must not encode goals or utilities

Forbidden:
- reward/utility functions
- optimization targets
- preferences or explicit “better” directions

Formal constraint:
$$M_s \not\supset U$$
where $U$ denotes any utility/reward function.

Enforcement:
- memory stores correlations/statistics, not objectives
- no gradients, maximization, or explicit improvement direction

### 4) $M_s$ must not override organism failure

Forbidden:
- preventing death or reversing collapse
- injecting energy/structure/time
- mid-cycle intervention

Formal constraint:
$$\frac{\partial\,\text{survival}}{\partial M_s}=0\quad(\text{directly})$$
$M_s$ may only act indirectly by biasing inherited defaults at spawn.

Enforcement:
- $M_s$ is read-only during lifecycle/cycle
- $M_s$ can be consulted only at spawn/init (offspring defaults)

### 5) $M_s$ must not collapse individual diversity

Forbidden:
- convergence to a single phenotype template
- broadcasting a fixed “best configuration”

Formal constraint:
$$\mathrm{Var}(\theta_{\text{offspring}}) > 0$$

Enforcement:
- $M_s$ biases distributions; it must not hard-fix parameters
- mutation/noise must remain non-zero (entropy floor)

### 6) $M_s$ must not learn fast

Forbidden:
- rapid updates that respond at cycle-timescale
- shock-driven overwrites that behave like cognition

Formal constraint:
$$\tau_{M_s} \gg \tau_{\text{organism}}$$

Enforcement:
- update only at generation/reproduction aggregation boundaries
- low learning rate ($\alpha$) and moving-average style updates only

### 7) $M_s$ must not become mandatory

Forbidden:
- organism viability requiring $M_s$
- tight coupling where disabling memory breaks the system

Formal constraint:
$$\exists\ \text{viable organisms}\ \mid\ M_s = \emptyset$$

Enforcement:
- $M_s$ must be removable (performance may degrade, viability must remain)

### Positive definition (allowed)

$M_s$ may only learn survivor-conditioned statistics of heritable parameters:
$$M_s(t) = \mathbb{E}[\phi(\theta)\mid \text{survival}]$$
where $\phi$ is compressive, lossy, and non-executable.

## Phase-9.1 Experimental Regime (Failure Mode Suite)

Phase-9.1 evaluates failure modes of Species Memory using controlled experiments.

### Fixed-Size Selection Policy (Top-Up ON)

Phase-9.1 experiments operate with **Top-Up ON**:
- population size is maintained at a fixed target
- reproduction is conditional (must be affordable / viable)
- if population dips, new organisms are instantiated from the current environment identity to restore sample size

This regime must not be mixed with strict extinction runs.

### Interpretation Under Top-Up ON

Under Top-Up ON:
- **survival rate is interpreted as trait viability under competitive pressure**, not ecosystem persistence
- metrics estimate **selection gradients** rather than demographic collapse
- $M_s(t)$ remains well-sampled across long horizons (reduces early-termination path dependence)

### Harsh Ecology Regime (Top-Up OFF) — Deferred

Top-Up OFF is reserved for later phases as a distinct regime focused on ecological resilience and true extinction dynamics.

---

## Phase-9.1 Failure Modes (Expected)

### 1. Over-Specialization
$M_s$ collapses toward a narrow phenotype that performs well in one regime but fails elsewhere.

### 2. Under-Adaptation
Low $\alpha$ produces memory lag when the environment switches, causing persistent mismatch.

### 3. Noise Drift
Small population sizes and/or injected noise corrupt $M_s$, creating spurious correlations.

### 4. Compression Loss
Dropping channels (cost, latency, gating, architecture) produces degraded adaptation or miscalibration.

### 5. Bias Amplification
Memory updates reinforce majority phenotypes, reducing diversity (entropy collapse).

### 6. Hysteresis Lock
Once converged, memory resists change even after environment shifts.

---

## Phase-9 Success Criteria

Phase-9 is successful if:
- $M_s$ converges to stable priors under stable environments
- $M_s$ adapts to regime shifts without catastrophic lag
- ablations reveal meaningful performance degradation (i.e. memory channels matter)
- failure modes can be induced and diagnosed (not hidden)
- offspring inherit beneficial priors without runaway collapse

---

## Boundary Conditions

Phase-9 does not require:
- explicit communication between organisms
- cooperation or deception
- explicit combat

Those remain deferred to later phases.
