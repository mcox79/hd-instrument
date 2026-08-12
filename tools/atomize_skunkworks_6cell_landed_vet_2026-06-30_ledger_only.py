"""Ledger-only follow-up for atomize_skunkworks_6cell_landed_vet_2026-06-30.

The main atomization landed all 26 atoms via PartitionedStore.add_atom (which is
write-through), but the script called store.flush() which doesn't exist on
PartitionedStore, raising AttributeError BEFORE the ledger-write loop ran. Atoms
landed cleanly (24 in math + 2 in meta verified by grep skunkworks_atomize_6cell
in atoms.jsonl files). This follow-up writes only the 26 cert_ledger rows.

Per the foreground_vs_background_for_sequential_store_ledger_writes discipline,
recovery via _ledger_only_* one-shot is the correct path.

Run:
  .venv/Scripts/python.exe tools/atomize_skunkworks_6cell_landed_vet_2026-06-30_ledger_only.py
"""
from __future__ import annotations
import importlib.util
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.partition import PartitionedStore
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_honest_negative_row,
    build_measured_mechanism_row,
)

# Import the main atomize module via spec because file name has hyphens
_spec = importlib.util.spec_from_file_location(
    "atomize_6cell_2026_06_30",
    "tools/atomize_skunkworks_6cell_landed_vet_2026-06-30.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ALL_ATOM_BUILDERS = _mod.ALL_ATOM_BUILDERS
RULING_NOTE = _mod.RULING_NOTE
CELL_COMMIT = _mod.CELL_COMMIT
ATOMIZED_BY = _mod.ATOMIZED_BY


def main():
    store = PartitionedStore(Path("data/substrate_index"))
    cert_count = sum(1 for a in store.all_atoms() if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE")
    print(f"[ledger-only] CERT N at start = {cert_count}")

    now = time.time()
    written = 0
    for tag, builder in ALL_ATOM_BUILDERS:
        a = builder()
        atom_qualified = f"{a.corpus.value}::{a.id}"

        is_meta = a.kind.value == "methodology_rule"
        cert_status = (a.metadata or {}).get("cert_status")

        if is_meta:
            row = {
                "ts": now,
                "op": "cert_ruling",
                "atom_id": atom_qualified,
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
                    "metrics_path": "n/a-meta-rule-derived-from-batch",
                    "atom_qualified_id": atom_qualified,
                },
                "supersedes": None,
                "note": f"6cell_batch_meta_rule_{tag}",
            }
        elif cert_status == "honest_negative":
            # Map our internal cert_class to ledger schema enum.
            atom_cert_class = (a.metadata or {}).get("cert_class") or ""
            # INFRA-DEP HFs (binding-op GPU-mandate, refuse-gate selftest-only) use infra_record;
            # TEST_DESIGN_MASKING (multihop SAT_CORNER) + REGIME_FLIP (TV seed_13) use pre_reg_miss_proven_bound
            if "infra_dep" in atom_cert_class or "selftest_only" in atom_cert_class or "gpu_mandate" in atom_cert_class:
                ledger_cert_class = "infra_record"
            else:
                ledger_cert_class = "pre_reg_miss_proven_bound"
            row = build_honest_negative_row(
                atom_id=atom_qualified,
                cell_commit=CELL_COMMIT,
                verdict=(a.metadata or {}).get("verdict") or "HARD_FAIL",
                notes_path=RULING_NOTE,
                metrics_path=(a.metadata or {}).get("metrics_path") or (a.metadata or {}).get("metrics_paths", ["n/a"])[0],
                cert_class=ledger_cert_class,
                atomized_by=ATOMIZED_BY,
                note=f"6cell_batch_HN_{tag}_atom_class_{atom_cert_class}",
                ts=now,
            )
        elif cert_status == "measured_mechanism":
            row = build_measured_mechanism_row(
                atom_id=atom_qualified,
                cell_commit=CELL_COMMIT,
                verdict=(a.metadata or {}).get("verdict") or "MIDDLE_BAND",
                notes_path=RULING_NOTE,
                metrics_path=(a.metadata or {}).get("metrics_path") or (a.metadata or {}).get("metrics_paths", ["n/a"])[0],
                atomized_by=ATOMIZED_BY,
                note=f"6cell_batch_MM_{tag}",
                ts=now,
            )
        else:
            print(f"  [SKIP] {tag} cert_status={cert_status}")
            continue

        try:
            append_cert_ledger_row(
                row,
                strict_a5=False,
                expected_cert_n_pre=cert_count,
                expected_cert_n_post=cert_count,
            )
            written += 1
            print(f"  [ledger] {tag:14s} appended ({cert_status if not is_meta else 'meta_rule'})")
        except Exception as e:
            print(f"  [ledger ERROR] {tag}: {e}")

    print(f"\n[DONE] {written} ledger rows appended.")


if __name__ == "__main__":
    main()
