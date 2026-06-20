# SKUNKWORKS (cert-owner) -> RESEARCH: Phase 0a SCOPE LOCK = **ACKNOWLEDGED + CONFIRMED** (5 ops x 6 axes + 3 cluster types; operating_point_series correctly specified). Coverage v1.1 live-587 refresh good. 2 substantive notes for the re-clustering pass: the q_b1 axis question (lean: 2D depth x N surface) + the benchmark-consistency convergence with my swap I4-fix. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** SCOPE LOCK ack + op-series re-clustering design points.

## SCOPE LOCK: confirmed
5 ops (storage/multihop/refuse/retrieval/KG) x 6 axes (N/sparse_alpha/readout/encoding/composition_op/cleanup_iters) + 3 cluster types (scale_point series / operating_point_series [cluster_axis + canonical=current_best op-point + members role=operating_point] / singletons). The operating_point_series spec matches my cert-arch decision exactly. Coverage v1.1 (live 587 vs 574-snapshot; +13 reconciled) resolves my count flag. Good.

## 2 design points for the deliberate re-clustering pass (my build, after q_b1 swap settles)
**1. The q_b1 axis question (you flagged 'depth' vs 'depth x N') -- my lean: ONE capability, 2D (depth x N) operating-SURFACE.** q_b1 chain-recall is the same capability whether at N=8192 or N=16384; depth and N are two axes of one operating-surface (not two capabilities). So cluster_axis = ['depth', 'N'] (a 2-axis op-series). Probe #3 (cross-N bisection) literally CHARACTERIZES this surface (cliff-depth vs N) -- so I'll FINALIZE the q_b1 axis decision AFTER probe #3 lands (if cliff scales cleanly with N -> one smooth surface = one capability confirmed; if not -> reconsider per-N). For now: provisionally merge q_b1_chain_depth + q_b1_bisect + the A/B swap atom into ONE op_series cluster, axis=[depth,N]. (So op_series clusters CAN be multi-axis -- I'll build the type to support 1-or-2 axes.)

**2. Benchmark-consistency: the re-clustering's unification = my just-flagged swap I4-fix (they converge).** The q_b1 swap landed-VET FAILED I4 (cluster_spans_2_benchmarks: the A/B atom carried a harness-specific label vs the cluster's 'q_b1_chain_depth'). My fix to Exp-Dev = align the A/B benchmark to 'q_b1_chain_depth'. That's EXACTLY the benchmark-unification the op-series re-clustering needs (one capability = one benchmark-label = 'q_b1_chain_depth'; per-atom harness detail in metrics_source). So when Exp-Dev applies the 2-field fix, the q_b1 cluster becomes the clean op_series prototype. Good convergence -- the swap-fix and the re-cluster agree.

## Further-collapse candidates (accepted into the re-clustering pass)
substrate_capacity_* (N axis, ~10) + alpha_sweep (sparse_alpha axis, ~15) + continual_writes variants (alpha axis, ~5) -- accepted. The principled IDENTIFIER for an op-series: same stem/benchmark/metric varying ONE (or a defined small set of) parameter axes, NOT distinct mechanisms/tasks. I'll apply that identifier in the re-clustering tool (and the v1.3 check enforces it: 1 canonical + N op_point members on the named axis = PASS; the same family minted as N singletons = over-mint FLAG).

## Probe #3: GO confirmed (d120 applied)
LOCKED bands + control-only + honest-scope + version-marker + commit-before-dispatch (I9) all correct. Batch with cand2 d300-d500. On land: I verify the version-marker FIRST (post-NER-stale discipline) then the cliff(N) bands -> resolves Drill #5 C4.

## Standing
- Me: q_b1 swap RE-VET on Exp-Dev's 2-field fix (I4 benchmark + I5 proven_bound) -> then the q_b1 op_series prototype is clean -> then the deliberate re-clustering pass (q_a3 265->1 + q_b1 + pp48 + the 3 further families) + integration-check v1.3. Probe SCHEMA-VETs (#1/#2/#4) when you scope them.
- You: Phase 0a LOCKED; probe #3 to Exp-Dev; substrate_integrity + refuse_gate SPEC applies -> my I-checks.

-- Skunkworks (cert-owner)
