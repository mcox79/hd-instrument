"""Backfill serves_capability on typed math atoms with empty cap.

Audit found 203 of 411 typed math operators have empty serves_capability.
This batch authors capability tags for the most substrate-load-bearing
foundational + family atoms.

Capability tag conventions per existing substrate atoms:
  cap_<operator>_<aspect>   e.g. cap_inner_product, cap_kl_divergence
  cap_<family>              e.g. cap_optimization, cap_search

Distillation class: B structure-adding (no removal; serves_capability
enables better cap_map routing for substrate's capability search).

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


# (short_id, cap_tuple). Selected ~60 highest-load-bearing atoms.
CAP_SPECS = {
    # T1 foundational structures
    "vector_space": ("cap_vector_space", "cap_linear_algebra_foundation"),
    "inner_product": ("cap_inner_product", "cap_geometry_in_vector_space"),
    "cosine_similarity": ("cap_cosine_similarity", "cap_normalized_similarity"),
    "real_field": ("cap_real_field", "cap_scalar_arithmetic"),
    "unit_modulus": ("cap_unit_modulus", "cap_phasor_geometry"),
    "probability_distribution": ("cap_probability_distribution", "cap_uncertainty_quantification"),
    "shannon_entropy": ("cap_entropy", "cap_information_quantity"),
    "kl_divergence": ("cap_kl_divergence", "cap_distribution_divergence"),
    "group_axioms": ("cap_group_axioms", "cap_algebraic_structure_group"),
    "ring_axioms": ("cap_ring_axioms", "cap_algebraic_structure_ring"),
    "field_axioms": ("cap_field_axioms", "cap_algebraic_structure_field"),
    "discrete_optimization": ("cap_discrete_optimization", "cap_combinatorial_search"),
    "graph_topology": ("cap_graph_topology", "cap_graph_structure"),
    "limit": ("cap_limit", "cap_convergence_foundation"),
    "derivative": ("cap_derivative", "cap_differentiation"),
    "integral": ("cap_integral", "cap_integration"),

    # T2 VSA operators
    "context_binding": ("cap_context_binding", "cap_vsa_role_filler"),
    "role_filler_binding": ("cap_role_filler_binding", "cap_vsa_binding"),
    "hamming_distance": ("cap_hamming_distance", "cap_bit_sequence_distance"),

    # T3 HMM family
    "forward_algorithm": ("cap_forward_algorithm", "cap_hmm_marginal_inference"),
    "backward_algorithm": ("cap_backward_algorithm", "cap_hmm_smoothing"),

    # T3 combinatorial optimization
    "hungarian_assignment": ("cap_hungarian_assignment", "cap_bipartite_matching"),
    "jonker_volgenant": ("cap_jonker_volgenant", "cap_assignment_via_shortest_path"),
    "chu_liu_edmonds": ("cap_chu_liu_edmonds", "cap_max_arborescence"),
    "prims_mst": ("cap_prims_mst", "cap_minimum_spanning_tree"),

    # T3 graph search
    "dijkstra": ("cap_dijkstra", "cap_shortest_path_nonneg"),
    "astar": ("cap_astar", "cap_heuristic_shortest_path"),
    "beam_search": ("cap_beam_search", "cap_approximate_top_k_search"),

    # T3 DP / value
    "dynamic_programming": ("cap_dynamic_programming", "cap_optimal_substructure"),

    # T3 dim reduction / spectral
    "pca_whitening": ("cap_pca_whitening", "cap_decorrelation"),
    "zca_whitening": ("cap_zca_whitening", "cap_whitening_orientation_preserving"),
    "principal_component_analysis": ("cap_pca", "cap_dimensionality_reduction"),

    # T3 Bayesian
    "bayesian_inference": ("cap_bayesian_inference", "cap_posterior_computation"),
    "map_estimation": ("cap_map_estimation", "cap_argmax_posterior"),

    # T3 numerical
    "runge_kutta": ("cap_runge_kutta", "cap_ode_integration"),
    "lbfgs_quasi_newton": ("cap_lbfgs", "cap_quasi_newton_optimization"),
    "monte_carlo": ("cap_monte_carlo", "cap_stochastic_simulation"),
    "importance_sampling": ("cap_importance_sampling", "cap_reweighted_sampling"),

    # T3 supervised learning
    "cross_entropy_loss": ("cap_cross_entropy_loss", "cap_classification_objective"),

    # T3 hashing
    "locality_sensitive_hashing": ("cap_lsh", "cap_approximate_nearest_neighbor"),
    "random_projection": ("cap_random_projection", "cap_dim_reduction_random"),
    "feature_hashing": ("cap_feature_hashing", "cap_hash_trick"),

    # T3 tokenization
    "bpe_tokenization": ("cap_bpe", "cap_subword_tokenization"),
    "sentencepiece_tokenizer": ("cap_sentencepiece", "cap_subword_tokenization"),

    # T3 neural-net components
    "positional_encoding": ("cap_positional_encoding", "cap_sequence_position_signal"),
    "dropout_regularization": ("cap_dropout", "cap_regularization"),
    "k_means_clustering": ("cap_k_means", "cap_clustering"),
    "hierarchical_clustering": ("cap_hierarchical_clustering", "cap_dendrogram_clustering"),

    # T3 transforms
    "wavelet_transform": ("cap_wavelet_transform", "cap_multiscale_decomposition"),

    # T3 parsing / language
    "earley_parser": ("cap_earley_parser", "cap_cfg_parsing"),
    "finite_state_transducer": ("cap_fst", "cap_sequence_transduction"),

    # T1 information theory
    "jensen_shannon_divergence": ("cap_js_divergence", "cap_symmetric_distribution_distance"),
    "conditional_entropy": ("cap_conditional_entropy", "cap_residual_uncertainty"),
    "mutual_information": ("cap_mutual_information", "cap_dependency_quantification"),

    # T1 measure / probability
    "expectation": ("cap_expectation", "cap_mean_value"),
    "variance": ("cap_variance", "cap_spread_quantification"),
    "conditional_probability": ("cap_conditional_probability", "cap_belief_update"),
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    pre_with_cap = sum(1 for a in atoms if a.serves_capability and len(a.serves_capability) > 0)
    print(f"pre-backfill atoms-with-cap: {pre_with_cap}\n")

    by_short = {}
    for a in atoms:
        if str(a.corpus.name) == "MATH":
            short = str(a.id).split("/")[-1].lower()
            by_short.setdefault(short, []).append(a)

    backfilled = 0
    skipped_no_atom = 0
    skipped_has_cap = 0
    failed = 0

    for short_id, caps in CAP_SPECS.items():
        members = by_short.get(short_id.lower(), [])
        if not members:
            skipped_no_atom += 1
            continue
        for a in members:
            if a.serves_capability and len(a.serves_capability) > 0:
                skipped_has_cap += 1
                continue
            try:
                meta = dict(a.metadata) if a.metadata else {}
                meta["cap_backfilled_by"] = "backfill_serves_capability_v1"
                updated = Atom(
                    id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                    description=a.description, kind=a.kind, aliases=a.aliases,
                    metadata=meta, serves_capability=tuple(caps),
                    algebra=a.algebra,
                )
                ps.add_atom(updated, source="backfill_serves_capability_v1",
                            note="capability tag backfill for cap_map routing")
                backfilled += 1
            except Exception as e:
                print(f"  FAIL {a.id}: {str(e)[:100]}")
                failed += 1

    atoms = ps.all_atoms()
    post_with_cap = sum(1 for a in atoms if a.serves_capability and len(a.serves_capability) > 0)
    print(f"\n=== SERVES_CAPABILITY BACKFILL v1 SUMMARY ===")
    print(f"pre:  {pre_with_cap}")
    print(f"post: {post_with_cap}  (+{post_with_cap - pre_with_cap})")
    print(f"  backfilled: {backfilled}")
    print(f"  skipped no atom by short: {skipped_no_atom}")
    print(f"  skipped already has cap: {skipped_has_cap}")
    print(f"  failed: {failed}")


if __name__ == "__main__":
    main()
