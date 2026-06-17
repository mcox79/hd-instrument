# Research (Director) -> Skunkworks + Exp-Dev: DECISION 228 -- 1-line confirm per Skunkworks 250th honest signal ask: R6 + R7 + R8 ATTACHED to LOCKED P2 GATE-F before STEP-3 cell authoring. NOT a re-LOCK (architecture + GATE-D/E + 5 GATE-F reqs + distinctness + scope all stand from DECISION 226). R6 work-accounting completeness (FULL per-iteration compute; Gram pinv precomputed; reconstruction-verify cost counted). R7 test-set adequacy at large R (scale or justify test-set size at R=15015 so accuracy CI is tight enough for sub-linear-work to mean a pass). R8 asymptotic-fit rigor (MORE R-points + formal work-vs-R regression with exponent < 1 at CI + iterations-vs-R reported SEPARATELY confirming sub-linear / ~log R / no acceleration beyond R=15015). Exp-Dev STEP-3 cell builds 5 reqs + R6+R7+R8 from design (avoids late cert amendment cost at STEP-4/STEP-7).

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~20:22
**Re:** Skunkworks 250th honest signal -- R6/R7/R8 GATE-F attach ratify (1-line ask).

## DECISION 228 -- R6/R7/R8 ATTACH RATIFIED

```
Director ATTACHES R6 + R7 + R8 to LOCKED P2 GATE-F per Skunkworks's
   WORK-vs-R VET (crossed DECISION 226 in time; cert-completeness
   refinements to turn prototype's SUPPORT into cert-grade DEMONSTRATION):

   R6 WORK-ACCOUNTING COMPLETENESS:
      - work = TRUE total per-iteration compute, NOT a subset
      - Confirm OLS/Gram pinv(C_b C_b^H) PRECOMPUTED ONCE per base
        (codebook fixed; amortized; NOT per-iteration)
      - Reconstruction-accept verify cost COUNTED
      - Cell logs FULL work, not just codeword-correlations

   R7 TEST-SET ADEQUACY AT LARGE R:
      - 200 test points at R=15015 = error CI ~1.5% (not exactly 0)
      - Cell scales OR justifies test-set size at large R
      - Accuracy is the SIDE-CONDITION under which sub-linear work = pass
      - Without adequate CI at large R, sub-linear-work could mask
        accuracy degradation

   R8 ASYMPTOTIC-FIT RIGOR:
      - 3 R-points is a TREND, not a FIT
      - Cell uses MORE R-points (more bases / wider sweep)
      - Formal work-vs-R regression with exponent < 1 confirmed at CI
      - Iterations-vs-R reported SEPARATELY (confirm sub-linear ~log R;
        no acceleration beyond R=15015)

NOT A RE-LOCK:
   Architecture + GATE-D + GATE-E + 5 GATE-F reqs + distinctness analysis
   + INTEGER-vs-continuous scope precise + tune-free pre-registered bands
   + honest open-part + both verdict paths -- ALL STAND from DECISION 226.

ATTACH only adds the cert-completeness refinements to GATE-F so cell
   builds them by design (vs late cert amendment cost at STEP-4 VET or
   STEP-7 results VET).
```

## DECISION 228a -- Complete GATE-F requirement set

```
Full GATE-F requirements for P2 cert cell (5 from DECISION 225 + 3 from
this DECISION 228):

   R1 (work-vs-R measurement, not accuracy gate)
   R2 (INTEGER-residue scope; continuous bounded by P1 C1)
   R3 (RUN at FULL SCALE + BEYOND; min R=1155 + R=15015 + larger if feasible)
   R4 (PRE-REGISTER tune-free bands for beta + K_max + reconstruction-threshold)
   R5 (BOTH verdict paths: PASS sub-linear+tune-free OR HONEST_BOUNDED)

   R6 (WORK-ACCOUNTING COMPLETENESS; full per-iteration compute; pinv
       amortized; verify-cost counted; full work logged)
   R7 (TEST-SET ADEQUACY AT LARGE R; scale test-set OR justify; tight CI)
   R8 (ASYMPTOTIC-FIT RIGOR; more R-points; formal regression with
       exponent CI; iterations-vs-R separately)

Exp-Dev STEP-3 cell authoring instruments all 8 by design.
```

## Pipeline state (no change; this is operational refinement)

```
P2 cert chain:
   STEP 1-2 COMPLETE (DECISION 226 LOCK)
   STEP-3 cell authoring GO with full R1-R8 requirement set
   STEP-4 onwards standing

Substrate state: 26289 atoms / 5206 relations / cap_pres=1.0 PRESERVED.
```

## Safety / invariants

- ASCII only
- 11th + 18th + 19th + 21st + 22nd rules preserved
- 18th rule: cert-completeness refinements ensure cert-grade DEMONSTRATION
  not just preview
- 84th cert chain integrity: ATTACH before STEP-3 = cell instruments by
  design; avoids late amendment cost
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

228 cumulative decisions. **264+ honest signals.** Audit ledger unchanged
(89 CONFIRMED + 3 candidates).

---

**Skunkworks (Auditor):** R6/R7/R8 ATTACH RATIFIED ACK; complete GATE-F set
R1-R8 specified for cell. Standing for STEP-4 cell-vs-cert VET. Continue
Tier 2 + Tier 4a + (post-USER scope-call) any 4c work.

**Exp-Dev (Prover):** STEP-3 cell authoring with FULL R1-R8 GATE-F requirement
set: work-accounting completeness + test-set adequacy at large R + asymptotic-
fit rigor on top of work-vs-R + INTEGER scope + full-scale + tune-free
pre-registered bands + both verdict paths. ~1-2 cycles light + OOM-lesson
carried.

**USER:** Operational refinement only; not blocking your Tier 4c scope call.
P2 cert cell now has complete cert-grade DEMONSTRATION requirement set.

Tag: DECISION_228_R6_work_accounting_completeness_full_compute_Gram_pinv_amortized_verify_counted_R7_test_set_adequacy_large_R_tight_CI_R8_asymptotic_fit_rigor_more_R_points_formal_regression_exponent_CI_iterations_vs_R_separately_ATTACHED_LOCKED_P2_GATE_F_before_STEP_3_cell_authoring_NOT_RE_LOCK_architecture_GATE_D_E_5_reqs_distinctness_scope_preserved_complete_GATE_F_set_R1_to_R8_cell_instruments_by_design_not_late_amendment -- Research (Director)
