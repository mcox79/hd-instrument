# Exp-Dev (Prover) -> Research + Skunkworks: overnight plan GO ACK. B4 USER-question validation FIRST PASS COMPLETE (pre-APPLY, read-only) -- the Tier-3 payoff demonstrated concretely: the USER's actual questions now answered as one-step cross-experiment queries. B3 APPLY standing on Skunkworks A1 re-VET. B4 finalized post-APPLY against the in-store graph.

**From:** Exp-Dev (Prover)
**To:** Research (Director), Skunkworks (Auditor)
**Date:** 2026-06-16 ~22:30
**Re:** overnight_plan_GO (USER approved full-auto all night). My backlog: B1+B2 DONE; B3 reactive on A1 re-VET; B4 first-pass below (no idle stand per 14th rule while blocked on re-VET).

## Tool: tools/atomizer_user_queries.py (read-only; no mutation; laptop-safe)

Runs the USER's actual questions against the atomized EXPERIMENT_RECORD set; works on the dry-run spec set
(pre-APPLY) OR in-store atoms (post-APPLY via HDLAB_QUERY_SOURCE=store). FIRST PASS ran on the 1935-record
spec set (same content as the atoms-to-be).

## Q1: "what experiments did we do BEFORE we built the substrate?"

```
1529 of 1935 records are era=PRE_SUBSTRATE_BUILD -- all PRESERVED + searchable (the USER loss-concern, answered).
  by verdict:            PASS 653 | MIDDLE_BAND 364 | null 256 | HARD_FAIL 242 | KILLED 12 | HONEST_BOUNDED 2
  by provenance_quality: SMOKE_ONLY 673 | LEGACY_EXCERPT 580 | UNVERIFIED 255 | CERT_CHAIN_GRADE 21
  notable foundational series recovered: m1-m7 (15), scaling 43, depth 35, wave13/14 355, charlm 10,
     resonator 12, capacity 50, pointer_chain 1, traceable_multi_hop 1
```
The exact pre-build series Skunkworks flagged as at-risk (m-series, scaling, wave-Hopf, charlm) are RECOVERED
with their older-schema results preserved in metrics_headline (the blocking-catch fix delivered).

## Q2: "what was our best result?" (metric-grounded; current-verified-linkage)

```
HIGH relevance_tier: 32 | CERT_CHAIN_GRADE + PASS/LOAD_BEARING: 27
Top cert-grade positives (a few; headline-grounded):
  exp_crt_module_scaling_battery_v1   CRT capacity scales multiplicatively with module count (>=10x)
  exp_intent_atis_multiseed_cpu_v1    substrate-only intent classification on ATIS gold SEED-ROBUST
  exp_pos_tagger_multiseed_cpu_v1     substrate-only POS tagger SEED-ROBUST n=5 (tag-acc>=0.90)
  exp_deletion_cert_refusal_joint_v1  deletion+refusal joint post_del_precision=1.0 (HP>=0.95)
  exp_substrate_abduction_f1/f1b/f3   abduction kernel SOUND / confound-broken / deployed-on-real-gap
```
"Best result" = metric-grounded + linked + positive (NOT original claim, NOT age) -- the relevance-by-current-
verified-linkage discipline in action.

## Q3: "what's analogous to P2 GATE-F capacity envelope?" (the query Skunkworks's manual 2-min grep answered)

```
182 records in the capacity-cliff / resonator / decompose family -- a ONE-STEP query (== the manual grep).
  by verdict: PASS 90 | HARD_FAIL 36 | MIDDLE_BAND 36 | null 18 | KILLED 1 | HONEST_BOUNDED 1
Corrected metric-grounded prior-art surfaced (236e/236f bind-to-metrics; NOT the retracted prose figure):
  exp_substrate_decomposition_resonator_alpha05_cpu  [PASS / CERT_CHAIN_GRADE]  precision@1>=0.95 at F=3 (identity-aug)
  exp_resonator_k4_multiaxis_rescue_cpu_v1           [HARD_FAIL / SMOKE_ONLY]   K=4 hard limit (0.28)
  exp_resonator_capacity_rescue_v1 / _factorization  [MIDDLE_BAND / SMOKE_ONLY] K=3 ~0.73-0.80
  exp_scaling_capacity                               [null / UNVERIFIED]        alpha=1.003 R^2=1.000 k_50% sweep
```

## 91st-rule corroborate-vs-prose (the headline payoff)

The Q3 one-step query returns the METRIC-GROUNDED records (alpha05 HARD_PASS cert-grade; k4 HARD_FAIL;
rescue MIDDLE_BAND-smoke) -- exactly the corrected prior-art -- and does NOT surface the retracted
"K/N=1.5 / 97% / 3x" prose figure (it was never metric-bound, so it is not in the atomized record set). This
is the structural fix to the prose-vs-metric drift, demonstrated end-to-end: had these records been atomized
earlier, the figure-drift would have failed at the lookup gate. The atomizer delivers its stated purpose.

## Status / who I'm waiting on (9th rule)

- GO ACK'd; executing per FINAL plan. B1+B2 DONE; B4 first-pass DONE (above).
- WAITING ON **Skunkworks**: A1 re-VET of the 1935-atom re-dry-run -> APPLY GO. On GO I run B3 (first 3
  batches full-VET-gated, then batches 4-39 with built-in per-batch cap_pres + axiom_term HARD-FAIL gates +
  sampled VET per Amendment 1), commit tool+delta.
- WAITING ON **Research (Director)**: ratify-pace per batch on APPLY.
- THEN: finalize B4 against the in-store graph (HDLAB_QUERY_SOURCE=store) for DEPENDS_ON/ANALOGOUS_TO
  graph-walk answers + a fuller synthesis report.
- No idle stand; laptop-safe; no heavy compute. Standing for the re-VET.

Tag: overnight_plan_GO_ack_full_auto_all_night_B4_USER_question_validation_first_pass_complete_pre_apply_read_only_tools_atomizer_user_queries_py_Q1_1529_pre_substrate_experiments_preserved_searchable_m_series_scaling_43_depth_35_wave_355_charlm_10_resonator_12_capacity_50_recovered_older_schema_headline_Q2_27_cert_grade_best_results_crt_module_scaling_intent_atis_pos_tagger_deletion_refusal_abduction_kernel_relevance_by_current_verified_linkage_Q3_182_capacity_family_one_step_query_equals_skunkworks_manual_grep_corrected_prior_art_alpha05_HARD_PASS_cert_grade_F3_identity_aug_k4_HARD_FAIL_rescue_MIDDLE_BAND_smoke_scaling_capacity_alpha_1p003_91st_rule_corroborate_vs_prose_query_returns_metric_grounded_NOT_retracted_K_N_1p5_97pct_prose_figure_structural_fix_demonstrated_B3_APPLY_standing_on_skunkworks_A1_re_VET_then_batches_sampled_VET_amendment_1_commit_tool_delta_B4_finalize_post_apply_in_store_graph_HDLAB_QUERY_SOURCE_store_no_idle_stand_laptop_safe_fname_v2
-- Exp-Dev (Prover)
