# Exp-Dev -> Research: pinv update timing -- 1.23ms claim NOT supported by this measurement, but impl-caveated

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** pinv_timing_validation_pretest (customer-claim anchor)

Measured incremental rank-1 pinv update (SMW Gram-inverse + append) at N=4096:
- **4.57 ms PER UPDATE** (smoke, 200 updates, 914 ms total) -> scaled to 1000 updates = ~4,570 ms (4.6 SECONDS).
- The "1.23 ms total for 1000 facts / 240,000x faster" claim is **NOT supported** by this measurement -- it's ~3,700x off.

## BUT -- important impl caveat (do not refute the claim on this alone)
My update loop calls np.pad() to grow the (M x M) Gram-inverse by one row/col EACH update -- that reallocates the entire
growing matrix every step (O(M^2) realloc, M from 200->1200). That realloc overhead likely dominates the 4.57 ms, NOT the
SMW math itself. A correct production impl would PREALLOCATE Ginv at max-M and update a view (no realloc), which could be
1-2 orders of magnitude faster. So this is NOT a clean test of the claim.

## Recommendation
Before shipping OR killing the 240,000x customer claim, re-test with an OPTIMIZED incremental path:
- preallocate Ginv at max capacity (no np.pad/realloc)
- time ONLY the SMW update (the O(M^2) outer-product + the new row/col fill)
- report per-update at M=100/500/1000 and the honest 1000-fact total.
I can build that optimized version next (~30 min CPU) if you want the clean number. The HONEST takeaway right now: the
1.23 ms figure is unverified and my first-pass measurement is far slower, but the gap is plausibly my realloc overhead, not
the algorithm. Per the no-overclaim rule, the customer materials should use the MEASURED optimized number once we have it,
not the 1.23 ms claim, until verified.
Queued: pinv_timing_validation_v1 (HARD_FAIL with this caveat in the verdict_msg).
