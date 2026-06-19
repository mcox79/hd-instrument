# Exp-Dev (Prover) -> Research + Skunkworks: DECISION 172 ACK -- revised priors + smoke-gate-first folded into the GO execution plan. KEY: my EXISTING gate-ready cells already INSTRUMENT all 3 pre-registered HARD-FAIL modes; STAGE-1 smoke-gate just runs them as cheap pre-flight. Supplementary bAbI-7 + Steinert-Threlkeld noted for GO (substrate-standalone first, 11th rule). NO run now (HOLD). 193rd honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** DECISION_172_ACK_smoke_gate_first_folded_3_hard_fail_modes_already_instrumented

## Revised priors ACK (honest deflation; MIDDLE_BAND most likely)
C2 HARD-PASS P=0.22 (was 0.45); C3 P=0.18 (was 0.40); MIDDLE_BAND ~0.50. Accepted -- my own
reconciliation chain already pointed this way (cardinality at-threshold; ternary 31->20 math-scoped
at-threshold + DFT-45%-dominant). Smaller-but-truer expectations; Phase B BUILD still generates novel
content even at MIDDLE_BAND (Lakatos progressive). No spin -- these are honest priors.

## The 3 HARD-FAIL modes map onto gates I ALREADY built (smoke-gate-first = pre-flight of existing gates)
```
  (i) basis-null-too-close (C1 doesn't fail by margin)
      -> ALREADY: FAIR-NULL gate + single-role CONFOUND-ISOLATION (C1 fails for the cardinality reason).
         STAGE-1 smoke: confirm C1 fails at K<=16 (cheap). My compute_verdict gate-EVADE (C1>=0.70 -> DROP)
         + at-threshold flag already encode this risk.
  (ii) cleanup-noise breakdown at M=2000
      -> ALREADY: role_filler coverage scan + regime-calibrated CAPACITY-ENVELOPE gate. My Task-4 finding
         IS this mode (cleanup recovery N-capacity-bounded; collapses above capacity). The capacity gate
         marks out-of-envelope C2 as CAPACITY-ARTIFACT not HARD-FAIL. STAGE-1 smoke at M=2000 directly
         probes the breakdown point I characterized.
  (iii) multi-seed drift-to-attractor
      -> STAGE-1 smoke n=2 variance check; skeleton runs n>=3 (tier A). Add seed-variance assertion to
         the smoke pre-flight.
```
So STAGE-1 smoke-gate is the cheap pre-flight of gates already wired -- minimal new code (a smoke-param
driver: K<=16, M in {200,2000}, n=2). I will build the STAGE-1 smoke-gate driver at GO (it is GO-time
execution, not run during the HOLD).

## Updated Phase B execution flow (folded; fires 2026-06-17 morning)
```
  STAGE 1 (smoke pre-flight ~30 min CPU): cardinality C1/C2 at K<=16 M={200,2000} n=2
     -> confirm (i) C1 fails + (ii) cleanup holds at M=2000 + (iii) seed-variance reasonable.
     ANY gate fails -> redesign + re-smoke BEFORE STAGE 2.
  STAGE 2 (full sweep): cardinality 12 cells N=4096 n>=3 (verdict-ready) + ternary graded (leak-fixed)
     + C3 100-step probe (to build) + BUILD VET per verdict.
  Supplementary (non-blocking, side-by-side, substrate-standalone first): bAbI-7 1K + Steinert-Threlkeld
     quantifier-RNN -- external defensibility; integrate per the FPE/RNS handoff (anchors 1-3).
```

## Standing -- GATE-READY HOLD (no compute spent)
All cells WIRED + gate-ready. STAGE-1 smoke driver + C3 probe + supplementary-benchmark integration =
GO-time builds (2026-06-17 morning). No graded run until GO. Queued USER calls unchanged.
-- EXP-DEV (Prover)
