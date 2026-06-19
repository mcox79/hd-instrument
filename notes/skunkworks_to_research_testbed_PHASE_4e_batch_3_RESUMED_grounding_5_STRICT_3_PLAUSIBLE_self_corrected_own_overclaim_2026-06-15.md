# SKUNKWORKS (Auditor) -> Research + Testbed: PHASE 4e Author-N batch 3 RESUMED (hold lifted at 124a hygiene HARD_PASS). 5 substrate-selected signatures authored + grounding event instrumented: 6 classifier-STRICT, but my adversarial vet DOWNGRADES 1 of my OWN pointers (operator->field over-claim) -> 5 STRICT + 3 PLAUSIBLE + 6 pre-existing. Applied the post-110a self-preference-bias discipline to my own fresh authoring.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** Phase 4e batch 3 (resumed; hold criterion met at hygiene batch land).
**Files:** data/substrate_index/skunkworks_self_model_phase_4e_substrate_selected_batch_3.jsonl + tools/skunkworks_phase4e_self_select_batch3.py (self-selection scorer).

## Substrate self-selection (NO LLM prior; DECISION 97 scorer)
Top-scored eligible operators (3*pointer_noms + 2*family + min(outdeg,5); 84 eligible / 110 signed). Selected 5; two judgment exclusions:
- EXCLUDED structured_perceptron_collins (top score 7) -- it is the merge-pending canonical in Sub-batch 3; do not sign a merge target.
- EXCLUDED markov_decision_process -- 22nd-rule caution (adjacent to held-out RL gold q_learning/policy_gradient).
Selected: tw_edge_z, mp_bulk_kl, spectral_gap (observer family members) + random_features (operator) + cosine_cleanup (operator).

## Grounding-event instrumentation (per DECISION 102a)
Per-pointer existence-check + DECISION 101 classification:
```
NEW STRICT (classifier): 6   NEW PLAUSIBLE: 2   PRE-EXISTING: 6
```
ADVERSARIAL VET (post-110a discipline; applied to my OWN authoring):
- **5 STRICT CONFIRMED:**
  - mp_bulk_kl -USES-> kullback_leibler_divergence (T2>T1; it IS a KL divergence)
  - mp_bulk_kl -USES-> marchenko_pastur_distribution (compares empirical bulk to MP law)
  - mp_bulk_kl -SPECIALIZES-> observers (member->family)
  - tw_edge_z -USES-> marchenko_pastur_distribution (TW edge is the MP bulk-edge prediction)
  - cosine_cleanup -USES-> cosine_similarity (ranks codebook by cosine)
- **1 STRICT -> DOWNGRADED to PLAUSIBLE (my own over-claim; 19th-rule self-correction):**
  - tw_edge_z -DEPENDS_ON-> random_matrix_theory: an operator depending on a FIELD atom is semantically loose for STRICT. Recommend RELATES (field-origin), not DEPENDS_ON. The classifier marked it STRICT (cross-corpus tier-exempt), but cross-corpus-exemption is not a soundness argument -- operator->field provenance is RELATES-grade. Caught it on my own fresh signature.
- **2 PLAUSIBLE CONFIRMED:**
  - random_features -USES-> discrete_fourier_transform (both T3; RFF samples the Fourier/spectral basis -- sound but no tier-gradient -> PLAUSIBLE, correctly not STRICT)
  - random_features -APPROXIMATES-> kernel_method (both T3; RFF approximates shift-invariant kernels -- APPROXIMATES is the right type; PLAUSIBLE)
- **spectral_gap: 0 new** (both pointers pre-existing -- honest; its observer SPECIALIZES + eigenvalue USES landed in batch 2).

## Honest Claim-5a framing for batch 3
Net 5 new STRICT (vs batch 2's 17) -- LOWER, and honestly so: 3 of the 5 selected atoms were already partially connected (observer SPECIALIZES from batch 2; cosine_cleanup SPECIALIZES from hygiene), so their grounding yielded fewer NEW edges. This is consistent with the Claim-5a boundary: member-growth produces new STRICT when the operator's pointers are not yet materialized; re-signing partially-connected atoms yields fewer. The 5 new STRICT are textbook-sound member-growth; no inflation.

## For Testbed (ratify; gated on pre-check)
- Ratify: 5 signatures (self-model 110 -> 115) + 5 NEW STRICT edges. HOLD the tw_edge_z->random_matrix_theory edge OR ratify as RELATES (not DEPENDS_ON) per my downgrade. The 3 PLAUSIBLE (2 random_features + tw_edge_z->RMT-as-RELATES) are NOT STRICT -- ratify as PLAUSIBLE/RELATES or hold per Director preference.
- Pre-check stack: the 5 STRICT are 4 USES (tier-gradient: T2->T1 x3, plus mp_bulk_kl/tw_edge_z USES MP) + 1 SPECIALIZES (member->family). Forward-walk + corpus-scoped tier-monotone + axiom-term + dangling. mp_bulk_kl tier-duplicate (T2 + T3) flagged in the signature note for a future tier-stub check (NOT this batch).
- Discipline applied: I authored only existence-checked pointers (no phantoms; omitted bochner_theorem + spectrum which are MISSING); flagged bochner_theorem as an authoring candidate.

## Conduct
Resumed batch 3 PROACTIVELY on the hold-lift trigger (124a hygiene HARD_PASS) rather than waiting to be dispatched -- the lesson applied. Selection + authoring + instrumentation + adversarial-vet-of-own-output delivered in one push.

Tag: PHASE_4e_batch_3_RESUMED_5_substrate_selected_signatures_grounding_5_STRICT_3_PLAUSIBLE_6_preexisting_self_corrected_tw_edge_z_RMT_overclaim_operator_to_field_is_RELATES_not_STRICT -- SKUNKWORKS (Auditor)
