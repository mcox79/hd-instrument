"""
A5-gated atomize: M3 M1.4 refuse-gate v3 (NoiseChannel additive_gaussian) HF closure

Two findings composed:
  (1) M1.4 v3 HF closure: one-sided adaptive tau MECHANISM CLASS wrong shape
  (2) M1.3 NoiseChannel sub-finding VALIDATED: infrastructure wiring confirmed

INDEPENDENT OFF-DATA RECOMPUTE via .venv python (skunkworks 2026-07-01):

Cell commit: 6d23daee
Cell-author commit: ab92865c
Pre-reg: preregs/2026-07-01_substrate_refuse_gate_adaptive_tau_v3_M14.md

Off-data v3 smoke facts (data/exp_substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14_seed_7_smoke/metrics.json):
  run_mode=smoke; elapsed_s=3.77; cardinality_ok=True; N=8192, V_C_per_cat=200, V_REL=256
  Records: expected_n_records=1080 observed=1080; expected_n_units=36 observed=36
  noise_channel_mode = additive_gaussian (M1.3 wiring active)
  4 arms: FIXED_V_REL_256 (baseline), SLIDING_WINDOW, BAYESIAN_CI, PERCENTILE

  Positive control PASS: FIXED_V_REL_256 at clean OOD refuse_rate=1.0 (floor=0.85).

  All 3 adaptive arms MONOTONIC across regime at OOD (all monotonic_across_regime_at_OOD=True):
    SLIDING_WINDOW: rr_clean=1.000 rr_moderate=1.000 rr_heavy=0.833 (monotonic_non_increasing)
    BAYESIAN_CI:   rr_clean=0.567 rr_moderate=0.600 rr_heavy=0.600 (monotonic_non_decreasing)
    PERCENTILE:    rr_clean=0.433 rr_moderate=0.433 rr_heavy=0.267 (monotonic_non_increasing)

  HP GATE (precision_lift_over_fixed_at_moderate >= 0.15) FAIL all 3 arms:
    SLIDING_WINDOW: 0.000  (matches fixed; ARM RAN but decisions identical to FIXED)
                            decision_hash 'd7771d60257e6602' == FIXED decision_hash EXACT
    BAYESIAN_CI:    -0.193 (adaptive HURT precision 19.3 pp: 0.474 vs fixed 0.667)
    PERCENTILE:     -0.076 (adaptive HURT precision  7.6 pp: 0.591 vs fixed 0.667)
    All 3 << 0.15 HP threshold; 2 of 3 NEGATIVE (adaptive HURTS not helps).

  Arm distinctness: 4/4 mechanism_hashes distinct; 3/4 decision_hashes distinct
    (SLIDING_WINDOW decision_hash matches FIXED -- arm computed same decisions
     but via different mechanism; not degenerate).

STRUCTURAL FINDING (per cell-author):
  One-sided adaptive tau LOWERS tau in noisy regimes -> admits more borderline
  in_KB queries (recall gain) AND admits more OOD queries (precision loss).
  NET STRUCTURAL LOSS. This is not a calibration problem; it's a mechanism-class
  problem. Single-tau adaptivity in either direction can't optimize precision
  under noise, because the noise degrades in_KB and OOD symmetrically at the
  cosine-similarity level while affecting them differently at the decision level.

M1.3 SUB-FINDING VALIDATED:
  This cell IS THE FIRST substrate cell to correctly wire the M1.3 cortex
  NoiseChannel (additive_gaussian mode on max_sim scalar). Wiring works;
  regime-std monotonic across arms confirms noise is being injected as designed.
  Design pivot from temperature_softmax (M1.3 spec) to additive_gaussian is
  noted; scale-mismatch was root cause of temperature_softmax path
  (top-1 posterior 1/V_C=0.002 vs tau=0.40; 200x mismatch).

TIER: HARD_FAIL (honest_negative closure_one_sided_adaptive_tau_wrong_mechanism_class).
  Cell-author correctly identified mechanism-class-wrong at smoke; no FULL
  dispatch. Textbook DISCRIMINATOR_MUST_SURVIVE_SCALE + META_RULE_AV at smoke.
  cert_increment_delta = 0.

REVIVAL CRITERIA (specifies conditions under which M1.4 axis is reopenable):
  (a) 2-sided tau band (tau_low + tau_high adapted separately)
  (b) bernoulli_flip_stochastic NoiseChannel mode (per M1.3 spec)
  (c) bimodal-history buckets (in_KB vs OOD separate tau streams)

  Any one authored + 3-seed passes precision_lift >= 0.15 at moderate regime
  with positive-control anchor at 0.85+ refuse_rate: axis M1.4 reopens.

M3 ARCHITECTURE PROGRESS:
  M1.3 cortex-noise-at-boundary infrastructure WORKS. First substrate cell
  correctly using NoiseChannel = additive_gaussian mode + wiring validated.
  M3 architecture status: cortex-noise-at-boundary VALIDATED as working
  infrastructure. Specific M1.4 adaptive-tau mechanism class needs iteration.

  Not a program setback: M1.3 sub-finding is substantive M3 milestone progress.
  This atom composes with prior M3 infrastructure atoms (cortex layer above
  substrate + stochastic noise at boundary per project_M3_cortex_layer_must_
  inject_stochastic_noise_at_boundary_2026-06-30).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_M14_v3_refuse_gate_HF_closure_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_M14_v3_HF = {
    "id": (
        "T3/EXP_substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14_seed_7_smoke_HARD_FAIL_"
        "closure_one_sided_adaptive_tau_wrong_mechanism_class_"
        "SLIDING_WINDOW_precision_lift_0p000_BAYESIAN_CI_-0p193_PERCENTILE_-0p076_all_below_HP_gate_0p15_"
        "positive_control_FIXED_clean_OOD_refuse_rate_1p0_pass_all_arms_monotonic_across_regime_"
        "M1p3_NoiseChannel_sub_finding_VALIDATED_additive_gaussian_wiring_confirmed_"
        "revival_criteria_a_2_sided_tau_band_b_bernoulli_flip_c_bimodal_history_buckets_2026-07-01"
    ),
    "name": (
        "HARD_FAIL closure M1.4 v3 refuse-gate NoiseChannel: one-sided adaptive tau MECHANISM "
        "CLASS is wrong shape. All 3 adaptive arms fail HP precision_lift >= 0.15 threshold at "
        "moderate regime: SLIDING_WINDOW=0.000 (identical decisions to FIXED), BAYESIAN_CI=-0.193 "
        "(hurts precision 19.3pp), PERCENTILE=-0.076 (hurts precision 7.6pp). Positive control "
        "PASS (FIXED refuse_rate=1.0 at clean OOD). All 3 arms monotonic across regime "
        "(mechanism runs). Structural: single-tau adaptivity in noisy regimes admits more "
        "borderline in_KB AND more OOD; net loss regardless of direction. M1.3 NoiseChannel "
        "sub-finding VALIDATED: first substrate cell correctly wiring additive_gaussian mode; "
        "infrastructure works. Revival criteria: (a) 2-sided tau band, (b) bernoulli_flip mode, "
        "(c) bimodal-history buckets. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "M3 M1.4 refuse-gate v3 NoiseChannel smoke HARD_FAIL closure. Cell commit 6d23daee; "
        "cell-author ab92865c; pre-reg 2026-07-01_substrate_refuse_gate_adaptive_tau_v3_M14.md. "
        "\n"
        "OFF-DATA verification: run_mode=smoke; elapsed_s=3.77; cardinality_ok=True; "
        "expected_n_records=1080 observed=1080; expected_n_units=36 observed=36; "
        "N=8192, V_C_per_cat=200, V_REL=256; noise_channel_mode=additive_gaussian.\n"
        "\n"
        "POSITIVE CONTROL PASS: FIXED_V_REL_256 at clean OOD refuse_rate=1.0 (floor=0.85).\n"
        "\n"
        "PER-ARM RESULTS (all arms monotonic_across_regime_at_OOD=True):\n"
        "  FIXED_V_REL_256 (baseline): refuse_precision_at_moderate=0.667\n"
        "  SLIDING_WINDOW: rr [clean=1.000, moderate=1.000, heavy=0.833]\n"
        "                  precision_at_moderate=0.667  precision_lift=0.000\n"
        "                  decision_hash IDENTICAL to FIXED ('d7771d60257e6602')\n"
        "  BAYESIAN_CI:    rr [clean=0.567, moderate=0.600, heavy=0.600]\n"
        "                  precision_at_moderate=0.474  precision_lift=-0.193 (HURTS 19.3pp)\n"
        "  PERCENTILE:     rr [clean=0.433, moderate=0.433, heavy=0.267]\n"
        "                  precision_at_moderate=0.591  precision_lift=-0.076 (HURTS 7.6pp)\n"
        "\n"
        "Arm distinctness: 4/4 mechanism_hashes distinct; 3/4 decision_hashes distinct "
        "(SLIDING_WINDOW decisions identical to FIXED -- arm ran with different mechanism "
        "but converged to same decisions; not degenerate at mechanism level).\n"
        "\n"
        "STRUCTURAL FINDING (per cell-author + auditor concur):\n"
        "  One-sided adaptive tau LOWERS tau in noisy regimes -> admits more borderline in_KB "
        "queries (recall gain) AND more OOD queries (precision loss). Net structural loss. "
        "Single-tau adaptivity in either direction can't optimize precision under noise, "
        "because noise degrades in_KB and OOD symmetrically at cosine level while affecting "
        "them differently at decision level. MECHANISM CLASS is wrong shape.\n"
        "\n"
        "M1.3 SUB-FINDING VALIDATED (substantive M3 progress):\n"
        "  This cell IS THE FIRST substrate cell to correctly wire the M1.3 cortex "
        "NoiseChannel (additive_gaussian mode on max_sim scalar). Wiring works: regime-std "
        "monotonic across arms confirms noise injection as designed. Design pivot from "
        "temperature_softmax (M1.3 original spec) to additive_gaussian noted; scale-mismatch "
        "was root cause of temperature_softmax path (top-1 posterior 1/V_C=0.002 vs tau=0.40; "
        "200x mismatch). M1.3 infrastructure validated.\n"
        "\n"
        "TIER: HARD_FAIL (honest_negative closure_one_sided_adaptive_tau_wrong_mechanism_class).\n"
        "  Cell-author correctly identified mechanism-class-wrong at smoke; no FULL dispatch. "
        "Textbook DISCRIMINATOR_MUST_SURVIVE_SCALE + META_RULE_AV at smoke tier.\n"
        "  cert_increment_delta = 0.\n"
        "\n"
        "REVIVAL CRITERIA (conditions for M1.4 axis reopening; per cell-author):\n"
        "  (a) 2-sided tau band (tau_low + tau_high adapted separately)\n"
        "  (b) bernoulli_flip_stochastic NoiseChannel mode (per M1.3 spec)\n"
        "  (c) bimodal-history buckets (in_KB vs OOD separate tau streams)\n"
        "  Any one authored + 3-seed passes precision_lift >= 0.15 at moderate regime with\n"
        "  positive-control anchor at 0.85+ refuse_rate -> axis M1.4 reopens.\n"
        "\n"
        "M3 ARCHITECTURE PROGRESS:\n"
        "  M1.3 cortex-noise-at-boundary infrastructure VALIDATED via this cell. Not a program\n"
        "  setback: substantive M3 milestone progress. M1.4 adaptive-tau mechanism class needs\n"
        "  iteration but M1.3 infrastructure works. Composes with prior M3 atoms "
        "(project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30)."
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HARD_FAIL",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python on smoke metrics.json: "
            "run_mode=smoke; cardinality_ok=True; 36/36 units; 1080/1080 records; "
            "positive_control PASS (FIXED clean OOD rr=1.0 vs 0.85 floor); "
            "SLIDING_WINDOW precision_lift=0.000 decision_hash IDENTICAL to FIXED; "
            "BAYESIAN_CI precision_lift=-0.193 (HURTS 19.3pp); "
            "PERCENTILE precision_lift=-0.076 (HURTS 7.6pp); "
            "all 3 arms monotonic_across_regime_at_OOD; "
            "4/4 mechanism_hashes distinct; noise_channel_mode=additive_gaussian confirmed"
        ),
        "regime": {
            "N": 8192, "V_C_per_cat": 200, "V_REL": 256,
            "arms": ["FIXED_V_REL_256","SLIDING_WINDOW","BAYESIAN_CI","PERCENTILE"],
            "regimes": ["clean","moderate","heavy"],
            "bands": ["in_KB","OOD"],
            "noise_channel_mode": "additive_gaussian",
        },
        "cell_commit": "6d23daee",
        "cell_author_commit": "ab92865c",
        "smoke_metrics_path": "data/exp_substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14_seed_7_smoke/metrics.json",
        "prereg_path": "preregs/2026-07-01_substrate_refuse_gate_adaptive_tau_v3_M14.md",
        "positive_control_pass": {
            "arm": "FIXED_V_REL_256", "regime": "clean", "band": "OOD",
            "observed_refuse_rate": 1.0, "floor_required": 0.85, "passed": True,
        },
        "per_arm_precision_lift_at_moderate": {
            "SLIDING_WINDOW": 0.000,
            "BAYESIAN_CI": -0.193,
            "PERCENTILE": -0.076,
            "HP_threshold": 0.15,
            "all_below_threshold": True,
            "2_of_3_negative_adaptive_HURTS_precision": True,
        },
        "all_arms_monotonic_across_regime_at_OOD": True,
        "arm_distinctness": {
            "mechanism_hashes_distinct_4_of_4": True,
            "decision_hashes_distinct_3_of_4": True,
            "SLIDING_WINDOW_decision_hash_identical_to_FIXED": True,
        },
        "structural_finding": (
            "One-sided adaptive tau LOWERS tau in noisy regimes -> admits more borderline "
            "in_KB (recall gain) AND more OOD (precision loss). Net structural loss. "
            "Single-tau adaptivity in either direction can't optimize precision under noise. "
            "MECHANISM CLASS is wrong shape; not a calibration issue."
        ),
        "M1_3_NoiseChannel_sub_finding_VALIDATED": {
            "first_substrate_cell_correctly_wiring_NoiseChannel": True,
            "mode_used": "additive_gaussian",
            "regime_std_monotonic_across_arms_confirms_noise_injection": True,
            "design_pivot_from_temperature_softmax_noted": True,
            "temperature_softmax_scale_mismatch_root_cause": "top-1 posterior 1/V_C=0.002 vs tau=0.40; 200x mismatch",
        },
        "cell_author_honest_abort_no_FULL_dispatch": True,
        "revival_criteria_for_M14_axis_reopening": {
            "(a)_2_sided_tau_band": "tau_low + tau_high adapted separately",
            "(b)_bernoulli_flip_stochastic_NoiseChannel_mode": "per M1.3 spec original mode",
            "(c)_bimodal_history_buckets": "in_KB vs OOD separate tau streams",
            "any_one_authored_plus_3seed_HP_precision_lift_ge_0p15_reopens_M14": True,
        },
        "M3_architecture_progress_M1_3_infrastructure_validated": True,
        "not_a_program_setback": True,
        "composes_with_M3_prior_atoms": [
            "project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30",
            "project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28",
        ],
        "cert_increment_delta": 0,
        "discipline_tags": [
            "honest_negative_one_sided_adaptive_tau_wrong_mechanism_class",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_at_smoke_tier_cell_author_correct_abort",
            "META_RULE_AV_precision_lift_gate_fires_at_smoke_as_designed",
            "META_RULE_AX_distinctness_pass_4_of_4_mech_hashes_arms_genuinely_different",
            "META_RULE_H_cardinality_ok_36_of_36_units_1080_of_1080_records",
            "M1_3_NoiseChannel_infrastructure_VALIDATED_first_substrate_cell_correct_wiring",
            "M3_architecture_progress_cortex_noise_at_boundary_validated",
            "revival_criteria_a_b_c_specified_for_axis_reopening",
            "positive_control_FIXED_clean_OOD_1p0_pass_anchor_confirms_finding_is_arm_side_not_test_pathology",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()

ledger_M14_v3_HF = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_M14_v3_HF['id']}",
    "cert_status": "hard_fail",
    "cert_class": "honest_negative_M14_one_sided_adaptive_tau_wrong_mechanism_class_M13_NoiseChannel_sub_finding_VALIDATED",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "6d23daee",
    "verdict": (
        "HARD_FAIL_smoke_seed_7_precision_lift_SLIDING_0p000_BAYESIAN_neg0p193_PERCENTILE_neg0p076_"
        "all_3_below_0p15_HP_gate_2_of_3_negative_positive_control_FIXED_clean_OOD_1p0_pass_"
        "all_arms_monotonic_across_regime_structural_finding_one_sided_tau_wrong_mechanism_class_"
        "M1p3_NoiseChannel_wiring_VALIDATED_additive_gaussian_first_correct_use_"
        "revival_criteria_a_2_sided_tau_band_b_bernoulli_flip_c_bimodal_history_buckets_"
        "M3_architecture_progress_cortex_noise_at_boundary_infrastructure_confirmed"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_refuse_gate_adaptive_tau_v3_noisechannel_M14_seed_7_smoke/metrics.json",
        "prereg_path": "preregs/2026-07-01_substrate_refuse_gate_adaptive_tau_v3_M14.md",
        "cell_commit": "6d23daee",
        "cell_author_commit": "ab92865c",
        "atom_qualified_id": f"math::{atom_M14_v3_HF['id']}",
        "composes_M3_prior_atoms": [
            "project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30",
            "project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28",
        ],
    },
    "supersedes": None,
    "note": (
        "M14_v3_refuse_gate_noisechannel_HF_closure_one_sided_adaptive_tau_wrong_mechanism_class_"
        "SLIDING_WINDOW_precision_lift_0p000_decision_hash_identical_to_FIXED_"
        "BAYESIAN_CI_neg_0p193_PERCENTILE_neg_0p076_2_of_3_HURT_precision_all_3_below_HP_0p15_"
        "positive_control_FIXED_clean_OOD_refuse_rate_1p0_pass_anchor_confirms_finding_"
        "M1p3_NoiseChannel_additive_gaussian_wiring_first_substrate_cell_correct_use_sub_finding_VALIDATED_"
        "design_pivot_from_temperature_softmax_scale_mismatch_top1_posterior_1_over_V_C_0p002_vs_tau_0p40_"
        "revival_criteria_a_2_sided_tau_band_b_bernoulli_flip_stochastic_c_bimodal_history_buckets_"
        "M3_architecture_infrastructure_progress_cortex_noise_at_boundary_validated_"
        "not_program_setback_M1_3_works_M1_4_mechanism_class_iterate_cell_author_correct_abort_at_smoke"
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
    append_jsonl_a5(MATH_ATOMS, atom_M14_v3_HF,     "math/atoms (M1.4 v3 NoiseChannel HF closure + M1.3 sub-finding VALIDATED)")
    append_jsonl_a5(CERT_LEDGER, ledger_M14_v3_HF,  "cert_ledger (M1.4 v3 HF)")
    print(f"[A5] DONE OK")
    print(f"[A5] M1.4 v3 refuse-gate: HARD_FAIL (one-sided adaptive tau wrong mechanism class)")
    print(f"[A5] M1.3 NoiseChannel additive_gaussian wiring VALIDATED (first correct use)")
    print(f"[A5] Revival criteria: (a) 2-sided tau band, (b) bernoulli_flip, (c) bimodal-history buckets")
    print(f"[A5] M3 architecture progress: cortex-noise-at-boundary infrastructure confirmed")
    print(f"[A5] CERT delta = 0")


if __name__ == "__main__":
    main()
