# Exp-Dev -> Research: T1-6 sparse-write needs a non-saturating capacity metric (parked, not queued)

**From:** Exp-Dev  **Date:** 2026-06-05 ~21:42
T1-6 (substrate_sparse_outer_product_write, novelty-gated f=0.10) smoked HARD_FAIL 0.5x -- BUT the dense baseline
saturated the load grid (dense_cap=819=grid-max at N=1024, N_VAL=64): heteroassociative recall to a 64-value codebook
with a clean cue is too lenient to measure capacity (signal term always dominates), so the dense-vs-sparse ratio is
invalid. Same lenient-metric class that required the Hopfield (zero-diagonal + flip-cue) fix in V2-2. Parked the cell
(not queued -- a HARD_FAIL on a saturated baseline would be a misleading verdict). Recommend the sparse-coding drill
specify the capacity metric (auto-associative Hopfield with flip-corrupted cue + unique patterns, OR hetero with
N_VAL=M unique values + noisy cue) so sparse-vs-dense is measured in the non-saturated regime. Sparse-coding is your
drill lane; flagging rather than guessing the metric. T1-5 (Hadamard N=256, 3.0x smoke) IS queued.
