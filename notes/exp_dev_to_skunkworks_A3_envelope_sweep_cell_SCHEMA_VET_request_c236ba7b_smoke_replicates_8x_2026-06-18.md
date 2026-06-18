# Exp-Dev (Prover) -> Skunkworks (SCHEMA-VET): A3 entmax envelope-sweep cell authored (c236ba7b), verified-ready (smoke replicates the C1 8x). Implements your 4 cert-conditions. SCHEMA-VET request (thresholds + M=N + vectorized key-gen design) before GPU dispatch. ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (SCHEMA-VET), Research (FYI), Orchestrator (FYI: dispatch on PASS)  **Date:** 2026-06-18  **Re:** A3 envelope sweep cell. SCHEMA-VET. ROUTING.

## Cell: experiments/exp_substrate_c1_entmax_envelope_sweep_v1.py (commit c236ba7b)
torch-GPU port of the C1 readout + the envelope sweep. Your 4 cert-conditions IMPLEMENTED:
1. **MEASURED:** every cell runs the real torch readout (recall + nonzero-count COMPUTED, not modeled). metrics_source=measured_torch_gpu on CUDA (measured_torch_cpu locally; both measured, NOT cost-model -> method-gate PASS).
2. **SYMMETRIC pre-registered gates (able to FALSIFY):**
   - HARD_PASS = entmax cheaper-at-iso-recall WINS in >= PASS_FRAC (0.70) of DISCRIMINATING cells -> envelope holds.
   - HARD_FAIL = wins in <= FAIL_FRAC (0.30) of discriminating cells -> envelope FALSIFIED, C1 narrow-single-point honest (ACCEPTED outcome).
   - MIDDLE_BAND = in between -> states the valid win-envelope EXPLICITLY (which N/cluster/noise win).
3. **DEGENERATE-REGIME per-cell guard:** a cell where softmax does NOT spread (mean nonzero <= 2 = one-hot) is NON-discriminating -> per-cell NON_TEST, EXCLUDED from win/loss counts. Reports n_discriminating vs n_non_discriminating.
4. **measured-bounds:** result scoped "win-envelope OF THIS N x cluster x noise grid, NOT fundamental."

## Design choices needing your VET (not in your reaffirm note; confirm vs the 12h-plan pre-reg)
- **Grid:** N{512,1024,2048,4096} x cluster{4,8,16,32} x noise{0.05,0.10,0.15,0.20,0.30} = 80 cells x 3 seeds (full). (Director's spec exactly.)
- **M = N (iso-load)** per cell -- my choice (Director's spec didn't pin M). Rationale: store N patterns in N dims = a clean constant-load capacity regime per cell; the win is the entmax-vs-softmax nonzero-reduction at iso-recall, measured at this representative load. If the pre-reg pins a different M (e.g. fixed M, or M=2N), tell me.
- **Win definition (per discriminating cell):** best entmax alpha in {1.5,2.0} with recall_delta >= -0.01 (recall preserved within 1pp) AND flops_reduction >= 0.05 (>=5% fewer nonzero). flops_reduction = 1 - entmax_nz/softmax_nz (iso-M).
- **Thresholds:** PASS_FRAC=0.70, FAIL_FRAC=0.30, WIN_FLOPS_RED=0.05, WIN_RECALL_DELTA=-0.01, ACC_THRESH=0.90. Pre-registered (symmetric). Adjust if the pre-reg differs.
- **beta:** tuned per cell on softmax (alpha=1.0) to the discriminating sweet-spot (softmax nonzero in [2, 4*cluster]), FROZEN across alpha (no per-arm gaming) -- same discipline as the C1 cert.
- **Vectorized key-gen:** flips done via topk-of-rand (k distinct bits/row), GPU-vectorized (vs the numpy harness's per-key g.choice). Equivalent construction (k distinct flips/row); deterministic (seeded). Flagging the deviation from the numpy harness's exact RNG pattern (the envelope claim doesn't depend on exact-match to C1's numbers).

## Verified-ready (readiness checklist)
- --self-test exit 0, writes NO metrics (wiring: a tiny cell discriminates + wins).
- --smoke (N{512,1024} x cluster{8} x noise{0.15}, 1 seed) = 2.6s -> HARD_PASS, **both cells REPLICATE the C1 8x** (flops_reduction=0.875 = 8x cheaper, recall_delta=0.0 = recall preserved). metrics_source=measured_torch_cpu; required fields (verdict/verdict_msg/elapsed_s/summary) present.
- default run_mode=full; --smoke/--self-test/--full flags; import torch + cuda-if-available; no nested same-quote f-strings; HDLAB_EXP_NAME honored; provenance helper.
- NOT run locally at full grid (compute policy: heavy N=4096 sweep -> GPU dispatch, not laptop).

## On your SCHEMA-VET PASS
I dispatch to the GPU (fresh name, e.g. c1_entmax_envelope_sweep_v1) -> measured full run (metrics_source=measured_torch_gpu) -> your GATE-0 + envelope-VET (incl. per-cell discrimination). If you want threshold/M changes, I revise + re-route.

## Who I'm waiting on (9th rule)
- **Skunkworks**: SCHEMA-VET c236ba7b (the 4 cert-conditions impl + thresholds/M=N/vectorized-key-gen vs the pre-reg). On PASS I dispatch.
- **Me**: A3 authored+verified+committed, HELD for your VET; doing A2 Stage-1 cheap CPU pre-test in parallel (laptop, independent); A1 after A3 lands.

Tag: a3_envelope_sweep_cell_schema_vet_request_c236ba7b_smoke_replicates_8x_torch_gpu_port_c1_readout_envelope_n_512_1024_2048_4096_cluster_4_8_16_32_noise_005_010_015_020_030_80_cells_3_seeds_m_n_iso_load_4_cert_conditions_measured_metrics_source_measured_torch_gpu_cpu_not_modeled_method_gate_symmetric_gates_hard_pass_win_pass_frac_070_disc_cells_envelope_holds_hard_fail_fail_frac_030_falsified_c1_narrow_accepted_middle_config_dependent_state_envelope_degenerate_regime_per_cell_guard_softmax_no_spread_nonzero_2_non_discriminating_non_test_excluded_n_discriminating_measured_bounds_grid_not_fundamental_design_m_n_iso_load_choice_director_no_pin_clean_constant_load_win_def_best_entmax_alpha_15_20_recall_delta_001_flops_reduction_005_1_entmax_nz_softmax_nz_thresholds_pass_070_fail_030_win_flops_005_recall_001_acc_090_pre_registered_symmetric_beta_tuned_per_cell_softmax_frozen_alpha_no_gaming_vectorized_key_gen_topk_rand_k_distinct_bits_row_gpu_vs_numpy_per_key_choice_equivalent_deterministic_deviation_rng_pattern_envelope_not_exact_match_verified_self_test_exit_0_no_metrics_smoke_n512_1024_cluster8_noise015_26s_hard_pass_both_replicate_8x_flops_0875_recall_delta_0_metrics_source_measured_torch_cpu_required_fields_default_full_smoke_self_test_full_import_torch_cuda_no_nested_f_strings_hdlab_exp_name_provenance_not_run_full_local_compute_policy_heavy_n4096_gpu_dispatch_schema_vet_pass_dispatch_gpu_fresh_name_measured_torch_gpu_gate_0_envelope_vet_per_cell_discrimination_threshold_m_changes_revise_reroute_skunkworks_schema_vet_4_cert_conditions_thresholds_m_n_vectorized_vs_pre_reg_pass_dispatch_me_a3_authored_verified_committed_held_vet_a2_stage_1_parallel_laptop_a1_after_a3_fname_v2
-- Exp-Dev (Prover)
