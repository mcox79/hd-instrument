"""Bayes' rule derivation chain authoring v1.

Per Research convolution-theorem pattern (commit 968c8a38) and Cycle 51 substrate-
on-its-own positioning: replicate the cross-domain L6-PROOF derivation chain for
Bayes' rule.

Bayes' rule (T1/bayes_rule already exists in substrate, but only via generic edges
without a typed derivation). Authoring the 2-step derivation makes it PROVEN.

CROSS-DOMAIN bridge: measure theory (probability_space + sigma-algebra) <->
Bayesian inference (posterior + prior + likelihood). Foundational cross-discipline
demonstration.

Derivation chain:
  Premise 1 (product rule of probability):
    P(A ∩ B) = P(A|B) * P(B) = P(B|A) * P(A)
    -- Joint probability factors via either conditioning direction.

  Premise 2 (definition of conditional probability):
    P(A|B) = P(A ∩ B) / P(B)  for P(B) > 0
    -- Established by T1/conditional_probability

  Synthesis: P(A|B) = P(B|A) * P(A) / P(B)
    From P1: P(A ∩ B) = P(B|A) * P(A)
    Substitute into P2: P(A|B) = (P(B|A) * P(A)) / P(B)
    QED

2 NEW T3 typed atoms:
  - product_rule_probability_lemma (Premise 1; joint via conditional)
  - bayes_rule_synthesis (the typed theorem derivation)

Then update T1/bayes_rule to DEPENDS_ON bayes_rule_synthesis (substrate knows
bayes_rule is derivable, not axiomatic).

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
        "id": "T3/product_rule_probability_lemma",
        "name": "Product rule of probability (joint via conditional)",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("product_rule_probability", "joint_via_conditional", "chain_rule_two_event"),
        "description": (
            "P(A ∩ B) = P(A|B) * P(B) = P(B|A) * P(A). "
            "Joint probability of two events factors via either conditioning direction. "
            "Foundational lemma; substrate-internal Bayes' rule derivation depends on this. "
            "Specialization of chain_rule_probability to two events."
        ),
        "serves_capability": ("cap_probability_property", "cap_bayesian_inference"),
        "metadata": {
            "operation_type": "typed_lemma",
            "lemma": "P(A and B) = P(A|B) * P(B) = P(B|A) * P(A)",
            "science_algebra_category": "probability_theory::joint_decomposition",
            "signature_hint": "joint_factors_via_either_conditional",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "bayes_rule_derivation_chain",
        },
        "depends_on": (
            "math::T1/conditional_probability",
            "math::T1/joint_distribution",
            "math::T1/probability_space",
            "math::T1/chain_rule_probability",
        ),
    },
    {
        "id": "T3/bayes_rule_synthesis",
        "name": "Bayes' rule (typed synthesis)",
        "tier": Tier.TIER_3_ALGORITHM,
        "aliases": ("bayes_rule_derivation", "posterior_via_likelihood_prior_evidence"),
        "description": (
            "P(A|B) = P(B|A) * P(A) / P(B) for P(B) > 0. Bayes' rule derived from "
            "product rule + conditional probability definition. "
            "DERIVATION:\n"
            "  Premise 1 (product rule of probability): P(A ∩ B) = P(B|A) * P(A)\n"
            "  Premise 2 (conditional probability definition): P(A|B) = P(A ∩ B) / P(B)\n"
            "  Substitute P1 into P2: P(A|B) = (P(B|A) * P(A)) / P(B)\n"
            "  QED\n"
            "Cross-domain bridge: measure-theoretic probability_space ↔ Bayesian inference "
            "(posterior = likelihood × prior / evidence)."
        ),
        "serves_capability": (
            "cap_bayesian_inference",
            "cap_posterior_computation",
            "cap_probability_property",
        ),
        "metadata": {
            "operation_type": "typed_theorem",
            "theorem": "P(A|B) = P(B|A) * P(A) / P(B)",
            "science_algebra_category": "probability_theory::bayes_rule_derivation",
            "signature_hint": "bayes_rule_typed_synthesis",
            "is_axiom": False,
            "content_type": "FORMAL_SYSTEMS",
            "substrate_load_bearing": False,
            "batch_origin": "bayes_rule_derivation_chain",
            "derivation_steps": [
                "product_rule_probability: P(A and B) = P(B|A) * P(A)",
                "conditional_probability_definition: P(A|B) = P(A and B) / P(B)",
                "Substitute: P(A|B) = (P(B|A) * P(A)) / P(B)",
            ],
        },
        "depends_on": (
            "math::T3/product_rule_probability_lemma",
            "math::T1/conditional_probability",
        ),
    },
]


# Existing atom updates: T1/bayes_rule now DEPENDS_ON the synthesis (it's derivable)
EXISTING_EDGES = [
    ("math::T1/bayes_rule", "math::T3/bayes_rule_synthesis"),
    ("math::T1/total_probability", "math::T3/product_rule_probability_lemma"),
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
            ps.add_atom(atom, source="bayes_rule_derivation_chain_v1",
                        note="cross-domain L6-PROOF chain; measure theory <-> Bayesian inference")
            print(f"  ATOM CREATED: {qid} [{spec['tier'].value}]")
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
                                source="bayes_rule_derivation_chain_v1",
                                note="bayes-rule derivation chain")
                print(f"  EDGE ADD: {src} -> {tgt}")
                added += 1
            except Exception as e:
                print(f"  EDGE FAIL: {str(e)[:80]}")
                edge_failed += 1

    print()
    for src, tgt in EXISTING_EDGES:
        if not ps.has_atom(src):
            print(f"  UPDATE SKIP_MISS_SRC: {src}")
            continue
        if not ps.has_atom(tgt):
            print(f"  UPDATE SKIP_MISS_TGT: {src} -> {tgt}")
            miss += 1
            continue
        key = (src, "DEPENDS_ON", tgt)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                            source="bayes_rule_derivation_chain_v1",
                            note="existing atom update; bayes_rule is derivable from synthesis")
            print(f"  UPDATE EDGE: {src} -> {tgt}")
            added += 1
        except Exception as e:
            print(f"  UPDATE FAIL: {str(e)[:80]}")
            edge_failed += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== BAYES RULE DERIVATION CHAIN SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  atoms created: {created} failed: {failed}")
    print(f"  edges added: {added} miss: {miss} failed: {edge_failed}")
    print(f"\nCross-domain L6-PROOF chain #2 (this session):")
    print(f"  #1 convolution theorem: VSA binding <-> signal processing (968c8a38)")
    print(f"  #2 Bayes rule: measure-theoretic probability <-> Bayesian inference")


if __name__ == "__main__":
    main()
