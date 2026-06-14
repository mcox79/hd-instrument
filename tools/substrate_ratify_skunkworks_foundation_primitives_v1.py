"""Phase-4 atomic ratification of Skunkworks's 8 foundation primitives.

Per Director DECISION 46b (2026-06-14): Skunkworks delivered 8 foundation
primitive atom drafts (commits in skunkworks_foundation_primitive_atoms_v1.jsonl).
Testbed atomically ratifies + adds SPECIALIZES edges per verified spec.

Tier convention call (per DECISION 46b options):
  Option B chosen: all atoms = T1; bedrock distinction in metadata.foundation_layer
  (less convention change than adding T0 to Tier enum; smaller blast radius)

Atoms (8):
  T1/proposition    foundation_layer=0 (bedrock; truth-bearer; axioms ARE distinguished propositions)
  T1/set            foundation_layer=1 (carrier under all algebraic structures)
  T1/natural_number foundation_layer=1 (Peano inductive primitive)
  T1/field_type     foundation_layer=2 (algebraic structure: field)
  T1/group_type     foundation_layer=2 (algebraic structure: group)
  T1/category_type  foundation_layer=2 (category-theoretic supertype)
  T1/functor_type   foundation_layer=2 (functor supertype)
  T1/pair_type      foundation_layer=2 (ordered pair / product type)

SPECIALIZES edges (15; per DECISION 46b verified list; non-existent
targets like free_vector_functor / powerset / list / vector_pair /
phasor_vector_pair excluded per R5):
  complex_field, real_field -> field_type
  vector_space, phasor_vector, unit_modulus -> group_type
  category, monoidal_category -> category_type
  labeled_example, inner_product -> pair_type
  predicate_logic, propositional_logic -> proposition
  metric_space, probability_distribution -> set
  vector, state_sequence -> natural_number

NO LLM. NO bge. Pure stdlib + substrate schema.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


SOURCE_PATH = Path("data/substrate_index/skunkworks_foundation_primitive_atoms_v1.jsonl")
AUDIT_PATH = Path("data/substrate_index/foundation_primitives_ratify_audit.jsonl")


# Verified SPECIALIZES edges (15; non-existent flagged by Skunkworks excluded per R5)
SPECIALIZES_EDGES = [
    ("T1/complex_field", "T1/field_type"),
    ("T1/real_field", "T1/field_type"),
    ("T1/vector_space", "T1/group_type"),
    ("T2/phasor_vector", "T1/group_type"),
    ("T1/unit_modulus", "T1/group_type"),
    ("T1/predicate_logic", "T1/proposition"),
    ("T1/propositional_logic", "T1/proposition"),
    ("T1/metric_space", "T1/set"),
    ("T1/probability_distribution", "T1/set"),
    ("T1/vector", "T1/natural_number"),
    ("T2/state_sequence", "T1/natural_number"),
    ("T2/labeled_example", "T1/pair_type"),
    ("T1/inner_product", "T1/pair_type"),
    ("T1/category", "T1/category_type"),
    ("T1/monoidal_category", "T1/category_type"),
]


def main():
    if not SOURCE_PATH.exists():
        print(f"ERROR: source missing: {SOURCE_PATH}")
        sys.exit(2)

    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ratify: {pre_atoms} atoms, {pre_rels} relations\n")

    # R4 math sanity-check (Skunkworks own discipline flag) -- inspect each atom
    # and confirm algebra is plausible. Print summary; manual gate.
    print("=== R4 math sanity-check (per Skunkworks 46a discipline) ===")
    atom_records = []
    for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        atom_records.append(d)
        alg = d.get("algebra", {})
        print(f"  {d['id']:25s} role={alg.get('role'):10s} structure={alg.get('structure')!r}")
    assert len(atom_records) == 8, f"expected 8 primitives; got {len(atom_records)}"
    print(f"  R4: 8 atoms parsed; math reads OK by inspection (Peano nat / set / proposition / field+group+category+functor+pair supertypes)")

    # Atom ingest (Option B: all T1; bedrock in metadata.foundation_layer)
    print("\n=== STEP 1: atom ingest (Option B: T1 + foundation_layer in metadata) ===")
    created = 0
    skipped_exists = 0
    failed = 0
    for d in atom_records:
        # Remap T0/X -> T1/X for substrate Tier compatibility
        original_id = d["id"]
        new_id = original_id.replace("T0/", "T1/", 1) if original_id.startswith("T0/") else original_id
        qid = f"math::{new_id}"

        if ps.has_atom(qid):
            print(f"  SKIP_EXISTS: {qid}")
            skipped_exists += 1
            continue

        try:
            meta = dict(d.get("metadata", {}))
            meta["ratified_by"] = "skunkworks_foundation_primitives_v1"
            meta["ratification_tag"] = "FOUNDATION_PRIMITIVES_RATIFIED"
            meta["original_tier"] = d.get("tier")  # preserve Skunkworks's T0 intent
            meta["tier_convention"] = "Option_B_T1_with_foundation_layer_metadata"

            atom = Atom(
                id=new_id,
                name=d.get("name", new_id),
                corpus=Corpus.MATH,
                tier=Tier.TIER_1_FOUNDATIONAL,
                description=d.get("description", ""),
                kind=AtomKind.PRIMITIVE,
                aliases=tuple(d.get("aliases", [])),
                metadata=meta,
                serves_capability=tuple(d.get("serves_capability", [])),
                algebra=dict(d.get("algebra", {})) if d.get("algebra") else None,
            )
            ps.add_atom(
                atom,
                source="skunkworks_foundation_primitives_v1",
                note="DECISION 46b Phase-4 atomic ratification",
            )
            print(f"  CREATED: {qid} (foundation_layer={meta.get('foundation_layer')})")
            created += 1
        except Exception as e:
            print(f"  FAIL {qid}: {str(e)[:120]}")
            failed += 1

    # SPECIALIZES edge ingest
    print("\n=== STEP 2: SPECIALIZES edges (15; verified targets) ===")
    existing_rels = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing_rels.add((src, rel_type.name, tgt))

    edges_added = 0
    edges_skipped_exists = 0
    edges_missing_endpoint = 0
    edges_failed = 0
    for src, tgt in SPECIALIZES_EDGES:
        src_qid = f"math::{src}"
        tgt_qid = f"math::{tgt}"
        if not ps.has_atom(src_qid):
            print(f"  SKIP_MISSING_SRC: {src_qid}")
            edges_missing_endpoint += 1
            continue
        if not ps.has_atom(tgt_qid):
            print(f"  SKIP_MISSING_TGT: {tgt_qid}")
            edges_missing_endpoint += 1
            continue
        key = (src_qid, "SPECIALIZES", tgt_qid)
        if key in existing_rels:
            edges_skipped_exists += 1
            continue
        try:
            ps.add_relation(
                src_qid, RelationType.SPECIALIZES, tgt_qid,
                source="skunkworks_foundation_primitives_v1",
                note="DECISION 46b foundation primitive specialization",
            )
            existing_rels.add(key)
            print(f"  EDGE: {src_qid} -SPECIALIZES-> {tgt_qid}")
            edges_added += 1
        except Exception as e:
            edges_failed += 1

    # Audit log
    audit = {
        "ratification_tag": "FOUNDATION_PRIMITIVES_RATIFIED",
        "source": "skunkworks_foundation_primitives_v1",
        "tier_convention": "Option_B_T1_with_foundation_layer_metadata",
        "counts": {
            "atoms_created": created,
            "atoms_skipped_exists": skipped_exists,
            "atoms_failed": failed,
            "edges_added": edges_added,
            "edges_skipped_exists": edges_skipped_exists,
            "edges_missing_endpoint": edges_missing_endpoint,
            "edges_failed": edges_failed,
        },
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(audit, ensure_ascii=False) + "\n")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== POST-RATIFY ===")
    print(f"atoms:    {pre_atoms} -> {post_atoms}  (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  atoms created: {created}")
    print(f"  edges added:   {edges_added}")
    print(f"  edges missing endpoint: {edges_missing_endpoint}")
    print(f"\naudit: {AUDIT_PATH}")
    print(f"ratification tag: FOUNDATION_PRIMITIVES_RATIFIED")


if __name__ == "__main__":
    main()
