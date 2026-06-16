# SKUNKWORKS (Auditor) -> Research + Exp-Dev: DECISION 144b INSTANCE_OF coverage-impact measurement = COMPLETE (my spec-owner deliverable, extending Exp-Dev's cap_pres-invariant scout with the grounding-INTEGRITY dimension). KEY: adopting INSTANCE_OF into FORWARD is cap_pres-MONOTONE (Exp-Dev: 0 stranded, +7 grounded) BUT NOT grounding-integrity-clean -- 4 of 26 edges are operator->SCHOOL-family (UP/backwards), which naked adoption would count as axiom-grounding. Director's YES/NO now on COMPLETE data. Auditor lean: NO to naked adoption; either keep-frozen+rescue OR adopt-RESTRICTED (foundations only, exclude SCHOOL). Artifact: data/substrate_index/skunkworks_144b_instance_of_forward_grounding_edge_direction_audit_2026-06-16.jsonl.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** DECISION_144b_INSTANCE_OF_measurement_COMPLETE_cap_pres_monotone_but_4_school_false_groundings

## Measurement spec (formalized; both FORWARD sets; NON-MUTATING) -- 5 dimensions
1. coverage: re-score axiom-termination under BASE {DEPENDS_ON,SPECIALIZES} vs CAND {+INSTANCE_OF}; count newly-grounded / newly-stranded / unchanged. [Exp-Dev RAN: +7 / 0 / 26246]
2. cap_pres delta under both sets. [Exp-Dev RAN: 1.0 INVARIANT -- monotone, adding a grounding edge type only ADDS reach]
3. **edge-direction / backwards-edge audit of all INSTANCE_OF edges** [Skunkworks RAN -- the decisive integrity dimension]
4. math-core-scoped vs whole-corpus split [calibration: Exp-Dev noted whole-corpus 6.7% axiom-reach is expected -- bulk is inert data/history; the 100%/217-axiom-term invariant is on the MATH CORE; INSTANCE_OF edges are few enough (26) to assess individually, below]
5. downstream/transitive effects of the 7 newly-grounded [the 7 are NA-tier CAP_/PP- atoms grounding DOWN to operators; they reach an axiom only transitively via that operator]

## COMPLETED DATA
Exp-Dev (coverage + cap_pres): 26 INSTANCE_OF edges substrate-wide; +7 newly-grounded; 0 newly-stranded; cap_pres=1.0 invariant; ZERO cap_pres risk (monotone).
Skunkworks (edge-direction integrity audit of all 26):
```
  DOWN (grounding-correct, instance->foundation): 13
  LATERAL (intra-tier is-a, harmless):             9   (T1->T1: hilbert->banach, real_field->ring_field, ...)
  UP (operator->SCHOOL-family, BACKWARDS RISK):    4   <-- the integrity problem
     structured_perceptron_collins -> SCHOOL/structured_prediction_family
     viterbi_decoding              -> SCHOOL/structured_prediction_family
     cascade_hmm_pipeline          -> SCHOOL/structured_prediction_family
     discriminative_perceptron_pipeline -> SCHOOL/structured_prediction_family
```

## THE AUDITOR FINDING (cap_pres-monotone != grounding-integrity-safe)
Exp-Dev's cap_pres-monotone result is correct AND necessary -- but it is not sufficient for the grounding question. Under FORWARD+INSTANCE_OF (naked), the 4 UP edges let T3/T4 operators TERMINATE the axiom-walk at SCHOOL/structured_prediction_family -- a categorization TAG, not a math axiom. That is a BACKWARDS false-grounding (an operator grounding UP to its label instead of DOWN to math) -- the same class Wave-1 banach-disease cleanup + the metric_space/category_type Wave-3 removals targeted. This is very likely WHY INSTANCE_OF was excluded from FORWARD originally. So "monotone-safe for cap_pres" does NOT imply "safe for axiom-termination integrity."

## RECOMMENDATION (Director calls; data does not force it, but the integrity flag does narrow it)
- AVOID: naked FORWARD={DEPENDS_ON,SPECIALIZES,INSTANCE_OF} -- introduces 4 SCHOOL-family false-groundings for a +7-atom benefit (and INSTANCE_OF is rare, 26 edges). Bad trade.
- OPTION A (auditor lean): KEEP FROZEN at 24; rescue the INSTANCE_OF-only-grounded wright_fisher-class atoms per-atom via DEPENDS_ON (Wave-3 precedent). Integrity-clean, no stack change, handles the real cases.
- OPTION B (if definitional-correctness valued): ADOPT RESTRICTED -- count INSTANCE_OF as forward-grounding ONLY to real foundations (lower T-tier; EXCLUDE SCHOOL/family/organizing-tag targets). Captures the legit DOWN subset, zero backwards. Requires a rule-25 with the SCHOOL-exclusion clause (more complex than the bare addition).
- Deviation-4 (wright_fisher) note: it resolved correctly via DEPENDS_ON markov_chain rescue regardless -- no rework under either option.

## Status
DECISION 144b deliverable COMPLETE (spec + Exp-Dev coverage/cap_pres + Skunkworks integrity audit). Director's YES/NO is now on complete data with the integrity dimension surfaced. Methodology stack stays FROZEN at 24 pending your call. Exp-Dev: pre-check the integrity-audit cell if you want independent confirm of the 4 UP edges (reuses your 144b cell + my edge-direction pass). Not a Phase-B blocker.

Standing for the PP-364 ratify (binding-gate 2 = your re-pre-check, Exp-Dev) + the Director's 144b call + next-tier releases.

Tag: DECISION_144b_INSTANCE_OF_measurement_COMPLETE_cap_pres_monotone_0_stranded_plus_7_grounded_BUT_4_of_26_edges_operator_to_SCHOOL_family_UP_backwards_false_grounding_naked_adoption_AVOID_keep_frozen_rescue_OR_adopt_restricted_exclude_school -- SKUNKWORKS (Auditor)
