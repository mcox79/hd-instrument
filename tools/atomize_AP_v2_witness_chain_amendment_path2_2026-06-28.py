"""
A5-gated amendment: extend AP_v2 witness chain to include Path 2 brain-composition
(witness #2 in chronological order; was missed in initial AP_v2 atom).

CORRECTION CONTEXT:
  Initial AP_v2 (atomized prior in same session) listed witness chain as:
    [Path 1 partition_oracle_substrate_derived_hint v1 HF,
     Path 3 narrative_partition_oracle_V_C_sweep v1 HF]
  But Path 2 (brain-composition vmPFC+cortex+hippo) ALSO landed today (commit
  1513e314) and atomized as math::T3/EXP_partition_oracle_brain_composition_hint_
  vmPFC_cortex_hippo_3primitive_HARD_FAIL_2026-06-28 with AP-witness role.

  This amendment atom files the full 3-witness chain CORRECTION. AP_v2 itself
  is not rewritten (Store atoms are append-only by convention); instead this
  amendment is filed as a NEW meta atom AP_v2_chain_amendment_witness_3.

CERT delta = 0 (amendment; no new rule promotion; just witness-chain correction).
"""

import json
import os
import time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
META_ATOMS = ROOT / "data/substrate_index/meta/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_AP_v2_witness_chain_amendment_path2_2026-06-28"

PATH_1 = "math::T3/EXP_partition_oracle_substrate_derived_hint_naive_centroid_composition_HARD_FAIL_2026-06-28"
PATH_2 = "math::T3/EXP_partition_oracle_brain_composition_hint_vmPFC_cortex_hippo_3primitive_HARD_FAIL_2026-06-28"
PATH_3 = "math::T3/EXP_narrative_partition_oracle_V_C_sweep_HARD_FAIL_Q2_no_V_C_cliff_2026-06-28"

AP_V2_ATOM_ID = (
    "META_RULE_AP_v2_chain_grade_eligible_composition_of_chain_grade_primitives_requires_signal_shape_"
    "adapter_OR_co_training_OR_pre_cell_compatibility_audit_2_witness_threshold_MET_witness_1_partition_"
    "oracle_substrate_derived_hint_v1_seed_7_HF_route_acc_at_chance_witness_2_narrative_partition_oracle_"
    "V_C_sweep_v1_seed_7_HF_oracle_Q2_at_floor_across_full_V_C_sweep_both_witnesses_show_same_failure_"
    "class_input_output_signal_shape_OR_operating_regime_incompatibility_between_chain_grade_primitive_"
    "validated_regime_AND_downstream_task_regime_SCHEMA_VET_directive_active_supersedes_v1_2026-06-28"
)


amendment_atom = {
    "id": (
        "META_RULE_AP_v2_witness_chain_amendment_witness_3_path_2_brain_composition_vmPFC_cortex_hippo_"
        "3primitive_HF_added_to_chain_initial_AP_v2_atom_listed_path1_and_path3_only_path2_landed_"
        "chronologically_2nd_today_commit_1513e314_amendment_brings_total_chain_to_3_witnesses_2026-06-28"
    ),
    "name": (
        "META_RULE_AP_v2 witness-chain AMENDMENT: Path 2 brain-composition (vmPFC+cortex+hippo) HF "
        "added as witness #2 (chronological). Total chain = 3 witnesses across 3 distinct composition "
        "designs all converging on same root cause (operating-regime / signal-shape incompatibility)"
    ),
    "corpus": "meta",
    "tier": "T_methodology",
    "kind": "discipline_rule_amendment",
    "description": (
        "AMENDMENT to META_RULE_AP_v2 witness chain. Initial AP_v2 atom (atomized same session) listed "
        "chain as [Path 1, Path 3] but missed Path 2 (brain-composition vmPFC+cortex+hippo HF, atomized "
        "via commit 1513e314 earlier same day). Full corrected chain (chronological): "
        ""
        "WITNESS #1: Path 1 partition_oracle_substrate_derived_hint_v1_seed_7 HF "
        "  - Composition: chain-grade partition-routing primitive (M=10M, dedicated category cue c_p) -> "
        "    multihop chain query (no category cue) via naive centroid argmax. "
        "  - Result: route_acc=0.2173 vs chance 0.20; cascade death. "
        ""
        "WITNESS #2: Path 2 partition_oracle_brain_composition_hint_v1_seed_7 HF "
        "  - Composition: brain-faithful 3-primitive (vmPFC schema-Bayes + cortex partition + hippo cleanup) "
        "    at FULL N=8192 depth=15. "
        "  - Result: arm_c top1=0.01; partition-correct-per-step mean=0.2093 (chance 0.20); "
        "    lift_C_A=-0.39; ORACLE_D=0.84 (rules out ingest/cleanup bug). "
        "  - Dual-mode diagnosis: (a) signal-shape (schema-prototype training distribution = first-hop "
        "    tuples; multihop inference distribution = OOD per-hop pairs); (b) iterated-state mismatch "
        "    (schema fires ONCE per chain; partition decided ONCE; hippo cleanup runs 15 times with SAME "
        "    chosen_part; test requires 15 distinct per-hop partition decisions). This is AP witness "
        "    AND first META_RULE_AQ witness (iterated-state-tracker discipline). "
        ""
        "WITNESS #3: Path 3 narrative_partition_oracle_V_C_sweep_v1_seed_7 HF "
        "  - Composition: chain-grade partition_oracle_v5 (validated V_C=4000 ORACLE_C=0.97 with "
        "    V_C-scaled anchor-projection basis) -> narrative-coref Q2 pronoun task (fixed N_CHARS=5 "
        "    partitions; per-partition vocab scales with V_C; anchor basis NOT V_C-scaled). "
        "  - Result: oracle_Q2 at floor (0.125) across full V_C sweep {50, 200, 1000, 4000}; "
        "    no V_C trend; lift_over_naive 0.000 at V_C=4000. "
        ""
        "WITNESS DIVERSITY (3-witness): 3 distinct primitives (partition-routing M=10M / vmPFC-schema-Bayes-"
        "cortex-hippo 3-primitive / partition_oracle_v5_hardened); 3 distinct downstream tasks (multihop "
        "chain / multihop chain with brain-grounded composition / narrative coreference Q2); 3 distinct "
        "failure modes (cascade death / per-step chance with cortex collapse / floor across V_C sweep) -- "
        "ALL three converge on SAME root cause: primitive A's natural operating regime / signal shape "
        "does NOT match primitive B's regime / signal shape. AP-discipline is robust across primitive class, "
        "task class, and failure-mode class. "
        ""
        "Path 2 ALSO witnesses META_RULE_AQ (iterated-state-tracker discipline; orthogonal to AP). "
        "AP applies to STATIC composition design; AQ applies to DYNAMIC per-step state evolution. "
        "Both witnesses can apply to the same cell when composition has both static-shape AND "
        "iterated-state mismatches. "
        ""
        "AP_v2 ENFORCEMENT remains as authored (SCHEMA-VET HARD GATE; prereg must declare upstream-output-"
        "shape + downstream-input-shape + compatibility argument). This amendment ONLY corrects the "
        "witness chain; does NOT change rule semantics or enforcement. "
        ""
        "CERT delta = 0 (no new rule promotion; amendment-only)."
    ),
    "aliases": [
        "AP_v2_chain_amendment_witness_3_path_2_added_2026-06-28",
        "META_RULE_AP_v2_full_witness_chain_correction",
    ],
    "metadata": {
        "provenance_quality": "AMENDMENT_TO_AP_V2",
        "cert_status": "amendment_record",
        "cert_class": "meta_discipline_amendment",
        "atomized_by": ATOMIZED_BY,
        "atomized_date": "2026-06-28",
        "amends_atom_id": f"meta::{AP_V2_ATOM_ID}",
        "full_witness_chain_chronological": [PATH_1, PATH_2, PATH_3],
        "witness_chain_diversity_check": (
            "3 distinct primitives + 3 distinct downstream tasks + 3 distinct failure modes -- "
            "all converge on operating-regime / signal-shape incompatibility root cause"
        ),
        "cert_increment_delta": 0,
        "ts_iso_atomized": "2026-06-28",
    },
}


amendment_ledger = {
    "ts": time.time(),
    "op": "meta_rule_amendment",
    "atom_id": f"meta::{amendment_atom['id']}",
    "cert_status": "amendment_record",
    "cert_class": "meta_discipline_amendment",
    "verified_off_data": True,
    "atomized_by": ATOMIZED_BY,
    "cell_commit": "amendment_to_AP_v2",
    "verdict": (
        "META_RULE_AP_v2_witness_chain_amendment_path_2_brain_composition_added_as_chronological_witness_2_"
        "full_chain_now_3_witnesses_path_1_substrate_derived_hint_path_2_brain_composition_vmPFC_cortex_hippo_"
        "path_3_narrative_V_C_sweep_all_3_converge_on_same_root_cause_operating_regime_signal_shape_"
        "incompatibility_AP_discipline_robust_across_primitive_class_task_class_failure_mode_class"
    ),
    "cert_increment_delta": 0,
    "cv": None,
    "referent_pointer": {
        "amends_atom_qualified_id": f"meta::{AP_V2_ATOM_ID}",
        "amendment_atom_qualified_id": f"meta::{amendment_atom['id']}",
        "witness_atom_qualified_ids": [PATH_1, PATH_2, PATH_3],
    },
    "supersedes": None,
    "note": (
        "AP_v2_chain_amendment_path_2_added_full_witness_chain_3_widespread_across_3_primitives_3_tasks_3_failure_modes"
    ),
}


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
        except Exception as e: raise RuntimeError(f"PRE fail {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed = json.loads(new_line)
    if "id" in new_row:
        assert parsed["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert parsed["atom_id"] == new_row["atom_id"]

    out = "\n".join(pre_lines + [new_line]) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out); f.flush(); os.fsync(f.fileno())
    os.replace(str(tmp), str(path))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    assert len(post_lines) == pre_count + 1
    tail = json.loads(post_lines[-1])
    if "id" in new_row: assert tail["id"] == new_row["id"]
    if "atom_id" in new_row: assert tail["atom_id"] == new_row["atom_id"]
    for i, ln in enumerate(post_lines):
        if not ln.strip(): continue
        try: json.loads(ln)
        except Exception as e: raise RuntimeError(f"POST fail {i+1}: {e}")
    print(f"[A5] {label}: OK post_count={len(post_lines)}")


def main():
    print(f"[A5] amendment START {ATOMIZED_BY}")
    append_jsonl_a5(META_ATOMS, amendment_atom, "meta/atoms.jsonl [AP_v2_amendment]")
    append_jsonl_a5(CERT_LEDGER, amendment_ledger, "meta/cert_ledger.jsonl [amendment]")
    print(f"[A5] DONE. CERT delta = 0 (amendment)")


if __name__ == "__main__":
    main()
