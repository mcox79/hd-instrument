"""DECISION 54: re-ratify wikidata atoms IN PLACE with real-label aliases.

Per Exp-Dev DECISION 49b FIX (commit fix): 5360 wikidata atoms had
PLACEHOLDER names ("wikidata Qxxx") -> bge-invisible blob. Mapper fixed
to carry real labels into aliases (id STABLE; aliases=[label, Qid]).

Verified by Exp-Dev: median cosine 0.910 (blob) -> 0.663 (distinguishable).

Phase-4 atomic re-ratification: substrate's add_atom upserts by id, so
re-running with same ids updates the existing atoms in place (aliases
field overwritten with new [label, Qid] tuple).

Expected: atom count stays ~26,272 (UPDATE, not +5510).

NO LLM. NO bge.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


SOURCE_PATH = Path("data/substrate_state/wikidata_action_api_v2_relabeled_adapted.jsonl")
AUDIT_PATH = Path("data/substrate_index/ingest_audit_wikidata_relabel_v1.jsonl")

HELDOUT_GOLD_SUBSTRINGS = {
    "active_inference", "free_energy_principle", "predictive_coding",
    "variational_free_energy",
    "CAP_pos_tagging", "CAP_ner", "CAP_chunking",
}


def main():
    if not SOURCE_PATH.exists():
        print(f"ERROR: source missing: {SOURCE_PATH}")
        sys.exit(2)

    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-reratify: {pre_atoms} atoms, {pre_rels} relations\n")

    # R2 audit on new labels (now that real labels exposed)
    r2_rejections = []
    atom_records = []
    for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        text_to_check = f"{d.get('id','')} {d.get('name','')} {' '.join(d.get('aliases', []))}"
        text_lower = text_to_check.lower()
        if any(g.lower() in text_lower for g in HELDOUT_GOLD_SUBSTRINGS):
            r2_rejections.append(d.get("id"))
            continue
        atom_records.append(d)
    print(f"R2 GATE (on real labels): {len(r2_rejections)} rejections; {len(atom_records)} pass")

    print("\n=== STEP 1: re-ratify atoms IN PLACE (upsert by id) ===")
    updated = 0
    created = 0
    failed = 0
    spot_check_atom_id = None
    spot_check_aliases_before = None
    spot_check_aliases_after = None

    for d in atom_records:
        atom_id = d["id"]
        corpus_str = d.get("corpus", "math").upper()
        try:
            corpus = Corpus[corpus_str]
        except KeyError:
            failed += 1
            continue
        qid = f"{corpus.value}::{atom_id}"

        # Spot-check: capture state before/after for Q182505 (Bayes' theorem)
        is_spot = atom_id.endswith("Q182505")
        if is_spot:
            existing = ps.get_atom(qid)
            if existing:
                spot_check_aliases_before = list(existing.aliases or [])
                spot_check_atom_id = atom_id

        try:
            existed = ps.has_atom(qid)
            meta = dict(d.get("metadata", {}))
            meta["relabeled_by"] = "reratify_wikidata_relabel_v1"
            meta["ratification_tag"] = "INGEST_PHASE_6_wikidata_action_api_RELABEL"
            atom = Atom(
                id=atom_id,
                name=d.get("name", atom_id),
                corpus=corpus,
                tier=Tier.TIER_3_ALGORITHM,
                description=d.get("description", ""),
                kind=AtomKind.PRIMITIVE,
                aliases=tuple(d.get("aliases", [])),
                metadata=meta,
                serves_capability=tuple(d.get("serves_capability", [])),
                algebra=dict(d.get("algebra", {})) if d.get("algebra") else None,
            )
            ps.add_atom(
                atom,
                source="wikidata_relabel_v1",
                note="DECISION 54 in-place relabel (aliases carry real label; id stable)",
            )
            if existed:
                updated += 1
            else:
                created += 1
            if is_spot:
                spot_check_aliases_after = list(d.get("aliases", []))
        except Exception as e:
            failed += 1

    audit = {
        "ratification_tag": "INGEST_PHASE_6_wikidata_action_api_RELABEL",
        "source": "exp_dev_DECISION_49b_FIX_handoff",
        "counts": {
            "r2_rejections": len(r2_rejections),
            "atoms_updated_in_place": updated,
            "atoms_newly_created": created,
            "atoms_failed": failed,
        },
        "spot_check": {
            "atom_id": spot_check_atom_id,
            "aliases_before": spot_check_aliases_before,
            "aliases_after": spot_check_aliases_after,
        },
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(audit, ensure_ascii=False) + "\n")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== POST-RERATIFY ===")
    print(f"atoms:    {pre_atoms} -> {post_atoms}  (delta: {post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels}")
    print(f"  atoms updated in place: {updated}")
    print(f"  atoms newly created:    {created}")
    print(f"  R2 rejections:          {len(r2_rejections)}")
    print(f"  failed:                 {failed}")
    print(f"\nSPOT CHECK ({spot_check_atom_id}):")
    print(f"  aliases BEFORE: {spot_check_aliases_before}")
    print(f"  aliases AFTER:  {spot_check_aliases_after}")
    print(f"\nratification tag: INGEST_PHASE_6_wikidata_action_api_RELABEL")


if __name__ == "__main__":
    main()
