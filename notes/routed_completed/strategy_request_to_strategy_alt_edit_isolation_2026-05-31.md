# Strategy request: alt-edit-isolation drill v1 (M1+M2 log-structured store recommended)

## Trigger: research drill 2026-05-31 (origin: v290 R-COW-INFEASIBILITY R3 + routing file `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md`)

## Finding (one paragraph)

The COW failure mode (mem-amp 10.13x, throughput 6-7.5/s; U3 HARD_FAIL) is structural: copying a full N x N matrix per rank-1 edit is asymptotically wasteful when the edit itself spans 2N floats. Three parallel Sonnet lit-scan subagents drilled four candidate architectures. **The recommended substrate-deployable mechanism is a log-structured rank-1 store (delta-encoding + LSM lazy-replay, the same family viewed from write-path and read-path perspectives).** Mem-amp formula 1 + 2K/N gives 2.0x at K=M and 3.0x at K=N (under the 4x target). Throughput projection 8-12K q/s GPU (orders above 50/s target). **Key architectural win: the edit log IS the audit log by construction, providing KF-2 deletion-cert compatibility for free.** Joint P_deflated 0.40-0.50 that all three targets (mem-amp, throughput, consistency >= 0.95) are met within a 7-day engineering budget. Load-bearing empirical risk: floating-point drift over K rank-1 corrections at depth=5; known engineering mitigation is Kahan compensated summation; cheap smoke gates the risk. A secondary M3+M4 CRDT+LSH-hybrid path (P_deflated 0.35) is available as a fallback if the FP-drift gate fails to close. CRDT-alone is rejected as standalone (depth>=2 retrieval breaks eventual-consistency semantics) but reused as the audit-log primitive in both paths.

## Recommended action

1. **Cap_map annotation (annotation-only, no row state change).** Append to v290 R-COW-INFEASIBILITY block: "Research drill 2026-05-31 (`notes/research_alt_edit_isolation_v1_2026-05-31.md`) identifies log-structured rank-1 store (M1+M2 unified) as PRIMARY substrate-deployable alternative; P_deflated 0.40-0.50 for production-feasible cost profile in 7-day engineering budget; M2 smoke recommended. M3+M4 CRDT+LSH hybrid SECONDARY (P_deflated 0.35); CRDT-alone REJECTED as standalone (depth>=2 retrieval incompatible with eventual-consistency)."

2. **Experiment dispatch (M2 log-structured retrieval smoke).** Cost-cheap (~30 min CPU laptop). Tests cosine(q_lazy, q_materialized) >= 0.9999 across K in {64, 256, 1024, 2048} at N=512, d=5. Falsifiable predictions (HARD-PASS / HARD-FAIL / MIDDLE-BAND) pre-registered in `notes/research_alt_edit_isolation_v1_2026-05-31.md` PART D. The audit-by-construction synergy means a PASS unlocks both U3 rehab AND KF-2 deletion-cert co-engineering. **Suggest queueing AFTER current G5/G6 modern-Hopfield batch lands (no priority conflict; this is engineering not theory).** Orchestrator decides timing per pause-flag state.

3. **Cross-application probe (research-side, not exp_dev).** Note in cap_map that Path D's per-hop Bayesian independence (T2 HARD_PASS 45/45 cells) is the substrate-native generalization of CRDT-style per-op independence at the retrieval layer; M1+M2 generalizes this same mechanism to the W-mutation layer. This is an explanatory bridge between two cap_map rows that previously appeared independent.

## Confidence

P_deflated 0.40-0.50 (M1+M2 hits all three production targets in 7-day engineering budget; range reflects naive-replay vs batch-merge variants and Kahan-summation contingency).
P_deflated 0.30-0.35 for M3+M4 hybrid fallback.
P_deflated 0.25 for CRDT-alone (not recommended).

Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]: nominal P deflated 0.20-0.32 across the four candidates; novel-synthesis cap at 0.50 not binding for M1+M2 (core mechanism well-grounded LSM literature) but binding for M4 (filesystem-COW analog is novel synthesis at dense-matrix subspace).

## Files of interest

- `notes/research_alt_edit_isolation_v1_2026-05-31.md` (primary deliverable; 9 external citations + 7 internal cross-refs; HARD-PASS/HARD-FAIL/MIDDLE-BAND pre-reg; M2 smoke design)
- `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md` (origin routing)
- `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` (companion: D3 edit-log-replay is same mechanism family as M2 here)
- `notes/substrate_capability_map.md` v290 R-COW-INFEASIBILITY block (lines ~20169-20174) and v290 T2 Path D block (lines ~19901-19903)

## Not auto-dispatched

This is a research delivery + recommendation. Orchestrator decides cap_map annotation timing (annotation-only is allowed while paused per [[feedback-obey-user-pause-explicitly]] semantics) and experiment dispatch timing (gated by pause flag).
