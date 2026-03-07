# MONO Phase-28 Specification: Spatial Ecosystems

## Objective
To evolve the MONO ecosystem from a single population pool into a **Spatial Ecosystem**. By restricting gene flow through geographical limits, we expect to observe localized adaptation, strategy clustering, and the first emergence of distinct biological proto-species.

## Architectural Additions

### 1. Spatial Grid & Two-Layer Environment
The environment will be a `50 x 50` 2D grid. Each tile independently maintains its own ecological state using a two-layer model:
*   `env_quality`: The local climate/damage state.
*   `resource_pool`: The harvestable energy bank.
*   **Regeneration Rule:** `resource_pool += regen_rate * env_quality`. (This allows damaged environments to recover slowly instead of collapsing permanently).

### 2. Tile Density Limits
To create territorial and migration pressure (like real spatial ecosystems), each tile has a maximum capacity:
*   `MAX_CELLS_PER_TILE = 10`
*   If a cell reproduces on a full tile, the offspring spills into a neighboring tile.

### 3. Asynchronous Cell Updates
To eliminate update bias (where cells processed earlier in the array dominate resources), the engine will shuffle the population every generation before acting:
`shuffled_cells = random.shuffle(all_cells)` -> `for cell in shuffled_cells: act()`

### 4. Local Interaction (Radius 1)
Cells only interact, compete, and reproduce within a Moore neighborhood of `radius = 1`. This strong local structure is crucial to suppress gene flow and encourage speciation.
* **Local Teaching Bias:** Cells only learn horizontally from neighbors within this radius. This forces cultural clustering on top of genetic clustering.

### 5. Migration
Cells have a base probability of moving to an adjacent tile to explore.
*   **Migration Rate:** `0.02` (2% chance per generation for a cell to diffuse `dx=random(-1,1), dy=random(-1,1)`).

## Expected Scientific Outcomes
When Phase-28 operates as intended, we should observe:
1.  **Spatial Clusters:**
    -   Restorers dominating damaged regions out of necessity.
    -   Extractors dominating rich regions out of opportunity.
2.  **Lineage Divergence:**
    -   Genetics separating geographically into localized sub-populations.
3.  **Proto-Species:**
    -   Distinct, isolated evolutionary groups emerging, driven by the geography of their environment rather than uniform, global selective pressure. This is the foundational prerequisite for true biodiversity.
