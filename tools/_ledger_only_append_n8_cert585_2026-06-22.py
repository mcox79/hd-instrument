"""One-off: append the cert_ledger row for n8 ConceptNet chain-grade (atom is already
present in Store at CERT 585; ledger missed it due to a background-task race in the
atomize tool). Idempotent re-write is safe (cert_ledger_writer's whole-ledger structural
idempotency check will skip if a duplicate landed)."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from tools.cert_ledger_writer import append_cert_ledger_row, build_chain_grade_ruling_row


def main():
    ledger_row = build_chain_grade_ruling_row(
        atom_id="math::T3/EXP_n8_conceptnet_ingest_eval_v1",
        cell_commit="8bbc11c4",
        verdict="HARD_PASS",
        notes_path="notes/research_n8_conceptnet_LANDED_HARD_PASS_2026-06-22.md",
        metrics_path="data/exp_n8_conceptnet_ingest_eval_v1/metrics.json",
        cv=0.027,
        cert_class="pre_reg_pass",
        atomized_by="skunkworks",
        note=(
            "n8_conceptnet_ingest_eval_v1_chain_grade_CERT_585_second_KB_ingest_atom_after_U1_"
            "OPEN_C_frozen_encoder_unlock_36_5x_ratio_discriminator_real_heldout_in_compose_graph_zero"
        ),
    )
    # CERT 585 is the live state -- the Store atom landed during a prior background-task race;
    # we are catching up the ledger. The Store mutation (the actual CERT increment) is already
    # past, so PRE and POST both read 585 here. We assert PRE = 585 only; POST is not asserted
    # because the ledger append itself does not move CERT (the Store write upstream did).
    row_h = append_cert_ledger_row(
        ledger_row,
        expected_cert_n_pre=585,
    )
    print(f"PHASE-C ledger row appended; hash = {row_h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
