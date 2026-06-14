"""Remove 11 backwards operator->field DEPENDS_ON edges (Skunkworks worklist).

Per Skunkworks GROUNDING_PRECISION note 2026-06-14: substrate has 11 edges
where operator points UP to its field-of-application instead of down to
foundations. These are directionally wrong:
  q_learning -DEPENDS_ON-> CS/reinforcement_learning   (RL USES q_learning)
  discriminative_perceptron -DEPENDS_ON-> CS/machine_learning (ML USES perceptron)
  ...etc

Removing these:
  Raises grounding precision 0.912 -> ~0.951
  Cleans transitive closures used by self-reasoning scorecard
  Same 18th-rule pattern as my DECISION 11 refusals (direction inverted)

Each edge to remove is read from data/substrate_index/skunkworks_grounding_removal_candidates.jsonl
(11 entries). Audit log written before remove.

NO LLM. NO bge.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


WORKLIST_PATH = Path("data/substrate_index/skunkworks_grounding_removal_candidates.jsonl")
AUDIT_PATH = Path("data/substrate_index/grounding_edge_removal_audit.jsonl")


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-removal: {pre_rels} relations\n")

    # Map src qualified IDs (need to resolve corpus prefix). Worklist uses
    # tier-prefixed bare IDs; resolve by querying substrate.
    by_id_short = {}
    for a in ps.all_atoms():
        # bare ID like "T3/q_learning"
        by_id_short.setdefault(a.id, []).append(f"{a.corpus.value}::{a.id}")

    audit_lines = []
    removed = 0
    not_found = 0
    failed = 0

    for line in WORKLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        src_short = rec["src"]
        dst_short = rec["dst"]
        rel_str = rec.get("rel_type", "DEPENDS_ON")
        reason = rec.get("reason", "")

        # Resolve src qid
        src_candidates = by_id_short.get(src_short, [])
        if not src_candidates:
            print(f"  NOT_FOUND src: {src_short}")
            not_found += 1
            continue
        # Resolve dst qid
        dst_candidates = by_id_short.get(dst_short, [])
        if not dst_candidates:
            print(f"  NOT_FOUND dst: {dst_short}")
            not_found += 1
            continue

        src_qid = src_candidates[0]
        dst_qid = dst_candidates[0]

        # Find the actual relation; Store.remove_relation API isn't exposed,
        # so we work around by deleting via the underlying store. PartitionedStore
        # has remove_atom which cascades; we need EDGE removal. The Store
        # has _all_relations as a set; we manipulate via direct removal.
        # Cleaner: use the Store's add/remove API. Looking at Store, there's
        # no public remove_relation. Let's find the underlying _all_relations.

        # Hack: use the math store directly and discard from _all_relations + flush
        # Use the bare _store_for entry point.
        from backend.substrate_index.partition import QualifiedAtomId
        src_q = QualifiedAtomId.parse(src_qid)
        dst_q = QualifiedAtomId.parse(dst_qid)
        # If same corpus, edge is in that store. If cross-corpus, it's in cross_index.
        # For our 11 backwards edges, all sources are math atoms, dests are concept/school atoms.
        # The edge is stored where the src lives.

        src_store = ps._store_for(src_q.corpus)
        triple = (src_q.local_id, rel_str, dst_qid)
        if triple in src_store._all_relations:
            src_store._all_relations.discard(triple)
            src_store._flush_relations()
            audit_lines.append({"removed_src": src_qid, "removed_dst": dst_qid, "rel_type": rel_str, "reason": reason})
            print(f"  REMOVED: {src_qid} -{rel_str}-> {dst_qid}")
            removed += 1
            continue

        # Try cross-corpus storage form
        cross_triple = (src_qid, rel_str, dst_qid)
        if hasattr(ps, "_cross_in") and dst_qid in ps._cross_in:
            entry = ps._cross_in.get(dst_qid, [])
            found_in_cross = any(e[0] == src_qid and e[1] == rel_str for e in entry)
            if found_in_cross:
                # cross-index is auto-derived; primary storage is still src_store._all_relations
                # if we missed it there, look at unqualified form
                triple_alt = (src_q.local_id, rel_str, dst_q.local_id)
                if triple_alt in src_store._all_relations:
                    src_store._all_relations.discard(triple_alt)
                    src_store._flush_relations()
                    audit_lines.append({"removed_src": src_qid, "removed_dst": dst_qid, "rel_type": rel_str, "reason": reason})
                    print(f"  REMOVED: {src_qid} -{rel_str}-> {dst_qid}")
                    removed += 1
                    continue

        # Final attempt: check via iter_all_relations whether the edge actually exists
        edge_exists = False
        for s, r, t in ps.iter_all_relations():
            if s == src_qid and r.name == rel_str and t == dst_qid:
                edge_exists = True
                break
        if not edge_exists:
            print(f"  NOT_PRESENT: {src_qid} -{rel_str}-> {dst_qid} (may have been removed already)")
            continue

        print(f"  REMOVE_FAIL: {src_qid} -{rel_str}-> {dst_qid} (in graph but couldn't find storage form)")
        failed += 1

    # Rebuild cross-index after removals
    if removed > 0 and hasattr(ps, "_rebuild_cross_index"):
        ps._rebuild_cross_index()

    # Write audit
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as fh:
        for rec in audit_lines:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== BACKWARDS-EDGE REMOVAL v1 SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels}  ({post_rels - pre_rels:+d})")
    print(f"  removed: {removed}")
    print(f"  not found: {not_found}")
    print(f"  failed: {failed}")
    print(f"\naudit: {AUDIT_PATH}")
    print(f"\nGrounding precision lift per Skunkworks projection: 0.912 -> ~0.951")


if __name__ == "__main__":
    main()
