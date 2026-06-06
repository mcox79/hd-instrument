# Research -> Exp-Dev: Batch D AUTHORIZED -- fact_checked_khop production-readiness (5 cells; ~2-3h CPU; $0)

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User
**Date:** 2026-06-06 ~23:15
**Re:** exp_dev_handoff_research_drill_fact_checked_khop_2026-06-06.md (optimization drill output)
**Subject:** User authorized Batch D. Tests whether fact_checked_khop KILLER DEMO (HP at K=3,5 smoke) is production-ready at K=10,20 where structural ceiling (drill math) predicts 0.60-0.75 AUC floor without architectural tweaks.

---

## User authorized Batch D

Per the optimization drill's recommendation. Drill identified structural mathematical ceiling at production K: joint AUC >= 1 - K*(1 - AUC_per_hop). At K=20 hard-domain per-hop AUC=0.975, floor = 0.60 (production-unacceptable). Must close this before K>=10 deployment.

### Dispatch order from drill (rank-ordered)

### Batch D1 (immediate parallel; 3 cells)

**Rank 1: Confidence-weighted aggregation** -- `fact_checked_khop_confidence_weighted_v1`
- Architecture: replace binary per-hop flag with C_min and C_chain product
- Cost: 1 day implementation; ZERO added compute at inference
- Substrate-product reading: cheapest possible adversarial-signal lift on KILLER DEMO
- HP: confidence-weighted AUC >= binary-flag AUC + 0.02 on adversarial test set
- MID: equal but with discrimination tightening
- HF: worse than binary flag (calibration issue)

**Rank 2: Middle-hop adversarial injection localization** -- `fact_checked_khop_middle_hop_localization_v1`
- Architecture: inject fabrication at position h in {0, K//2, K-1} for K in {3, 5}; measure per-position localization accuracy
- Cost: ~30 min CPU; standalone benchmark
- Substrate-product reading: **PRODUCTION GATE TEST**. If middle-hop localization <0.65, backward chaining (Rank 5) becomes mandatory before K>=5 deployment.
- HP: middle-hop localization accuracy >= 0.85
- MID: 0.65-0.85 (degraded but usable)
- HF: < 0.65 (requires backward chaining redesign)

**Rank 3: Per-hop Merkle chain + HP-12 V1 root** -- `fact_checked_khop_merkle_chain_hp12_root_v1`
- Architecture: each hop's verification cert gets a Merkle leaf; per-K chain forms Merkle tree; root cert via HP-12 V1's RSA accumulator at <1ms
- Cost: 1-2 days engineering; ~$0 compute
- Substrate-product reading: extends HP-12 "answer-certified" to "per-hop reasoning chain certified end-to-end". No frontier system has this.
- HP: end-to-end Merkle cert latency < 1ms at K=20; verification round-trip works
- MID: latency 1-5ms; usable but not flagship-fast
- HF: > 5ms (engineering optimization needed before production)

### Batch D2 (conditional / sequential after D1)

**Rank 4: K-scaling latency parallelization** -- `fact_checked_khop_parallel_latency_v1`
- Architecture: parallel per-hop verification (vs sequential); measure latency + accuracy delta
- Cost: ~30 min benchmark on CPU/GPU
- Substrate-product reading: enables K=20 production deployment at feasible latency
- HP: parallel accuracy >= sequential AUC - 0.005 (safe to parallelize)
- HF: > 0.005 degradation (parallelization breaks the chain-coupling that gives localization)

**Rank 5: Backward chaining accuracy lift** -- `fact_checked_khop_backward_chaining_v1`
- **CONDITIONAL** on Rank 2 finding middle-hop localization < 0.85
- Architecture: after forward K-hop, do backward pass verifying each hop against final answer
- Cost: 2x KF-1 calls; production latency cost real
- Substrate-product reading: catches error-propagation that forward-only misses; highest adversarial-robustness lift if Rank 2 reveals need
- HP: backward chaining lifts middle-hop localization to >= 0.85
- MID: lifts but doesn't clear 0.85 (some residual error)
- HF: minimal lift (error-propagation mechanism is something else)

---

## Total estimate

- D1 (Ranks 1+2+3): ~2h CPU parallel; $0; production-gate decisive
- D2 (Rank 4 + conditional Rank 5): ~1h additional CPU; $0; depends on D1 outcomes
- Total: ~2-3h CPU sequential; $0

---

## Strategic value

### If Rank 2 finds middle-hop localization >= 0.85
- KILLER DEMO is production-ready at K=10,20 with confidence-weighted aggregation + Merkle audit
- Phase 4 v3 deploys with cryptographically-verifiable per-hop reasoning trace
- Categorical differentiator vs ALL frontier LLM/RAG systems

### If Rank 2 finds middle-hop localization 0.65-0.85
- Confidence-weighted aggregation likely closes the gap (free lift)
- Production deployment OK with notes on K-scale recommendations

### If Rank 2 finds middle-hop localization < 0.65
- Backward chaining (Rank 5) becomes mandatory before K >= 5 deployment
- Production latency cost: 2x KF-1 calls
- Architecture pivots: still ships but with cost note

**Either outcome ships the KILLER DEMO with production-grade specification, not lab-bench smoke results.**

---

## Cross-references

- Optimization drill: notes/research_drill_fact_checked_khop_optimization_robustness_2026-06-06.md
- Original handoff: notes/exp_dev_handoff_research_drill_fact_checked_khop_2026-06-06.md
- Batch B HP smoke: notes/exp_dev_to_research_batchB_complete_2026-06-06.md
- KF-1 + K-hop primitives: search notes/ for KF-1 / K-hop entries
- HP-12 V1 RSA accumulator: search notes/ for HP-12 V1

---

## Contract

You design anchor specifics, sweep grids, HP/MID/HF thresholds, queue assignments, timeout formulas. Pre-reg per envelope-fail-band protocol. write_metrics() required fields. ASCII-only. Apply [[feedback-no-experiment-design-in-prompts]] -- this handoff names anchors + WHY only.

Rank 2 is the production gate test; if HF, Rank 5 is mandatory. Otherwise Rank 5 is informational only.

---

**END.**

**Exp-Dev:** Batch D authorized (5 cells; ~2-3h CPU; $0). Ship D1 first (Ranks 1+2+3; production gate decisive). D2 conditional on D1 outcomes. Drill's pull order is recommendation; override if queue state argues.

**User:** Batch D (5 cells) routed to Exp-Dev. Tests whether fact_checked_khop KILLER DEMO is production-ready at K=10,20 deployment where drill math predicted structural ceiling. If middle-hop localization HF (<0.65), backward chaining becomes mandatory. Either outcome ships KILLER DEMO with production-grade specs.
