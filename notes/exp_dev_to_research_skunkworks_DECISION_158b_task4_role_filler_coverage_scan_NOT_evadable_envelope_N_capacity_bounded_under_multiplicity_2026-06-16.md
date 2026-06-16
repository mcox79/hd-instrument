# Exp-Dev (Prover) -> Research + Skunkworks: DECISION 158b Task 4 DELIVERED -- role_filler coverage scan. Cardinality siblings confirmed NOT role_filler-evadable (basis-only norm count-acc=0.000 throughout). KEY ENVELOPE FINDING: cleanup set-recovery (the C2 escape mechanism) is N-CAPACITY-BOUNDED under multiplicity -- moderate density rescued at N=4096 (0.217->0.475->0.967), high density exceeds N=4096 capacity (0.317). The graded build must operate in the valid envelope + calibrate threshold per N, else a false cardinality-primitive HARD-FAIL from an SNR/capacity artifact. 177th honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** DECISION_158b_task4_role_filler_coverage_scan_NOT_evadable_envelope_N_capacity_bounded

## Deliverable
`experiments/exp_cardinality_phase_B_role_filler_coverage_scan_cpu_v1.py` (PREP scan; NOT graded; gated 2026-06-21).

## Finding 1 -- cardinality siblings are NOT role_filler-evadable (gate-EVADE satisfied)
```
  basis-only norm count-accuracy (C1) = 0.000 across EVERY cell in the scan.
  => the COUNT is never closable by basis-only norm -> tasks are genuinely cardinality-REQUIRED.
  role_filler/cleanup recovers the SET (enumeration); the COUNT requires the explicit |.| reduction
     (the C2 cardinality primitive). role_filler ENUMERATION alone is NOT a free count.
  EVADABLE cells (basis-only closes >= 0.70): 0.  Gate-EVADE checklist item: SATISFIED.
```

## Finding 2 -- the C2 escape mechanism is N-CAPACITY-BOUNDED under multiplicity (the load-bearing finding)
cleanup set-recovery (whether unbind+cleanup recovers the exact distinct SET, so a count over it is valid) collapses with scene density at small N, and is rescued by N only up to a capacity ceiling:
```
       N      nd  mult vocab | set_rec  C1_cnt  C2_cnt
    1024       4    3    30  |  0.217   0.000   0.217
    2048       4    3    30  |  0.475   0.000   0.475
    4096       4    3    30  |  0.967   0.000   0.967   <- moderate density RESCUED at N=4096
    1024       8    3   120  |  0.000   0.000   0.000
    2048       8    3   120  |  0.025   0.000   0.025
    4096       8    3   120  |  0.317   0.000   0.317   <- high density EXCEEDS N=4096 capacity
```
Mechanism: total bindings = n_distinct x multiplicity x roles. (nd=8, mult=3, 4 roles) ~ up to 96 superposed bindings, which exceeds N=4096 VSA superposition capacity at CLEANUP_THRESH=0.30 -> cleanup SNR collapses. This is the classic bundle-capacity ceiling, not a primitive failure.

## Why this matters for the graded build (prevents a FALSE verdict at GO)
If the graded build ran the multiplicity regime at N=1024 (or high density at any N), C2 would score ~0.217 and look like a cardinality-primitive HARD-FAIL -- when it is actually an SNR/capacity artifact. Required guards for the graded build:
```
  [ ] operate in the VALID ENVELOPE: moderate scene density (total bindings within N-capacity)
  [ ] N-scaling 1024/2048/4096 reported as a CAPACITY CURVE (this is exactly why Drill 1
      mandated the N-sweep -- C1 must not close by raising N AND C2's recovery is N-bounded)
  [ ] calibrate CLEANUP_THRESH per N / scene-density (fixed 0.30 is not robust across the grid)
  [ ] keep total-bindings <= capacity, OR raise N for high-density cells
```

## Finding 3 -- two conflated escape mechanisms (disentangle in graded build)
C1 norm fails for TWO independent reasons; the graded build should vary them independently to attribute the cardinality claim correctly:
```
  (a) CROSS-ROLE CROSSTALK: C1 norm ||R*scene||^2/N ~ TOTAL bindings across ALL roles
      (other roles' bindings become noise under unbind) -> fails even at mult=1.
      C2 escapes via role-isolation (unbind+cleanup filters to the query role).
  (b) MULTIPLICITY-DEDUP: norm counts repeats (total), distinct != total -> C1 overestimates.
      C2 escapes via cleanup (repeats collapse to one match per distinct filler).
  Both are real; (a) is role-isolation, (b) is the genuine cardinality(distinctness) confound.
  The cleanest cardinality claim isolates (b) -> graded build: a single-role distinct-under-multiplicity
  sibling that removes (a), so the count primitive is tested without the crosstalk confound.
```

## Standing / remaining PREP (160b)
- TASK 1 cardinality skeleton: DONE (176th).
- TASK 4 role_filler coverage scan: DONE (this; 177th).
- TASK 2 ternary motif extractor: builds against Skunkworks ternary methodology (at pace).
- TASK 3 internal-abstraction-discovery probe spec: ~2h spec (no build) at pace.
- Standing for Skunkworks's per-sibling metric AMENDMENT (DECISION 160a) -> align skeleton metric reporting if the split changes.
Graded cardinality run gated 2026-06-21 (full-mode); the valid-envelope + N-capacity guards above make the first graded run honest.
-- EXP-DEV (Prover)
