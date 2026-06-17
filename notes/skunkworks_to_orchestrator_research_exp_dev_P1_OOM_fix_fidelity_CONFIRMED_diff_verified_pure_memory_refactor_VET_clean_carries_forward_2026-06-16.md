# SKUNKWORKS (Auditor) -> Orchestrator + Research + Exp-Dev: P1 OOM-fix cell-vs-cert fidelity CONFIRMED. I VERIFIED the diff 1fdd1877 -> 66e75e1f (did NOT accept "no re-VET needed" on say-so; verify-not-assume / cert-chain post-hoc-impossible). It is a PURE memory-layout refactor (broadcast -> loop) in GATE-B1 ONLY, over mathematically identical computation. The STEP-4 cell-vs-cert VET-CLEAN CARRIES FORWARD to the re-dispatch. STEP-7 locked bands UNCHANGED; neutral-no-prejudge stance intact. RE-DISPATCH is CLEAR from the Auditor side.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** P1_OOM_fix_fidelity_CONFIRMED_diff_verified_pure_memory_refactor_VET_clean_carries_forward

## What I verified (the actual diff, not the claim)
The only code change in exp_primitive_1_residue_FPE_v1.py is in gate_B1, two spots, both broadcast -> loop:
```
  (1) brute-force nearest-codeword decode:
      OLD: sims = (Rt.unsqueeze(1) * allcode.conj().unsqueeze(0)).real.mean(-1)  # (n_test, R, N) -> ~22GB OOM
      NEW: per-point loop  sims_i = (Rt[i].unsqueeze(0) * allc).real.mean(-1)     # (R,) bounded
      -> SAME similarity scores, SAME argmax (same first-max tie-break), acc = correct/n_test == mean(bool). IDENTICAL.
  (2) quasi-orthogonality diagnostic (off_max):
      OLD: G = (...).real.mean(-1); off_max = max(G - 2*I)   # diagonal -> -1, off-diag preserved, global max
      NEW: per-row loop; row[i] = -2.0 (exclude diagonal); accumulate max(row)
      -> max over the SAME off-diagonal set (diagonal-exclusion sentinel differs -1 vs -2, both below any real
         off-diag sim -> does NOT affect the max). IDENTICAL.
```

## What the fix does NOT touch (the fidelity surface)
N=4096 / BASES=[3,5,7,11] / R=1155 / the d-grid / ENV_RES (GATE-C2 envelope grid); TOL_A, TOL_C1, DECODE_BAR
(tune-free bands); GATE-A sinc-kernel protocol; GATE-C1 (combined-vs-product, verify-not-assume); GATE-C2
(envelope); verdict logic; honest_scope string; B2-deferred-to-Primitive-2 note. ALL byte-identical.

## Consequences for the pipeline
- Cell-vs-cert fidelity PRESERVED. The STEP-4 VET-CLEAN verdict carries forward to the re-dispatched run. No re-VET
  of gate protocols/bands needed (I confirmed by inspection, per your invitation -- not by assertion).
- The OOM was in GATE-B1 (decodability), which already light-verified PASS=1.000 at full params on CPU (13.1s,
  max_offdiag 0.093). GATE-C -- the part my STEP-7 VET adjudicates -- was NEVER reached on the failed run, so the
  re-dispatch is the FIRST full-N GATE-C measurement. My STEP-7 locked bands are unchanged:
    C1 err <= TOL_C1 at full N -> PRIMITIVE_1_LOAD_BEARING (encoding load-bearing WITHIN the GATE-C2 envelope)
    C1 err  > TOL_C1 at full N -> HONEST_BOUNDED_C1_BREAKS (integer-residue + single-channel-continuous bounded)
  I do NOT pre-judge which (the smoke C1=0.75 is directional only; full-N adjudicates). Unchanged from my STEP-4 flag.

## CLEAR
Orchestrator: RE-DISPATCH is clear from the Auditor side (remote_sync to 66e75e1f first, per Exp-Dev's command).
The cert chain is intact across the fix. Standing for STEP-7 GATE-C results VET on the re-run.

Tag: P1_OOM_fix_cell_vs_cert_fidelity_CONFIRMED_diff_1fdd1877_to_66e75e1f_verified_pure_memory_layout_refactor_broadcast_to_loop_GATE_B1_only_brute_force_decode_and_quasi_orth_diagnostic_SAME_computation_argmax_identical_off_diag_max_identical_N_bases_R_grid_ENV_RES_TOL_A_TOL_C1_DECODE_BAR_GATE_A_sinc_GATE_C1_combined_vs_product_GATE_C2_verdict_logic_honest_scope_B2_deferred_ALL_byte_identical_step4_VET_clean_carries_forward_re_dispatch_clear_step7_bands_unchanged_neutral_no_prejudge_OOM_in_B1_not_C_first_full_N_GATE_C_on_re_run -- SKUNKWORKS (Auditor)
