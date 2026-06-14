"""Phase-4 atomic ratification of Exp-Dev's wikidata action-API ingest.

Per DECISION 45 step 5 (handoff from Exp-Dev): 5510 atoms + 5510 DEPENDS_ON
edges fetched via Wikidata action API (bypassed WDQS outage); Q-classes
validated; R2-clean (held-out gold excluded); quality-clean (manual sample).

Pipeline:
  1. Parse adapted JSONL files (atoms + relations)
  2. R2 belt-and-suspenders gate: refuse any atom that names held-out gold
  3. Phase-4 pattern: ps.add_atom + ps.add_relation per item
  4. Audit log: counts + R3 invariant pre/post

NO LLM. NO bge. NO torch. Pure stdlib + substrate schema.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


ATOMS_PATH = Path("data/substrate_state/wikidata_action_api_v1_adapted.jsonl")
RELS_PATH = Path("data/substrate_state/wikidata_action_api_v1_adapted_relations.jsonl")
AUDIT_PATH = Path("data/substrate_index/ingest_audit_wikidata_action_api_v1.jsonl")


# R2 held-out gold atom names (from F1 RETRACTION); reject any of these
HELDOUT_GOLD_SUBSTRINGS = {
    "active_inference", "free_energy_principle", "predictive_coding",
    "variational_free_energy", "kl_divergence",
    # CAP atoms; not in this slice but defensive
    "CAP_pos_tagging", "CAP_ner", "CAP_chunking",
}


def main():
    if not ATOMS_PATH.exists() or not RELS_PATH.exists():
        print(f"ERROR: handoff files missing")
        print(f"  atoms:     {ATOMS_PATH.exists()}: {ATOMS_PATH}")
        print(f"  relations: {RELS_PATH.exists()}: {RELS_PATH}")
        sys.exit(2)

    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ratify substrate state: {pre_atoms} atoms, {pre_rels} relations\n")

    # R2 belt-and-suspenders gate
    print("=== R2 GATE: held-out gold check ===")
    r2_rejections = []
    atom_records = []
    for line in ATOMS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception as e:
            print(f"  PARSE_FAIL: {line[:80]}")
            continue
        # Check for held-out gold contamination in id / name / aliases
        text_to_check = f"{d.get('id','')} {d.get('name','')} {' '.join(d.get('aliases', []))}"
        text_lower = text_to_check.lower()
        if any(g.lower() in text_lower for g in HELDOUT_GOLD_SUBSTRINGS):
            r2_rejections.append(d.get("id"))
            continue
        atom_records.append(d)
    print(f"  parsed atoms: {len(atom_records) + len(r2_rejections)}")
    print(f"  R2 rejections: {len(r2_rejections)}")
    print(f"  passed R2 gate: {len(atom_records)}")
    if r2_rejections:
        print(f"  WARN: rejected ids: {r2_rejections[:5]}")

    # Phase-4 atom ingest
    print("\n=== STEP 5a: atom ingest (Phase-4 pattern) ===")
    created = 0
    skipped_exists = 0
    failed = 0
    for d in atom_records:
        atom_id = d["id"]
        corpus_str = d.get("corpus", "math").upper()
        try:
            corpus = Corpus[corpus_str]
        except KeyError:
            print(f"  SKIP_BAD_CORPUS: {atom_id} corpus={corpus_str}")
            failed += 1
            continue

        qid = f"{corpus.value}::{atom_id}"
        if ps.has_atom(qid):
            skipped_exists += 1
            continue

        try:
            tier_str = d.get("tier", "T3").upper()
            tier_map = {"T1": Tier.TIER_1_FOUNDATIONAL,
                        "T2": Tier.TIER_2_PRIMITIVE,
                        "T3": Tier.TIER_3_ALGORITHM,
                        "NA": Tier.TIER_NA}
            tier = tier_map.get(tier_str, Tier.TIER_3_ALGORITHM)
            kind_map = {"PRIMITIVE": AtomKind.PRIMITIVE,
                        "FAMILY_TAG": AtomKind.FAMILY_TAG,
                        "SUB_OP": AtomKind.SUB_OP,
                        "MACRO": AtomKind.MACRO}
            kind = kind_map.get(d.get("kind", "PRIMITIVE"), AtomKind.PRIMITIVE)
            meta = dict(d.get("metadata", {}))
            meta["ratified_by"] = "substrate_ratify_wikidata_action_api_v1"
            meta["ratification_tag"] = "INGEST_PHASE_6_wikidata_action_api_v1"
            atom = Atom(
                id=atom_id,
                name=d.get("name", atom_id),
                corpus=corpus,
                tier=tier,
                description=d.get("description", ""),
                kind=kind,
                aliases=tuple(d.get("aliases", [])),
                metadata=meta,
                serves_capability=tuple(d.get("serves_capability", [])),
                algebra=dict(d.get("algebra", {})) if d.get("algebra") else None,
            )
            ps.add_atom(
                atom,
                source="wikidata_action_api_v1",
                note="DECISION 45 step 5 Phase-4 atomic ratification",
            )
            created += 1
        except Exception as e:
            print(f"  ATOM_FAIL {atom_id}: {str(e)[:120]}")
            failed += 1

    print(f"  atoms created:  {created}")
    print(f"  atoms skipped:  {skipped_exists}")
    print(f"  atoms failed:   {failed}")

    # Phase-4 relation ingest
    print("\n=== STEP 5b: relation ingest ===")
    edges_added = 0
    edges_skipped = 0
    edges_failed = 0
    edges_missing_endpoint = 0
    existing_rels = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing_rels.add((src, rel_type.name, tgt))

    for line in RELS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            edges_failed += 1
            continue
        src = d["src"]
        tgt = d["tgt"]
        rel_str = d.get("rel_type", "DEPENDS_ON")
        if not ps.has_atom(src) or not ps.has_atom(tgt):
            edges_missing_endpoint += 1
            continue
        key = (src, rel_str, tgt)
        if key in existing_rels:
            edges_skipped += 1
            continue
        try:
            rel_type = RelationType[rel_str]
            ps.add_relation(
                src, rel_type, tgt,
                source="wikidata_action_api_v1",
                note="DECISION 45 step 5 ratified DEPENDS_ON edge",
            )
            existing_rels.add(key)
            edges_added += 1
        except Exception as e:
            edges_failed += 1

    print(f"  edges added:           {edges_added}")
    print(f"  edges skipped:         {edges_skipped}")
    print(f"  edges missing endpoint: {edges_missing_endpoint}")
    print(f"  edges failed:          {edges_failed}")

    # Audit log
    audit = {
        "ratified_at_ts": None,  # filled by caller; module is deterministic
        "ratification_tag": "INGEST_PHASE_6_wikidata_action_api_v1",
        "source": "exp_dev_DECISION_45_handoff",
        "files": {
            "atoms": str(ATOMS_PATH),
            "relations": str(RELS_PATH),
        },
        "counts": {
            "atoms_parsed": len(atom_records) + len(r2_rejections),
            "r2_rejections": len(r2_rejections),
            "atoms_created": created,
            "atoms_skipped_exists": skipped_exists,
            "atoms_failed": failed,
            "edges_added": edges_added,
            "edges_skipped_exists": edges_skipped,
            "edges_missing_endpoint": edges_missing_endpoint,
            "edges_failed": edges_failed,
        },
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(audit, ensure_ascii=False) + "\n")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== POST-RATIFY substrate state ===")
    print(f"atoms:    {pre_atoms} -> {post_atoms}  (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"\naudit: {AUDIT_PATH}")
    print(f"ratification tag: INGEST_PHASE_6_wikidata_action_api_v1")


if __name__ == "__main__":
    main()
