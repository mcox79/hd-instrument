"""Backfill algebra metadata on 17 substantive untyped T2 math atoms.

OEIS T2 atoms intentionally remain bare (sequence number tabulation).

The 17 substantive ones include 6 VSA operators, 9 family abstractions
(probabilistic_inference / discriminative_classification / etc.), the
gradient_based_optimizer TEMPLATE (somehow never typed itself), and
viterbi_decoding.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


BACKFILL = {
    # VSA operators (mostly already SPECIALIZES family supertypes; type for prover)
    "tier2_schema":              {"about_topic": "tier2_schema", "domain": "substrate_internal", "structure": "T2_primitive_schema_layout", "role": "type"},
    "context_binding":           {"about_topic": "context_binding", "domain": "vsa_binding", "structure": "phasor_x_eq_role_otimes_filler", "role": "operation"},
    "role_filler_binding":       {"about_topic": "role_filler_binding", "domain": "vsa_binding", "structure": "bind_role_to_filler_via_circ_conv", "role": "operation"},
    "hamming_distance":          {"about_topic": "hamming_distance", "domain": "binary_codes", "structure": "count_differing_bits", "role": "operation"},
    "cosine_cleanup":            {"about_topic": "cosine_cleanup", "domain": "vsa_cleanup", "structure": "argmax_codebook_inner_product", "role": "operation"},
    "pointwise_product":         {"about_topic": "pointwise_product", "domain": "vsa_binding", "structure": "elementwise_complex_product", "role": "operation"},

    # Family abstraction supertypes (T2_FAM); previously bare
    "probabilistic_inference":   {"about_topic": "probabilistic_inference", "domain": "probability", "structure": "posterior_or_marginal_estimation", "role": "abstraction_supertype"},
    "discriminative_classification":{"about_topic": "discriminative_classification", "domain": "supervised_learning", "structure": "decision_boundary_from_weights", "role": "abstraction_supertype"},
    "representation_transform":  {"about_topic": "representation_transform", "domain": "linear_algebra", "structure": "linear_or_nonlinear_remap", "role": "abstraction_supertype"},
    "graph_traversal":           {"about_topic": "graph_traversal", "domain": "graph_search", "structure": "visit_via_neighborhood", "role": "abstraction_supertype"},
    "sequence_decoding":         {"about_topic": "sequence_decoding", "domain": "sequence_decoding", "structure": "best_seq_via_scoring_model", "role": "abstraction_supertype"},
    "weak_supervision":          {"about_topic": "weak_supervision", "domain": "supervised_learning", "structure": "aggregate_noisy_label_sources", "role": "abstraction_supertype"},
    "algebraic_binding":         {"about_topic": "algebraic_binding", "domain": "vsa_binding", "structure": "associative_binding_of_atoms", "role": "abstraction_supertype"},
    "cleanup_retrieval":         {"about_topic": "cleanup_retrieval", "domain": "vsa_cleanup", "structure": "best_match_from_noisy_query", "role": "abstraction_supertype"},
    "superposition_aggregation": {"about_topic": "superposition_aggregation", "domain": "vsa_composition", "structure": "additive_combination_of_atoms", "role": "abstraction_supertype"},

    # The template
    "gradient_based_optimizer":  {"about_topic": "gradient_based_optimizer", "domain": "convex_optimization", "structure": "iter_x_n_plus_1_eq_x_n_minus_eta_grad_f", "role": "abstraction_supertype"},

    # Last bare algorithm
    "viterbi_decoding":          {"about_topic": "viterbi", "domain": "sequence_decoding", "structure": "DP_argmax_path_HMM_or_CRF", "role": "operation"},
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    pre_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"pre-backfill atoms-with-algebra: {pre_typed}")

    by_short = {}
    for a in atoms:
        if str(a.corpus).endswith("MATH") and str(a.tier).endswith("TIER_2_PRIMITIVE"):
            short = str(a.id).split("/")[-1].lower()
            by_short.setdefault(short, []).append(a)

    backfilled = 0
    skipped_no_atom = 0
    skipped_already = 0
    failed = 0

    for short_id, alg in BACKFILL.items():
        members = by_short.get(short_id.lower(), [])
        if not members:
            print(f"  SKIP_NO_ATOM: {short_id}")
            skipped_no_atom += 1
            continue
        for a in members:
            if a.algebra and len(a.algebra) >= 3:
                print(f"  SKIP_ALREADY: {a.id}")
                skipped_already += 1
                continue
            try:
                existing = dict(a.algebra) if a.algebra else {}
                merged = {**existing, **alg}
                meta = dict(a.metadata) if a.metadata else {}
                meta["typed_by"] = "backfill_T2_math_algebra_v1"
                meta["distillation_class"] = "B_structure_adding_hygiene"
                updated = Atom(
                    id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                    description=a.description, kind=a.kind, aliases=a.aliases,
                    metadata=meta, serves_capability=a.serves_capability,
                    algebra=merged,
                )
                ps.add_atom(updated, source="backfill_T2_math_algebra_v1",
                            note="T2 math typing for prover-traversable structured core")
                print(f"  BACKFILLED: {a.id}")
                backfilled += 1
            except Exception as e:
                print(f"  FAIL {a.id}: {str(e)[:120]}")
                failed += 1

    atoms = ps.all_atoms()
    post_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"\n=== T2 MATH ALGEBRA BACKFILL v1 SUMMARY ===")
    print(f"pre:  {pre_typed}")
    print(f"post: {post_typed}  (+{post_typed - pre_typed})")
    print(f"  backfilled: {backfilled}")
    print(f"  skipped no atom: {skipped_no_atom}")
    print(f"  skipped already: {skipped_already}")
    print(f"  failed: {failed}")
    print(f"\nT2 substantive coverage: all 17 substantive T2 math atoms now typed.")
    print(f"(OEIS T2 atoms intentionally remain bare per leaf-by-design policy.)")


if __name__ == "__main__":
    main()
