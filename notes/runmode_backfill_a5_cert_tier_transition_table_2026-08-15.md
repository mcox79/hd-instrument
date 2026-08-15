# run_mode backfill: OLD -> NEW cert-tier transition table (Skunkworks A5, 2026-08-15)

Companion to `notes/runmode_ingestion_fix_source_patched_backfill_deferred_2026-08-15.md`
(Testbed: source fix + guard, landed `f7affa518`). This note is the **cert-tier**
reclassification half, which is A5-gated and Skunkworks-owned. Published BEFORE any write.

## 0. The one-sentence framing

**Nothing is deleted, demoted, or refuted. The results are real; the LABEL was wrong.**
A smoke result is evidence of what it measured at the scale it measured. This backfill makes
the stored label say so. Verdicts, key_metrics, headlines, relations and relevance_tier are
untouched; `run_mode` and `provenance_quality` are corrected, and the description sentence that
quotes them is corrected to match.

Counter-evidence is preserved and was re-verified off disk, not inherited from the brief:
`data/exp_kf2_isolation_proof_v2_n4096_audit/metrics.json` has `config.smoke = False` (a genuine
full run) at `N=4096` with `max_iso=0.02020 < 0.05`, HARD_PASS. **The isolation finding itself is
independently corroborated by a non-smoke sibling.** So the kf2 defect is LABELLING, NOT REFUTATION.

## 1. What was verified, and what turned out to be wrong

Three of my own inputs failed verification. Each is recorded because the correction is load-bearing.

**(a) `relevance_tier` does NOT move. It was asserted that it would.**
Both the predecessor note and the dispatch brief state that backfilling `run_mode` "necessarily
moves `provenance_quality` AND `relevance_tier`". Off data: **0 of 273 tiers move.**
`classify_relevance()` (`tools/atomize_experiment_records.py:498`) reads `run_mode` only as
`run_mode == "full"` and `pq` only as `pq == "CERT_CHAIN_GRADE"`. Under `None -> "smoke"` and
`{LEGACY_EXCERPT,UNVERIFIED} -> SMOKE_ONLY`, both comparisons are False before AND after, so the
function is invariant. `depends_on`/`cap_serving` enter only via two booleans, so the input space
is finite and was enumerated EXHAUSTIVELY: 54 points, 0 differ, **with a negative control proving
the check can fail** (`None -> "full"` moves 2 verdict classes). Only `provenance_quality` moves.

**(b) The recommended write path would have silently DELETED 20 atoms.**
The brief instructed using the tool's own `--apply` fresh-load-per-batch path. Measured:
`schema.load_atoms()` **silently skips malformed rows** -- 20 on this partition (15x `KeyError
'corpus'`, 4x `KeyError 'id'`, 1x `ValueError`), several named `*_FULL_CHAIN_GRADE_*`.
`Store.add_atom -> _flush_atoms() -> save_atoms(list(self._by_id.values()))` writes back only what
loaded, so **every one of those 20 would be erased**, and the existing gate `post_atoms ==
pre_atoms` CANNOT catch it because both sides are measured after the lossy load (29611 == 29611).
Raw JSONL lines 29631, `load_atoms()` returns 29611. This is why the backfill is a line-level
rewrite that passes every untouched line through **byte-for-byte**.

**(c) A line-ending scare that was itself a tooling artifact.**
`save_atoms` opens in text mode, which on this Windows box produces CRLF (verified empirically),
while the partition on disk is LF-only (verified: 0 CRLF in a 200KB sample; tail ends `}\n`). An
earlier check of mine using `od -c | grep -c '\\r'` returned 15 and looked like CRLF -- that was
**bogus**: the shell reduced the pattern to the literal letter `r`, so it counted `od` output lines
containing "r". The real answer is that `.gitattributes` already carries
`data/substrate_index/** text eol=lf`, which neutralises the churn at the git layer by design.
The rewriter still writes explicit LF.

## 2. Scope, enumerated (not searched)

`scratch/scan_runmode_affected_atoms.py --self-test` re-run: **7/7 PASS**, including the
`exp_capacity_ceiling_near_far_v1_SMOKE_n150` counter-example (`n150` = `n_items=150`, not a
dimension) correctly excluded. Full re-scan: **3774 experiment_record atoms examined, 273 flagged**,
reproducing the predecessor count exactly. All 273 are in the `math` partition; **`concept` has 0**,
so `concept/atoms.jsonl` is not touched at all.

Independent re-derivation of the same population by different code agreed on 268 and disagreed on 5.
Cause found and benign: the scan's honest-name exclusion is `_smoke(_|$)`, so the five
`..._smoketest` atoms are not treated as self-disclosing. They are included; their metadata is
wrong either way. No defect in either counter.

Residue classes deliberately OUT OF SCOPE (from `scratch/runmode_residue_audit.py`, 3774 atoms partitioned exhaustively -- every atom is assigned to exactly one class):

- `A_run_mode_already_set`: **2070**
- `B_run_mode_None_metrics_UNREADABLE`: **3**
- `C_smoke_source_but_honest_name_EXCLUDED`: **76**
- `D_IN_THE_273`: **268**
- `E_run_mode_None_resolves_to_UNKNOWN`: **1252**
- `E_run_mode_None_resolves_to_full`: **103**
- `E_run_mode_None_resolves_to_smoke`: **2**

- **CLASS C (76 atoms)** are the same defect with a self-disclosing `_smoke` name. Their
  stored metadata is equally wrong (`run_mode None`, `pq LEGACY_EXCERPT`). Correcting them is the
  identical transformation with the identical invariance proof. I did NOT widen scope unilaterally;
  this is a one-flag follow-up and should be a deliberate call, not an auditor's side-effect.
- **CLASS E-full (103 atoms)** would resolve to `"full"`, an UPGRADE. Checked: **0 would reach
  `CERT_CHAIN_GRADE`** (85 stay LEGACY_EXCERPT, 16 stay UNVERIFIED, 2 would move LEGACY_EXCERPT ->
  UNVERIFIED, i.e. downward). Low risk, but an upward provenance move is a promotion and is not
  in tonight's authorised scope.
- **CLASS B (3 atoms)** cite a `metrics_path` that no longer reads. Two of the three are
  `data/cornerstone_results/...` files showing as **deleted in the working tree by another agent
  tonight** -- flagged, not mine to act on.

## 3. OLD -> NEW transition table

Recomputed by calling the REAL `resolve_run_mode()` / `provenance_quality()` /
`classify_relevance()` against a fresh re-read of each atom's own cited `metrics.json`.
`0` metrics re-read errors, `0` atoms missing from the partition.

Cross-check that this is label-only: **verdict recomputed from source == verdict stored for
273/273** atoms -- no verdict drifts. And **273/273** descriptions carry the literal
`run_mode None`, so every one has the exact edit anchor.

| field | transition | count |
|---|---|---|
| run_mode | `None` -> `smoke` | 273 |
| provenance_quality | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | 257 |
| provenance_quality | `UNVERIFIED` -> `SMOKE_ONLY` | 16 |
| relevance_tier | `ARCHIVE` -> `ARCHIVE` | 200 |
| relevance_tier | `LOW` -> `LOW` | 61 |
| relevance_tier | `MEDIUM` -> `MEDIUM` | 12 |

Tier population is unchanged: {'MEDIUM': 12, 'ARCHIVE': 200, 'LOW': 61}.

### 3a. PRIORITY SUBSET -- the 12 `relevance_tier: MEDIUM` atoms, individually

These are `linked_found` (they cite a real T2/T3 primitive) AND `PASS`, so they are the most
likely to be leaned on elsewhere.

| # | atom_id | run_mode | provenance_quality | relevance_tier | verdict | n_seeds |
|---|---|---|---|---|---|---|
| 1 | `T3/EXP_axis1_mb_chunk1_v1` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 2 | `T3/EXP_bid_n_stability_v2` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 3 | `T3/EXP_c1_kf_battery_phase_v1_n4096` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 4 | `T3/EXP_fluctuation_dissipation_ooe_v1` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 5 | `T3/EXP_kf45_pre_argmax_joint_probe_v1_n4096` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 6 | `T3/EXP_modern_hopfield_pipeline_validation_v1_n2048_n4096` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 7 | `T3/EXP_n_scaling_cpu_only_v8_n16384` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 8 | `T3/EXP_operating_point_singularity_basin_map_v1_n4096` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 9 | `T3/EXP_reasoning_storage_4way_cleanup_v1_n16384` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 10 | `T3/EXP_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | 1 |
| 11 | `T3/EXP_wave14_corpus_N_scaling_tau_unblock_v1` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |
| 12 | `T3/EXP_wave14f_hippo_warmstart_v1` | `None` -> `smoke` | `LEGACY_EXCERPT` -> `SMOKE_ONLY` | `MEDIUM` (unchanged) | PASS | None |

**Read this carefully:** these 12 stay `MEDIUM` after the backfill. `classify_relevance` awards
MEDIUM on `linked_found and pos` and never consults `run_mode`, so a single-seed smoke can hold
`relevance_tier: MEDIUM`. The honest signal lands in `provenance_quality: SMOKE_ONLY`, not in the
tier. **Whether MEDIUM should itself be gated on `run_mode` is a real open cert-policy question,
and answering it downward would be a DEMOTION -- explicitly excluded tonight.** I am flagging it,
not deciding it.

### 3b. Full enumeration of all affected atoms

All rows below: `run_mode None -> smoke`, `relevance_tier` unchanged. Grouped by the
`provenance_quality` transition, then by tier.

#### provenance_quality `LEGACY_EXCERPT` -> `SMOKE_ONLY`  (257 atoms)

<details><summary>relevance_tier <code>MEDIUM</code> (unchanged) -- 12 atoms</summary>

- `T3/EXP_axis1_mb_chunk1_v1` -- verdict PASS
- `T3/EXP_bid_n_stability_v2` -- verdict PASS
- `T3/EXP_c1_kf_battery_phase_v1_n4096` -- verdict PASS
- `T3/EXP_fluctuation_dissipation_ooe_v1` -- verdict PASS
- `T3/EXP_kf45_pre_argmax_joint_probe_v1_n4096` -- verdict PASS
- `T3/EXP_modern_hopfield_pipeline_validation_v1_n2048_n4096` -- verdict PASS
- `T3/EXP_n_scaling_cpu_only_v8_n16384` -- verdict PASS
- `T3/EXP_operating_point_singularity_basin_map_v1_n4096` -- verdict PASS
- `T3/EXP_reasoning_storage_4way_cleanup_v1_n16384` -- verdict PASS
- `T3/EXP_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384` -- verdict PASS
- `T3/EXP_wave14_corpus_N_scaling_tau_unblock_v1` -- verdict PASS
- `T3/EXP_wave14f_hippo_warmstart_v1` -- verdict PASS

</details>

<details><summary>relevance_tier <code>LOW</code> (unchanged) -- 52 atoms</summary>

- `T3/EXP_alpha1_cleanup_sweep_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_axis1_mb_chunk2_v1` -- verdict MIDDLE_BAND
- `T3/EXP_axis3_triplepoint_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_bid_m_normalized_v1` -- verdict MIDDLE_BAND
- `T3/EXP_bid_m_normalized_v4_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_bid_m_normalized_v5_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_bid_n_sweep_v1` -- verdict MIDDLE_BAND
- `T3/EXP_bid_order_parameter_v6_n4096` -- verdict HARD_FAIL
- `T3/EXP_bid_order_parameter_v7_n4096_bsc` -- verdict HARD_FAIL
- `T3/EXP_bid_substrate_probe_v1` -- verdict MIDDLE_BAND
- `T3/EXP_c2_order_param_id_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_cross_shard_correlation_k10_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_gpu_large_n_rescue_serialized_v1_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_hatano_sasa_v3_n8192_multiseed` -- verdict MIDDLE_BAND
- `T3/EXP_kf1_hallu_rescue_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_kf2_be1_retrieval_acc_n8192` -- verdict HARD_FAIL
- `T3/EXP_kf4_drift_detect_v1` -- verdict MIDDLE_BAND
- `T3/EXP_kf4_drift_detect_v4_n4096` -- verdict HARD_FAIL
- `T3/EXP_lyapunov_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_m1_boundary_fine_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_maes_netocny_frenesy_positivity_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_modern_hopfield_ceiling_probe_gpu_v1_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_modern_hopfield_cpu_backup_extended_v1_n16384` -- verdict MIDDLE_BAND
- `T3/EXP_modern_hopfield_cpu_extended_v10_n16384` -- verdict MIDDLE_BAND
- `T3/EXP_modern_hopfield_cpu_extended_v9_n16384` -- verdict MIDDLE_BAND
- `T3/EXP_modern_hopfield_replication_gpu_v1_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_multi_hop_higher_m_stress_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_n_scaling_chunked_codebook_v4_n16384` -- verdict MIDDLE_BAND
- `T3/EXP_ne1_mct_aging_signature_v2_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_ne2_dmft_retrieval_cliff_v1` -- verdict MIDDLE_BAND
- `T3/EXP_ortho_noneq_corroborator_v1` -- verdict MIDDLE_BAND
- `T3/EXP_pb1_susceptibility_v2_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_pb2_corr_len_bsc_v1` -- verdict HARD_FAIL
- `T3/EXP_pb2_corr_len_v4_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_phase_region_cd_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_region_c_kf1_n4096_beta64_mfrac4` -- verdict MIDDLE_BAND
- `T3/EXP_sagawa_ueda_mutual_info_jarzynski_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_sagawa_ueda_v6` -- verdict MIDDLE_BAND
- `T3/EXP_spectral_graph_alt_predictors_v1` -- verdict MIDDLE_BAND
- `T3/EXP_spectral_graph_anticorr_v1` -- verdict MIDDLE_BAND
- `T3/EXP_spectral_graph_lambda2_v4` -- verdict MIDDLE_BAND
- `T3/EXP_superposition_single_hop_decomp_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_t1_beta_fine_v2_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_t1_m_sweep_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_tda_moe_w_crossvalidation_v1` -- verdict HARD_FAIL
- `T3/EXP_tda_reanalysis_5probe_v1` -- verdict HARD_FAIL
- `T3/EXP_tensor_binding_two_shard_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_wave14_beti_depth_polylog_v1` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_beti_depth_polylog_v3` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_moe_cosine_router_v2_k_stress` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_moe_cosine_router_v3_dynamic` -- verdict HARD_FAIL
- `T3/EXP_wave14_moe_hebbian_anchor_router_v1` -- verdict HARD_FAIL

</details>

<details><summary>relevance_tier <code>ARCHIVE</code> (unchanged) -- 193 atoms</summary>

- `T3/EXP_adaptive_threshold_rescue_v2_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_adaptive_threshold_rescue_v3_n4096` -- verdict HARD_FAIL
- `T3/EXP_adversarial_a_query_sim_defense_cpu_n8192` -- verdict PASS
- `T3/EXP_adversarial_aqsim_path_d_compose_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_adversarial_aqsim_path_d_compose_v2_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_adversarial_aqsim_path_d_compose_v3_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_adversarial_aqsim_path_d_compose_v5_k2_n16384` -- verdict MIDDLE_BAND
- `T3/EXP_adversarial_codebook_collision_defense_probe_v1_n4096` -- verdict PASS
- `T3/EXP_adversarial_multi_hop_probing_v2_n4096` -- verdict HARD_FAIL
- `T3/EXP_agentic_edge_cases_v1_n4096` -- verdict PASS
- `T3/EXP_agentic_workload_characterization_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_alpha2_codebook_variation_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_alternative_edit_isolation_mechanisms_v1_n4096` -- verdict PASS
- `T3/EXP_aqsim_3way_diagnostic_v1` -- verdict PASS
- `T3/EXP_aqsim_3way_diagnostic_verbose_v2_n4096` -- verdict PASS
- `T3/EXP_axis1_mb_chunk4_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_axis1_mb_chunk5_n4096` -- verdict PASS
- `T3/EXP_axis1_mb_chunk6_n4096` -- verdict PASS
- `T3/EXP_axis1_mb_chunk7_n4096` -- verdict PASS
- `T3/EXP_axis1_mb_chunk8_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_axis1_mb_chunk9_v1_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_axis2_codebook_density_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_axis3_triplepoint_v2_n4096` -- verdict PASS
- `T3/EXP_axis3_triplepoint_v3_n4096` -- verdict PASS
- `T3/EXP_axis4_hyst_ramp_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_bet_b_genreplay_phaseD_v1_n2048` -- verdict MIDDLE_BAND
- `T3/EXP_bet_b_moe_per_task_dg_gating_v1_n2048` -- verdict MIDDLE_BAND
- `T3/EXP_bet_b_tp_hdc_subspace_v1_n2048` -- verdict MIDDLE_BAND
- `T3/EXP_c3_tcft_phase_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_calibrated_confidence_ece_v1_n1024` -- verdict PASS
- `T3/EXP_chunked_codebook_n16384_v6_smoketest` -- verdict PASS
- `T3/EXP_compressed_path_d_composition_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_compressed_path_d_composition_v2_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_continuous_output_multi_hop_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_depth_sanity_check_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_dp_gaussian_write_noise_v1_n512` -- verdict PASS
- `T3/EXP_dr_merkle_randproj_w_verify_v1_n4096` -- verdict PASS
- `T3/EXP_edit_audit_trail_refinement_v1_n4096` -- verdict PASS
- `T3/EXP_edit_impact_dag_reverse_traversal_v1` -- verdict PASS
- `T3/EXP_edit_isolation_guard_probe_v1_n4096` -- verdict PASS
- `T3/EXP_free_prob_free_additivity_v1_n4096` -- verdict PASS
- `T3/EXP_free_prob_kmax_formula_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_free_prob_rank1_edit_perturb_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_handoff_composition_probe_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_hier_concept_v2_structured` -- verdict HARD_FAIL
- `T3/EXP_hier_concept_v3_costructured` -- verdict MIDDLE_BAND
- `T3/EXP_kf1_hallu_impossibility_v1` -- verdict PASS
- `T3/EXP_kf1_hallu_impossibility_v2` -- verdict MIDDLE_BAND
- `T3/EXP_kf1_hallu_rescue_v4_n8192_bsc` -- verdict MIDDLE_BAND
- `T3/EXP_kf1_tier1_rescue_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_kf2_be1_fp32_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_kf2_be1_int1_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_kf2_be1_int8_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_kf2_be1_soft_readout_n8192` -- verdict HARD_FAIL
- `T3/EXP_kf2_cpu_v1` -- verdict MIDDLE_BAND
- `T3/EXP_kf2_cross_codebook_v2_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_kf2_edit_impact_v1` -- verdict MIDDLE_BAND
- `T3/EXP_kf2_isolation_proof_v1` -- verdict PASS
- `T3/EXP_kf2_isolation_proof_v2_n8192` -- verdict PASS
- `T3/EXP_kf3_multisub_isolation_v1` -- verdict MIDDLE_BAND
- `T3/EXP_kf3_multisub_v3_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_kf3_multisub_v4_n4096_codebook` -- verdict MIDDLE_BAND
- `T3/EXP_kf4_drift_detect_v2` -- verdict PASS
- `T3/EXP_kf4_drift_detect_v5_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_kf5_fine_beta_betac_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_kf5_multi_output_steer_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_kf5_steerable_beta_v1` -- verdict MIDDLE_BAND
- `T3/EXP_kf5_steerable_beta_v2` -- verdict MIDDLE_BAND
- `T3/EXP_kf5_steerable_beta_v3_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_large_deviations_substrate_v1` -- verdict HARD_FAIL
- `T3/EXP_large_k_path_scaling_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_longtail_zipfian_pp10a_v1_n4096` -- verdict PASS
- `T3/EXP_mechanism_composition_at_breaking_v2_n4096_smoketest` -- verdict MIDDLE_BAND
- `T3/EXP_mechanism_composition_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_memory_pattern_characterization_v1_n4096` -- verdict PASS
- `T3/EXP_moe_capacity_v2_n4096` -- verdict PASS
- `T3/EXP_moe_capacity_v3_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_moe_fixed_total_capacity_K_sweep_v1_n4096` -- verdict PASS
- `T3/EXP_moe_gradient_router_v1` -- verdict HARD_FAIL
- `T3/EXP_multi_hop_adversarial_concurrent_edits_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_multi_hop_caching_baseline_v1_n4096` -- verdict PASS
- `T3/EXP_multi_hop_caching_baseline_v2_n4096` -- verdict PASS
- `T3/EXP_multi_hop_caching_baseline_v3_n4096` -- verdict PASS
- `T3/EXP_multi_hop_noise_robustness_v1_n4096_smoketest` -- verdict MIDDLE_BAND
- `T3/EXP_multi_hop_stress_at_breaking_v1_n4096_smoketest` -- verdict PASS
- `T3/EXP_multi_signal_kf1_design_v2_n4096` -- verdict PASS
- `T3/EXP_multi_signal_kf1_refinement_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_multi_tenant_arch1_full_v1_n16384` -- verdict PASS
- `T3/EXP_ne2_dmft_retrieval_cliff_v2_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_ne4_su_landauer_cert_v1` -- verdict MIDDLE_BAND
- `T3/EXP_ne5_su_audit_no_benefit_v1` -- verdict PASS
- `T3/EXP_ortho_noneq_v2_n4096` -- verdict PASS
- `T3/EXP_path_b_subcapacity_characterization_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_path_d_24n_32n_envelope_v1_n4096` -- verdict PASS
- `T3/EXP_path_d_adversarial_composition_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_path_d_adversarial_composition_v2_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_path_d_cpu_latency_profiling_v1_n4096` -- verdict PASS
- `T3/EXP_path_d_edit_isolation_under_load_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_path_d_high_k_scaling_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_path_d_k1_cross_n_null_prediction_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_path_d_k1_phase_boundary_cross_m_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_path_d_k1_phase_boundary_probe_v1_n4096` -- verdict PASS
- `T3/EXP_path_d_k_fine_grained_transition_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_path_d_latency_profiling_v1_n4096` -- verdict PASS
- `T3/EXP_path_d_mixed_confidence_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_path_d_upper_envelope_stress_v1_n4096` -- verdict PASS
- `T3/EXP_path_e_engineering_characterization_v1_n4096` -- verdict PASS
- `T3/EXP_path_e_latency_envelope_v1_n4096_smoketest` -- verdict MIDDLE_BAND
- `T3/EXP_path_probability_propagation_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_pb1_susceptibility_v1` -- verdict MIDDLE_BAND
- `T3/EXP_pb2_corr_len_v3_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_pb2_correlation_length_v1` -- verdict HARD_FAIL
- `T3/EXP_pb3_critical_slowing_v1` -- verdict HARD_FAIL
- `T3/EXP_pb3_extended_v2_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_pb3_extended_v3_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_pb3_extended_v6_v3identical_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_pp4_codebook_histogram_divergence_v1` -- verdict MIDDLE_BAND
- `T3/EXP_pp4_write_retrieve_ratio_drift_v1` -- verdict PASS
- `T3/EXP_qe1_substrate_annealing_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_qe3_syndrome_error_correction_v1_n4096` -- verdict HARD_FAIL
- `T3/EXP_reasoning_storage_threshold_sweep_v1_n4096` -- verdict PASS
- `T3/EXP_region_d_kf1_n4096_beta64_mfrac12` -- verdict MIDDLE_BAND
- `T3/EXP_saad_solla_v12_n8192_5seed` -- verdict MIDDLE_BAND
- `T3/EXP_saad_solla_v13_n4096_5seed` -- verdict MIDDLE_BAND
- `T3/EXP_saad_solla_v14_n8192_3seed` -- verdict MIDDLE_BAND
- `T3/EXP_saad_solla_v15_n8192_5seed` -- verdict MIDDLE_BAND
- `T3/EXP_saad_solla_v18_n16384` -- verdict PASS
- `T3/EXP_saad_solla_v20_n4096_m_sweep` -- verdict MIDDLE_BAND
- `T3/EXP_saad_solla_v21_n4096_m_sweep_v2` -- verdict MIDDLE_BAND
- `T3/EXP_sparse_block_edit_isolation_v1_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_sparse_w_deletion_sequences_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_sparse_w_edit_heavy_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_sparse_w_gpu_integration_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_sparse_w_large_n_integration_v1` -- verdict PASS
- `T3/EXP_sparse_w_mc_beat_v1_n4096_m32k` -- verdict MIDDLE_BAND
- `T3/EXP_sparse_w_mixed_crud_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_spectral_path_identification_v1_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_state_compression_adversarial_codebook_v1_n4096` -- verdict PASS
- `T3/EXP_substrate_operation_cost_modeling_v1_n4096` -- verdict PASS
- `T3/EXP_substrate_state_compression_v1_n4096` -- verdict PASS
- `T3/EXP_substrate_state_compression_v2_n4096` -- verdict PASS
- `T3/EXP_substrate_state_compression_v3_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_substrate_state_compression_v4_n16384` -- verdict MIDDLE_BAND
- `T3/EXP_sustained_agentic_load_v1_n4096` -- verdict PASS
- `T3/EXP_t1_beta_sweep_v2_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_t1_beta_v3_n4096_mfrac_sweep` -- verdict MIDDLE_BAND
- `T3/EXP_t2_codebook_boundary_v2_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_t2_codebook_v3_n4096_op_sweep` -- verdict HARD_FAIL
- `T3/EXP_t3_susceptibility_v2_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_tcft_alpha_sweep_v1_n8192` -- verdict MIDDLE_BAND
- `T3/EXP_tcft_direct_empirical_sweep_v1_n16384` -- verdict PASS
- `T3/EXP_tcft_erase_robustness_n2048_v1` -- verdict PASS
- `T3/EXP_tcft_erase_robustness_n8192_v1` -- verdict PASS
- `T3/EXP_tcft_m_sweep_v1` -- verdict PASS
- `T3/EXP_tcft_m_sweep_v2` -- verdict PASS
- `T3/EXP_tcft_m_sweep_v3_n8192_5seed` -- verdict MIDDLE_BAND
- `T3/EXP_tcft_m_sweep_v4_n4096` -- verdict MIDDLE_BAND
- `T3/EXP_tcft_n8192_v6` -- verdict MIDDLE_BAND
- `T3/EXP_tcft_n8192_v7` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_1rsb_cluster_cond_pq_v1` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_1rsb_hysteresis_v5_n4096_gpu` -- verdict PASS
- `T3/EXP_wave14_1rsb_hysteresis_v6_n4096` -- verdict PASS
- `T3/EXP_wave14_1rsb_pq_retained_v2` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_1rsb_pq_retained_v3` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_1rsb_rate_dep_hysteresis_v1` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_betB_5corpus_fullscale_v1` -- verdict PASS
- `T3/EXP_wave14_betB_5corpus_noreplay_fix_v1` -- verdict HARD_FAIL
- `T3/EXP_wave14_betB_nscaling_v1` -- verdict HARD_FAIL
- `T3/EXP_wave14_betB_nscaling_v2` -- verdict HARD_FAIL
- `T3/EXP_wave14_betB_rd_perturbation_recovery_v3` -- verdict HARD_FAIL
- `T3/EXP_wave14_betB_replay_hA_direct_v1` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_betB_replay_hA_direct_v2` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_beti_depth_polylog_v2` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_beti_depth_polylog_v4` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_corpus_size_scaling_v2` -- verdict HARD_FAIL
- `T3/EXP_wave14_moe_gating_sharpness_v1` -- verdict HARD_FAIL
- `T3/EXP_wave14_moe_remoe_relu_router_v1` -- verdict HARD_FAIL
- `T3/EXP_wave14_moe_shift_K_scaling_v1` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_moe_shift_K_scaling_v2` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_moe_shift_K_scaling_v3` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_moe_shift_M_scaling_v1` -- verdict HARD_FAIL
- `T3/EXP_wave14_moe_top_edge_v4` -- verdict HARD_FAIL
- `T3/EXP_wave14_ortho_jarzynski_crooks_v1` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_ortho_jarzynski_crooks_v3` -- verdict HARD_FAIL
- `T3/EXP_wave14_ortho_optimal_transport_retention_v1` -- verdict MIDDLE_BAND
- `T3/EXP_wave14_ortho_reservoir_lyapunov_v1` -- verdict HARD_FAIL
- `T3/EXP_wave14_saddle_cascade_plateau_v4_n2048` -- verdict PASS
- `T3/EXP_wave14_saddle_cascade_plateau_v5_n4096` -- verdict PASS
- `T3/EXP_wave14_unified_svd_cascade_falsifier_v1` -- verdict HARD_FAIL
- `T3/EXP_wave14_unified_svd_cascade_falsifier_v2` -- verdict HARD_FAIL
- `T3/EXP_wave14e_bet_n_wta_v5` -- verdict HARD_FAIL
- `T3/EXP_wave14f_hippo_eigenspace_v1` -- verdict HARD_FAIL
- `T3/EXP_wave14f_hippo_replay_w_v1` -- verdict MIDDLE_BAND

</details>

#### provenance_quality `UNVERIFIED` -> `SMOKE_ONLY`  (16 atoms)

<details><summary>relevance_tier <code>LOW</code> (unchanged) -- 9 atoms</summary>

- `T3/EXP_anchor_novel_class_declaration_probe_v1` -- verdict None
- `T3/EXP_anchor_novel_phase_battery_v2_lit_threads` -- verdict None
- `T3/EXP_bid_n_stability_v3_n16384` -- verdict None
- `T3/EXP_bid_n_stability_v4_n12288` -- verdict None
- `T3/EXP_kf4_drift_detect_v3_n4096` -- verdict None
- `T3/EXP_kf5_phase_v1_n4096` -- verdict None
- `T3/EXP_mct_k_extended_v1` -- verdict None
- `T3/EXP_wave14_betB_replay_hA_direct_v3` -- verdict None
- `T3/EXP_wave14_spin_ice_frustration_comparison_v1` -- verdict None

</details>

<details><summary>relevance_tier <code>ARCHIVE</code> (unchanged) -- 7 atoms</summary>

- `T3/EXP_gpu_baseline_expansion_v1_n8192` -- verdict None
- `T3/EXP_kf3_cross_codebook_v1_n4096` -- verdict None
- `T3/EXP_wave14_1rsb_hysteresis_v4_multi_N` -- verdict None
- `T3/EXP_wave14_1rsb_rate_dep_hysteresis_v2` -- verdict None
- `T3/EXP_wave14_moe_intraexpert_overlap_v1` -- verdict None
- `T3/EXP_wave14_moe_top_edge_v2` -- verdict None
- `T3/EXP_wave14_moe_top_edge_v3` -- verdict None

</details>

## 4. One additional description-only correction (not a run_mode atom)

`T3/EXP_pubmedqa_3baseline_v3` has `run_mode: full` and is NOT among the 273. Its defect is
different: `experiments/exp_pubmedqa_3baseline_v3.py`'s docstring literally opens
`"exp_pubmedqa_3baseline_v2 -- ..."`, and `extract_hypothesis()` builds the atom description from
that docstring, so the atom describes the WRONG MECHANISM for its own pass.

Verified by diffing the two cells rather than trusting the docstring: v2 does `whiten + K-hop
select 2` (`h1 = argmax`, then bundle-and-re-query for `h2`); **v3 deletes the K-hop entirely** and
takes `argsort(ew @ qw)[::-1][:SUB_K]` with `SUB_K = 6`. So the inherited phrase
`substrate (whiten+K-hop select 2)` is doubly wrong for v3. Corrected in the docstring and in the
atom's `description` + `metadata.hypothesis`. **The result (HARD_PASS) is untouched.**

## 5. Double-counting flags -- flagged, nothing removed

- `exp_single_shot_attention_multihop_v1` vs `exp_hotpot_3baseline_v1`: `diff` confirms they differ
  in exactly two lines (docstring line 2, `ANCHOR_NAME`). Stronger evidence than the source diff:
  their stored headlines are **character-identical**, same numbers
  (`bare=0.222 vanilla-RAG=0.52...`, `substrate matches vanilla-RAG by -0.023`). Wherever both are
  tallied as independent evidence, that is ONE run counted twice. Both are `run_mode: full`,
  `relevance_tier: LOW`, so neither is in the 273.
- `exp_kf2_isolation_proof_v1` (smoke, `config.N = 1024`) and `exp_kf2_isolation_proof_v2_n8192`
  (smoke, `config.N = 1024`, headline claims `N=8192 ... at production scale`) report the
  **identical** `max_iso = 0.03030`. That is the same measurement under two names and two claimed
  scales. Flagged; the honest corroboration remains the non-smoke `_n4096_audit` sibling.

## 5a. POST-BACKFILL: a second defect became visible, and it is the more serious one

Re-running the scan after the write flags **61 atoms**, not 0. This is not a regression. All 61 are
a strict SUBSET of the 273 just corrected, and all 61 now read `provenance_quality: SMOKE_ONLY`.
They surface via the scan's SECONDARY signal (B), which was previously MASKED because `classify()`
returns on signal A first. Signal B does not test `run_mode` at all, so silencing A revealed it.

**What signal B says: for 61 atoms, the scale in the filename disagrees with the scale in the
atom's own headline text.** Breakdown by filename-declared N: `n4096` 35, `n8192` 16, `n16384` 6,
`n2048` 2, `n1024` 1, `n512` 1. This is exactly the `kf2_isolation_proof_v2_n8192` pattern -- a cell
NAMED for a production scale that reports a headline computed at a smaller one.

That is arguably worse than the label defect just fixed, because the wrong number is in the
*quotable claim*, not the metadata. **It is NOT fixed by this backfill and must not be assumed
fixed.** Correcting it means either renaming atoms or amending headline claims, both of which reach
past labelling into the cells' self-reported results -- a separate, larger, deliberate call. Note
also that signal B was never independently validated against a known positive the way signal A was;
before acting on these 61, that self-test should be built first.

## 6. Store-integrity findings surfaced in passing (NOT fixed here)

- **20 atoms are unloadable** and are silently dropped by `schema.load_atoms()` (see 1b). They
  survive this backfill because it never round-trips them. They remain a latent landmine for ANY
  tool that writes via the Store. Separate cert-integrity task.
- **367 experiment_record atoms in `math` have non-dict `metadata`**, which crashes naive
  `metadata.get(...)` consumers.
- `Store.add_atom` rewrites the WHOLE partition on EVERY call with no lock anywhere in
  `backend/substrate_index/store.py` or `schema.py`. A 273-atom edit through that API is 273
  full-file rewrites of a 43.8 MB file; this rewriter is ONE `os.replace`.

## 7. Safety determination

Measured rather than assumed, in both directions:

- `data/substrate_index/math/atoms.jsonl` mtime **2026-08-03** -- no write in 12 days.
  `concept/atoms.jsonl` 2026-06-19, and it has 0 affected atoms anyway.
- Exactly three live python processes; command lines read via `wmic`:
  `exp_capacity_binds_c3_v1.py` (x2) and `tools/director_kb_continuous_ingest.py --once`.
  **None references `substrate_index` / `PartitionedStore` / `add_atom` / `save_atoms`** -- grep
  run WITH a known-positive control (`import` -> 15 hits) so a silent empty result could not be
  mistaken for a clean one. The KB ingest writes `data/substrate_director_kb_*`, a different tree.
- `git status --porcelain -- data/substrate_index/` is **empty**: the store is clean at HEAD, so
  rollback is exactly `git checkout -- data/substrate_index/math/atoms.jsonl`.
- The write is a single `os.replace` guarded by an immediately-prior `(st_mtime_ns, st_size)`
  re-check; if a peer touched the file between read and write, it ABORTS rather than clobbering.
- Serialization fidelity self-tested: `json.dumps(json.loads(line), ensure_ascii=False)` reproduces
  **all 29631 lines byte-identically**, so the on-disk diff contains only intended edits.
- `content_hash` recomputation self-tested against the 13 atoms that carry one: **13/13 reproduce
  the stored hash** from the pre-edit description, proving the argument list is right before it is
  used to write a new one. The other 260 keep `content_hash: None` (legacy) untouched.
- A5 POST gate: line count identical, id sequence identical, differing lines == intended edit count,
  `load_atoms` skip count still 20 (the malformed rows SURVIVED), `PartitionedStore` loads.

