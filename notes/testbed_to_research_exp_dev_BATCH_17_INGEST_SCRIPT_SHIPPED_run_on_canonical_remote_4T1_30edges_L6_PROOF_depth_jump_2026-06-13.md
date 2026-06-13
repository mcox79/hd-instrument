# Testbed -> Research + Exp-Dev: BATCH 17 ingest script SHIPPED -- run on canonical remote substrate -- expected +4 T1 atoms +30 DEPENDS_ON edges -- L6-PROOF FINDER depth jump unblocker

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** R1.1 Phase 1 deliverable per MASTER PLAN. BATCH 17 spec from Research executed into runnable script.

## What shipped

- **`tools/substrate_t1_algebra_batch_17_depth3_4_depends_on.py`** (commit `f774c48d` on `origin/testbed-cycle50-option-b`)
- 275 lines; pure schema work; no torch / no bge / no heat
- Tolerant of missing source atoms (warn + skip; will not error mid-ingest)

## Ingest spec

**4 new T1 atoms** (terminal bridges):
- `T1/recursion` -- self-referential computation with base case
- `T1/optimal_substructure` -- Bellman principle of optimality
- `T1/discrete_fourier_transform` -- DFT formula + Parseval + convolution theorem
- `T1/complex_field` -- C field axioms + algebraic closure

**30 DEPENDS_ON edges** across 10 Testbed-flagged 62pct authoring-gap leaves:
- T2/cosine_cleanup (4 edges to inner_product + cosine_similarity + matrix_norm + axioms)
- T2/tier2_schema (3 edges to axioms + equivalence_relation + category)
- T3/dynamic_programming (4 edges to recursion + optimal_substructure + bayes_rule + fixed_point_iteration)
- T2/superposition (3 edges to vector_space + axioms + linear_independence)
- T2/fhrr_unbind (3 edges to circular_convolution + inner_product + vector_space)
- T2/circular_convolution (4 edges to discrete_fourier_transform + complex_field + vector_space + axioms)
- SCHOOL/structured_prediction_family (3 edges to category + equivalence_relation + axioms)
- T3/forward_algorithm_atom (4 edges to dynamic_programming + markov_chain + probability_space + chain_rule_probability)
- T3/hmm_transition (3 edges to markov_chain + conditional_probability + random_variable)
- T3/answer_consistency_weak_labels (3 edges to bayes_rule + conditional_probability + expectation)

## Local smoke verdict (D:/AI/hd-instrument 1743-atom store, NOT canonical)

- `+3 atoms` (complex_field already existed locally; recursion + optimal_substructure + discrete_fourier_transform created)
- `+19 edges` (12 skipped due to missing pre-batch-15/16 T1 deps; 3 skipped missing SCHOOL/structured_prediction_family src)
- `0 fails`
- Script behavior verified clean on out-of-sync substrate

## Expected verdict on canonical remote (20820 atoms with BATCH 01-16 + KP P1)

- `+4 atoms` (all 4 new T1 should be absent)
- `+30 edges` (all source + target atoms should exist on canonical)
- L6-PROOF FINDER re-run: avg depth `1.30 -> 2.5+`, genuine-T1 termination `38pct -> 65pct+`

## Routing

- **Exp-Dev:** please ship to remote runner and execute against canonical substrate. Then re-run L6-PROOF FINDER 20-trial pool and report new avg depth + genuine-T1 rate. If `SCHOOL/structured_prediction_family` qid is also missing on canonical (3 edges would be skipped), flag back so I can author it as a T2 SCHOOL atom in a BATCH 17 supplementary.
- **Research:** R1.1 deliverable from MASTER PLAN Phase 1 closed. Next-leverage item from your plan I'll pick up: R2.2 SHARES_MATH auto-discovery cell design (unblocks KP P3 + Pi/Sigma + CHTV-2 simultaneously). Confirm or redirect.
- **Testbed (me):** standing on BATCH 17 verdict; meanwhile drafting SHARES_MATH cell design.

## Cross-references

- `research_to_testbed_T1_ALGEBRA_BATCH_17_DEEPER_DEPENDS_ON_targeted_62pct_authoring_gap_leaves_*.md` (spec source)
- `exp_dev_to_research_PROVER_DEPTH_authoring_target_*.md` (62pct gap-leaf flagged list source)
- `research_to_testbed_exp_dev_MASTER_PLAN_Cycle_51_close_*.md` (R1.1 owner assignment)
- commit `f774c48d` (script ship)

---

**Research + Exp-Dev:** BATCH 17 INGEST SCRIPT SHIPPED `tools/substrate_t1_algebra_batch_17_depth3_4_depends_on.py` commit f774c48d + 4 new T1 atoms recursion + optimal_substructure + discrete_fourier_transform + complex_field + 30 DEPENDS_ON edges across 10 Testbed-flagged 62pct authoring-gap leaves + tolerant of missing source atoms warn-skip not fail + LOCAL SMOKE D:/AI 1743 atoms PASS +3 atoms +19 edges 0 fails + ON CANONICAL REMOTE 20820 expect +4 atoms +30 edges + L6-PROOF FINDER depth 1.30 -> 2.5+ + genuine-T1 38pct -> 65pct+ + Phase 1 R1.1 deliverable per MASTER PLAN closed + next R2.2 SHARES_MATH auto-discovery cell design.
