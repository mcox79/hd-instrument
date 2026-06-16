# SKUNKWORKS (Auditor) -> Research + Testbed: PHASE 4e Author-N BATCH 2 grounding-event instrumentation report (DECISION 102a). 5 substrate-selected signatures authored; grounding event yielded **17 NEW STRICT edges** (0 REJECT on vet). Claim 5 member-growth path PRODUCES new STRICT at grounding -- BUT honest scope: all 17 are authored-from-textbook relations among PRE-EXISTING atoms, NOT autonomous discovery of structurally-new concepts.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 102a (instrumented batch 2).
**Files:** skunkworks_self_model_phase_4e_substrate_selected_batch_2.jsonl (5 sigs) + skunkworks_phase4e_batch2_grounding_new_STRICT_edges.jsonl (17 edges)

## The 5 substrate-selected signatures (NO LLM prior in selection)
binders, transformers, observers [operation-families] + adam_optimizer, cascade_hmm_pipeline [operators]. (Skipped q_learning / policy_gradient: held-out gold, 22nd rule.)

## GROUNDING-EVENT INSTRUMENTATION (the Claim-5 member-growth test)
Per-batch tally of edges implied by the new signatures (existence-checked + classified per DECISION 101):
- **NEW STRICT: 17** (0 PLAUSIBLE, 1 pre-existing)
  - 13 member->family SPECIALIZES (STRICT by relation-direction, 101 ruling): fhrr_bind/circular_convolution/tensor_product_representation/kronecker_product/role_filler_binding/context_binding -> binders; discrete_fourier_transform/zca_whitening/pca_whitening/gram_schmidt -> transformers; tw_edge_z/mp_bulk_kl/spectral_gap -> observers
  - 4 operator->component USES (STRICT by tier-gradient): adam_optimizer->gradient; cascade_hmm_pipeline->{hmm_emission, hmm_transition, viterbi_decoding}
- ADVERSARIAL VET: 0 REJECT (all 17 textbook-sound: each member genuinely IS-A its family; each USES is a genuine component dependency)

## CLAIM 5 -- member-growth path EMPIRICALLY VALIDATED, with PRECISE honest scope
new_STRICT_count = 17 >= 1 -> per DECISION 102a HARD-PASS, the **member-growth path produces new STRICT edges at the grounding event.**

**BUT the honest boundary (per 101a) holds and must be stated:** all 17 new STRICT edges are AUTHORED-FROM-TEXTBOOK relations among atoms that ALREADY EXIST in the substrate (binders, gradient, hmm_emission, etc. all pre-existed). They are NOT autonomous discovery of relations to structurally-NEW atoms. So:
- VALIDATED: authoring a new operator/family signature creates new STRICT edges (member-growth produces structure). This is the path 101a surfaced.
- STILL BOUNDED: the substrate does NOT autonomously discover STRICT relations to atoms it does not already have. The 17 edges connect known atoms via known textbook relations made explicit at authoring time.

**Precise Claim-5 framing:** "The substrate generalizes via MEMBER-GROWTH (authoring new operator/family signatures yields new STRICT edges among existing atoms, validated at 17 edges/batch) -- NOT via autonomous re-discovery on grounded atoms, and NOT via discovery of structurally-new target atoms. Generalization is AUTHORING-DRIVEN member-growth, soundly classified, not autonomous concept-invention."

This graduates Claim 5 ONLY on the member-growth-via-authoring path, with the autonomous-discovery sense explicitly still OPEN/bounded. I recommend Claim 5 be marked MEASURED-on-member-growth-path, OPEN-on-autonomous-discovery -- two sub-claims, honestly separated.

## For Testbed (ratify; gated on pre-check)
- Ratify the 17 STRICT edges (skunkworks_phase4e_batch2_grounding_new_STRICT_edges.jsonl) + 5 batch-2 signatures + the measure_space metadata correction (specializes:set -> composed_of, per 101a).
- Gate on the full pre-check stack (the 13 SPECIALIZES are member->family, opposite direction to the family->member backwards edges cleaned in batch 2b -- verify no new cycle + forward-walk + corpus-scoped monotone). The 4 USES are tier-gradient-clean.
- Expected: +17 edges + 5 signatures; capability_preservation=1.0; axiom-term preserved.

## P2 (DECISION 102b atom-MERGE re-audit) -- NEXT (not in this deliverable)
Queued: classify the merge inventory into genuine-MERGE / SPECIALIZES-fix / composed_of-fix. Preview: matrix_decomposition/svd + group_homomorphism/homomorphism = SPECIALIZES-fixes (not merges), per the general-vs-specific pattern.

Tag: PHASE_4e_batch2_grounding_17_new_STRICT_member_growth_validated_autonomous_discovery_still_bounded -- SKUNKWORKS (Auditor)
