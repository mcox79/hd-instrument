"""
A5-gated atomize: Capacity multi-bank alpha-K HIGH v1 3-seed CHAIN_GRADE
                  (5th CG of 2026-07-01)

INDEPENDENT OFF-DATA VERIFICATION (skunkworks 2026-07-01):

Cell commit: 068fef8b
Pre-reg: preregs/2026-07-01_capacity_multi_bank_alpha_K_HIGH_v1.md

Substrate-KB overlap check (per new 2026-07-01 discipline):
  Query 'capacity_multi_bank_alpha_K': cosine 0.32 top match = older research
  chunk ('capacity_envelope_multibank_alpha_3_v1' in 2026-06-27 drill notes).
  No prior Store atom for HIGH-K extension. Cell-author's report matches --
  genuinely novel.

Off-data facts (all 3 seeds run_mode=full on GPU cuda:0 RTX 4060 Ti):
  Per-seed verdicts: HARD_PASS all 3 seeds
  Elapsed: 32.0-32.6s per seed
  Cardinality: 108/108 units + 36/36 phase points all seeds
  Regimes: [MULTI_BANK_BIND, SINGLE_BANK_BASELINE, RANDOM_FLOOR] all seeds
  arms_differ: 36/36 all seeds (100% distinctness)
  n_failures: 0 all seeds
  GPU utilization: mean 32-47%, max 87-91% all seeds
  store_dtype: torch.float16

Cross-seed n_pass:
  seed_7:  n_pass=19 / phase_points=36; saturate=11; floor=8
  seed_13: n_pass=20 / phase_points=36; saturate=9;  floor=8
  seed_19: n_pass=19 / phase_points=36; saturate=11; floor=8
  Cross-seed mean n_pass=19.33; sd=0.58; cv=0.0299 (excellent stability)
  All 3 exceed n_pass>=12 HP threshold by 1.5x+ margin.

Cross-seed cliff_per_B: identical all 3 seeds
  B=16: 0.6 (K_per=1024 cliff)
  B=64: 0.9 (K_per=2048 cliff)

Positive control (rail_alpha=0.30 K=2048 B=64 N=8192):
  1.0000 all 3 seeds (rail_ok=True by HP_rail>=0.90 gate)

probe_cliffs = 0 all seeds (control healthy; no probe denials)

META_RULE_Q check:
  saturate = 11/36 (seed_7 and seed_19) = 30% saturated phase points
             9/36 (seed_13) = 25% saturated
  Below 60% META_RULE_Q threshold. Rail at 1.0000 is positive-control
  expected-ceiling for the rail regime specifically; not metric saturation
  across the 36 phase-point grid. NOT trapped.

CONFIG NOTES:
  alpha_values = [0.3, 0.6, 0.9] (MID-band)
  K_per_bank_values = [256, 512, 1024, 2048] (HIGH-K extension)
  num_banks_values = [4, 16, 64]
  N_dim_values = [8192] (single N)
  CB=16384 (codebook); sigma=1.0; CUE_COS=0.70; N_ITEMS_PER_TRIAL=256

DESIGN CORRECTION PRESERVED (from cell-author):
  M/B (per-bank load) is the real predictor of capacity behavior, not
  M/B/K_per. Cell-author caught this design falsification at smoke and
  re-spec'd the discriminator around M/B calibration. FULL landed HP
  after respec. This calibration insight is load-bearing for future
  capacity-envelope cell authoring.

============================================================
TIER RULING: CHAIN_GRADE. cert_increment_delta = +1.
============================================================

  All 3 seeds HP per-cell; cross-seed n_pass cv=0.0299 (<<0.10 CG threshold);
  cliff_per_B identical all seeds (mechanism reproduces exactly); positive
  control rail at 1.0000 all seeds (rail_ok); probe_cliffs=0 (no probe denials);
  arms_differ 36/36 all seeds (100% distinctness); cardinality 108/108 + 36/36
  all seeds; META_RULE_Q not tripped (saturation 25-30% below 60% threshold);
  substrate-KB check confirms no prior Store atom.

  FIFTH CG of 2026-07-01 (after A_v2 c7feb0c4, E_v5 716174a7, Cell D v2
  863e14b5, ANCHOR4 N=16384 5ec1b83b).

  SUBSTRATE DESIGN IMPLICATION (chain-grade):
    At N=8192 CB=16384 sigma=1.0 CUE_COS=0.70, MULTI_BANK_BIND regime in the
    HIGH-K coverage (K_per_bank in [256, 512, 1024, 2048], B in [4, 16, 64],
    alpha in [0.3, 0.6, 0.9] MID-band):
      - 19-20 of 36 phase points pass HP discriminator (>=0.30 lift over baseline)
      - cliff_per_B={B=16: K=1024 cliff, B=64: K=2048 cliff}
      - Rail alpha=0.30 K=2048 B=64 rec=1.000 (positive control)
    M/B calibration insight: per-bank load M/B (not M/B/K_per) is the operative
    predictor; hdlab/ primitives should calibrate capacity envelopes around M/B
    for HIGH-K regimes.

  COMPOSES WITH: prior capacity multi-bank alpha-K CG (per Director framing;
  HIGH-K extension of the prior arc).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_capacity_MB_alpha_K_HIGH_v1_CG_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_capacity_MB_HIGH_CG = {
    "id": (
        "T3/EXP_capacity_multi_bank_alpha_K_HIGH_v1_3seed_CHAIN_GRADE_"
        "n_pass_19_20_19_of_36_all_seeds_cv_0p030_cliff_per_B_16_0p6_64_0p9_identical_all_seeds_"
        "rail_alpha_0p30_K_2048_B_64_N_8192_1p000_positive_control_probe_cliffs_0_arms_differ_36_of_36_"
        "cardinality_108_of_108_units_36_of_36_phase_points_saturation_25_to_30_pct_below_META_RULE_Q_"
        "GPU_cuda_RTX_4060_Ti_gpu_util_mean_37pct_max_91pct_"
        "M_over_B_per_bank_load_real_predictor_not_M_over_B_over_K_per_design_calibration_note_"
        "HIGH_K_extension_K_per_bank_256_512_1024_2048_alpha_MID_band_0p3_0p6_0p9_B_4_16_64_N_8192_"
        "5th_CG_of_2026_07_01_2026-07-01"
    ),
    "name": (
        "CHAIN-GRADE Capacity multi-bank alpha-K HIGH v1 3-seed FULL: n_pass=[19,20,19]/36 "
        "cross-seed (cv=0.0299; all >=12 HP threshold by 1.5x+ margin); cliff_per_B identical "
        "all 3 seeds ({B=16: 0.6, B=64: 0.9}); rail alpha=0.30 K=2048 B=64 N=8192 rec=1.000 "
        "all 3 seeds (positive control); probe_cliffs=0 all seeds; arms_differ=36/36 all seeds; "
        "cardinality 108/108 units + 36/36 phase points all seeds; saturation 25-30% below "
        "META_RULE_Q threshold; GPU cuda:0 RTX 4060 Ti util mean 37% max 91%. HIGH-K extension "
        "(K_per_bank in [256, 512, 1024, 2048], B in [4, 16, 64], alpha in [0.3, 0.6, 0.9] "
        "MID-band, N=8192). Design correction from cell-author: M/B (per-bank load) is real "
        "predictor, not M/B/K_per. Composes with prior capacity multi-bank alpha-K CG "
        "(HIGH-K extension). Substrate-KB check confirms no prior Store atom. FIFTH CG of "
        "2026-07-01. CERT +1."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL Capacity multi-bank alpha-K HIGH v1. Cell commit 068fef8b; pre-reg "
        "2026-07-01_capacity_multi_bank_alpha_K_HIGH_v1.md. HIGH-K extension of prior arc.\n"
        "\n"
        "SUBSTRATE-KB OVERLAP CHECK (per new 2026-07-01 discipline rule):\n"
        "  cosine 0.32 top match = older research-drill chunk ('capacity_envelope_multibank_"
        "alpha_3_v1' in 2026-06-27 drill notes); no prior Store atom for HIGH-K extension.\n"
        "  Cell-author's report matches -- genuinely novel HIGH-K coverage.\n"
        "\n"
        "OFF-DATA verification: all 3 seeds run_mode=full on GPU cuda:0 (RTX 4060 Ti); "
        "elapsed 32.0-32.6s per seed; cardinality 108/108 units + 36/36 phase points; "
        "regimes = [MULTI_BANK_BIND, SINGLE_BANK_BASELINE, RANDOM_FLOOR]; arms_differ=36/36; "
        "n_failures=0; probe_cliffs=0; store_dtype=torch.float16; GPU util mean 32-47% "
        "max 87-91%.\n"
        "\n"
        "PER-SEED DISCRIMINATOR METRICS:\n"
        "  seed_7:  n_pass=19/36  saturate=11/36  floor=8/36  n_pass_at_full_N=19  rail_ok=True\n"
        "  seed_13: n_pass=20/36  saturate=9/36   floor=8/36  n_pass_at_full_N=20  rail_ok=True\n"
        "  seed_19: n_pass=19/36  saturate=11/36  floor=8/36  n_pass_at_full_N=19  rail_ok=True\n"
        "\n"
        "CROSS-SEED CV on n_pass:\n"
        "  n_pass = [19, 20, 19]; mean=19.33; sd=0.58; cv=0.0299 (excellent; <<0.10 CG)\n"
        "\n"
        "CROSS-SEED cliff_per_B (identical all 3 seeds; mechanism reproduces exactly):\n"
        "  B=16: 0.6 (K_per=1024 cliff)\n"
        "  B=64: 0.9 (K_per=2048 cliff)\n"
        "\n"
        "POSITIVE CONTROL (rail_alpha=0.30 K=2048 B=64 N=8192):\n"
        "  Rail recall = 1.0000 all 3 seeds (rail_ok=True by HP_rail>=0.90 gate)\n"
        "  probe_cliffs = 0 all seeds (probe control healthy)\n"
        "\n"
        "META_RULE_Q CHECK:\n"
        "  Saturation fraction: 25-30% of 36 phase points across seeds.\n"
        "  Below 60% META_RULE_Q threshold. Rail at 1.0000 is positive-control expected\n"
        "  ceiling for the rail regime specifically; not metric saturation across the 36\n"
        "  phase-point grid. NOT trapped.\n"
        "\n"
        "CONFIG:\n"
        "  alpha_values = [0.3, 0.6, 0.9] (MID-band)\n"
        "  K_per_bank_values = [256, 512, 1024, 2048] (HIGH-K extension)\n"
        "  num_banks_values = [4, 16, 64]\n"
        "  N_dim_values = [8192] (single N)\n"
        "  CB = 16384 (codebook); sigma = 1.0; CUE_COS = 0.70; N_ITEMS_PER_TRIAL = 256\n"
        "\n"
        "DESIGN CORRECTION PRESERVED (from cell-author, load-bearing calibration note):\n"
        "  M/B (per-bank load) is the real predictor of capacity behavior, NOT M/B/K_per.\n"
        "  Cell-author caught this design falsification at smoke and re-spec'd the\n"
        "  discriminator around M/B calibration. FULL landed HP after respec.\n"
        "  This calibration insight is load-bearing for future capacity-envelope cell\n"
        "  authoring: hdlab/ primitives should calibrate around M/B for HIGH-K regimes.\n"
        "\n"
        "TIER: CHAIN_GRADE. cert_increment_delta = +1. FIFTH CG of 2026-07-01.\n"
        "\n"
        "COMPOSES WITH: prior capacity multi-bank alpha-K CG (per Director framing; HIGH-K "
        "extension of prior arc)."
    ),
    "metadata": {
        "provenance_quality": "CERT_CHAIN_GRADE",
        "verdict": "HARD_PASS",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json: all 3 seeds run_mode=full "
            "GPU cuda; cardinality 108/108 + 36/36 all seeds; n_pass=[19,20,19] cross-seed cv=0.030; "
            "cliff_per_B identical all seeds; rail=1.000 all seeds; probe_cliffs=0; arms_differ=36/36; "
            "saturation 25-30% below META_RULE_Q threshold; substrate-KB check confirms no prior atom"
        ),
        "regime": {
            "alpha_values": [0.3, 0.6, 0.9], "MID_band": True,
            "K_per_bank_values": [256, 512, 1024, 2048], "HIGH_K_extension": True,
            "num_banks_values": [4, 16, 64],
            "N_dim_values": [8192],
            "CB": 16384, "sigma": 1.0, "CUE_COS": 0.70, "N_ITEMS_PER_TRIAL": 256,
            "regimes_tested": ["MULTI_BANK_BIND", "SINGLE_BANK_BASELINE", "RANDOM_FLOOR"],
        },
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_capacity_multi_bank_alpha_K_HIGH_v1_seed_7/metrics.json",
            "seed_13": "data/exp_capacity_multi_bank_alpha_K_HIGH_v1_seed_13/metrics.json",
            "seed_19": "data/exp_capacity_multi_bank_alpha_K_HIGH_v1_seed_19/metrics.json",
        },
        "prereg_path": "preregs/2026-07-01_capacity_multi_bank_alpha_K_HIGH_v1.md",
        "cell_commit": "068fef8b",
        "per_seed_discriminator_metrics": {
            "seed_7":  {"n_pass": 19, "saturate": 11, "floor": 8, "arms_differ": "36/36", "rail_ok": True},
            "seed_13": {"n_pass": 20, "saturate": 9,  "floor": 8, "arms_differ": "36/36", "rail_ok": True},
            "seed_19": {"n_pass": 19, "saturate": 11, "floor": 8, "arms_differ": "36/36", "rail_ok": True},
        },
        "cross_seed_n_pass": {
            "vals": [19, 20, 19], "mean": 19.33, "sd": 0.58, "cv": 0.0299,
            "HP_threshold": 12, "margin_x": 1.6,
        },
        "cliff_per_B_identical_all_seeds": {"B=16": 0.6, "B=64": 0.9},
        "positive_control_rail_1p000_all_seeds": True,
        "probe_cliffs_0_all_seeds": True,
        "arms_differ_36_of_36_all_seeds": True,
        "META_RULE_Q_saturation_25_to_30_pct_below_60_pct_threshold_NOT_trapped": True,
        "GPU_utilization_mean_32_to_47_pct_max_87_to_91_pct": True,
        "M_over_B_per_bank_load_design_calibration_note": (
            "M/B (per-bank load) is real predictor of capacity behavior, NOT M/B/K_per. "
            "Cell-author caught this design falsification at smoke and re-spec'd discriminator "
            "around M/B calibration. Load-bearing for future capacity-envelope cell authoring."
        ),
        "cert_increment_delta": 1,
        "cg_promotion_note": "FIFTH CG of 2026-07-01 (after A_v2 c7feb0c4, E_v5 716174a7, Cell D v2 863e14b5, ANCHOR4 N=16384 5ec1b83b)",
        "substrate_design_implication_chain_grade": (
            "At N=8192 CB=16384 sigma=1.0 CUE_COS=0.70, MULTI_BANK_BIND regime HIGH-K coverage "
            "(K_per_bank in [256,512,1024,2048], B in [4,16,64], alpha in [0.3,0.6,0.9] MID-band): "
            "19-20 of 36 phase points pass HP discriminator; cliff_per_B={B=16: K=1024 cliff, "
            "B=64: K=2048 cliff}. hdlab/ primitives should calibrate capacity envelopes around "
            "M/B for HIGH-K regimes."
        ),
        "composes_with_prior_capacity_multi_bank_alpha_K_CG_HIGH_K_extension": True,
        "discipline_tags": [
            "META_RULE_Q_saturation_below_60pct_threshold_NOT_trapped",
            "META_RULE_H_cardinality_ok_108_of_108_units_36_of_36_phase_points_all_seeds",
            "META_RULE_AV_HP_discriminator_gates_fire_cross_seed_n_pass_ge_12_by_1p6x_margin",
            "META_RULE_AF_cliff_per_B_identical_all_seeds_mechanism_reproduces_exactly",
            "META_RULE_AH_arms_differ_36_of_36_positive_control_rail_1p000_probe_cliffs_0",
            "M_over_B_per_bank_load_real_predictor_design_calibration_note_load_bearing",
            "5th_CG_promotion_of_2026_07_01",
            "results_to_application_hdlab_calibrate_M_over_B_for_HIGH_K_regimes",
            "substrate_KB_check_first_confirms_no_prior_Store_atom_HIGH_K_extension_novel",
            "composes_with_prior_capacity_multi_bank_alpha_K_CG_HIGH_K_extension",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()

ledger_capacity_MB_HIGH_CG = {
    "ts": _t0,
    "op": "cert_ruling_promotion_chain_grade",
    "atom_id": f"math::{atom_capacity_MB_HIGH_CG['id']}",
    "cert_status": "chain_grade",
    "cert_class": "pre_reg_pass_capacity_multi_bank_alpha_K_HIGH_extension",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "068fef8b",
    "verdict": (
        "CHAIN_GRADE_3seed_HP_n_pass_19_20_19_of_36_cross_seed_cv_0p030_ge_12_HP_threshold_1p6x_margin_"
        "cliff_per_B_16_0p6_64_0p9_identical_all_seeds_mechanism_reproduces_exactly_"
        "rail_alpha_0p30_K_2048_B_64_N_8192_1p000_positive_control_probe_cliffs_0_"
        "arms_differ_36_of_36_all_seeds_cardinality_108_of_108_36_of_36_saturation_25_to_30_pct_below_META_RULE_Q_"
        "GPU_cuda_RTX_4060_Ti_util_mean_37pct_HIGH_K_extension_K_per_bank_256_to_2048_alpha_MID_B_4_to_64_N_8192_"
        "M_over_B_per_bank_load_design_calibration_note_composes_with_prior_capacity_multi_bank_alpha_K_CG_5th_CG_of_2026_07_01"
    ),
    "cert_increment_delta": 1,
    "cv": 0.0299,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_capacity_multi_bank_alpha_K_HIGH_v1_seed_{7,13,19}/metrics.json",
        "prereg_path": "preregs/2026-07-01_capacity_multi_bank_alpha_K_HIGH_v1.md",
        "cell_commit": "068fef8b",
        "atom_qualified_id": f"math::{atom_capacity_MB_HIGH_CG['id']}",
    },
    "supersedes": None,
    "note": (
        "capacity_multi_bank_alpha_K_HIGH_v1_3seed_CHAIN_GRADE_5th_CG_of_2026_07_01_"
        "n_pass_19_20_19_of_36_cross_seed_cv_0p030_all_ge_12_HP_threshold_1p6x_margin_"
        "cliff_per_B_16_0p6_64_0p9_identical_all_seeds_mechanism_reproduces_exactly_"
        "rail_alpha_0p30_K_2048_B_64_N_8192_1p000_positive_control_probe_cliffs_0_arms_differ_36_of_36_"
        "cardinality_108_of_108_units_36_of_36_phase_points_saturation_25_to_30_pct_below_META_RULE_Q_"
        "GPU_cuda_RTX_4060_Ti_util_mean_37pct_max_91pct_"
        "HIGH_K_extension_K_per_bank_256_512_1024_2048_alpha_MID_band_0p3_0p6_0p9_B_4_16_64_N_8192_"
        "M_over_B_per_bank_load_real_predictor_design_calibration_note_load_bearing_for_future_capacity_envelope_authoring_"
        "cell_author_caught_design_falsification_at_smoke_respec_M_over_B_FULL_landed_HP_"
        "substrate_KB_check_first_confirms_no_prior_Store_atom_only_older_research_chunk_cosine_0p32_"
        "composes_with_prior_capacity_multi_bank_alpha_K_CG_HIGH_K_extension_"
        "hdlab_primitives_should_calibrate_capacity_envelopes_around_M_over_B_for_HIGH_K_regimes"
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
    append_jsonl_a5(MATH_ATOMS, atom_capacity_MB_HIGH_CG,      "math/atoms (capacity multi-bank alpha-K HIGH v1 3-seed CHAIN_GRADE)")
    append_jsonl_a5(CERT_LEDGER, ledger_capacity_MB_HIGH_CG,   "cert_ledger (capacity MB alpha-K HIGH CG +1; 5th CG of 2026-07-01)")
    print(f"[A5] DONE OK")
    print(f"[A5] capacity multi-bank alpha-K HIGH v1 3-seed: CHAIN_GRADE +1 (5th CG of 2026-07-01)")
    print(f"[A5] cross-seed n_pass cv=0.030; cliff_per_B identical all seeds; rail=1.000 all seeds")
    print(f"[A5] M/B (per-bank load) design calibration note preserved")
    print(f"[A5] CERT delta = +1")


if __name__ == "__main__":
    main()
