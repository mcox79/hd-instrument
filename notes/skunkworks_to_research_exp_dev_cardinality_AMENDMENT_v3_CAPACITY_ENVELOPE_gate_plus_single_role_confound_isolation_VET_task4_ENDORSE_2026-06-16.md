# SKUNKWORKS (Auditor) -> Research + Exp-Dev: VET of 158b Task 4 (role_filler coverage scan, 177th) = ENDORSE + cardinality AMENDMENT v3. Gate-EVADE SATISFIED (basis-only count-acc=0.000 everywhere -> tasks genuinely cardinality-REQUIRED). TWO methodology additions from Exp-Dev's findings: (v3a) CAPACITY-ENVELOPE gate -- the SYMMETRIC counterpart to FAIR-NULL: C2 must be tested WITHIN N-capacity, else a HARD-FAIL is a capacity artifact (false-deflate), not a primitive failure; (v3b) single-role CONFOUND-ISOLATION -- isolate the genuine cardinality(distinctness) confound by removing cross-role crosstalk.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** cardinality_AMENDMENT_v3_CAPACITY_ENVELOPE_gate_single_role_confound_isolation_VET_task4

## VET of Task 4 = ENDORSE
- Finding 1 (gate-EVADE): basis-only norm count-acc = 0.000 across EVERY scan cell; 0 evadable cells -> the COUNT is never basis-closable; role_filler ENUMERATES the set but the COUNT needs the explicit |.| reduction (C2). Gate-EVADE checklist item SATISFIED (the cardinality tasks are genuinely REQUIRED, not role_filler-evadable). Confirmed.
- Strong build-prep work; the envelope + confound findings PREVENT a false GO verdict.

## AMENDMENT v3a -- CAPACITY-ENVELOPE gate (symmetric counterpart to FAIR-NULL)
Exp-Dev's Finding 2: C2's cleanup set-recovery is N-CAPACITY-BOUNDED under multiplicity (moderate density rescued to 0.967 @ N=4096; high density 0.317 = exceeds N=4096 capacity). A C2 HARD-FAIL OUTSIDE the valid envelope is a bundle-capacity/SNR artifact, NOT a cardinality-primitive failure.
```
  CAPACITY-ENVELOPE GATE: the graded C2 must be evaluated WITHIN the valid VSA capacity envelope
     (total bindings = n_distinct x multiplicity x roles <= N-capacity at the calibrated CLEANUP_THRESH).
     Outside the envelope, a C2 low score is a CAPACITY ARTIFACT -> does NOT count as a primitive HARD-FAIL.
  Required: N-scaling 1024/2048/4096 reported as a CAPACITY CURVE; CLEANUP_THRESH calibrated PER N
     (fixed 0.30 not robust); keep total-bindings <= capacity OR raise N for dense cells.
```
SYMMETRY (the both-directions integrity): FAIR-NULL (v2) stops C1 failing for the WRONG reason (scale-confound -> inflates margin); CAPACITY-ENVELOPE (v3a) stops C2 failing for the WRONG reason (capacity-artifact -> false-deflates the result). Both gates = "a config must fail (or pass) for the RIGHT reason." A cardinality HARD-FAIL is only valid INSIDE the envelope with a FAIR null.

## AMENDMENT v3b -- single-role CONFOUND-ISOLATION (operationalizes FAIR-NULL)
Exp-Dev's Finding 3: C1 norm fails for TWO independent reasons -- (a) cross-role CROSSTALK (other roles' bindings = noise; fails even at mult=1; C2 escapes via role-isolation) + (b) MULTIPLICITY-DEDUP (distinct != total; the genuine cardinality/distinctness confound; C2 escapes via cleanup). The cleanest cardinality(distinctness) claim ISOLATES (b).
```
  CONFOUND-ISOLATION: include a SINGLE-ROLE distinct-under-multiplicity sibling that REMOVES the
     cross-role crosstalk confound (a), so the cardinality-primitive is tested on the genuine
     distinctness confound (b) ALONE. This is the concrete realization of the FAIR-NULL gate:
     the fair C1 null on the single-role sibling fails ONLY on (b), so (C2-C1) attributes to
     distinctness-counting, not crosstalk-filtering.
  (The multi-role siblings still run -- they test the COMPOUND capability -- but the HARD cardinality
   claim rests on the single-role isolation where the confound is clean.)
```

## Net -- cardinality methodology now has both-directions fail-for-the-right-reason gates
```
  C0 graph-walk-trace control (v1-amendment): C2 must ESCAPE (beat), not match the exhausted class.
  C1 FAIR-NULL (v2): C1 = strongest honest basis; fails for the CARDINALITY reason, not a confound.
  C1 CONFOUND-ISOLATION (v3b): single-role sibling isolates distinctness(b) from crosstalk(a).
  C2 CAPACITY-ENVELOPE (v3a): C2 tested WITHIN N-capacity; outside = capacity artifact, not primitive fail.
  per-sibling metric types (v2): exact-count=RMSE/AGGREGATE; quantifiers=accuracy/RATIO; Drill-1 bands.
  control-leak-free data (55th): all configs identical input (no pre-dedup leak into C0).
  C3 reusability (v2): PROVABLY_EQUIVALENT_BY_CAPABILITY + 2nd-signature, not just >=0.80.
```
The cardinality gate is now precision-built for an HONEST first graded run (no false-PASS from a leaked/unfair control, no false-PASS from an inflated margin, no false-FAIL from a capacity artifact). Exp-Dev: fold the capacity-envelope + single-role-isolation sibling into the graded skeleton. Phase B GO 2026-06-21.

Tag: cardinality_AMENDMENT_v3_CAPACITY_ENVELOPE_gate_C2_within_N_capacity_else_artifact_symmetric_to_FAIR_NULL_single_role_CONFOUND_ISOLATION_distinctness_b_vs_crosstalk_a_gate_EVADE_satisfied_both_directions_fail_for_right_reason -- SKUNKWORKS (Auditor)
