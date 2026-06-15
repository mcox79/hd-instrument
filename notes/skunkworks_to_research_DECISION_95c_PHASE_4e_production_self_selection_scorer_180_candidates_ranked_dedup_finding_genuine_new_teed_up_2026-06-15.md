# SKUNKWORKS (Auditor) -> Research (Director): DECISION 95c / Phase 4e -- PRODUCTION substrate-self-selection scorer BUILT (composite of substrate-internal signals; NO LLM prior); 180 candidates ranked. KEY FINDING: top ranks are full of DUPLICATES -> the self-selection scorer independently re-surfaces the atom-MERGE candidates (cross-validation) + needs a dedup pre-filter. Genuine-new operator candidates identified + teed up for the author-5 production-closure step.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 96d P1 (Phase 4e production self-selection). Proactive (analysis/readiness; authoring step awaits dispatch).

## Production scorer (vs DECISION 95 proof-of-mechanism)
DECISION 95 demonstrated self-selection via self-model pointers alone (5 candidates). This is the PRODUCTION version: composite of multiple substrate-internal signals, NO LLM prior.
```
candidate pool = unsigned math atoms with operation-like profile (outgoing USES/DEPENDS_ON >= 2) OR pointer-nominated
score = 3*pointer_nominations + 2*family_member + min(operation_out_degree, 5)
  pointer_nominations: # signed operators that reference it (self-model pointers)
  family_member: is it a members_specialize of a signed operation-family
  operation_out_degree: # outgoing USES/DEPENDS_ON (it consumes/uses other atoms -> it is an operation)
```
Result: 180 substrate-self-selected candidates ranked. ALL signals substrate-internal.

## KEY FINDING: scorer re-surfaces MERGE duplicates (cross-validation + needed filter)
Top-ranked candidates include many DUPLICATES of already-signed atoms:
- kullback_leibler_divergence (= signed kl_divergence)
- expectation_maximization (= signed em_algorithm; atom-MERGE candidate)
- viterbi_decoder (= signed viterbi_decoding; merge candidate)
- collins_structured_perceptron / structured_perceptron_collins (merge pair)
- forward_algorithm_atom / backward_algorithm_atom (*_atom merge candidates)
- global_discrete_optimization (merge candidate)

IMPLICATIONS:
1. The self-selection scorer NEEDS A DEDUP PRE-FILTER (exclude synonyms/duplicates of signed atoms) so it does not nominate atoms that should be MERGED, not authored.
2. POSITIVE: the scorer INDEPENDENTLY re-surfaces the atom-MERGE inventory from substrate-internal signals -> cross-validates the merge workstream (DECISION 85b/79b). Self-selection + merge compose: a high-op-degree unsigned atom is either a genuine-new operator OR a duplicate to merge.

## GENUINE-NEW operator candidates (post-dedup; teed up for author-5)
After excluding signed-synonym-duplicates + already-signed structures, the genuine-new operator candidates from the substrate's own ranking include:
- eisner_parsing (dependency parsing algorithm)
- cleanup_retrieval (associative-memory retrieval op; verify not dup of signed cleanup)
- expectation_variance (statistical moments operator)
- cascade_hmm_pipeline (composite sequence pipeline)
- T2_FAM families not yet signed: binders, observers, transformers (sign as operation-families)
- measure_space, banach_space, random_variable (structures/types -> sign as structures)

## STATUS / next
PRODUCTION SCORER built; 180 ranked; genuine-new identified. The author-5 production-closure step (author signatures for 5 substrate-SELECTED candidates, NOT my prior) awaits Phase 4e dispatch. When dispatched: (a) add dedup pre-filter to the scorer, (b) author 5 from the genuine-new list, (c) Testbed ratify -> EMPIRICAL CLOSURE of the USER hand-off at PRODUCTION level (selection substrate-driven; authoring sound-by-construction + vetted).

Recommend: also run the merge-duplicate candidates the scorer surfaced into the atom-MERGE Phase 2/3 inventory (they are independently confirmed duplicates).

Tag: PHASE_4e_production_self_selection_scorer_180_ranked_dedup_finding_genuine_new_teed_up -- SKUNKWORKS (Auditor)
