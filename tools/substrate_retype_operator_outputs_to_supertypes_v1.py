"""Retype operator atoms' signature_output_type to point at atomized supertypes.

Per Exp-Dev's CELL-DISTILL-VERIFY-2 re-run analysis (2026-06-13 evening):
the 13 Skunkworks supertype atoms were CREATED but operator atoms were
NOT RE-TYPED to use them as their signature_output_type. V2 fires
SHARED_ABSTRACTION only when group members share one signature_output_type
+ domain. This is the second-step authoring that closes the gap.

Concrete plan from Exp-Dev:
  HMM family   -> set forward/backward/(+ relevant) output to `state_distribution`
  Sequence dec -> set beam_search/viterbi/astar output to `state_sequence`
  RL family    -> introduce + assign shared `value_or_policy_object`

This v1 does the first two (HMM + sequence decoding). RL family needs a
new supertype atom which can be a follow-up.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


# operator short_id -> new signature_output_type (atomized supertype)
RETYPE_SPECS = {
    # HMM family -> state_distribution (Bayesian marginal over states)
    "forward_algorithm":   "state_distribution",
    "backward_algorithm":  "state_distribution",
    "hmm_transition":      "state_distribution",   # row of n_by_n stochastic matrix is state_distribution

    # Sequence decoding -> state_sequence (sequence of states emitted as output)
    "beam_search":         "state_sequence",
    "viterbi_decoder":     "state_sequence",
    "viterbi_decoding":    "state_sequence",
    "astar":               "state_sequence",       # path = state sequence
    "dijkstra":            "state_sequence",
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()

    # Build short_id -> list of atoms (may include T2 + T3 dups)
    by_short = {}
    for a in atoms:
        short = str(a.id).split("/")[-1].lower()
        by_short.setdefault(short, []).append(a)

    retyped_count = 0
    atoms_updated = 0
    skipped_no_atom = 0

    for short_id, new_out_type in RETYPE_SPECS.items():
        members = by_short.get(short_id, [])
        if not members:
            print(f"  SKIP_NO_ATOM: {short_id}")
            skipped_no_atom += 1
            continue
        for a in members:
            try:
                existing = dict(a.algebra) if a.algebra else {}
                old_out = existing.get("signature_output_type", "(none)")
                if old_out == new_out_type:
                    print(f"  ALREADY: {a.id} -> {new_out_type}")
                    continue
                existing["signature_output_type"] = new_out_type
                existing["retyped_from"] = old_out
                meta = dict(a.metadata) if a.metadata else {}
                meta["retyped_by"] = "retype_operator_outputs_v1"
                meta["distillation_class"] = "A_atom_removing_unlock_via_supertype_binding"
                updated = Atom(
                    id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                    description=a.description, kind=a.kind, aliases=a.aliases,
                    metadata=meta, serves_capability=a.serves_capability,
                    algebra=existing,
                )
                ps.add_atom(updated, source="retype_operator_outputs_v1",
                            note=f"Exp-Dev V2 gap closure: signature_output_type -> {new_out_type}")
                print(f"  RETYPED: {a.id}  ({old_out} -> {new_out_type})")
                atoms_updated += 1
            except Exception as e:
                print(f"  FAIL {a.id}: {str(e)[:120]}")
        retyped_count += 1

    print(f"\n=== OPERATOR OUTPUT RETYPE v1 SUMMARY ===")
    print(f"  retyped groups: {retyped_count}")
    print(f"  atoms updated: {atoms_updated}")
    print(f"  skipped (no atom): {skipped_no_atom}")
    print(f"\nNext: Exp-Dev re-runs CELL-DISTILL-VERIFY-2; HMM family + sequence_decoding")
    print(f"should now flip DISTINCT -> SHARED_ABSTRACTION. F2 projection lifts from 3.1pct.")


if __name__ == "__main__":
    main()
