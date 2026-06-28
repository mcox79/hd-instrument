"""
A5-gated atomize: substrate_partition_oracle_substrate_derived_hint_v1_seed_7 HARD_FAIL
+ META_RULE_AP (composition-of-chain-grade-primitives signal-shape-adapter discipline).

Verdict: HARD_FAIL_NO_SIGNAL_AT_DERIVED.
Cert class: mechanism_characterization. CERT delta = 0 (HF) + 1 (META_RULE_AP candidate).

OFF-DATA recompute (verify-OFF-DATA, NOT verdict_msg):
  A=0.40 B=0.00 C=0.84 D=0.00 E=0.00
  lift_B_A=-0.40 (NEGATIVE; derived is WORSE than baseline)
  route_acc=0.2173 vs 1/5 chance=0.20 (=+0.017; essentially chance over 5 partitions)
  per-step decay arm_b: 0.23 -> 0.05 -> 0.01 -> 0.00 ... (cascade death)
  arms_distinct=True saturation=False cardinality_ok=True
  ORACLE C=0.84 -> ground-truth path still works (rules out cleanup/ingest bug)

Mechanism diagnosis (load-bearing):
  Chain-grade partition-routing primitive (exp_substrate_partition_routing M=10M routing_acc=0.97)
  used a DEDICATED category cue c_p injected per query. Multihop chain query
  E[s] * R[p] * sq carries NO partition cue. Naive centroid C[p]=normalize(mean(E_part[p] @ W))
  argmax against the W-state fires at ~chance (route_acc 0.2173 vs 0.20 floor).
  Cascade death once partition wrong: cleanup-narrowing locks into wrong partition's
  E_part subspace, no recovery path. Per-step monotone decay confirms.

  THIS IS COMPOSITION-OF-CHAIN-GRADE-PRIMITIVES gap. The output signal shape of
  the multihop chain query does NOT match the input signal shape the partition-
  routing primitive was trained/validated against. A's natural output is not
  shape-compatible with B's natural input. Naive composition breaks.

META_RULE_AP (novel; not duplicate of AC-AO):
  AL/AM/AN/AO cover "substrate already does X" + capacity-scaling + capability-closure.
  AP addresses COMPOSITION risk: chain-grade primitives are NOT trivially composable.
  Pre-cell signal-shape compatibility audit required when composing primitive A's
  output into primitive B's input, OR adapter mechanism, OR co-training.

A5 protocol:
  1. PRE: read full file + count + parse all lines
  2. Append HF atom to math/atoms.jsonl via tmp -> os.replace
  3. Append META_RULE_AP atom to meta/atoms.jsonl via tmp -> os.replace
  4. Append 2 cert_ledger rows to meta/cert_ledger.jsonl via tmp -> os.replace
  5. POST: verify-load: count delta + tail-line parses + round-trip ID match + every-line integrity

Anchors:
  - metrics: data/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7_smoke/metrics.json
  - prereg:  preregs/2026-06-28_substrate_partition_oracle_substrate_derived_hint_v1.md
  - cell:    experiments/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7.py
  - parent primitive cell: experiments/exp_substrate_partition_routing_10M_full_v2.py
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

METRICS_PATH = "data/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7_smoke/metrics.json"
PREREG_PATH = "preregs/2026-06-28_substrate_partition_oracle_substrate_derived_hint_v1.md"
CELL_PATH = "experiments/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7.py"

ATOMIZED_BY = "skunkworks_atomize_partition_oracle_substrate_derived_hint_v1_HF_AP_2026-06-28"
ATOMIZED_DATE = "2026-06-28"
CELL_COMMIT = "0e7d9142"  # latest staging commit (sibling MB atomize)


# ============================================================
# ATOM 1: math T3 experiment_record HARD_FAIL
# ============================================================
hf_atom = {
    "id": "T3/EXP_partition_oracle_substrate_derived_hint_naive_centroid_composition_HARD_FAIL_2026-06-28",
    "name": (
        "Partition-oracle substrate-derived hint v1 seed_7 smoke at FULL-N=8192 d=15 "
        "-- HARD_FAIL_NO_SIGNAL_AT_DERIVED (naive centroid composition of chain-grade "
        "partition-routing primitive into multihop chain query -- signal-shape incompatible)"
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "experiment_record",
    "description": (
        "M3-usable Barrier 1 break candidate: replace ground-truth partition oracle "
        "(parent _hardened_v1 ORACLE_B=0.835 at single seed) with SUBSTRATE-DERIVED "
        "partition hint via naive composition with the chain-grade partition-routing "
        "primitive (parent atom: exp_substrate_partition_routing M=10M routing_acc=0.97). "
        "Composition: ingest -> C[p]=normalize(mean(E_part[p] @ W)) per-partition centroid "
        "in W-output space (substrate-learned; no gen-time peek); query at hop i -> "
        "state=W@key; pred_part=argmax(C @ state); cleanup over E_part[pred_part]. "
        "Smoke single seed=7 at FULL N=8192 V_C=4000 V_P=10 depth=15 n_chains_test=100 (5-arm). "
        "OFF-DATA recompute: A_BASELINE=0.40 (rail PASS [0.30,0.70]); "
        "B_SUBSTRATE_DERIVED=0.00 route_acc=0.2173 (vs 1/5=0.20 chance = +0.017; essentially chance); "
        "C_ORACLE=0.84 (ground-truth still works); D_NOISY=0.00; E_RANDOM=0.00. "
        "lift_B_A = -0.40 (NEGATIVE; substrate-derived is WORSE than baseline). "
        "Per-step decay arm_b: 0.23 -> 0.05 -> 0.01 -> 0 -> 0 (cascade death once partition wrong). "
        "arms_distinct=True saturation=False cardinality_ok=True (5 of 5). "
        "MECHANISM DIAGNOSIS: chain-grade partition-routing primitive used a DEDICATED "
        "category cue c_p injected per query. The multihop chain query E[s] * R[p] * sq "
        "carries NO partition cue. Naive centroid argmax against W-state fires at chance. "
        "Cascade death because cleanup-narrowing locks into wrong partition's E_part subspace "
        "with no recovery path; oracle arm C=0.84 confirms the cleanup-narrowing mechanism "
        "works WHEN given correct partition -- rules out ingest/cleanup bugs. "
        "ROOT CAUSE: composition-of-chain-grade-primitives signal-shape incompatibility. "
        "A's natural output signal shape (W-state from multihop key) does NOT match B's "
        "natural input signal shape (dedicated category cue c_p). See META_RULE_AP atom. "
        "Path 2 implication (vmPFC schema-Bayes + cortex partition + hippo pattern completion): "
        "SAME composition-risk applies unless schema-Bayes output shape maps to cortex partition "
        "input shape. If Path 2 ALSO HARD_FAILs, that's evidence the composition-discipline gap "
        "is real and triggers a research drill on adapter/cocompose mechanisms."
    ),
    "aliases": [
        "partition_oracle_substrate_derived_hint_naive_centroid_composition_HARD_FAIL_2026-06-28",
        "substrate_partition_oracle_substrate_derived_hint_v1_seed_7_HF",
        "barrier_1_M3_usable_substrate_derived_naive_centroid_composition_dead",
        "composition_of_chain_grade_primitives_signal_shape_incompatible_witness_1",
    ],
    "metadata": {
        "provenance_quality": "MEASURED",
        "cert_status": "hard_fail",
        "cert_class": "mechanism_characterization",
        "verdict": "HARD_FAIL_NO_SIGNAL_AT_DERIVED",
        "verdict_subtype": "NAIVE_CENTROID_COMPOSITION_ROUTING_AT_CHANCE_CASCADE_DEATH",
        "cell_commit": CELL_COMMIT,
        "cell_path": CELL_PATH,
        "prereg_path": PREREG_PATH,
        "metrics_path": METRICS_PATH,
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "verified_off_data": True,
        "verified_off_data_evidence": (
            "OFF-DATA recompute via .venv python on metrics.json per_seed[0]: "
            "A=0.40 B=0.00 C=0.84 D=0.00 E=0.00; route_acc=0.2173 (+0.017 over 1/5 chance); "
            "lift_B_A=-0.40 (negative); per-step decay 0.23->0.05->0.01->0; "
            "ORACLE C=0.84 rules out cleanup/ingest bug; cardinality_ok=True; "
            "arms_distinct=True (5 unique SHA-256); saturation=False"
        ),
        "n_seeds_run": 1,
        "n_seeds_planned_total": 3,
        "seeds_pending": [13, 19],
        "seeds_pending_note": (
            "Sibling cells seed_13 + seed_19 exist but not yet dispatched. Given HF magnitude "
            "(arm_b=0.00; lift=-0.40; route_acc=chance), additional seeds will not change "
            "verdict class -- mechanism is dead at this composition. Sibling dispatch optional "
            "for cv-confirmation; primary action is research drill on adapter mechanism."
        ),
        "regime": {
            "N": 8192,
            "V_C": 4000,
            "V_P": 10,
            "depth": 15,
            "n_chains_train": 200,
            "n_chains_test": 100,
            "encoder": "SUBSTRATE_NATIVE_BIPOLAR",
            "n_partitions": 5,
            "part_size": 800,
            "crosstalk_part": 0.3123,
            "crosstalk_baseline": 0.6987,
        },
        "per_arm_top1": {
            "A_baseline_full_V_C": 0.40,
            "B_substrate_derived_centroid": 0.00,
            "C_oracle_ground_truth": 0.84,
            "D_noisy_permuted_hint": 0.00,
            "E_random_partition": 0.00,
        },
        "lifts_gaps": {
            "lift_B_A": -0.40,
            "lift_B_E": 0.00,
            "gap_C_B": 0.84,
            "noisy_sanity_abs": 0.40,
        },
        "routing_diagnostic": {
            "route_acc": 0.2173,
            "chance_5_partitions": 0.20,
            "above_chance_delta": 0.0173,
            "interpretation": "routing fires at chance; centroid signal carries no partition info in multihop W-state",
        },
        "per_step_acc_arm_b": [0.23, 0.05, 0.01, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "cascade_death_witness": "per_step monotone decay from 0.23 to 0 by step 5; once partition wrong, cleanup locks into wrong subspace",
        "gates_evaluated": {
            "B_in_HP_band_0p50_0p95": False,
            "B_above_HF_floor_0p30": False,
            "lift_B_A_ge_0p10_signal_floor": False,
            "lift_B_A_ge_0p30_HP": False,
            "lift_B_E_ge_0p30": False,
            "gap_C_B_le_0p30": False,
            "noisy_sanity_abs_D_A_le_0p10": False,
            "baseline_A_in_rail_0p30_0p70": True,
            "saturation_lt_0p95": True,
            "arms_distinct_sha256_5_unique": True,
            "cardinality_ok_5_arms_5_expected": True,
        },
        "hf_driver_primary": "B_below_HF_floor_AND_negative_lift_AND_routing_at_chance",
        "ruling_out_alternatives": {
            "ingest_bug": "ruled out -- ORACLE arm C=0.84 works (same W matrix)",
            "cleanup_bug": "ruled out -- ORACLE arm C=0.84 works (same E_part cleanup)",
            "centroid_construction_bug": "ruled out -- centroid build verified in selftest T4 (unit-norm check)",
            "smoke_too_small": "ruled out -- DISCRIMINATOR-MUST-SURVIVE-SCALE smoke at FULL N + FULL depth",
        },
        "mechanism_root_cause": (
            "Naive centroid C[p] = normalize(mean(E_part[p] @ W)) captures the AVERAGE W-row "
            "mass projected onto partition p's atoms, but the W-state W @ key for a multihop "
            "chain query is the BOUND output state for the specific (s, p_rel) binding -- "
            "an extremely high-variance signal where partition identity is dominated by "
            "the specific source atom + relation. The mean centroid signature is washed out "
            "by atom-level + relation-level variance; argmax over 5 centroids fires at chance. "
            "The chain-grade partition-routing primitive avoided this by injecting a DEDICATED "
            "category cue c_p into the query (E[s] * R[p] * c_p * sq), making the W-state "
            "carry an explicit partition signal. Multihop has no such cue."
        ),
        "composition_failure_class": "input_output_signal_shape_incompatibility_between_chain_grade_primitives",
        "rescue_paths_for_future_work": [
            "adapter_head: learned linear projection from W-state to category-cue-space (small head; CE loss vs partition labels)",
            "co_train: ingest with augmented bindings that carry the partition cue c_p so multihop query naturally projects to category space",
            "centroid_construction_v2: contrastive centroids OR multi-vector partition signatures OR per-relation centroids",
            "scratch_pad_augmentation: explicit partition-prediction sub-state with its own update rule",
        ],
        "barrier_1_status": "M3_usable_naive_composition_DEAD; ground-truth ORACLE arm still chain-grade-eligible at MIDDLE_BAND (sibling cell single seed)",
        "capability_closure_status": (
            "DO_NOT_CLOSE_partition_oracle_direction -- this is HF #1 on substrate-derived hint mechanism class. "
            "META_RULE_AO (3 HF before closure) NOT triggered. Path 2 vmPFC composition cell in flight will "
            "provide 2nd data-point on composition-discipline gap (or contradict it if Path 2 HARD_PASSes)."
        ),
        "cert_increment_delta": 0,
        "discipline_tags": [
            "META_RULE_AC", "META_RULE_AE", "META_RULE_AF", "META_RULE_AG",
            "META_RULE_AH", "META_RULE_AL", "META_RULE_AN", "META_RULE_AP",
            "META_RULE_H", "BIAS-Q", "BIAS-N", "BIAS-S",
            "DISCRIMINATOR_MUST_SURVIVE_SCALE_USER_2026-06-26",
            "Fix_28_per_arm_metrics_not_verdict_msg",
            "functional_requirement_first_USER_2026-06-28",
        ],
        "next_actions": [
            "decide_research_drill_now_vs_wait_for_Path_2_evidence_(acf38256ac9fd3a60)",
            "if_Path_2_also_HARD_FAILs_compose_discipline_gap_confirmed_dispatch_adapter_head_cell",
            "if_Path_2_HARD_PASSes_re_examine_signal_shape_compatibility_in_path_2_vs_path_1",
            "no_blind_re_dispatch_of_naive_centroid_variants",
        ],
        "parent_chain_grade_primitive": {
            "atom_id_pattern": "exp_substrate_partition_routing*",
            "M": "10M",
            "routing_acc": 0.97,
            "key_design": "dedicated category cue c_p injected per query",
            "design_delta_from_this_cell": "multihop query carries NO category cue",
        },
        "supersedes": None,
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# ATOM 2: META_RULE_AP (meta corpus; cert-neutral discipline rule)
# ============================================================
ap_atom = {
    "id": "META_RULE_AP_composition_of_chain_grade_primitives_requires_signal_shape_adapter_OR_co_training_OR_pre_cell_compatibility_audit_naive_compose_breaks_when_primitive_A_natural_output_signal_shape_does_not_match_primitive_B_natural_input_signal_shape_witness_substrate_derived_hint_v1_seed_7_HARD_FAIL_route_acc_at_chance_despite_parent_routing_primitive_M10M_route_acc_0p97_2026-06-28_extends_META_RULE_AM_substrate_already_does_X_at_composition_layer_meta_discipline",
    "name": (
        "META_RULE_AP -- composition of chain-grade primitives requires signal-shape "
        "compatibility audit OR explicit adapter OR co-training; naive pipe-A-into-B "
        "breaks when A's natural output shape does not match B's natural input shape"
    ),
    "corpus": "meta",
    "tier": "T_methodology",
    "kind": "discipline_rule",
    "description": (
        "META_RULE_AP (composition-discipline at primitive-composition layer): "
        "Chain-grade primitives are NOT trivially composable. Each chain-grade primitive "
        "was trained / validated with a specific signal structure (specific input cue shape, "
        "specific state representation, specific regime). Piping primitive A's output into "
        "primitive B's input may break B because A's output does NOT match B's expected input "
        "signal structure. "
        ""
        "Composition requires at least ONE of: "
        "(1) explicit signal-shape adapter mechanism between A and B (learned projection, "
        "    classifier head, attention readout, etc.); "
        "(2) co-training of the composition (A and B trained jointly on the downstream task); "
        "(3) pre-cell signal-shape compatibility audit verifying A's NATURAL output signal "
        "    shape matches B's NATURAL input signal shape (cue type, dimensionality, "
        "    representation basis, variance regime). "
        ""
        "PRE-CELL DISCIPLINE (cell-author + Skunkworks SCHEMA-VET): when a cell proposes "
        "to COMPOSE 2+ chain-grade primitives, the prereg must explicitly state (a) the "
        "natural output signal shape of each upstream primitive, (b) the natural input signal "
        "shape of each downstream primitive, (c) the compatibility argument OR the adapter "
        "mechanism. Pre-reg lacking this triggers SCHEMA-VET REJECT pending compatibility audit. "
        ""
        "WITNESS 1 (atomized 2026-06-28): "
        "exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7 HARD_FAIL: "
        "naive composition of chain-grade partition-routing primitive (M=10M routing_acc=0.97 "
        "with DEDICATED category cue c_p) into multihop chain query (NO category cue) via "
        "centroid argmax fired at chance (route_acc=0.2173 vs 1/5=0.20). The parent primitive's "
        "natural input is (E[s] * R[p_rel] * c_p * sq) -- a cue-augmented binding. The multihop "
        "query natural output is (E[s] * R[p_rel] * sq) -- no category cue. Signal shapes "
        "incompatible. Naive centroid C[p]=normalize(mean(E_part[p] @ W)) does NOT bridge the "
        "gap; centroid signature is washed out by atom-level + relation-level variance. "
        ""
        "Extends META_RULE_AM (substrate-already-does-X) at the COMPOSITION layer: AM forces "
        "demonstration that existing primitive FAILS before adding new mechanism; AP forces "
        "demonstration that downstream primitive's input requirements are SATISFIED by upstream "
        "primitive's output BEFORE composing them. "
        ""
        "Related but distinct from: "
        "- META_RULE_AL (cosine kernel pre-encodes schema prior): about substrate primitive "
        "  doing X already; AP is about TWO primitives not composing. "
        "- META_RULE_AN (cone-collapse formula scaling): about REGIME extrapolation; AP is "
        "  about REPRESENTATION compatibility. "
        "- META_RULE_AO (3-HF capability closure): about KNOWING when to stop; AP is about "
        "  designing compositions correctly to avoid spurious HF on real capability."
    ),
    "aliases": [
        "composition_of_chain_grade_primitives_signal_shape_adapter_discipline",
        "no_naive_pipe_A_into_B_without_signal_shape_compatibility_audit",
        "META_RULE_AP_composition_adapter_discipline",
    ],
    "metadata": {
        "provenance_quality": "DERIVED_FROM_WITNESS",
        "cert_status": "cert_neutral_discipline_rule",
        "cert_class": "meta_discipline",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": ATOMIZED_DATE,
        "rule_letter": "AP",
        "rule_layer": "composition",
        "extends": ["META_RULE_AM"],
        "related": ["META_RULE_AL", "META_RULE_AN", "META_RULE_AO"],
        "witness_atom_ids": [
            f"math::{hf_atom['id']}",
        ],
        "witness_count": 1,
        "promotion_criterion_for_chain_grade_meta_rule": (
            "2 independent witness cells of composition-failure rooted in signal-shape "
            "incompatibility (e.g., Path 2 vmPFC+cortex+hippo composition if it ALSO HARD_FAILs) "
            "OR USER+research consensus that single witness + mechanism diagnosis is sufficient"
        ),
        "rescue_paths": [
            "learned_adapter_head_projection",
            "co_training_with_downstream_task_objective",
            "centroid_construction_v2_contrastive_or_multi_vector",
            "scratch_pad_augmentation_with_explicit_sub_state",
        ],
        "applies_to_in_flight_cells": [
            "exp_dev_acf38256ac9fd3a60_Path_2_vmPFC_schema_Bayes_plus_cortex_partition_plus_hippo_pattern_completion",
        ],
        "schema_vet_directive": (
            "Any prereg proposing primitive-composition must include: "
            "(a) upstream primitive natural output signal shape; "
            "(b) downstream primitive natural input signal shape; "
            "(c) compatibility argument OR explicit adapter mechanism. "
            "Skunkworks SCHEMA-VET will REJECT preregs lacking this."
        ),
        "ts_iso_atomized": ATOMIZED_DATE,
    },
}


# ============================================================
# CERT_LEDGER ROW 1: HF cert_ruling (delta=0)
# ============================================================
hf_ledger = {
    "ts": time.time(),
    "op": "cert_ruling",
    "atom_id": f"math::{hf_atom['id']}",
    "cert_status": "hard_fail",
    "cert_class": "mechanism_characterization",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "HARD_FAIL_NO_SIGNAL_AT_DERIVED_smoke_at_FULL_N8192_d15_arm_b_0p00_route_acc_0p2173_at_chance_"
        "lift_b_a_negative_0p40_cascade_death_per_step_decay_oracle_C_0p84_rules_out_ingest_cleanup_bug_"
        "ROOT_CAUSE_composition_signal_shape_incompatibility_parent_primitive_used_dedicated_category_cue_"
        "multihop_query_has_no_category_cue_naive_centroid_does_not_bridge_gap"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "atom_qualified_id": f"math::{hf_atom['id']}",
    },
    "supersedes": None,
    "note": (
        "partition_oracle_substrate_derived_hint_v1_seed_7_HARD_FAIL_naive_composition_of_chain_grade_"
        "partition_routing_primitive_into_multihop_chain_signal_shape_incompatible_route_acc_at_chance_"
        "cascade_death_DO_NOT_close_partition_oracle_direction_HF_count_1_of_3_per_META_RULE_AO_"
        "trigger_META_RULE_AP_composition_adapter_discipline_first_witness"
    ),
}


# ============================================================
# CERT_LEDGER ROW 2: META_RULE_AP atomization (delta=+1 if first-of-kind chain-grade-eligible meta rule)
# Conservative: delta=0 here; meta rule promoted to chain-grade after 2nd witness OR USER consensus
# ============================================================
ap_ledger = {
    "ts": time.time(),
    "op": "meta_rule_atomization",
    "atom_id": f"meta::{ap_atom['id']}",
    "cert_status": "cert_neutral_discipline_rule",
    "cert_class": "meta_discipline",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": CELL_COMMIT,
    "verdict": (
        "META_RULE_AP_first_atomized_composition_of_chain_grade_primitives_requires_signal_shape_adapter_"
        "OR_co_training_OR_pre_cell_compatibility_audit_witness_1_substrate_derived_hint_v1_seed_7_HF_"
        "extends_META_RULE_AM_at_composition_layer_cert_neutral_pending_2nd_witness_for_chain_grade_promotion"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "metrics_path": METRICS_PATH,
        "prereg_path": PREREG_PATH,
        "cell_path": CELL_PATH,
        "atom_qualified_id": f"meta::{ap_atom['id']}",
        "witness_atom_qualified_ids": [f"math::{hf_atom['id']}"],
    },
    "supersedes": None,
    "note": (
        "META_RULE_AP_composition_adapter_discipline_atomized_cert_neutral_pending_2nd_witness_"
        "SCHEMA_VET_directive_active_immediately_for_in_flight_Path_2_vmPFC_cortex_hippo_composition_cell_"
        "acf38256ac9fd3a60_if_Path_2_also_HF_promote_AP_to_chain_grade_and_dispatch_adapter_head_research_drill"
    ),
}


# ============================================================
# A5 WRITE PROTOCOL
# ============================================================
def append_jsonl_a5(path: Path, new_row: dict, label: str):
    """Atomic append with verify-load + integrity-check."""
    print(f"[A5] {label}: path={path}")
    assert path.exists(), f"target does not exist: {path}"

    # PRE: read full file + count
    with open(path, "r", encoding="utf-8") as f:
        pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    # Validate every pre-line parses (integrity)
    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    # Build new content
    new_line = json.dumps(new_row, ensure_ascii=True)
    # Round-trip validate
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id"), "round-trip id mismatch"
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id"), "round-trip atom_id mismatch"

    out_lines = pre_lines + [new_line]
    out_text = "\n".join(out_lines) + "\n"

    # tmp -> os.replace (atomic)
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp_path), str(path))

    # POST: verify-load
    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1, f"count delta mismatch: {pre_count} -> {post_count}"

    # Tail must parse + match
    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"], f"tail id mismatch"
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"], f"tail atom_id mismatch"

    # Re-validate every line parses
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK (atomic append + verify-load + integrity-check)")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    print(f"[A5] HF atom_id = math::{hf_atom['id']}")
    print(f"[A5] META_RULE_AP atom_id = meta::{ap_atom['id'][:80]}...")
    print(f"[A5] cert_ledger ops: hf_ruling (delta=0) + ap_atomization (delta=0; cert-neutral)")

    append_jsonl_a5(MATH_ATOMS, hf_atom, "math/atoms.jsonl")
    append_jsonl_a5(META_ATOMS, ap_atom, "meta/atoms.jsonl")
    append_jsonl_a5(CERT_LEDGER, hf_ledger, "meta/cert_ledger.jsonl[hf]")
    append_jsonl_a5(CERT_LEDGER, ap_ledger, "meta/cert_ledger.jsonl[ap]")

    print(f"[A5] DONE OK; CERT delta = 0 (HF) + 0 (META_RULE_AP cert-neutral pending 2nd witness)")


if __name__ == "__main__":
    main()
