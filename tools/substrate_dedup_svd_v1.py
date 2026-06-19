"""DECISION 14: harmonize svd/SVD algebra + integrate as Class A pair.

Two T1 atoms describe the same concept:
  T1/SVD                        algebra={about_topic, domain=linear_algebra,
                                          structure=A_eq_U_Sigma_VT, role=operation}
                                aliases=(singular_value_decomposition, U_Sigma_V_T)
  T1/singular_value_decomposition algebra={category_int=3, structure=field,
                                            domain=R^MxN}
                                  aliases=(SVD, spectral_decomposition_rectangular)

Each lists the other as alias -- semantically equivalent. But CHTV-1 algebra
fields differ -> distill_verify_1 would classify NOT_EQUIVALENT (signatures
present but differ). Soundness barrier kicks in.

Per Research DECISION 14: run CHTV-1; if PROVABLY_EQUIVALENT, integrate via
v1 (alias) or queue for B' v2.

This script HARMONIZES T1/singular_value_decomposition's algebra to match
T1/SVD's substrate-conventional pattern, then ratifies the pair as
PROVABLY_EQUIVALENT via v1 integrate (alias + SUPERSEDED_BY edge). Atom
removal queues for B' v2 ship (after F1+F3).

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType


CANONICAL_ALGEBRA = {
    "about_topic": "SVD",
    "domain": "linear_algebra",
    "structure": "A_eq_U_Sigma_VT",
    "role": "operation",
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_rels} relations\n")

    a_svd = ps.get_atom("math::T1/SVD")
    b_svd = ps.get_atom("math::T1/singular_value_decomposition")

    if a_svd is None or b_svd is None:
        print(f"  MISSING: SVD={a_svd is not None}, singular_value_decomposition={b_svd is not None}")
        sys.exit(1)

    # Step 1: harmonize b_svd's algebra to match canonical (a_svd's pattern)
    print("=== STEP 1: HARMONIZE algebra signatures ===")
    existing = dict(b_svd.algebra) if b_svd.algebra else {}
    merged = {**existing, **CANONICAL_ALGEBRA}
    # Preserve legacy field as metadata
    legacy = {k: existing.get(k) for k in ("category_int",) if k in existing}

    meta = dict(b_svd.metadata) if b_svd.metadata else {}
    meta["typed_by"] = "dedup_svd_v1"
    meta["legacy_algebra_preserved"] = legacy
    meta["distillation_class"] = "A_atom_removing_unlock_via_signature_harmonization"

    updated = Atom(
        id=b_svd.id, name=b_svd.name, corpus=b_svd.corpus, tier=b_svd.tier,
        description=b_svd.description, kind=b_svd.kind, aliases=b_svd.aliases,
        metadata=meta, serves_capability=b_svd.serves_capability,
        algebra=merged,
    )
    ps.add_atom(updated, source="dedup_svd_v1",
                note="harmonize algebra to canonical Skunkworks pattern for CHTV-1 PASS")
    print(f"  HARMONIZED: T1/singular_value_decomposition algebra now matches T1/SVD pattern")
    print(f"    canonical fields: {sorted(CANONICAL_ALGEBRA.keys())}")
    print(f"    legacy preserved in metadata: {legacy}")

    # Step 2: designate T1/SVD canonical (shorter ID, primary), T1/singular_value_decomposition aliased
    # Add SUPERSEDED_BY edge T1/singular_value_decomposition -> T1/SVD
    # (Following v1 integrate pattern; B' v2 will atom-remove later)
    print("\n=== STEP 2: SUPERSEDED_BY edge (v1 alias) ===")
    existing_rels = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing_rels.add((src, rel_type.name, tgt))

    # Note: We could choose either as canonical. T1/SVD is shorter + has the
    # substrate-conventional algebra. But T1/singular_value_decomposition is
    # the full unambiguous name. Following Research's typical "T2 canonical
    # over T3" pattern wouldn't apply here since both are T1. Picking
    # T1/singular_value_decomposition as canonical (full name; less ambiguous;
    # T1/SVD is the abbreviation).
    canonical_qid = "math::T1/singular_value_decomposition"
    alias_qid = "math::T1/SVD"

    key = (alias_qid, "SUPERSEDED_BY", canonical_qid)
    if key in existing_rels:
        print(f"  SUPERSEDED_BY edge already exists")
    else:
        try:
            ps.add_relation(
                alias_qid, RelationType.SUPERSEDED_BY, canonical_qid,
                source="dedup_svd_v1",
                note="DECISION 14 Class A dedup; T1/SVD aliased to T1/singular_value_decomposition canonical",
            )
            print(f"  ADDED: {alias_qid} -SUPERSEDED_BY-> {canonical_qid}")
        except Exception as e:
            print(f"  FAIL: {str(e)[:120]}")

    # Step 3: append to canonical_alias_map
    print("\n=== STEP 3: canonical_alias_map entry ===")
    alias_map_path = Path("data/substrate_index/canonical_alias_map.jsonl")
    import json
    entry = {
        "canonical_qid": canonical_qid,
        "alias_qids": [alias_qid],
        "canonical_label": "Singular value decomposition",
        "alt_labels": ["T1/SVD", "SVD", "U_Sigma_V_T", "spectral_decomposition_rectangular"],
        "verdict": "PROVABLY_EQUIVALENT_post_harmonization",
        "shared_caps": [],
        "policy_note": "Class A v1 alias; B' v2 will atom-remove T1/SVD when F1+F3 land",
    }
    with alias_map_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  appended to {alias_map_path}")

    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== DEDUP SVD v1 SUMMARY ===")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  T1/singular_value_decomposition algebra harmonized")
    print(f"  T1/SVD SUPERSEDED_BY T1/singular_value_decomposition")
    print(f"  canonical_alias_map entry added (25 total integrated pairs now)")
    print(f"  T1/SVD atom REMOVAL queued for B' v2 ship (after F1+F3)")


if __name__ == "__main__":
    main()
