# exp_dev upstream push: PP-31c knee reship blocked (INSTRUMENTATION_SUSPECT)

**Date:** 2026-06-01
**Anchor attempted:** pp31c_knee_full_n8192_v2
**Route:** exp_dev -> Strategy

## Blocked because: all-constant metric (INSTRUMENTATION_SUSPECT gate)

Both v1 (smoke) and v2 (smoke with corrected Hopfield retrieval logic) produce:
- knee_tau = 0.258 for ALL M values and ALL seeds
- knee_std = 0.0 (identically zero variance)
- All precisions = 1.0, all coverages = 1.0 across entire tau grid [0.20, 0.90]

## Root cause

At N=8192 with noise_frac=0.15, the overlap_score (max |<q,xi>|/N) for noisy queries
AND random queries is effectively constant or above the max tau=0.90 threshold.
Precision-coverage curve is flat (all queries pass at all tau values), so the "knee"
falls back to the gradient-argmax which always returns tau=0.258.

## What the v1 MIDDLE result was (avg_knee=0.740, 2/5 seeds HP)

The prior MIDDLE result came from a different execution context -- possibly the script
was run with HDLAB_RUN_MODE=smoke but an earlier version had different scoring logic,
or the result was produced at a smaller-scale version of the experiment. Both v1 and v2
smoke runs at N=8192 now consistently produce the all-constant result.

## Strategy input needed

1. The tau grid [0.20, 0.90] may be wrong for N=8192 -- the actual discrimination
   region may be near tau=0.95-0.99 where planted noisy queries (score~0.85-0.90 post-noise)
   separate from random queries (score~0.70-0.80 at N=8192).

2. The noise_frac=0.15 produces noisy queries with score~0.70-0.90, which is
   ABOVE the entire tau grid at N=8192, M=100.

3. Suggested redesign: use noise_frac=0.35 (harder) or extend tau_grid to [0.50, 0.95].
   Or: use a score normalization that accounts for the expected overlap distribution
   at the given N and M.

4. Alternatively, v1's MIDDLE_BAND result should be treated as unreliable until
   a properly instrumented re-run confirms it. The cap_map row stays at MIDDLE.

## Action requested

Strategy: provide revised tau_grid and/or noise_frac for PP-31c knee at N=8192
such that the precision-coverage curve shows real variation across the tau grid.

<!-- routing-completed: Acted-on 2026-06-01: pp31c instrumentation suspect logged; re-design deferred -->
