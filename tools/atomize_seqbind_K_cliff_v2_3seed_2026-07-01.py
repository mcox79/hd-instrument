"""
A5-gated atomize: 2x-drill seqbind K-cliff phase-diagram v2 3-seed MM (2026-07-01)

INDEPENDENT OFF-DATA RECOMPUTE via .venv python:

Per-seed verdict (author): MIDDLE_BAND all 3 seeds; SAT=42-43, MB=7-10, FLOOR=6-7,
                           TRANSITION=12-16 of 72 phase points; K_cliffs=12/12 all seeds.
                           run_mode=full all 3; cardinality 72/72 records 21600/21600 all seeds;
                           arms_identical=False all seeds.

Cross-seed cross-check (skunkworks recompute 2026-07-01):
  K_cliffs_per_combo exact-match cross-seed: 10/12 combos identical (N16384 all 3 Q,
    N2048 all 3 Q, N8192 all 3 Q, N4096_Q4 identical at 200); the 2 disagreements are:
    - N4096_Q1: seed_7=200, seed_13=500, seed_19=200 (cv=0.577; boundary region)
    - N4096_Q2: seed_7=500, seed_13=200, seed_19=200 (cv=0.577; boundary region)
    mean CV across combos = 0.096; max CV = 0.577 (both at N4096, moderate cardinality region)

  Band tallies cv cross-seed:
    n_SAT:  [43, 43, 42] cv=0.014 (essentially identical)
    n_MB:   [10, 7, 10]  cv=0.192 (slightly above CG cv threshold 0.15)
    n_FLOOR:[7, 6, 6]    cv=0.091 (well below)
    n_TRAN: [12, 16, 14] cv=0.143 (just below)

  avg_arms_diff cross-seed: [0.7678, 0.7679, 0.7657] cv=0.00162 (extraordinary reproducibility)

  Per-phase-point band agreement:
    all-3 same band: 61/72 (85%)
    at-least-2 same: 72/72 (100%)
    per-point arms_diff cv: mean=0.061 median=0.006 max=0.750

Positive controls (arms_identical=False all seeds; per_phase point SUBSTRATE > RANDOM=0.0
  = SHUFFLE=0.0 at each SAT point; per-point discriminator fires):
  RANDOM_top1_mean=0.0 and SHUFFLE_top1_mean=0.0 at SAT points across all seeds.
  Clean control-vs-mechanism separation.

Cardinality: 72/72 phase points + 21600/21600 records all seeds; cardinality_ok=True all seeds.

============================================================
TIER DECISION: MEASURED_MECHANISM (strongest possible MM but does not clear CG bar)
============================================================
Rationale:
  (1) Per-cell verdict is MIDDLE_BAND all 3 seeds (author criterion). Chain-grade
      normally requires per-cell HARD_PASS + cross-seed HARD_PASS (cf theta-gamma
      v2 which was HP-per-cell + HP-cross-seed for CG). MB-per-cell means the cell
      itself is not making a chain-grade claim -- the SAT count (60% of phase space)
      trips META_RULE_Q suspect-1.000 and prevents HP promotion.

  (2) HOWEVER: the CROSS-SEED reproducibility is at the CEILING for this instrument:
      - 10/12 K_cliffs exact-match (83%)
      - 61/72 phase points same band all-3 (85%)
      - avg_arms_diff cv=0.00162 (0.2 percent)
      - n_SAT cv=0.014, n_FLOOR cv=0.091, n_TRAN cv=0.143 (all below 0.15)
      - only n_MB cv=0.192 slightly above (MB is the narrowest band by definition)
      - K_cliffs=12/12 fired all seeds
      This is textbook phase-diagram characterization with tight reproducibility.

  (3) The 2 disagreeing cliff combos (N4096 Q1/Q2) are BOTH at the same regime
      boundary -- likely a legitimate cliff-location uncertainty at moderate N,
      not a mechanism instability. This is exactly the kind of boundary region
      one expects in a phase diagram.

  (4) The distinction between this and CG theta-gamma v2:
      - theta-gamma v2: per-cell HP + cross-seed HP + non-saturated discriminator
      - K-cliff v2:     per-cell MB + cross-seed MB + 60% SAT (saturation dominant)
      The mechanism is REAL and REPRODUCIBLE but the axis characterization is
      SATURATION-BOUND, not FREE-DISCRIMINATION.

MM captures this precisely: proven bound (phase diagram characterized with strong
cross-seed evidence; SAT-dominant regime identified; cliff locations reproducible
to 83% exact match; 12/12 cliff combos fire). CERT +0.

2x-DRILL RECOMMENDATION for CG-lift:
  To move MM -> CG, need to reduce SAT-dominance. Options:
  (a) Increase K range floor (test higher K where SUBSTRATE drops below 1.0);
  (b) Reduce N at some Q levels to move phase points into MB/TRANSITION;
  (c) Constrain analysis to non-SAT points only (excluding 42-43 SAT points from
      the axis characterization; then n_MB + n_FLOOR + n_TRANS = 28-30 points
      would need CG-quality cross-seed agreement).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_2x_drill_seqbind_K_cliff_v2_3seed_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_seqbind_MM = {
    "id": (
        "T3/EXP_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_3seed_MM_"
        "phase_characterized_10of12_K_cliffs_exact_match_61of72_band_agreement_"
        "avg_arms_diff_cv_0p0016_SAT_dominant_60pct_META_RULE_Q_2x_drill_CG_recompute_confirmed_2026-07-01"
    ),
    "name": (
        "MEASURED-MECHANISM seqbind K-cliff phase-diagram v2 N in {2048,4096,8192,16384} x Q in {1,2,4} "
        "3-seed FULL: cross-seed phase characterization with strong reproducibility (10/12 K_cliffs "
        "exact-match; 61/72 phase points same band all-3 seeds; avg_arms_diff cv=0.00162; "
        "n_SAT cv=0.014; K_cliffs 12/12 fire all seeds). Per-cell verdict MB all 3 seeds "
        "(SAT=42-43 / MB=7-10 / FLOOR=6-7 / TRANS=12-16 of 72). SAT-dominant 60% of phase space "
        "trips META_RULE_Q -- prevents CG promotion; axis characterization is saturation-bound "
        "not free-discrimination. 2 cliff-combo disagreements (N4096 Q1/Q2) are at boundary "
        "regime with legitimate location-uncertainty. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "3-seed FULL seqbind K-cliff phase-diagram v2 characterization at 72 phase points "
        "(N in {2048,4096,8192,16384} x Q_level in {1,2,4} x K sweep). Per-seed verdict: "
        "MIDDLE_BAND all 3 (author criterion; SAT-count triggers MB tag). "
        "OFF-DATA cross-seed recompute (skunkworks 2026-07-01):\n"
        "  cardinality: 72/72 phase points + 21600/21600 records all seeds; ok=True all.\n"
        "  run_mode=full all 3; elapsed_s=[87.5, 83.7, 98.7]; arms_identical=False all.\n"
        "  K_cliffs_per_combo exact-match: 10/12 (83%); disagreements at N4096_Q1 "
        "(seed_7=200 seed_13=500 seed_19=200; cv=0.577) and N4096_Q2 (seed_7=500 "
        "seed_13=200 seed_19=200; cv=0.577); both at same regime boundary.\n"
        "  Mean cliff-combo cv=0.096; median cv=0.000.\n"
        "  Per-phase-point band agreement: all-3 same=61/72 (85%); at-least-2 same=72/72 (100%).\n"
        "  Per-phase-point arms_diff cv: mean=0.061 median=0.006 max=0.750.\n"
        "  Band tally cv cross-seed: n_SAT [43,43,42] cv=0.014; n_MB [10,7,10] cv=0.192; "
        "n_FLOOR [7,6,6] cv=0.091; n_TRANSITION [12,16,14] cv=0.143.\n"
        "  avg_arms_diff cross-seed: [0.7678, 0.7679, 0.7657] cv=0.00162 (extraordinary).\n"
        "  Positive control: RANDOM_top1=0.0 SHUFFLE_top1=0.0 at all SAT points; clean.\n"
        "  Author verdict MB tag PHASE_DIAGRAM_PARTIAL (seed_7 + seed_19) / PHASE_DIAGRAM_SPARSE (seed_13).\n"
        "\n"
        "TIER RULING: MEASURED_MECHANISM. Rationale: cross-seed reproducibility is at "
        "instrument ceiling (10/12 exact K_cliff match; 85% band-agreement; avg_arms_diff "
        "cv=0.002). BUT per-cell verdict is MB not HP; 60% of phase space is SAT-dominant "
        "which trips META_RULE_Q suspect-1.000 and prevents CG promotion. The mechanism "
        "IS characterized (proven bound: phase diagram with tight cross-seed cliff locations) "
        "but the axis is capacity-bound at low K + moderate N. This is the strongest "
        "possible MM tier -- one step below CG in the ladder. cert_increment_delta=0.\n"
        "\n"
        "2x-DRILL for CG-lift (queue candidate for Director): (a) extend K range above "
        "current ceiling to test where SUBSTRATE_top1 drops below 1.0 across the SAT region; "
        "(b) OR filter to non-SAT phase points and require CG-quality cross-seed agreement "
        "on the 28-30 discriminating points."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM",
        "verdict": "MEASURED_MECHANISM",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on 3 seeds metrics.json (all local): "
            "run_mode=full all 3; cardinality 72/72 phase points + 21600/21600 records all seeds; "
            "K_cliffs_per_combo exact-match 10/12 combos (mean cv=0.096); "
            "61/72 phase points same band all-3; 72/72 at-least-2 same; "
            "avg_arms_diff cv=0.00162; n_SAT cv=0.014; K_cliffs=12/12 all seeds; "
            "arms_identical=False all; RANDOM+SHUFFLE = 0.0 at SAT points (clean control)"
        ),
        "regime": {
            "N_grid": [2048, 4096, 8192, 16384],
            "Q_level_grid": [1, 2, 4],
            "K_sweep": "per_cell_sweep_to_find_cliff",
            "n_phase_points": 72,
            "n_records_per_seed": 21600,
        },
        "per_seed_metrics_paths": {
            "seed_7":  "data/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_7/metrics.json",
            "seed_13": "data/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_13/metrics.json",
            "seed_19": "data/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_19/metrics.json",
        },
        "K_cliffs_per_combo_cross_seed": {
            "N2048_Q1":   [100, 100, 100],
            "N2048_Q2":   [100, 100, 100],
            "N2048_Q4":   [100, 100, 100],
            "N4096_Q1":   [200, 500, 200],
            "N4096_Q2":   [500, 200, 200],
            "N4096_Q4":   [200, 200, 200],
            "N8192_Q1":   [500, 500, 500],
            "N8192_Q2":   [500, 500, 500],
            "N8192_Q4":   [500, 500, 500],
            "N16384_Q1":  [1000, 1000, 1000],
            "N16384_Q2":  [1000, 1000, 1000],
            "N16384_Q4":  [1000, 1000, 1000],
        },
        "K_cliff_exact_match_cross_seed": "10 of 12 combos",
        "K_cliff_disagreements": ["N4096_Q1 (cv=0.577)", "N4096_Q2 (cv=0.577)"],
        "band_tallies_cross_seed": {
            "n_SAT":        {"vals": [43, 43, 42], "cv": 0.014},
            "n_MB":         {"vals": [10, 7, 10],  "cv": 0.192},
            "n_FLOOR":      {"vals": [7, 6, 6],    "cv": 0.091},
            "n_TRANSITION": {"vals": [12, 16, 14], "cv": 0.143},
        },
        "avg_arms_diff_cross_seed": {"vals": [0.7678, 0.7679, 0.7657], "cv": 0.00162},
        "phase_point_all_3_same_band": "61 of 72 (85%)",
        "phase_point_at_least_2_same_band": "72 of 72 (100%)",
        "K_cliffs_fire_all_seeds": "12 of 12",
        "positive_control_random_top1_at_SAT": 0.0,
        "positive_control_shuffle_top1_at_SAT": 0.0,
        "arms_identical_all_seeds": False,
        "meta_rule_Q_tripped": True,
        "meta_rule_Q_saturation_fraction": "42-43 of 72 SAT (58-60%)",
        "meta_rule_H_cardinality_ok": True,
        "chain_grade_lift_drill_recommendation": (
            "Options for MM -> CG: (a) extend K range above SAT ceiling; "
            "(b) filter phase space to non-SAT points (28-30 points) + require CG cross-seed cv."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_Q_SUSPECT_1p000_60pct_saturation_dominant",
            "META_RULE_H_cardinality_ok_72_of_72_all_seeds_21600_records_all_seeds",
            "META_RULE_AF_cross_seed_reproducibility_at_instrument_ceiling_10of12_K_cliffs_exact_match_61of72_band_match",
            "Fix_28_per_arm_metrics_verified",
            "cross_seed_2x_drill_confirmed_seed_7_finding",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_confirmed_at_N_16384_full",
            "stage_3_compositional_understanding_USER_2026-06-26",
            "phase_diagram_action_data_survives_phase_transformations",
        ],
        "supersedes_single_seed_atom": (
            "prior skunkworks landed-VET tiered single-seed as MM per_seed_K_cliff_phase_characterization; "
            "this 3-seed atom confirms and strengthens that ruling with cross-seed evidence"
        ),
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()
ledger_seqbind = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_seqbind_MM['id']}",
    "cert_status": "measured_mechanism",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_3seed_MB_per_cell_MB_cross_seed_phase_diagram_char_10of12_K_cliffs_exact_"
        "match_61of72_band_agreement_avg_arms_diff_cv_0p0016_n_SAT_cv_0p014_SAT_dominant_"
        "60pct_META_RULE_Q_trip_prevents_CG_promotion_axis_capacity_bound"
    ),
    "cert_increment_delta": 0,
    "cv": 0.096,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": "data/exp_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_seed_{7,13,19}/metrics.json",
        "atom_qualified_id": f"math::{atom_seqbind_MM['id']}",
    },
    "supersedes": None,
    "note": (
        "seqbind_K_cliff_v2_3seed_MM_phase_diagram_10of12_K_cliffs_exact_"
        "match_61of72_band_agree_avg_arms_diff_cv_0p0016_n_SAT_cv_0p014_"
        "K_cliffs_12of12_fire_all_seeds_SAT_dominant_60pct_META_RULE_Q_"
        "prevents_CG_axis_saturation_bound_at_low_K_moderate_N_"
        "2x_drill_for_CG_lift_extend_K_range_or_filter_non_SAT_points"
    ),
}


# ============================================================================
# A5 write protocol with Windows os.replace retry
# ============================================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], f"tail id mismatch"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], f"tail atom_id mismatch"

    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] atom_id = math::{atom_seqbind_MM['id']}")
    print(f"[A5] ledger: cert_status={ledger_seqbind['cert_status']} delta={ledger_seqbind['cert_increment_delta']}")

    append_jsonl_a5(MATH_ATOMS, atom_seqbind_MM, "math/atoms.jsonl (seqbind K-cliff v2 3seed MM)")
    append_jsonl_a5(CERT_LEDGER, ledger_seqbind, "meta/cert_ledger.jsonl (seqbind K-cliff v2 3seed MM)")

    print(f"[A5] DONE OK")
    print(f"[A5] seqbind K-cliff v2 3seed: MEASURED_MECHANISM (SAT-dominant META_RULE_Q; strongest MM below CG)")
    print(f"[A5] CERT delta = 0")


if __name__ == "__main__":
    main()
