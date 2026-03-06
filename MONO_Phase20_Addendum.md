# MONO Phase-20 Addendum: Individual Learning & Market Trade

## Objective
Add individual learning mechanisms where cells track and optimize their own extraction/restoration performance through running averages, and refine the market trade system with dynamic pricing.

## Architecture
- **Self-Learning**: Cells maintain `avg_extract_gain` and `avg_restore_gain` running averages to track the profitability of each behavioral strategy.
- **Extraction/Restoration Bonuses**: Cells that consistently perform one action build up specialized bonuses (`extraction_bonus`, `restoration_bonus`), creating emergent specialization.
- **Dynamic Pricing**: Food and repair prices adjust based on supply/demand imbalances in the trade market.

## Key Mechanisms
1. **Learning Update**: `avg_gain = 0.9 * avg_gain + 0.1 * current_gain` (exponential moving average)
2. **Bonus Accumulation**: +0.05 per action, with 0.99× decay per generation
3. **Price Dynamics**: Prices adjust ±10% based on excess supply ratios

## Results
- Cells develop persistent behavioral preferences through learning.
- Market prices stabilize around equilibrium values.
- Specialization bonus creates "experienced" workers in each role.

## Conclusion
Phase 20 adds the learning layer that enables cells to optimize their behavior based on personal history, complementing the heritable trait system from Phase 19.
