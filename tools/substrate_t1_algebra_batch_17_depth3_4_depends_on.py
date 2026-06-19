"""T1 algebra BATCH 17: 4 new T1 atoms + 30 DEPENDS_ON edges targeting 62pct authoring-gap leaves.

Per research_to_testbed_T1_ALGEBRA_BATCH_17_DEEPER_DEPENDS_ON_targeted_62pct_*.md
(Phase 1 R1.1 of MASTER PLAN). Closes L6-PROOF FINDER depth caveat: 38pct genuine-T1 /
62pct authoring-gap leaf -> projected 65pct+ / depth 1.30 -> 2.5+.

This script is tolerant of missing source atoms: if a flagged T2/T3 atom is absent on
the runner's substrate (local laptop vs remote canonical), it warns + skips the edges
for that atom rather than failing. Run against canonical remote substrate for full effect.

Mechanism:
  1. Author 4 new T1 atoms: recursion + optimal_substructure + discrete_fourier_transform + complex_field
  2. Add 30 DEPENDS_ON edges across 10 flagged atoms

NO LLM. NO bge. Pure schema work; no heat.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


# -- 4 NEW T1 atoms (terminal bridges per BATCH 17 spec) --
NEW_T1_ATOMS = [
    {
        "id": "T1/recursion",
        "name": "Recursion",
        "aliases": ("recursive_definition", "self_referential_computation"),
        "description": (
            "Self-referential computation: f(n) defined in terms of f(n-1) or smaller subproblems. "
            "Requires a base case for termination. Foundation for induction, fixed-point iteration, "
            "and dynamic programming. Examples: factorial, fibonacci, recursive tree traversal, "
            "recursive proof unfolding."
        ),
        "serves_capability": (
            "algorithmic_substrate_foundation",
            "recursive_definition_substrate",
            "substrate_self_knowledge",
        ),
        "metadata": {
            "science_algebra_category": "algorithms::recursion",
            "signature_hint": "self_referential_computation_with_base_case",
            "batch_origin": "batch_17",
            "is_axiom": False,
            "base_case_required": True,
        },
    },
    {
        "id": "T1/optimal_substructure",
        "name": "Optimal substructure (Bellman principle of optimality)",
        "aliases": ("bellman_principle_of_optimality",),
        "description": (
            "Optimal solution decomposes into optimal solutions of subproblems (Bellman 1957). "
            "Foundational property required for dynamic programming correctness. Examples: "
            "Dijkstra shortest path, knapsack DP, Viterbi decoding, RL value iteration."
        ),
        "serves_capability": (
            "DP_correctness_substrate",
            "RL_substrate_foundation",
            "optimization_substructure",
            "substrate_self_knowledge",
        ),
        "metadata": {
            "science_algebra_category": "optimization::dynamic_programming",
            "signature_hint": "optimal_decomposes_into_optimal_subproblems",
            "batch_origin": "batch_17",
            "is_axiom": False,
        },
    },
    {
        "id": "T1/discrete_fourier_transform",
        "name": "Discrete Fourier Transform (DFT)",
        "aliases": ("DFT", "FFT_basis"),
        "description": (
            "X_k = sum_{n=0}^{N-1} x_n exp(-2*pi*i*k*n/N); inverse x_n = (1/N) sum X_k exp(+2*pi*i*k*n/N). "
            "Linear, Parseval norm-preserving; convolution in time domain becomes pointwise multiplication "
            "in frequency domain. Foundation for FHRR substrate, signal processing, and "
            "frequency-domain analysis."
        ),
        "serves_capability": (
            "signal_processing_foundation",
            "fhrr_substrate",
            "frequency_domain_analysis",
            "substrate_self_knowledge",
        ),
        "metadata": {
            "science_algebra_category": "signal_processing::frequency_domain",
            "signature_hint": "frequency_domain_decomposition_via_basis_exponentials",
            "batch_origin": "batch_17",
            "is_axiom": False,
        },
    },
    {
        "id": "T1/complex_field",
        "name": "Complex field (C)",
        "aliases": ("field_of_complex_numbers", "C_field"),
        "description": (
            "C = {a + b*i : a, b in R, i^2 = -1}; complex numbers form a field. Algebraically closed "
            "(fundamental theorem of algebra), characteristic 0, contains R as subfield. Foundation "
            "for complex analysis, Fourier transform, and FHRR substrate."
        ),
        "serves_capability": (
            "complex_analysis_foundation",
            "fourier_transform_foundation",
            "fhrr_substrate",
            "substrate_self_knowledge",
        ),
        "metadata": {
            "science_algebra_category": "abstract_algebra::field_theory",
            "signature_hint": "real_pair_with_i_squared_eq_minus_one",
            "batch_origin": "batch_17",
            "is_axiom": False,
        },
    },
]


# DEPENDS_ON edges. Source qid -> list of target qids.
# Tolerant: missing src or tgt logs SKIP_MISS, no fail.
DEPENDS_ON_EDGES = [
    # 1. cosine_cleanup
    ("math::T2/cosine_cleanup", "math::T1/inner_product"),
    ("math::T2/cosine_cleanup", "math::T1/cosine_similarity"),
    ("math::T2/cosine_cleanup", "math::T1/matrix_norm"),
    ("math::T2/cosine_cleanup", "math::T1/axioms"),
    # 2. tier2_schema
    ("math::T2/tier2_schema", "math::T1/axioms"),
    ("math::T2/tier2_schema", "math::T1/equivalence_relation"),
    ("math::T2/tier2_schema", "math::T1/category"),
    # 3. dynamic_programming (T3 leaf -> deeper T1 deps)
    ("math::T3/dynamic_programming", "math::T1/recursion"),
    ("math::T3/dynamic_programming", "math::T1/optimal_substructure"),
    ("math::T3/dynamic_programming", "math::T1/bayes_rule"),
    ("math::T3/dynamic_programming", "math::T1/fixed_point_iteration"),
    # 4. superposition
    ("math::T2/superposition", "math::T1/vector_space"),
    ("math::T2/superposition", "math::T1/axioms"),
    ("math::T2/superposition", "math::T1/linear_independence"),
    # 5. fhrr_unbind
    ("math::T2/fhrr_unbind", "math::T2/circular_convolution"),
    ("math::T2/fhrr_unbind", "math::T1/inner_product"),
    ("math::T2/fhrr_unbind", "math::T1/vector_space"),
    # 6. circular_convolution
    ("math::T2/circular_convolution", "math::T1/discrete_fourier_transform"),
    ("math::T2/circular_convolution", "math::T1/complex_field"),
    ("math::T2/circular_convolution", "math::T1/vector_space"),
    ("math::T2/circular_convolution", "math::T1/axioms"),
    # 7. structured_prediction_family (SCHOOL); may live as math::SCHOOL/... or math::T2/...
    ("math::SCHOOL/structured_prediction_family", "math::T1/category"),
    ("math::SCHOOL/structured_prediction_family", "math::T1/equivalence_relation"),
    ("math::SCHOOL/structured_prediction_family", "math::T1/axioms"),
    # 8. forward_algorithm_atom
    ("math::T3/forward_algorithm_atom", "math::T3/dynamic_programming"),
    ("math::T3/forward_algorithm_atom", "math::T1/markov_chain"),
    ("math::T3/forward_algorithm_atom", "math::T1/probability_space"),
    ("math::T3/forward_algorithm_atom", "math::T1/chain_rule_probability"),
    # 9. hmm_transition
    ("math::T3/hmm_transition", "math::T1/markov_chain"),
    ("math::T3/hmm_transition", "math::T1/conditional_probability"),
    ("math::T3/hmm_transition", "math::T1/random_variable"),
    # 10. answer_consistency_weak_labels
    ("math::T3/answer_consistency_weak_labels", "math::T1/bayes_rule"),
    ("math::T3/answer_consistency_weak_labels", "math::T1/conditional_probability"),
    ("math::T3/answer_consistency_weak_labels", "math::T1/expectation"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    # --- Step 1: author 4 new T1 atoms ---
    created_atoms = 0
    skipped_atoms = 0
    for spec in NEW_T1_ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"  ATOM SKIP (exists): {qid}")
            skipped_atoms += 1
            continue
        atom = Atom(
            id=spec["id"],
            name=spec["name"],
            corpus=Corpus.MATH,
            tier=Tier.TIER_1_FOUNDATIONAL,
            description=spec["description"],
            kind=AtomKind.PRIMITIVE,
            aliases=spec["aliases"],
            metadata=spec["metadata"],
            serves_capability=spec["serves_capability"],
        )
        ps.add_atom(
            atom,
            source="t1_algebra_batch_17_depth3_4_depends_on",
            note="BATCH 17 new T1 terminal bridge per Research Phase 1 R1.1",
        )
        print(f"  ATOM CREATED: {qid}")
        created_atoms += 1

    print(f"\n  atoms: created={created_atoms} skipped_exists={skipped_atoms}")

    # --- Step 2: add 30 DEPENDS_ON edges ---
    added_edges = 0
    skipped_miss_src = 0
    skipped_miss_tgt = 0
    skipped_dup = 0
    failed = 0

    # Build existing edge set to avoid duplicates (tuple(src, rel, tgt))
    existing = set()
    for r in ps.iter_all_relations():
        try:
            key = (r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id)
            existing.add(key)
        except AttributeError:
            pass

    for src_qid, tgt_qid in DEPENDS_ON_EDGES:
        if not ps.has_atom(src_qid):
            print(f"  EDGE SKIP_MISS_SRC: {src_qid} -> {tgt_qid}")
            skipped_miss_src += 1
            continue
        if not ps.has_atom(tgt_qid):
            print(f"  EDGE SKIP_MISS_TGT: {src_qid} -> {tgt_qid}")
            skipped_miss_tgt += 1
            continue
        key = (src_qid, "DEPENDS_ON", tgt_qid)
        if key in existing:
            print(f"  EDGE SKIP_DUP: {src_qid} -> {tgt_qid}")
            skipped_dup += 1
            continue
        try:
            ps.add_relation(
                src_qid,
                RelationType.DEPENDS_ON,
                tgt_qid,
                source="t1_algebra_batch_17_depth3_4_depends_on",
                note="BATCH 17 depth-3+4 edge per Research Phase 1 R1.1",
            )
            print(f"  EDGE ADD: {src_qid} DEPENDS_ON {tgt_qid}")
            added_edges += 1
        except Exception as e:
            msg = str(e)[:140]
            if any(k in msg.lower() for k in ("already", "exists", "duplicate")):
                print(f"  EDGE SKIP_DUP_GUARD: {src_qid} -> {tgt_qid}")
                skipped_dup += 1
            else:
                print(f"  EDGE FAIL: {src_qid} -> {tgt_qid}: {msg}")
                failed += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  atom created: {created_atoms} / skipped_exists: {skipped_atoms}")
    print(f"  edge added: {added_edges}")
    print(f"  edge skipped_miss_src: {skipped_miss_src}")
    print(f"  edge skipped_miss_tgt: {skipped_miss_tgt}")
    print(f"  edge skipped_dup: {skipped_dup}")
    print(f"  edge failed: {failed}")
    print(f"\nPre-reg KPI (canonical substrate):")
    print(f"  atoms target: +4 (4 new T1)")
    print(f"  edges target: +30 (30 DEPENDS_ON)")
    print(f"  L6-PROOF FINDER avg depth target: 1.30 -> 2.5+ (post-ingest re-run)")
    print(f"  genuine-T1 termination target: 38pct -> 65pct+")


if __name__ == "__main__":
    main()
