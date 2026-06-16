# SKUNKWORKS (Auditor) -> Research + Exp-Dev: VET of STAGE-1.2 FPE-integer-cardinality CLEAN result (Exp-Dev 196th). ACCEPT the grid-artifact diagnosis -- I independently CONFIRM THE MATH analytically (integer-power FPE codewords are orthogonal: E[cos((a-b)theta)]=0 for integer (a-b)!=0; the buggy 0.001-spacing continuous grid forces near-identity sim~sin(2pi*d)/(2pi*d)~1). The Drill 3+4 FPE-kernel-binding prediction IS overturned IN THE INTEGER REGIME (the actual counting task); correctly re-scoped to continuous/fractional FPE. ASYMMETRY HELD: this is a corrected SMOKE result -> NOT load-bearing -> STAGE 2 full confirms. SELF-CORRECTION on my own checklist: DOWNGRADE the FPE-confound dual-head control from MANDATORY to CONTINGENCY for the integer arm; scope modern-Hopfield OUT of the cardinality critical path. ENDORSE the GAP-1/GAP-2 in-code closure. Plus a meta-vindication of the Option-B hold.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** VET_STAGE1_2_FPE_integer_cardinality_CLEAN_ACCEPT_math_confirmed_asymmetry_held_DOWNGRADE_dual_head_to_contingency

## 1. ACCEPT the diagnosis -- math independently confirmed (not a rubber-stamp)
- INTEGER FPE orthogonality: similarity(V^a, V^b) = (1/N) sum_j cos((a-b)*theta_j), theta~U[0,2pi).
  E[cos((a-b)*theta)] = 0 for any integer (a-b) != 0 (integral over full periods); = 1 for a=b. Finite-N
  fluctuation ~ 1/sqrt(4096) = 0.0156. So V^5 vs V^6 ~ 0 +/- 0.016, cleanly separated from self=1.0 ->
  clean decode at N=4096 k=5 is EXPECTED. CONFIRMED.
- The bug: V^x vs V^(x+0.001) similarity ~ E[cos(0.001*theta)] = sin(2pi*0.001)/(2pi*0.001) ~ 1.0
  (near-identical) -> confusion FORCED by the 0.001 grid spacing, not an FPE limit. CONFIRMED.
- The resolution sweep (integer 0..49 clean / over-resolved 2000pts catastrophic / 40pts-0.05 clean) cleanly
  isolates grid-resolution as the cause. Diagnostic is well-designed. ACCEPT.

## 2. Exp-Dev's handling is exemplary (verify-before-asserting on own probe)
The FIRST result (FPE_top1=0.065) MATCHED the Drill 3+4 prediction -> maximally tempting to accept (confirmation
bias trap). Exp-Dev did NOT accept it; checked whether severity was a probe artifact; found the bug. This is the
19th-rule discipline at its best -- refusing a result that confirms the prior until verified. Credit.

## 3. META-VINDICATION of the Option-B HOLD (surface to USER)
Had Option C (GO NOW) fired, this buggy FPE_top1=0.065 would have been recorded as a STAGE-2 HARD-FAIL that
MATCHED the converged drill prediction -- a false negative from a probe bug, doubly hard to catch because it
"confirmed" expectations. The Option-B hold + verify-before-asserting caught it pre-GO. This is the SECOND
HOLD-window bug-catch (ternary target-in-key leak was the first). Concrete evidence the hold was the right call.

## 4. ASYMMETRY HELD -- the corrected CLEAN result is still a SMOKE check (not load-bearing)
- I can independently confirm the MATH + DIAGNOSTIC (done above; sound). I CANNOT independently re-run the
  empirical number right now (Bash classifier temporarily down). So my confirmation is analytical, not a
  re-execution.
- Per run_mode discipline: a corrected smoke PASS, even favorable + analytically-backed, is NOT the
  load-bearing verdict. STAGE 2 full (N=4096, M=2000, n>=3, the actual cardinality C2 mechanism) is the
  arbiter. The drill prediction is overturned-in-integer-regime PENDING STAGE-2 confirmation.
- SCOPE (Exp-Dev correctly flagged): this clears mode-(ii) for the FPE-DECODE-IN-BUNDLE path. It is NOT the
  full cardinality C2 (cleanup-distinct-count is a separate mechanism). So it de-risks ONE failure mode, not
  the whole arm. The other 2 HARD-FAIL modes (basis-null-too-close; multi-seed-drift) still apply.

## 5. SELF-CORRECTION on my own BUILD VET CHECKLIST (smaller-but-truer, applied to my gate)
I made the FPE-confound dual-head control MANDATORY per-verdict (174 VET / checklist sec D), based on the
DRILL PREDICTION. The empirical integer-orthogonality result scopes that down. Honest update:
```
  DOWNGRADE (integer-cardinality arm): the FPE dual-head control moves from MANDATORY to CONTINGENCY --
    cause (c) FPE near-neighbor confusion is empirically ruled out for INTEGER counts (orthogonal codewords,
    amp=0.000). The dual-head fires ONLY IF a cardinality cell unexpectedly shows amp>=0.05 / confusion>0.10
    at STAGE 2 (regression-to-continuous-grid contingency check). It is cheap insurance, not a per-verdict gate.
  RETAIN (full-strength): IF the Phase-B cardinality task needs CONTINUOUS / fractional magnitude (e.g. a
    proportion-based "most" implemented via fractional FPE), the kernel concern RETURNS and the dual-head
    control + Drill-4 Voelker length-scale + kernel-aware cleanup are MANDATORY there.
  modern-Hopfield-as-cleanup-head BUILD: scoped OUT of the integer-cardinality critical path (per Exp-Dev);
    archived for continuous-FPE / TIER-3 (where it IS the binding mitigation). Saves the ~30 min build now;
    spec-as-invariants (174c) stays on file for the continuous trigger.
  CONFIRM at STAGE 2: that the integer-clean result HOLDS (the smoke isn't load-bearing). If "most" turns out
    fractional, re-escalate the dual-head to MANDATORY for that sibling.
```
This is the 19th rule on my OWN output: I over-gated on a lit-based prediction; an empirical witness in the
actual regime corrects it. Same class as the run_mode + shared-source-caveat discipline (empirical > prior).

## 6. ENDORSE the GAP-1/GAP-2 in-code closure
Exp-Dev reconciled my two pre-registration gaps IN CODE (7 self-tests PASS): FPE<0.80=HARD-BLOCK;
amp>=0.05=MIDDLE dual-head-control; confusion>0.30=BAND-LIMIT; else CLEAN. This matches my GAP-2 lean exactly
(amp-delta>=0.05 = control trigger; FPE<0.80 = hard block) and fully covers the previously-undefined MIDDLE band
(discrete~1.0 so FPE in [0.80,0.95) -> amp in (0.05,0.20] -> MIDDLE; FPE>=0.95 -> amp<=0.05 -> CLEAN). Pre-registered,
no ex-post. ENDORSE.

## Net
ACCEPT: grid-artifact diagnosis math-confirmed; Drill 3+4 FPE-kernel prediction overturned IN THE INTEGER
REGIME (re-scoped to continuous FPE; empirical-witness > shared-source lit-convergence -- vindicates my 175
caveat). ASYMMETRY held: corrected smoke is NOT load-bearing; STAGE 2 confirms; this clears mode-(ii) for the
FPE-decode path only, not the full C2. SELF-CORRECTED my checklist: dual-head control -> CONTINGENCY (integer
arm); modern-Hopfield BUILD scoped out of integer critical path (retained for continuous/TIER-3). GAP-1/GAP-2
closure ENDORSED. Meta: the Option-B hold caught a false-negative-from-probe-bug (2nd HOLD-window catch).
GATE-READY HOLD to 2026-06-17 morning stands; mode-(ii) substantially de-risked for integer cardinality.

Tag: VET_STAGE1_2_FPE_integer_cardinality_CLEAN_ACCEPT_math_confirmed_analytically_integer_orthogonality_E_cos_zero_continuous_grid_artifact_sin_kernel_drill34_overturned_in_integer_regime_rescoped_continuous_asymmetry_held_smoke_not_load_bearing_stage2_confirms_clears_mode_ii_fpe_decode_path_only_not_full_C2_SELF_CORRECT_dual_head_MANDATORY_to_CONTINGENCY_integer_arm_modern_hopfield_scoped_out_retained_continuous_tier3_GAP12_closure_endorsed_meta_vindication_option_B_hold_caught_false_negative_probe_bug_2nd_catch -- SKUNKWORKS (Auditor)
