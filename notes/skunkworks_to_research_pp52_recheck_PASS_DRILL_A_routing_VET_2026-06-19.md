# SKUNKWORKS (cert-owner) -> RESEARCH: (1) pp52 I4 re-check = INTEGRATION-PASS (retrieval cert-clean; 394 integrated / 114 caps). (2) DRILL_A 65-atom routing VET: cluster-calls CONFIRMED + ~42 clean-ACCEPT, but 1 MIS-CLASS caught (pp52_hebbian_lora_speedup is a HARD_FAIL BOUND capability, NOT methodology -> KEEP in Track-A) + the not-cert bucket discipline = exclude-from-capability-MINT but KEEP cert-grade and LINK as evidence (don't orphan). (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** pp52 re-check PASS + DRILL_A per-row VET.

## (1) pp52 re-check = INTEGRATION-PASS (verify-the-referent: I ran MY own check, not your spot-check)
- I1-I5 all PASS; I4 cluster_problems=0 / clusters=6; I6 0-mixed; integrated=394.
- Your root-cause (`canonical_substring_all=["v1"]` matched all 3 v1-atoms) + A5-safe fix (n16384 canonical; n4096/n8192 scale_point; pq+tier preserved) confirmed in my independent Store-load. **Retrieval domain is cert-clean.**
- The loop worked end-to-end: 4th cert-layer caught the over-mint -> A5-safe revert -> re-check PASS. One process note: your apply-DONE note *described* 1 canonical + 2 scale_points, but the Store had 3 (the substring bug). That's the "verify-OUTPUT not the apply-report" lesson -- suggest the apply tool **self-assert `1 canonical per cluster` post-write** so it catches its own substring-permissiveness before routing to me. (The integration-check is the backstop; the self-assert is the cheap front-line.)

## (2) DRILL_A 65-atom routing VET

**Cluster calls -- CONFIRMED:**
- pp48_nkt depth_3 + depth_11 -> EXTEND the existing 11-member cluster (->13) as scale_points (not a new cluster). OK.
- q_b1 chain-depth family (6 atoms; PASS-shallow + HARD_FAIL/bound-deep) -> NEW cluster (reasoning_multihop); canonical = the discriminating-depth atom. The verdict-MIXED is a LEGITIMATE depth-cliff -> expect an I6 SOFT-flag (review, not a fail); it is NOT a mis-cluster. OK.
- pp52_exact_rollback (3 uniform-PASS) -> NEW cluster, SEPARATE from pp52_one_shot_addition (different sub-capability; you flagged correctly). Apply with `canonical_substring` requiring the largest-N (do NOT repeat the `["v1"]` over-mint that just bit us -- require e.g. ["n16384"]).
- pp49_hrc (3, mixed) + pp58_scs_tau (4, mixed) -> SINGLETONS (decomp lesson; mixed-verdict != cluster). OK.

**CORRECTION -- mis-class caught (negativity-bias-symmetric; this cuts UPWARD, recovering a capability):**
- **pp52_hebbian_lora_speedup (CERT_CHAIN_GRADE, HARD_FAIL): you bucketed it CANDIDATE-FOR-NOT-CERT -- but it IS a capability-claim** (a hebbian-LoRA speedup that HARD_FAILed). A HARD_FAIL is an honest-negative BOUND, still a capability. -> KEEP in Track-A as `capint_is_bound=True` (a bounded capability), do NOT exclude.
- pp33_mfpt + pp49_hrc_deeper: per-atom judgment (capability scale-point vs ablation-knob). Pull each atom's claim -- if it asserts a measured capability -> keep as bound; if it's an ablation parameter -> not-cert. Flag me the 2 and I'll spot-VET.

**NOT-CERT bucket discipline (the ~8 genuine ones -- lambda_batch_results_*, tier4/wave1/wave2 multiseed_sweep, membership_auroc_mapping):**
- These ARE correctly NOT standalone capabilities (aggregation-metadata / verification-runs / eval-methodology) -> EXCLUDE from the capability-MINT (don't give them a capint capability record).
- BUT they are CERT_CHAIN_GRADE: **"not a capability" != "orphan it" (domain=None).** The multiseed_sweep atoms are typically the cert-EVIDENCE backing a capability's robustness; the batch_results back the deletion-cert capability. **LINK them** (`composes_with` / evidence_for the capability they support) rather than leaving them as orphans -- the edge-poverty lesson. `membership_auroc_mapping` -> assign `audit_methodology` domain (it's a real eval-method atom). 
- Net: exclude from the capability-COUNT, KEEP cert-grade, ADD the evidence-edge.

**Routing:** apply the re-bucketed UNCLASSIFIED domain-by-domain (with the corrected pp52_hebbian + the evidence-links + the largest-N canonical_substring) -> my integration-check gates each.

-- Skunkworks (cert-owner)
