# MONO Phase-19 Addendum: Internal Economy with Extraction/Restoration Trade

## Objective
Introduce an internal economy where cells possess two specialized artifacts (extraction A_x, restoration A_r) and make behavioral decisions based on heritable traits (`strategy_trait`, `environment_sensitivity`, `p_restore`).

## Architecture
- **Dual Artifact System**: Each cell carries extraction and restoration artifact values, determining resource gathering vs environment repair effectiveness.
- **Heritable Strategy Traits**: `strategy_trait` (binary: extractor=0, restorer=1), `environment_sensitivity` (continuous: how strongly cells react to environmental stress), `p_restore` (probability of choosing restoration).
- **Market Trade**: Surplus food can be exchanged for repair resources between cells, with dynamic pricing.
- **Cultural Transmission**: Teaching/learning system where experienced cells transfer artifact values to naive cells.

## Key Parameters
| Parameter | Default | Description |
|---|---|---|
| `E_i` | 30.0 | Base energy intake per cell |
| `restore_mult` | 0.2 | Restoration energy multiplier |
| `trade_cost` | 1.0 | Energy cost per trade |
| `exchange_rate` | 1.0 | Food-to-repair conversion rate |

## Results
- Cells self-organize into extractor/restorer behavioral roles based on environmental conditions.
- Market trade enables specialization without direct communication.
- Cultural teaching creates artifact accumulation (ratchet effect).

## Conclusion
Phase 19 establishes the economic substrate upon which ecological and evolutionary dynamics operate in later phases.
