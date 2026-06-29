"""Recovery: anchor4-encoder-family landed-VET atomization completion.

The original script atomize_skunkworks_anchor4_encoder_family_landed_vet_2026-06-29.py
landed Atom 1 to the Store but failed at the ledger gate due to invalid cert_class value
'regime_conditional_encoder_collapse' (valid set requires 'mechanism_characterization').

This recovery script:
  1) verifies Atom 1 is already in Store (no double-write)
  2) appends ledger row for Atom 1 with cert_class='mechanism_characterization'
  3) writes Atoms 2 + 3 to Store and ledger
  4) re-runs A5 PRE/POST gates throughout

PRE CERT N (verified live; per Atom 1 already landed): 632 (MM doesn't increment)
POST CERT N: 632 unchanged
"""
from __future__ import annotations
import sys
import importlib.util
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row

# Load the original script as a module (hyphens in filename block normal import)
_ORIG_PATH = Path("tools/atomize_skunkworks_anchor4_encoder_family_landed_vet_2026-06-29.py").resolve()
_spec = importlib.util.spec_from_file_location("anchor4_encoder_orig", _ORIG_PATH)
_orig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_orig)

build_atom1_anchor4_encoder_mm = _orig.build_atom1_anchor4_encoder_mm
build_atom2_meta_rule_ao_sparse_regime = _orig.build_atom2_meta_rule_ao_sparse_regime
build_atom3_meta_rule_ap_gate_recency_floor = _orig.build_atom3_meta_rule_ap_gate_recency_floor
RULING_NOTE = _orig.RULING_NOTE
CELL_COMMIT = _orig.CELL_COMMIT
ATOMIZED_BY = _orig.ATOMIZED_BY
METRICS_SEED_7 = _orig.METRICS_SEED_7
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
    print(f"[recovery] PRE cert_n={pre_cert_n}")
    assert pre_cert_n == 632, f"PRE cert_n {pre_cert_n} != 632 expected"

    atoms = [
        build_atom1_anchor4_encoder_mm(),
        build_atom2_meta_rule_ao_sparse_regime(),
        build_atom3_meta_rule_ap_gate_recency_floor(),
    ]

    # Verify Atom 1 already in Store
    a1_hits = [a for a in store.all_atoms() if a.id == atoms[0].id]
    assert len(a1_hits) == 1, f"Atom 1 should already be in Store; found {len(a1_hits)}"
    print(f"[recovery] Atom 1 confirmed in Store: {a1_hits[0].id[:80]}...")

    # Check Atoms 2 + 3 presence (may have partially landed from earlier crash)
    a2_in_store = bool([a for a in store.all_atoms() if a.id == atoms[1].id])
    a3_in_store = bool([a for a in store.all_atoms() if a.id == atoms[2].id])
    print(f"[recovery] Atom 2 in Store: {a2_in_store}; Atom 3 in Store: {a3_in_store}")

    if not apply:
        print("[recovery] DRY mode -- no writes. Re-run with --apply.")
        return 0

    expected_n = pre_cert_n  # delta=0 throughout

    # ============================================================
    # Atom 1: ledger row only (Store already has it)
    # ============================================================
    print("[recovery] Appending ledger row for Atom 1 (Store already has it)...")
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"math::{atoms[0].id}",
            "cert_status": "measured_mechanism",
            "cert_class": "mechanism_characterization",
            "verified_off_data": True,
            "atomized_by": ATOMIZED_BY,
            "cell_commit": CELL_COMMIT,
            "verdict": "SMOKE_HARD_PASS_DEMOTE_TO_MM_BY_CONSTRUCTION_DEGENERACY",
            "cert_increment_delta": 0,
            "cv": None,
            "referent_pointer": {
                "notes_path": RULING_NOTE,
                "metrics_path": METRICS_SEED_7,
                "atom_qualified_id": f"math::{atoms[0].id}",
            },
            "supersedes": None,
            "note": "anchor4_encoder_family_v1_3seed_MM_smoke_not_full_AND_binary_HRR_FHRR_byte_identical_n_pairs_differ_3_of_6_AND_sparse_seed_13_pass_uninformative_recency_0p405_chance_AND_prior_CG_eviction_v2_Pareto_AUC_already_covers_TD_gt_RD_70pts",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )
    print("[recovery] Atom 1 ledger row appended.")

    # ============================================================
    # Atom 2: Store + ledger (Store may already have it from prior crash)
    # ============================================================
    if not a2_in_store:
        print("[recovery] Writing Atom 2 (META_RULE_AO sparse-regime-conditional) to Store...")
        store.add_atom(atoms[1])
    else:
        print("[recovery] Atom 2 already in Store -- ledger row only.")
    post_n_2 = _cert_count(store)
    assert post_n_2 == expected_n, f"After Atom 2: cert_n={post_n_2} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atoms[1].id}",
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
                "metrics_path": "n/a-meta-rule-derived-from-anchor4-Atom1",
                "atom_qualified_id": f"meta::{atoms[1].id}",
            },
            "supersedes": None,
            "note": "anchor4_META_RULE_AO_sparse_bipolar_bundle_lift_is_regime_conditional_collapse_at_N128_n_atoms_200_6active_bits_recency_chance_0p41_cite_with_regime_bounds",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    # ============================================================
    # Atom 3: Store + ledger
    # ============================================================
    if not a3_in_store:
        print("[recovery] Writing Atom 3 (META_RULE_AP gate-needs-recency-floor) to Store...")
        store.add_atom(atoms[2])
    else:
        print("[recovery] Atom 3 already in Store -- ledger row only.")
    post_n_3 = _cert_count(store)
    assert post_n_3 == expected_n, f"After Atom 3: cert_n={post_n_3} != {expected_n}"
    append_cert_ledger_row(
        {
            "op": "cert_ruling",
            "atom_id": f"meta::{atoms[2].id}",
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
                "metrics_path": "n/a-meta-rule-derived-from-anchor4-Atom1-gate-code-inspection",
                "atom_qualified_id": f"meta::{atoms[2].id}",
            },
            "supersedes": None,
            "note": "anchor4_META_RULE_AP_pareto_AUC_chain_grade_gate_must_pair_with_recency_decode_acc_floor_else_both_arms_chance_decoders_can_PASS_witnessed_seed_13_sparse_8of8_at_recency_0p405",
        },
        expected_cert_n_pre=pre_cert_n,
        expected_cert_n_post=expected_n,
    )

    final_cert_n = _cert_count(store)
    print(f"[recovery] FINAL cert_n={final_cert_n} (pre={pre_cert_n}, delta=0)")
    assert final_cert_n == expected_n

    # Round-trip verify
    store_verify = PartitionedStore(STORE_ROOT)
    for a in atoms:
        match = [x for x in store_verify.all_atoms() if x.id == a.id]
        assert len(match) == 1, f"Round-trip FAIL for atom id={a.id} (found {len(match)})"
        assert (match[0].metadata or {}).get("atomized_by") == ATOMIZED_BY
        print(f"[recovery] Round-trip OK: {a.id[:60]}...")

    print("[recovery] APPLY OK -- ledger 3 rows + Store 3 atoms; cert_n unchanged at 632.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
