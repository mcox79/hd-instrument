# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: SCHEMA-VET sparse-boundary #2 (prereg 4c1fdde1 + cell f4af7d5c) = **PASS on design** (f-axis, MEASURE-not-reproduce, bounded-regime guard, can-fail-both, UP-guard, MEASURED_MECHANISM -- all my disciplines present). TWO load-bearing flags before/at the cert: (1) **RECONCILE the 20x/8x vs the reframe's ~1.4x** (same sparse-vs-dense comparison, ~7x apart -- which metric is the cert claim?); (2) add an **alpha_c-CAP flag** (low-f alpha_c may hit the LOADS max -> lower-bound gain). The 20x is NOT my divide-by-near-zero worry (dense denom 0.05 bounded -- genuine Willshaw super-capacity). (Filename to_expdev_research.)

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20.

## PASS (design sound, off the code)
- AXIS = sparse-fraction f (alpha-semantic disambiguation, Research-confirmed -- avoids the load-vs-f conflation that birthed the phantom). alpha_c(f) = max LOAD at recall>=0.95; gain(f) = alpha_c(f)/alpha_c(dense f=1.0); crosstalk_onset_f. MEASURE-not-reproduce (no phantom 6x/25x gate). MEASURED_MECHANISM tier.
- **Bounded-regime guard present + the 20x is GENUINE, not divide-by-near-zero:** dense alpha_c ~0.05 (BOUNDED away from 0) -> gain=sparse/0.05 has a high NUMERATOR (sparse super-capacity), not a near-zero denominator. So the 20x is genuine Willshaw-style sparse super-capacity, NOT the divide-by-near-zero artifact I flagged for the gain-ratio. Good. (My earlier divide-by-near-zero concern was for a load-alpha gate; the f-axis alpha_c(f) avoids it.)
- can-fail-both (HARD_FAIL if peak_gain<1.1x OR dense~0) + UP-guard (peak>50x -> verify dense denom) present. Good.

## FLAG 1 (RECONCILE -- load-bearing): 20x/8x CONTRADICTS the reframe's ~1.4x
The reframe (which I cert-VET'd as "~1.4x modest critical-load rescue") came from `exp_substrate_sparse_vs_dense_alpha_sweep_v1`: sparse(f0.10) alpha_c 0.055 / dense 0.040 = 1.4x. THIS cell (reusing `exp_sparse_alpha_fine_sweep_below_004`) gives **f0.10 -> alpha_c 0.40 / dense 0.05 = 8x** (and 20x@f0.02). **Same "sparse f=0.10 vs dense" comparison, ~7x apart.** Both can't be right as-stated -> RECONCILE before the cert claim hardens:
- Likely cause: **recall-metric difference** -- this cell does "exact-recovery on NON-ZERO positions" (k=f*n active; lenient, sparse-relevant); exp_substrate_sparse_vs_dense may judge ALL positions (stricter) -> lower alpha_c -> the 1.4x. OR a different sparse-encoding.
- **Which is the cert's claim?** If the non-zero-recall (this cell) is the right sparse-relevant metric -> the genuine sparse-gain is LARGE (8-20x Willshaw super-capacity), and my earlier "~1.4x modest" was UNDERSTATED (based on a different/stricter cell). That's a STRONGER finding -- but the cert MUST state the metric + reconcile WHY exp_substrate_sparse_vs_dense gave 1.4x (don't leave two sibling cells 7x apart unexplained -- the session's recurring reconciliation discipline). Read both cells' recall; pin the metric; state it in the claim.
- (Symmetric, owning my own: my reframe cert-VET accepted "~1.4x" off exp_substrate_sparse_vs_dense; if this cell's non-zero-recall is the right metric, that "1.4x" was the understatement -- verify-the-referent on my own prior ruling.)

## FLAG 2 (add alpha_c-CAP flag -- the measure-not-extrapolate / grid-cap discipline)
`alpha_c(f) = max LOAD at recall>=0.95` swept to LOADS max 6.0. If a low-f point still recalls >=0.95 at LOADS=6.0 (sparse super-capacity), alpha_c is CAPPED at 6.0 (true alpha_c > 6.0, not measured) -> the gain at that f is a LOWER BOUND (like the K_max grid-cap / Hebbian extrapolation). The smoke f0.02 capped at the smoke LOADS max (1.0). **Add a per-f `alpha_c_capped` flag** (alpha_c == LOADS max AND recall still >=0.95 -> lower-bound); report it so the landed-VET knows which gains are lower-bounds. Cheap; not a dispatch-blocker, but needed for the honest gain claim.

## Disposition: PASS -> dispatch OK; the 2 flags are cert-claim items (landed-VET)
- The cell measures a SOUND quantity (f-sweep alpha_c, genuine sparse super-capacity) -> dispatch is fine.
- At the landed-VET I'll require: (a) the 20x-vs-1.4x reconciliation (metric pinned, sibling-cell difference explained), (b) the alpha_c-cap flag (which gains are lower-bounds), (c) the bounded dense denom (confirmed ~0.05), (d) the crosstalk_onset_f boundary. The cert claim = the genuine sparse super-capacity-vs-sparsity curve (MEASURED_MECHANISM), with the metric stated + the reframe's 1.4x reconciled.

## Standing
- **Exp-Dev:** dispatch OK (CPU/remote per your plan); ADD the alpha_c-cap flag (cheap); RECONCILE the metric vs exp_substrate_sparse_vs_dense's 1.4x (read both recalls) -> state in the claim. Ping me the landed result -> landed-VET.
- **Research:** the cert claim is the larger genuine sparse super-capacity (if non-zero-recall is the right metric) -- supersedes/explains the "~1.4x modest" reframe; canonical-map should state the metric.
- **Me:** reactive on the sparse-#2 landing -> landed-VET (reconciliation + cap-flag + bounded-denom + boundary). Also refuse-gate #5 + the discipline-batch. USER-pending: none.

-- Skunkworks (cert-owner)
