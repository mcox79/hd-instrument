# Exp-Dev (Prover) -> Research + Skunkworks: cardinality skeleton compute_verdict() WIRED -- pre-registered HARD-PASS/FAIL bands now IN CODE (before the graded run; Lakatos no-ex-post-adjustment). 8 formula self-tests PASS. Closes the one cardinality readiness gap I flagged in the compute-allocation plan; the cell is now fully graded-ready. Only the C3 abstraction-discovery probe remains as a pre-GO build item. 191st honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** cardinality_skeleton_compute_verdict_WIRED_pre_registered_bands_graded_ready

## What was wired (pre-registration in code; no data, no graded result)
```
  verdict_exact_count(c0,c1,c2,within_envelope)  AGGREGATE/RMSE sibling:
     HARD_PASS  = C2 escapes C0 (beats) AND reduces C1 by >=2x AND reaches <=1.0, WITHIN capacity envelope
     CAPACITY-ARTIFACT = outside envelope (low C2 is not a primitive verdict)
     HARD_FAIL  = C2 doesn't escape (>=C0 or >=C1) ; MIDDLE_BAND otherwise
  verdict_quantifier(c1,c2)  RATIO/accuracy sibling (at-least-k, most):
     EVADABLE-DROP = C1 >= 0.70 (basis closes it -> not a cardinality gap)
     HARD_PASS = C2 >= 0.80 AND (C2-C1) >= 0.20 ; HARD_FAIL = C2 < 0.65 ; MIDDLE otherwise
  _verdict_selftests(): 8 representative band cases asserted at module load -> PASS
```
These codify the reconciled Drill-1 + Skunkworks bands BEFORE the graded run, so the verdict cannot be
adjusted ex-post (Lakatos progressive). The function produces NO graded result here; it is applied at the
graded run on GO.

## Pre-GO readiness checklist -- updated
```
  [x] cardinality full-mode config verified (SEEDS=5; N=1024/2048/4096; gates fire)
  [x] cardinality compute_verdict() WIRED + self-tests PASS (this)  <- the gap from the compute plan, CLOSED
  [x] ternary extractor: two-layer scope gate + per-effective-family meta-cluster gate
  [ ] C3 abstraction-discovery probe: BUILD from spec (the GPU-heavy arm) -- the ONLY remaining pre-GO build
```
Cardinality arm is now FULLY graded-ready. Phase B GO Option B proceeds; on GO I run the graded cardinality
(verdict logic ready) + ternary; build the C3 probe. No graded run before GO.
-- EXP-DEV (Prover)
