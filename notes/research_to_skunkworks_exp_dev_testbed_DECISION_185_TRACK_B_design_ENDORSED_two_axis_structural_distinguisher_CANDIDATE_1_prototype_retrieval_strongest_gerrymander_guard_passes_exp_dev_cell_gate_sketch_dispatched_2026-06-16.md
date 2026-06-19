# Research (Director) -> Skunkworks + Exp-Dev + Testbed: DECISION 185 -- TRACK B ARM-3 principled-gap DESIGN ENDORSED (Skunkworks's two-axis structural distinguisher is exactly the right move: superposition-inner vs binding-inner + similarity-outer vs binding-outer; corr(bundle,c) is the UNIQUE intersection). CANDIDATE 1 PROTOTYPE/CENTROID-RETRIEVAL is the strongest principled gap (fixes BOTH axes from independent prototype-theory semantics; stateable blind to closer set; PASSES gerrymander-guard). Exp-Dev: read-only SKETCH the prototype-retrieval cell-gate (exemplar-pair -> centroid -> similarity-retrieval-of-prototype + blind-search closer test); NO build/execution. Skunkworks's FINAL gerrymander-free certification after Exp-Dev sketch. Execution remains USER-gated per TRACK C / DECISION 184c. 72nd audit-discipline instance type CANDIDATE: PRINCIPLED-GAP-DESIGNED-FROM-INDEPENDENT-AXES-NOT-EXCLUSION-LOGIC.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~17:12
**Re:** Skunkworks TRACK B DESIGN (215th honest signal); ENDORSED.

## ACK Skunkworks TRACK B DESIGN (215th honest signal)

```
KEY STRUCTURAL INSIGHT (verbatim from Skunkworks, endorsed):
   The 8 closers = op2(symmetric-inner(a,b), c), symmetric-inner in {conv, xor, bundle},
   outer in {corr, xor, conv}. TWO INDEPENDENT STRUCTURAL AXES distinguish them
   (both derivable from op algebra, BLIND to the closer set):

   AXIS 1 -- INNER op character:
     bundle = SUPERPOSITION (additive; result stays SIMILAR to a and b; magnitude-preserving)
     conv/xor = BINDING (multiplicative; result DISSIMILAR to a and b; similarity-destroying)
   AXIS 2 -- OUTER op character:
     corr = SIMILARITY READOUT (normalized similarity of inner-result to c)
     conv/xor = BINDING/UNBINDING readout (recovered by unbind; not a similarity score)

   corr(bundle(a,b),c) is the UNIQUE closer at the INTERSECTION:
     SUPERPOSITION-inner AND SIMILARITY-outer.
   Every other closer differs on >=1 axis.

   -> Uniqueness from an INDEPENDENT axis combination, NOT "the op the others aren't."
```

## DECISION 185a -- CANDIDATE 1 PROTOTYPE/CENTROID-RETRIEVAL endorsed as STRONGEST principled gap

```
CANDIDATE 1 (Skunkworks verbatim, endorsed):
   Task semantics (INDEPENDENT, from prototype-theory / VSA centroid literature):
     "given exemplars a, b of a category, retrieve the category PROTOTYPE c."
   The prototype IS the centroid = magnitude-preserving superposition of exemplars;
     retrieval is by SIMILARITY (nearest codebook entry to the centroid).
   -> STRUCTURALLY requires SUPERPOSITION-inner (centroid; conv/xor binding DESTROYS the centroid)
      AND SIMILARITY-outer (nearest-to-centroid; unbinding is not similarity-retrieval).
   -> PREDICTS corr(bundle,c) uniquely closes; conv/xor-inner fail (no centroid);
      conv/xor-outer fail (no similarity readout).
   NOT target-fit: derived from prototype-retrieval semantics; a third party could state it
     WITHOUT knowing corr(bundle,c) is the answer.

Why C1 over C2/C3:
   C2 (magnitude-sensitive) fixes AXIS 1 only; needs pairing with C3 to fix AXIS 2.
   C3 (similarity-graded) fixes AXIS 2 only; needs pairing with C2 to fix AXIS 1.
   C1 fixes BOTH axes from a SINGLE independent task -> the clean principled gap.

Director endorses C1 as the canonical principled-gap target for any future USER-gated execution.
C2+C3 retained as axis-decomposed fallback if C1's prototype-theory semantics prove hard
to instantiate as a verifiable cell-gate.
```

## DECISION 185b -- GERRYMANDER-GUARD certification (provisional pre-sketch)

```
GUARD TEST (Skunkworks verbatim, endorsed):
   A criterion is PRINCIPLED (not gerrymander) iff it can be stated AND a third party could
   DERIVE it from the TASK DESCRIPTION ALONE, BLIND to the closer set -- without ever
   referencing "corr(bundle,c)" or "exclude xor/conv."

   TEST for Candidate 1: "prototype = centroid of exemplars; retrieve by similarity" is
   stateable from prototype theory with ZERO reference to the substrate's op inventory
   -> PASSES the guard.

   Uniqueness is then a PREDICTION to be tested by BLIND search at execution:
   - does corr(bundle,c) close?
   - do the other 7 fail?
   If blind search finds OTHER closers too -> criterion did NOT uniquely select ->
     HONEST NEGATIVE (still not a gerrymander, just not unique). Uniqueness must FALL OUT,
     not be imposed.

Director PROVISIONAL gerrymander-free certification ISSUED for the C1 design as
DESCRIBED. FINAL certification gated on Skunkworks's post-sketch review (Exp-Dev's
cell-gate sketch may surface implementation details that affect blindness).
```

## DECISION 185c -- 72nd audit-discipline instance type CANDIDATE

```
72nd audit-discipline instance type CANDIDATE:
   PRINCIPLED-GAP-DESIGNED-FROM-INDEPENDENT-AXES-NOT-EXCLUSION-LOGIC

   When designing a structural criterion to support a uniqueness claim, the principled
   approach is to identify INDEPENDENT structural axes (derivable from the op algebra
   blind to the closer set), find the candidate at their INTERSECTION, then identify
   an independent task whose semantics naturally REQUIRE that intersection.

   ANTI-PATTERN (gerrymander): list the closers; pick the one you want; reverse-engineer
   a criterion that excludes the others by naming the rejection. Uniqueness is IMPOSED.

   PRINCIPLED: identify orthogonal structural axes from op algebra; map each candidate
   onto the axes; the target falls at a unique intersection; find an independent task
   that maps onto that intersection. Uniqueness is PREDICTED + tested blind. If the
   prediction fails -> honest negative.

   Today's instance: Skunkworks TRACK B design identifies AXIS 1 (superposition vs binding
   inner) + AXIS 2 (similarity vs binding outer); corr(bundle,c) sits at their intersection;
   prototype/centroid-retrieval is an independent task that naturally requires both axes;
   uniqueness is a PREDICTION to be tested blind.

   Composes with prior instance types:
     7th rule (honest both directions)
     18th rule (refuses-what-cannot-prove)
     58th candidate (document-citation-motif-as-soft-gerrymander)
     70th candidate (qualified-finding-filed-without-overclaim-cross-session-consensus)
     71st candidate (degenerate-kappa-sample-honestly-disclosed-no-overread)
     72nd (THIS) -- principled-gap-designed-from-independent-axes-not-exclusion-logic

   Pattern is: substrate-product positioning maturity = ability to design uniqueness
   criteria from independent structural analysis + verify blindness pre-execution +
   refuse imposed-uniqueness. The path-to-honest-uniqueness is decompose-axes-find-
   intersection-find-independent-task-test-blind.
```

## DECISION 185d -- DIRECTIONS

```
Exp-Dev (TRACK B continuation): read-only SKETCH the C1 prototype-retrieval cell-gate:
   - Setup: exemplar pairs (a_1, a_2) drawn from a generative prototype c (codebook entry);
            substrate-internal generative model (e.g., c is a stored unitary; a_i = c + noise_i
            in the appropriate substrate-internal noise model per 11th rule).
   - Closure test: blind-search over the 38-op basis; closer = recovers c above per-op
                   chance baseline; exclude corr(bundle,c) from the seed (no leakage,
                   per ARM-3's existing protocol).
   - Prediction: corr(bundle,c) closes; the other 7 ARM-3-class closers fail (no centroid
                 OR no similarity readout).
   - Honest-negative path: if other closers also close on prototype-retrieval -> uniqueness
                           NOT earned; ARM-3 finding stays QUALIFIED + new test is honest
                           contribution to substrate-product positioning maturity.

   SKETCH ONLY -- no cell-build, no execution. Output: read-only spec of the cell-gate
   sufficient for Skunkworks final gerrymander-free certification + USER review.

Skunkworks: standing -- FINAL gerrymander-free certification on Exp-Dev's sketch
   (post-sketch, pre-USER-execution-decision); VET FORM-A backlog ratifies on TRACK A
   as they land (standard discipline).

Testbed: standing -- TRACK A ratify chain on FORM-A anchors when Exp-Dev hands off
   (no TRACK B atom mutation; design is concept-level).

Orchestrator: standing -- ready remote-desktop dispatch if/when USER gates execution
   per compute policy.

USER: TRACK B design GERRYMANDER-FREE provisional (pending final Exp-Dev sketch +
   Skunkworks post-sketch certification). Future execution remains your call per
   TRACK C / DECISION 184c. C1 PROTOTYPE/CENTROID-RETRIEVAL is the path to an EARNED
   ARM-3 uniqueness claim IF executed AND IF corr(bundle,c) uniquely closes prototype-
   retrieval blind. Otherwise: honest negative; finding stays QUALIFIED.
```

## Pipeline state at post-DECISION-185

```
Phase B BUILD: COMPLETE
Phase B tail:
   TRACK A: Awaiting Exp-Dev rank-order of 12+ FORM-A anchors by 4-point pre-pass
   TRACK B: Skunkworks design ENDORSED + gerrymander-free PROVISIONAL; Exp-Dev sketch
            DISPATCHED; FINAL certification gated on sketch; USER-gated execution
   TRACK C: HELD (Phase C TIER-3 + formal-oracle + Drill 5 + 218-signal cell-build
            all USER-architectural)

Sessions:
   Exp-Dev: TRACK A + TRACK B sketch (parallel work)
   Skunkworks: standing for FORM-A VETs + post-sketch FINAL certification
   Testbed: standing for FORM-A ratify chain
   Orchestrator: standing for remote-desktop dispatch
   Research (Director): 13th-rule active state-check armed; 14th-rule both tracks dispatched

USER 4 standing calls: unchanged (formal-oracle close + Drill 5 + Phase C TIER-3 +
   218-signal cell-build). C1 prototype-retrieval execution is a NEW USER-gateable
   decision per DECISION 184c TRACK C; non-blocking.
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal generative model for prototype + noise per 185d
- 18th rule: refuses imposed-uniqueness; uniqueness must be a tested prediction
- 19th rule: 72 instance types empirical (44 confirmed + 28 candidates today: 45-72)
- 22nd rule: Lakatos progressive (TRACK B C1 design generates a NEW falsifiable
            uniqueness prediction; honest-negative path preserved)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (no atom mutation
  in TRACK B design phase)
- Methodology stack FROZEN at 24

## Session tally

185 cumulative decisions. **215+ honest signals.** Substrate-product positioning at
post-DECISION-185: TRACK B principled-gap design ENDORSED + gerrymander-free PROVISIONAL;
72 audit-discipline instance types empirical (44 + 28 today).

---

**Skunkworks (Auditor):** DECISION 185 ENDORSES TRACK B design + provisional gerrymander-
free certification; standing for FINAL certification post-Exp-Dev sketch + FORM-A VETs.

**Exp-Dev (Prover):** TRACK B continuation -- read-only sketch the C1 prototype-retrieval
cell-gate per 185d spec; parallel with TRACK A FORM-A rank-order; no build, no execution.

**Testbed (Integrator):** TRACK A standing for FORM-A ratify chain; no TRACK B atom
mutation (design is concept-level).

**Orchestrator (Custodian):** standing for remote-desktop dispatch if USER gates TRACK B
execution per compute policy.

**USER:** TRACK B principled-gap design ENDORSED (gerrymander-free provisional).
CANDIDATE 1 prototype/centroid-retrieval is the principled path to an EARNED ARM-3
uniqueness claim -- if/when YOU gate execution. Two independent axes (superposition vs
binding inner; similarity vs binding outer) put corr(bundle,c) at a unique intersection.
Uniqueness will be a TESTED prediction (blind search), not an assumption. 72 audit-
discipline candidates documents the principled-gap-design pattern. Standing on 4
architectural calls + (new) TRACK B execution timing.

Tag: DECISION_185_TRACK_B_design_ENDORSED_two_axis_structural_distinguisher_superposition_inner_similarity_outer_corr_bundle_unique_intersection_CANDIDATE_1_prototype_centroid_retrieval_strongest_independent_task_semantics_gerrymander_guard_passes_72nd_audit_discipline_candidate_principled_gap_from_independent_axes_not_exclusion_logic -- Research (Director)
