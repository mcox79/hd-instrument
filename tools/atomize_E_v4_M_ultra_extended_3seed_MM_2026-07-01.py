"""
A5-gated atomize: E_v4 bytes_per_fact_pareto v4 M-ultra-extended 3-seed MM

INDEPENDENT OFF-DATA RECOMPUTE via .venv python (skunkworks 2026-07-01):

Per-seed author verdict: MIDDLE_BAND all 3 seeds (5/6 gates PASS; pareto_2x False).

Off-data top-level:
  run_mode=full all 3; elapsed 157-158s; cardinality PASS all.
  positive_control_ok=True all seeds (FP32 recall=1.0).
  fp16_range_safe_not_collapsed=True all seeds.
  int4_valid_tier=True all seeds.
  monotone_decay_ok=True all seeds.
  bfloat16 tracks FP32 tightly.
  mechanism_hashes_distinct=True all seeds.

M grid: [1000, 4000, 10000, 40000, 80000, 160000]; crack region M=40000-160000.

META_RULE_Q CEILING ESCAPE (the primary claim):
  ceiling_saturation_ratio cross-seed: [0.381, 0.405, 0.286]
  mean = 0.357, cv = 0.176.
  v3 was 0.714 all 3 seeds (structurally identical). v4 dropped to 0.29-0.40.
  ESCAPE CONFIRMED cross-seed but cv=0.176 above CG threshold 0.15.

FULL ARM x M RECALL GRID (off-data cross-seed):
  Arm           M=1k    M=4k    M=10k   M=40k   M=80k   M=160k
  FP32          1.000   1.000   0.995+  0.398   0.113   0.031  (mean cross-seed)
  BFLOAT16      1.000   1.000   0.995+  0.397   0.112   0.031
  FP16_RS       1.000   1.000   0.995+  0.398   0.113   0.031
  INT8          1.000   1.000   0.995+  0.398   0.113   0.031
  INT4          1.000   1.000   0.994+  0.387   0.109   0.030
  BINARY        1.000   1.000   0.961   0.223   0.059   0.017
  SPARSE_0p05   0.837   0.118   0.026   0.002   0.001   0.001

CRACK ORDERING ANALYSIS:
  Top-4 precisions (FP32 / BFLOAT16 / FP16_RS / INT8) are ALL EQUIVALENT within
  recall noise <0.001 at every M level.

  Ordering FLIPS across seeds within top-4:
    seed_7  M=40k: FP32=FP16_RS=INT8=0.3858 > BFLOAT16=0.3845 (INT8 ties FP32)
    seed_13 M=40k: INT8=0.4008 > BFLOAT16=0.4005 > FP32=FP16_RS=0.4000 (INT8 BEATS FP32)
    seed_19 M=40k: FP32=FP16_RS=0.4073 > BFLOAT16=INT8=0.4058 (BFLOAT ties INT8)

  Clear tier separations that DO survive cross-seed:
    Tier 1 (top-4 fungible): FP32 / BFLOAT16 / FP16_RS / INT8 within 0.001 noise
    Tier 2 (INT4 slightly below): INT4 ~0.010-0.012 below top-4 at M=40-80k
    Tier 3 (BINARY at ~0.4-0.6x): BINARY at 0.22 vs top-4 at 0.40 at M=40k
    Tier 4 (SPARSE_0p05 floor): sparse-bipolar at 0.001-0.003 near zero

CANONICAL RULES CHECK:
  Per-cell verdict = MB not HP (5/6 gates; pareto_2x False) -> per-cell not CG-eligible
  Cross-seed reproducibility on 5/6 gates: EXCELLENT (identical PASS pattern all 3 seeds)
  ceiling_saturation_ratio cv = 0.176 > 0.15 CG threshold
  Top-4 ordering NOT consistent cross-seed (instrument noise dominates ordering claim)
  META_RULE_Q ceiling ESCAPED (0.71 -> 0.36) but not below CG boundary
  META_RULE_H cardinality OK all seeds
  Positive control PASS all seeds
  Mechanism hashes distinct all seeds

TIER RULING: MEASURED_MECHANISM (not CG-eligible).

RATIONALE:
  (1) Per-cell verdict is MB across all 3 seeds. CG requires per-cell HP + cross-seed HP.
  (2) The "crack ordering discriminator" claim over-reaches: top-4 precisions are
      EQUIVALENT within recall noise; ordering FLIPS across seeds (INT8 first for
      seed_13; FP32 first for seed_7/19). Not a chain-grade precision hierarchy.
  (3) ceiling_saturation_ratio cv=0.176 above 0.15 CG threshold; ceiling escape is
      real (0.71 -> 0.36) but not uniform enough to be CG.
  (4) pareto_2x_separation False all 3 seeds (arms converge at capacity limit;
      the "crack" reveals fungibility of top-4 precisions, not a Pareto separation).

PROVEN BOUNDS (chain-grade-quality within tier tolerances):
  - Precision tier 1: FP32 / BFLOAT16 / FP16_RS / INT8 mutually fungible for
    recall in this M/N regime. INT8 at 0.5x memory vs FP32 loses ~0 recall.
  - Precision tier 2: INT4 loses ~0.01 recall vs Tier 1 (marginal cost of 2x
    compression from INT8 to INT4).
  - Precision tier 3: BINARY loses ~0.18 recall vs Tier 1 at M=40k crack (large
    cost for 32x compression from FP32).
  - Precision tier 4: SPARSE_BIPOLAR_0p05 collapses to floor at moderate M
    (bandwidth insufficient at this configuration).

  The USEFUL CG-eligible CLAIM (not the current cell's HP verdict framing):
    "At N=8192, in the capacity-crack regime M=40000-80000, INT8 is Pareto-optimal
    (memory 4x FP32, recall equivalent). INT4 acceptable for 8x compression at
    0.01 recall cost. BINARY not competitive."
  This sub-claim survives cross-seed but needs its own pre-reg to be CG-atomized.

cert_increment_delta = 0. 2x-drill recommendation:
  Author a NEW pre-reg specifically testing INT8-vs-FP32 Pareto-optimality at
  M=40k-80k crack with a direct discriminator gate ("INT8 recall_mean >=
  FP32 recall_mean - 0.005 AND INT8 bytes/fact <= 0.30 * FP32 bytes/fact").
  If 3-seed passes -> CG-eligible.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_E_v4_M_ultra_extended_3seed_MM_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_E_v4_MM = {
    "id": (
        "T3/EXP_substrate_bytes_per_fact_pareto_v4_M_ultra_extended_3seed_MM_"
        "META_RULE_Q_ceiling_ESCAPE_0p71_to_0p36_but_cv_0p176_above_0p15_"
        "crack_ordering_TOP4_precisions_EQUIVALENT_within_noise_FP32_BFLOAT16_FP16_RS_INT8_"
        "ordering_flips_cross_seed_INT4_0p01_below_BINARY_0p18_below_SPARSE_floor_"
        "pareto_2x_separation_FALSE_but_tier_1_INT8_Pareto_optimal_sub_claim_CG_eligible_2026-07-01"
    ),
    "name": (
        "MEASURED-MECHANISM bytes_per_fact_pareto v4 M-ultra-extended 3-seed FULL: META_RULE_Q "
        "ceiling ESCAPED (0.714->0.36 mean; cv 0.176 slightly above 0.15). Per-cell MB all 3 "
        "seeds (5/6 gates PASS; pareto_2x False). "
        "CRACK ORDERING NOT CHAIN-GRADE: top-4 precisions (FP32 / BFLOAT16 / FP16_RS / INT8) "
        "are EQUIVALENT within recall noise <0.001 at every M; ordering FLIPS cross-seed within "
        "top-4 (INT8 first for seed_13; FP32 first for seed_7/19). "
        "Clear TIER separations that DO survive cross-seed: Tier1 top-4 fungible / Tier2 INT4 "
        "0.01 below / Tier3 BINARY 0.18 below / Tier4 SPARSE floor. INT8 Pareto-optimal at "
        "M=40k-80k crack (memory 0.25x FP32, recall equivalent) is a CG-ELIGIBLE SUB-CLAIM "
        "if authored with dedicated pre-reg. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL bytes_per_fact_pareto v4 with M-ultra-extension to escape META_RULE_Q "
        "ceiling. M grid = [1k, 4k, 10k, 40k, 80k, 160k]; crack region M=40k-160k. "
        "OFF-DATA recompute: run_mode=full all 3; elapsed 157-158s; cardinality PASS; "
        "positive_control_ok=True all seeds (FP32 recall=1.0); fp16_range_safe_not_collapsed=True "
        "all; int4_valid_tier=True all; monotone_decay_ok=True all; mechanism_hashes_distinct=True "
        "all. Author verdict MB all 3 seeds (5/6 gates PASS; pareto_2x_separation_ok=False). "
        "\n"
        "META_RULE_Q CEILING ESCAPE (primary claim): ceiling_saturation_ratio cross-seed "
        "[0.381, 0.405, 0.286]; mean 0.357; cv 0.176. v3 was 0.714 all 3 seeds; v4 escape "
        "CONFIRMED cross-seed but cv 0.176 above CG threshold 0.15.\n"
        "\n"
        "FULL ARM x M RECALL GRID (mean cross-seed):\n"
        "  Arm          M=1k    M=4k    M=10k   M=40k   M=80k   M=160k\n"
        "  FP32         1.000   1.000   0.995   0.398   0.113   0.031\n"
        "  BFLOAT16     1.000   1.000   0.995   0.397   0.112   0.031\n"
        "  FP16_RS      1.000   1.000   0.995   0.398   0.113   0.031\n"
        "  INT8         1.000   1.000   0.995   0.398   0.113   0.031\n"
        "  INT4         1.000   1.000   0.994   0.387   0.109   0.030\n"
        "  BINARY       1.000   1.000   0.961   0.223   0.059   0.017\n"
        "  SPARSE_0p05  0.837   0.118   0.026   0.002   0.001   0.001\n"
        "\n"
        "CRACK ORDERING ANALYSIS (the framing claim; auditor rejects as CG-quality):\n"
        "  Top-4 precisions EQUIVALENT within noise <0.001 at every M. Ordering FLIPS "
        "cross-seed within top-4:\n"
        "    seed_7  M=40k: FP32=FP16_RS=INT8=0.3858 > BFLOAT16=0.3845\n"
        "    seed_13 M=40k: INT8=0.4008 > BFLOAT16=0.4005 > FP32=FP16_RS=0.4000\n"
        "    seed_19 M=40k: FP32=FP16_RS=0.4073 > BFLOAT16=INT8=0.4058\n"
        "  The Framing 'CRACK ORDER reveals precision hierarchy' is NOT SUPPORTED at "
        "chain-grade quality; instrument noise dominates top-4 ordering. INT8 sometimes "
        "BEATS FP32 (seed_13) which is instrument-level noise, not a signal.\n"
        "\n"
        "CLEAR TIER SEPARATIONS that DO survive cross-seed:\n"
        "  Tier 1 (top-4 fungible): FP32 / BFLOAT16 / FP16_RS / INT8 within 0.001 recall noise\n"
        "  Tier 2 (INT4 slightly below): ~0.01 recall gap vs Tier 1 at M=40-80k\n"
        "  Tier 3 (BINARY at ~0.55x Tier 1): 0.22 vs 0.40 at M=40k (0.18 recall loss)\n"
        "  Tier 4 (SPARSE_BIPOLAR_0p05 floor): near-zero at M >= 40k\n"
        "\n"
        "CANONICAL RULES CHECK:\n"
        "  Per-cell MB (not HP) -> not per-cell CG-eligible.\n"
        "  ceiling_saturation_ratio cv=0.176 slightly above 0.15 CG threshold.\n"
        "  Top-4 ordering NOT consistent cross-seed (instrument noise level).\n"
        "  META_RULE_Q ceiling escape 0.71->0.36 confirmed cross-seed.\n"
        "  META_RULE_H cardinality OK all seeds; positive_control PASS all seeds.\n"
        "  monotone_decay_ok True all; mechanism_hashes_distinct True all.\n"
        "\n"
        "TIER RULING: MEASURED_MECHANISM. Per-cell MB + top-4 ordering instrument-level noise "
        "+ ceiling cv above 0.15 = not CG. But 4 proven precision tiers ARE characterized "
        "cross-seed to instrument-quality precision.\n"
        "\n"
        "CG-ELIGIBLE SUB-CLAIM (needs dedicated pre-reg to atomize as CG):\n"
        "  'At N=8192 in capacity-crack regime M=40k-80k, INT8 is Pareto-optimal (memory 0.25x "
        "FP32; recall equivalent within 0.001). INT4 acceptable for 0.5x additional compression "
        "at 0.01 recall cost. BINARY not competitive at these M levels.'\n"
        "\n"
        "cert_increment_delta = 0. Recommend Director queue 2x-drill: author dedicated pre-reg "
        "with discriminator 'INT8_recall_mean >= FP32_recall_mean - 0.005 AND INT8_bytes_per_fact "
        "<= 0.30 * FP32_bytes_per_fact' at M in {40k, 80k}. If 3-seed HP -> CG-eligible."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM",
        "verdict": "MEASURED_MECHANISM",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (local): "
            "run_mode=full all 3; author MB all 3; 5/6 gates PASS all seeds; pareto_2x False all; "
            "ceiling_saturation_ratio [0.381, 0.405, 0.286] cv=0.176 above 0.15 CG threshold; "
            "top-4 precision recall equivalent within 0.001 noise all M all seeds; ordering "
            "FLIPS cross-seed within top-4 (INT8 first seed_13; FP32 first seed_7/19); "
            "4 clear precision tiers preserved cross-seed at coarser granularity"
        ),
        "regime": {
            "arms": ["FP32_DENSE","BFLOAT16_DENSE","FP16_DENSE_RANGE_SAFE","INT8_DENSE",
                     "INT4_QUANTIZED","BINARY_DENSE","SPARSE_BIPOLAR_0p05"],
            "M_sweep": [1000, 4000, 10000, 40000, 80000, 160000],
            "M_top_saturation_crack": 160000,
            "crack_region": "M=40000_to_160000",
        },
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_bytes_per_fact_pareto_v4_seed_7/metrics.json",
            "seed_13": "data/exp_substrate_bytes_per_fact_pareto_v4_seed_13/metrics.json",
            "seed_19": "data/exp_substrate_bytes_per_fact_pareto_v4_seed_19/metrics.json",
        },
        "ceiling_saturation_ratio_cross_seed": {
            "vals": [0.381, 0.405, 0.286],
            "mean": 0.357,
            "cv": 0.176,
            "v3_baseline": 0.714,
            "escape_confirmed_but_cv_above_CG_threshold": True,
        },
        "crack_ordering_top4_flips_cross_seed": {
            "seed_7_M_40k":  "FP32=FP16_RS=INT8=0.3858 > BFLOAT16=0.3845",
            "seed_13_M_40k": "INT8=0.4008 > BFLOAT16=0.4005 > FP32=FP16_RS=0.4000",
            "seed_19_M_40k": "FP32=FP16_RS=0.4073 > BFLOAT16=INT8=0.4058",
            "noise_dominates_top4_ordering_at_recall_diff_lt_0p001": True,
        },
        "proven_precision_tiers_cross_seed": {
            "Tier_1_top4_fungible": ["FP32_DENSE","BFLOAT16_DENSE","FP16_DENSE_RANGE_SAFE","INT8_DENSE"],
            "Tier_2_INT4_marginal": "INT4_QUANTIZED (~0.01 below Tier 1 at M=40-80k)",
            "Tier_3_BINARY_0p55x_Tier1": "BINARY_DENSE (0.223 vs 0.398 at M=40k)",
            "Tier_4_SPARSE_floor": "SPARSE_BIPOLAR_0p05 (collapses to near-zero at M>=40k)",
        },
        "CG_eligible_sub_claim_needs_dedicated_prereg": (
            "At N=8192 in capacity-crack regime M=40k-80k, INT8 is Pareto-optimal (memory 0.25x "
            "FP32; recall equivalent within 0.001). INT4 acceptable for 0.5x additional "
            "compression at 0.01 recall cost. BINARY not competitive at these M levels."
        ),
        "recommended_2x_drill_discriminator": (
            "INT8_recall_mean >= FP32_recall_mean - 0.005 AND INT8_bytes_per_fact <= 0.30 * "
            "FP32_bytes_per_fact at M in {40k, 80k}; 3-seed HP -> CG-eligible"
        ),
        "author_verdict_MB_confirmed_not_overridden_this_time": True,
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_Q_ceiling_escape_0p71_to_0p36_but_cv_0p176_above_0p15_CG_threshold",
            "META_RULE_H_cardinality_ok_all_seeds",
            "crack_ordering_top4_flips_cross_seed_instrument_noise_dominates_ordering",
            "4_precision_tiers_preserved_cross_seed_at_coarser_granularity",
            "Fix_28_per_arm_metrics_verified_reveals_top4_recall_diff_lt_0p001",
            "auditor_confirms_author_MB_not_overriding_this_time",
            "CG_eligible_sub_claim_INT8_pareto_optimal_needs_dedicated_prereg",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()

ledger_E_v4_MM = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_E_v4_MM['id']}",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization_precision_tiers_META_RULE_Q_escape_partial",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_3seed_MB_META_RULE_Q_escape_0p71_to_0p36_cv_0p176_slightly_above_0p15_CG_threshold_"
        "crack_ordering_top4_FP32_BFLOAT16_FP16_RS_INT8_EQUIVALENT_within_0p001_noise_flips_cross_seed_"
        "4_precision_tiers_preserved_cross_seed_INT8_Pareto_optimal_sub_claim_CG_eligible_with_dedicated_prereg"
    ),
    "cert_increment_delta": 0,
    "cv": 0.176,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_bytes_per_fact_pareto_v4_seed_{7,13,19}/metrics.json",
        "atom_qualified_id": f"math::{atom_E_v4_MM['id']}",
    },
    "supersedes": None,
    "note": (
        "E_v4_bytes_per_fact_pareto_v4_M_ultra_extended_3seed_MM_"
        "META_RULE_Q_ceiling_escape_0p71_to_0p36_but_cv_0p176_above_0p15_CG_threshold_"
        "crack_ordering_top4_precisions_FP32_BFLOAT16_FP16_RS_INT8_all_equivalent_within_0p001_noise_"
        "ordering_flips_cross_seed_INT8_first_seed_13_FP32_first_seed_7_and_19_"
        "4_precision_tiers_preserved_INT4_0p01_below_BINARY_0p18_below_SPARSE_floor_"
        "author_MB_confirmed_not_overridden_pareto_2x_False_all_seeds_"
        "CG_eligible_sub_claim_INT8_Pareto_optimal_at_M_40k_80k_needs_dedicated_prereg_2x_drill_recommended"
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
    append_jsonl_a5(MATH_ATOMS, atom_E_v4_MM,     "math/atoms (E_v4 M-ultra-extended 3-seed MM)")
    append_jsonl_a5(CERT_LEDGER, ledger_E_v4_MM,  "cert_ledger (E_v4 MM)")
    print(f"[A5] DONE OK")
    print(f"[A5] E_v4 3-seed: MM (META_RULE_Q escape confirmed but cv 0.176 above 0.15;")
    print(f"                        top-4 precision ordering flips cross-seed;")
    print(f"                        4 precision tiers preserved; INT8 Pareto sub-claim CG-eligible)")
    print(f"[A5] CERT delta = 0")


if __name__ == "__main__":
    main()
