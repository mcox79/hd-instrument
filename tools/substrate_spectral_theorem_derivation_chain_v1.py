"""Spectral theorem cross-domain L6-PROOF derivation chain v1.

4th cross-domain L6-PROOF chain this session. Replicates convolution-theorem
(968c8a38) + Bayes (4f731dba) + CLT (13c608bb) pattern for the SPECTRAL THEOREM.

Cross-domain bridge: FINITE-DIM LINEAR ALGEBRA (eigenvalues, matrices) ↔
FUNCTIONAL ANALYSIS (Hilbert space operators, self-adjoint operators).

Bonus cross-domain SHARES_MATH bridge: spectral_theorem_synthesis ↔ SVD.
SVD generalizes spectral theorem to non-square matrices; both rely on the same
orthonormal-eigenbasis structure.

Spectral theorem statement (finite-dim self-adjoint version):
  For a self-adjoint operator T on a finite-dim inner-product space H, there
  exists an orthonormal basis of H consisting of eigenvectors of T, and all
  eigenvalues of T are real.

Derivation:
  Premise 1 (self-adjoint property):
    <Tx, y> = <x, Ty> for all x, y in H

  Premise 2 (eigenvalues of self-adjoint are real):
    If Tv = λv with v ≠ 0, then λ = λ̄ (so λ is real).
    Proof: λ<v,v> = <Tv, v> = <v, Tv> = <v, λv> = λ̄<v,v>, so λ = λ̄.

  Premise 3 (eigenvectors with distinct eigenvalues are orthogonal):
    If Tv_1 = λ_1 v_1 and Tv_2 = λ_2 v_2 with λ_1 ≠ λ_2, then <v_1, v_2> = 0.

  Synthesis: induction on dimension yields an orthonormal eigenbasis. QED.

3 NEW T3 atoms + cross-domain SHARES_MATH bridge to SVD.

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
        "id": "T3/self_adjoint_operator_lemma",
        "name": "Self-adjoint operator property",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("hermitian_operator_property", "T_adjoint_T_equals_T"),
        "description": (
            "Operator T on inner-product space H is self-adjoint iff <Tx, y> = <x, Ty> "
            "for all x, y in H. Equivalent to T* = T where T* is the adjoint. "
            "Self-adjoint operators are the bridge object between finite-dim linear "
            "algebra (symmetric matrices) and functional analysis (Hermitian operators "
            "on Hilbert space). Foundation for spectral theorem."
        ),
        "serves_capability": ("cap_spectral_theory", "cap_self_adjoint_property"),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "T self-adjoint iff <Tx, y> = <x, Ty> for all x, y in H",
            "science_algebra_category": "linear_algebra::operator_property",
            "signature_hint": "self_adjoint_inner_product_invariance",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "spectral_theorem_chain",
        },
        "depends_on": (
            "math::T1/inner_product",
            "math::T1/hilbert_space",
            "math::T1/complex_field",
        ),
    },
    {
        "id": "T3/self_adjoint_real_eigenvalues_lemma",
        "name": "Self-adjoint operator has real eigenvalues",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("hermitian_real_spectrum", "self_adjoint_real_lambda"),
        "description": (
            "If T is self-adjoint and Tv = λv with v ≠ 0, then λ ∈ ℝ (i.e., λ = λ̄). "
            "Proof: λ<v,v> = <Tv, v> = <v, Tv> = <v, λv> = λ̄<v,v>. "
            "Since <v,v> > 0, divide to get λ = λ̄, so λ is real. "
            "This lemma is the FIRST PIECE of the spectral theorem proof."
        ),
        "serves_capability": ("cap_spectral_theory", "cap_self_adjoint_property"),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "T self-adjoint, Tv = λv, v ≠ 0 ⟹ λ ∈ ℝ",
            "science_algebra_category": "linear_algebra::eigenvalue_property",
            "signature_hint": "real_spectrum_of_self_adjoint",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "spectral_theorem_chain",
        },
        "depends_on": (
            "math::T3/self_adjoint_operator_lemma",
            "math::T1/eigenvalue_eigenvector",
            "math::T1/inner_product",
        ),
    },
    {
        "id": "T3/spectral_theorem_synthesis",
        "name": "Spectral theorem (typed synthesis for self-adjoint operators)",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": (
            "spectral_decomposition_self_adjoint",
            "orthonormal_eigenbasis_theorem",
        ),
        "description": (
            "For a self-adjoint operator T on a finite-dim inner-product space H, "
            "there exists an orthonormal basis of H consisting of eigenvectors of T, "
            "and all eigenvalues of T are real. "
            "DERIVATION:\n"
            "  Premise 1 (self_adjoint_operator): <Tx, y> = <x, Ty> for all x, y\n"
            "  Premise 2 (real eigenvalues): λ ∈ ℝ for any eigenvalue (via P1)\n"
            "  Premise 3 (eigenvectors with distinct λ orthogonal):\n"
            "    If Tv_1 = λ_1 v_1, Tv_2 = λ_2 v_2, λ_1 ≠ λ_2:\n"
            "    λ_1 <v_1, v_2> = <Tv_1, v_2> = <v_1, Tv_2> = λ_2 <v_1, v_2>\n"
            "    So (λ_1 - λ_2)<v_1, v_2> = 0, and since λ_1 ≠ λ_2, <v_1, v_2> = 0.\n"
            "  Synthesis: induct on dim(H). Take any eigenvector v_1 (exists in ℂ); "
            "consider H' = v_1^⊥; T restricts to a self-adjoint operator on H'; "
            "apply induction.\n"
            "  Output: orthonormal eigenbasis {v_1, ..., v_n} with real eigenvalues {λ_1, ..., λ_n}\n"
            "  QED\n"
            "Cross-domain bridge: finite-dim linear algebra (symmetric matrices) ↔ "
            "functional analysis (self-adjoint operators on Hilbert space)."
        ),
        "serves_capability": (
            "cap_spectral_theory",
            "cap_diagonalization_self_adjoint",
            "cap_eigenvalue_decomposition",
        ),
        "metadata": {
            "operation_type": "typed_theorem",
            "theorem": (
                "Self-adjoint T on finite-dim H admits orthonormal eigenbasis with real eigenvalues"
            ),
            "science_algebra_category": "linear_algebra::spectral_theorem",
            "signature_hint": "self_adjoint_diagonalizes_in_orthonormal_basis",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "spectral_theorem_chain",
            "derivation_steps": [
                "self_adjoint_operator_lemma: <Tx,y> = <x,Ty>",
                "self_adjoint_real_eigenvalues: λ ∈ ℝ",
                "distinct-eigenvalue eigenvectors orthogonal (via P1)",
                "Induction on dim: orthonormal eigenbasis exists",
            ],
        },
        "depends_on": (
            "math::T3/self_adjoint_operator_lemma",
            "math::T3/self_adjoint_real_eigenvalues_lemma",
            "math::T1/eigenvalue_eigenvector",
            "math::T1/vector_space",
        ),
    },
]


EXISTING_EDGES = [
    ("math::T1/spectral_theorem", "math::T3/spectral_theorem_synthesis"),
]

# Cross-domain SHARES_MATH bridge: spectral_theorem ↔ SVD (SVD generalizes spectral)
CROSS_DOMAIN_BRIDGES = [
    (
        "math::T3/spectral_theorem_synthesis",
        "math::T1/singular_value_decomposition",
        RelationType.SHARES_MATH,
        (
            "spectral theorem (orthonormal eigenbasis of self-adjoint operator) and "
            "SVD (orthonormal singular vector bases) share the orthonormal-bases-from-"
            "operators structure; SVD generalizes spectral theorem to non-square"
        ),
    ),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    created = 0
    failed = 0
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
            ps.add_atom(atom, source="spectral_theorem_chain_v1",
                        note="4th cross-domain L6-PROOF chain; linear algebra <-> functional analysis")
            print(f"  ATOM CREATED: {qid}")
            created += 1
        except Exception as e:
            print(f"  ATOM FAIL: {str(e)[:120]}")
            failed += 1

    print()
    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    added = 0
    miss = 0
    edge_failed = 0
    for spec in NEW_ATOMS:
        src = f"math::{spec['id']}"
        if not ps.has_atom(src):
            continue
        for tgt in spec["depends_on"]:
            if not ps.has_atom(tgt):
                print(f"  EDGE SKIP_MISS_TGT: {src} -> {tgt}")
                miss += 1
                continue
            key = (src, "DEPENDS_ON", tgt)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                                source="spectral_theorem_chain_v1",
                                note="spectral theorem derivation chain")
                print(f"  EDGE ADD: {src} -> {tgt}")
                added += 1
                existing_edges.add(key)
            except Exception as e:
                print(f"  EDGE FAIL: {str(e)[:80]}")
                edge_failed += 1

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
                            source="spectral_theorem_chain_v1",
                            note="existing atom update; spectral_theorem derivable")
            print(f"  UPDATE EDGE: {src} -> {tgt}")
            added += 1
            existing_edges.add(key)
        except Exception as e:
            print(f"  UPDATE FAIL: {str(e)[:80]}")

    print()
    bridges_added = 0
    for src, tgt, rel_type, note in CROSS_DOMAIN_BRIDGES:
        if not ps.has_atom(src) or not ps.has_atom(tgt):
            print(f"  BRIDGE SKIP_MISS: {src} OR {tgt}")
            continue
        for s, t in ((src, tgt), (tgt, src)):
            key = (s, rel_type.name, t)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(s, rel_type, t,
                                source="spectral_theorem_chain_v1_cross_domain_bridge",
                                note=note)
                print(f"  CROSS-DOMAIN BRIDGE: {s} {rel_type.name} {t}")
                bridges_added += 1
                existing_edges.add(key)
            except Exception as e:
                print(f"  BRIDGE FAIL: {str(e)[:120]}")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SPECTRAL THEOREM CHAIN SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  atoms created: {created} failed: {failed}")
    print(f"  edges added: {added} miss: {miss} failed: {edge_failed}")
    print(f"  cross-domain bridges: {bridges_added}")
    print(f"\nCross-domain L6-PROOF chains cumulative (this session):")
    print(f"  #1 convolution theorem: VSA binding <-> signal processing (968c8a38)")
    print(f"  #2 Bayes rule: measure-theoretic probability <-> Bayesian inference (4f731dba)")
    print(f"  #3 CLT: probability theory <-> Fourier analysis (13c608bb)")
    print(f"  #4 Spectral theorem: linear algebra <-> functional analysis (this commit)")
    print(f"  3 cross-domain SHARES_MATH bridges total: char_function<->DFT (#1<->#3) + spectral<->SVD (this)")


if __name__ == "__main__":
    main()
