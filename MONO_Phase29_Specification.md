# MONO Phase 29 Specification: The Sandbox Playground & Co-Evolution

## 1. Executive Summary
Phase 29 represents the fundamental inflection point where MONO transitions from a closed-loop Python simulation into an **Evolving Intelligence Platform**. We are lifting the biological rules proven in Phases 1-28 (Metabolism, Sensing, Selection, Species Memory, Speciation, Resilience) and applying them to **Real-World Agent Tasks**.

The new architecture operates as a **Sandbox Chatbot Playground** where individual "Instances" (chatbots/agents) are spawned to handle user queries. They live, breathe (consume energy), hear (process queries and environment), act (execute tasks), and die—depositing their successes and failures into a global **Species Memory** that guides the next generation of spawned agents.

Simultaneously, we will inject **Red Queen Dynamics** (Predator Co-Evolution) into this playground, forcing the agents to continuously adapt their strategies to survive hostile system pressures, rather than simply solving static environment puzzles.

## 2. The Sandbox Architecture

The Playground consists of a real-time visual dashboard and a user interaction layer attached to a pool of active MONO Instances.

### 2.1 The Instance Lifecycle
1. **Birth/Incubation:** A new instance (chatbot agent) is spawned. It initializes with a set energy quota and inherits the current best practices from the Species Memory DB.
2. **Breathing (Energy Flow):** The instance has an internal metabolic burn. It costs energy simply to exist, and executing complex reasoning or calling tools costs spikes of energy.
3. **Hearing (Sensing):** The instance listens to the environment. This includes User Messages (tasks), but also signals from Predators (system constraints/hostile processes) and other Peer instances.
4. **Action (Execution):** The instance attempts to satisfy the user query, evade predators, and harvest resources (success tokens).
5. **Outcome Observation:** The system evaluates the action. Did the task succeed? Was it energy-efficient? Was the latency acceptable?
6. **Species Memory Update:** The instance's performance is graded. Successful heuristic patterns are reinforced and permanently stored in the DB. Failing strategies are pruned.
7. **Death/Reincubation:** When energy depletes (or the instance reaches its 'Age' limit), it dies. Its local memory is wiped, but its extracted 'Lessons' have already been saved to Species Memory. A new instance is immediately spawned, possessing the upgraded Species Memory.

### 2.2 Red Queen Dynamics (Predator/Prey)
To prevent the Chatbot Instances from simply finding one "good enough" conversational strategy and stagnating (as seen before Phase 28.1), they will be hunted by **Predator Processes**.
- **The Prey (The Chatbot):** Trying to answer queries quickly and accurately to gain Energy.
- **The Predator (System Stressor):** An antagonistic process designed to steal the Chatbot's energy, interrupt its reasoning, or mutate the user's queries to confuse it.
- **The Arms Race:** The Chatbot must evolve better contextual parsing (evasion/camouflage) and faster execution (speed) to answer the user before the Predator consumes its energy. The Predator, in turn, evolves to become more aggressive if the Chatbots become too efficient.

## 3. Implementation Plan

**Step 1: The Playground UI (Dashboard)**
* Build a web interface (HTML/JS) featuring a Chat Window (for the user) alongside a visual "Dashboard" tracking the active Instance Pool, their Energy levels, and the current state of the global Species Memory.

**Step 2: The Core Loop (Backend)**
* Implement the Instance Lifecycle Manager in Python. This orchestrates the spawning of agent loops, managing their energy depletion per token/action, and enforcing the Death/Reincubation cycle.

**Step 3: Species Memory DB**
* Create a persistent layer (e.g., JSON or SQLite) that stores prompt heuristics, successful action-chains, and temperature/parameter genes that undergo crossover and mutation across generations.

**Step 4: The Predator Injection**
* Introduce the single Predator Class. Define its Movement (how it targets chatbots), its Energy Model (stealing from chatbots), and its Reproduction (spawning more aggressive predators if successful).
