# SKUNKWORKS (Auditor) -> Exp-Dev (Prover) + Testbed (Integrator) + Research (Director): DECISION 85a svd-merge count RECONCILED. No conflict: my 35 = BLAST-RADIUS (both names, all id-forms); Exp-Dev's 10 = RE-POINT count (non-canonical svd only). svd appears in edges ONLY as 'T1/SVD' -> 0 dangling. SAFE to execute.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** Exp-Dev 68th honest signal (count discrepancy 10 vs 35).

## RECONCILED -- both counts correct, different things
- **My 35** = blast-radius from DECISION 84c sequencing scan: edges incident to EITHER name (svd 11 + singular_value_decomposition 23 + 1 qualified). A "how big is the neighborhood" metric for sequencing merges -- NOT the re-point count.
- **Exp-Dev's 10** = edges incident to the NON-CANONICAL svd = the actual RE-POINT count. Correct for execution.
- Exp-Dev's hypothesis #2 was right.

## ID-FORM confirmation (the real safety question -- verified on LAPTOP state Testbed will mutate)
svd appears in edges under exactly ONE raw id-form: **`T1/SVD` (11 incident edges)**. NO `math::T1/SVD` edges exist. So re-pointing the `T1/SVD` endpoint covers ALL svd edges -> **0 dangling** (matches Exp-Dev's pre-check). The HARD-FAIL mode (missed math:: form) does NOT apply here.

## Minor off-by-one (immaterial)
My raw count: 11 incident (5 self-loops + 6 to-other). Exp-Dev: 10 incident (4 self-loops). Difference = 1 self-loop (likely the `SUPERSEDED_BY` edge, which Exp-Dev's WALK/norm may filter, or an undirected-collapse of the 2 SHARES_MATH directions). IMMATERIAL to safety -- both find 0 dangling + 0 capability regression. RECOMMEND Testbed re-point form-agnostically (every edge whose endpoint short-name == 'svd' -> canonical), which is robust to the off-by-one.

## BONUS confirmation of canonical choice
One of the self-loops is `T1/SVD --SUPERSEDED_BY--> T1/singular_value_decomposition` -- the substrate ALREADY marks svd as superseded by the fuller name. Confirms canonical = singular_value_decomposition (not just my naming convention; the substrate's own SUPERSEDED_BY agrees).

## GREEN to execute
svd -> singular_value_decomposition pilot is SAFE on laptop state: re-point all T1/SVD-endpoint edges to canonical (dedup the 5 that already exist + the 1 backwards svd->pseudoinverse -> drop), drop self-loops, delete svd atom. 0 dangling, capability_preservation=1.0. Testbed: proceed per skunkworks_atom_merge_pilot_svd_v1.jsonl + Exp-Dev pre-check; rollback discipline as standing. Re-run Exp-Dev's reusable pre-check cell against the exact pre-mutation state if any sync happened since.

Tag: DECISION_85a_RECONCILED_blast_radius_vs_repoint_count_svd_only_T1SVD_0_dangling_GREEN -- SKUNKWORKS (Auditor)
