"""Pythagoras theorem (inner-product space form) cross-domain L6-PROOF chain v1.

6th cross-domain L6-PROOF chain this session. Replicates earlier pattern.

Pythagoras (inner-product space form):
  If <u, v> = 0 (orthogonal) then ||u + v||^2 = ||u||^2 + ||v||^2.

Cross-domain reach: classical Euclidean geometry <-> inner-product space (functional
analysis) <-> probability (var(X+Y) = var(X) + var(Y) when X,Y uncorrelated).

Derivation (1-step from inner-product bilinearity):
  ||u + v||^2 = <u + v, u + v>                          (definition of norm)
              = <u, u> + <u, v> + <v, u> + <v, v>      (bilinearity of <,>)
              = <u, u> + 0 + 0 + <v, v>                 (orthogonality: <u, v> = 0)
              = ||u||^2 + ||v||^2                        (definition of norm)
  QED

2 NEW T3 atoms.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


NEW_ATOMS = [
    {
        "id": "T3/inner_product_bilinearity_lemma",
        "name": "Inner product bilinearity",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("bilinear_inner_product", "ip_linear_in_both_arguments"),
        "description": (
            "Inner product <,> is linear in each argument (over the relevant field). "
            "Specifically: <a u + b w, v> = a <u, v> + b <w, v> and similarly for "
            "the second argument (with possible conjugation for complex case). "
            "Foundation for expansion arguments like Pythagoras' theorem in inner-"
            "product spaces."
        ),
        "serves_capability": ("cap_inner_product_property", "cap_bilinearity"),
        "metadata": {
            "operation_type": "typed_axiom_consequence",
            "lemma": "<au + bw, v> = a<u,v> + b<w,v>; symmetric on 2nd arg",
            "science_algebra_category": "linear_algebra::inner_product_axiom",
            "signature_hint": "bilinear_form",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "pythagoras_inner_product_chain",
        },
        "depends_on": ("math::T1/inner_product", "math::T1/vector_space"),
    },
    {
        "id": "T3/pythagoras_inner_product_synthesis",
        "name": "Pythagoras theorem (inner-product space form)",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("pythagoras_in_ip", "orthogonal_decomposition_norm_squared"),
        "description": (
            "For u, v in an inner-product space H with <u, v> = 0 (orthogonal), "
            "||u + v||^2 = ||u||^2 + ||v||^2. "
            "DERIVATION (1-step from bilinearity):\n"
            "  ||u + v||^2 = <u+v, u+v>                          (def of norm)\n"
            "              = <u,u> + <u,v> + <v,u> + <v,v>      (bilinearity)\n"
            "              = <u,u> + 0 + 0 + <v,v>               (orthogonality)\n"
            "              = ||u||^2 + ||v||^2                    (def of norm)\n"
            "  QED\n"
            "Cross-domain reach: classical Euclidean Pythagorean theorem (geometry) "
            "<-> inner-product spaces (functional analysis) <-> probability theory "
            "(variance additivity for uncorrelated random variables: "
            "Var(X+Y) = Var(X) + Var(Y) when Cov(X,Y) = 0)."
        ),
        "serves_capability": (
            "cap_pythagoras_inner_product",
            "cap_variance_additivity_uncorrelated",
            "cap_orthogonal_decomposition",
        ),
        "metadata": {
            "operation_type": "typed_theorem",
            "theorem": "<u,v> = 0  =>  ||u+v||^2 = ||u||^2 + ||v||^2",
            "science_algebra_category": "linear_algebra::pythagoras_inner_product",
            "signature_hint": "orthogonal_implies_norm_sq_additive",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "pythagoras_inner_product_chain",
            "derivation_steps": [
                "Expand <u+v, u+v> via inner_product_bilinearity",
                "<u,v> = 0 (orthogonality) zeros out cross terms",
                "Remaining: ||u+v||^2 = <u,u> + <v,v> = ||u||^2 + ||v||^2",
            ],
        },
        "depends_on": (
            "math::T3/inner_product_bilinearity_lemma",
            "math::T1/orthogonality",
            "math::T1/inner_product",
        ),
    },
]


EXISTING_EDGES = [
    # Pythagoras-in-IP is logically related to triangle_inequality (special case at orthogonality)
    ("math::T1/triangle_inequality", "math::T3/pythagoras_inner_product_synthesis"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    created = 0
    for spec in NEW_ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"  SKIP (exists): {qid}")
            continue
        try:
            atom = Atom(
                id=spec["id"], name=spec["name"], corpus=Corpus.MATH,
                tier=spec["tier"], description=spec["description"],
                kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                metadata=spec["metadata"], serves_capability=spec["serves_capability"],
            )
            ps.add_atom(atom, source="pythagoras_ip_chain_v1",
                        note="6th cross-domain L6-PROOF; geometry <-> inner-product <-> probability")
            print(f"  CREATED: {qid}")
            created += 1
        except Exception as e:
            print(f"  FAIL: {str(e)[:120]}")

    print()
    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    added = 0
    miss = 0
    for spec in NEW_ATOMS:
        src = f"math::{spec['id']}"
        if not ps.has_atom(src):
            continue
        for tgt in spec["depends_on"]:
            if not ps.has_atom(tgt):
                miss += 1
                continue
            key = (src, "DEPENDS_ON", tgt)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                                source="pythagoras_ip_chain_v1", note="pythagoras IP chain")
                print(f"  EDGE: {src} -> {tgt}")
                added += 1
                existing_edges.add(key)
            except Exception as e:
                pass

    for src, tgt in EXISTING_EDGES:
        if not ps.has_atom(src) or not ps.has_atom(tgt):
            continue
        key = (src, "DEPENDS_ON", tgt)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                            source="pythagoras_ip_chain_v1",
                            note="existing atom update")
            print(f"  UPDATE: {src} -> {tgt}")
            added += 1
            existing_edges.add(key)
        except Exception as e:
            pass

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== PYTHAGORAS-IP CHAIN SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  created: {created} added: {added} miss: {miss}")
    print(f"\nCross-domain L6-PROOF chains cumulative: 6")
    print(f"  #1 convolution, #2 Bayes, #3 CLT, #4 spectral, #5 Cauchy-Schwarz, #6 Pythagoras-IP")


if __name__ == "__main__":
    main()
