"""Skunkworks batch 4 atomization (2026-07-02 early).

Writes:
1. Dim H v3 B.1 MM atom (softmax magnitude-collapse; single-seed HF at N=8192 wall)
2. Dim H v3 B.2 MM atom (dimensional-headroom-absorption; single-seed HF at N=8192 wall)
3. META synthesis atom: Willshaw two-tier prediction FALSIFIED across 3 mechanism classes
   (dense-Hopfield uniform-write baseline v2 + softmax scaling v3.B1 + canonical Hebbian W-matrix v3.B2)
   Tier: MM_TENTATIVE_SYNTHESIS (author-suggested; single-seed + N=1024 sign-mixed suggests weak-effect regime)
4. cross_axis_v2 seed_7 CELL_CRASHED note (SELFTEST bug — fake-grid HP path failed;
   NOT a substrate finding; cell needs author fix; seeds 13/19 not landed yet)

Atomic write via os.replace + verify-load + cert_ledger increment.
"""

import json
import os
import time
import hashlib
from pathlib import Path

MATH_PATH = Path("d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl")
META_PATH = Path("d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl")
LEDGER_PATH = Path("d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl")

now = time.time()
ts_iso = "2026-07-02T01:35:00+00:00"

# ---- ATOMS ----
b1_atom_id = "math::T3/EXP_distributional_shape_zipfian_v3_B1_softmax_tape_write_scale_seed_7_smoke_HF_MEASURED_MECHANISM_architectural_magnitude_collapse_at_Amit_Gutfreund_wall_N_8192_preview_recall_0p005_gap_neg_0p080_control_alpha_0_saturates_1p000_confirms_per_row_eta_scaling_breaks_softmax_scale_invariance_head_row_eta_1p0_vs_tail_eta_0p03_collapses_argmax_to_highest_magnitude_row_regardless_of_query_similarity_2026-07-02"

b1_atom = {
    "atom_id": b1_atom_id,
    "corpus": "math",
    "tier_class": "MEASURED_MECHANISM",
    "entity": "Distributional shape B.1 softmax + tape-write-scale reinforcement architectural magnitude-collapse at Amit-Gutfreund wall N=8192",
    "claim": (
        "MEASURED@d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v3_hebbian_frequency_reinforce_seed_7/metrics.json: "
        "at N=8192 with per-row eta scaling (head_eta=1.0, tail_eta=0.03 for Zipfian α=1), preview_recall_all=0.005 "
        "(collapse across all queries); Q1_head=0.003, Q4_tail=0.083, gap=-0.080 (<0.10 HF gate). "
        "Uniform-alpha control (α=0, σ=0.30, L=0.12, N=8192) recovers to 1.000 (all quartiles equal). "
        "PHYSICS: per-row eta scaling breaks softmax scale-invariance; softmax(β * q @ K_tape.T) with K_tape = eta_i * K_norm "
        "puts ~exp(β*log(eta_head/eta_tail)) mass on head row regardless of query similarity. "
        "For eta ratio 30:1 and β~10: ~exp(30) magnitude bias → argmax collapses to rank-1 head row. "
        "Tier MM (single seed_7, one mechanism class); scope-bounded to continuous bipolar substrate with softmax READ-REPLACE."
    ),
    "cert_status": "measured_mechanism",
    "corpus_tags": ["distributional_shape", "Zipfian", "softmax", "magnitude_collapse", "Amit_Gutfreund_wall", "hidden_phase_diagram_Dim_H", "smoke_HF", "single_seed_MM"],
    "referent_pointer": {
        "metrics_paths": [
            "d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v3_hebbian_frequency_reinforce_seed_7/metrics.json"
        ],
        "notes_path": "d:/AI/hd-instrument/notes/exp_dev_findings/exp_distributional_shape_zipfian_v3_HF_HEBBIAN_TWO_MECHANISMS_2026-07-01.md",
        "cell_commit": "4a0da238"
    },
    "verification": {
        "verified_off_data": True,
        "auditor": "skunkworks_batch4_2026-07-02",
        "recompute_confirmed": "preview_recall_0.005, Q1_head=0.003, Q4_tail=0.083, gap=-0.080, control_1.000 all matched off-disk",
        "cross_arc_overlap_check": "substrate_query.sh top cosine=0.2432 (< 0.30 novelty threshold); NOVEL"
    },
    "cross_seed_cv": None,
    "n_seeds_verified": 1,
    "ts_added": ts_iso,
    "amends_atom": None,
    "superseded": False,
    "meta_rule_gate_history": ["META_RULE_L_strict_band", "META_RULE_AC_provenance", "META_RULE_AF_arms_differ", "META_RULE_AG_baseline_in_band", "META_RULE_M_calibration", "DISCRIMINATOR_MUST_SURVIVE_SCALE_pattern_C"]
}

b2_atom_id = "math::T3/EXP_distributional_shape_zipfian_v3_B2_canonical_Hebbian_Wmatrix_seed_7_smoke_HF_MEASURED_MECHANISM_dimensional_headroom_absorbs_Zipfian_asymmetry_at_N_8192_preview_recall_0p95_gap_neg_0p010_control_alpha_0_saturates_1p000_N_1024_shows_mixed_sign_max_abs_gap_0p118_weak_effect_dies_at_scale_2026-07-02"

b2_atom = {
    "atom_id": b2_atom_id,
    "corpus": "math",
    "tier_class": "MEASURED_MECHANISM",
    "entity": "Distributional shape B.2 canonical Hebbian W-matrix frequency-reinforcement dimensional-headroom absorption at N=8192",
    "claim": (
        "MEASURED@d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v3_hebbian_wmatrix_canonical_seed_7/metrics.json: "
        "at N=8192 with canonical Hebbian W-matrix outer-product accumulator (Zipfian α=1, σ=0.30, L=0.10), "
        "preview_recall_all=0.9500; Q1_head=0.9448, Q4_tail=0.9545, gap=-0.010 (|gap|<0.05 HF gate — near-isotropic recall). "
        "Uniform-alpha control (α=0) saturates at 1.000. "
        "N=1024 window sweep shows MAX |gap|=0.118 (tail-favored at α=1, σ=0.30, L=0.12) but SIGN-MIXED across arms — "
        "not a coherent effect. "
        "PHYSICS: at high N (8192) substrate has dimensional headroom that ABSORBS Zipfian eta-weighted cross-talk into argmax cleanup; "
        "at low N (1024) weak effect visible but sign-mixed suggesting seed-dependent noise. "
        "Effective asymmetry ~1% at N=8192 (below drill's predicted 30%). "
        "Tier MM (single seed_7, sign-mixed at N=1024 suggests weak-effect regime that dies at scale)."
    ),
    "cert_status": "measured_mechanism",
    "corpus_tags": ["distributional_shape", "Zipfian", "canonical_Hebbian", "W_matrix", "dimensional_headroom", "hidden_phase_diagram_Dim_H", "smoke_HF", "single_seed_MM"],
    "referent_pointer": {
        "metrics_paths": [
            "d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v3_hebbian_wmatrix_canonical_seed_7/metrics.json"
        ],
        "notes_path": "d:/AI/hd-instrument/notes/exp_dev_findings/exp_distributional_shape_zipfian_v3_HF_HEBBIAN_TWO_MECHANISMS_2026-07-01.md",
        "cell_commit": "4a0da238"
    },
    "verification": {
        "verified_off_data": True,
        "auditor": "skunkworks_batch4_2026-07-02",
        "recompute_confirmed": "preview_recall_0.95, gap=-0.010, control_1.000, N=1024 max_abs_gap=0.118 sign-mixed all matched off-disk",
        "cross_arc_overlap_check": "substrate_query.sh top cosine=0.2305 (< 0.30 novelty threshold); NOVEL"
    },
    "cross_seed_cv": None,
    "n_seeds_verified": 1,
    "ts_added": ts_iso,
    "amends_atom": None,
    "superseded": False,
    "meta_rule_gate_history": ["META_RULE_L_strict_band", "META_RULE_AC_provenance", "META_RULE_AF_arms_differ", "META_RULE_AG_baseline_in_band", "META_RULE_M_calibration", "DISCRIMINATOR_MUST_SURVIVE_SCALE_pattern_C"]
}

# META joint closure atom
meta_atom_id = "meta::T3/META_synthesis_Willshaw_two_tier_prediction_FALSIFIED_across_3_mechanism_classes_at_Amit_Gutfreund_wall_MM_TENTATIVE_SYNTHESIS_dense_Hopfield_uniform_write_v2_plus_softmax_tape_write_scale_v3_B1_plus_canonical_Hebbian_Wmatrix_v3_B2_all_fail_head_favors_tail_collapses_signature_at_N_8192_continuous_bipolar_substrate_scope_bounded_binary_sparse_CAM_Willshaw_original_untested_escape_hatch_2026-07-02"

meta_atom = {
    "atom_id": meta_atom_id,
    "corpus": "meta",
    "tier_class": "MM_TENTATIVE_SYNTHESIS",
    "entity": "META synthesis: sparse-coding Willshaw two-tier prediction FALSIFIED across 3 mechanism classes at Amit-Gutfreund wall (continuous bipolar substrate scope)",
    "claim": (
        "META-SYNTHESIS composing 3 mechanism-class evidence pillars: "
        "(1) Cell D v2 dense-Hopfield READ-REPLACE uniform-write CG parent [prior atom]; "
        "(2) v3.B1 softmax + tape-write-scale reinforcement MM (this batch, seed_7 smoke HF; architectural magnitude-collapse); "
        "(3) v3.B2 canonical Hebbian W-matrix MM (this batch, seed_7 smoke HF; dimensional-headroom absorption). "
        "JOINT CLOSURE: sparse-coding drill's Willshaw BINARY sparse-CAM two-tier prediction "
        "(head items collide in shared coordinates forcing tail eviction under saturation) "
        "does NOT translate to continuous bipolar substrate across ANY of 3 tested continuous-substrate mechanism classes. "
        "In continuous substrate: (a) softmax path breaks architecturally via magnitude-scaling argmax collapse; "
        "(b) linear W-matrix path absorbs asymmetry via dimensional headroom at N=8192; "
        "(c) uniform-write baseline shows no asymmetry (v2 established). "
        "SCOPE-BOUNDED: binary sparse-CAM (Willshaw's original substrate) NOT tested — genuine escape hatch. "
        "N<<512 (very-thin substrate where dimensional headroom disappears) NOT tested. "
        "Correlated keys NOT tested (in-flight per Director; may inject shared-coordinate collision the drill predicts). "
        "TIER: MM_TENTATIVE_SYNTHESIS — single-seed evidence for 2 of 3 legs; N=1024 sign-mix for B.2 suggests weak-effect regime. "
        "EXPANSION CRITERIA TO CG: (a) seed_13+19 dispatch replication OR (b) N<<512 substrate-thin regime dispatch OR "
        "(c) binary sparse-CAM Willshaw-original dispatch shows the drill's prediction fires (would ANTI-FALSIFY the joint claim by demonstrating substrate-specific scope)."
    ),
    "cert_status": "mm_tentative_synthesis",
    "corpus_tags": ["META_synthesis", "sparse_coding_drill", "Willshaw_two_tier", "Amit_Gutfreund_wall", "hidden_phase_diagram_Dim_H", "continuous_bipolar_substrate", "3_mechanism_class_closure"],
    "composes_atoms": [
        b1_atom_id,
        b2_atom_id,
        "math::T3/PRIOR_CELL_D_v2_dense_Hopfield_READ_REPLACE_uniform_write_CG_parent"  # symbolic pointer; already in Store
    ],
    "referent_pointer": {
        "notes_path": "d:/AI/hd-instrument/notes/exp_dev_findings/exp_distributional_shape_zipfian_v3_HF_HEBBIAN_TWO_MECHANISMS_2026-07-01.md",
        "sparse_coding_drill_source": "d:/AI/hd-instrument/notes/research_sparse_coding_compressed_sensing_2026-07-01.md"
    },
    "verification": {
        "verified_off_data": True,
        "auditor": "skunkworks_batch4_2026-07-02",
        "composition_evidence_verified": "3-class synthesis: v2 CG (prior in Store) + v3.B1 MM (this batch) + v3.B2 MM (this batch), each off-disk verified",
        "cross_arc_overlap_check": "novel synthesis — 3-class closure not previously atomized"
    },
    "ts_added": ts_iso,
    "amends_atom": None,
    "superseded": False,
    "expansion_criterion": "seed_13+19 dispatch replication OR N<<512 substrate-thin regime OR binary sparse-CAM Willshaw-original dispatch"
}

# ---- WRITE atomically ----
def append_atom(path: Path, atom: dict):
    """Atomic append: read all, append new, tmp-write, os.replace, verify-load."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_lines = []
    if path.exists():
        with open(path, "rb") as f:
            existing_lines = [l.decode("utf-8", errors="strict") for l in f if l.strip()]
    existing = [json.loads(l) for l in existing_lines]
    existing.append(atom)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for a in existing:
            f.write(json.dumps(a) + "\n")
    os.replace(tmp, path)
    # Verify load
    with open(path, "rb") as f:
        loaded_lines = [l.decode("utf-8", errors="strict") for l in f if l.strip()]
    loaded = [json.loads(l) for l in loaded_lines]
    assert loaded[-1]["atom_id"] == atom["atom_id"], "verify-load failed"
    return len(loaded)

n_math_before = 0
if MATH_PATH.exists():
    with open(MATH_PATH, "rb") as f:
        n_math_before = sum(1 for _ in f)
n_meta_before = 0
if META_PATH.exists():
    with open(META_PATH, "rb") as f:
        n_meta_before = sum(1 for _ in f)

n_math_after_b1 = append_atom(MATH_PATH, b1_atom)
n_math_after_b2 = append_atom(MATH_PATH, b2_atom)
n_meta_after = append_atom(META_PATH, meta_atom)

print(f"math atoms: {n_math_before} -> {n_math_after_b2}")
print(f"meta atoms: {n_meta_before} -> {n_meta_after}")

# ---- LEDGER entries ----
ledger_entries = [
    {
        "ts": now,
        "op": "cert_ruling_MEASURED_MECHANISM_Dim_H_v3_B1_softmax_scale_reinforcement_smoke_HF_architectural_magnitude_collapse_single_seed_scope_bounded_continuous_bipolar_softmax_READ_REPLACE",
        "atom_id": b1_atom_id,
        "cert_status": "measured_mechanism",
        "cert_class": "distributional_shape_Dim_H_v3_B1_softmax_magnitude_collapse_MM_single_seed",
        "verified_off_data": True,
        "atomized_by": "skunkworks_batch4_2026-07-02",
        "cell_commit": "4a0da238",
        "verdict": "MM_smoke_HF_architectural_magnitude_collapse_positive_control_saturates_1p000_physics_attributed_softmax_scale_invariance_broken_by_per_row_eta_scaling",
        "cert_increment_delta": 1,
        "cv": None,
        "referent_pointer": {
            "metrics_path": "d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v3_hebbian_frequency_reinforce_seed_7/metrics.json",
            "notes_path": "d:/AI/hd-instrument/notes/exp_dev_findings/exp_distributional_shape_zipfian_v3_HF_HEBBIAN_TWO_MECHANISMS_2026-07-01.md"
        }
    },
    {
        "ts": now + 0.001,
        "op": "cert_ruling_MEASURED_MECHANISM_Dim_H_v3_B2_canonical_Hebbian_Wmatrix_smoke_HF_dimensional_headroom_absorption_at_N_8192_single_seed_scope_bounded_continuous_bipolar_linear_W_matrix",
        "atom_id": b2_atom_id,
        "cert_status": "measured_mechanism",
        "cert_class": "distributional_shape_Dim_H_v3_B2_dimensional_headroom_absorption_MM_single_seed",
        "verified_off_data": True,
        "atomized_by": "skunkworks_batch4_2026-07-02",
        "cell_commit": "4a0da238",
        "verdict": "MM_smoke_HF_dimensional_headroom_absorbs_Zipfian_asymmetry_gap_neg_0p010_at_N_8192_positive_control_saturates_1p000_N_1024_shows_sign_mixed_max_abs_gap_0p118_weak_effect_dies_at_scale",
        "cert_increment_delta": 1,
        "cv": None,
        "referent_pointer": {
            "metrics_path": "d:/AI/hd-instrument/data/exp_distributional_shape_zipfian_v3_hebbian_wmatrix_canonical_seed_7/metrics.json",
            "notes_path": "d:/AI/hd-instrument/notes/exp_dev_findings/exp_distributional_shape_zipfian_v3_HF_HEBBIAN_TWO_MECHANISMS_2026-07-01.md"
        }
    },
    {
        "ts": now + 0.002,
        "op": "cert_ruling_MM_TENTATIVE_SYNTHESIS_META_Willshaw_two_tier_prediction_FALSIFIED_3_mechanism_classes_continuous_bipolar_substrate_scope_bounded_binary_sparse_CAM_escape_hatch",
        "atom_id": meta_atom_id,
        "cert_status": "mm_tentative_synthesis",
        "cert_class": "META_synthesis_sparse_coding_drill_falsification_3_mechanism_class_closure_MM_TENTATIVE",
        "verified_off_data": True,
        "atomized_by": "skunkworks_batch4_2026-07-02",
        "cell_commit": "4a0da238",
        "verdict": "MM_TENTATIVE_SYNTHESIS_composes_v2_CG_parent_plus_v3_B1_MM_plus_v3_B2_MM_falsifies_Willshaw_across_continuous_bipolar_substrate_expansion_criteria_seed_13_19_or_N_lt_512_or_binary_sparse_CAM_dispatch",
        "cert_increment_delta": 1,
        "cv": None,
        "referent_pointer": {
            "notes_path": "d:/AI/hd-instrument/notes/exp_dev_findings/exp_distributional_shape_zipfian_v3_HF_HEBBIAN_TWO_MECHANISMS_2026-07-01.md",
            "sparse_coding_drill_source": "d:/AI/hd-instrument/notes/research_sparse_coding_compressed_sensing_2026-07-01.md"
        }
    },
    {
        "ts": now + 0.003,
        "op": "cert_no_ruling_CELL_CRASHED_cross_axis_v2_seed_7_SELFTEST_bug_HF_ARM_IDENTICAL_META_RULE_AF_fake_grid_HP_path_assertion_failure_line_944_cell_needs_author_fix_NOT_substrate_finding_seeds_13_19_not_landed_yet",
        "atom_id": None,
        "cert_status": "cell_crashed_no_atom",
        "cert_class": "cross_axis_v2_selftest_bug_test_design_failure",
        "verified_off_data": True,
        "atomized_by": "skunkworks_batch4_2026-07-02",
        "cell_commit": "4c8acf54",
        "verdict": "CELL_CRASHED_SELFTEST_ASSERTION_line_944_fake_grid_HP_path_HF_ARM_IDENTICAL_META_RULE_AF_STD_beta13_K4000_equals_K100_across_M_N_and_DIS_beta4_same_pattern_hash_reported_STD_beta13_3e880_pattern_indicates_arm_hash_not_K_sensitive_cell_author_test_bug_prevented_full_execution_seeds_13_19_dispatched_same_code_likely_same_crash_recommend_cell_author_fix_and_redispatch",
        "cert_increment_delta": 0,
        "cv": None,
        "referent_pointer": {
            "metrics_path": "d:/AI/hd-instrument/data/exp_cross_axis_m_n_k_discriminating_arm_v2_seed_7/metrics.json",
            "smoke_metrics_HP": "d:/AI/hd-instrument/data/exp_cross_axis_m_n_k_discriminating_arm_v2_seed_7_smoke/metrics.json"
        }
    }
]

# Atomic append to ledger
existing_ledger = []
if LEDGER_PATH.exists():
    with open(LEDGER_PATH, "rb") as f:
        existing_ledger_lines = [l.decode("utf-8", errors="strict") for l in f if l.strip()]
    existing_ledger = [json.loads(l) for l in existing_ledger_lines]
n_ledger_before = len(existing_ledger)
existing_ledger.extend(ledger_entries)
tmp_ledger = LEDGER_PATH.with_suffix(LEDGER_PATH.suffix + ".tmp")
with open(tmp_ledger, "w", encoding="utf-8") as f:
    for e in existing_ledger:
        f.write(json.dumps(e) + "\n")
os.replace(tmp_ledger, LEDGER_PATH)
with open(LEDGER_PATH, "rb") as f:
    reloaded_lines = [l.decode("utf-8", errors="strict") for l in f if l.strip()]
reloaded = [json.loads(l) for l in reloaded_lines]
assert len(reloaded) == n_ledger_before + len(ledger_entries), "ledger verify-load failed"
print(f"cert_ledger: {n_ledger_before} -> {len(reloaded)} (added {len(ledger_entries)})")
print("A5 GATE PASS: atomic write + verify-load + integrity-check all confirmed")
