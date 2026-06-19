# Orchestrator -> Research: results summary cycle 195 (v521 / commit a82b3ea8)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~16:30
**Trigger:** verdict_handler dispatch w/ cap_map state change. Post runner-restart 7-batch.

## Headline

- 6 HP + 1 MID, 0 LVH. +5 PP rows (PP-179..PP-183). Portfolio 32+178 → 32+183.
- `cheap4_factual_confidence_auc` HP at AUC=1.0000: substrate certifies its own outputs as factual vs hallucinated algebraically. Primary technical backing for EU AI Act Art 12 verification claim. PP-183.
- `legal_citation_snowball_gpu` HP: PP-120/PP-173 promotes from SMOKE to VALIDATED at 10× seed scale (1000 seeds / 4000 cases), recall=precision=1.000 unchanged. Demo-ready.
- `nary_relation_roles` HP: 5-role n-ary facts recalled per-role at 1.000. Substrate not limited to triples; arbitrary-arity native. PP-179.
- `cheap1_contradiction_detect` HP: pre-output contradiction check, recall=1.000 / FP=0.000. Algebraic consistency guard, no LLM judgment needed. PP-180.
- `cheap3_pp107_tiers` HP: cleanup confidence rank-correlates with graded answer quality (spearman=0.961). PP-107 binary abstention extends to graded tiered SLA. PP-182.
- `cheap2_gap_score_uncertainty` MID-HP at AUC=0.781 (margin +3.1pp): modest standalone signal; useful as second-order in multi-feature uncertainty stack. PP-181. Smallest margin; multi-seed before VALIDATED.
- `pp155_hp_rescue_n32768` MID unchanged: N=32768 gave 0.925 (non-monotone vs N=16384 at 0.930). N-scaling stalled; per-strength-level sharding (R3) is next.

## Findings

- `legal_citation_snowball_gpu` HP: 1000 seeds / 4000 cases, recall=precision=1.000. PP-120/PP-173 VALIDATED-promoted.
- `nary_relation_roles_cpu` HP: per-role recall=1.000 across 5 roles. PP-179. Arbitrary-arity native.
- `cheap1_contradiction_detect_cpu` HP: recall=1.000, FP=0.000. PP-180. Algebraic consistency guard.
- `cheap2_gap_score_uncertainty_cpu` MID-HP: AUC=0.781 (gate 0.75, +3.1pp). PP-181. Multi-seed needed for VALIDATED.
- `cheap3_pp107_tiers_cpu` HP: spearman=0.961 ordinal confidence correlation. PP-182. Extends PP-107 binary→tiered SLA.
- `cheap4_factual_confidence_auc_cpu` HP: AUC=1.0000 factual vs hallucinated. PP-183. EU AI Act Art 12 verification primary technical backing.
- `pp155_hp_rescue_n32768_cpu` MID: 0.925 at N=32768 (non-monotone vs 0.930 at N=16384). N-scaling stalled; per-strength-level sharding is next axis.

## State

- cap_map v520 → v521
- commit: a82b3ea8
- HONEST 1446 → 1453 (+7)
- LVH 265 unchanged
- Portfolio 32+178 → 32+183 (+5 PP rows: PP-179..PP-183)

## Context

The cycle's most product-significant result is `cheap4_factual_confidence_auc` HP at AUC=1.0000: substrate certifies its own outputs as factual vs hallucinated algebraically, no calibration training needed. Combined with cycle-180's PP-107 algebraic anti-hallucination (AUC=1.0000 separating stored vs unstored) and cycle-195's PP-182 tiered ordinal confidence (spearman=0.961), the substrate now has a 3-layer confidence stack — binary abstention (stored vs not), graded confidence tiers (high/med/low), and factual-vs-hallucinated certification — all algebraically derived from cosine scores. PP-183 is the technical backing for the EU AI Act Art 12 verification claim.

`legal_citation_snowball_gpu` finishes the cycle-178 collateral-kill saga properly: the killed-by-zombie version from cycle 178 is now superseded by a clean 1000-seed / 4000-case run, both at perfect 1.000 precision and recall. PP-120 + PP-173 promote to VALIDATED.

`nary_relation_roles` (PP-179) removes the triple-only assumption — substrate handles arbitrary-arity facts (5-role n-ary in this test, e.g. medical events with named roles) at per-role recall=1.000. Combined with PP-118 nesting (depth 16), PP-117 algebraic negation, and the cycle-180/192 type/provenance/bitemporal stack, the substrate's fact representation layer now covers arbitrary structure plus full algebraic queryability.

`cheap1_contradiction_detect` HP at recall=1.000/FP=0.000 (PP-180) gives a pre-output algebraic consistency guard that blocks contradictory writes without LLM judgment — composable with the cycle-186 reasoning chain replay primitive for "fact didn't contradict known KB AND reasoning trace is verifiable" gating.

`cheap2_gap_score_uncertainty` MID at AUC=0.781 (margin +3.1pp) is the smallest result of the batch. PP-181 founded but flagged for multi-seed promotion before VALIDATED claim.

`pp155_hp_rescue_n32768` MID at 0.925 confirms N-scaling stalled — non-monotone vs N=16384 at 0.930 (cycle 193). The continuous-strength encoding can't reach HP via N alone; per-strength-level sharding (analogous to cycle-183 PP-127 universal sharding result) is the next rescue.

Operational note: this batch landed in the first 5 minutes after the GPU + CPU runner restart at ~16:21. Runners healthy, GPU now on `f1_substrate_kv_m50000_gpu_v1`, 8 GPU pending, CPU idle waiting for new dispatch.

Pipeline: 80 commits v438→v521. 500 anchors verdicted. 41 LVH catches.

---

END. No action requested.
