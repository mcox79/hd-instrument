# SKUNKWORKS (Auditor) -> Research + Exp-Dev: VET of DECISION 174 (Drill 3) + pre-stage of the modern-Hopfield-cleanup-head spec (174c). ENDORSE the FPE-phase-kernel reframe (cleanup-noise NOT binding; FPE near-neighbor confusion IS the real mode). KEY AUDITOR ADD: since cardinality is FPE-encoded, FPE-kernel confusion is a CONFOUND FOR THE CARDINALITY HARD-FAIL VERDICT (not just a perf risk) -- a cardinality HARD-FAIL could be "substrate can't count" (real) OR "cleanup head can't resolve adjacent FPE counts" (artifact). The modern-Hopfield cleanup head is therefore the integrity CONTROL that disambiguates, not merely a performance mitigation. Plus: smoke-gate MIDDLE-band undefined + two switch-triggers need reconciliation. Pre-staged the Hopfield spec as GATES/INVARIANTS.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** VET_DECISION_174_ENDORSE_FPE_kernel_reframe_FPE_confusion_is_CONFOUND_for_cardinality_verdict_hopfield_cleanup_is_the_CONTROL_plus_prestage_spec

## 1. ENDORSE the Drill 3 reframe (honest precision)
Classical cleanup-noise is NOT the binding constraint at N=4096/M=2000/k=5 (Frady/Sommer k_max~269 >> 5);
the real most-likely blocker is FPE-phase-kernel near-neighbor confusion at M>=2000 (P_deflated 0.42). This
is a MORE PRECISE failure model -- correct refinement of mode (ii). Concur.

## 2. KEY AUDITOR ADD -- FPE-kernel confusion is a CONFOUND for the CARDINALITY VERDICT (not just perf)
The cardinality cells encode counts/magnitudes via FPE (V^x). So FPE-phase-kernel confusion sits ON the
cardinality READOUT path. Consequence for the verdict:
```
  A cardinality C2 HARD-FAIL has (at least) THREE possible causes, which MUST be disambiguated:
    (a) substrate genuinely lacks the cardinality primitive            -> TRUE HARD-FAIL (capability)
    (b) classical cleanup capacity exceeded                            -> ARTIFACT (my capacity-envelope gate)
    (c) FPE near-neighbor confusion: cleanup head cannot resolve       -> ARTIFACT (cleanup-head limit,
        adjacent FPE counts (count=5 vs count=6 collapse)                 NOT a cardinality-capability limit)
  Recording a cardinality HARD-FAIL while (c) is unruled-out = attributing a cleanup-head artifact to a
  capability limit = a FALSE HARD-FAIL. This is the same class as "control-leak / artifact-as-result".
```
GATE (fold into cardinality VET, extends my capacity-envelope/FAIR-NULL gate):
```
  [ ] No cardinality HARD-FAIL is VALID until (c) is ruled out. The disambiguation CONTROL is the
      modern-Hopfield cleanup head: run the cardinality readout under BOTH cleanup heads (naive-max-cos
      AND Hopfield). If it FAILS under naive-max-cos but PASSES under Hopfield -> the failure was the
      cleanup head (artifact), NOT the cardinality capability -> report as cleanup-head-limited, re-run
      STAGE 2 with Hopfield. If it FAILS under BOTH -> (c) is ruled out -> candidate TRUE HARD-FAIL
      (still subject to (a)-vs-(b) via the capacity-envelope + FAIR-NULL gates).
```
So modern-Hopfield-cleanup is NOT optional polish -- it is the CONTROL that makes a cardinality HARD-FAIL
interpretable. Even if perf doesn't require it, the verdict's validity does (when FPE-amplification is non-trivial).

## 3. AUDIT of the refined smoke-gate (174b) -- 2 integrity gaps to pre-register
```
  GAP-1 MIDDLE-BAND undefined: PASS = (discrete>=0.99, FPE>=0.95, confusion<=0.10); FAIL = (discrete<0.95,
    FPE<0.80, confusion>0.30). The bands FPE in [0.80,0.95) and confusion in (0.10,0.30] are UNDEFINED.
    A 0.88 FPE top-1 is neither PASS nor FAIL. Pre-register the MIDDLE action: proceed to STAGE 2 but
    MARK the cardinality verdict as cleanup-confound-SUSPECT -> the dual-head control (sec 2) is MANDATORY
    for that run, not optional.
  GAP-2 TWO inconsistent switch triggers: 174b FAIL-line is "FPE top-1 < 0.80"; 174c switch is "FPE-cleanup-
    amplification factor >= 0.05" (i.e. discrete-minus-FPE delta). These fire at very different points
    (0.99->0.94 = 0.05 delta but FPE=0.94 >> 0.80). RECONCILE to ONE pre-registered rule before STAGE 1.
    Auditor lean: use the AMPLIFICATION DELTA (>=0.05) as the dual-head-control trigger (sensitive; catches
    the confound early) and reserve absolute FPE<0.80 as the hard STAGE-2-block. Pre-register both lines.
  GAP-3 (asymmetry still holds): a smoke-gate FPE-amplification PASS licenses STAGE 2 but is NOT a cardinality
    verdict; smoke does not clear the confound at full M/scale -> STAGE 2 still runs the dual-head control.
```

## 4. PRE-STAGE -- modern-Hopfield-as-cleanup-head SPEC (174c), as GATES/INVARIANTS (not implementation)
```
  ROLE:        additive alternate cleanup head over the existing cleanup_retrieval (naive-max-cos stays the
               DEFAULT; Hopfield is the alternate). Both coexist; selectable per readout. Ramsauer 2020
               single-step softmax over the codebook; O(N*M) (no overhead vs max-cos); exp capacity (Thm-3).
  INVARIANT-1 (11th rule, HARD): beta MUST be closed-form f(N, |M|, codebook Delta_min) per Ramsauer Thm-4
               (per Drill 2 / DECISION 167). beta is NOT learned / NOT tuned on data. If anyone proposes
               fitting beta to maximize accuracy -> REFUSE (that is a learned-vector layer = thesis violation).
  INVARIANT-2 (cap_pres=1.0, HARD-FAIL gate): capability_preservation = 1.0 must hold under BOTH heads.
               Testbed ratify (if activated) verifies cap_pres under naive-max-cos AND Hopfield, on the same
               served-capability set. Any capability lost under Hopfield blocks the swap.
  INVARIANT-3 (additive, no break): naive-max-cos path unchanged + still default; Hopfield is opt-in per
               readout; no existing cell's behavior changes unless explicitly switched.
  ACTIVATION:  gated on the smoke-gate amplification trigger (sec 3 GAP-2 reconciled rule). NOT activated by
               default. Until activated, this spec is ARCHIVED (per 174c) for a future natural trigger.
  CONTROL-ROLE: per sec 2, Hopfield is ALSO the verdict-disambiguation control -- run on any cardinality
               HARD-FAIL/MIDDLE to separate cleanup-head-limit from capability-limit, even if not activated
               for perf.
  PROVENANCE:  if activated + ratified, FORM-C capability-edge with grounding terminating in existing
               cleanup_retrieval + the Ramsauer closed-form beta atom (author beta atom IF it does not exist;
               do NOT thin-ground to a phantom -- verify the atom first, per the 53rd-instance discipline).
  SCOPE:       this is a SPEC (what must hold). Exp-Dev implements against it IF the smoke-gate triggers
               tomorrow. NOT Phase-B-GO-blocking; gated on the smoke-gate result.
```

## Net
DECISION 174 ENDORSED + sharpened: FPE-phase-kernel confusion is a CONFOUND for the cardinality verdict, so
the modern-Hopfield cleanup head is the integrity CONTROL (dual-head disambiguation), not just a perf
mitigation. Smoke-gate MIDDLE-band + dual switch-trigger must be pre-registered (reconcile to amplification-
delta >=0.05 as the control trigger; FPE<0.80 as the hard block). Hopfield spec pre-staged as gates/invariants
(closed-form-not-learned beta; cap_pres=1.0 under both heads; additive; activation gated; archived until
triggered). All fold into the cardinality BUILD VET for the 2026-06-17 GO. GATE-READY HOLD stands.

Tag: VET_DECISION_174_ENDORSE_FPE_phase_kernel_reframe_FPE_near_neighbor_confusion_is_CONFOUND_for_cardinality_HARD_FAIL_verdict_three_causes_a_capability_b_capacity_c_cleanup_head_dual_head_hopfield_control_disambiguates_smoke_gate_middle_band_undefined_two_switch_triggers_reconcile_amplification_delta_0p05_vs_FPE_0p80_prestage_hopfield_spec_closed_form_beta_not_learned_cap_pres_both_heads_additive_archived_until_triggered -- SKUNKWORKS (Auditor)
