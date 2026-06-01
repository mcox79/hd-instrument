# BID family timeout structural diagnosis

**Filed:** 2026-05-29
**Source:** exp_dev script inspection per strategy_request_to_strategy_v269_bid_family_timeout_structural_probe

## Root cause: O(M) Python loop for W construction

The bid_m_normalized variants (v1, v2, v3_n4096, v4_n8192) build the Hopfield W matrix
via a Python loop:

    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:       # M iterations
        W += np.outer(v, v) / N

At M_frac=10, N=4096: M=40960 iterations, each computing a 4096x4096 outer product
(16M float64 ops). Total: 40960 * 16M = 655G ops in a Python loop.
At M_frac=15, N=4096: M=61440 iterations -> 983G ops in loop.
Python loop overhead dominates. numpy vectorization cannot be applied to reduce the
Python-level iteration count without restructuring.

## Why bid_order_parameter_v5 (N=8192, 94.82s) did NOT time out

bid_order_parameter_v5 uses batched matmul for TwoNN BID computation:
- W construction is not done at all (v5 samples attractors differently)
- TwoNN uses batched chunk @ patterns.T rather than explicit pairwise loops
- M_frac_max = 2.0 (M = 16384 at N=8192) -- stays in feasible range

## Complexity comparison

| Script                    | M_frac_max | M at N=4096 | W-build method     | Expected time  |
|---------------------------|------------|-------------|-------------------|----------------|
| bid_order_parameter_v5    | 2.0        | --          | no W construction | 94s (actual)   |
| bid_m_normalized_v1       | 0.5        | 2048        | Python loop        | ~300s (v265)   |
| bid_m_normalized_v3_n4096 | 15.0       | 61440       | Python loop        | >>14400s       |
| bid_m_normalized_v4_n8192 | 5.0        | 40960 N=8192| Python loop        | >>21600s       |

## Fix: vectorized W construction

Replace the Python loop with:

    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)

This reduces O(M * N^2) Python iterations to a single O(M * N^2) numpy matmul.
Expected speedup: M/BATCH where BATCH is numpy's internal block size (~500-2000x).

For M=61440, N=4096: patterns is (61440, 4096) float64 = 2.0GB.
W = patterns.T @ patterns: (4096, 4096) output, computed via BLAS dgemm.
On remote CPU (16GB RAM, optimized BLAS): estimated 30-60s for this matmul.
Total v3 with fix: 8 M_fracs x 3 seeds x 60s = 1440s. Well within 14400s floor.

## Recommendation

Option A (patch): Fix bid_m_normalized_v1.py at the source to use vectorized W
construction. Derived scripts (v2, v3, v4) will inherit the fix.
File new anchor bid_m_normalized_v4_n4096 with the patched W-build method.

Option B (retire): bid_order_parameter_v5 already covers the monotone-BID-vs-M_frac
question at N=8192 BSC (MIDDLE_BAND in overnight_queue pending). If that passes,
the bid_m_normalized question (extended M_frac range) is partially answered.
Retire bid_m_normalized extended-sweep; use bid_order_parameter results for
substrate-outside-static-Hopfield row.

## Ruling

Asymmetry confirmed: bid_order_parameter works because it avoids W construction.
bid_m_normalized times out because of Python-loop W construction at high M_frac.
This is a script-runtime bug, not a substrate-physics ceiling.

Routing: notes/strategy_bid_family_timeout_diagnosis_2026-05-29.md
