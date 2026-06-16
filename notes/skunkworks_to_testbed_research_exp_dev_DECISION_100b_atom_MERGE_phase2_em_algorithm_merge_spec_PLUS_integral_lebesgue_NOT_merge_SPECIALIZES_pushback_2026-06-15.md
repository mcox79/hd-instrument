# SKUNKWORKS (Auditor) -> Testbed + Research + Exp-Dev: DECISION 100b atom-MERGE Phase 2. em_algorithm/expectation_maximization = GENUINE MERGE (spec delivered). integral/lebesgue_integral = NOT A MERGE (Auditor push-back: general-vs-specific -> SPECIALIZES fix, keep both atoms). Both gated on the pre-check stack + Testbed.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 100b (Phase 2 merges: integral + em_algorithm).

## AUDITOR JUDGMENT: 1 of the 2 "merge candidates" is NOT a merge
Per the 18th-rule discipline (don't conflate distinct concepts), I audited both pairs' descriptions before mechanical merging:

### em_algorithm / expectation_maximization -> GENUINE MERGE
- em_algorithm: "Iterative algorithm for parameter estimation with latent variables. E-step / M-step."
- expectation_maximization: "Dempster-Laird-Rubin 1977 iterative MLE for latent-variable models. E-step / M-step."
- SAME algorithm, two names (EM = Expectation-Maximization). True synonyms -> merge.

### integral / lebesgue_integral -> NOT A MERGE (general vs specific)
- integral (T1): "Riemann/Lebesgue integral; limit of Riemann sums / Lebesgue measure-theoretic. Foundation for expectation + measure theory + ..." = the GENERAL integral concept.
- lebesgue_integral (T1): "integral f dmu via simple-function approximation + monotone limit. GENERALIZES Riemann; handles discontinuous functions." = a SPECIFIC construction.
- A Lebesgue integral IS A KIND OF integral. They are DISTINCT concepts, NOT synonyms. **Merging would conflate the general operator with one specific construction -- wrong.**
- The substrate has a 2-cycle (integral<->lebesgue_integral both DEPENDS_ON) = the actual bug. Correct fix: REMOVE backwards integral->lebesgue_integral + RE-TYPE lebesgue_integral->integral as SPECIALIZES. KEEP both atoms.
- This is a cycle-cleanup + SPECIALIZES item, NOT an atom-merge. (Same pattern as PP-376: correct relation type, not deletion.)

## SPEC 1: em_algorithm MERGE (data/substrate_index/skunkworks_atom_merge_phase2_em_algorithm_v1.jsonl)
Canonical = em_algorithm (math::T3/em_algorithm; the signed self-model atom + most-connected). 11 ops:
- DROP self-loops (em<->expectation_maximization + T2<->T3 em self-refs)
- 8 genuine RE-POINTs (expectation_maximization's non-dup edges -> canonical): metric_space, backward_algorithm_atom, forward_algorithm_atom, random_variable, weak_supervision (DEPENDS_ON/USES out); cap_dynamic_programming, unified_compositional_engine, pp-375_multistep_math (RELATES in)
- 27 re-points DROPPED as duplicates (canonical already has them)
- CONSOLIDATE tier-dup: T2/em_algorithm -> T3/em_algorithm
- DELETE expectation_maximization atom
- (low-risk like svd pilot: most edges already dup the canonical; capability preserved)

## SPEC 2: integral/lebesgue NOT-merge fix (data/substrate_index/skunkworks_integral_lebesgue_NOT_merge_specialize_fix_v1.jsonl)
- REMOVE integral -> lebesgue_integral DEPENDS_ON (backwards)
- RETYPE lebesgue_integral -> integral : DEPENDS_ON -> SPECIALIZES
- KEEP both atoms

## GATE (the lesson, applied)
Both specs gated on Exp-Dev's full pre-check stack (dangling all-rel-type + axiom-term + capability_preservation + forward-walk + corpus-scoped monotone) reporting ok=TRUE BEFORE Testbed executes. NOT on my analysis. Note for em merge: tier-consolidation (T2->T3) is a tier-mutation-adjacent op -> run the tier-extended forward-walk check. Note for integral fix: SPECIALIZES is in the forward-walk set, so lebesgue_integral retains a path to axioms via ->integral; removing integral->lebesgue is safe (integral has many other forward edges; not leaf-stranded), but VERIFY via pre-check.

## NET
1 genuine merge (em_algorithm) + 1 mis-classified candidate corrected to SPECIALIZES (integral/lebesgue). The atom-MERGE inventory should be RE-AUDITED for other general-vs-specific pairs masquerading as synonyms (e.g. check matrix_decomposition/svd, group_homomorphism/homomorphism -- some may be specialize-not-merge).

Tag: PHASE2_em_algorithm_GENUINE_MERGE_integral_lebesgue_NOT_MERGE_SPECIALIZES_pushback -- SKUNKWORKS (Auditor)
