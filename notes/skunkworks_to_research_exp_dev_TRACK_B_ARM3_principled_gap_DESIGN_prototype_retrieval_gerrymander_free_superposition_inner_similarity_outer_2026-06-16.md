# SKUNKWORKS (Auditor) -> Research + Exp-Dev: TRACK B -- ARM-3 principled-gap-narrowing DESIGN (DECISION 184c; DESIGN ONLY, no execution). GOAL: a structural criterion under which ONLY corr(bundle,c) closes, derived from INDEPENDENT task semantics (gerrymander-free), NOT reverse-engineered to exclude the other 7 closers. KEY STRUCTURAL INSIGHT: among the 8 closers, corr(bundle(a,b),c) is uniquely SUPERPOSITION-INNER (magnitude/similarity-preserving) + SIMILARITY-READOUT-OUTER. The strongest principled gap = PROTOTYPE/CENTROID-RETRIEVAL (a real independent task whose semantics naturally require exactly that). + a gerrymander-guard test. Design-only; I sign off gerrymander-free BEFORE any future (USER-gated) execution.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** TRACK_B_ARM3_principled_gap_DESIGN_prototype_retrieval_gerrymander_free_superposition_inner_similarity_outer

## Structural analysis of the 8 closers (why corr(bundle,c) is distinguishable WITHOUT target-fit)
The 8 closers = op2(symmetric-inner(a,b), c), symmetric-inner in {conv, xor, bundle}, outer in {corr, xor, conv}.
Two INDEPENDENT structural axes distinguish them (both derivable from op algebra, blind to the closer set):
```
  AXIS 1 -- INNER op character:
    bundle = SUPERPOSITION (additive; result stays SIMILAR to both a and b; magnitude/count-preserving)
    conv/xor = BINDING (multiplicative; result DISSIMILAR to a and b; similarity-destroying)
  AXIS 2 -- OUTER op character:
    corr = SIMILARITY READOUT (normalized similarity of inner-result to c; "how close is c")
    conv/xor = BINDING/UNBINDING readout (produces a vector, recovered by unbind; not a similarity score)
  corr(bundle(a,b),c) is the UNIQUE closer at the intersection: SUPERPOSITION-inner AND SIMILARITY-outer.
  Every other closer differs on >=1 axis (conv/xor-inner OR conv/xor-outer).
```
So uniqueness is achievable from an INDEPENDENT axis combination, not from "the op that isn't the others."

## CANDIDATE PRINCIPLED GAPS (gerrymander-free; uniqueness is a PREDICTION, tested blind at execution)
```
  CANDIDATE 1 (STRONGEST) -- PROTOTYPE / CENTROID RETRIEVAL:
    Task semantics (INDEPENDENT, from prototype-theory / VSA centroid literature): "given exemplars a, b of a
    category, retrieve the category PROTOTYPE c." The prototype IS the centroid = magnitude-preserving
    superposition of exemplars; retrieval is by SIMILARITY (nearest codebook entry to the centroid).
    -> STRUCTURALLY requires SUPERPOSITION-inner (centroid; conv/xor binding destroys the centroid) AND
       SIMILARITY-outer (nearest-to-centroid; unbinding is not similarity-retrieval).
    -> PREDICTS corr(bundle,c) uniquely closes; conv/xor-inner fail (no centroid); conv/xor-outer fail (no
       similarity readout). NOT target-fit: derived from prototype-retrieval semantics, which a third party could
       state WITHOUT knowing corr(bundle,c) is the answer.
  CANDIDATE 2 -- MAGNITUDE-SENSITIVE COMPLETION:
    Task whose correct answer DEPENDS on the count/magnitude of the a,b superposition (which bundle/superposition
    preserve, conv/xor binding destroy). Selects superposition-inner. (Weaker on AXIS 2 -- may not uniquely fix
    the outer; pair with a similarity-graded readout.)
  CANDIDATE 3 -- SIMILARITY-GRADED COMPLETION:
    Task where completion quality is GRADED by similarity (not binary unbind-success) -> requires the corr-outer
    similarity readout. Selects similarity-outer. (Weaker on AXIS 1 -- pair with C2 to fix both axes.)
  -> Candidate 1 fixes BOTH axes from a single independent task -> the clean principled gap. C2+C3 are the
     axis-decomposed fallback if C1's semantics prove hard to instantiate as a cell.
```

## GERRYMANDER-GUARD (the test the design MUST pass before I sign off)
```
  A criterion is PRINCIPLED (not gerrymander) iff it can be stated + a third party could DERIVE it from the TASK
  DESCRIPTION ALONE, BLIND to the closer set -- i.e., without ever referencing "corr(bundle,c)" or "exclude
  xor/conv." If the only way to state the gap is "the op the other 7 don't satisfy," it is GERRYMANDER -> BARRED.
  TEST for Candidate 1: "prototype = centroid of exemplars; retrieve by similarity" is stateable from prototype
  theory with ZERO reference to the substrate's op inventory -> PASSES the guard. The uniqueness of corr(bundle,c)
  is then a PREDICTION to be tested by BLIND search at execution (does corr(bundle,c) close + do the other 7 fail?),
  NOT an assumption built into the gap. If the blind search finds OTHER closers too -> the criterion did NOT
  uniquely select -> honest negative (still not a gerrymander, just not unique). Uniqueness must FALL OUT, not be
  imposed.
```

## Design status + sign-off conditions
- This is DESIGN ONLY (no cell-build, no execution) per DECISION 184c. 
- Exp-Dev (TRACK B): read-only SKETCH what Candidate 1 (prototype-retrieval) looks like as a verifiable cell-gate
  -- exemplar-pair -> centroid -> similarity-retrieval-of-prototype; the blind-search closer test; NO build yet.
- I (Skunkworks) will SIGN OFF a design as gerrymander-free ONLY IF: (a) the gap is stateable from independent
  task semantics blind to the closer set (Candidate 1 passes); (b) the uniqueness is a TESTED prediction not an
  assumption; (c) the blind-search protocol excludes the target from the seed (as ARM-3 already did -> no leakage).
- FUTURE EXECUTION is USER-gated (per DECISION 184c TRACK C / door-open); NOT auto-execute. If executed and
  corr(bundle,c) uniquely closes prototype-retrieval -> the ARM-3 uniqueness claim would be EARNED (honest, not
  gerrymandered). If not -> honest negative, finding stays QUALIFIED.

## Net
Principled gap DESIGNED (gerrymander-free): PROTOTYPE/CENTROID-RETRIEVAL uniquely requires corr(bundle,c)'s
superposition-inner + similarity-outer, derivable from prototype-theory semantics blind to the closer set.
This is the honest path to the ARM-3 uniqueness claim -- NOT chased now (USER-gated execution), but the design
is ready + gerrymander-guarded. TRACK A: I VET FORM-A backlog ratifies as they land (standard discipline).

Tag: TRACK_B_ARM3_principled_gap_DESIGN_two_independent_structural_axes_inner_superposition_vs_binding_outer_similarity_vs_binding_corr_bundle_c_unique_at_intersection_CANDIDATE_1_prototype_centroid_retrieval_strongest_fixes_both_axes_from_independent_task_semantics_C2_magnitude_C3_similarity_graded_axis_decomposed_fallback_GERRYMANDER_GUARD_stateable_from_task_description_blind_to_closer_set_uniqueness_is_tested_prediction_not_imposed_must_fall_out_design_only_no_execution_sign_off_conditions_future_USER_gated -- SKUNKWORKS (Auditor)
