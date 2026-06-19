"""Optimizer family SHARED_ABSTRACTION authoring v1.

Per CELL-DISTILL-VERIFY-2 anchor: optimizer_family verdict SHARED_ABSTRACTION
across 3 atoms (T1/gradient_descent + T3/adam_optimizer + T3/stochastic_gradient_descent).
These share the gradient-based-iterative-optimization abstraction but currently have
no explicit shared parent.

Closes the SECOND DISTILL_VERIFY_2 verdict (first was convolution_theorem; addressed
in commit 968c8a38 with derivation chain).

Approach: author a new T2 atom `gradient_based_optimizer` as the shared abstraction;
add SPECIALIZES edges from each of the 3 specific optimizers to it. This makes the
abstraction EXPLICIT and substrate-internally recognizable.

NO LLM. NO bge. Pure schema authoring.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


# Specific optimizers found in CELL-DISTILL-VERIFY-2; each will SPECIALIZE the abstraction
SPECIFIC_OPTIMIZERS = [
    "math::T1/gradient_descent",
    "math::T3/adam_optimizer",
    "math::T3/stochastic_gradient_descent",
]


SHARED_ABSTRACTION = {
    "id": "T2/gradient_based_optimizer",
    "name": "Gradient-based optimizer (shared abstraction)",
    "tier": Tier.TIER_2_PRIMITIVE,
    "aliases": ("gradient_optimizer", "first_order_optimizer"),
    "description": (
        "Shared abstraction over iterative optimizers that use the gradient of an "
        "objective function to update parameters. Iteration scheme: theta_{t+1} = "
        "theta_t - eta * F(g_t, ...) where g_t = nabla L(theta_t) and F is a "
        "method-specific update rule (identity for SGD; first/second moment estimates "
        "for Adam; etc.). Captures the common structure across gradient_descent + "
        "stochastic_gradient_descent + adam_optimizer (and other first-order methods). "
        "Per CELL-DISTILL-VERIFY-2 SHARED_ABSTRACTION verdict."
    ),
    "serves_capability": (
        "cap_gradient_based_optimization",
        "cap_optimization_substrate",
        "cap_neural_network_training_default_optimizer",
    ),
    "metadata": {
        "operation_type": "abstract_iteration_scheme",
        "abstraction_form": "theta_{t+1} = theta_t - eta * F(grad_t)",
        "specializations": [s.split("::")[-1] for s in SPECIFIC_OPTIMIZERS],
        "science_algebra_category": "optimization::gradient_based",
        "signature_hint": "iterative_gradient_descent_template",
        "is_axiom": False,
        "content_type": "FORMAL_SYSTEMS",
        "substrate_load_bearing": False,  # abstraction; substrate KNOWS but doesn't USE directly
        "batch_origin": "optimizer_family_abstraction",
    },
    "depends_on": ("math::T1/gradient", "math::T1/derivative", "math::T1/vector_space"),
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    # Author the shared abstraction atom
    spec = SHARED_ABSTRACTION
    qid = f"math::{spec['id']}"
    if ps.has_atom(qid):
        print(f"  ATOM SKIP (exists): {qid}")
        created = 0
    else:
        try:
            atom = Atom(
                id=spec["id"], name=spec["name"], corpus=Corpus.MATH,
                tier=spec["tier"], description=spec["description"],
                kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                metadata=spec["metadata"], serves_capability=spec["serves_capability"],
            )
            ps.add_atom(atom, source="optimizer_family_abstraction_v1",
                        note="DISTILL_VERIFY_2 SHARED_ABSTRACTION verdict; gradient-based optimizer family")
            print(f"  ATOM CREATED: {qid}")
            created = 1
        except Exception as e:
            print(f"  ATOM FAIL: {str(e)[:120]}")
            return

    print()
    # DEPENDS_ON edges from abstraction
    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    added = 0
    miss = 0
    for dep in spec["depends_on"]:
        if not ps.has_atom(dep):
            print(f"  DEP SKIP_MISS: {qid} -> {dep}")
            miss += 1
            continue
        key = (qid, "DEPENDS_ON", dep)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(qid, RelationType.DEPENDS_ON, dep,
                            source="optimizer_family_abstraction_v1",
                            note="abstraction inherits gradient + derivative + vector_space premises")
            print(f"  DEP ADD: {qid} -> {dep}")
            added += 1
        except Exception as e:
            print(f"  DEP FAIL: {str(e)[:80]}")

    print()
    # SPECIALIZES edges: each specific optimizer -> abstraction
    specialized = 0
    for spec_qid in SPECIFIC_OPTIMIZERS:
        if not ps.has_atom(spec_qid):
            print(f"  SPEC SKIP_MISS_SRC: {spec_qid}")
            miss += 1
            continue
        key = (spec_qid, "SPECIALIZES", qid)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(spec_qid, RelationType.SPECIALIZES, qid,
                            source="optimizer_family_abstraction_v1",
                            note=f"{spec_qid.split('/')[-1]} is a specialization of gradient_based_optimizer abstraction")
            print(f"  SPECIALIZES: {spec_qid} -> {qid}")
            specialized += 1
        except Exception as e:
            print(f"  SPEC FAIL: {str(e)[:80]}")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== OPTIMIZER FAMILY ABSTRACTION SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  abstraction atom created: {created}")
    print(f"  DEPENDS_ON edges added: {added}")
    print(f"  SPECIALIZES edges added: {specialized}")
    print(f"  misses: {miss}")
    print(f"\nExpected DISTILL_VERIFY_2 verdict post-authoring:")
    print(f"  optimizer_family: still SHARED_ABSTRACTION but now EXPLICITLY represented")
    print(f"  substrate can answer 'what abstraction do these 3 optimizers share?' -> gradient_based_optimizer")
    print(f"  Closes 2nd DISTILL_VERIFY_2 verdict (1st was convolution_theorem)")


if __name__ == "__main__":
    main()
