# SKUNKWORKS (Auditor) -> Research + Exp-Dev: (1) CONSTRUCT-1 3-op vet = PLAUSIBLE-authored (agree with Exp-Dev's prediction). (2) PRE-EMPTIVE flag on CONSTRUCT-2 BEFORE the 2-4-day build: its utility tests (Req 3a close-open-derivation, 3b bridge) are SCALE-CONFOUNDED by the thin load-bearing core -- a HARD_FAIL would be AMBIGUOUS (scale-artifact vs novelty-bound). Recommend a precondition check so the result is interpretable. This is the USER's depth-of-math point applied to the test design.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 133c (vet the 3 ops) + 134a (CONSTRUCT-2 design) + 134b (standing vet).

## (1) Vet of CONSTRUCT-1's 3 construction operations: PLAUSIBLE-authored (NOT STRICT)
quotient / completion / tensor_product: per my 128b rubric -- SOUND (textbook-correct, produce genuine new carriers, 4-gate pass) BUT (a) AUTHORED-SUPPLIED (Exp-Dev provided the schemas from math knowledge = external knowledge source, like Phase 4a), (b) HOLLOW utility (0 open derivations closed; bridges=1), (c) carrier-extension ASSERTED not measured. -> PLAUSIBLE-authored, NOT autonomous-novelty-STRICT. I CONCUR with Exp-Dev's self-flag and prediction. CONSTRUCT-1 does NOT refute grounding-bound; the construction PATH is plausible + the validator handles construction outputs (real positive), but autonomous-construction-novelty-with-real-utility is UNTESTED.

## (2) PRE-EMPTIVE CONFOUND FLAG on CONSTRUCT-2 (verify-before-asserting, applied to the test BEFORE it runs)
CONSTRUCT-2's REAL-utility requirements are:
- Req 3a: find an atom X currently NOT reaching axioms (an OPEN derivation) that a construction CLOSES.
- Req 3b: a construction that BRIDGES >=2 existing result chains (compression).
- Req 4: wire a construction output into a module + measure a benchmark delta.

THE CONFOUND: all three utility signals are STARVED BY THE THIN LOAD-BEARING CORE (the structural fact from today's data-vs-atoms scan + CONSTRUCT-1's hollow result):
- The proof corpus is ~42 lemma/synthesis atoms and the substrate maintains 217/217 axiom-termination (everything ALREADY reaches axioms by invariant). So there are essentially ZERO genuinely-OPEN derivations for Req 3a to close -- not because constructions can't close them, but because the substrate has no thin frontier of unproven-but-provable results. CONSTRUCT-1 already hit exactly this (result_term_before=True for all 3).
- Bridgeable result-clusters (Req 3b) require a dense-enough result corpus that >=2 chains share a compressible sub-structure; at 816 atoms with 2+ edges and 42 proofs, the bridge targets are sparse.
- Empirical utility (Req 4) is MISMATCHED: the modules (HMM/NER/perceptron/Bayes/EM) are NLP/ML tasks; a new pure-MATH construction (quotient/tensor space) has no benchmark that measures its math-utility. A quotient group will not move an NER score.

CONSEQUENCE: a CONSTRUCT-2 HARD_FAIL would be AMBIGUOUS between:
  (b1) substrate-internal construction-novelty is genuinely bounded (the intended conclusion), vs
  (b2) the substrate is too THIN to contain the utility targets (open derivations / bridge clusters / math-native benchmarks) that would let a real construction DEMONSTRATE utility (the USER's depth-of-math point; the likely confound).
These are DIFFERENT conclusions. As-designed, CONSTRUCT-2 cannot distinguish them -- so a HARD_FAIL would NOT validly establish grounding-bound; it would re-establish the scale limitation.

## RECOMMENDATION (make CONSTRUCT-2 interpretable; cheap precondition)
Before/within CONSTRUCT-2, run a PRECONDITION CHECK on whether the utility targets even EXIST:
  - Count genuinely-OPEN derivations (atoms not reaching axioms) -- if ~0 (likely, given 217/217), Req 3a CANNOT fire regardless of construction quality -> a Req-3a miss is a SCALE finding, not a novelty finding. Report it as such.
  - Count bridgeable result-clusters (>=2 chains sharing compressible substructure) -- if sparse, Req 3b is starved.
  - Confirm NO math-native benchmark exists for Req 4 (the ML modules don't measure math-utility).
If the precondition shows the utility targets are absent/starved: CONSTRUCT-2 should report "utility UNTESTABLE at current scale" rather than HARD_FAIL -> which empirically CONFIRMS the depth-of-math limitation (USER's point) and redirects to the real lever: GROW THE LOAD-BEARING CORE (proof corpus + math-native utility targets) FIRST, then re-run CONSTRUCT-2. This is the honest interpretation that does not over-claim a novelty-bound from a scale-starved test.

## Net (ties the thread together)
- grounding-bound (needs external truth): RETRACTED/over-claimed (my 5x drill; accepted).
- construction is the right MECHANISM class: confirmed plausible (CONSTRUCT-1 validator handles it).
- BUT autonomous-construction-novelty CANNOT be validly tested until the load-bearing core (esp. proof corpus + math-native utility) is grown -- the USER's depth-of-math point, now reinforced by CONSTRUCT-1's hollow utility AND by the data-vs-atoms structure (91pct of atoms are disconnected DATA; the functional core is ~hundreds; the proof corpus is 42).
- So the honest next step is NOT CONSTRUCT-2-as-novelty-test (scale-confounded) -- it is GROW THE LOAD-BEARING MATHEMATICAL CORE, then test. I recommend the basis-spec (target one construction-rich field; grow its operators + relations + proof corpus to a frontier) as the real path, with CONSTRUCT-2 sequenced AFTER, or run NOW only as the precondition-check that confirms utility-untestable-at-current-scale.

## Standing
ITEM 1 (bilateral kappa design) delivered; ITEM 2 (content audit) delivered (systemic backwards-edges); CONSTRUCT-2 standing vet acknowledged (134b) with the confound flag above. Holding for USER greenlight on the basis-spec.

Tag: DECISION_134_CONSTRUCT_1_vet_PLAUSIBLE_authored_CONSTRUCT_2_SCALE_CONFOUND_utility_targets_starved_by_thin_core_HARD_FAIL_would_be_ambiguous_precondition_check_grow_core_first -- SKUNKWORKS (Auditor)
