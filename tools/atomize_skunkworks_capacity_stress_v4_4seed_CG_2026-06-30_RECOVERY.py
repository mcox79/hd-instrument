"""Recovery: capacity_stress_v4 4-seed CG atomization completion.

The original script atomize_skunkworks_capacity_stress_v4_4seed_CG_2026-06-30.py
landed Atom 1 to the Store successfully (cert_n moved 632 -> 633) but failed at the
ledger gate because the writer's A5-PRE compares LIVE cert_n to expected_cert_n_pre,
and LIVE cert_n had already advanced to 633 post-Store-add. The writer's contract is
expected_cert_n_pre = the cert_n at ledger-PRE-snapshot moment, which for delta=+1
post-Store-add is the POST value, not the script's pre-Store-add 632.

This recovery script:
  1) verifies Atom 1 is already in Store (no double-write)
  2) appends ledger row for Atom 1 with expected_cert_n_pre=633 expected_cert_n_post=633
     (the cert_n is already at 633 when the ledger row is written; the ledger row
     itself doesn't change cert_n)
  3) writes Atom 2 (META_RULE_AR) to Store + ledger (delta=0; cert_n stays 633)
  4) round-trip verifies both atoms

LIVE PRE (verified): cert_n=633 (Atom 1 already landed via prior script run)
LIVE POST: cert_n=633 (Atom 2 is META_RULE_AR delta=0)
"""
from __future__ import annotations
import sys
import importlib.util
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row

# Import the builders from the original script
_ORIG_PATH = Path("tools/atomize_skunkworks_capacity_stress_v4_4seed_CG_2026-06-30.py").resolve()
_spec = importlib.util.spec_from_file_location("capacity_stress_v4_orig", _ORIG_PATH)
_orig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_orig)

build_atom1 = _orig.build_atom1_capacity_stress_v4_chain_grade
build_atom2 = _orig.build_atom2_meta_rule_ar_centroid_noise_suppression
RULING_NOTE = _orig.RULING_NOTE
CELL_COMMIT = _orig.CELL_COMMIT
ATOMIZED_BY = _orig.ATOMIZED_BY
METRICS_SEED_13 = _orig.METRICS_SEED_13
STORE_ROOT = _orig.STORE_ROOT


def _cert_count(store):
    return sum(
        1 for a in store.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )


def main(argv):
    apply = "--apply" in argv
    mode = "APPLY" if apply else "DRY"
    print(f"[recovery] mode={mode}")

    store = PartitionedStore(STORE_ROOT)
    pre_cert_n = _cert_count(store)
    print(f"[recovery] LIVE PRE cert_n={pre_cert_n}")
    assert pre_cert_n == 633, f"LIVE PRE cert_n {pre_cert_n} != 633 (Atom 1 should already be landed)"

    atom1 = build_atom1()
    atom2 = build_atom2()

    a1_hits = [a for a in store.all_atoms() if a.id == atom1.id]
    assert len(a1_hits) == 1, f"Atom 1 should already be in Store; found {len(a1_hits)}"
    print(f"[recovery] Atom 1 confirmed in Store: {atom1.id[:80]}...")

    a2_in_store = bool([a for a in store.all_atoms() if a.id == atom2.id])
    print(f"[recovery] Atom 2 in Store: {a2_in_store}")

    if not apply:
        print("[recovery] DRY mode -- no writes. Re-run with --apply.")
        return 0

    # ============================================================
    # Atom 1: ledger row only (Store already has it; cert_n=633 stays at 633 through this write)
    # ============================================================
    print("[recovery] Appending ledger row for Atom 1 (Store already has it; cert_n stays at 633)...")
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atom1.id}",
            "cert_status": "chain_grade",
            "cert_class": "pre_reg_pass",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "CHAIN_GRADE_MULTI_4SEED_3OF3_AGG_GATES_MET",
            "cert_increment_delta": 1,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_SEED_13,
                "atom_qualified_id": f"math::{atom1.id}",
            },
            "supersedes": None,
            "note": (
                "capacity_stress_v4_4seed_CG_MULTI_3of3_AGG_gates_GR_3of5_HM_4of5_RF_4of5_HM_4of4_"
                "REF_4of4_GR_3of4_seed_19_just_below_threshold_floor_ret_0p25_BIAS_Q_not_triggered_"
                "Fix_26_satisfied_cardinality_ok_arms_diverge_64of64_no_pathology_seed_7_import_crash_"
                "honest_infra_failure_effective_N_4_recovery_after_writer_PRE_snapshot_at_post_Store_state"
            ),
        },
        expected_cert_n_pre=633,
        expected_cert_n_post=633,
    )
    print("[recovery] Atom 1 ledger row appended.")

    # ============================================================
    # Atom 2: Store + ledger (META rule; delta=0; cert_n stays 633)
    # ============================================================
    if not a2_in_store:
        print("[recovery] Writing Atom 2 (META_RULE_AR centroid noise-suppression) to Store...")
        store.add_atom(atom2)
    else:
        print("[recovery] Atom 2 already in Store -- ledger row only.")

    post_n_2 = _cert_count(store)
    assert post_n_2 == 633, f"After Atom 2: cert_n={post_n_2} != 633"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atom2.id}",
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
                "metrics_path": "n/a-meta-rule-derived-from-capacity_stress_v4_Atom1-decade-binned-HM-minus-GR",
                "atom_qualified_id": f"meta::{atom2.id}",
            },
            "supersedes": None,
            "note": (
                "META_RULE_AR_centroid_argmax_noise_suppressing_prototype_primitive_advantage_grows_"
                "monotonic_with_alpha_HM_minus_GR_D0_0p000_D1_0p021_D2_0p067_D3_0p127_D4_0p288_witnessed_"
                "capacity_stress_v4_4seed_aliased_after_AQ_taken_by_brain_composition_rule"
            ),
        },
        expected_cert_n_pre=633,
        expected_cert_n_post=633,
    )

    final_cert_n = _cert_count(store)
    print(f"[recovery] FINAL cert_n={final_cert_n} (chain_grade Atom1 + META Atom2)")
    assert final_cert_n == 633

    # Round-trip verify
    store_verify = PartitionedStore(STORE_ROOT)
    for a in [atom1, atom2]:
        match = [x for x in store_verify.all_atoms() if x.id == a.id]
        assert len(match) == 1, f"Round-trip FAIL for atom id={a.id} (found {len(match)})"
        assert (match[0].metadata or {}).get("atomized_by") == ATOMIZED_BY
        print(f"[recovery] Round-trip OK: {a.id[:60]}...")

    print(f"[recovery] APPLY OK -- ledger 2 rows + Store 2 atoms; cert_n=633 (pre=632 implicit; +1).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
