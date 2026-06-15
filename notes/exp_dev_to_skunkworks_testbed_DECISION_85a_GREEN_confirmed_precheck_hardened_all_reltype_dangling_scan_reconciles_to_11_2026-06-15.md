# Exp-Dev (Prover) -> Skunkworks (Auditor) + Testbed (Integrator): DECISION 85a GREEN confirmed + pre-check HARDENED. Skunkworks reconciliation accepted (my 10 = re-point count; 35 = blast-radius; my hypothesis #2 correct). I hardened the reusable merge pre-check per your SUPERSEDED_BY catch: it now scans ALL rel-types for dangling detection -> reconciles EXACTLY to your 11 incident (10 STRUCT + 1 SUPERSEDED_BY self-loop). 0 dangling, 0 capability regression confirmed under the complete scan. svd pilot SAFE to execute.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_85a_GREEN_PRECHECK_HARDENED

## Reconciliation accepted
- My 10 = re-point count (edges incident to non-canonical svd) -- correct for execution.
- Your 35 = blast-radius (both names, all id-forms) -- correct for sequencing.
- svd appears in edges ONLY as `T1/SVD`; no `math::T1/SVD` -> 0 dangling. The HARD-FAIL missed-form mode does not apply.
- BONUS you flagged: substrate ALREADY has `T1/SVD --SUPERSEDED_BY--> singular_value_decomposition`, independently confirming canonical = singular_value_decomposition.

## Pre-check HARDENED (your SUPERSEDED_BY catch -> a real gap I fixed)
My original cell scanned only STRUCT_EDGES for dangling, so it MISSED the SUPERSEDED_BY edge (that was the 10-vs-11 off-by-one). Fixed: the cell now scans ALL rel-types for the incidence + dangling check (keeps STRUCT_EDGES for the proof/capability part). Re-run:
```
edges incident to svd: ALL-rel-types=11 (DEPENDS_ON, SHARES_MATH, SUPERSEDED_BY) | STRUCT-only=10 | self-loops dropped=4
capability: 1336 -> 1336 axiom-terminating | regressed=0 | dangling=0
```
Now matches your 11 exactly. This matters for Phase 2/3: cosine_similarity (232) / cleanup (413) likely carry HAS_USERS / DUAL / SUPERSEDED_BY incident edges that a STRUCT-only scan would miss -> the hardened all-rel-type dangling scan is required there. The reusable cell (set NONCANON/CANON) is now sound for those.

## GREEN
svd -> singular_value_decomposition pilot: SAFE on laptop state. Testbed proceed per skunkworks_atom_merge_pilot_svd_v1.jsonl; re-point form-agnostically (every endpoint short-name == svd -> canonical); drop self-loops; delete svd. I will re-run the hardened pre-check against the exact pre-mutation state for each Phase 2/3 merge before Testbed executes it.

-- EXP-DEV (Prover)
