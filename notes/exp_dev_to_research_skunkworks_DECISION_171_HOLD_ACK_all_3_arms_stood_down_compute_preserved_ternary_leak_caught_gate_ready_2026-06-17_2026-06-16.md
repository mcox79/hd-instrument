# Exp-Dev (Prover) -> Research + Skunkworks: DECISION 171 HOLD ACK -- all 3 BUILD arms stood down; in-flight cardinality graded run KILLED (compute preserved); walked-back partial artifacts removed; gate-ready for 2026-06-17 morning Option B. NET POSITIVE from the brief Option-C window: caught + fixed a target-in-key LEAK in the ternary graded cell (verify-before-asserting; would have given a false HARD_FAIL) BEFORE GO. 192nd honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** DECISION_171_HOLD_ACK_all_3_arms_stood_down_compute_preserved_ternary_leak_caught

## HOLD executed (DECISION 171b)
```
  ARM 1 cardinality: in-flight full-mode graded run (background b56ijrsbc, ~5 min in) KILLED via TaskStop -> compute preserved
  ARM 2 ternary motif: stood down (not run for a verdict)
  ARM 3 C3 abstraction-discovery: not started (was the to-build arm)
  Walked-back partial artifacts REMOVED: data/phase_B_cardinality_graded_run_2026-06-16.log + ternary verdict json
     (must not persist as "results" -- they were partial/leaked, USER walked back the rushed GO)
```

## Gate-ready state (all WIRED; re-fire 2026-06-17 morning)
```
  CARDINALITY skeleton: FULLY graded-ready -- full-mode config (SEEDS=5, N=1024/2048/4096) + C0/C1/C2 readouts
     + single-role isolation + regime-calibrated capacity-envelope + compute_verdict() pre-registered bands
     + 8 verdict self-tests PASS. (The in-flight run confirmed it FIRES cleanly before kill.)
  TERNARY extractor: math-scoped MOTIF-B=20 + two-layer scope gate + per-effective-family + meta-cluster non-DFT gate.
  TERNARY graded-completion cell: leak-FIXED + compile-OK (see below); graded run deferred to GO.
  C3 probe: to BUILD at GO from spec (the GPU-heavy arm; deliberately held for methodology-settle + focus).
```

## NET POSITIVE from the brief Option-C window (verify-before-asserting catch)
The ~3-min Option-C window wasn't wasted: building ARM-2 surfaced a real cell bug.
```
  My first ternary graded-completion design had a TARGET-IN-KEY LEAK: key(a,b,c) used c=X where X was
  ALSO the recovery target -> trivial recovery for ALL ops -> a FALSE HARD_FAIL (singles "closed" too).
  Caught via verify-before-asserting (the result was uninterpretable). FIXED to the faithful assembly_2
  design: SEPARATE random target labels (no leak) + 3 c-role assignments per real 3-set (c-sensitivity
  makes fully-symmetric singles fail) + a-b swap split (asymmetric singles fail). Compile-OK; runs at GO.
```
So the 2026-06-17 graded ternary run is now MORE robust than if Option C had completed with the leaked cell.
Same class as the 55th (control-leak-at-sanity) + the Director's 60th (relay-vs-direct) -- verify-before-asserting.

## Standing -- GATE-READY HOLD
- Phase B GO: 2026-06-17 morning (Option B, USER-direct-endorsed). All 3 arms re-fire then.
- No compute spent on graded runs until GO (cardinality run killed; ternary not run-for-verdict; C3 not started).
- At GO I run: cardinality (verdict-ready) + ternary (leak-fixed) + build C3.
- Queued USER architectural calls unchanged (formal-oracle kappa STRONG LEAN; infra findings).
-- EXP-DEV (Prover)
