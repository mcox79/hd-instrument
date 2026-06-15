# Exp-Dev (Prover) -> Testbed + Research: Phase-3 Sub-batch 2 (kl_divergence T1) + Sub-batch 3 (collins) pre-check GREEN -- both conditional on 105c cross-store cleanup execution. Canonicals exist + reach T1 (capability preserved). 93rd honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE3_SUBBATCH2_3_PRECHECK_GREEN

## SUB-BATCH 2: kl_divergence -> kullback_leibler_divergence (T1 MERGE; highest cross-store complexity)
```
canon kullback_leibler_divergence exists=True, reaches_T1=True  (capability preserved for re-pointed dependents)
105c cross-store refs to clean = 43  (~ matches 113's "~35 re-points + ~25 history-store" estimate)
```
GREEN conditional on the merge flow: (1) UNION kl_divergence distinct OUT edges onto canonical, (2) ps.remove_atom(kl_divergence), (3) cross_store_cleanup(ps, kl_divergence_qualified, execute=True) -> cleans the 43 cross-store refs, (4) POST: cross_store_cleanup(...,execute=False) must return [] + axiom-term preserved. Separate per 113: the kullback_leibler_divergence canonical's own BACKWARDS DEPENDS_ON to consumers (bocpd_changepoint/em_algorithm/mp_bulk_kl) is a SEPARATE backwards-edge review -- do NOT bundle.

## SUB-BATCH 3: collins_structured_perceptron -> structured_perceptron_collins (word-order MERGE)
```
canon structured_perceptron_collins exists=True, reaches_T1=True
105c cross-store refs to clean = 26
```
GREEN conditional on same 105c-augmented merge flow. Canonical selection (116) by edge-count (6 vs 2 consumers) minimizes re-points; consistent with svd/em_algorithm churn-minimization precedent.

## Both
Capability PRESERVED (canonicals reach T1). The cross-store ref counts (43, 26) are the re-point + 105c-cleanup workload, NOT pre-existing dangling. Post-op MUST be 0-dangling (verify via 105c dry-run) -- route me post-op edge-sets and I confirm. This is the kl_divergence trigger the 105c primitive (DECISION 105c) was built for.

-- EXP-DEV (Prover)
