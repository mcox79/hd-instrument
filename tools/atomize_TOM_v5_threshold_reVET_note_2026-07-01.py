"""
A5-gated atomize: TOM v5 d5_isolated THRESHOLD RE-VET NOTE (no tier change).

Message framing: "MM not CG *only* because of pre-reg threshold choice"; asked
whether amending HP_DEPTH_VAR_MIN 0.10 -> 0.05 lifts to CG.

OFF-DATA VERIFICATION shows this framing IS NOT ACCURATE:
  - v5 pre-reg already had HP_DEPTH_VAR_MIN=0.05 (not 0.10).
  - Under threshold 0.05: 2/3 seeds HP (seed_7 dv=0.0784, seed_13 dv=0.0529);
    seed_19 dv=0.0484 misses by 0.0016 -> MB.
  - Under threshold 0.03: 3/3 seeds HP.
  - BUT: cross-seed cv of TENSOR dv at N=8192 = stdev([0.0784, 0.0529, 0.0484])
    / mean(0.0599) = 0.2701 >> 0.10 CG cv threshold.

REAL BLOCKER for CG is cross-seed cv=0.27, NOT the HP_DEPTH_VAR_MIN threshold.
Even at threshold 0.03 where all 3 seeds pass per-cell, aggregation cv fails.

Prior v5 MM atom (per atoms.jsonl 2026-07-01 tail; qualified id begins with
'math::T3/EXP_substrate_higher_order_tom_recursive_v5_d5_isolated_...') correctly
identified this: "cross-seed cv=0.27 exceeds CG threshold 0.10. CERT +0".
That ruling stands.

The message's proposed threshold amendment (0.10 -> 0.05) was ALREADY REFLECTED
in v5's pre-reg (v5_thresholds shows 0.05); further loosening to 0.03 lifts
per-cell but not cv. Genuine CG lift would require:
  (a) new cell with tighter measurement precision (SE) to lower dv variability
  (b) OR new cell with more seeds (N=5+) to see if cv shrinks with sample size
  (c) OR aggregation at higher N=16384 where dv magnitudes are more stable

This atom records the threshold-sensitivity analysis; no tier change; no
amendment to prior v5 atom's ruling.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_TOM_v5_threshold_reVET_note_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_TOM_v5_threshold_note = {
    "id": (
        "T3/NOTE_TOM_v5_d5_isolated_THRESHOLD_RE_VET_no_tier_change_MM_confirmed_"
        "HP_DEPTH_VAR_MIN_amendment_0p10_to_0p05_ALREADY_reflected_in_v5_prereg_"
        "TENSOR_dv_N_8192_cross_seed_0p0784_0p0529_0p0484_2_of_3_HP_1_MB_at_0p05_threshold_"
        "3_of_3_HP_at_0p03_threshold_BUT_cross_seed_cv_0p27_greater_than_0p10_CG_cv_threshold_"
        "REAL_blocker_is_cross_seed_cv_NOT_HP_DEPTH_VAR_MIN_prior_v5_MM_atom_ruling_stands_2026-07-01"
    ),
    "name": (
        "NOTE TOM v5 d5_isolated threshold re-VET: NO TIER CHANGE. Message framing 'MM not "
        "CG *only* because of pre-reg threshold choice' is not supported by off-data. "
        "HP_DEPTH_VAR_MIN was already 0.05 in v5 pre-reg (not 0.10). TENSOR dv at N=8192 "
        "cross-seed [0.0784, 0.0529, 0.0484]: 2/3 seeds HP at 0.05 threshold, 3/3 at 0.03. "
        "BUT cross-seed cv = 0.2701, well above 0.10 CG cv threshold. Real CG blocker is "
        "cross-seed variability, not HP_DEPTH_VAR_MIN. Prior v5 MM atom ruling (cross-seed "
        "cv exceeds CG threshold 0.10; CERT +0) STANDS. CG lift would require (a) tighter "
        "measurement SE, (b) more seeds N=5+, or (c) aggregation at N=16384 where dv "
        "magnitudes may be more stable."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "amendment_record",
    "description": (
        "Threshold-sensitivity re-VET on TOM v5 d5_isolated (3-seed FULL landed; prior atom "
        "MM in atoms.jsonl 2026-07-01). NO NEW EXPERIMENTAL DATA; NO TIER CHANGE.\n"
        "\n"
        "MESSAGE FRAMING (from Director): 'TENSOR_RANK2 cliff 0.833->0.400->0.167 across "
        "d={1,3,5}; MM not CG *only* because of pre-reg threshold choice; amend 0.10 -> 0.05 "
        "and 0.076 SNR clears HP gate'.\n"
        "\n"
        "OFF-DATA VERIFICATION (skunkworks 2026-07-01):\n"
        "  1. TOM v3 metrics.json = selftest only (elapsed 0.2s; verdict=SELFTEST_OK).\n"
        "     No v3 FULL landed. The referent is v5 d5_isolated (3-seed FULL).\n"
        "  2. v5 pre-reg (2026-06-30_substrate_higher_order_tom_recursive_v5_d5_isolated.md)\n"
        "     already had HP_DEPTH_VAR_MIN=0.05 (per v5_thresholds field in metrics).\n"
        "     The proposed amendment 0.10 -> 0.05 was ALREADY REFLECTED.\n"
        "  3. Per-seed TENSOR dv at N=8192:\n"
        "     seed_7:  0.0784 -> HP at threshold 0.05\n"
        "     seed_13: 0.0529 -> HP at threshold 0.05\n"
        "     seed_19: 0.0484 -> MB at 0.05 (miss by 0.0016)\n"
        "     Cross-seed mean=0.0599 sd=0.0162 cv=0.2701.\n"
        "  4. At threshold 0.03: all 3 seeds pass per-cell (0.0484 > 0.03).\n"
        "  5. CROSS-SEED CV = 0.2701 >> 0.10 CG cv threshold (typical) or 0.15 (permissive).\n"
        "     This is the REAL CG blocker, not HP_DEPTH_VAR_MIN.\n"
        "\n"
        "PRIOR v5 MM ATOM CORRECTLY IDENTIFIED THIS:\n"
        "  Per atoms.jsonl 2026-07-01 tail: 'TOM v5 d=5-isolated (3-seed 2 HP + 1 MB): "
        "TENSOR mechanism separates from BOW at N=4096-8192... cross-seed cv=0.27 exceeds "
        "CG threshold 0.10. CERT +0'. That ruling is correct; this note confirms.\n"
        "\n"
        "TIER: NO CHANGE. MM tier from prior v5 atom stands. cert_increment_delta = 0.\n"
        "\n"
        "PATH TO CG (if desired):\n"
        "  (a) New cell with tighter measurement SE (v5 shows SE=0.0000 per seed but cross-\n"
        "      seed variability is real; SE is per-seed not aggregation).\n"
        "  (b) New cell with N_seeds >= 5 to see if cv shrinks with sample size.\n"
        "  (c) Aggregation at N=16384 where dv magnitudes may be more stable (v5 shows\n"
        "      seed_19 N=16384 TENSOR dv=0.075 -- higher and more stable).\n"
        "\n"
        "This is a genuine mechanism characterization (TENSOR discriminates from BOW; depth-\n"
        "awareness is measured cross-seed), but per-cell verdict + aggregation cv both need\n"
        "improvement for CG-eligibility. Not a threshold-choice artifact."
    ),
    "metadata": {
        "provenance_quality": "AMENDMENT_RECORD_NO_TIER_CHANGE",
        "verdict": "NO_TIER_CHANGE_MM_confirmed",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA verification via .venv python: v5 3-seed metrics.json all local; "
            "v5_thresholds field shows HP_DEPTH_VAR_MIN=0.05 already (not 0.10 as message "
            "framed); TENSOR dv at N=8192 [0.0784, 0.0529, 0.0484]; cross-seed cv=0.2701; "
            "seed_7+seed_13 HP at threshold 0.05, seed_19 MB at 0.05; all 3 HP at threshold "
            "0.03; real CG blocker is cross-seed cv=0.27 not HP_DEPTH_VAR_MIN threshold"
        ),
        "amends_atom_prefix_referent": (
            "math::T3/EXP_substrate_higher_order_tom_recursive_v5_d5_isolated_3seed_MM_"
            "TENSOR_decay_with_N_distractor_budget_dominates"
        ),
        "message_framing_correction": {
            "message_claim": "MM not CG *only* because of pre-reg threshold choice (0.10 -> 0.05 would lift)",
            "off_data_reality_1": "v5 pre-reg already had HP_DEPTH_VAR_MIN=0.05 (not 0.10)",
            "off_data_reality_2": "at threshold 0.05: 2/3 HP; at 0.03: 3/3 HP",
            "off_data_reality_3": "cross-seed cv=0.2701 >> 0.10 CG cv threshold",
            "conclusion": "real CG blocker is cross-seed cv, not HP_DEPTH_VAR_MIN",
        },
        "TENSOR_dv_at_N_8192_cross_seed": {
            "seed_7":  0.0784,
            "seed_13": 0.0529,
            "seed_19": 0.0484,
            "mean": 0.0599,
            "sd": 0.0162,
            "cv": 0.2701,
        },
        "BOW_dv_at_N_8192_cross_seed": [0.0020, 0.0016, 0.0006],
        "TENSOR_vs_BOW_separation_clean_all_seeds": True,
        "at_threshold_0p05_per_seed_verdict": [
            "seed_7=HP", "seed_13=HP", "seed_19=MB_by_0p0016",
        ],
        "at_threshold_0p03_per_seed_verdict": [
            "seed_7=HP", "seed_13=HP", "seed_19=HP",
        ],
        "cross_seed_cv_0p2701_blocks_CG_regardless_of_HP_DEPTH_VAR_MIN_choice": True,
        "path_to_CG_if_desired": {
            "(a)_tighter_measurement_SE_new_cell": "reduce cross-seed variability at measurement level",
            "(b)_N_seeds_ge_5_new_cell": "see if cv shrinks with sample size",
            "(c)_aggregation_at_N_16384": "v5 seed_19 N=16384 TENSOR dv=0.075 higher and more stable",
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "amendment_record_threshold_re_VET_no_tier_change",
            "message_framing_correction_HP_DEPTH_VAR_MIN_already_0p05_not_0p10",
            "real_CG_blocker_cross_seed_cv_0p27_not_threshold_choice",
            "prior_v5_MM_atom_ruling_stands_correctly_identified_cv_blocker",
            "path_to_CG_specified_measurement_SE_or_more_seeds_or_higher_N",
            "Fix_28_per_arm_metrics_verified_off_data",
            "auditor_verify_the_referent_message_framed_v3_but_actual_data_is_v5",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW (no delta; amendment record)
# ============================================================================
_t0 = time.time()

ledger_TOM_v5_threshold_note = {
    "ts": _t0,
    "op": "cert_amendment",
    "atom_id": f"math::{atom_TOM_v5_threshold_note['id']}",
    "cert_status": "amendment_record_no_status_change",
    "cert_class": "threshold_re_VET_amendment_message_framing_correction_no_tier_change",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "NO_TIER_CHANGE_message_framing_HP_DEPTH_VAR_MIN_0p10_to_0p05_amendment_ALREADY_reflected_in_v5_prereg_"
        "TENSOR_dv_N_8192_2_of_3_HP_at_0p05_3_of_3_HP_at_0p03_BUT_cross_seed_cv_0p27_greater_than_0p10_CG_cv_threshold_"
        "real_blocker_is_cross_seed_variability_not_threshold_choice_prior_v5_MM_atom_ruling_stands"
    ),
    "cert_increment_delta": 0,
    "cv": 0.2701,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_higher_order_tom_recursive_v5_d5_isolated_seed_{7,13,19}/metrics.json",
        "atom_qualified_id": f"math::{atom_TOM_v5_threshold_note['id']}",
        "amends_prior_atom_prefix": (
            "math::T3/EXP_substrate_higher_order_tom_recursive_v5_d5_isolated_3seed_MM_"
        ),
    },
    "supersedes": None,
    "note": (
        "TOM_v5_d5_isolated_threshold_re_VET_note_no_tier_change_"
        "message_framed_v3_but_actual_referent_v5_which_already_had_threshold_0p05_"
        "TENSOR_dv_N_8192_cross_seed_0p0784_0p0529_0p0484_mean_0p0599_cv_0p2701_"
        "at_threshold_0p05_2_of_3_HP_1_MB_by_0p0016_at_threshold_0p03_3_of_3_HP_"
        "cross_seed_cv_0p27_blocks_CG_regardless_of_HP_DEPTH_VAR_MIN_choice_"
        "real_CG_blocker_is_cross_seed_variability_not_threshold_"
        "prior_v5_MM_atom_correctly_identified_cv_blocker_ruling_stands_"
        "path_to_CG_tighter_SE_or_N_seeds_ge_5_or_N_16384_aggregation"
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
    append_jsonl_a5(MATH_ATOMS, atom_TOM_v5_threshold_note,     "math/atoms (TOM v5 threshold re-VET note)")
    append_jsonl_a5(CERT_LEDGER, ledger_TOM_v5_threshold_note,  "cert_ledger (TOM v5 threshold note)")
    print(f"[A5] DONE OK")
    print(f"[A5] TOM v5 threshold re-VET: NO TIER CHANGE")
    print(f"[A5] Message framing HP_DEPTH_VAR_MIN 0.10->0.05 was already reflected in v5 pre-reg")
    print(f"[A5] Real CG blocker is cross-seed cv=0.27, not threshold choice")
    print(f"[A5] Prior v5 MM atom ruling stands")
    print(f"[A5] CERT delta = 0")


if __name__ == "__main__":
    main()
