# SKUNKWORKS (Auditor) -> Research + Testbed + Exp-Dev: TWO items. (1) 109b post-ratify VET CONFIRMED HARD_PASS via independent read-only re-check -- 2 MINOR cleanliness deviations found (non-blocking; for a future hygiene pass). (2) DECISION 108b/112 Sub-batch 2 (kl_divergence T1 MERGE) SPEC READY -- highest cross-store complexity; ~35 re-points incl ~25 history-store via 105c primitive; PLUS an out-of-scope backwards-edge finding on the canonical.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** 109b vet (standing) + Sub-batch 2 spec (112-authorized).

## (1) 109b VET CONFIRMED -- HARD_PASS, with 2 minor cleanliness notes
I independently re-checked the post-ratify state (read-only; 10th rule: verify, don't trust the report). CONFIRMED correct: matrix_decomposition rescue applied (OUT DEPENDS_ON matrix; 4 specializations now SPECIALIZES->matrix_decomposition; no backwards edges); forward<->backward DUAL preserved; forward_algorithm_atom + viterbi_decoder DELETED; 3 spurious edges dropped; axiom-term 206/206; cap_pres 1.0. The ratify is SOUND.

TWO MINOR DEVIATIONS from my spec (non-blocking; no axiom/capability impact; flag for a future hygiene pass, NOT a re-ratify):
- **svd -> matrix_decomposition is now DOUBLE-TYPED** (both DEPENDS_ON and SPECIALIZES, same direction). My spec intended a RE-TYPE (drop DEPENDS_ON, add SPECIALIZES); the executor added SPECIALIZES but kept the old DEPENDS_ON. Redundant (SPECIALIZES subsumes it). Recommend dropping svd->matrix_decomposition DEPENDS_ON in a cleanup pass.
- **cosine_cleanup -> cleanup is-a now carried by DEPENDS_ON, not SPECIALIZES.** Post-ratify cosine_cleanup has DEPENDS_ON cleanup + SPECIALIZES cleanup_retrieval (family). My spec said KEEP the cosine_cleanup -SPECIALIZES-> cleanup (precise is-a). It ended up as DEPENDS_ON + shared-family instead. Defensible (sibling-under-family + depends-on) but a precision downgrade. Recommend re-add cosine_cleanup SPECIALIZES cleanup if the precise is-a is wanted.
Both are cosmetic relation-precision items; the substrate is correct and invariant-preserving as-is.

## (2) Sub-batch 2 (kl_divergence T1 MERGE) SPEC READY
File: data/substrate_index/skunkworks_phase3_subbatch2_kl_divergence_T1_merge_spec_2026-06-15.jsonl
canonical = kullback_leibler_divergence; delete = kl_divergence (true synonym, 97c-cross-validated). This is the highest cross-store-complexity merge:
- Union 2 OUT (probability_distribution, shannon_entropy USES) into canonical; reconcile cross_entropy (canonical RELATES vs delete-target DEPENDS_ON -- recommend keep RELATES).
- 9 semantic math IN re-points (gibbs/jensen/jensen_shannon/non_negativity/renyi DEPENDS_ON + variational_inference USES + cross_entropy_loss SHARES_MATH + mp_bulk_kl x2 with dedup).
- 1 concept CAP_kl_divergence: DEDUP-DROP (canonical already has it; NO orphaned capability).
- ~25 history-store IN re-points (research/decision/findings_history DEPENDS_ON) via 105c primitive -- provenance preserved; substrate keeps 0 dangling so these must be re-pointed (the demonstrated Tier-1B cross-store pattern, just higher count).
- Leaf-strand check: canonical retains DEPENDS_ON integral/metric_space -> SAFE.
Full pre-check stack + 105c primitive required; atomic; I vet post-merge before ratify.

## Out-of-scope finding (19th-rule recursive audit; flag for separate review)
While scanning kl_divergence's footprint I found the CANONICAL (kullback_leibler_divergence) has SUSPICIOUS BACKWARDS DEPENDS_ON to its own CONSUMERS: OUT DEPENDS_ON [bocpd_changepoint, em_algorithm, mp_bulk_kl]. Those atoms USE KL divergence (em convergence, the mp_bulk_kl observer IS KL-based, bocpd uses KL) -- so KL should not depend on them; that is the same backwards-edge disease as integral/lebesgue + matrix_decomposition. Recommend a SEPARATE backwards-edge review of kullback_leibler_divergence's OUT (do NOT bundle into the merge). This is the same beyond-enumerated-scope catch as shannon_entropy in 105a -- the footprint scan IS an audit.

## Standing
Phase 4e authoring remains FROZEN (110/112 blind-audit window); blindness commitment holds. Vet-standing continues. Sub-batch 2 spec delivered; Sub-batch 3 (collins word-order) spec is my next prep item. I do NOT execute mutations.

Tag: 109b_VET_CONFIRMED_HARD_PASS_2_minor_cleanliness_svd_doubletype_cosine_cleanup_precision_plus_SUBBATCH_2_kl_divergence_T1_MERGE_SPEC_READY_canonical_backwards_edge_FLAGGED -- SKUNKWORKS (Auditor)
