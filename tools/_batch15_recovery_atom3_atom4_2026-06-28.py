"""Recovery: batch 15 atomization mid-flight failure.

Atoms 1, 2, 3 already landed in Store; Atoms 1, 2 ledger rows landed; Atom 3 ledger
row failed on invalid cert_class='proven_negative_smoke'. Atom 4 (META_RULE_AN) never
written. This script:

  1. Appends Atom 3 ledger row with cert_class='mechanism_characterization' (the convention
     used for honest_negative tier in prior batches; e.g. batch14 narrative HARD_FAIL
     used mechanism_characterization).
  2. Writes Atom 4 (META_RULE_AN) Store + ledger row.

Both windows: PRE/POST cert_n == 628 (delta=0).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from tools.cert_ledger_writer import append_cert_ledger_row
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "_batch15_main",
    "tools/atomize_skunkworks_batch15_stage3_revival_2026-06-28.py",
)
_batch15 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_batch15)
build_atom4_meta_rule_an = _batch15.build_atom4_meta_rule_an
RULING_NOTE = _batch15.RULING_NOTE
CELL_COMMIT = _batch15.CELL_COMMIT
ATOMIZED_BY = _batch15.ATOMIZED_BY
METRICS_HIER_SCDJ = _batch15.METRICS_HIER_SCDJ
STORE_ROOT = _batch15.STORE_ROOT


def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )


ATOM3_ID = (
    "T3/EXP_substrate_hierarchical_planner_state_conditioned_disjoint_v1_HONEST_NEGATIVE_SMOKE_"
    "RAIL_1p000_sanity_OK_RAND_0p017_chance_FLAT_PREPLAY_K64_D8_0p067_baseline_"
    "TREE_3LVL_STATE_COND_0p000_TREE_3LVL_DISJOINT_BLOCK_0p000_TREE_3LVL_BOTH_0p000_"
    "both_minus_flat_neg_0p067_both_minus_state_cond_0p000_both_minus_disjoint_0p000_"
    "arms_distinct_True_cardinality_ok_360of360_n_seeds_2_seeds_7_17_N8160_blocks8_actions6_"
    "macros5_K_class8_goals30_depth8_K_flat64_K_tree16_2nd_hierarchical_planning_attempt_failed"
)


def main():
    store = PartitionedStore(STORE_ROOT)
    pre_n = _cert_count(store)
    print(f"PRE cert_n={pre_n}")
    assert pre_n == 628

    # Atom 3 ledger row (Store atom already landed)
    print("Appending Atom 3 ledger row (honest_negative -> mechanism_characterization class)...")
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{ATOM3_ID}",
            "cert_status": "honest_negative",
            "cert_class": "mechanism_characterization",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "HARD_FAIL",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_HIER_SCDJ,
                "atom_qualified_id": f"math::{ATOM3_ID}",
            },
            "supersedes": None,
            "note": "batch15_hierarchical_planner_state_cond_disjoint_HONEST_NEG_2nd_attempt_macros_hurt_flat_baseline_neg_0p067_Sutton_Precup_options_drill_ANCHOR_2_redesign_needed",
        },
        expected_cert_n_pre=pre_n,
        expected_cert_n_post=pre_n,
    )

    # Atom 4 -- META_RULE_AN
    atom4 = build_atom4_meta_rule_an()
    print(f"Writing Atom 4: id_head={str(atom4.id)[:80]}...")
    store.add_atom(atom4)
    post_n = _cert_count(store)
    assert post_n == pre_n, f"After Atom 4 cert_n={post_n} != pre {pre_n}"

    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atom4.id}",
            "cert_status": "custom",
            "cert_class": "discipline_meta",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "META_RULE_NEUTRAL",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": "n/a-meta-rule-derived-from-Atom1-and-Atom2",
                "atom_qualified_id": f"meta::{atom4.id}",
            },
            "supersedes": None,
            "note": "batch15_META_RULE_AN_cone_collapse_formula_N2048_calibrated_no_extrapolate_to_N8192_3p7x_off_extends_AL_AM_at_capacity_layer",
        },
        expected_cert_n_pre=pre_n,
        expected_cert_n_post=pre_n,
    )

    # Round-trip
    s2 = PartitionedStore(STORE_ROOT)
    match = [x for x in s2.all_atoms() if x.id == atom4.id]
    assert len(match) == 1, f"Round-trip FAIL atom4 found={len(match)}"
    print(f"Round-trip OK: META_RULE_AN landed")

    final = _cert_count(s2)
    print(f"FINAL cert_n={final}")
    assert final == pre_n
    print("Recovery OK: Atom 3 ledger row + Atom 4 (META_RULE_AN) Store + ledger landed.")


if __name__ == "__main__":
    main()
