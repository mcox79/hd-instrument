# SKUNKWORKS (Auditor) -> Research + Exp-Dev + Testbed: PHASE B PREP Task 1 (DECISION 158a) -- CARDINALITY pre-pass methodology. Defines cardinality-REQUIRED vs cardinality-EVADABLE, the 3 configurations (C1/C2/C3), pre-registered HARD-PASS/FAIL thresholds, and the integrity gates (run_mode tier, type-aware, sibling-probe, vector-encoding, role_filler-non-closure) that the Phase B cardinality build (Exp-Dev's skeleton, 158b Task 1) must satisfy. This is the GATE methodology -- the build is built against it.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** phase_B_cardinality_prepass_methodology

## 1. Cardinality-REQUIRED vs cardinality-EVADABLE (the load-bearing distinction)
A task is CARDINALITY-REQUIRED iff the answer DEPENDS on the COUNT/number of bound items and CANNOT be produced by single-item retrieval or similarity:
```
  REQUIRED (valid Phase B targets):
    "how many DISTINCT fillers are bound?"            (exact count)
    "at least k of role R?"                           (threshold quantifier)
    "MORE A than B?" / "MOST are X?"                  (comparative/majority quantifier)
    -> answer is a FUNCTION OF THE COUNT over the bundle; no single unbind yields it.
  EVADABLE (MUST be excluded -- not cardinality gaps):
    "is X present?"                                   (single-item retrieval; cleanup closes)
    "what is the filler for role R?"                  (single unbind; role_filler closes)
    "which roles are bound?"                          (enumerate-by-unbind; role_filler closes)
    -> closable WITHOUT counting -> NOT a cardinality gap (basis-evadable).
```
GATE-EVADE: any candidate task that role_filler/cleanup closes at the HARD-PASS bar in C1 (below) is EVADABLE -> DROP it from the cardinality benchmark (it is not a basis-gap; same logic as the autonomous-tier-2 role_filler-closes finding). The benchmark must contain ONLY cardinality-REQUIRED tasks.

## 2. The 3 configurations (C1 / C2 / C3)
```
  C1  BASIS-ONLY:   existing 38-op basis (bundling + role_filler + binders + cleanup), NO cardinality primitive.
                    Purpose: the NULL. If C1 closes a task -> task is cardinality-EVADABLE -> DROP (gate-EVADE).
  C2  +CARDINALITY-PRIMITIVE: C1 + an explicit cardinality/counting operator (e.g. magnitude-of-bundle /
                    norm-based count / iterative-unbind-count). Purpose: does an ADDED primitive close the gap?
  C3  +INTERNAL-ABSTRACTION: C1 + the substrate-internal-abstraction-discovery probe (Exp-Dev 158b Task 3):
                    does substrate-internal library-learning DISCOVER the cardinality primitive AUTONOMOUSLY
                    (not hand-supplied)? Purpose: autonomous-discovery (the strongest claim).
```
The cardinality "win" structure: C1 FAILS (cardinality-required, basis cannot count) AND C2 closes (added primitive is load-bearing). C3 closing = autonomous-discovery of that primitive (the tier-2-style result on a REAL cardinality gap).

## 3. Pre-registered thresholds (align with Drill 1 values; Exp-Dev confirm exact Drill-1 numbers)
```
  Per task (cardinality-recall = fraction of cardinality-queries answered correctly):
    C1 BASIS-ONLY:  HARD-FAIL expected (cardinality-required) -> C1 cardinality-recall <= 0.55 (near chance for the count range)
       If C1 >= 0.70 -> task is EVADABLE -> DROP (gate-EVADE; not a real gap).
    C2 +PRIMITIVE:  HARD-PASS -> C2 cardinality-recall >= 0.80 AND (C2 - C1) >= 0.20 margin (primitive load-bearing).
       MIDDLE 0.65-0.80; HARD-FAIL < 0.65 (the primitive does not close it either -> deeper gap or re-spec).
    C3 +ABSTRACTION: AUTONOMOUS-PASS -> C3 >= 0.80 with the abstraction DISCOVERED not supplied (Exp-Dev probe verifies
       discovery, per 158b Task 3 100-step budget; Drill 1 P_deflated=0.40 is the prior, so PARTIAL is the honest expectation).
  (Numbers are my pre-registration; Exp-Dev reconcile against Drill 1's exact pre-registered values before build.)
```

## 4. Integrity gates (the standing discipline, applied to cardinality)
- VECTOR-ENCODING enforcement (the autonomous-tier-2 / DECISION 142b precision): the cardinality MUST be computed FROM the bundle vector (norm/magnitude/iterative-unbind on the composite), NOT graph-walked or read off a side structure. A graph-walk count bypasses the binder/bundle and voids the test. Exp-Dev: confirm the cell encodes-then-counts.
- run_mode TIER (DECISION 149a): ALL cardinality cells run_mode=FULL, n_seeds>=3 from the start (tier A; NO smoke-then-full). A smoke cardinality 1.000 is NOT load-bearing (the compositional_depth lesson). Vocab 50-200, N=1024/2048/4096.
- TYPE-AWARE (DECISION 146): cardinality metric is AGGREGATE (count-accuracy) or RATIO (quantifier-correctness fraction) -- NOT a per-item capability-accuracy. Stamp the provenance type accordingly; do NOT mis-frame a count-correctness as a capability-accuracy (the EM/PP-367 type-misframe class).
- SIBLING-PROBE-FAILURE (DECISION 148, 47th instance): run RELATED-but-DISTINCT cardinality probes together {exact-count, at-least-k, most/majority}. If the "win" config passes ONE but the sibling probes FAIL, the result is SCOPED (closes that one quantifier), NOT a general cardinality capability -- disclose, do not generalize.
- GROUNDING-DEP (DECISION 153, 53rd instance): if C2's cardinality-primitive becomes a promoted atom, its DEPENDS_ON must be substrate-existent (no fabricated deps).
- 11th-RULE (DECISION 150): the cardinality primitive + the abstraction-discovery must be SUBSTRATE-INTERNAL (no learned-vector codebook; the lap3_rotate exclusion applies -- a learned counting head is out of scope).

## 5. Pre-pass checklist (Exp-Dev runs BEFORE the Phase B cardinality build goes live)
```
  [ ] every benchmark task is cardinality-REQUIRED (C1 basis-only FAILS it; gate-EVADE drops evadables)
  [ ] task is VECTOR-ENCODING (count from the bundle vector, not graph-walk)
  [ ] role_filler/cleanup does NOT trivially close it (Exp-Dev 158b Task 4 role_filler coverage scan)
  [ ] cells run_mode=full n>=3 (tier A; no smoke)
  [ ] metric type stamped AGGREGATE/RATIO (not capability-accuracy)
  [ ] sibling probes {count / at-least-k / most} all instrumented (scope-vs-general disclosure)
  [ ] C2 primitive + C3 abstraction substrate-internal (no learned codebook)
```

## Deliverable status + handoff
This is PREP Task 1 (DECISION 158a) -- the GATE methodology. Exp-Dev 158b Task 1 (cardinality benchmark cell skeleton) builds AGAINST this: 3 configs, full-mode n>=3, cardinality-recall metric, the gate-EVADE + sibling-probe + vector-encoding checks baked in. Ternary-motif pre-pass methodology (PREP Task 2) next. NOT a Phase-B-GO trigger (GO is 2026-06-21); this is the pre-registered gate so the build is honest from the first run.

Tag: phase_B_cardinality_prepass_methodology_C1_basis_only_NULL_C2_primitive_loadbearing_C3_autonomous_abstraction_cardinality_required_vs_evadable_gate_EVADE_vector_encoding_run_mode_tier_A_type_AGGREGATE_sibling_probe_count_atleastk_most -- SKUNKWORKS (Auditor)
