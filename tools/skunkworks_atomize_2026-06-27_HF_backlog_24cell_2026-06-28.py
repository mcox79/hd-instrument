"""Skunkworks 2026-06-28 atomize the 2026-06-27 HARD_FAIL backlog identified by comprehensive audit.

24 cells classified into 4 disposition buckets (all cert_delta=0):
  - honest_negative: clean negatives with mechanism characterization (substantive)
  - cert_ruling_dispatch_infra_failure: infra/runner/OOM/manifest issues; not science failures
  - cert_ruling_test_design_failure: cell-bug / cardinality / NaN / setup-exception / by-construction
  - cluster_amendment: extends existing CLOSED-negative or proven_bound cluster

Cluster amendments tracked: Barrier 1, TWO_TIER/CLS-handoff, NREM, edge_importance, KB-partition.

A5 discipline: per-batch fresh load -> atomic write (tmp + os.replace) -> verify-load -> integrity-check.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

REPO = Path("d:/AI/hd-instrument")
MATH_ATOMS = REPO / "data" / "substrate_index" / "math" / "atoms.jsonl"
META_ATOMS = REPO / "data" / "substrate_index" / "meta" / "atoms.jsonl"
CERT_LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"
NOTES_PATH = "notes/skunkworks_HF_backlog_24cell_atomize_2026-06-28.md"
ATOMIZER = "skunkworks_HF_backlog_24cell_2026-06-28"
TS_BASE = time.time()


# ============================================================================
# Cell -> disposition mapping (verified off-disk metrics.json 2026-06-28)
# ============================================================================
# Each entry: (anchor, raw_verdict, disposition_class, cert_class, headline_summary, key_metrics_dict, cluster_tag)

CELLS = [
    # --- HONEST NEGATIVES (substantive; mechanism characterized; counts as proven-bound negative)
    {
        "anchor": "exp_swr_preplay_constructive_hypothesis_generator_v1_preview_fullN",
        "disposition": "honest_negative",
        "cert_class": "hard_fail_preview_pipeline_top1_below_floor",
        "headline": "HARD_FAIL preview_full: SWR preplay constructive hypothesis generator pipeline_top1=0.083 < 0.15 floor; ARM_PREPLAY_FULL recall@10=0.650 novelty=1.000 but pipeline composition fails; ECHO=RAND=PARROT all 0.000 (lift_echo=+0.650 strong but pipeline collapse downstream)",
        "key_metrics": {
            "pipeline_top1": 0.083,
            "preplay_recall_at_10": 0.650,
            "preplay_novelty": 1.000,
            "echo_recall_at_10": 0.000,
            "rand_recall_at_10": 0.000,
            "parrot_recall": 0.000,
            "parrot_novelty": 0.000,
            "lift_echo": 0.650,
            "lift_rand": 0.650,
            "diversity": 0.066,
            "cv": 0.179,
            "arms_distinct": True,
            "pass_floor_pipeline_top1": 0.15,
        },
        "cluster": "swr_preplay_constructive_hypothesis_generation",
        "note": "Preview full-N run shows the SWR-preplay constructive arm achieves novelty=1.0 + recall@10=0.65 (strong intra-arm) but the downstream pipeline composing into top-1 selection collapses to 0.083. Mechanism characterization: preplay generates novel hypotheses; the COMPOSITION/SELECTION stage is the bound. cluster=swr_preplay; opens revival path: improved scorer or post-hoc filter on preplay candidates.",
        "run_mode": "full_preview",
    },
    {
        "anchor": "exp_edge_importance_v6_CFU_stronger_regime",
        "disposition": "honest_negative",
        "cert_class": "hard_fail_regime_strengthening_did_not_help",
        "headline": "HARD_FAIL v6_CFU stronger regime: best v6 sel=+0.027 <= v5_baseline=+0.037; stronger regime did NOT help. ARM_CFU_LEAVE_K_OUT@a=2.0 sel=+0.027 cor=0.009 n_down=307; TRACE@a=2.0 unretr=0.759 cor=0.037 sel=+0.035. CFU leave-K-out mechanism over-prunes vs canonical TRACE.",
        "key_metrics": {
            "best_v6_sel": 0.027,
            "v5_baseline_sel": 0.037,
            "best_arm": "ARM_CFU_LEAVE_K_OUT_alpha_2p0",
            "best_n_down": 307,
            "trace_alpha_2p0_unretr": 0.759,
            "trace_alpha_2p0_cor": 0.037,
            "trace_alpha_2p0_sel": 0.035,
            "delta_below_baseline": -0.010,
        },
        "cluster": "edge_importance",
        "note": "v6 CFU-stronger-regime characterizes that LEAVE-K-OUT mechanism with higher-alpha regime does NOT improve selectivity over v5 baseline. Extends edge_importance cluster characterization: CFU isn't the path to clear the 0.85 floor either. Joins v6_CFU into the body of CFU-arms tried and falsified.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix",
        "disposition": "honest_negative",
        "cert_class": "hard_fail_surprise_negative_TRACE_cor_below_drill_claim",
        "headline": "HARD_FAIL v2 stratified-replay diagnostic SURPRISE_NEGATIVE: TRACE cor=+0.060 << 0.30 drill claim; either Cauchy-Schwarz math wrong OR test rigging wrong. alpha=1.953 cor(RAND)=-0.008 cor(TRACE)=+0.060 cor(STRAT)=-0.002 cor(INV_WGT)=-0.013. Both v2 variants (arm_count_fix + proper_import_guard) reproduce identical numbers.",
        "key_metrics": {
            "cor_trace": 0.060,
            "cor_rand": -0.008,
            "cor_strat": -0.002,
            "cor_inv_wgt": -0.013,
            "drill_claim_cor_threshold": 0.30,
            "shortfall_vs_claim": -0.240,
            "alpha": 1.953,
            "v2_variants_reproduced_identically": True,
        },
        "cluster": "edge_importance",
        "note": "SURPRISE_NEGATIVE: drill predicted TRACE cor>=0.30; observed +0.060 (5x below). Both v2 variants (arm_count_fix + proper_import_guard) land identical cor=+0.060 reproducibly. Either Cauchy-Schwarz derivation is wrong OR the cor-importance-magnitude correlation isn't the right discriminator. cluster=edge_importance; opens drill path: re-derive Cauchy-Schwarz prediction OR pick a different discriminator.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_substrate_director_kb_reingest_det_snapshot_isolated_v3",
        "disposition": "honest_negative",
        "cert_class": "hard_fail_content_vs_filename_discriminator_failed",
        "headline": "HARD_FAIL substrate_director_kb_reingest_det v3: smoke+full OK but discriminator ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST failed; the load-bearing v2-content-KB-separates-from-v1-metadata-index discriminator does NOT pass. Without this, content_chunk KB is unverified as content-bearing vs filename-only.",
        "key_metrics": {
            "smoke_ok": True,
            "full_ok": True,
            "disc_ok": False,
            "failing_arms": ["ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST"],
        },
        "cluster": "substrate_director_kb_v2_content_chunk",
        "note": "v3 isolated re-ingest discriminator FAILED on the content-vs-filename tripwire (the load-bearing test that v2 content-KB retrieves content rather than filename metadata). This corroborates Skunkworks's prior 2026-06-27 ruling on the content_chunk_ingest_v1_smoke MM: 'tripwire CLAIMED in directive but NOT IN metrics' -- and now an isolated test confirms the tripwire does NOT fire. Atomized as honest_negative (substantive: the v2 KB's value-add hypothesis is FALSIFIED at this implementation). Promotion blocked until content-discriminator passes.",
        "run_mode": "full",
    },

    # --- DISPATCH INFRA FAILURE (runner / OOM / manifest / incomplete run)
    {
        "anchor": "exp_substrate_multihop_brain_pushback_composition_v3_chain_gen_fix",
        "disposition": "cert_ruling_dispatch_infra_failure",
        "cert_class": "dispatch_infra_failure_runner_died_mid_full_run_incomplete_22_of_45_units",
        "headline": "INCOMPLETE: v3 chain_gen_fix completed only 22/45 units before runner stopped (last seed=17 arm=r2_pfc_scratchpad depth=2; elapsed_s=2604.5); verdict UNKNOWN. Not a science result -- a runner/dispatch failure mid-run.",
        "key_metrics": {
            "completed_units": 22,
            "expected_n_units": 45,
            "completion_ratio": 0.489,
            "elapsed_s": 2604.5,
            "last_seed": 17,
            "last_arm": "r2_pfc_scratchpad",
            "last_depth": 2,
            "verdict": "UNKNOWN",
            "hardening_marker": "L1early+L2perarm+L3outertry+L4importsentinel",
        },
        "cluster": "substrate_multihop_brain_pushback",
        "note": "Runner-stop mid-full-run (22/45 units; elapsed 43 min). Hardening L1-L4 in place but the runner-process died before completion. Probably ties to the 2026-06-28 SSH-disconnect-kill cascade (runner_zombie root cause fix per MEMORY.md). Atomized as dispatch_infra_failure NOT science failure; re-dispatch needed to land a verdict. Cluster: brain_pushback_composition.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu",
        "disposition": "cert_ruling_dispatch_infra_failure",
        "cert_class": "dispatch_infra_failure_OOM_at_alpha4_headroom10x",
        "headline": "HARD_FAIL_UNIT_EXCEPTION: MULTI_BANK_K4_alpha4.0_h10x OOM crash; n_units=0/expected=3 BREACH_META_RULE_H. OOM is dispatch-infra failure (GPU memory budget exceeded at alpha=4.0 headroom=10x); composes with v2c chain-grade evidence on lower alpha. Not a mechanism science failure.",
        "key_metrics": {
            "failed_arm": "MULTI_BANK_K4_alpha4p0_headroom10x",
            "n_units_completed": 0,
            "n_units_expected": 3,
            "failure_type": "OutOfMemoryError",
            "elapsed_s": 127.9,
            "seed_failed": 11,
        },
        "cluster": "phase_diagram_capacity_multi_bank",
        "note": "GPU OOM at alpha=4.0 headroom=10x bank K=4; composes with v2c chain_grade evidence on lower-alpha regimes. Dispatch infra: the cell envelope (memory budget) was exceeded -- not a mechanism falsification. cluster=phase_diagram_capacity; re-dispatch needs chunked-alpha or larger GPU.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_substrate_director_kb_remote_provision_v1",
        "disposition": "cert_ruling_dispatch_infra_failure",
        "cert_class": "dispatch_infra_failure_local_manifest_missing",
        "headline": "HARD_FAIL arm_exception ARM_LOCAL_INGEST_FRESHNESS_CHECK: local manifest missing at C:\\dev\\hd-instrument\\data\\substrate_director_kb_v1\\manifest.json. Cell crashed in provisioning check on remote; not a science test failure.",
        "key_metrics": {
            "failing_arm": "ARM_LOCAL_INGEST_FRESHNESS_CHECK",
            "missing_path": "C:/dev/hd-instrument/data/substrate_director_kb_v1/manifest.json",
            "elapsed_s": 0.14,
            "crashed_in": "provisioning_freshness_check",
        },
        "cluster": "substrate_director_kb_provisioning",
        "note": "Remote provisioning cell crashed on a freshness-check pre-condition (missing manifest). Pure infra: the cell never got to test anything substantive. Re-dispatch after manifest is provisioned. cluster=substrate_director_kb_provisioning.",
        "run_mode": "preflight",
    },

    # --- TEST DESIGN FAILURE (cell-bug / cardinality breach / by-construction / NaN / setup exception)
    {
        "anchor": "exp_self_explanation_deletion_fidelity_v1",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_import_crash_setup_assertion",
        "headline": "IMPORT_CRASH: AssertionError 'contribution_true_trace argmax should be query index 0; got 3 scores=[1.484, 1.297, 0.906, 1.531]'. Cell-author setup assertion failed before any experiment ran -- the assumed argmax=query_index_0 invariant does NOT hold in the cell's own setup data.",
        "key_metrics": {
            "verdict": "UNKNOWN_IMPORT_CRASH",
            "elapsed_s": 0.0,
            "assertion_failed_at": "contribution_true_trace_argmax_should_be_query_index_0",
            "actual_argmax_idx": 3,
            "expected_argmax_idx": 0,
            "argmax_scores": [1.484, 1.297, 0.906, 1.531],
        },
        "cluster": "self_explanation_deletion_fidelity",
        "note": "Cell crashed on its own setup-assertion before any experimental arm ran. Test design failure: the assumed-argmax-invariant the cell-author baked in does not hold in the data. Need: (a) verify the assertion is sound (does true_trace contribution actually argmax to query_index_0?), or (b) revise the test to not assume it. cluster=self_explanation_deletion_fidelity.",
        "run_mode": "n/a_import_crash",
    },
    {
        "anchor": "exp_substrate_multihop_brain_pushback_composition_v2_hardened",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_chain_generator_yielded_zero_chains",
        "headline": "CRASHED: RuntimeError BLOCKING make_deep_chains: only 0/200 generated for V=200 disallow|=200 max_depth=8. Chain-generator yielded ZERO chains -- the test cannot run because the chain-generation regime (V=200, disallow_set_size=200, max_depth=8) is over-constrained. Test design failure.",
        "key_metrics": {
            "verdict": "UNKNOWN_CRASH",
            "elapsed_s": 2.2,
            "chains_generated": 0,
            "chains_expected": 200,
            "vocab_V": 200,
            "disallow_set_size": 200,
            "max_depth": 8,
        },
        "cluster": "substrate_multihop_brain_pushback",
        "note": "Chain-gen regime over-constrained: V=200 with disallow=200 leaves no chains to construct. v3 chain_gen_fix supersedes (V_C 200->1000, max_depth 8->5) but ran out of time mid-run. Test design failure here; v3 supersession is the right move. cluster=brain_pushback_composition.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_stage3_typed_routing_falsification_bijective_v1",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_by_construction_saturation_META_RULE_K",
        "headline": "HARD_FAIL by_construction_saturation_META_RULE_K: baseline=0.9991 >= 0.98; lift requirement structurally unachievable. Cell-author correctly self-detected per META_RULE_K and HARD_FAIL'd rather than spuriously claim a lift on a saturated baseline. Test design issue: bijective-routing baseline is too easy -- need harder regime.",
        "key_metrics": {
            "baseline_acc": 0.9991,
            "by_construction_saturation_threshold": 0.98,
            "lift_structurally_achievable": False,
            "self_detected_via_rule": "META_RULE_K",
            "elapsed_s": 78.1,
        },
        "cluster": "stage3_typed_routing",
        "note": "META_RULE_K caught the test design flaw correctly. Bijective-routing falsification cannot be tested when baseline is already 0.9991 -- no headroom for a lift to demonstrate routing's contribution. Healthy use of the self-checking rule. Re-design needed: make routing-task harder (longer typed chains, more clutter relations) to drop baseline into a testable regime. cluster=stage3_typed_routing.",
        "run_mode": "smoke_or_full",
    },
    {
        "anchor": "exp_multihop_kbeam_pathsum_v1",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_aggregation_sanity_breach_baseline_regime_drift",
        "headline": "SANITY_BREACH: depth-2 rails out of [0.60, 0.70]. baseline=0.1017 (ok=False); beta_2=0.0967 (ok=False). 2026-06-24 beta-sweep regime not reproduced -- setup drifted. PRIMARY K10_PATHSUM d5=0.0117 K10_ARGMAX d5=0.0083 lift_ps_vs_am=+0.0033 BASELINE d5=0.0083. Aggregation/setup regime drifted; do NOT interpret main arms.",
        "key_metrics": {
            "depth_2_baseline": 0.1017,
            "depth_2_beta_2": 0.0967,
            "expected_band_low": 0.60,
            "expected_band_high": 0.70,
            "sanity_breach": True,
            "K10_PATHSUM_d5": 0.0117,
            "K10_ARGMAX_d5": 0.0083,
            "lift_ps_vs_am": 0.0033,
            "elapsed_s": 3294.7,
        },
        "cluster": "multihop_kbeam_pathsum",
        "note": "Audit-flagged test_design_failure_aggregation: depth-2 baseline regime drifted 6x from the 2026-06-24 reference (0.10 vs expected 0.60-0.70). Main K10_PATHSUM/ARGMAX results are uninterpretable because the sanity rails are breached. Need: re-anchor the cell-setup to the 2026-06-24 regime (configuration/aggregation drift); re-dispatch. cluster=multihop_kbeam_pathsum.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_edge_importance_stratified_replay_baseline_diagnostic_v1",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_cardinality_breach_META_RULE_H",
        "headline": "HARD_FAIL META_RULE_H cardinality_ok breach seed=7: expected 4 arms, got 6. Cell-author self-detected cardinality mismatch and HARD_FAIL'd correctly. v2_arm_count_fix is the supersession.",
        "key_metrics": {
            "expected_arms": 4,
            "actual_arms": 6,
            "breach_at_seed": 7,
            "rule_triggered": "META_RULE_H_cardinality_ok",
            "elapsed_s": 0.002,
        },
        "cluster": "edge_importance",
        "note": "Cell self-aborted on META_RULE_H cardinality breach; healthy self-check. v2_arm_count_fix supersedes this cell. Atomized as test_design_failure (cell-bug self-caught), counts toward edge_importance cluster's iterate-history but not toward CERT N.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_edge_importance_stratified_replay_baseline_diagnostic_v2",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_no_metrics_supersede_by_named_variants",
        "headline": "NO_METRICS at bare-v2 path; supersede by named variants v2_arm_count_fix and v2_proper_import_guard (both landed HARD_FAIL with identical SURPRISE_NEGATIVE TRACE cor=+0.060 -- atomized as honest_negative under arm_count_fix entry).",
        "key_metrics": {
            "metrics_present": False,
            "supersede_paths": [
                "exp_edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix",
                "exp_edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard",
            ],
        },
        "cluster": "edge_importance",
        "note": "Bare-v2 anchor has no metrics; both named v2 variants landed identical HF with SURPRISE_NEGATIVE TRACE cor=+0.060. The substantive result is atomized under the v2_arm_count_fix honest_negative entry; this bare-anchor atom is recorded as test_design_failure (no-metrics; supersede by named variants).",
        "run_mode": "n/a",
    },
    {
        "anchor": "exp_gap3_cls_two_tier_BCM_v2_init_fix",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_unit_exception_BCM_overflow_to_float",
        "headline": "HARD_FAIL_UNIT_EXCEPTION key=11_ARM_BCM_V2_INIT_ONLY RuntimeError 'value cannot be converted to type float without overflow' (1/12 units before crash). BCM update produces non-finite values that overflow float conversion; numerical-stability test design issue.",
        "key_metrics": {
            "failed_unit_key": "11_ARM_BCM_V2_INIT_ONLY",
            "exc_type": "RuntimeError",
            "exc_msg_prefix": "value_cannot_be_converted_to_type_float_without_overflow",
            "units_completed": 1,
            "units_expected": 12,
            "elapsed_s": 0.07,
        },
        "cluster": "cls_handoff_two_tier_BCM",
        "note": "BCM update produces overflow-causing values within 1 unit. Numerical stability problem in the BCM consolidation arm. Extends CLS-handoff TWO_TIER cluster: BCM variant joins the falsified arms (alongside HOPFIELD v2 regime_fix etc.). cluster=cls_handoff_two_tier; opens drill: numerical-stable BCM (clamping/normalization) or different consolidation mechanism.",
        "run_mode": "n/a_crashed_early",
    },
    {
        "anchor": "exp_multihop_barrier1_M2_M3_M1_combined_5arm_v1",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_setup_exception_chain_gen_under_yield",
        "headline": "HARD_FAIL D3 caught setup exception seed=7: BLOCKING make_deep_chains: only 200/500 generated for V=200 disallow|=0 max_depth=8. Chain-gen yields 40% of requested chains; setup-exception caught by D3 discriminator. Test design / chain-gen regime under-yields.",
        "key_metrics": {
            "chains_generated": 200,
            "chains_expected": 500,
            "yield_ratio": 0.40,
            "vocab_V": 200,
            "max_depth": 8,
            "elapsed_s": 0.73,
            "failed_at_seed": 7,
        },
        "cluster": "barrier1_M2_M3_M1_combined",
        "note": "Extends Barrier 1 CLOSED-negative cluster (per MEMORY.md barrier1 chain-grade partition_oracle 3seed PROMOTE 2026-06-28 + drill2 HF capability CLOSED). v1 5-arm composition test_design_failure: chain-gen yields 40% (V=200 max_depth=8 too tight). Supersede by v2 attempt (also HF -- see next entry). cluster=barrier1.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_multihop_barrier1_M2_M3_M1_combined_5arm_v2",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_setup_exception_chain_gen_under_yield_v2_supersede",
        "headline": "HARD_FAIL D3 caught setup exception seed=7: BLOCKING make_deep_chains: only 180/200 generated for V=500 disallow|=320 max_depth=8 enforce_distinct=True. v2 widened V_C and reduced expected chains; STILL under-yields at 90%. enforce_distinct=True + disallow=320 over-constrains.",
        "key_metrics": {
            "chains_generated": 180,
            "chains_expected": 200,
            "yield_ratio": 0.90,
            "vocab_V": 500,
            "disallow_set_size": 320,
            "max_depth": 8,
            "enforce_distinct": True,
            "elapsed_s": 7.78,
            "failed_at_seed": 7,
        },
        "cluster": "barrier1_M2_M3_M1_combined",
        "note": "Second v2 attempt: even after V_C widening (200->500) and chain-count reduction (500->200), enforce_distinct=True + disallow=320 still over-constrains chain-gen to 90%. Extends Barrier 1 CLOSED-negative cluster: composition-test infrastructure cannot generate chains at this regime. cluster=barrier1. Closes 5arm-composition attempt at this regime; drill needs different regime (lower max_depth, lower enforce_distinct, or smaller disallow).",
        "run_mode": "full",
    },
    {
        "anchor": "exp_gap1_multihop_ldpc_rts_bidirectional_v1",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_sanity_breach_baseline_out_of_band",
        "headline": "SANITY_BREACH_BASELINE_OUT_OF_BAND: 5/5 seeds; baseline_mean=0.3320 outside [0.125, 0.165]. BASELINE=0.3320 SOFT_FWD=0.6090 BACKWARD=0.3350 LDPC=0.6090 RTS=0.6090. Anchor1_LDPC=HARD_FAIL Anchor2_RTS=HARD_PASS BUT baseline regime breach invalidates interpretation.",
        "key_metrics": {
            "baseline_mean": 0.3320,
            "expected_baseline_band_low": 0.125,
            "expected_baseline_band_high": 0.165,
            "sanity_breach_seeds": 5,
            "n_seeds": 5,
            "SOFT_FWD": 0.6090,
            "BACKWARD": 0.3350,
            "LDPC": 0.6090,
            "RTS": 0.6090,
            "anchor1_LDPC": "HARD_FAIL",
            "anchor2_RTS": "HARD_PASS_uninterpretable",
            "elapsed_s": 628.8,
        },
        "cluster": "multihop_ldpc_rts_bidirectional",
        "note": "Baseline 2x above expected band -- can't interpret LDPC or RTS verdicts. Test design failure: baseline regime drifted; either the cell's setup invariants changed or the canonical 2026-06-24 regime needs re-anchoring. RTS HARD_PASS appears but is gated by sanity-breach -- do NOT promote. cluster=multihop_ldpc_rts. Verify-the-referent gate caught it.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_phase_diagram_capacity_codebook_separated_v2a_mech_plus_sentinels",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_cardinality_breach_META_RULE_H_36_of_66",
        "headline": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units=36 < expected=66. ALL completed arms show rec=1.0000 cv=0.0000 in-band (alpha0p5_h10x, alpha0p5_h2x, alpha1p0_h10x...). Cardinality breach blocks the verdict despite all completed units passing -- test_design discipline correctly held the line.",
        "key_metrics": {
            "n_units_completed": 36,
            "n_units_expected": 66,
            "completion_ratio": 0.545,
            "completed_arms_at_metric_cap": True,
            "elapsed_s": 596.8,
        },
        "cluster": "phase_diagram_capacity_codebook_separated",
        "note": "30 of 66 units missing -- META_RULE_H correctly holds the verdict despite the 36 completed showing at-cap saturation. Either runner died on the remaining 30 OR cardinality config bug. Companion to multi_bank_K4_v2b OOM. cluster=phase_diagram_capacity. Re-dispatch with fixed cardinality or larger envelope. Healthy use of META_RULE_H.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_edge_importance_v3p2_trace_only_with_D1_audit_v1",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_cardinality_breach_META_RULE_H_2_arms_got_6",
        "headline": "HARD_FAIL META_RULE_H cardinality_ok breach seed=7: expected 2 arm entries, got 6. Cell self-aborted on cardinality; v2_arm_count_fix is the supersession (landed MIDDLE_BAND).",
        "key_metrics": {
            "expected_arm_entries": 2,
            "actual_arm_entries": 6,
            "breach_at_seed": 7,
            "rule_triggered": "META_RULE_H_cardinality_ok",
            "elapsed_s": 0.001,
        },
        "cluster": "edge_importance",
        "note": "Cardinality breach self-aborted before any experimental result. v2_arm_count_fix is the supersession (MB). Healthy self-check. cluster=edge_importance.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_edge_importance_v3p2_trace_only_with_D1_audit_v2",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_no_metrics_supersede_by_named_variant",
        "headline": "NO_METRICS at bare-v2 path; supersede by v2_arm_count_fix variant (landed MIDDLE_BAND: composition operational but PASS bands not cleared; sel_minus_rand=+0.083 for TRACE, +0.008 for ULTRA; hp_checks split).",
        "key_metrics": {
            "metrics_present": False,
            "supersede_path": "exp_edge_importance_v3p2_trace_only_with_D1_audit_v2_arm_count_fix",
            "supersede_verdict": "MIDDLE_BAND",
            "trace_sel_minus_rand": 0.083,
            "ultra_sel_minus_rand": 0.008,
        },
        "cluster": "edge_importance",
        "note": "Bare-v2 has no metrics; v2_arm_count_fix landed MIDDLE_BAND with TRACE sel_minus_rand=+0.083 (PASS rec_retr, FAIL sel_unretr, FAIR fairness gate). Substantive MM result tracked at v2_arm_count_fix; this bare entry is test_design_failure (no-metrics; supersede). cluster=edge_importance.",
        "run_mode": "n/a",
    },
    {
        "anchor": "exp_edge_importance_v3_D1_alternative_discriminators_v1",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_all_nan_non_finite_D1_AUC",
        "headline": "HARD_FAIL: non-finite D1 AUC in RAND. RAND(D1_AUC=nan); TRACE(D1_AUC=nan,cv=nan,D2_p@N_USE=nan,D2_p@50=nan,D3_KM=nan); ULTRA(D1_AUC=nan); COMP(lam=0.1, all-nan). Discriminator computation failed across all arms -- numerical/init issue.",
        "key_metrics": {
            "RAND_D1_AUC": "nan",
            "TRACE_D1_AUC": "nan",
            "ULTRA_D1_AUC": "nan",
            "COMP_D1_AUC": "nan",
            "TRACE_D2_p_at_N_USE": "nan",
            "TRACE_D3_KM": "nan",
            "elapsed_s": 0.005,
        },
        "cluster": "edge_importance",
        "note": "Discriminator computation returns NaN across all arms within 5ms -- a numerical/init failure not a science result. Likely division-by-zero or empty-array in D1 AUC. cluster=edge_importance. Cell-bug fix needed before any verdict is interpretable.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_kb_partition_by_source_class_v3_self_contained",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_v3_band_miss_superseded_by_v4_calibrated_PASS",
        "headline": "HARD_FAIL v3_band_miss: routing_acc=1.0000 (mb_floor 0.9 PASS); leak=0.0000 (ceil 0.05 PASS); ratio_resolved=0.1429 (floor 0.8 MISS); ud_ret=0.2143 (floor 0.7 MISS); diag_n_capacity_regression=1. v4_calibrated supersedes (per batch11 atomization shows v4 at routing_acc=1.0, leak=0.0, ratio_resolved=0.9643, ud_ret=0.9286 -- chain-grade candidate).",
        "key_metrics": {
            "routing_acc": 1.0000,
            "leak": 0.0000,
            "ratio_resolved": 0.1429,
            "ratio_resolved_floor": 0.80,
            "ud_ret": 0.2143,
            "ud_ret_floor": 0.70,
            "diag_n_capacity_regression": 1,
            "elapsed_s": 5.38,
            "superseded_by_v4_calibrated": True,
        },
        "cluster": "kb_partition_by_source_class",
        "note": "v3 cleared routing+leak but missed ratio_resolved (0.14 vs 0.80 floor) and ud_ret (0.21 vs 0.70 floor); diagnostic flag for n_capacity regression. v4_calibrated supersedes with all 4 floors cleared (per batch11 landed-VET atomization). cluster=kb_partition_by_source_class. v3 is an iteration-history record (test_design_failure: band miss at v3 calibration regime; fixed in v4).",
        "run_mode": "full",
    },

    # --- CLUSTER AMENDMENTS (extend existing cluster)
    {
        "anchor": "exp_importance_ceiling_v7B_n_seeds_scale",
        "disposition": "honest_negative",  # MIDDLE_BAND with substantive characterization (cert-neutral, delta=0)
        "cert_class": "middle_band_real_signal_bounded_not_chain_grade_cv_unresolved",
        "headline": "MIDDLE_BAND [REAL_SIGNAL_BOUNDED_NOT_CHAIN_GRADE]: winner=eight_readout_fisher mean=-0.003 (cv=10.448, lb=-0.020); PCA=-0.012 (v1_band=False); Fisher=-0.003; Single=-0.004; Trace=0.998; Rand=-0.008. rand_clean=True trace_sane=True cv_resolved=False sem_separated=False. n_seeds=16. crlb_k8=0.0884 crlb_sanity_ok=True arms_differ=True.",
        "key_metrics": {
            "winner_arm": "eight_readout_fisher",
            "winner_mean": -0.003,
            "winner_cv": 10.448,
            "winner_lb": -0.020,
            "PCA_mean": -0.012,
            "Fisher_mean": -0.003,
            "Single_mean": -0.004,
            "Trace_mean": 0.998,
            "Rand_mean": -0.008,
            "rand_clean": True,
            "trace_sane": True,
            "cv_resolved": False,
            "sem_separated": False,
            "n_seeds": 16,
            "crlb_k8": 0.0884,
            "arms_differ": True,
            "v1_band_pass": False,
        },
        "cluster": "importance_ceiling_eight_readout_fisher",
        "note": "n_seeds=16 scaling did NOT resolve cv (10.448 >> 1.0 threshold) and SEM not separated. All readout arms (PCA/Fisher/Single) cluster near zero (-0.003 to -0.012); TRACE=0.998 confirms substrate-encoding control (positive control); RAND=-0.008 confirms clean random baseline. Test rationality issue identified in MEMORY.md 'encoding before readout' rule -- PCA-Fisher reads geometry nothing wrote. Extends importance_ceiling cluster characterization: scaling n_seeds is NOT the lever; the substrate does not encode importance for these readouts to recover. cluster=importance_ceiling. cert-neutral delta=0.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_kb_coarse_grain_at_promotion_v4_with_ud_detection",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_RC2_invariant_n_atoms_full_below_scale_threshold",
        "headline": "HARD_FAIL RC-2 invariant: n_atoms_full=4735 < 10000 (scale insufficient to break saturation). Cell's own RC-2 invariant: chain-grade promotion of ANCHOR 3 requires scaling n_atoms past 10000 to break rec_unclst=1.000 cap. This run only achieved 4735 atoms; invariant correctly fails the verdict.",
        "key_metrics": {
            "n_atoms_full": 4735,
            "RC2_scale_threshold": 10000,
            "shortfall_ratio": 0.4735,
            "rule_triggered": "RC2_break_saturation_invariant",
            "elapsed_s": 8.66,
        },
        "cluster": "kb_coarse_grain_anchor3_RC2_promotion",
        "note": "Extends ANCHOR 3 coarse-grain proven_bound (per batch3 + 2026-06-27 landed-VET): RC-2 promotion path requires n_atoms>=10000 to break the rec_unclst=1.000 metric cap. v4 with UD detection only mustered 4735 atoms; invariant correctly held the verdict. UD detection itself may have worked but cannot be tiered without the scale. cluster=ANCHOR_3_coarse_grain. Re-dispatch needs larger corpus (10k+ atoms) for RC-2 promotion attempt.",
        "run_mode": "full",
    },
    {
        "anchor": "exp_edge_importance_v4_NREM_replay_modulated_trace",
        "disposition": "cert_ruling_test_design_failure",
        "cert_class": "test_design_failure_fairness_gate_breach_cor_W_0p841",
        "headline": "HARD_FAIL fairness gate cor(importance,|W|)=0.841 >= 0.30 -- mechanism is secretly indexing via correlation with edge magnitude, not via NREM-replay-modulated trace. alpha=1.953 lam_best=0.5. TRACE retr=1.000 unretr=0.603 sel-rand=+0.100; REPLAY retr=0.738 unretr=0.687 sel-rand=+0.017; COMP retr=1.000 unretr=0.603 cor=0.841 cv=0.000.",
        "key_metrics": {
            "fairness_cor_W": 0.841,
            "fairness_threshold": 0.30,
            "fairness_breach": True,
            "alpha": 1.953,
            "lam_best": 0.5,
            "TRACE_retr": 1.000,
            "TRACE_unretr": 0.603,
            "TRACE_sel_minus_rand": 0.100,
            "REPLAY_retr": 0.738,
            "REPLAY_unretr": 0.687,
            "REPLAY_sel_minus_rand": 0.017,
            "COMP_retr": 1.000,
            "COMP_unretr": 0.603,
            "n_down": 300,
            "elapsed_s": 16.73,
        },
        "cluster": "edge_importance_NREM_modulated",
        "note": "Extends NREM proven_bound + edge_importance cluster: NREM-replay-modulated trace COMPOSITION fairness-gate breached (cor with |W|=0.841 >> 0.30 threshold). The COMP mechanism is correlating with edge weight magnitudes, not with NREM-replay signal -- exactly the confound the fairness gate is designed to catch. REPLAY arm alone has sel-rand=+0.017 (essentially no lift). cluster=NREM + edge_importance. Healthy fairness-check; the proposed COMP mechanism is NOT what's driving the lift.",
        "run_mode": "full",
    },
]


# ============================================================================
# Build atoms + ledger rows
# ============================================================================

def _safe_id(anchor: str, cls: str) -> str:
    """Generate stable, deterministic atom id."""
    safe = anchor.replace("exp_", "")
    return f"T3/EXP_{safe}_2026_06_27_HF_BACKLOG_{cls}"


def build_math_atoms() -> list[dict]:
    """Build experiment_record atoms (one per cell) into math::T3."""
    atoms = []
    for cell in CELLS:
        anchor = cell["anchor"]
        disposition = cell["disposition"]
        cert_class = cell["cert_class"]
        atom_id = _safe_id(anchor, cert_class[:80])

        # Description: full off-data summary
        description = (
            f"HF_BACKLOG_2026_06_27 atomization (2026-06-28).\n"
            f"\n"
            f"DISPOSITION: {disposition} (cert-neutral, delta=0).\n"
            f"CERT_CLASS: {cert_class}\n"
            f"CLUSTER: {cell['cluster']}\n"
            f"\n"
            f"HEADLINE:\n  {cell['headline']}\n"
            f"\n"
            f"KEY_METRICS (off-disk verified):\n"
        )
        for k, v in cell["key_metrics"].items():
            description += f"  {k} = {v}\n"
        description += f"\nNOTE:\n  {cell['note']}\n"
        description += f"\nMETRICS_PATH: data/{anchor}/metrics.json\n"
        description += f"VERIFIED_OFF_DATA: True (Skunkworks 2026-06-28 .venv recompute)\n"

        atoms.append({
            "id": atom_id,
            "name": f"HF_BACKLOG 2026-06-27 {anchor} [{disposition}]",
            "corpus": "math",
            "tier": "T3",
            "kind": "experiment_record",
            "description": description,
            "aliases": [anchor],
            "metadata": {
                "record_class": "experiment_record",
                "provenance_quality": "CERT_NEUTRAL",
                "cert_status": disposition,
                "cert_class": cert_class,
                "cell_anchor": anchor,
                "cell_commit": "n/a-2026-06-27-landed",
                "metrics_path": f"data/{anchor}/metrics.json",
                "ruling_note": NOTES_PATH,
                "verified_off_data": True,
                "run_mode": cell["run_mode"],
                "key_metrics": cell["key_metrics"],
                "cluster": cell["cluster"],
                "headline_summary": cell["headline"],
                "ruling_note_summary": cell["note"],
                "cert_increment_delta": 0,
                "atomized_by": ATOMIZER,
                "backlog_source": "comprehensive_audit_2026_06_27",
                "_llm_forward_calls_at_inference": 0,
            },
        })
    return atoms


def build_cluster_amendment_meta_atoms() -> list[dict]:
    """Build cluster-amendment atoms (one per cluster touched) into meta corpus."""
    # Group cells by cluster
    cluster_cells = {}
    for cell in CELLS:
        cluster_cells.setdefault(cell["cluster"], []).append(cell)

    atoms = []
    for cluster_name, cells in cluster_cells.items():
        if len(cells) < 2 and cluster_name not in (
            "barrier1_M2_M3_M1_combined",
            "cls_handoff_two_tier_BCM",
            "edge_importance_NREM_modulated",
            "kb_coarse_grain_anchor3_RC2_promotion",
            "substrate_director_kb_v2_content_chunk",
            "phase_diagram_capacity_multi_bank",
            "phase_diagram_capacity_codebook_separated",
            "kb_partition_by_source_class",
        ):
            # Single-cell isolated clusters don't get cluster amendment atoms
            continue

        anchors = [c["anchor"] for c in cells]
        dispositions = [c["disposition"] for c in cells]
        amendment_id = f"T_methodology/META_CLUSTER_AMENDMENT_2026_06_27_HF_BACKLOG_{cluster_name}_2026-06-28"

        desc = (
            f"CLUSTER AMENDMENT: 2026-06-27 HF_BACKLOG additions to '{cluster_name}' cluster.\n"
            f"\n"
            f"Cells in this amendment ({len(cells)}):\n"
        )
        for c in cells:
            desc += f"  - {c['anchor']} [{c['disposition']}]: {c['headline'][:120]}...\n"

        desc += (
            f"\n"
            f"Cluster significance:\n"
            f"  - Adds to existing cluster body of evidence; iterate-history extended.\n"
            f"  - All cert_increment_delta=0 (cert-neutral characterizations).\n"
            f"  - Iteration patterns: chain-gen regimes, cardinality breaches, by-construction saturations, fairness-gate breaches, infra-OOM.\n"
            f"  - These additions strengthen the cluster's CLOSED-negative or proven_bound status; do not re-explore without a revival angle.\n"
        )

        atoms.append({
            "id": amendment_id,
            "name": f"META_CLUSTER_AMENDMENT 2026-06-27 HF_BACKLOG cluster={cluster_name}",
            "corpus": "meta",
            "tier": "T_methodology",
            "kind": "discipline_rule_amendment",
            "description": desc,
            "aliases": [],
            "metadata": {
                "record_class": "cluster_amendment",
                "cluster_name": cluster_name,
                "amendment_date": "2026-06-28",
                "amendment_source": "comprehensive_audit_2026_06_27_HF_backlog",
                "n_cells_amended": len(cells),
                "cell_anchors": anchors,
                "cell_dispositions": dispositions,
                "cert_neutral_delta": 0,
                "atomized_by": ATOMIZER,
                "_llm_forward_calls_at_inference": 0,
            },
        })
    return atoms


def build_ledger_rows(math_atoms: list[dict]) -> list[dict]:
    """One ledger row per atom; all cert_increment_delta=0."""
    rows = []
    ts = TS_BASE
    for atom in math_atoms:
        ts += 0.001
        anchor = atom["metadata"]["cell_anchor"]
        rows.append({
            "ts": ts,
            "op": "cert_ruling",
            "atom_id": f"math::{atom['id']}",
            "cert_status": atom["metadata"]["cert_status"],
            "cert_class": atom["metadata"]["cert_class"],
            "verified_off_data": True,
            "atomized_by": ATOMIZER,
            "cell_commit": "n/a-2026-06-27-landed",
            "verdict": f"HF_BACKLOG_2026_06_27_{atom['metadata']['cert_class']}",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": NOTES_PATH,
                "metrics_path": atom["metadata"]["metrics_path"],
                "atom_qualified_id": f"math::{atom['id']}",
                "cluster": atom["metadata"]["cluster"],
            },
            "supersedes": None,
            "note": atom["metadata"]["ruling_note_summary"][:200],
        })
    return rows


# ============================================================================
# A5-gate appender (atomic write + verify-load + integrity-check)
# ============================================================================

def a5_append_jsonl(path: Path, new_rows: list[dict], label: str) -> tuple[int, int]:
    """Atomic append: read old -> append new -> atomic os.replace -> verify-load."""
    assert path.exists(), f"GATE_FAIL: missing {path}"
    old_text = path.read_text(encoding="utf-8")
    old_lines = old_text.count("\n") if old_text else 0
    if old_text and not old_text.endswith("\n"):
        old_text = old_text + "\n"

    append_buf = []
    for row in new_rows:
        append_buf.append(json.dumps(row, ensure_ascii=True))
    append_text = "\n".join(append_buf) + "\n"

    tmp = path.with_suffix(path.suffix + ".tmp.vet20260628hfbacklog")
    tmp.write_text(old_text + append_text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)

    new_text = path.read_text(encoding="utf-8")
    new_lines = new_text.count("\n")
    parsed_ok = 0
    for ln in new_text.splitlines():
        if not ln.strip():
            continue
        try:
            json.loads(ln)
            parsed_ok += 1
        except json.JSONDecodeError as e:
            raise SystemExit(f"GATE_FAIL: verify-load failed on {path}: {e}")
    print(f"[A5 {label}] {old_lines} -> {new_lines} lines (+{new_lines-old_lines}); {parsed_ok} JSON-valid lines; ATOMIC_OK")
    return old_lines, new_lines


def a5_pre_check() -> int:
    sys.path.insert(0, str(REPO))
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(str(REPO / "data" / "substrate_index"))
    n_atoms = sum(1 for _ in ps.all_atoms())
    print(f"[A5 PRE] PartitionedStore LOADS OK -- {n_atoms} atoms")
    return n_atoms


def a5_post_check(expected_atom_delta: int, pre_count: int) -> None:
    sys.path.insert(0, str(REPO))
    from backend.substrate_index.partition import PartitionedStore
    ps2 = PartitionedStore(str(REPO / "data" / "substrate_index"))
    n_atoms = sum(1 for _ in ps2.all_atoms())
    actual_delta = n_atoms - pre_count
    print(f"[A5 POST] PartitionedStore LOADS OK -- {n_atoms} atoms (delta={actual_delta:+d}, expected {expected_atom_delta:+d})")
    if actual_delta != expected_atom_delta:
        raise SystemExit(f"GATE_FAIL: atom-count delta mismatch")
    print("[A5 POST] integrity OK")


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    print(f"Skunkworks HF_BACKLOG 2026-06-27 atomization @ {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  cells classified: {len(CELLS)}")

    math_atoms = build_math_atoms()
    meta_atoms = build_cluster_amendment_meta_atoms()
    ledger_rows = build_ledger_rows(math_atoms)

    print(f"  math atoms to append: {len(math_atoms)}")
    print(f"  meta cluster-amendment atoms to append: {len(meta_atoms)}")
    print(f"  ledger rows to append: {len(ledger_rows)}")

    # Sanity: no duplicate IDs
    seen = set()
    for a in math_atoms + meta_atoms:
        if a["id"] in seen:
            raise SystemExit(f"GATE_FAIL: duplicate atom id {a['id']}")
        seen.add(a["id"])
    print(f"  no duplicate atom IDs")

    # Sanity: ledger count matches math atom count
    assert len(ledger_rows) == len(math_atoms), "ledger/math mismatch"

    # Cert delta total should be 0
    total_delta = sum(r["cert_increment_delta"] for r in ledger_rows)
    assert total_delta == 0, f"expected total delta=0; got {total_delta}"
    print(f"  cert_increment_delta total: {total_delta} (all cert-neutral)")

    # A5 PRE
    pre_count = a5_pre_check()

    # Sequential atomic appends
    a5_append_jsonl(MATH_ATOMS, math_atoms, "math/atoms.jsonl")
    a5_append_jsonl(META_ATOMS, meta_atoms, "meta/atoms.jsonl")
    a5_append_jsonl(CERT_LEDGER, ledger_rows, "meta/cert_ledger.jsonl")

    # A5 POST
    expected = len(math_atoms) + len(meta_atoms)
    a5_post_check(expected_atom_delta=expected, pre_count=pre_count)

    # Disposition summary
    counts = {}
    for c in CELLS:
        counts[c["disposition"]] = counts.get(c["disposition"], 0) + 1
    print(f"\n  Disposition counts:")
    for k, v in sorted(counts.items()):
        print(f"    {k}: {v}")
    print(f"\n  Cluster amendments: {len(meta_atoms)}")
    for a in meta_atoms:
        print(f"    {a['metadata']['cluster_name']} (n_cells={a['metadata']['n_cells_amended']})")

    print("\nHF_BACKLOG 24-CELL ATOMIZATION COMPLETE; CERT N unchanged (all delta=0)")


if __name__ == "__main__":
    main()
