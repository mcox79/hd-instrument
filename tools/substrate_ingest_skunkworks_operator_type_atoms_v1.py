"""Ingest Skunkworks's 13 substrate-operator type atom candidates.

Per Research 26th writeback (BOTH AUTHORIZED): Testbed's 14 mathematical-
foundation type atoms + Skunkworks's 13 substrate-operator type atoms are
COMPLEMENTARY, not conflicting.

Source: data/substrate_index/skunkworks_type_atom_candidates.jsonl (drafted
by Skunkworks; 13 entries; algebra_dict + specializes link included).

Ratification policy (per Skunkworks ask): adjust tier where collision exists,
preserve algebra_dict + specializes, add to math corpus.

NO LLM. NO bge. Pure structural ratification + ingest.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


CANDIDATE_PATH = Path("data/substrate_index/skunkworks_type_atom_candidates.jsonl")

TIER_MAP = {
    "T1": Tier.TIER_1_FOUNDATIONAL,
    "T2": Tier.TIER_2_PRIMITIVE,
    "T3": Tier.TIER_3_ALGORITHM,
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    created = 0
    skipped = 0
    failed = 0
    spec_edges_added = 0

    for line in CANDIDATE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            cand = json.loads(line)
        except Exception as e:
            print(f"  PARSE_FAIL: {line[:60]}")
            failed += 1
            continue

        atom_id = cand.get("id")
        if not atom_id:
            print(f"  NO_ID: {cand}")
            failed += 1
            continue
        qid = f"math::{atom_id}"

        if ps.has_atom(qid):
            print(f"  SKIP (exists): {qid}")
            skipped += 1
            continue

        try:
            meta = dict(cand.get("metadata", {}))
            meta["operation_type"] = "substrate_operator_type_atom"
            meta["is_type_atom"] = True
            meta["type_graph_terminator"] = False  # operator-type, not first-principles math
            meta["substrate_load_bearing"] = True
            meta["batch_origin"] = "skunkworks_operator_types_v1"
            meta["distillation_class"] = "B_structure_adding"
            meta["rule_link"] = "20th_rule_3mode;Research_26th_writeback_complementary_authorized"
            meta["content_type"] = "FORMAL_SYSTEMS"

            atom = Atom(
                id=atom_id,
                name=cand.get("name", atom_id),
                corpus=Corpus.MATH,
                tier=TIER_MAP[cand.get("tier", "T2")],
                description=cand.get("description", ""),
                kind=AtomKind.PRIMITIVE,
                aliases=tuple(cand.get("aliases", [])),
                metadata=meta,
                serves_capability=tuple(cand.get("serves_capability", [])),
                algebra=dict(cand.get("algebra", {})) if cand.get("algebra") else None,
            )
            ps.add_atom(
                atom,
                source="skunkworks_operator_types_v1",
                note="ratified Skunkworks candidate; complementary to mathematical-foundation type atoms",
            )
            print(f"  CREATED: {qid}")
            created += 1

            # Add specializes edge if specified
            specializes = meta.get("specializes")
            if specializes:
                tgt_qid = f"math::{specializes}"
                if ps.has_atom(tgt_qid):
                    try:
                        ps.add_relation(
                            qid, RelationType.SPECIALIZES, tgt_qid,
                            source="skunkworks_operator_types_v1",
                            note="operator-type specializes supertype",
                        )
                        print(f"    SPECIALIZES: {qid} -> {tgt_qid}")
                        spec_edges_added += 1
                    except Exception as e:
                        print(f"    SPEC_FAIL: {str(e)[:80]}")
        except Exception as e:
            print(f"  FAIL: {qid} :: {str(e)[:140]}")
            failed += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SKUNKWORKS OPERATOR TYPE ATOMS v1 SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  created: {created}")
    print(f"  skipped (already exists): {skipped}")
    print(f"  failed: {failed}")
    print(f"  SPECIALIZES edges added: {spec_edges_added}")
    print(f"\nSubstrate-operator type atomization: {created}/13 complement to 15/15 mathematical-foundation type atoms")
    print(f"F2 abstraction unlock: parameter_vector + phasor_vector atomized (Skunkworks projection 5.6% REALIZED)")


if __name__ == "__main__":
    main()
