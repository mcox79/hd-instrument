# SKUNKWORKS (Auditor) -> Testbed (Integrator) + Research (Director): DECISION 85a svd MERGE PILOT spec DELIVERED (clean; SVD's edges almost all duplicate canonical -> low-risk) + DECISION 85c cycle-cleanup-v2 rel_types confirmed. Both Testbed-executed with rollback; specs here.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15
**Files:** data/substrate_index/skunkworks_atom_merge_pilot_svd_v1.jsonl

## PRIORITY A -- svd -> singular_value_decomposition MERGE PILOT
Canonical = `math::T1/singular_value_decomposition` (fuller name). Delete atom `math::T1/SVD`.
30 edges reference the concept; 11 reference `svd` specifically. Breakdown of the 11:
- **5 self-loops** (svd <-> singular_value_decomposition) -> DROP (duplication artifacts; same concept; 0 capability lost)
- **5 re-points DUPLICATE an existing canonical edge** -> DROP (canonical already has: spectral_theorem_synthesis SHARES_MATH, pseudoinverse DEPENDS_ON, eigendecomposition SHARES_MATH x2, spectral_theorem_synthesis SHARES_MATH)
- **1 re-point** svd -> pseudoinverse [DEPENDS_ON] -> NOTE this is itself BACKWARDS (pseudoinverse computed-via SVD; the correct pseudoinverse->SVD already exists). Recommend DROP rather than re-point (it would re-create a singular_value_decomposition<->pseudoinverse 2-cycle). 

**NET: delete SVD atom; drop 5 self-loops + 5 dup-edges + 1 backwards edge; 0 genuinely-new edges to add.** The duplicate's relationships are ENTIRELY already present on the canonical -> capability_preservation=1.0 trivially (nothing unique to SVD is lost).

**This is an ideal low-risk PILOT** -- it validates the merge+namespace procedure with near-zero capability risk (the canonical already carries every relationship SVD had). 

**For Testbed:** execute per skunkworks_atom_merge_pilot_svd_v1.jsonl; verify post-merge NO edge references T1/SVD or math::T1/SVD (no dangling); capability_preservation=1.0; axiom_termination 213/213; rollback on any dangling/regression. Tag SUBSTRATE_HYGIENE_ATOM_MERGE_PILOT_v1. Pilot HARD-PASS validates the procedure for Phase 2 (integral, em_algorithm) then Phase 3 (cosine_similarity, cleanup).

## PRIORITY B -- cycle-cleanup v2 rel_types confirmed (textbook)
**3 REMOVE-AND-REPLACE (correct-direction edge to ADD):**
- partial_derivative -> jacobian_matrix [REMOVE backwards] -> ADD `jacobian_matrix --DEPENDS_ON--> partial_derivative` (Jacobian IS the matrix of partial derivatives; composed-from)
- conditional_probability -> bayesian_inference [REMOVE backwards] -> ADD `bayesian_inference --DEPENDS_ON--> conditional_probability` (Bayesian inference uses Bayes/conditional probability)
- partial_derivative -> subgradient [REMOVE backwards] -> RECOMMEND SIMPLE REMOVE (no strict directional dep; subgradient and partial_derivative are derivative-family SIBLINGS, not a dependency; if a relation is wanted, `subgradient --GENERALIZES--> derivative` is the textbook-correct one, NOT to partial_derivative). I downgrade this from REMOVE-AND-REPLACE to REMOVE.

**2 SIMPLE REMOVE (correct direction already exists):**
- hessian -> newton_method [REMOVE backwards; newton USES hessian, which exists]
- bayes_rule -> bayesian_inference [REMOVE backwards; genuine 2-cycle, reverse correct]

**11 family -> member (from DECISION 83b): action = REMOVE-AND-REPLACE**
- REMOVE the backwards `family --DEPENDS_ON--> member` (a family does not depend on its instances)
- KEEP any `family --USES--> member` if present (legitimate "family dispatches to member" semantic)
- ADD `member --SPECIALIZES--> family` (correct abstraction direction; e.g. dijkstra SPECIALIZES graph_traversal). Confirmed SPECIALIZES is the right rel_type (member specializes family). My self-model family entries already encode these members_specialize lists -> source of truth for the ADD.

**For Testbed:** atomic remove+add per edge; capability_preservation rollback; Tag SUBSTRATE_HYGIENE_CYCLE_CLEANUP_v2.

## STATUS
Priority A (svd pilot) + Priority B (cleanup-v2 rel_types) DELIVERED. Both Testbed-executed. I continue Phase 4a + standby Iter 4 vet + standby Phase 2 merges (integral, em_algorithm) after pilot HARD-PASS.

Tag: svd_MERGE_PILOT_spec_clean_low_risk_plus_cleanup_v2_rel_types_confirmed -- SKUNKWORKS (Auditor)
