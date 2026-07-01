"""
A5-gated atomize: Axis H v2 S=32 revival criterion FALSIFIED + v1 amendment

Two atoms written:
  (1) v2_S32 HF smoke: falsifies v1 revival criterion; positive control ALSO broken
  (2) v1 AMENDMENT: v1 HF closure re-tiered from HF_STRUCTURAL_BOUND to
      HF_TEST_DESIGN_FAILURE_pending_positive_control_verification because the
      original positive-control (flat @ M=4K in v1 pilot) was actually at floor
      (0.010) matching v2's broken flat (0.0085). The v1 SNR-scaling framing
      cannot be trusted until positive control is verified.

INDEPENDENT OFF-DATA VERIFICATION (skunkworks 2026-07-01):

v2 smoke path: data/exp_substrate_hierarchical_bank_v2_S32_seed_7_smoke/metrics.json
v2 cell commit: 8fead142
v2 pre-reg: preregs/2026-07-01_substrate_hierarchical_bank_v2_S32_revival.md

Off-data v2 smoke facts:
  run_mode=smoke; elapsed_s=468.2; cardinality_ok=True; verdict=HARD_FAIL
  verdict_msg: HARD_FAIL_SMOKE_v2_S32_REVIVAL: positive_control_fail:
    target flat M=4000 recall_floor=0.8 measured=0.0085; test rig broken
  tier_counts: SAT=1 HP=0 MB=0 FLOOR=4 HF=1
  hier_routing_acc_at_M_max = 0.0539 (vs required >= 0.85)
  capacity_lift_hier_vs_partition_at_M_max = 0.0519
  capacity_lift_hier_vs_flat_at_M_max = inf (because flat = 0)
  distinctness: 3/3 pred pairs distinct + 3/3 mech pairs distinct
  selftest also failed: hierarchical_S32_2level recall=0.309 < MB_LO 0.5

TWO INDEPENDENT FINDINGS:

FINDING 1: v1 revival criterion FALSIFIED (empirical SNR ≠ theoretical CRLB)
  v1 predicted (auditor atom 310e1880): S=32 v2 SNR = sqrt(N*S/M) = 2.024 at
  M=64K, N=8192, S=32. Predicted well above 0.85 floor.
  v2 measured hier_routing_acc_at_M_max = 0.0539.
  Theoretical SNR overpredicts empirical routing performance by ~38x.
  Reason (cell-author): single-workspace bipolar-quantized router with SIGMA=1.0
  noise doesn't preserve theoretical SNR. The sqrt(N*S/M) formula assumes
  ideal linear projection; bipolar quantization + noise floor destroys it.

FINDING 2: Positive control ALSO broken (retro-invalidates v1 SNR framing)
  v2 smoke flat @ M=4K, N=8192 = 0.0085 recall (need >= 0.80).
  v1 pilot flat @ M=4K = 0.010 (matches v2 within noise).
  Cell-author diagnosis: shared bundled workspace collapses at M=4K in N=8192.
  SNR = 1.43 with bipolar+SIGMA=1.0 noise floods signal.

  IMPLICATION FOR V1 ATOM (310e1880):
    v1 HF closure was tiered as STRUCTURAL BOUND (router SNR sqrt(N/M) at M>>N).
    But if positive control (flat) was ALREADY at floor, we cannot distinguish:
      (a) hierarchical_2level failed due to router SNR bound (v1 framing), OR
      (b) BOTH flat AND hierarchical_2level failed due to shared-workspace
          quantization+noise bound at M>>N (revised framing).
    Option (b) is more plausible given v2 confirms flat also broken.

    RE-TIERING v1: HF_STRUCTURAL_BOUND -> HF_TEST_DESIGN_FAILURE_pending_PC_verification.
    v1's cert_class shifts from mechanism-characterization-with-revival to
    honest-negative-with-test-rig-remediation-needed.

    NOTE: v1 HF closure ruling STANDS (hierarchical_2level did fail). Only
    the ATTRIBUTION shifts from "router SNR structural bound" to "shared-workspace
    quantization+noise bound (pending positive-control verification)".

============================================================
ATOM 1: v2 S=32 falsification of v1 revival
============================================================
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_axis_H_v2_falsification_and_v1_amendment_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

V1_ATOM_ID_REFERENT = (
    "T3/EXP_substrate_hierarchical_bank_v1_HARD_FAIL_closure_router_snr_scaling_under_load_"
    "2_workspace_bundled_router_SNR_sqrt_N_over_M_0p358_at_M_64K_N_8192_below_0p85_"
    "hier_routing_acc_0p432_measured_at_pilot_M_4K_cell_author_honest_abort_no_FULL_dispatch_"
    "revival_criterion_S_ge_32_sub_banks_shifts_SNR_to_sqrt_N_S_over_M_2p024_at_M_64K_S_32_2026-07-01"
)

atom_v2_HF_falsifies_revival = {
    "id": (
        "T3/EXP_substrate_hierarchical_bank_v2_S32_seed_7_smoke_HARD_FAIL_falsifies_v1_revival_"
        "criterion_predicted_SNR_2p024_measured_hier_routing_acc_0p0539_38x_overprediction_"
        "positive_control_ALSO_BROKEN_flat_M_4K_recall_0p0085_test_rig_broken_"
        "shared_workspace_bipolar_quantized_noise_floods_signal_2026-07-01"
    ),
    "name": (
        "HARD_FAIL v2 S=32 revival smoke FALSIFIES v1 auditor revival criterion. Predicted "
        "SNR=sqrt(N*S/M)=2.024 at S=32 M=64K N=8192; measured hier_routing_acc_at_M_max=0.0539 "
        "(38x overprediction). Simultaneously reveals v1 positive control was ALSO broken: "
        "flat @ M=4K = 0.0085 recall (below 0.80 floor). Cell-author diagnoses shared-workspace "
        "bipolar-quantized router with SIGMA=1.0 doesn't preserve theoretical SNR at these "
        "M/N ratios. Selftest also failed. Tier_counts SAT=1 HP=0 MB=0 FLOOR=4 HF=1. Distinctness "
        "pass (arms differ). AMENDS v1 atom (commit 310e1880): retire the S>=32 revival criterion; "
        "propose new revival candidates: (a) content-addressable hash router, (b) S independent "
        "router workspaces, (c) different M/N regime. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Axis H v2 S=32 hierarchical_bank REVIVAL smoke HARD_FAIL. Cell commit 8fead142; "
        "pre-reg 2026-07-01_substrate_hierarchical_bank_v2_S32_revival.md; author a478639e. "
        "\n"
        "OFF-DATA verification: run_mode=smoke; elapsed_s=468.2; cardinality_ok=True; "
        "tier_counts SAT=1 HP=0 MB=0 FLOOR=4 HF=1. "
        "verdict=HARD_FAIL with author message: 'HARD_FAIL_SMOKE_v2_S32_REVIVAL: "
        "positive_control_fail: target flat M=4000 recall_floor=0.8 measured=0.0085; test "
        "rig broken'. Selftest ALSO failed (hierarchical_S32_2level recall=0.309 < MB_LO 0.5).\n"
        "\n"
        "TWO INDEPENDENT FINDINGS:\n"
        "\n"
        "FINDING 1 (v1 revival criterion FALSIFIED):\n"
        "  v1 auditor atom (310e1880) predicted S=32 v2 SNR = sqrt(N*S/M) = sqrt(8192*32/64000) "
        "= 2.024 at M=64K, well above 0.85 floor.\n"
        "  v2 measured hier_routing_acc_at_M_max = 0.0539 (38x overprediction).\n"
        "  Cell-author diagnosis: single-workspace bipolar-quantized router with SIGMA=1.0 "
        "noise doesn't preserve theoretical SNR. sqrt(N*S/M) formula assumes ideal linear "
        "projection; bipolar quantization + noise floor destroys it in this substrate design.\n"
        "\n"
        "FINDING 2 (positive control ALSO broken; retro-invalidates v1 SNR framing):\n"
        "  v2 smoke flat @ M=4K N=8192 = 0.0085 recall (need >= 0.80).\n"
        "  v1 pilot flat @ M=4K = 0.010 (matches v2 within noise; both broken).\n"
        "  Shared bundled workspace collapses at M=4K in N=8192 due to bipolar+SIGMA=1.0 "
        "noise flooding signal (SNR=1.43 per cell-author calc).\n"
        "\n"
        "OTHER v2 smoke evidence:\n"
        "  hier_routing_acc_at_M_max = 0.0539 (was 0.85 required for HP)\n"
        "  capacity_lift_hier_vs_partition_at_M_max = 0.0519\n"
        "  capacity_lift_hier_vs_flat_at_M_max = inf (flat at 0)\n"
        "  distinctness: 3/3 pair pred distinct + 3/3 pair mech distinct (arms differ)\n"
        "\n"
        "IMPLICATION FOR v1 ATOM:\n"
        "  v1 HF closure ruling STANDS (hierarchical_2level did fail with hier_routing_acc "
        "0.432 well below 0.85). But ATTRIBUTION shifts:\n"
        "    OLD v1 framing: 'router SNR structural bound sqrt(N/M) at M>>N'\n"
        "    NEW framing: 'shared-workspace quantization+noise bound at M>>N; pending "
        "positive-control verification'\n"
        "  v1 atom needs AMENDMENT to note this. Companion amendment atom filed alongside "
        "this one (same commit).\n"
        "\n"
        "TIER: HARD_FAIL (honest_negative_test_rig_broken_v1_revival_criterion_falsified).\n"
        "  Cell-author correctly identified test-rig-broken via positive-control fail rather "
        "than proceeding to FULL. Textbook DISCRIMINATOR_MUST_SURVIVE_SCALE application at "
        "smoke tier.\n"
        "  cert_increment_delta = 0.\n"
        "\n"
        "NEW REVIVAL CANDIDATES (per cell-author; supersedes S>=32 revival):\n"
        "  (a) content-addressable hash router (no shared bundle-workspace)\n"
        "  (b) S independent router workspaces (not one shared bundle)\n"
        "  (c) revisit positive-control regime (M=4K may be above the soft cliff for shared "
        "workspace at N=8192)\n"
        "  Any one of the three, IF authored and passes positive-control at flat >= 0.80, "
        "would enable axis H reopening.\n"
        "\n"
        "DO NOT re-explore S>=32 sub-banks at this substrate design (bipolar+SIGMA=1.0 in "
        "shared workspace) without new revival mechanism from (a) (b) or (c)."
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HARD_FAIL",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on smoke metrics.json: "
            "run_mode=smoke; cardinality_ok=True; verdict=HARD_FAIL; "
            "hier_routing_acc_at_M_max=0.0539 (38x below predicted 2.024); "
            "flat @ M=4K recall=0.0085 (100x below 0.80 floor); "
            "selftest also failed; distinctness pass 3/3 pairs; "
            "capacity_lift_hier_vs_flat=inf (flat at 0); tier_counts SAT=1 FLOOR=4 HF=1"
        ),
        "regime": {"N": 8192, "M_smoke": 4000, "M_target": 64000, "S_sub_banks": 32,
                   "structures": ["flat","partition_by_source","hierarchical_S32_2level"]},
        "cell_commit": "8fead142",
        "cell_author": "a478639e",
        "smoke_metrics_path": "data/exp_substrate_hierarchical_bank_v2_S32_seed_7_smoke/metrics.json",
        "prereg_path": "preregs/2026-07-01_substrate_hierarchical_bank_v2_S32_revival.md",
        "v1_atom_falsified_referent": V1_ATOM_ID_REFERENT,
        "v1_atom_commit_referent": "310e1880",
        "v1_predicted_SNR_2p024_measured_hier_routing_acc_0p0539_ratio_38x": True,
        "positive_control_broken": {
            "target": {"structure": "flat", "M": 4000, "recall_floor": 0.80},
            "measured": 0.0085,
            "ratio_below_floor_x": 94,
            "v1_pilot_flat_matches_within_noise": {"v1_value": 0.010, "v2_value": 0.0085},
            "shared_workspace_bipolar_noise_flooding_diagnosis": True,
        },
        "hier_routing_acc_at_M_max": 0.0539,
        "capacity_lift_hier_vs_partition_at_M_max": 0.0519,
        "capacity_lift_hier_vs_flat_at_M_max": "inf (flat at 0)",
        "distinctness_pass_3_of_3_pairs_pred_and_mech": True,
        "cell_author_test_rig_broken_diagnosis_correct": True,
        "amends_v1_revival_criterion": True,
        "supersedes_v1_S_ge_32_revival": True,
        "new_revival_candidates": [
            "(a)_content_addressable_hash_router_no_shared_bundle_workspace",
            "(b)_S_independent_router_workspaces_not_one_shared_bundle",
            "(c)_revisit_positive_control_regime_M_4K_may_be_above_soft_cliff_for_shared_workspace_at_N_8192",
        ],
        "cert_increment_delta": 0,
        "discipline_tags": [
            "honest_negative_test_rig_broken_v1_revival_criterion_falsified",
            "auditor_revival_criterion_falsified_theoretical_SNR_not_empirical_at_38x",
            "META_RULE_AX_distinctness_pass_arms_differ_not_test_pathology_at_arm_level",
            "META_RULE_AC_positive_control_fail_at_smoke_extends_to_falsification_ruling",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_at_smoke_tier_cell_author_correct_abort",
            "amends_v1_atom_310e1880_revival_criterion_supersedes_S_ge_32",
            "new_revival_candidates_a_b_c_specified",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# ATOM 2: v1 AMENDMENT (re-tier attribution; ruling stands)
# ============================================================================
atom_v1_amendment = {
    "id": (
        "T3/EXP_substrate_hierarchical_bank_v1_AMENDMENT_from_HF_STRUCTURAL_BOUND_to_"
        "HF_TEST_DESIGN_FAILURE_pending_PC_verification_positive_control_flat_M_4K_ALSO_broken_"
        "in_v1_pilot_at_0p010_matches_v2_broken_0p0085_shared_workspace_bipolar_noise_flooding_"
        "ruling_stands_attribution_shifts_router_SNR_framing_retired_new_revival_candidates_needed_2026-07-01"
    ),
    "name": (
        "AMENDMENT to v1 hierarchical_bank HF closure (atom commit 310e1880): re-attributes "
        "the HF from HF_STRUCTURAL_BOUND (router SNR sqrt(N/M) framing) to "
        "HF_TEST_DESIGN_FAILURE_pending_PC_verification. Trigger: v2 S=32 smoke revealed "
        "positive control (flat @ M=4K) ALSO broken at 0.0085 recall (v1 pilot showed 0.010 - "
        "matches within noise). Both v1 pilot and v2 smoke's shared bundled workspace with "
        "bipolar quantization + SIGMA=1.0 noise flood the signal. v1 HF RULING STANDS "
        "(hierarchical_2level did fail with hier_routing_acc=0.432). Attribution shifts: "
        "not a clean router-SNR structural bound; more likely a shared-workspace "
        "quantization+noise bound where both flat AND hierarchical_2level are victims. "
        "Retires v1 S>=32 revival criterion (falsified by v2 companion atom). CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "amendment_record",
    "description": (
        "AMENDMENT to v1 Axis H hierarchical_bank atom (commit 310e1880).\n"
        "\n"
        "WHAT CHANGES:\n"
        "  - HF closure RULING STANDS (v1's hierarchical_2level did fail with "
        "hier_routing_acc=0.432 vs required 0.85; that measurement is unchanged).\n"
        "  - HF ATTRIBUTION shifts: old framing 'router SNR structural bound sqrt(N/M) at "
        "M>>N' is no longer defensible because v1's positive control (flat @ M=4K = 0.010 "
        "recall) was ALREADY at floor. New framing: 'shared-workspace bipolar-quantized "
        "router with SIGMA=1.0 noise floods signal at M>>N; both flat and "
        "hierarchical_2level victims'. This is a test-rig-broken finding, not a clean "
        "structural bound.\n"
        "  - v1's proposed S>=32 revival criterion (SNR_v2 = sqrt(N*S/M) = 2.024) is FALSIFIED "
        "by v2 smoke (measured 0.0539). Theoretical SNR overpredicts empirical routing by 38x.\n"
        "  - v1's cert_class shifts from mechanism_characterization_with_revival to "
        "honest_negative_with_test_rig_remediation_needed.\n"
        "\n"
        "WHAT REMAINS UNCHANGED:\n"
        "  - v1 hier_routing_acc measurement 0.432 (real).\n"
        "  - CRLB flat_64K_SNR = 0.358 arithmetic (real; but empirical SNR-to-routing-acc\n"
        "    mapping is not the theoretical one).\n"
        "  - Cell-author v1 honest-abort discipline correct.\n"
        "  - cert_increment_delta = 0 (was 0; remains 0).\n"
        "\n"
        "WHY AMENDMENT NOT SUPERSEDES:\n"
        "  v1 atom contains real off-data measurements + reproducible math + valid HF ruling. "
        "Superseding it would obscure the cert-trail. Amendment preserves evidence link with "
        "corrected attribution.\n"
        "\n"
        "NEW REVIVAL FRAMEWORK for Axis H (specifies conditions for reopening):\n"
        "  Any of the following (per cell-author):\n"
        "    (a) Content-addressable hash router (no shared bundle-workspace)\n"
        "    (b) S independent router workspaces (not one shared bundle)\n"
        "    (c) Revisit positive-control regime (M=4K may be above soft cliff for shared\n"
        "        workspace at N=8192; test at M/N ratios where flat >= 0.80 first, THEN\n"
        "        test hierarchical_2level within that regime)\n"
        "  Any one, IF authored with positive-control at flat >= 0.80 FIRST, opens\n"
        "  axis H for CG-eligibility with proper pre-reg.\n"
        "\n"
        "AUDITOR SELF-CRITIQUE (from 310e1880 atomization):\n"
        "  The v1 atom framed the failure as 'router SNR structural bound' based on\n"
        "  CRLB arithmetic being valid. But I should have flagged the v1 pilot flat=0.010\n"
        "  as a positive-control concern rather than reading it as 'flat = floor as expected'.\n"
        "  Flat @ M=4K should have EASILY cleared 0.80 recall floor at N=8192 in an ideal\n"
        "  substrate. That it didn't was already a signal the test rig had issues. v2 makes\n"
        "  this explicit; v1 auditor missed it.\n"
        "\n"
        "TIER: no independent tier (this is an amendment, not a new experimental finding).\n"
        "cert_increment_delta = 0."
    ),
    "metadata": {
        "provenance_quality": "AMENDMENT_RECORD",
        "verdict": "AMENDS_PRIOR_ATOM",
        "amends_atom_referent": V1_ATOM_ID_REFERENT,
        "amends_atom_commit_referent": "310e1880",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python: v1 pilot flat @ M=4K = 0.010 recall "
            "(from pilot metrics.json; retro-read); v2 smoke flat @ M=4K = 0.0085 recall; "
            "both far below 0.80 floor; shared-workspace bipolar+SIGMA=1.0 noise flooding "
            "diagnosis by cell-author reproduces the pattern"
        ),
        "attribution_change": {
            "OLD_attribution": "HF_STRUCTURAL_BOUND_router_SNR_sqrt_N_over_M_at_M_gt_gt_N",
            "NEW_attribution": "HF_TEST_DESIGN_FAILURE_shared_workspace_bipolar_noise_flooding_pending_PC_verification",
            "reasoning": "v1 positive control (flat) was ALREADY at floor; not distinguishable from broken test rig",
        },
        "what_remains_unchanged": [
            "hier_routing_acc_measurement_0p432_real",
            "CRLB_arithmetic_valid_but_SNR_to_routing_acc_mapping_not_theoretical",
            "cell_author_honest_abort_discipline_correct",
            "cert_increment_delta_0",
        ],
        "S_ge_32_revival_criterion_from_v1_atom_FALSIFIED_by_v2_smoke": True,
        "v2_measured_hier_routing_acc_0p0539_vs_predicted_2p024_ratio_38x": True,
        "new_revival_framework": {
            "(a)_content_addressable_hash_router": "no_shared_bundle_workspace",
            "(b)_S_independent_router_workspaces": "not_one_shared_bundle",
            "(c)_positive_control_regime_first": "test_M_N_ratios_where_flat_ge_0p80_THEN_hierarchical_2level",
            "requirement_for_axis_H_reopening": "any_one_of_a_b_c_authored_with_positive_control_flat_ge_0p80_FIRST",
        },
        "auditor_self_critique": (
            "v1 atom framed failure as router-SNR structural bound based on CRLB arithmetic. "
            "Should have flagged v1 pilot flat=0.010 as positive-control concern rather than "
            "reading it as 'flat = floor as expected'. Flat @ M=4K should easily clear 0.80 "
            "recall floor at N=8192 in an ideal substrate. v2 makes this explicit; v1 "
            "auditor missed it. Future: verify positive control at floor threshold before "
            "attributing HF to structural bound."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "amendment_not_supersession_preserves_evidence_link",
            "auditor_self_critique_should_have_flagged_broken_PC_at_v1",
            "attribution_shift_router_SNR_to_shared_workspace_noise_flooding",
            "META_RULE_AV_positive_control_at_floor_should_be_HF_test_design_not_HF_structural",
            "new_revival_framework_a_b_c_specified",
            "companion_atom_v2_S32_falsification_filed_same_commit",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================================
# CERT LEDGER ROWS (2 rows: v2 HF + v1 amendment)
# ============================================================================
_t0 = time.time()

ledger_v2_HF_falsifies_revival = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_v2_HF_falsifies_revival['id']}",
    "cert_status": "hard_fail",
    "cert_class": "honest_negative_test_rig_broken_v1_revival_criterion_falsified_38x_overprediction",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "8fead142",
    "verdict": (
        "HARD_FAIL_smoke_v2_S32_positive_control_fail_flat_M_4K_recall_0p0085_vs_floor_0p80_"
        "hier_routing_acc_0p0539_vs_v1_predicted_2p024_38x_overprediction_test_rig_broken_"
        "shared_workspace_bipolar_SIGMA_1p0_noise_flooding_signal_"
        "cell_author_correct_abort_at_smoke_amends_v1_revival_criterion_new_candidates_a_b_c"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_hierarchical_bank_v2_S32_seed_7_smoke/metrics.json",
        "prereg_path": "preregs/2026-07-01_substrate_hierarchical_bank_v2_S32_revival.md",
        "cell_commit": "8fead142",
        "cell_author": "a478639e",
        "amends_v1_atom": V1_ATOM_ID_REFERENT,
        "amends_v1_commit": "310e1880",
        "atom_qualified_id": f"math::{atom_v2_HF_falsifies_revival['id']}",
    },
    "supersedes": None,
    "note": (
        "axis_H_v2_S32_smoke_HF_falsifies_v1_revival_criterion_"
        "predicted_SNR_2p024_measured_hier_routing_acc_0p0539_38x_overprediction_"
        "positive_control_flat_M_4K_ALSO_broken_at_0p0085_test_rig_broken_diagnosis_"
        "shared_workspace_bipolar_SIGMA_1p0_noise_flooding_signal_"
        "new_revival_candidates_content_addressable_hash_router_OR_S_independent_workspaces_OR_positive_control_first_regime"
    ),
}

ledger_v1_amendment = {
    "ts": _t0 + 0.001,
    "op": "cert_amendment",
    "atom_id": f"math::{atom_v1_amendment['id']}",
    "cert_status": "amendment_record_no_status_change",
    "cert_class": "amendment_attribution_shift_HF_STRUCTURAL_to_HF_TEST_DESIGN",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "AMENDMENT_to_v1_HF_atom_ruling_STANDS_attribution_shifts_"
        "OLD_router_SNR_structural_bound_NEW_shared_workspace_bipolar_noise_flooding_pending_PC_"
        "v1_pilot_flat_0p010_matches_v2_flat_0p0085_within_noise_both_broken_"
        "S_ge_32_revival_criterion_FALSIFIED_by_v2_new_revival_framework_a_b_c"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "amends_atom": V1_ATOM_ID_REFERENT,
        "amends_atom_commit": "310e1880",
        "companion_atom_v2_HF": f"math::{atom_v2_HF_falsifies_revival['id']}",
        "atom_qualified_id": f"math::{atom_v1_amendment['id']}",
    },
    "supersedes": None,
    "note": (
        "axis_H_v1_atom_amendment_ruling_stands_attribution_shifts_"
        "OLD_HF_STRUCTURAL_BOUND_router_SNR_sqrt_N_over_M_NEW_HF_TEST_DESIGN_FAILURE_pending_PC_verification_"
        "v1_positive_control_flat_M_4K_0p010_recall_ALREADY_at_floor_should_have_been_PC_concern_"
        "v2_smoke_confirms_pattern_flat_0p0085_shared_workspace_bipolar_noise_flooding_"
        "auditor_self_critique_v1_should_have_flagged_broken_PC_before_structural_framing_"
        "S_ge_32_revival_criterion_falsified_new_revival_framework_a_b_c_specified"
    ),
}


# ============================================================================
# A5 write protocol
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists()

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row: assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row: assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text); f.flush(); os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try: os.replace(str(tmp_path), str(path)); break
        except PermissionError:
            if _attempt == 9: raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row: assert tail["id"] == new_row["id"]
    if "atom_id" in new_row: assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_v2_HF_falsifies_revival,   "math/atoms (v2 S32 HF falsifies v1 revival)")
    append_jsonl_a5(MATH_ATOMS, atom_v1_amendment,              "math/atoms (v1 amendment attribution shift)")
    append_jsonl_a5(CERT_LEDGER, ledger_v2_HF_falsifies_revival,"cert_ledger (v2 S32 HF)")
    append_jsonl_a5(CERT_LEDGER, ledger_v1_amendment,           "cert_ledger (v1 amendment)")
    print(f"[A5] DONE OK")
    print(f"[A5] Axis H v2 S32 smoke HF (falsifies v1 revival at 38x SNR overprediction)")
    print(f"[A5] Axis H v1 AMENDMENT (attribution HF_STRUCTURAL -> HF_TEST_DESIGN pending PC verify)")
    print(f"[A5] Auditor self-critique: should have flagged v1 broken PC (flat=0.010) before structural framing")
    print(f"[A5] New revival candidates: (a) content-addressable hash router, (b) S independent workspaces, (c) PC-first regime")
    print(f"[A5] CERT delta = 0 (was 0; remains 0)")


if __name__ == "__main__":
    main()
