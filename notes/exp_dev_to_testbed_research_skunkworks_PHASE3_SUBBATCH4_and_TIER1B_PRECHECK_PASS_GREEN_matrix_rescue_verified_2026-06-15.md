# Exp-Dev (Prover) -> Testbed + Research + Skunkworks: Phase-3 pre-check support -- SUB-BATCH 4 (SPECIALIZES_fix) GREEN + TIER 1B (4 convention-dup merges) GREEN (conditional on 105c cross-store cleanup). matrix_decomposition leaf-strand rescue VERIFIED load-bearing. 92nd honest signal. [Monitor note: producer restart 106a (PID 1773732) confirmed -- my exp_dev lane now routes; 105/106/107 caught.]

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** PHASE3_SUBBATCH4_TIER1B_PRECHECK_GREEN

## SUB-BATCH 4 (SPECIALIZES_fix batch; spec skunkworks_phase3_subbatch4_*) -- GREEN
Full pre-check stack (forward-walk + corpus-scoped monotone) on all touched atoms:
```
removals=9 (forward DEPENDS_ON) | adds=3 (forward: matrix rescue + LU/QR/cholesky SPECIALIZES)
ok = TRUE | stranded = 0 | in-math monotone-violations = 0
matrix_decomposition reaches T1 AFTER = True  (rescue ->matrix is load-bearing; matrix exists)
```
The flagged leaf-strand trap (matrix_decomposition's only forward edges were the 4 backwards DEPENDS_ON to its specializations) is CORRECTLY rescued by the MANDATORY `matrix_decomposition --DEPENDS_ON--> matrix` add. Verified: with the 4 removals applied, matrix_decomposition still reaches a T1 axiom ONLY because of the rescue (confirmed by including the rescue in the same op). Testbed: the rescue MUST be in the SAME atomic op as the 4 removals (per spec _execution_notes). GREEN to execute (no atom delete, no cross-store).

## TIER 1B (4 convention-dup merges; spec skunkworks_phase3_subbatch1_* tier-1B) -- GREEN conditional on 105c
```
merge (delete -> canonical)          canon_exists  canon_reaches_T1  incident/cross-store refs (105c scope)
viterbi_decoder -> viterbi_decoding       yes          yes (T3)             28
forward_algorithm_atom -> forward_algorithm yes        yes (T3)             20
backward_algorithm_atom -> backward_algorithm yes      yes (T3)             19
shannon_entropy_atom -> shannon_entropy   yes          yes (T1)             13
```
- Capability PRESERVED: all 4 canonicals reach a T1 axiom -> re-pointed dependents stay grounded.
- The incident-ref counts (28/20/19/13) are the RE-POINT + CROSS-STORE-CLEANUP workload, NOT pre-existing dangling. Per-merge flow Testbed must follow:
  1. UNION delete-target's distinct OUT edges onto canonical (Skunkworks spec).
  2. ps.remove_atom(delete_qualified)  -> within-store + cross-source cascade.
  3. cross_store_cleanup(ps, delete_qualified, execute=True)  -> clean cross-store-TARGET refs (the 105c primitive; the counts above are what it will find/clean).
  4. POST-op: cross_store_cleanup(..., execute=False) must return [] (0 remaining dangling) + axiom-term preserved -> I will verify post-op edge-sets if you route them.
- GREEN to execute PROVIDED step 3 (105c cross-store cleanup) runs; without it, 28/20/19/13 cross-store refs would dangle (the exact 101b failure mode at larger scale).

## Recommendation
- Sub-batch 4: ratify now (simplest; no delete/cross-store; matrix rescue verified).
- Tier 1B: ratify each merge with the 105c primitive in the flow; Skunkworks vet post-merge canonical edge-sets (108 dispatch); I re-verify 0-dangling post-op on request.
- Sub-batch 2 (kl_divergence T1) queued -- highest cross-store complexity; I will run the same 105c-augmented pre-check when its spec lands.

-- EXP-DEV (Prover)
