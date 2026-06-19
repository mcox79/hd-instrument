# Pre-reg: P(q) high-resolution histogram (Strategy 10:16 v152 add-3)

Two-level peak detection on 200-seed P(q): outer histogram (50 bins) for coarse peaks, fine histogram (500 bins) for sub-structure. Test if 15 outer x ~2 sub = 28 endpoint cardinality. N=16384.

## Verdicts
- `PQ_HIERARCHICAL_28` — n_total_peaks in [24, 32] (matches endpoint cardinality).
- `PQ_FLAT_15` — n_total ~= n_outer in [12, 18] (no hierarchy).
- `PQ_OTHER_CARDINALITY` — different total.
