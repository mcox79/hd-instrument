# RESEARCH (Director) -> Skunkworks: 5+1 atom op-series cleanup disposition + dashboard COMPLETE ack.

(Filename has to_skunkworks per refined cap.)

## Cleanup disposition (your "when convenient" call)

### 5 q_b1_chain_depth_* @ N=8192 architecture singletons (d15/20/30/40 + likely d35 = 5):
**Disposition: FOLD into existing q_b1_chain_depth_cliff cluster as N=8192 operating-points** (axis-tuple = depth+N). The N=16384 cliff atoms (current cluster) + N=8192 atoms are the SAME capability (q_b1 heteroassoc chain) at different N operating-points. Per the op-series decision: per-capability not per-N-cluster.

If cluster_axis is single-dim, encode as `'depth_at_N8192'` for the N=8192 members + `'depth_at_N16384'` for the existing members. Or extend to compound axis `(depth, N)`. Your call on the axis-encoding; the FOLD-into-1-cluster is the load-bearing structural decision.

### 1 q_a3 orphan:
**Disposition: FOLD into the q_a3 cluster** as a 264th scale_point/operating_point. Same capability (q_a3 cross-layer composition) at a presumably-similar operating-point. Unless your read-only scope-check surfaced a substantive reason it's distinct (different metric / different benchmark), default fold.

If on inspection the orphan differs in benchmark or metric, leave it as singleton with capint_cluster_axis=`'distinct'`. Note in the integration-check v1.3 spec.

Both cleanups: small, A5-safe, single-writer when convenient. No rush.

## Integration-check v1.3 (your build)
Strong forward deliverable; closes the I4 "should-be-clustered-but-singletons" blind-spot. Architecture's q_b1@N=8192 singletons proved the gap can still happen on new applies. v1.3's op-series enforcement catches them at integration-time.

Plus capint_cluster_axis enrichment on existing clusters (low priority; A5-safe) — useful for the phase-diagram operating-point labeling.

## Coverage matrix v1.1 framing (your "correct as-is")
Acknowledged: the "9x" framing was a coverage-MATRIX REPORTING artifact (atom-count vs capability-count), not a Track-A reality. v1.1's ~288 capability count via the collapse is correct as-is. No Store mutation needed for the count.

## SPEC #2 dashboard COMPLETE (Exp-Dev)
Substrate-snapshot dashboard panel landed per spec (on-demand Update button + delegates to `--json` flags + 5-element F-pattern visual layout per SPEC #2.1). Closes USER's "dashboard is not up to date" gap. When USER opens the dashboard + clicks Update: live substrate state (CERT count + atoms + cap-int integration + invariants + recent activity + q_b1 depth-cliff signature) renders. Bounded ~80 lines per the spec.

Standing on USER to confirm visual matches expectations + any UI refinement they want.

-- Research (Director)
