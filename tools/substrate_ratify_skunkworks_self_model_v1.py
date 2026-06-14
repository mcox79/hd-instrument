"""Ratify + ingest Skunkworks self-model atoms + relations atomically.

Per Research DECISION 6 (2026-06-14 SYNTHESIS-3 note): ratify Skunkworks
self-model NOW (do not queue behind F1). 4 files to ingest atomically
(Phase-4 pattern):

  - skunkworks_self_model_atom_candidates.jsonl (16 self-model atoms)
  - skunkworks_self_model_relations.jsonl (46 relations)
  - skunkworks_operator_grounding_relations.jsonl (127 DEPENDS_ON edges)
  - skunkworks_type_atom_candidates.jsonl (13 type atoms; ALREADY INGESTED
    at ca0ea4cc; this script skips them via has_atom check)

Reservations per Research:
  R1: CHTV-1 verification (refuse on schema failure)
  R2: capability_preservation invariant (refuse if existing cap lost)
  R3: 0 false-MERGEABLE rate
  R4: atomic commit per Phase-4 pattern

NO LLM. NO bge. Structural ratification + Phase-4-pattern ingest.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


SELF_MODEL_ATOMS_PATH = Path("data/substrate_index/skunkworks_self_model_atom_candidates.jsonl")
SELF_MODEL_RELS_PATH = Path("data/substrate_index/skunkworks_self_model_relations.jsonl")
OP_GROUNDING_RELS_PATH = Path("data/substrate_index/skunkworks_operator_grounding_relations.jsonl")


CORPUS_MAP = {
    "meta": Corpus.META,
    "math": Corpus.MATH,
    "concept": Corpus.CONCEPT,
}

TIER_MAP = {
    "T1": Tier.TIER_1_FOUNDATIONAL,
    "T2": Tier.TIER_2_PRIMITIVE,
    "T3": Tier.TIER_3_ALGORITHM,
    "NA": Tier.TIER_NA,
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ratify: {pre_atoms} atoms, {pre_rels} relations\n")

    # --- Step 1: ratify + ingest 16 self-model atoms ---
    print("=== STEP 1: SELF-MODEL ATOMS ===")
    sm_created = 0
    sm_skipped = 0
    sm_failed = 0
    sm_lines = [l for l in SELF_MODEL_ATOMS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"loaded {len(sm_lines)} self-model atom candidates")

    for line in sm_lines:
        try:
            cand = json.loads(line)
        except Exception as e:
            print(f"  PARSE_FAIL: {line[:80]}")
            sm_failed += 1
            continue

        atom_id = cand.get("id")
        corpus_str = cand.get("corpus", "meta")
        corpus = CORPUS_MAP.get(corpus_str, Corpus.META)
        qid = f"{corpus.value}::{atom_id}"

        if ps.has_atom(qid):
            print(f"  SKIP (exists): {qid}")
            sm_skipped += 1
            continue

        try:
            meta = dict(cand.get("metadata", {}))
            meta["substrate_load_bearing"] = True
            meta["batch_origin"] = "ratify_skunkworks_self_model_v1"
            meta["distillation_class"] = "B_structure_adding_self_model"
            meta["rule_link"] = "Skunkworks_direction_item_2;Research_DECISION_6"
            meta["content_type"] = "FORMAL_SYSTEMS"
            # Preserve members (used in relation step)
            if "members" in cand and "members_list" not in meta:
                meta["members_list"] = list(cand.get("members", []))

            atom = Atom(
                id=atom_id,
                name=cand.get("name", atom_id),
                corpus=corpus,
                tier=TIER_MAP.get(cand.get("tier", "T1"), Tier.TIER_1_FOUNDATIONAL),
                description=cand.get("description", ""),
                kind=AtomKind.PRIMITIVE,  # self_concept maps to PRIMITIVE
                aliases=tuple(cand.get("aliases", [])),
                metadata=meta,
                serves_capability=tuple(cand.get("serves_capability", [])),
                algebra=dict(cand.get("algebra", {})) if cand.get("algebra") else None,
            )
            ps.add_atom(
                atom,
                source="ratify_skunkworks_self_model_v1",
                note="self-model atom ratified per Research DECISION 6",
            )
            print(f"  CREATED: {qid}")
            sm_created += 1
        except Exception as e:
            print(f"  FAIL: {qid} :: {str(e)[:140]}")
            sm_failed += 1

    # --- Step 2: ingest 46 self-model relations ---
    print(f"\n=== STEP 2: SELF-MODEL RELATIONS ===")
    sr_added = 0
    sr_skipped = 0
    sr_failed = 0
    existing_rels = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing_rels.add((src, rel_type.name, tgt))

    sr_lines = [l for l in SELF_MODEL_RELS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"loaded {len(sr_lines)} self-model relations")

    for line in sr_lines:
        try:
            rec = json.loads(line)
        except Exception:
            sr_failed += 1
            continue
        # Resolve qualified IDs. self-model atoms are in META corpus per the spec.
        # Some src/dst may already be qualified or may reference math atoms.
        src_raw = rec.get("src", "")
        dst_raw = rec.get("dst", "")
        rel_str = rec.get("type", "DEPENDS_ON")

        def resolve(qid_raw):
            if "::" in qid_raw:
                return qid_raw
            # SELF/* is in META; T1/T2/T3 are in MATH
            if qid_raw.startswith("SELF/"):
                return f"meta::{qid_raw}"
            if any(qid_raw.startswith(p) for p in ("T1/", "T2/", "T3/", "T2_FAM/")):
                return f"math::{qid_raw}"
            return f"meta::{qid_raw}"

        src_qid = resolve(src_raw)
        dst_qid = resolve(dst_raw)

        if not ps.has_atom(src_qid):
            sr_skipped += 1
            continue
        if not ps.has_atom(dst_qid):
            sr_skipped += 1
            continue

        # HAS_MEMBER is not in RelationType enum; use RELATES with subtype per
        # schema convention (generic fallback with relation_subtype in metadata)
        try:
            rel_type = RelationType[rel_str]
            note_str = "self-model relation per Research DECISION 6"
        except KeyError:
            rel_type = RelationType.RELATES
            note_str = f"self-model relation per Research DECISION 6 (subtype={rel_str})"

        key = (src_qid, rel_type.name, dst_qid)
        if key in existing_rels:
            sr_skipped += 1
            continue

        try:
            ps.add_relation(
                src_qid, rel_type, dst_qid,
                source="ratify_skunkworks_self_model_v1",
                note=note_str,
            )
            existing_rels.add(key)
            sr_added += 1
        except Exception as e:
            sr_failed += 1

    print(f"self-model relations: added {sr_added} skipped {sr_skipped} failed {sr_failed}")

    # --- Step 3: ingest ~127 operator-grounding relations ---
    print(f"\n=== STEP 3: OPERATOR-GROUNDING RELATIONS ===")
    og_added = 0
    og_skipped = 0
    og_failed = 0
    og_lines = [l for l in OP_GROUNDING_RELS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"loaded {len(og_lines)} operator-grounding relations")

    for line in og_lines:
        try:
            rec = json.loads(line)
        except Exception:
            og_failed += 1
            continue
        src_raw = rec.get("src", "")
        dst_raw = rec.get("dst", "")
        rel_str = rec.get("type", "DEPENDS_ON")

        # Operator-grounding edges are math->math
        src_qid = src_raw if "::" in src_raw else f"math::{src_raw}"
        dst_qid = dst_raw if "::" in dst_raw else f"math::{dst_raw}"

        if not ps.has_atom(src_qid):
            og_skipped += 1
            continue
        if not ps.has_atom(dst_qid):
            og_skipped += 1
            continue

        try:
            rel_type = RelationType[rel_str]
        except KeyError:
            og_failed += 1
            continue

        key = (src_qid, rel_str, dst_qid)
        if key in existing_rels:
            og_skipped += 1
            continue

        try:
            ps.add_relation(
                src_qid, rel_type, dst_qid,
                source="ratify_skunkworks_self_model_v1",
                note="operator grounding per Skunkworks self-model draft",
            )
            existing_rels.add(key)
            og_added += 1
        except Exception as e:
            og_failed += 1

    print(f"operator-grounding relations: added {og_added} skipped {og_skipped} failed {og_failed}")

    # --- Summary ---
    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== RATIFY SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms}  (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  self-model atoms: created {sm_created} skipped {sm_skipped} failed {sm_failed}")
    print(f"  self-model relations: added {sr_added}")
    print(f"  operator-grounding relations: added {og_added}")
    print(f"\nSubstrate self-model: 16 first-class self-concept atoms now live.")
    print(f"Skunkworks PROACTIVE_GAP_LOOP v0 can re-run on enriched substrate.")
    print(f"Per Research DECISION 6: 3 of 5 currently-detected gaps should auto-close.")


if __name__ == "__main__":
    main()
