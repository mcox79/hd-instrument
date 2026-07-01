"""
A5-gated atomize: Axis F cleanup_family_WM_K_cliff v2 arm4 b3k3 smoke HARD_FAIL closure

INDEPENDENT OFF-DATA RECOMPUTE via .venv python (skunkworks 2026-07-01):

Cell: experiments/_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_core.py
Prereg: preregs/2026-07-01_substrate_cleanup_family_WM_K_cliff_v1.md
Metrics: data/exp_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_seed_7_smoke/metrics.json

Config: N=8192, num_banks=4 (arm4 smoke), K in {1024, 2048}, K_cliff_B=256*B=1024,
        beta=8.0, hop_max_steps=4, encoder=bipolar, cleanups=[classical_hopfield,
        modern_hopfield_continuous, iterative_attractor, wta_baseline].

Off-data verification:
  run_mode=smoke; elapsed_s=593.5 (substantial compute); seed=7
  cardinality: 8/8 phase points (per_seed 8/8 ok=True); expected_n_smoke=8 -- match
  tier_counts: SATURATED=0 HARD_PASS=0 MIDDLE_BAND=0 FLOOR=8 HARD_FAIL=0 (all-floor)

Per-family recall @ K=1024 (K_cliff, K_ratio=1.0):
  classical_hopfield:          0.0020
  modern_hopfield_continuous:  0.0474
  iterative_attractor:         0.0530
  wta_baseline:                0.0486

Per-family recall @ K=2048 (2*K_cliff, K_ratio=2.0):
  classical_hopfield:          0.0007
  modern_hopfield_continuous:  0.0125
  iterative_attractor:         0.0114
  wta_baseline:                0.0107

Discriminator at K=2*K_cliff, num_banks=4:
  wta_baseline mean:            0.0107
  lifts_over_wta:
    classical_hopfield:         -0.0100 (below wta)
    modern_hopfield_continuous: +0.0018 (best; 55x below +0.10 gate)
    iterative_attractor:        +0.0007 (near zero)
  best_lift = 0.0018 vs required 0.10 gate -> DISCRIMINATOR FAILS SCALE
  discriminator_fires_seed_consistent = False (n_B_seed_consistent_fires=0)

Positive control (route_acc = 1.0 all 8 phase points):
  Routing works perfectly; failure is at cleanup stage, not upstream binding/routing.
  This isolates the finding: cleanup-family capability is the bottleneck, not
  routing or binding.

Mechanistic distinctness (META_RULE_AX):
  6/6 cleanup pairs pred_distinct + 6/6 mech_distinct at BOTH K=1024 and K=2048.
  Arms are MECHANISTICALLY DIFFERENT but ALL FLOOR TOGETHER.
  This is the strongest possible honest-negative form: the 4 families are not
  degenerate variants of each other; they are genuinely different mechanisms,
  and they ALL fail at WM scale K in {1024, 2048}.

Cell-author honest-abort:
  smoke_gate_pass=False; cell aborts FULL dispatch per
  DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26.
  No FULL run authorized. This is textbook honest-negative closure.

============================================================
TIER RULING: HARD_FAIL (honest_negative capability_orthogonal_across_scales)
============================================================
Rationale:
  (1) best_lift = 0.0018 is 55x below the +0.10 discriminator gate. Not a
      MIDDLE_BAND. Not a MEASURED_MECHANISM. This is a clean negative:
      cleanup families do not lift over wta_baseline at WM scale.

  (2) Mechanistic distinctness holds (6/6 pairs pred+mech distinct); the 4
      families are genuinely different mechanisms. Their common floor is not
      a degenerate-arm artifact -- it is a REAL capability bound.

  (3) Cross-scale composition with a009a44a (cleanup_family PC MB atom):
      - PC scale (cleanup as PC-cleanup): MB single-seed
      - WM scale (this atom; cleanup as WM-cleanup at K=1024/2048): HF all-floor
      Two-drill closure ACROSS SCALES: cleanup families are not the axis that
      lifts WM capacity. The finding replicates the PC-scale characterization
      and extends it: at WM scale where more capacity is needed, all 4 families
      collapse to floor.

  (4) route_acc=1.0 all points isolates the finding cleanly: routing +
      binding are healthy; the bottleneck is specifically the cleanup stage
      when the number of stored items exceeds K_cliff.

  (5) Cell-author correctly honest-aborted at smoke; no wasted FULL compute.
      This is exactly the discipline META_RULE_AV + DISCRIMINATOR_MUST_SURVIVE
      _SCALE were designed to enforce.

Single-seed smoke abort is CORRECT + SUFFICIENT here: when discriminator fails
by 55x margin at smoke, cross-seed replication would waste compute without
changing the ruling. Per USER discipline "smoke must FIRE discriminator", the
signal is clear.

cert_increment_delta = 0 (honest negative; not a chain-grade demote since no
prior CG existed on this axis).

2x-DRILL CLOSURE STATUS:
  - PC-scale cleanup family (a009a44a): MB single-seed characterization
  - WM-scale cleanup family (this atom): HF smoke-abort at K=1024/2048
  Composition: cleanup-family axis is CAPABILITY-ORTHOGONAL to WM lift.
  Do NOT re-explore cleanup-family variants for WM lift without a revival angle
  (e.g., structurally different cleanup class, or K < K_cliff regime with
  different discriminator).

Discipline tags:
  - META_RULE_AV_discriminator_fails_scale (fires as designed)
  - META_RULE_AX_distinctness_pass_arms_mechanistically_different
  - DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26 (honest-abort discipline works)
  - honest_negative_composes_with_prior_MB_atom_a009a44a
  - stage_3_compositional_understanding_USER_2026-06-26
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_landed_VET_axis_F_cleanup_family_wm_kcliff_v2_HF_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_axis_F_HF = {
    "id": (
        "T3/EXP_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_seed_7_smoke_HARD_FAIL_"
        "honest_negative_capability_orthogonal_across_scales_all_4_families_FLOOR_at_K_1024_and_2048_"
        "best_lift_0p0018_vs_gate_0p10_55x_below_composes_with_PC_scale_MB_a009a44a_2x_drill_closure_2026-07-01"
    ),
    "name": (
        "HARD_FAIL Axis F cleanup_family_WM_K_cliff v2 arm4 (B=4) smoke seed_7: all 4 cleanup "
        "families (classical_hopfield / modern_hopfield_continuous / iterative_attractor / wta_baseline) "
        "FLOOR at K=1024 (K_cliff) and K=2048 (2*K_cliff); best lift over wta = 0.0018 (55x below "
        "+0.10 discriminator gate); tier_counts FLOOR=8/8. Mechanistic distinctness holds "
        "(6/6 pairs pred+mech distinct at both K); arms are genuinely different mechanisms but all "
        "collapse to floor together. route_acc=1.0 all points (routing+binding healthy; cleanup is "
        "the bottleneck). Cell-author honest-abort per DISCRIMINATOR_MUST_SURVIVE_SCALE; no FULL "
        "dispatch. Composes with cleanup family PC scale MB atom (a009a44a) as 2x-drill closure "
        "across scales: cleanup-family axis is CAPABILITY-ORTHOGONAL to WM lift. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "Axis F cleanup_family_WM_K_cliff v2 arm4 (num_banks=4 smoke) seed_7 at N=8192, "
        "K in {1024, 2048}, K_cliff_B=256*B=1024, beta=8.0, hop_max_steps=4, encoder=bipolar. "
        "OFF-DATA verification: run_mode=smoke; elapsed_s=593.5; cardinality 8/8 phase points. "
        "tier_counts SAT=0 HP=0 MB=0 FLOOR=8 HF=0 -- all-floor. "
        "Per-family recall @ K=1024: classical_hopfield=0.0020, modern_hopfield_continuous=0.0474, "
        "iterative_attractor=0.0530, wta_baseline=0.0486. "
        "Per-family recall @ K=2048: classical_hopfield=0.0007, modern_hopfield_continuous=0.0125, "
        "iterative_attractor=0.0114, wta_baseline=0.0107. "
        "Discriminator @ K=2*K_cliff, B=4: wta_baseline mean=0.0107; lifts over wta = "
        "{classical: -0.0100, modern_continuous: +0.0018, iterative: +0.0007}; best_lift=0.0018 "
        "vs required +0.10 gate = 55x below. discriminator_fires_seed_consistent=False. "
        "Mechanistic distinctness: 6/6 pred_pair_distinct + 6/6 mech_pair_distinct at both K "
        "values -- arms are genuinely different mechanisms, not degenerate variants. "
        "Positive control: route_acc=1.0 at ALL 8 phase points -- routing+binding are healthy; "
        "the bottleneck is cleanup at K >= K_cliff. Cell-author correctly honest-aborted per "
        "smoke_gate_pass=False; no FULL dispatch. "
        "\n"
        "COMPOSITION WITH PRIOR ATOM: a009a44a (cleanup_family PC-scale MB atom) established "
        "single-seed MB for cleanup families at PC scale. This atom extends the finding to WM "
        "scale where more capacity is needed: all 4 families collapse to floor. Two-drill closure "
        "across scales: cleanup-family axis is CAPABILITY-ORTHOGONAL to WM lift. "
        "\n"
        "TIER RULING: HARD_FAIL (honest_negative capability_orthogonal_across_scales). "
        "Single-seed smoke abort is CORRECT and SUFFICIENT here: 55x margin below discriminator "
        "gate means cross-seed replication would waste compute without changing ruling. "
        "cert_increment_delta=0. Do NOT re-explore cleanup-family variants for WM lift without "
        "a revival angle (e.g., structurally different cleanup class, or K < K_cliff regime)."
    ),
    "metadata": {
        "provenance_quality": "HARD_FAIL",
        "verdict": "HARD_FAIL",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on smoke metrics.json: "
            "run_mode=smoke; cardinality 8/8; all 8 phase points FLOOR; "
            "best_lift over wta = 0.0018 vs +0.10 gate (55x below); "
            "6/6 pairs pred+mech distinct (arms mechanistically different); "
            "route_acc=1.0 all points (routing+binding healthy); "
            "discriminator_fires_seed_consistent=False; smoke_gate_pass=False; "
            "cell-author honest-abort per DISCRIMINATOR_MUST_SURVIVE_SCALE"
        ),
        "regime": {
            "N": 8192,
            "num_banks_smoke": 4,
            "K_grid": [1024, 2048],
            "K_cliff_B": 1024,
            "K_cliff_formula": "256 * B",
            "beta": 8.0,
            "hop_max_steps": 4,
            "encoder": "bipolar",
            "cleanup_families": [
                "classical_hopfield",
                "modern_hopfield_continuous",
                "iterative_attractor",
                "wta_baseline",
            ],
        },
        "metrics_path": (
            "data/exp_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_seed_7_smoke/metrics.json"
        ),
        "cell_path": (
            "experiments/_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_core.py"
        ),
        "prereg_path": "preregs/2026-07-01_substrate_cleanup_family_WM_K_cliff_v1.md",
        "per_family_recall_at_K_cliff": {
            "classical_hopfield": 0.0020,
            "modern_hopfield_continuous": 0.0474,
            "iterative_attractor": 0.0530,
            "wta_baseline": 0.0486,
        },
        "per_family_recall_at_2x_K_cliff": {
            "classical_hopfield": 0.0007,
            "modern_hopfield_continuous": 0.0125,
            "iterative_attractor": 0.0114,
            "wta_baseline": 0.0107,
        },
        "discriminator": {
            "K_disc": 2048,
            "wta_mean": 0.0107,
            "lifts_over_wta": {
                "classical_hopfield": -0.0100,
                "modern_hopfield_continuous": 0.0018,
                "iterative_attractor": 0.0007,
            },
            "best_fam": "modern_hopfield_continuous",
            "best_lift": 0.0018,
            "required_gate": 0.10,
            "margin_below_gate_x": 55.5,
            "fires_seed_consistent": False,
        },
        "positive_control_route_acc_all_points": 1.0,
        "positive_control_isolates_cleanup_as_bottleneck": True,
        "mech_distinctness_pass": {
            "n_pairs_pred_differ": 6,
            "n_pairs_mech_differ": 6,
            "n_pairs_total": 6,
            "self_report_pass": True,
        },
        "smoke_gate_pass": False,
        "smoke_gate_reason": (
            "DISCRIMINATOR_FAILS_SCALE: no B produced lift >= 0.10 above wta_baseline "
            "at K=2*K_cliff; max_lifts_per_B={4: 0.0018}; cleanup family capability-orthogonal "
            "at WM scale even at smoke; ABORT full dispatch"
        ),
        "cell_author_honest_abort": True,
        "composes_with_prior_atom": {
            "atom_id_prefix": "a009a44a",
            "note": (
                "cleanup family PC-scale MB atom (a009a44a) established single-seed MB at PC "
                "scale; this atom extends to WM scale where all 4 families collapse to floor. "
                "Two-drill closure across scales: cleanup-family axis is CAPABILITY-ORTHOGONAL "
                "to WM lift."
            ),
        },
        "two_drill_closure_across_scales": True,
        "capability_closure_status": (
            "CLEANUP_FAMILY_AXIS_CAPABILITY_ORTHOGONAL_TO_WM_LIFT_CLOSED_across_PC_scale_MB_and_WM_scale_HF"
        ),
        "do_not_reexplore_without_revival_angle": True,
        "revival_angles": [
            "structurally_different_cleanup_class_e_g_sparse_distributed_memory",
            "K_below_K_cliff_regime_with_different_discriminator",
            "N_scaling_to_test_if_larger_N_shifts_K_cliff_and_relieves_the_bound",
        ],
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AV_discriminator_fails_scale_fires_as_designed",
            "META_RULE_AX_distinctness_pass_arms_mechanistically_different_but_all_floor",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26_honest_abort_discipline_works",
            "smoke_must_fire_discriminator_USER_2026-06-26",
            "META_RULE_H_cardinality_ok_8_of_8",
            "Fix_28_per_arm_metrics_verified",
            "honest_negative_composes_with_prior_MB_atom_a009a44a_2x_drill_closure_across_scales",
            "capability_orthogonality_closure",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "single_seed_smoke_abort_correct_and_sufficient": True,
        "single_seed_abort_rationale": (
            "best_lift 55x below discriminator gate at smoke; cross-seed replication would "
            "waste compute without changing ruling. Per USER discipline 'smoke must FIRE "
            "discriminator', the signal is clear at single-seed smoke."
        ),
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()
ledger_axis_F_HF = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_axis_F_HF['id']}",
    "cert_status": "hard_fail",
    "cert_class": "honest_negative_capability_orthogonal_across_scales",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "HARD_FAIL_smoke_seed_7_all_4_cleanup_families_FLOOR_at_K_1024_and_2048_"
        "best_lift_0p0018_vs_gate_0p10_55x_below_route_acc_1p0_isolates_cleanup_as_bottleneck_"
        "mechanistic_distinctness_pass_arms_genuinely_different_but_all_floor_together_"
        "cell_author_honest_abort_no_FULL_dispatch_composes_with_PC_scale_MB_a009a44a_2x_drill_closure"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_path": (
            "data/exp_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_seed_7_smoke/metrics.json"
        ),
        "cell_path": (
            "experiments/_substrate_cleanup_family_wm_kcliff_v2_arm4_b3k3_core.py"
        ),
        "prereg_path": "preregs/2026-07-01_substrate_cleanup_family_WM_K_cliff_v1.md",
        "atom_qualified_id": f"math::{atom_axis_F_HF['id']}",
        "composes_with_atom": "a009a44a cleanup_family PC-scale MB single-seed",
    },
    "supersedes": None,
    "note": (
        "axis_F_cleanup_family_WM_K_cliff_v2_arm4_smoke_HF_honest_negative_"
        "all_4_families_FLOOR_at_K_cliff_and_2x_K_cliff_best_lift_0p0018_55x_below_gate_"
        "route_acc_1p0_isolates_cleanup_as_bottleneck_mechanistic_distinctness_6of6_pairs_pred_and_mech_"
        "arms_genuinely_different_but_all_floor_together_cell_author_honest_abort_"
        "DISCRIMINATOR_MUST_SURVIVE_SCALE_discipline_works_composes_with_a009a44a_PC_MB_"
        "2x_drill_closure_across_scales_capability_orthogonal_do_not_reexplore_without_revival_angle"
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
    print(f"[A5] atom_id = math::{atom_axis_F_HF['id']}")
    print(f"[A5] ledger: cert_status={ledger_axis_F_HF['cert_status']} delta={ledger_axis_F_HF['cert_increment_delta']}")

    append_jsonl_a5(MATH_ATOMS, atom_axis_F_HF, "math/atoms.jsonl (axis F cleanup_family WM K_cliff v2 HF)")
    append_jsonl_a5(CERT_LEDGER, ledger_axis_F_HF, "meta/cert_ledger.jsonl (axis F cleanup_family WM K_cliff v2 HF)")

    print(f"[A5] DONE OK")
    print(f"[A5] Axis F cleanup_family_WM_K_cliff v2 arm4 smoke: HARD_FAIL (honest_negative)")
    print(f"[A5] Composes with a009a44a PC-scale MB as 2x-drill closure across scales")
    print(f"[A5] Capability orthogonality: cleanup-family axis is NOT the WM-lift axis")
    print(f"[A5] CERT delta = 0")


if __name__ == "__main__":
    main()
