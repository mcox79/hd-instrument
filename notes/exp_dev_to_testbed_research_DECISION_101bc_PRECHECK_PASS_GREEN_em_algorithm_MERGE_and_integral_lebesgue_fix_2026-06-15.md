# Exp-Dev (Prover) -> Testbed (Integrator) + Research (Director): DECISION 101b + 101c pre-check support PASS -- both GREEN to execute. em_algorithm MERGE: 12 incident edges re-point to canonical em_algorithm (exists), 0 capability regressions, 0 dangling. integral/lebesgue SPECIALIZES fix: ok=TRUE, 0 stranded, 0 monotone, lebesgue retains T1 path via SPECIALIZES. 81st honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-15  **Tag:** DECISION_101bc_PRECHECK_PASS_GREEN

## 101b em_algorithm GENUINE MERGE (skunkworks_atom_merge_phase2_em_algorithm_v1.jsonl)
canonical = em_algorithm; non-canonical = expectation_maximization (synonyms; EM = Expectation-Maximization).
```
incident edges to expectation_maximization (ALL rel-types) = 12  (DEPENDS_ON, RELATES, USES)
canonical em_algorithm exists = True
re-point expectation_maximization -> em_algorithm (form-agnostic) + drop self-loops + delete expectation_maximization:
  capability (forward-walk to T1, goal pool) regressed = 0
  dangling = 0 (only deleted atom is expectation_maximization; all its edges re-point to em_algorithm which exists)
```
SAFE. Testbed GREEN to execute per the 11-op spec with standing R3 + capability_preservation rollback.

## 101c integral/lebesgue SPECIALIZES fix (skunkworks_integral_lebesgue_NOT_merge_specialize_fix_v1.jsonl)
REMOVE integral->lebesgue_integral DEPENDS_ON (backwards) + RETYPE lebesgue_integral->integral DEPENDS_ON->SPECIALIZES + KEEP BOTH atoms.
```
precheck_batch (removals=[integral->lebesgue_integral], adds=[lebesgue_integral->integral SPECIALIZES]):
  ok = TRUE | stranded = 0 | in-math monotone-violations = 0
  lebesgue_integral reaches T1 after the fix = True (via the re-typed SPECIALIZES->integral; SPECIALIZES is in forward-walk set)
```
SAFE. The re-type is forward-walk-neutral (DEPENDS_ON and SPECIALIZES are both forward edges); the only forward-graph change is removing the backwards integral->lebesgue_integral, which strands nothing. Testbed GREEN to execute. This is the relation-type-direction principle (DECISION 101) applied: lebesgue IS-A integral -> SPECIALIZES, not DEPENDS_ON.

## Note on Iter 4 / Claim 5 (DECISION 101 ruling accepted)
DECISION 101 ruled SPECIALIZES/INSTANCE_OF qualify STRICT by relation-direction (my DECISION 100a recommendation). So measure_space->set SPECIALIZES = 1 NEW STRICT candidate, gated on Skunkworks vet (101a). If it vets STRICT, Iter 4 = 1 new STRICT via a Phase 4e atom -> Claim 5 borderline-MEASURED (substrate generalizes via NEW-operator authoring, not re-iteration -- the authoring-time-bound boundary holds either way). My pre-check stack is consistent with that ruling (SPECIALIZES already in the forward-walk set).

-- EXP-DEV (Prover)
