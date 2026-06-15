"""DECISION 49c: ratify 14 qclass atoms from Skunkworks (closes 5133 missing-endpoint edges).

Source: data/substrate_index/skunkworks_qclass_atoms_v1.jsonl
Each atom T1/wikidata_qclass_Qxxx; SPECIALIZES T1/category_type.

R2 check: held-out gold (active_inference / free_energy_principle /
predictive_coding / CAP_pos_tagging) collision check.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


SOURCE_PATH = Path("data/substrate_index/skunkworks_qclass_atoms_v1.jsonl")
AUDIT_PATH = Path("data/substrate_index/qclass_atoms_49c_ratify_audit.jsonl")

HELDOUT_GOLD = {"active_inference", "free_energy_principle", "predictive_coding",
                "variational_free_energy", "cap_pos_tagging", "cap_ner", "cap_chunking"}


def main():
    if not SOURCE_PATH.exists():
        print(f"ERROR: source missing: {SOURCE_PATH}")
        sys.exit(2)

    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ratify: {pre_atoms} atoms, {pre_rels} relations\n")

    created = 0
    skipped_exists = 0
    failed = 0
    r2_rejections = 0
    spec_edges_added = 0

    for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        atom_id = d["id"]

        # R2 check
        text = f"{atom_id} {d.get('name','')} {' '.join(d.get('aliases', []))}".lower()
        if any(g in text for g in HELDOUT_GOLD):
            print(f"  R2_REJECT: {atom_id} (held-out collision)")
            r2_rejections += 1
            continue

        qid = f"math::{atom_id}"
        if ps.has_atom(qid):
            skipped_exists += 1
            continue

        try:
            meta = dict(d.get("metadata", {}))
            meta["ratified_by"] = "ratify_qclass_atoms_49c_v1"
            meta["ratification_tag"] = "INGEST_PHASE_6_qclass_49c"
            atom = Atom(
                id=atom_id, name=d.get("name", atom_id),
                corpus=Corpus.MATH, tier=Tier.TIER_1_FOUNDATIONAL,
                description=d.get("description", ""),
                kind=AtomKind.PRIMITIVE,
                aliases=tuple(d.get("aliases", [])),
                metadata=meta,
                serves_capability=tuple(d.get("serves_capability", [])),
                algebra=dict(d.get("algebra", {})) if d.get("algebra") else None,
            )
            ps.add_atom(atom, source="ratify_qclass_atoms_49c_v1",
                        note="DECISION 49c qclass atom ratified")
            created += 1
            print(f"  CREATED: {qid}")

            # SPECIALIZES T1/category_type per spec
            spec_tgt = "math::T1/category_type"
            if ps.has_atom(spec_tgt):
                try:
                    ps.add_relation(qid, RelationType.SPECIALIZES, spec_tgt,
                                    source="ratify_qclass_atoms_49c_v1",
                                    note="qclass SPECIALIZES category_type bedrock supertype")
                    spec_edges_added += 1
                except Exception:
                    pass
        except Exception as e:
            print(f"  FAIL {atom_id}: {str(e)[:80]}")
            failed += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    audit = {
        "ratification_tag": "INGEST_PHASE_6_qclass_49c",
        "counts": {"created": created, "skipped_exists": skipped_exists,
                   "failed": failed, "r2_rejections": r2_rejections,
                   "spec_edges_added": spec_edges_added}
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(audit, ensure_ascii=False) + "\n")
    print(f"\natoms: {pre_atoms} -> {post_atoms} (+{post_atoms-pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels-pre_rels})")
    print(f"  created: {created}  spec edges: {spec_edges_added}")
    print(f"  R2 rejections: {r2_rejections}  failed: {failed}")


if __name__ == "__main__":
    main()
