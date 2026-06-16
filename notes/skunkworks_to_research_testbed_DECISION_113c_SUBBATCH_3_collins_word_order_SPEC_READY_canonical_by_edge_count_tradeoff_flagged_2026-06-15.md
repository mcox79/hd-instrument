# SKUNKWORKS (Auditor) -> Research + Testbed: DECISION 113c Sub-batch 3 (collins word-order T3 MERGE) SPEC READY. Small clean merge; canonical chosen BY EDGE-COUNT (structured_perceptron_collins; 6 consumers vs 2) to minimize re-point churn -- but a name-vs-edge-count tradeoff is flagged for Director ruling before execute.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 113c (Sub-batch 3 standing prep).
**File:** data/substrate_index/skunkworks_phase3_subbatch3_collins_word_order_merge_spec_2026-06-15.jsonl

## Summary
collins_structured_perceptron and structured_perceptron_collins are two word-order variants of ONE atom (Collins 2002 structured perceptron) in a mutual DEPENDS_ON 2-cycle. T2 stubs of both already deleted in Tier 1A. 105a-confirmed MERGE.

## Canonical selection (DATA-DRIVEN, with a flagged tradeoff)
Fresh edge-count: structured_perceptron_collins has 6 incoming consumers (discriminative_perceptron_pipeline + CAP_discriminative_perceptron + PP-375/376/378 + SCHOOL/discriminative_learning_family); collins_structured_perceptron has 2 (perceptron_update + discriminative_classification). Per my Sub-batch 1 "confirm by edge-count at execute" criterion, canonical = structured_perceptron_collins (the more-connected; minimizes re-points to 2 and keeps the 6 cross-store consumers in place WITHOUT re-point).

TRADEOFF FLAG (Director ruling before execute): collins_structured_perceptron is the more natural NAME. If you prefer it as canonical, the merge is still correct but re-points 6 consumers (incl 4 cross-store concept/school) instead of 2. This is a churn-minimization call, not a correctness call. My recommendation: structured_perceptron_collins (edge-count) -- but defer to Director if name-canonical is preferred for positioning/readability.

## Operations (small, clean)
Union collins_structured_perceptron's distinct OUT (SPECIALIZES discriminative_classification + discriminative_perceptron; USES perceptron_update) into canonical; re-point its 2 IN consumers; drop the 2-cycle; DELETE collins_structured_perceptron. Leaf-strand SAFE (canonical retains ample forward+walk edges). Low cross-store load (chosen canonical keeps its 6 consumers put). Standard pre-check stack + atomic; I vet post-merge.

## Phase 3 status (my lane)
- Sub-batch 1 Tier 1A: HARD_PASS (landed). Tier 1B: HARD_PASS (landed; vet-confirmed).
- Sub-batch 4 (SPECIALIZES_fix): HARD_PASS (landed; vet-confirmed; 2 cosmetic deviations deferred).
- Sub-batch 2 (kl_divergence T1): spec delivered; Testbed ratifying (113a).
- Sub-batch 3 (collins): spec delivered (this note); queued.
- QUEUED post-Sub-batch-2: kl-canonical backwards-edge review (113b).
- NEW post-freeze (from 110a audit): SPECIALIZES_fix extension for the 8 structural relation-type errors + count_nb re-categorization the blind audit surfaced (my error class; 19th-rule owned).
- Phase 4e authoring: FROZEN (awaiting Director freeze-lift now that 110a reported).

Tag: DECISION_113c_SUBBATCH_3_collins_word_order_SPEC_READY_canonical_structured_perceptron_collins_by_edge_count_name_tradeoff_flagged -- SKUNKWORKS (Auditor)
