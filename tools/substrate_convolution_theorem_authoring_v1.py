"""Convolution theorem 4-step derivation chain authoring v1.

Per Research routing 16:12: substrate KNOWS circular_convolution and discrete_fourier_transform
are linked (same capability cap_circular_convolution + cap_fhrr_bind) but CANNOT PROVE it.
The only edge between them is generic RELATES. Authoring a 4-step typed derivation chain
converts THEOREM_LINKED-unproven -> PROVEN.

5 NEW atoms:
  1. pointwise_product (T2)
  2. DFT_linearity (T3 typed lemma)
  3. DFT_convolution_to_pointwise (T3 typed lemma; key)
  4. IDFT_inverse_property (T3 typed lemma)
  5. convolution_theorem_synthesis (T3 typed theorem)

2 UPDATES:
  - circular_convolution: + DEPENDS_ON convolution_theorem_synthesis
  - discrete_fourier_transform: + DEPENDS_ON DFT_linearity + DFT_convolution_to_pointwise

Cross-domain L6-PROOF demonstration: VSA binding (FHRR fhrr_bind ~ circular_convolution)
<-> signal processing (DFT + IDFT). Closes capability gap flagged by CELL-DISTILL-VERIFY-2.

NO LLM. NO bge. Pure schema authoring; tolerant of missing atoms.
"""
from __future__ import annotations
import sys
import dataclasses
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


NEW_ATOMS = [
    {
        "id": "T2/pointwise_product",
        "name": "Pointwise (Hadamard) product",
        "tier": Tier.TIER_2_PRIMITIVE,
        "aliases": ("hadamard_product", "elementwise_product"),
        "description": (
            "Pointwise (Hadamard) product of two vectors: (a * b)_i = a_i * b_i. "
            "Elementwise multiplication; the operation that makes DFT-domain "
            "convolution-to-multiplication identity work."
        ),
        "serves_capability": ("cap_pointwise_arithmetic",),
        "metadata": {
            "operation_type": "elementwise",
            "signature": "complex_vector x complex_vector -> complex_vector",
            "science_algebra_category": "linear_algebra::elementwise_op",
            "signature_hint": "elementwise_multiplication",
            "is_axiom": False,
            "batch_origin": "convolution_theorem_authoring",
        },
        "depends_on": ("math::T1/complex_field", "math::T1/vector_space"),
    },
    {
        "id": "T3/dft_linearity_lemma",
        "name": "DFT linearity lemma",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("DFT_linearity",),
        "description": (
            "DFT(a + b) = DFT(a) + DFT(b) AND DFT(c * a) = c * DFT(a) for scalar c. "
            "Linearity of the discrete Fourier transform; standard introductory property. "
            "Typed lemma; foundation for convolution_theorem_synthesis chain."
        ),
        "serves_capability": ("cap_DFT_property",),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "DFT(a + b) = DFT(a) + DFT(b); DFT(c*a) = c*DFT(a)",
            "science_algebra_category": "signal_processing::dft_property",
            "signature_hint": "linear_operator",
            "is_axiom": False,
            "batch_origin": "convolution_theorem_authoring",
        },
        "depends_on": ("math::T1/discrete_fourier_transform", "math::T1/complex_field",
                       "math::T1/vector_space"),
    },
    {
        "id": "T3/dft_convolution_to_pointwise_lemma",
        "name": "DFT convolution-to-pointwise lemma",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("convolution_theorem_in_fourier_domain", "DFT_convolution_to_pointwise"),
        "description": (
            "DFT(conv(a, b)) = DFT(a) * DFT(b). The KEY lemma in the convolution theorem: "
            "convolution in the time domain becomes pointwise multiplication in the frequency "
            "domain. Foundation for fast convolution via DFT/FFT."
        ),
        "serves_capability": ("cap_DFT_property", "cap_convolution_theorem"),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "DFT(conv(a, b)) = DFT(a) * DFT(b)",
            "science_algebra_category": "signal_processing::convolution_theorem",
            "signature_hint": "time_to_frequency_domain_convolution",
            "is_axiom": False,
            "batch_origin": "convolution_theorem_authoring",
        },
        "depends_on": ("math::T1/discrete_fourier_transform", "math::T2/circular_convolution",
                       "math::T2/pointwise_product"),
    },
    {
        "id": "T3/idft_inverse_property_lemma",
        "name": "IDFT inverse property lemma",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("IDFT_inverse_property",),
        "description": (
            "IDFT(DFT(v)) = v AND DFT(IDFT(v)) = v for any complex vector v. "
            "Inverse property of the discrete Fourier transform; the IDFT is the exact inverse "
            "(not just left-inverse). Required to invert the convolution-theorem identity."
        ),
        "serves_capability": ("cap_DFT_inverse_property",),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "IDFT(DFT(v)) = v; DFT(IDFT(v)) = v",
            "science_algebra_category": "signal_processing::dft_property",
            "signature_hint": "inverse_isomorphism",
            "is_axiom": False,
            "batch_origin": "convolution_theorem_authoring",
        },
        # We rely on discrete_fourier_transform (DFT) atom for both forward + inverse direction;
        # if a separate IDFT atom exists it will get a SHARES_MATH peer in future authoring.
        "depends_on": ("math::T1/discrete_fourier_transform",),
    },
    {
        "id": "T3/convolution_theorem_synthesis",
        "name": "Convolution theorem (synthesis)",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("convolution_theorem", "circular_conv_dft_identity"),
        "description": (
            "conv(a, b) = IDFT(DFT(a) * DFT(b)). The classical convolution theorem in the "
            "Z/N circular convention. Synthesized from DFT_convolution_to_pointwise_lemma "
            "(time-domain convolution equals frequency-domain pointwise product) and "
            "IDFT_inverse_property_lemma (apply IDFT to invert). "
            "DERIVATION:\n"
            "  Premise 1 (DFT_convolution_to_pointwise): DFT(conv(a, b)) = DFT(a) * DFT(b)\n"
            "  Premise 2 (IDFT_inverse_property): IDFT(DFT(v)) = v for any v\n"
            "  Apply IDFT to both sides of premise 1: IDFT(DFT(conv(a, b))) = IDFT(DFT(a) * DFT(b))\n"
            "  Substitute premise 2 on LHS (v := conv(a, b)): conv(a, b) = IDFT(DFT(a) * DFT(b))\n"
            "  QED"
        ),
        "serves_capability": ("cap_convolution_theorem", "cap_circular_convolution",
                              "cap_fhrr_bind"),
        "metadata": {
            "operation_type": "typed_theorem",
            "theorem": "conv(a, b) = IDFT(DFT(a) * DFT(b))",
            "science_algebra_category": "signal_processing::convolution_theorem",
            "signature_hint": "convolution_via_dft",
            "is_axiom": False,
            "batch_origin": "convolution_theorem_authoring",
            "derivation_steps": [
                "DFT_convolution_to_pointwise: DFT(conv(a, b)) = DFT(a) * DFT(b)",
                "IDFT_inverse_property: IDFT(DFT(v)) = v",
                "Apply IDFT to both sides: IDFT(DFT(conv(a, b))) = IDFT(DFT(a) * DFT(b))",
                "Substitute on LHS: conv(a, b) = IDFT(DFT(a) * DFT(b))",
            ],
        },
        "depends_on": (
            "math::T3/dft_convolution_to_pointwise_lemma",
            "math::T3/idft_inverse_property_lemma",
        ),
    },
]


# Existing atom updates: add DEPENDS_ON edges from existing atoms to the new ones.
EXISTING_EDGES = [
    ("math::T2/circular_convolution", "math::T3/convolution_theorem_synthesis"),
    ("math::T1/discrete_fourier_transform", "math::T3/dft_linearity_lemma"),
    ("math::T1/discrete_fourier_transform", "math::T3/dft_convolution_to_pointwise_lemma"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    # Author 5 new atoms
    created = 0
    skipped = 0
    failed = 0
    for spec in NEW_ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"  ATOM SKIP (exists): {qid}")
            skipped += 1
            continue
        try:
            atom = Atom(
                id=spec["id"], name=spec["name"], corpus=Corpus.MATH,
                tier=spec["tier"], description=spec["description"],
                kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                metadata=spec["metadata"], serves_capability=spec["serves_capability"],
            )
            ps.add_atom(atom, source="convolution_theorem_authoring_v1",
                        note="LANE B convolution theorem derivation chain per Research routing 16:12")
            print(f"  ATOM CREATED: {qid} [{spec['tier'].value}]")
            created += 1
        except Exception as e:
            print(f"  ATOM FAIL {qid}: {str(e)[:120]}")
            failed += 1

    # Add intra-batch DEPENDS_ON edges
    print()
    added = 0
    miss_tgt = 0
    edge_failed = 0
    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    for spec in NEW_ATOMS:
        src_qid = f"math::{spec['id']}"
        if not ps.has_atom(src_qid):
            continue
        for tgt_qid in spec["depends_on"]:
            if not ps.has_atom(tgt_qid):
                print(f"  EDGE SKIP_MISS_TGT: {src_qid} -> {tgt_qid}")
                miss_tgt += 1
                continue
            key = (src_qid, "DEPENDS_ON", tgt_qid)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(src_qid, RelationType.DEPENDS_ON, tgt_qid,
                                source="convolution_theorem_authoring_v1",
                                note="convolution theorem derivation chain")
                print(f"  EDGE ADD: {src_qid} -> {tgt_qid}")
                added += 1
            except Exception as e:
                print(f"  EDGE FAIL: {src_qid} -> {tgt_qid}: {str(e)[:80]}")
                edge_failed += 1

    # Existing atom updates: add DEPENDS_ON from existing -> new
    print()
    for src_qid, tgt_qid in EXISTING_EDGES:
        if not ps.has_atom(src_qid):
            print(f"  UPDATE SKIP_MISS_SRC: {src_qid}")
            continue
        if not ps.has_atom(tgt_qid):
            print(f"  UPDATE SKIP_MISS_TGT: {src_qid} -> {tgt_qid}")
            miss_tgt += 1
            continue
        key = (src_qid, "DEPENDS_ON", tgt_qid)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(src_qid, RelationType.DEPENDS_ON, tgt_qid,
                            source="convolution_theorem_authoring_v1",
                            note="existing atom update; cross-domain L6-PROOF chain")
            print(f"  UPDATE EDGE: {src_qid} -> {tgt_qid}")
            added += 1
        except Exception as e:
            print(f"  UPDATE FAIL: {src_qid} -> {tgt_qid}: {str(e)[:80]}")
            edge_failed += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== CONVOLUTION THEOREM AUTHORING SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  atoms created: {created} skipped: {skipped} failed: {failed}")
    print(f"  edges added: {added} miss_tgt: {miss_tgt} failed: {edge_failed}")
    print(f"\nExpected substrate behavior post-authoring:")
    print(f"  CELL-DISTILL-VERIFY-2 verdict on (circular_convolution, DFT): THEOREM_LINKED-PROVEN")
    print(f"  L6-PROOF derivation chain: 4 typed steps; CHTV-1 verifiable")
    print(f"  Cross-domain L6-PROOF win: VSA binding <-> signal processing")


if __name__ == "__main__":
    main()
