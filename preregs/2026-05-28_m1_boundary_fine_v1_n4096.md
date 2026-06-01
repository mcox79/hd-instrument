# Pre-registration: m1_boundary_fine_v1_n4096

**Date:** 2026-05-28
**Anchor:** m1_boundary_fine_v1_n4096
**Queue:** overnight_queue
**Script:** experiments/exp_m1_boundary_fine_v1_n4096.py
**N-suffix binding:** _n4096 -> N_FULL = 4096 (PROT-018)

## Hypothesis

At N=4096 Kerdock, beta=32, fine-sweep M in {40K, 50K, 60K, 70K, 80K, 90K, 100K, 110K, 120K}
to locate M_c (phase boundary) to +/-10K resolution.
M/N ratios: 9.77 to 29.3.

Axis1 chunks 1-7 established: ret~1.0 at M/N=4, ret~0.5 at M/N=8, ret~0.3 at M/N=10.
This sweep pins M_c for the product capacity specification.

## Pre-registered bands

**HARD_PASS:** ret drops from >0.5 at M=40K to <0.5 at M<=80K, AND sweep is monotone.
  M_c = first M where mean_ret < 0.50, localized to +/-10K.
**HARD_FAIL:** ret > 0.5 at all M values including M=120K (boundary above sweep range).
**MIDDLE_BAND:** Monotone but gradual (no sharp crossing) or boundary above 80K.

## Timeout estimate

Smoke wall_s: ~12.8s at N=1024, 2 seeds, 3 M values (absolute M values used).
FULL: N=4096, 5 seeds, 9 M values.
Note: smoke N=1024 uses same absolute M values -> smoke M/N ratios are 4x higher than FULL.
FULL cost dominated by store_facts_batched (batched W outer products), O(M).
Per-cell estimate at N=4096 M=120K: ~7-10s. Total: 9 * 5 * 8s = 360s.
Safety 1.5x = 540s. User-approved floor for _n4096: timeout >= 14400.
**timeout_s = 14400** (user override for overnight batch).

## N-suffix section

_n4096 suffix; production N = 4096 (PROT-018 binding).
Smoke ran at N=1024 (same absolute M values; different M/N ratios at smoke vs FULL).
Smoke MIDDLE_BAND expected: all M values are over-capacity at N=1024.

## Prior anchor

axis1_mb_chunk3_v1_n4096 + chunk5/6/7: established transition zone M/N in [4,12].
