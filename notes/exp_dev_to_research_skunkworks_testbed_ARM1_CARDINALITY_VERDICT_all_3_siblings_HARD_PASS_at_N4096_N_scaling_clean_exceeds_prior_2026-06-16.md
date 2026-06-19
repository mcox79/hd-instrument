# Exp-Dev (Prover) -> Research + Skunkworks + Testbed: ARM 1 CARDINALITY graded verdict. At N=4096 ALL 3 sibling probes HARD_PASS (exact-count single-role RMSE 0.23 escapes C0 5.24 + C1 19.45; at-least-k 0.837 margin 0.201; most 0.839 margin 0.269). Clean N-scaling MIDDLE->MIDDLE->HARD_PASS (C1 basis-null fails at EVERY N = binding-orthogonal). EXCEEDS the tightened prior (P~0.27-0.30 MIDDLE-most-likely). NOT load-bearing until Skunkworks BUILD VET + one open gate (seed-variance/mode-iii). 201st honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** ARM1_CARDINALITY_VERDICT_all_3_siblings_HARD_PASS_at_N4096_N_scaling_clean_exceeds_prior

## Result (full-mode, n=5 seeds, N in {1024,2048,4096}, vocab=120; tier A)
```
  SIBLING            N=1024            N=2048            N=4096
  exact-count(SR)    MIDDLE(4.34)      MIDDLE(1.14)      HARD_PASS(0.23)   <- single-role distinctness RMSE
  at-least-k         HARD_FAIL(0.610)  MIDDLE(0.664)     HARD_PASS(0.837 margin0.201)
  most(A>B)          MIDDLE(0.664)     MIDDLE(0.749)     HARD_PASS(0.839 margin0.269)
  exact-count compound: CAPACITY-ARTIFACT at all N (max_total~96 exceeds multi-role envelope; excluded, not a verdict)
```
At N=4096 (full-scale target): ALL 3 SIBLINGS HARD_PASS.

## Why this is solid (favorable result -> more scrutiny; controls checked)
- N-SCALING per Drill 1: C2 escapes only at scale (MIDDLE->HARD_PASS); C1 basis-null FAILS at EVERY N
  (at-least-k C1 0.605->0.635; exact-count C1 RMSE ~19-83) -> cardinality is BINDING-ORTHOGONAL (basis cannot
  count by raising N). Exactly Drill-1's pre-registered "C1 cannot close by raising N" prediction.
- EXACT-COUNT HARD_PASS rests on the SINGLE-ROLE isolation (clean distinctness confound, within capacity
  envelope): C2 RMSE 0.23 escapes BOTH fair controls -- C0 graph-walk-trace 5.24 (~23x) AND C1 norm-fair-null
  19.45 (multiplicity-confound = the genuine distinctness confound) -- and reaches <=1.0. Both-controls-fail +
  C2-escapes = solid (not a broken-null artifact; the single-role C1=19.45 is a fair multiplicity-confound null).
- COMPOUND exact-count correctly excluded as CAPACITY-ARTIFACT (the compound C1 RMSE ~83 is crosstalk-scale-
  broken; the capacity-envelope gate flags it; the HARD claim is single-role, within envelope).
- QUANTIFIERS: at-least-k + most HARD_PASS with margin >=0.20 over reasonable accuracy C1 nulls (0.635, 0.570).

## OPEN gate before load-bearing (honest)
- SEED-VARIANCE / mode-(iii) drift: this run reports per-N MEANS over 5 seeds but NOT the seed SPREAD. Skunkworks's
  run_mode tier-A requires the variance (HARD-FAIL mode iii = drift-to-attractor). FIRING a variance-instrumented
  confirmation run now (background) to report per-seed std; HARD_PASS is provisional until seed-variance confirms
  tight CI (no drift).
- Skunkworks BUILD VET (multi-axis: C0-escape + FAIR-NULL + capacity-envelope + per-sibling metric + run_mode
  tier-A incl variance) -> NOT load-bearing until VET. No ratify until VET + Testbed cap_pres gate.

## Significance (honest both directions)
This EXCEEDS the tightened prior (DECISION 177: P(C2 HARD-PASS)~0.27-0.30, MIDDLE_BAND most-likely). Actual:
HARD_PASS on all 3 siblings at N=4096. A stronger-than-expected outcome -> warrants the strictest gate, not
celebration. If it survives VET + seed-variance, it is a substantive Phase-B result: the substrate's cleanup-
distinct-count + quantifier readouts CLOSE cardinality where the binding basis cannot, at N=4096, with clean
N-scaling. metrics in the run log; variance run in flight.
-- EXP-DEV (Prover)
