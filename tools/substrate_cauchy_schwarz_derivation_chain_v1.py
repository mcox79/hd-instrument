"""Cauchy-Schwarz inequality cross-domain L6-PROOF derivation chain v1.

5th cross-domain L6-PROOF chain this session. Replicates earlier pattern.

Cauchy-Schwarz: |<u, v>|^2 <= <u, u> * <v, v>

Cross-domain reach: inner-product spaces (functional analysis) <->
probability (covariance bound: cov(X,Y)^2 <= var(X) var(Y)) <->
geometry (cosine angle bound: |cos theta| <= 1).

Standard derivation via quadratic discriminant:
  Premise 1 (inner product is positive semidefinite):
    <u - t v, u - t v> >= 0 for all real t

  Premise 2 (expand the inner product):
    <u - t v, u - t v> = <u,u> - 2 t <u,v> + t^2 <v,v>

  Synthesis: this quadratic in t is >= 0 for all t,
    so its discriminant is <= 0:
    (2<u,v>)^2 - 4 <u,u> <v,v> <= 0
    <u,v>^2 <= <u,u> <v,v>
    QED

3 NEW T3 atoms; substrate already has T1/cauchy_schwarz_inequality.

NO LLM. NO bge. Pure schema authoring.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


NEW_ATOMS = [
    {
        "id": "T3/inner_product_positive_semidefinite_lemma",
        "name": "Inner product positive semidefiniteness",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("ip_psd", "norm_squared_nonneg"),
        "description": (
            "For any vector w in an inner-product space H, <w, w> >= 0, with "
            "equality iff w = 0. This is the positive-semidefinite axiom of inner "
            "products. Used in the standard Cauchy-Schwarz derivation via the "
            "quadratic discriminant trick."
        ),
        "serves_capability": ("cap_inner_product_property",),
        "metadata": {
            "operation_type": "typed_axiom_consequence",
            "lemma": "<w, w> >= 0; <w, w> = 0 iff w = 0",
            "science_algebra_category": "linear_algebra::inner_product_axiom",
            "signature_hint": "psd_inner_product",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "cauchy_schwarz_chain",
        },
        "depends_on": ("math::T1/inner_product", "math::T1/vector_space"),
    },
    {
        "id": "T3/quadratic_nonnegative_discriminant_lemma",
        "name": "Nonnegative quadratic has nonpositive discriminant",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("quad_nonneg_disc_le_0", "discriminant_test"),
        "description": (
            "If q(t) = a t^2 + b t + c with a >= 0 and q(t) >= 0 for all real t, "
            "then the discriminant b^2 - 4 a c <= 0. "
            "Proof: if the discriminant were positive, q would have two distinct "
            "real roots and would be negative between them, contradicting q(t) >= 0."
        ),
        "serves_capability": ("cap_quadratic_property",),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "a>=0, q(t) = a t^2 + b t + c >= 0 for all t  =>  b^2 - 4 a c <= 0",
            "science_algebra_category": "algebra::quadratic_property",
            "signature_hint": "nonneg_quad_discriminant_test",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "cauchy_schwarz_chain",
        },
        "depends_on": ("math::T1/real_field",),
    },
    {
        "id": "T3/cauchy_schwarz_synthesis",
        "name": "Cauchy-Schwarz inequality (typed synthesis)",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("cauchy_schwarz_proof_chain", "bunyakovsky_inequality"),
        "description": (
            "For u, v in an inner-product space H: |<u, v>|^2 <= <u, u> * <v, v>. "
            "DERIVATION (quadratic discriminant trick):\n"
            "  P1 (inner_product_positive_semidefinite): <u - t v, u - t v> >= 0 for all t in R\n"
            "  P2 (expand by bilinearity): <u - tv, u - tv> = <u,u> - 2 t <u,v> + t^2 <v,v>\n"
            "  P3 (quadratic_nonnegative_discriminant): quadratic q(t) = <v,v> t^2 - 2 <u,v> t + <u,u> "
            "is >= 0 for all t, so discriminant <= 0\n"
            "  Compute discriminant: (-2<u,v>)^2 - 4 <v,v> <u,u> = 4 <u,v>^2 - 4 <u,u><v,v> <= 0\n"
            "  Therefore: <u,v>^2 <= <u,u> <v,v>\n"
            "  Equivalently: |<u,v>| <= ||u|| ||v|| (taking square root)\n"
            "  QED\n"
            "Cross-domain implications: |cos(angle(u,v))| <= 1 (geometry), "
            "cov(X,Y)^2 <= var(X) var(Y) (probability), |int f g| <= ||f||_2 ||g||_2 (analysis)."
        ),
        "serves_capability": (
            "cap_inner_product_inequality",
            "cap_covariance_bound",
            "cap_cosine_bound",
        ),
        "metadata": {
            "operation_type": "typed_theorem",
            "theorem": "|<u,v>|^2 <= <u,u> <v,v>  (Cauchy-Schwarz)",
            "science_algebra_category": "linear_algebra::cauchy_schwarz_derivation",
            "signature_hint": "inner_product_bilinear_inequality",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "cauchy_schwarz_chain",
            "derivation_steps": [
                "inner_product_positive_semidefinite: <u-tv, u-tv> >= 0",
                "expand: <u,u> - 2t<u,v> + t^2 <v,v> >= 0 for all t",
                "quadratic_nonneg_discriminant: 4<u,v>^2 - 4<u,u><v,v> <= 0",
                "Therefore <u,v>^2 <= <u,u><v,v>",
            ],
        },
        "depends_on": (
            "math::T3/inner_product_positive_semidefinite_lemma",
            "math::T3/quadratic_nonnegative_discriminant_lemma",
            "math::T1/inner_product",
            "math::T1/cosine_similarity",
        ),
    },
]


EXISTING_EDGES = [
    ("math::T1/cauchy_schwarz_inequality", "math::T3/cauchy_schwarz_synthesis"),
    # Cross-domain implication: triangle_inequality follows from Cauchy-Schwarz in inner-product spaces
    ("math::T1/triangle_inequality", "math::T3/cauchy_schwarz_synthesis"),
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
            print(f"  ATOM SKIP (exists): {qid}")
            continue
        try:
            atom = Atom(
                id=spec["id"], name=spec["name"], corpus=Corpus.MATH,
                tier=spec["tier"], description=spec["description"],
                kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                metadata=spec["metadata"], serves_capability=spec["serves_capability"],
            )
            ps.add_atom(atom, source="cauchy_schwarz_chain_v1",
                        note="5th cross-domain L6-PROOF chain; inner-product geometry <-> probability <-> analysis")
            print(f"  ATOM CREATED: {qid}")
            created += 1
        except Exception as e:
            print(f"  ATOM FAIL: {str(e)[:120]}")

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
                print(f"  SKIP_MISS_TGT: {src} -> {tgt}")
                miss += 1
                continue
            key = (src, "DEPENDS_ON", tgt)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                                source="cauchy_schwarz_chain_v1",
                                note="cauchy-schwarz derivation chain")
                print(f"  EDGE ADD: {src} -> {tgt}")
                added += 1
                existing_edges.add(key)
            except Exception as e:
                print(f"  EDGE FAIL: {str(e)[:80]}")

    print()
    for src, tgt in EXISTING_EDGES:
        if not ps.has_atom(src) or not ps.has_atom(tgt):
            miss += 1
            continue
        key = (src, "DEPENDS_ON", tgt)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                            source="cauchy_schwarz_chain_v1",
                            note="existing atom update; cauchy-schwarz derivable")
            print(f"  UPDATE EDGE: {src} -> {tgt}")
            added += 1
            existing_edges.add(key)
        except Exception as e:
            print(f"  UPDATE FAIL: {str(e)[:80]}")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== CAUCHY-SCHWARZ CHAIN SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  atoms created: {created}")
    print(f"  edges added: {added} miss: {miss}")
    print(f"\nCross-domain L6-PROOF chains cumulative (this session):")
    print(f"  #1 convolution: VSA <-> signal processing (968c8a38)")
    print(f"  #2 Bayes: probability <-> Bayesian inference (4f731dba)")
    print(f"  #3 CLT: probability <-> Fourier (13c608bb)")
    print(f"  #4 spectral: linear algebra <-> functional analysis (e02b5155)")
    print(f"  #5 Cauchy-Schwarz: inner-product <-> probability <-> geometry (this)")


if __name__ == "__main__":
    main()
