"""
A5-gated atomize: META SYNTHESIS atom composing D×O + Axis J findings.

FINDING: binding-family capability invariance on capacity axis at WM regime.

Two orthogonal binding-family axes independently show:
  - K_cliff / K* (capacity LOCATION) is INVARIANT to binding-op family choice
  - top1 recall (performance LEVEL) DIFFERS across ops within each axis

EVIDENCE COMPOSITION:

Axis D×O (binding_op_x_capacity v1, 3-seed FULL):
  Ops: HADAMARD_BIND, CIRCULAR_CONV_HRR, FHRR_COMPLEX_MUL
  Per-seed cross-op K_cliff at alpha=0.5:
    All 9 cells (3 ops x 3 seeds): K_cliff = 750 IDENTICAL
    All 9 K_cliff_shift_from_ref = 0.0 IDENTICAL
  Cross-seed mean top1 at alpha=0.5:
    HADAMARD_BIND:      mean=0.289 sd=0.038
    CIRCULAR_CONV_HRR:  mean=0.300 sd=0.088
    FHRR_COMPLEX_MUL:   mean=0.800 sd=0.067
    Performance range: 0.29 -> 0.80 = 2.7x span; FHRR dominates.
  Positive control (HADAMARD alpha=0.1 M=150 top1=1.0) PASS all 3 seeds.
  Referent: math::T3/EXP_substrate_binding_op_x_capacity_v1_3seed_HARD_FAIL... (3197b903)

Axis J (order_binding_family v1, 2-seed FULL; seed_7 phantom-runner):
  Ops: CYCLIC_SHIFT, RANDOM_PERMUTATION, PHASE_ROTATION
  Per-seed cross-op K* at N=8192:
    All 6 cells (3 ops x 2 completed seeds): K* = 500 IDENTICAL
    All 6 K_star_log10_sep_pairs = 0.0 IDENTICAL
  Mechanistic distinctness holds: 3/3 pair-wise bundle+positions distinctness both seeds.
  Positive control (CYCLIC_SHIFT K=50 top1=1.0) PASS both completed seeds.
  Referent: math::T3/EXP_substrate_order_binding_family_v1_2seed_HARD_FAIL... (c7feb0c4)

SYNTHESIS CLAIM:
  Binding-family operation choice does NOT shift capacity location (K_cliff, K*)
  at WM regime. Substrate WM capacity is determined by (N, K, alpha, codebook
  geometry) NOT by binding-family choice within either axis (bind-op OR order-op).
  Binding-family choice DOES affect performance level (recall) but through
  NOISE-GEOMETRY not CAPACITY-CEILING.

  Substrate design implication: pick binding-family for performance regime, not
  for capacity extension. FHRR dominates recall at moderate K; HAD/CIR are
  cleaner asymptotic; ORDER-family (cyclic/permutation/phase) is fungible on
  capacity but may differ on downstream compositional properties.

TIERING RATIONALE:
  Evidence STRENGTH:
    - 9/9 D×O cells at K_cliff=750 shift=0.0 across 3 seeds (STRONG cross-seed)
    - 6/6 Axis J cells at K*=500 log10_sep=0.0 across 2 seeds (STRONG within-axis;
      seed_7 phantom-runner blocks 3-seed replication)
    - Both axes independently confirm the pattern (STRONG axis-orthogonality)

  Evidence LIMITATIONS:
    - Only 3 ops per axis; the "family" is under-sampled
    - Axis J is 2-seed not 3-seed (phantom-runner infrastructure block)
    - Only WM regime tested; not multi-regime (PC / narrow-K / wide-K)
    - No structurally-different binding-class tested (e.g., graph-op, tensor-order)

  RULING: MM_TENTATIVE_SYNTHESIS (mechanism_characterization).
  This is a REAL cross-axis pattern (0.0 shift EVERYWHERE tested) but the meta
  claim rests on a narrow test surface. TENTATIVE tag signals:
    - the finding IS characterized within the tested surface
    - expansion criteria are specified below
    - not eligible for CG until expansion criteria are met

  EXPANSION CRITERIA (any of the following elevates MM_TENTATIVE -> MM_STANDARD;
  all three would enable CG-eligibility with a proper pre-reg):
    (a) Axis J seed_7 completes and matches K*=500 (3-seed instead of 2-seed)
    (b) At least 5 ops tested on at least one axis (currently 3)
    (c) A structurally-DIFFERENT binding class (e.g., graph-tensor, non-commutative)
        tested and shows same capacity-invariance

  cert_increment_delta = 0.

COMPOSES:
  This atom composes and cross-links two prior HF atoms:
  - math::T3/EXP_substrate_binding_op_x_capacity_v1_3seed_HARD_FAIL... (3197b903)
  - math::T3/EXP_substrate_order_binding_family_v1_2seed_HARD_FAIL... (c7feb0c4)

  Neither prior atom is superseded; this atom AMENDS them with meta-level context.
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_META_synthesis_binding_family_capacity_invariance_2026-07-01"
ATOMIZED_DATE = "2026-07-01"

atom_META_SYNTHESIS = {
    "id": (
        "T3/META_synthesis_binding_family_capability_invariance_capacity_axis_at_WM_regime_"
        "MM_TENTATIVE_composes_D_x_O_binding_op_3seed_HF_and_axis_J_order_binding_2seed_HF_"
        "K_cliff_and_K_star_INVARIANT_across_9_of_9_binding_op_cells_and_6_of_6_order_op_cells_"
        "shift_0p0_everywhere_performance_top1_DIFFERS_2p7x_HAD_0p29_CIR_0p30_FHRR_0p80_"
        "expansion_criteria_seed_7_completion_5_ops_per_axis_new_binding_class_2026-07-01"
    ),
    "name": (
        "MM_TENTATIVE META SYNTHESIS: binding-family capability invariance on capacity axis "
        "at WM regime. Two orthogonal binding-family axes (D-x-O binding_op + Axis J order_op) "
        "independently show K_cliff/K* location INVARIANT to op-family choice within each axis "
        "(9/9 D-x-O cells at K_cliff=750 shift=0.0; 6/6 Axis J cells at K*=500 log10_sep=0.0), "
        "while top1 recall level DIFFERS meaningfully (D-x-O: HAD 0.29 / CIR 0.30 / FHRR 0.80 "
        "cross-seed means at alpha=0.5). Substrate WM capacity is determined by (N, K, alpha, "
        "codebook geometry), NOT by binding-family choice; binding-family affects noise geometry, "
        "not capacity ceiling. TENTATIVE per 3-op-per-axis narrow surface + Axis J 2-seed "
        "(seed_7 phantom-runner). Expansion criteria: Axis J seed_7 completion + >=5 ops per "
        "axis + structurally-different binding class. CERT +0."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "synthesis_meta_finding",
    "description": (
        "META SYNTHESIS atom composing two independent axis findings:\n"
        "\n"
        "AXIS D-x-O (binding_op_x_capacity v1, 3-seed FULL, ref atom 3197b903):\n"
        "  Ops tested: HADAMARD_BIND / CIRCULAR_CONV_HRR / FHRR_COMPLEX_MUL\n"
        "  K_cliff per op per seed at alpha=0.5: ALL 9 cells (3 ops x 3 seeds) = 750 IDENTICAL\n"
        "  K_cliff_shift_from_ref: ALL 9 cells = 0.0 IDENTICAL\n"
        "  top1 at alpha=0.5 cross-seed mean: HAD=0.289 (sd 0.038) / CIR=0.300 (sd 0.088) / "
        "FHRR=0.800 (sd 0.067). Performance range 2.7x; FHRR dominates.\n"
        "  Positive control PASS all 3 seeds (HAD alpha=0.1 M=150 top1=1.0).\n"
        "\n"
        "AXIS J (order_binding_family v1, 2-seed FULL, ref atom c7feb0c4):\n"
        "  Ops tested: CYCLIC_SHIFT / RANDOM_PERMUTATION / PHASE_ROTATION\n"
        "  K* per op per seed at N=8192: ALL 6 cells (3 ops x 2 completed seeds) = 500 IDENTICAL\n"
        "  K_star_log10_sep_pairs: ALL 6 pair-cells = 0.0 IDENTICAL\n"
        "  Mechanistic distinctness holds: 3/3 pair-wise bundle+positions distinctness both seeds.\n"
        "  Positive control PASS both completed seeds (CYCLIC K=50 top1=1.0).\n"
        "  seed_7 phantom-runner (0.15s elapsed stuck); infrastructure block; 3-seed replication "
        "pending Testbed unblock.\n"
        "\n"
        "SYNTHESIS CLAIM: binding-operation choice within a family axis (bind-op OR order-op) "
        "does NOT shift capacity location (K_cliff, K*) at WM regime. Substrate WM capacity is "
        "determined by (N, K, alpha, codebook geometry). Binding-family choice affects "
        "performance LEVEL through noise geometry, NOT capacity CEILING.\n"
        "\n"
        "SUBSTRATE DESIGN IMPLICATION: at chain-grade scale, pick binding-family for "
        "performance regime (FHRR dominates recall at moderate K; HAD/CIR asymptotic behavior; "
        "ORDER-family fungible on capacity but may differ on downstream compositional "
        "properties). Do NOT use binding-family choice to try to extend capacity; capacity is "
        "set by (N, K, alpha) hyperparameters.\n"
        "\n"
        "TIER: MM_TENTATIVE_SYNTHESIS. The 0.0-shift pattern is UNIVERSAL across all 15 tested "
        "(op, seed) combos with 4/5 positive controls PASS. But the meta claim rests on a "
        "narrow surface: 3 ops per axis, 2 axes, WM regime only, Axis J 2-seed only.\n"
        "\n"
        "EXPANSION CRITERIA (elevates MM_TENTATIVE toward CG-eligibility):\n"
        "  (a) Axis J seed_7 completes and matches K*=500 (3-seed instead of 2-seed)\n"
        "  (b) >= 5 ops tested per axis (currently 3)\n"
        "  (c) Structurally-DIFFERENT binding class tested (e.g., graph-tensor, "
        "non-commutative bind-op) and shows same capacity-invariance\n"
        "\n"
        "This atom AMENDS but does NOT supersede the two prior HF atoms. Both remain "
        "authoritative single-axis characterizations; this atom adds the cross-axis synthesis."
    ),
    "metadata": {
        "provenance_quality": "MEASURED_MECHANISM_TENTATIVE_SYNTHESIS",
        "verdict": "MEASURED_MECHANISM_TENTATIVE",
        "verified_off_data_by": ATOMIZED_BY,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on all 5 metrics.json files (3 D-x-O seeds + "
            "2 Axis J seeds): D-x-O 9/9 cells K_cliff=750 unique={750} shift=0.0 unique={0.0}; "
            "Axis J 6/6 cells K*=500 log10_sep=0.0 all pairs both seeds; positive controls PASS "
            "all 5 seeds; mechanistic distinctness holds both axes; top1 differentiation "
            "confirmed cross-seed for D-x-O (FHRR mean 0.800 vs HAD/CIR 0.29/0.30)"
        ),
        "kind_notes": "SYNTHESIS_META composing two prior single-axis HF atoms",
        "composes_atoms": [
            {
                "atom_id_prefix": "T3/EXP_substrate_binding_op_x_capacity_v1_3seed_HARD_FAIL",
                "commit": "3197b903",
                "role": "axis_D_x_O_evidence_source",
                "seeds": [7, 13, 19],
                "ops": ["HADAMARD_BIND","CIRCULAR_CONV_HRR","FHRR_COMPLEX_MUL"],
                "K_cliff_all_9_cells": 750,
                "shift_all_9_cells": 0.0,
            },
            {
                "atom_id_prefix": "T3/EXP_substrate_order_binding_family_v1_2seed_HARD_FAIL",
                "commit": "c7feb0c4",
                "role": "axis_J_evidence_source",
                "seeds_completed": [13, 19],
                "seed_7_phantom_runner_stuck": True,
                "ops": ["CYCLIC_SHIFT","RANDOM_PERMUTATION","PHASE_ROTATION"],
                "K_star_all_6_cells": 500,
                "log10_sep_all_pairs_all_seeds": 0.0,
            },
        ],
        "cross_axis_evidence": {
            "D_x_O_K_cliff_unique_values_across_9_cells": [750],
            "D_x_O_shift_unique_values_across_9_cells": [0.0],
            "Axis_J_K_star_unique_values_across_6_cells": [500],
            "Axis_J_log10_sep_unique_values_across_all_pairs_both_seeds": [0.0],
            "total_op_seed_combos_tested": 15,
            "total_capacity_invariance_confirmations": 15,
            "positive_controls_passing": 5,
            "total_positive_controls": 5,
        },
        "performance_differentiation_evidence": {
            "D_x_O_top1_at_alpha_0p5_cross_seed_mean": {
                "HADAMARD_BIND": 0.289,
                "CIRCULAR_CONV_HRR": 0.300,
                "FHRR_COMPLEX_MUL": 0.800,
                "performance_range_ratio": 2.77,
                "FHRR_dominates": True,
            },
        },
        "synthesis_claim": (
            "Binding-family operation choice (within either binding-op axis or order-op axis) "
            "does NOT shift capacity location (K_cliff, K*) at WM regime. Capacity is set by "
            "(N, K, alpha, codebook geometry). Binding-family choice affects performance LEVEL "
            "through noise geometry, not capacity CEILING."
        ),
        "substrate_design_implication": (
            "At chain-grade scale, pick binding-family for performance regime (FHRR at moderate "
            "K for recall dominance; HAD/CIR for asymptotic cleanness; ORDER-family fungible on "
            "capacity dimension). Do NOT use binding-family choice to extend capacity; capacity "
            "is set by (N, K, alpha) hyperparameters."
        ),
        "evidence_limitations": {
            "ops_per_axis": 3,
            "axes_tested": 2,
            "regime": "WM_only_no_PC_or_multi_scale",
            "Axis_J_seed_count": "2_of_3_seed_7_phantom_runner",
            "no_structurally_different_binding_class_tested": True,
        },
        "expansion_criteria_for_MM_STANDARD_and_CG_eligibility": {
            "(a)_Axis_J_seed_7_completion_K_star_500_match": {
                "current_status": "seed_7_stuck_at_0p15s_phantom_runner_infrastructure_block",
                "elevates_to": "MM_STANDARD_when_met",
            },
            "(b)_5_ops_per_axis_min": {
                "current_status": "3_ops_per_axis",
                "candidate_additional_ops_D_x_O": ["MAP_BIND","VECTOR_TENSOR_PRODUCT"],
                "candidate_additional_ops_Axis_J": ["INDEX_TAG_BIND","POSITIONAL_CONCAT"],
                "elevates_to": "MM_STANDARD_when_met",
            },
            "(c)_structurally_different_binding_class": {
                "candidates": ["graph_tensor_op","non_commutative_bind","tensor_order_op"],
                "elevates_to": "CG_eligibility_with_pre_reg_when_met",
            },
        },
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_synthesis_composes_two_prior_HF_atoms",
            "capability_axis_orthogonality_capacity_vs_performance_axes_split",
            "MM_TENTATIVE_flag_narrow_test_surface_3_ops_per_axis_2_axes_WM_only",
            "expansion_criteria_specified_for_MM_STANDARD_and_CG_eligibility",
            "does_not_supersede_composing_atoms",
            "Fix_28_per_arm_metrics_verified",
            "stage_3_compositional_understanding_USER_2026-06-26",
        ],
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}

# ============================================================================
# CERT LEDGER ROW
# ============================================================================
_t0 = time.time()

ledger_META_SYNTHESIS = {
    "ts": _t0,
    "op": "cert_ruling",
    "atom_id": f"math::{atom_META_SYNTHESIS['id']}",
    "cert_status": "measured_mechanism_tentative",
    "cert_class": "synthesis_meta_finding_binding_family_capacity_invariance",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": None,
    "verdict": (
        "MM_TENTATIVE_SYNTHESIS_binding_family_capability_invariance_capacity_axis_at_WM_regime_"
        "composes_D_x_O_3seed_HF_and_axis_J_2seed_HF_15_of_15_op_seed_combos_confirm_zero_shift_"
        "K_cliff_750_all_D_x_O_K_star_500_all_axis_J_performance_axis_top1_differs_"
        "FHRR_0p800_vs_HAD_0p289_CIR_0p300_2p7x_range_expansion_criteria_"
        "seed_7_completion_plus_5_ops_per_axis_plus_new_binding_class_needed_for_CG"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "notes_path": None,
        "metrics_paths": [
            "data/exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}/metrics.json",
            "data/exp_substrate_order_binding_family_v1_seed_{13,19}/metrics.json",
        ],
        "atom_qualified_id": f"math::{atom_META_SYNTHESIS['id']}",
        "composes_atoms_referents": [
            "math::T3/EXP_substrate_binding_op_x_capacity_v1_3seed_HARD_FAIL... (commit 3197b903)",
            "math::T3/EXP_substrate_order_binding_family_v1_2seed_HARD_FAIL... (commit c7feb0c4)",
        ],
    },
    "supersedes": None,
    "note": (
        "META_synthesis_binding_family_capability_invariance_capacity_axis_MM_TENTATIVE_"
        "composes_D_x_O_3seed_HF_3197b903_and_axis_J_2seed_HF_c7feb0c4_"
        "15_of_15_op_seed_combos_show_zero_shift_on_capacity_axis_"
        "performance_axis_top1_differentiates_FHRR_dominates_2p7x_range_"
        "TENTATIVE_flag_narrow_surface_3_ops_per_axis_2_axes_WM_only_2_seed_Axis_J_"
        "expansion_criteria_seed_7_unblock_plus_5_ops_per_axis_plus_new_binding_class_"
        "elevates_MM_STANDARD_and_enables_CG_eligibility_with_proper_pre_reg"
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
    append_jsonl_a5(MATH_ATOMS, atom_META_SYNTHESIS,    "math/atoms (META SYNTHESIS binding-family capacity invariance)")
    append_jsonl_a5(CERT_LEDGER, ledger_META_SYNTHESIS, "cert_ledger (META SYNTHESIS MM_TENTATIVE)")
    print(f"[A5] DONE OK")
    print(f"[A5] META SYNTHESIS: MM_TENTATIVE binding-family capability invariance (capacity-axis)")
    print(f"[A5] Composes D-x-O 3seed HF + Axis J 2seed HF (15 of 15 combos confirm zero shift)")
    print(f"[A5] Expansion criteria: seed_7 unblock + 5+ ops per axis + new binding class")
    print(f"[A5] CERT delta = 0")


if __name__ == "__main__":
    main()
