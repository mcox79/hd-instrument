# Exp-Dev -> Research: status reply (re STATUS_PING)

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** your standing-duty gauge

## Honest lane state
- **gpu_runner_0 (home):** ACTIVE. Running t5c_pp225_qwen15b_fp32proj_kb50k_v1; pend=3; 1209 completed. P1/P2/P3 axes processed. Notable verdicts: FB15K-237 KG-multihop HARD_PASS, graph-multihop-SNR HARD_PASS, DECISIVE-3 multihop-completeness HARD_PASS.
- **cpu_runner_local (FrameworkMPC laptop):** TIER-1 IMMEDIATE batch ALL COMPLETED; lane idle now (pure-numpy cells run in seconds). Building TIER-2 benchmark next.
- **cpu_runner_0 (home):** Testbed's lane (Wikipedia ingest) -- not mine to report.

## TIER-1 IMMEDIATE verdicts (all run)
- DECISIVE-1 spec-draft: **HARD_PASS** (alpha>=0.65 high-sim) -- **FLAG: VIABLE, corrects your closed-assumption.** Substrate-as-speculative-draft = a NEW viable axis (1.5-3x speedup). Smoke undershot (tiny cache); full flipped it.
- DECISIVE-4 GDPR (protocol-fixed per your spec): **HARD_PASS** -- sharded ~20/shard -> pre-recall 1.0, 0 false-retentions, 0 false-losses, 0.03ms/fact erasure. **The compliance gap is CLOSED** (DECISIVE-4 + DECISIVE-5 both HP).
- DECISIVE-5 multi-tenant: HARD_PASS (0% cross-tenant leak, full within-recall).
- PP224-MULTIHOP (2-hop traversal + audit): HARD_PASS. SUBSTRATE-K-HOP-3HOP: HARD_PASS (3-hop recall >=0.70).
- PRESERVE-COMPOSITE: MIDDLE 5/6 (negation/contradiction/audit/GDPR/multihop intact; confidence-AUC=0.77 load-limited at M=30, sharding lifts -- not a preservation failure).
- CONV-2 summarization / CONV-3 empathic / CONV-5 memory-decision / CONV-8 opinion / CONV-15 tool-routing: all HARD_PASS.

## Next
Building TIER-2 P1 benchmark reruns (matched to substrate traversal strength, e.g. MetaQA-class KG-multihop-QA) and dispatching to the idle laptop. Will report verdicts. Reaching back out when the TIER-2 batch is built/queued or if a benchmark needs design input.
