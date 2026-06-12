"""Populate signature + complexity fields on the 54 collision atoms per
strategy_request_to_testbed_2026-06-12_signature_complexity_population_for_32_collision_atoms_v586.md

Goal: break cos=1.0 collisions between same-category_int atoms by adding
per-atom-unique signature + complexity fields. AlgebraIndex encoder binds
(key, value) pairs into HRR -> unique fillers diverge the vectors.

Per Strategy direction: signature = structural distinguisher derived from
atom content; complexity = nesting-depth or operator-count scalar.

54 collision atoms grouped by class:
- MWP role atoms (5): differentiate by semantic_role + role_position_index
- math::T1 foundational (33): differentiate by primitive_class + structural_role
- math::T3 algorithm (16): differentiate by algorithm_family + algorithm_step
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("populate_signature_complexity")

DATA_ROOT = Path("data/substrate_index")

# Per-atom schemas. Each entry: (signature, complexity).
# Designed to give every colliding pair at least one distinguishing field.
SCHEMAS: dict[str, tuple[dict, dict]] = {
    # MWP semantic role atoms (5; ALL mutually cos=1.0)
    "concept::MWP/ROLE_ARG0_agent": (
        {"semantic_role": "agent", "role_position_index": 0, "role_class": "core_argument",
         "argument_modifier": "none", "thematic_relation": "doer"},
        {"role_arity": 1, "syntactic_depth": 1, "semantic_specificity": "high"},
    ),
    "concept::MWP/ROLE_ARG1_theme": (
        {"semantic_role": "theme", "role_position_index": 1, "role_class": "core_argument",
         "argument_modifier": "none", "thematic_relation": "patient"},
        {"role_arity": 1, "syntactic_depth": 1, "semantic_specificity": "high"},
    ),
    "concept::MWP/ROLE_ARG2_recipient": (
        {"semantic_role": "recipient", "role_position_index": 2, "role_class": "core_argument",
         "argument_modifier": "none", "thematic_relation": "goal"},
        {"role_arity": 1, "syntactic_depth": 1, "semantic_specificity": "high"},
    ),
    "concept::MWP/ROLE_ARGM_LOC_location": (
        {"semantic_role": "location", "role_position_index": 3, "role_class": "modifier_argument",
         "argument_modifier": "ARGM_LOC", "thematic_relation": "spatial_setting"},
        {"role_arity": 1, "syntactic_depth": 2, "semantic_specificity": "spatial"},
    ),
    "concept::MWP/ROLE_ARGM_TMP_time": (
        {"semantic_role": "time", "role_position_index": 4, "role_class": "modifier_argument",
         "argument_modifier": "ARGM_TMP", "thematic_relation": "temporal_setting"},
        {"role_arity": 1, "syntactic_depth": 2, "semantic_specificity": "temporal"},
    ),

    # math::T1 foundational atoms (33)
    "math::T1/probability_space": (
        {"primitive_class": "measure_theory_probability_space", "structural_role": "axiomatic_space",
         "carries_measure": True, "measure_normalization": "unit_measure", "axiom_family": "kolmogorov"},
        {"axiom_depth": 3, "operator_count": 0, "object_type": "space"},
    ),
    "math::T1/measure_space": (
        {"primitive_class": "measure_theory_general", "structural_role": "axiomatic_space",
         "carries_measure": True, "measure_normalization": "unrestricted", "axiom_family": "caratheodory"},
        {"axiom_depth": 2, "operator_count": 0, "object_type": "space"},
    ),
    "math::T1/matrix": (
        {"primitive_class": "linear_algebra_object", "structural_role": "rectangular_array",
         "is_operator": False, "object_class": "data_container"},
        {"axiom_depth": 1, "operator_count": 0, "object_type": "rank_2_tensor"},
    ),
    "math::T1/matrix_norms": (
        {"primitive_class": "linear_algebra_operator", "structural_role": "scalar_functional",
         "is_operator": True, "object_class": "norm_operator", "operator_codomain": "non_negative_real"},
        {"axiom_depth": 2, "operator_count": 1, "object_type": "functional"},
    ),
    "math::T1/cauchy_sequence": (
        {"primitive_class": "real_analysis_sequence", "structural_role": "limit_property",
         "property_type": "convergence_criterion", "domain": "metric_space"},
        {"axiom_depth": 2, "operator_count": 0, "object_type": "sequence"},
    ),
    "math::T1/continuity": (
        {"primitive_class": "topology_function_property", "structural_role": "limit_preservation",
         "property_type": "function_continuity_epsilon_delta", "domain": "topological_space"},
        {"axiom_depth": 2, "operator_count": 0, "object_type": "function_property"},
    ),
    "math::T1/kullback_leibler_divergence": (
        {"primitive_class": "information_theory_divergence", "structural_role": "asymmetric_divergence",
         "divergence_type": "KL", "is_symmetric": False, "literature": "Kullback_Leibler_1951"},
        {"axiom_depth": 2, "operator_count": 2, "object_type": "divergence_functional"},
    ),
    "math::T1/cross_entropy": (
        {"primitive_class": "information_theory_loss", "structural_role": "expected_codelength",
         "divergence_type": "cross_entropy", "is_symmetric": False, "literature": "Shannon_1948"},
        {"axiom_depth": 2, "operator_count": 2, "object_type": "loss_functional"},
    ),
    "math::T1/renyi_divergence": (
        {"primitive_class": "information_theory_alpha_divergence", "structural_role": "parameterized_divergence",
         "divergence_type": "renyi_alpha", "is_symmetric": False, "literature": "Renyi_1961"},
        {"axiom_depth": 3, "operator_count": 2, "object_type": "parametric_divergence_family"},
    ),
    "math::T1/expectation_variance": (
        {"primitive_class": "probability_first_second_moments", "structural_role": "moment_pair",
         "moment_orders": "1_and_2", "is_symmetric": False, "operator_kind": "linear_then_squared_deviation"},
        {"axiom_depth": 2, "operator_count": 2, "object_type": "moment_functional"},
    ),
    "math::T1/concentration_inequality": (
        {"primitive_class": "probability_tail_bound", "structural_role": "deviation_inequality",
         "inequality_family": "Markov_Chebyshev_Hoeffding", "tail_kind": "upper_bound"},
        {"axiom_depth": 3, "operator_count": 1, "object_type": "inequality_theorem"},
    ),
    "math::T1/characteristic_function": (
        {"primitive_class": "probability_fourier_transform", "structural_role": "moment_generating",
         "transform_kind": "fourier_of_distribution", "domain": "real_random_variable"},
        {"axiom_depth": 3, "operator_count": 1, "object_type": "integral_transform"},
    ),
    "math::T1/rank_nullity_theorem": (
        {"primitive_class": "linear_algebra_dimension_theorem", "structural_role": "rank_nullity_identity",
         "theorem_kind": "dimension_decomposition", "domain": "finite_dim_vector_space"},
        {"axiom_depth": 2, "operator_count": 0, "object_type": "theorem"},
    ),
    "math::T1/null_space": (
        {"primitive_class": "linear_algebra_kernel", "structural_role": "vector_subspace",
         "subspace_kind": "linear_map_kernel", "domain": "vector_space"},
        {"axiom_depth": 2, "operator_count": 0, "object_type": "subspace"},
    ),
    "math::T1/convex_function": (
        {"primitive_class": "convex_analysis_function_property", "structural_role": "epigraph_property",
         "property_type": "convexity", "domain": "real_vector_space"},
        {"axiom_depth": 2, "operator_count": 0, "object_type": "function_property"},
    ),
    "math::T1/newton_method": (
        {"primitive_class": "numerical_optimization_iterative", "structural_role": "second_order_root_finding",
         "method_kind": "newton_raphson_iteration", "convergence_order": 2},
        {"axiom_depth": 2, "operator_count": 3, "object_type": "iterative_algorithm"},
    ),
    "math::T1/metric_space": (
        {"primitive_class": "topology_distance_axiomatic", "structural_role": "metric_axioms",
         "carries_metric": True, "metric_axioms": "nonneg_symmetric_triangle", "axiom_family": "frechet"},
        {"axiom_depth": 2, "operator_count": 0, "object_type": "metric_space"},
    ),
    "math::T1/topological_space": (
        {"primitive_class": "topology_open_sets", "structural_role": "topology_axioms",
         "carries_topology": True, "topology_axioms": "open_set_closure", "axiom_family": "hausdorff_general"},
        {"axiom_depth": 2, "operator_count": 0, "object_type": "topological_space"},
    ),
    "math::T1/lagrange_multiplier": (
        {"primitive_class": "constrained_optimization_equality", "structural_role": "equality_constraint_lagrangian",
         "constraint_kind": "equality_only", "literature": "Lagrange_1797"},
        {"axiom_depth": 3, "operator_count": 2, "object_type": "constrained_optimum_condition"},
    ),
    "math::T1/kkt_conditions": (
        {"primitive_class": "constrained_optimization_inequality", "structural_role": "inequality_constraint_KKT",
         "constraint_kind": "inequality_complementarity", "literature": "Karush_1939_Kuhn_Tucker_1951"},
        {"axiom_depth": 4, "operator_count": 4, "object_type": "constrained_optimum_condition"},
    ),
    "math::T1/category": (
        {"primitive_class": "category_theory_object", "structural_role": "object_morphism_axioms",
         "abstraction_level": "objects_and_morphisms", "axiom_family": "eilenberg_maclane"},
        {"axiom_depth": 1, "operator_count": 0, "object_type": "categorical_structure"},
    ),
    "math::T1/group": (
        {"primitive_class": "abstract_algebra_group", "structural_role": "single_op_with_inverse",
         "axiom_count": 4, "operation_count": 1, "has_inverse": True},
        {"axiom_depth": 2, "operator_count": 1, "object_type": "algebraic_structure"},
    ),
    "math::T1/monoid": (
        {"primitive_class": "abstract_algebra_monoid", "structural_role": "single_op_with_identity",
         "axiom_count": 3, "operation_count": 1, "has_inverse": False},
        {"axiom_depth": 1, "operator_count": 1, "object_type": "algebraic_structure"},
    ),
    "math::T1/ring_field": (
        {"primitive_class": "abstract_algebra_ring", "structural_role": "two_ops_distributive",
         "axiom_count": 7, "operation_count": 2, "has_inverse": True},
        {"axiom_depth": 3, "operator_count": 2, "object_type": "algebraic_structure"},
    ),
    "math::T1/module_ring": (
        {"primitive_class": "abstract_algebra_module_over_ring", "structural_role": "ring_action_on_abelian_group",
         "axiom_count": 4, "operation_count": 2, "has_inverse": False, "external_scalar_ring": True},
        {"axiom_depth": 3, "operator_count": 2, "object_type": "algebraic_structure"},
    ),
    "math::T1/jacobian_matrix": (
        {"primitive_class": "multivariate_calculus_first_derivative", "structural_role": "linear_approximation_matrix",
         "differentiation_order": 1, "is_matrix_valued": True, "literature": "Jacobi_1841"},
        {"axiom_depth": 2, "operator_count": 1, "object_type": "derivative_matrix"},
    ),
    "math::T1/duality_optimization": (
        {"primitive_class": "convex_optimization_dual_problem", "structural_role": "lagrangian_dual_transform",
         "transform_kind": "primal_to_dual", "dual_type": "lagrange_dual"},
        {"axiom_depth": 3, "operator_count": 2, "object_type": "optimization_transform"},
    ),
    "math::T1/pde": (
        {"primitive_class": "differential_equations_partial", "structural_role": "multivariate_diff_equation",
         "equation_kind": "partial_derivative_constraint", "order": "variable"},
        {"axiom_depth": 3, "operator_count": 2, "object_type": "differential_equation"},
    ),
    "math::T1/tracy_widom_distribution": (
        {"primitive_class": "random_matrix_theory_extreme_value", "structural_role": "edge_eigenvalue_law",
         "distribution_kind": "tracy_widom_F1_F2_F4", "literature": "Tracy_Widom_1994"},
        {"axiom_depth": 4, "operator_count": 0, "object_type": "probability_distribution"},
    ),

    # math::T3 algorithm atoms (16)
    "math::T3/euclidean_distance": (
        {"primitive_class": "metric_l2", "structural_role": "l2_metric_function",
         "metric_kind": "euclidean", "domain": "R_n", "is_translation_invariant": True},
        {"axiom_depth": 1, "operator_count": 2, "object_type": "distance_function"},
    ),
    "math::T3/forward_algorithm_atom": (
        {"primitive_class": "hmm_inference", "structural_role": "forward_message_pass",
         "algorithm_family": "HMM", "algorithm_step": "forward", "direction": "left_to_right",
         "literature": "Baum_1972"},
        {"axiom_depth": 2, "operator_count": 3, "object_type": "dp_algorithm"},
    ),
    "math::T3/backward_algorithm_atom": (
        {"primitive_class": "hmm_inference", "structural_role": "backward_message_pass",
         "algorithm_family": "HMM", "algorithm_step": "backward", "direction": "right_to_left",
         "literature": "Baum_1972"},
        {"axiom_depth": 2, "operator_count": 3, "object_type": "dp_algorithm"},
    ),
    "math::T3/hmm_transition": (
        {"primitive_class": "hmm_parameter", "structural_role": "state_transition_probability",
         "algorithm_family": "HMM", "algorithm_step": "transition_matrix", "matrix_dims": "K_by_K"},
        {"axiom_depth": 1, "operator_count": 1, "object_type": "stochastic_matrix"},
    ),
    "math::T3/hmm_emission": (
        {"primitive_class": "hmm_parameter", "structural_role": "observation_emission_probability",
         "algorithm_family": "HMM", "algorithm_step": "emission_matrix", "matrix_dims": "K_by_V"},
        {"axiom_depth": 1, "operator_count": 1, "object_type": "stochastic_matrix"},
    ),
    "math::T3/earley_parser": (
        {"primitive_class": "parsing_chart_topdown", "structural_role": "topdown_chart_parsing",
         "parser_family": "chart", "parser_strategy": "topdown_earley", "grammar_kind": "CFG",
         "literature": "Earley_1970"},
        {"axiom_depth": 3, "operator_count": 3, "object_type": "parsing_algorithm"},
    ),
    "math::T3/cyk_parser": (
        {"primitive_class": "parsing_chart_bottomup", "structural_role": "bottomup_chart_parsing",
         "parser_family": "chart", "parser_strategy": "bottomup_cyk", "grammar_kind": "CNF",
         "literature": "Cocke_Younger_Kasami_1965"},
        {"axiom_depth": 3, "operator_count": 3, "object_type": "parsing_algorithm"},
    ),
    "math::T3/normal_form_NF": (
        {"primitive_class": "grammar_normalization", "structural_role": "CFG_to_CNF_transform",
         "transform_kind": "CNF_chomsky_normal_form", "literature": "Chomsky_1959"},
        {"axiom_depth": 2, "operator_count": 2, "object_type": "grammar_transform"},
    ),
    "math::T3/bpe_tokenization": (
        {"primitive_class": "subword_tokenization_merge", "structural_role": "frequency_merge_tokenizer",
         "tokenizer_family": "BPE", "merge_strategy": "frequency_greedy",
         "literature": "Sennrich_2016"},
        {"axiom_depth": 2, "operator_count": 2, "object_type": "tokenizer"},
    ),
    "math::T3/sentencepiece_tokenizer": (
        {"primitive_class": "subword_tokenization_unigram", "structural_role": "unigram_LM_tokenizer",
         "tokenizer_family": "SentencePiece", "merge_strategy": "unigram_LM_likelihood",
         "literature": "Kudo_2018"},
        {"axiom_depth": 2, "operator_count": 2, "object_type": "tokenizer"},
    ),
    "math::T3/word2vec_embedding": (
        {"primitive_class": "distributional_embedding_local_context", "structural_role": "skipgram_or_cbow",
         "embedding_family": "word2vec", "training_objective": "local_context_prediction",
         "literature": "Mikolov_2013"},
        {"axiom_depth": 2, "operator_count": 2, "object_type": "word_embedding"},
    ),
    "math::T3/glove_embedding": (
        {"primitive_class": "distributional_embedding_global_cooc", "structural_role": "global_cooc_matrix_factorization",
         "embedding_family": "GloVe", "training_objective": "global_cooccurrence_factorization",
         "literature": "Pennington_2014"},
        {"axiom_depth": 2, "operator_count": 2, "object_type": "word_embedding"},
    ),
    "math::T3/digital_filter_design": (
        {"primitive_class": "dsp_filter_synthesis", "structural_role": "frequency_response_to_coefficients",
         "filter_kind": "IIR_or_FIR_design", "synthesis_method": "windowing_or_pole_placement"},
        {"axiom_depth": 2, "operator_count": 3, "object_type": "filter_specification"},
    ),
    "math::T3/finite_state_transducer": (
        {"primitive_class": "fsa_with_output", "structural_role": "input_output_state_machine",
         "machine_family": "transducer", "extends": "finite_state_acceptor",
         "literature": "Mohri_1997"},
        {"axiom_depth": 2, "operator_count": 1, "object_type": "automaton"},
    ),
    "math::T3/wavelet_transform": (
        {"primitive_class": "multiresolution_analysis", "structural_role": "scale_localized_transform",
         "transform_kind": "wavelet_basis_expansion", "literature": "Daubechies_1988"},
        {"axiom_depth": 3, "operator_count": 2, "object_type": "integral_transform"},
    ),
    "math::T3/fast_fourier_transform": (
        {"primitive_class": "spectral_analysis_radix", "structural_role": "radix_recursive_DFT",
         "transform_kind": "DFT_by_butterfly", "complexity_class": "NlogN",
         "literature": "Cooley_Tukey_1965"},
        {"axiom_depth": 2, "operator_count": 3, "object_type": "spectral_transform"},
    ),
    "math::T3/k_means_clustering": (
        {"primitive_class": "centroid_clustering_iterative", "structural_role": "lloyd_iteration",
         "algorithm_family": "k_means", "init_strategy": "kmeans_plus_plus",
         "literature": "MacQueen_1967"},
        {"axiom_depth": 2, "operator_count": 3, "object_type": "clustering_algorithm"},
    ),
    "math::T3/hierarchical_clustering": (
        {"primitive_class": "agglomerative_clustering", "structural_role": "linkage_dendrogram",
         "algorithm_family": "hierarchical", "linkage_strategy": "single_complete_average_ward"},
        {"axiom_depth": 2, "operator_count": 3, "object_type": "clustering_algorithm"},
    ),
    "math::T3/lbfgs_quasi_newton": (
        {"primitive_class": "quasi_newton_optimization", "structural_role": "limited_memory_BFGS",
         "method_family": "quasi_newton", "memory_strategy": "limited_history_inverse_hessian",
         "literature": "Nocedal_1980"},
        {"axiom_depth": 3, "operator_count": 3, "object_type": "optimizer"},
    ),
    "math::T3/tw_edge_z": (
        {"primitive_class": "spectral_observability_substrate", "structural_role": "tracy_widom_edge_z_score",
         "spectral_lever": "edge_eigenvalue_TW_normalized_z", "substrate_observable": True},
        {"axiom_depth": 4, "operator_count": 1, "object_type": "spectral_diagnostic"},
    ),
}


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-populate: %d atoms total", len(pstore.all_atoms()))

    updated = missing = 0
    for qid, (signature, complexity) in SCHEMAS.items():
        if not pstore.has_atom(qid):
            log.warning("MISSING: %s", qid)
            missing += 1
            continue
        a = pstore.get_atom(qid)
        new_signature = dict(a.signature or {})
        new_signature.update(signature)
        new_complexity = dict(a.complexity or {})
        new_complexity.update(complexity)
        new_atom = Atom(
            id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
            description=a.description, kind=a.kind, aliases=a.aliases,
            metadata=a.metadata, algebra=a.algebra,
            signature=new_signature, complexity=new_complexity,
            equivalences=a.equivalences, concept_links=a.concept_links,
            current_best_solution=a.current_best_solution,
            solution_history=a.solution_history,
            serves_capability=a.serves_capability,
        )
        pstore.add_atom(new_atom, source="signature_complexity_population_pp408_rescue2",
                        note=f"+{len(signature)} signature fields +{len(complexity)} complexity fields per strategy_request_v586")
        updated += 1

    log.info("post-populate: updated=%d missing=%d", updated, missing)


if __name__ == "__main__":
    main()
