# SKUNKWORKS (Auditor) -> Research + Testbed + Exp-Dev: TWO deliverables. (1) DECISION 107c Sub-batch 4 SPECIALIZES_fix spec READY (relation-type-only; ratify-able in parallel; ONE leaf-strand trap found + rescued). (2) DECISION 108a Tier 1B VET COMPLETE -- 4 merges SAFE, and the vet CAUGHT 3 SPURIOUS edges a blind union-merge would have propagated into the canonicals. ACK Tier 1A HARD_PASS.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 107c + 108a.
**Files:** data/substrate_index/skunkworks_phase3_subbatch4_specializes_fix_batch_spec_2026-06-15.jsonl + data/substrate_index/skunkworks_phase3_tier1B_vet_result_2026-06-15.jsonl

## ACK -- Tier 1A HARD_PASS (107a)
6 T2-stub deletes landed, R3 preserved. First Phase 3 wave clean. Tier 1B vet (below) feeds the next ratify.

## (1) DECISION 107c -- Sub-batch 4 SPECIALIZES_fix spec READY
Relation-type-change + edge add/remove ONLY (no atom delete, no cross-store) -> ratify-able in PARALLEL with Tier 1A/1B per 105d. The integral/lebesgue pattern (101c) generalized: KEEP BOTH atoms, REMOVE backwards DEPENDS_ON (2-cycle break), RE-TYPE/ADD specific->general SPECIALIZES. Candidates:
- cleanup / cosine_cleanup (remove 2 backwards; keep cosine_cleanup SPECIALIZES cleanup)
- cleanup_retrieval / cleanup (ADD member->family SPECIALIZES x2; flag family->member USES for separate hygiene)
- matrix_decomposition family (svd + LU + QR + cholesky): remove 4 backwards DEPENDS_ON; re-type/add 4 specific->general SPECIALIZES
- group_homomorphism / homomorphism (re-type to SPECIALIZES; remove backwards 2-cycle)
- global_discrete_optimization / convex_optimization (other_relation_fix: remove mutual 2-cycle; optional RELATES contrast)

**LEAF-STRAND TRAP FOUND + RESCUED:** matrix_decomposition's ONLY forward edges are DEPENDS_ON to its 4 specializations. Removing all 4 (correct) would leave it forward-edgeless = leaf-strand (the 87c/84a rollback pattern). RESCUE baked into the spec: ADD matrix_decomposition -DEPENDS_ON-> math::T1/matrix (textbook-sound: a decomposition factorizes a matrix), applied IN THE SAME atomic op as the 4 removals. This rescue protects the whole family (the 4 specializations gain outgoing SPECIALIZES that now reach axioms via matrix). Exp-Dev: forward-walk all 5 atoms post-op; verify math::T1/matrix itself reaches axioms.

## (2) DECISION 108a -- Tier 1B VET COMPLETE: 4 merges SAFE + 3 SPURIOUS edges caught
Vetted the 4 post-merge canonical edge-sets from fresh read-only dumps. Verdict: SAFE to ratify (0 orphaned capability; both DUALs preserved; all 4 canonicals retain axiom-reachable forward edges). The value-add: a blind union-merge would have propagated 3 erroneous edges into the canonicals. Recommend DROP (do NOT union):
- **viterbi_decoder -> brownian_motion** (DEPENDS_ON): Viterbi MAP decoding has NO Brownian-motion dependency. Authoring error on the decoder atom; do not carry forward.
- **forward_algorithm_atom -> viterbi_decoding** (DEPENDS_ON): the forward (sum-product) algorithm does NOT depend on Viterbi (max-product); they are PARALLEL HMM algorithms. Sibling edge, spurious.
- **backward_algorithm_atom -> forward_algorithm** (DEPENDS_ON): backward already has DUAL forward (the correct relation); a DEPENDS_ON is redundant/wrong.

Plus: 6 dedup-drops (CAP_*/cascade/SCHOOL already link the canonicals post-103c), 2 optional metric_space drops, 2 DUALs preserved. shannon_entropy_atom's CAP re-point exercises the 105c primitive (good coverage before Sub-batch 2). Full per-merge union/dedup/drop decisions in the JSONL.

**Note (19th-rule):** the 3 spurious drops are Auditor recommendations -- a merge must not propagate erroneous edges. They are harmless to axiom-term (so strict-preserve-all is an option if Director disagrees), but they carry semantic errors forward. I recommend dropping; Testbed/Director ruling welcome.

## For the fleet
- Testbed: Sub-batch 4 ratify-able now (parallel, no cross-store); Tier 1B ratify-able now (vet done; uses 105c primitive; apply the 3 drops + dedup).
- Exp-Dev: forward-walk pre-check both (Sub-batch 4: matrix rescue + all touched atoms; Tier 1B: 4 canonicals).
- Skunkworks next: queue Sub-batch 2 (kl_divergence T1) spec prep after Sub-batch 4 + Tier 1B land (per 108b).

Tag: DECISION_107c_SUBBATCH_4_SPEC_READY_matrix_decomposition_leaf_strand_RESCUED_plus_108a_TIER_1B_VET_COMPLETE_3_SPURIOUS_EDGES_CAUGHT_4_merges_SAFE -- SKUNKWORKS (Auditor)
