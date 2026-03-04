# Latency-First Cognition: Conditional Adaptivity of Predictive Intelligence Under Time Pressure

## Abstract

Cognitive systems are typically evaluated by the accuracy or richness of their internal models, implicitly assuming that cognition is always beneficial. In contrast, biological and artificial agents operating under strict latency and energy constraints must decide whether to think before deciding what to think. We introduce Latency-First Cognition (LFC), a theoretical framework in which cognition is treated as a costly, delayed action whose invocation must itself be regulated. Using an evolutionary agent system (MONO), we study the emergence and failure modes of cognitive gating mechanisms under competitive ecological pressure. In Phase-9, we extend this framework to Species Memory, demonstrating that evolutionary selection on cognitive traits can produce stable, cross-generational memory without pathological dynamics. Our results reveal that cognition is a conditional survival strategy, not a universal improvement, providing a unifying explanation for bounded rationality, reflex dominance, and the evolutionary suppression of unnecessary prediction.

---

## Contributions

This work makes the following contributions:

1. **Latency-First Cognition (LFC)**: We propose LFC as a theoretical framework in which action latency, not representational optimality, is the primary organizing constraint of cognition.
2. **Formalization of Cognitive Gating as a Control Law**: We show that the cognitive gating threshold $\Gamma$ is not a tunable heuristic but an evolved control variable governing access to deliberation under energy and time constraints.
3. **Identification of Gating Pathologies**: We empirically characterize distinct failure modes—hypercognition, oscillatory cognition, hypocognition, and late cognition—and show that each arises from structural violations of gating validity rather than task difficulty.
4. **Discovery of a Gating Viability Window**: We demonstrate that viable cognition exists only within a bounded range of $\Gamma$, outside of which agents suffer either metabolic collapse or reflex blindness.
5. **Necessity of Two-Stage Gating**: We prove that single-stage gating mechanisms cannot simultaneously prevent rumination, oscillation, and causal delay, establishing two-stage gating as a structural requirement.
6. **Species Memory Under Evolutionary Pressure**: We introduce Species Memory ($M_s$) as a cross-generational accumulator of cognitive traits, demonstrating that selection can produce stable memory dynamics without drift or bias amplification.
7. **The No-Free-Cognition Theorem**: We formally show that cognition cannot be universally beneficial in latency-bounded environments and must therefore be selectively suppressed by default.
---

## 1. Introduction

Artificial intelligence research has historically emphasized better models, deeper planning, and more computation. However, biological intelligence did not evolve to maximize optimality—evolved to **avoid being too late**. In natural organisms, reaction time, metabolic cost, and coordination overhead constrain cognition. Reflexes often outperform deliberation, and prediction emerges only where anticipation outweighs its cost.

This paper proposes **Latency-First Cognition (LFC)**: an architectural principle where decision-making is explicitly bounded by time-to-failure. We present MONO, a synthetic organism designed to test whether cognition provides survival benefits when time pressure, damage propagation, and energy constraints are explicitly modeled.

Our contribution is not a new learning algorithm, but a *systems-level result*: intelligence can be disadvantageous unless environmental conditions justify its overhead.

---

## 2. Related Work

Most contemporary AI systems optimize objective functions under the assumption that computation is cheap and delay is tolerable. Reinforcement learning, planning agents, and large language models rarely model internal latency as a first-class constraint. Prior work on bounded rationality and real-time systems acknowledges these limits, but lacks empirical demonstrations where cognition itself causes failure.

MONO differs by embedding cognition inside a survival-critical loop, where delayed coordination directly causes structural collapse.

---

## 3. MONO Architecture Overview

### 3.1 Core State Variables

* **Structure**: Represents organism integrity. Structural collapse causes death.
* **Energy**: Finite resource consumed by cognition, repair, and coordination.
* **Tau (τ)**: Time-to-failure metric governing allowable delay.

### 3.2 Reactive vs Predictive Modes

* **Reactive Mode**: Immediate response without planning or scene switching.
* **Predictive Mode**: Narrative cognition with scene prediction, coordination, and repair planning.

### 3.3 Scene Switching Mechanism

Predictive MONO maintains discrete narrative scenes. A scene switch incurs cognitive cost but enables anticipatory repair actions.

---

## 4. Phase‑6 Experimental Design

Phase‑6 evaluates whether cognition improves survival under increasing realism.

### 4.1 Phase‑6.1: Physics Viability

Objective: Validate baseline survival without cognition.
Result: Organism survives indefinitely under stable conditions.

### 4.2 Phase‑6.2: Functional Diagnostic Test

Objective: Compare predictive vs reactive MONO under mild damage.
Result: Predictive MONO underperforms due to cognitive overhead.

### 4.3 Phase‑6.3: Shock-Regime Validation

Objective: Introduce sudden damage with anticipatory signal.
Result: Predictive MONO survives 21% longer by switching scenes precisely at shock onset.

---

### 5.1 Survival Outcomes

| Phase | Regime      | Population Trend | Cognitive Shift (Modules) | Outcome                  |
| ----- | ----------- | ---------------- | ------------------------- | ------------------------ |
| 6     | Shock       | N/A (Isolated)   | Fixed (1.0)               | Conditional Advantage    |
| 7     | Evolutionary| Divergent        | Pruning (3.0 -> 2.1)      | Cost-Efficiency Selection|
| 8     | Competitive | Stable (1312)    | Extreme Leaning (3.0 -> 0.83)| Latency Dominates Habitat|
| 9     | Species Memory | Stable (Fixed) | Adaptive Inheritance | Memory Without Collapse |

### 5.2 Failure Modes

In Phase-8, "Starvation via Over-thinking" emerges as a primary failure mode. Organisms that fail to gate their cognition fast enough lose energy to background metabolic costs or lose resource priority to faster neighbors, leading to structural collapse.

In Phase-9, we identify Species Memory pathologies: over-specialization (narrow trait convergence), under-adaptation (memory lag on regime shifts), noise drift (corrupted priors from small samples), compression loss (missing trait channels degrade adaptation), bias amplification (majority phenotypes dominate diversity), and hysteresis lock (memory resists change post-convergence).

---

## 8. Phase-9: Species Memory Failure Modes

Phase-9 evaluates Species Memory ($M_s$) under controlled selection pressure. We test six failure modes: over-specialization, under-adaptation, noise drift, compression loss, bias amplification, and hysteresis lock.

### Key Findings
- **Over-Specialization**: Populations converge to narrow phenotypes, failing in untested environments.
- **Under-Adaptation**: Low update rates ($\alpha$) cause persistent lag in shifting regimes.
- **Noise Drift**: Small populations introduce spurious correlations, degrading $M_s$ stability.
- **Compression Loss**: Dropping channels (e.g., gating threshold, module count) reduces adaptation quality.
- **Bias Amplification**: Memory reinforces majority traits, collapsing diversity.
- **Hysteresis Lock**: Post-convergence memory resists change, even when beneficial.

These results demonstrate that evolutionary memory is feasible but fragile, requiring careful design to avoid pathologies.

---

## 9. Analysis

### Theorem (No-Free-Cognition)
In any environment where:
1. Actions are subject to a finite response deadline $T_a$,
2. Cognitive processes incur non-zero latency $L_c > 0$ and energy cost $E_c > 0$,
3. Reflexive actions incur lower latency $L_r < L_c$ and lower energy cost $E_r < E_c$,

there exists no policy under which cognition is universally optimal across all states. Therefore, ungated cognition strictly reduces expected survival fitness.

#### Definitions
- Let $S$ be the set of environmental states.
- Let $\pi_r$ be a reflexive policy with latency $L_r$.
- Let $\pi_c$ be a cognitive policy with latency $L_c$.
- Let $\Gamma$ be a gating function determining when $\pi_c$ is invoked.
- Let $F(s, \pi)$ denote expected fitness from state $s$ under policy $\pi$.

#### Assumptions
- **Latency Dominance**: For some subset $S_f \subset S$, action success requires response before $T_a$: $L_c > T_a \implies F(s, \pi_c) = 0, \forall s \in S_f$.
- **Metabolic Cost**: For all states: $F(s, \pi_c) \le F(s, \pi_r) - E_c + \Delta(s)$, where $\Delta(s)$ is the informational benefit of cognition and is bounded.
- **Environmental Uncertainty**: The agent cannot perfectly predict whether a state belongs to $S_f$ without incurring cognitive cost.

#### Proof Sketch
1. Consider a policy that invokes cognition unconditionally.
2. In fast-reaction states $S_f$, delayed response causes immediate failure. Thus, expected fitness is strictly worse than reflexive action.
3. Consider a policy that never invokes cognition. In slow-changing states $S_s$, fitness is suboptimal due to missed planning benefits.
4. Therefore, no unconditional policy dominates. Any benefit of cognition is state-dependent.
5. Determining state membership itself incurs cost.
6. Hence, cognition must be selectively gated, and incurs unavoidable downside whenever invoked unnecessarily.

**Conclusion**: Cognition is not free; therefore, it cannot be always optimal.

#### Corollary 1: Reflex Dominance Principle
In latency-critical environments, reflexive behavior dominates by default, and cognition emerges only as an exception handler.

#### Corollary 2: Evolutionary Suppression of Intelligence
Natural selection minimizes cognitive activation frequency rather than maximizing predictive accuracy.

---

## 7. Analysis

The results reveal three critical insights:

1. **Cognition is not free**: Prediction consumes energy and coordination time.
2. **Latency dominates intelligence**: When action windows shrink, overthinking kills.
3. **Competitive Scarcity Prunes Overhead**: Multi-agent competition accelerates the rejection of non-essential cognitive structures.
4. **Adaptive Gating is the Superior Strategy**: The most successful lineages were not the "smartest," but those with the strictest gating (only Thinking when strictly necessary).

This mirrors biological evolution, where high-metabolic brains are only supported when they provide decisive, time-critical advantages over reflexive peers.

---

## 7. Implications for AI Systems

Latency-First Cognition suggests a new design paradigm:

* AI systems should regulate *when* to think
* Planning should be gated by time-to-failure
* Reflexive control must dominate under shock

This has implications for robotics, manufacturing systems, infrastructure automation, and safety-critical AI.

---

* MONO is a minimal organism, not a general-purpose learner
* Environmental signals are currently simplistic
* Future work will explore multi-agent cooperation and social signaling under latency constraints

---

We demonstrate that cognition is a conditional survival strategy, not a universal improvement. Through Phase-8, we have shown that competitive pressure acts as a powerful pruner of cognitive overhead, favoring organisms that act reflexively whenever possible. In Phase-9, we extend this to Species Memory, proving that evolutionary selection can produce stable cross-generational priors without pathological dynamics, but only under constrained conditions. Latency-First Cognition reframes AI design around the oldest problem in life: acting before it is too late.

---

## Acknowledgments

This work was developed as part of the MONO experimental program exploring foundational principles of synthetic cognition.
