"""Backfill algebra metadata on remaining ~70 T1 math atoms (v3).

Continues v1 + v2. Covers 4 categorical clusters:
  Optimization: duality_lagrangian / subgradient / line_search / trust_region /
    fixed_point_iteration / linear_programming
  Measure / probability / stochastic processes: measurable_function /
    lebesgue_integral / dominated_convergence / monotone_convergence /
    fubini_tonelli / radon_nikodym / absolute_continuity / almost_everywhere /
    sigma_finite / martingale / brownian_motion / stationary_distribution /
    ergodicity / stopping_time / ito_integral / sde / levy_process /
    poisson_process
  Functional analysis: bounded_linear_operator / compact_operator /
    dual_space / weak_topology / sobolev_space / schwartz_space /
    distribution_generalized_function / reflexive_space / separable_space /
    hahn_banach_theorem
  Graph theory + analysis tools: tree / bipartite_graph / planar_graph /
    laplacian_matrix / spectral_graph_theory / chromatic_number /
    cheeger_inequality / fiedler_vector / generating_function /
    finite_difference / monte_carlo / importance_sampling /
    graph_random_walk / shortest_path / belief_propagation

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


BACKFILL = {
    # Optimization
    "duality_lagrangian":            {"about_topic": "lagrangian_duality", "domain": "optimization", "structure": "L_x_lambda_eq_f_plus_lambda_g", "role": "principle"},
    "subgradient":                   {"about_topic": "subgradient", "domain": "convex_optimization", "structure": "generalized_gradient_convex_nonsmooth", "role": "operation"},
    "line_search":                   {"about_topic": "line_search", "domain": "optimization", "structure": "argmin_t_f_x_plus_t_d", "role": "operation"},
    "trust_region":                  {"about_topic": "trust_region", "domain": "optimization", "structure": "constrained_step_in_ball", "role": "operation"},
    "fixed_point_iteration":         {"about_topic": "fixed_point_iteration", "domain": "numerical_analysis", "structure": "x_n_plus_1_eq_f_x_n_converges_to_fixed_point", "role": "operation"},
    "linear_programming":            {"about_topic": "linear_programming", "domain": "optimization", "structure": "min_cx_st_Ax_le_b", "role": "type"},
    "concave_function":              {"about_topic": "concave_function", "domain": "convex_analysis", "structure": "minus_f_convex", "role": "type"},  # retry from v2

    # Measure theory / probability
    "measurable_function":           {"about_topic": "measurable_function", "domain": "measure_theory", "structure": "preimage_of_borel_is_measurable", "role": "type"},
    "lebesgue_integral":             {"about_topic": "lebesgue_integral", "domain": "measure_theory", "structure": "int_f_dmu_via_simple_functions", "role": "operation"},
    "dominated_convergence_theorem": {"about_topic": "dominated_convergence", "domain": "measure_theory", "structure": "fn_le_g_implies_int_fn_to_int_f", "role": "theorem"},
    "monotone_convergence_theorem":  {"about_topic": "monotone_convergence", "domain": "measure_theory", "structure": "fn_increasing_implies_int_lim_eq_lim_int", "role": "theorem"},
    "fubini_tonelli":                {"about_topic": "fubini_tonelli", "domain": "measure_theory", "structure": "iterated_integrals_equal_product_integral", "role": "theorem"},
    "radon_nikodym":                 {"about_topic": "radon_nikodym", "domain": "measure_theory", "structure": "f_eq_dnu_dmu_density", "role": "theorem"},
    "absolute_continuity_of_measures":{"about_topic": "absolute_continuity", "domain": "measure_theory", "structure": "nu_ll_mu_iff_mu_null_implies_nu_null", "role": "property"},
    "almost_everywhere":             {"about_topic": "almost_everywhere", "domain": "measure_theory", "structure": "holds_except_on_null_set", "role": "modifier"},
    "sigma_finite":                  {"about_topic": "sigma_finite", "domain": "measure_theory", "structure": "X_eq_union_finite_measure_sets", "role": "property"},
    "martingale":                    {"about_topic": "martingale", "domain": "probability", "structure": "E_Xn1_given_Fn_eq_Xn", "role": "type"},
    "brownian_motion":               {"about_topic": "brownian_motion", "domain": "stochastic_processes", "structure": "continuous_gaussian_independent_increments", "role": "type"},
    "stationary_distribution":       {"about_topic": "stationary_distribution", "domain": "probability", "structure": "pi_P_eq_pi_for_markov", "role": "type"},
    "ergodicity":                    {"about_topic": "ergodicity", "domain": "stochastic_processes", "structure": "time_avg_eq_space_avg_invariant_meas", "role": "property"},
    "stopping_time":                 {"about_topic": "stopping_time", "domain": "probability", "structure": "tau_le_n_in_Fn", "role": "type"},
    "ito_integral":                  {"about_topic": "ito_integral", "domain": "stochastic_calculus", "structure": "int_X_dB_via_simple_processes", "role": "operation"},
    "sde":                           {"about_topic": "sde", "domain": "stochastic_calculus", "structure": "dX_eq_mu_dt_plus_sigma_dB", "role": "type"},
    "levy_process":                  {"about_topic": "levy_process", "domain": "stochastic_processes", "structure": "indep_stationary_increments_cadlag", "role": "type"},
    "poisson_process":               {"about_topic": "poisson_process", "domain": "stochastic_processes", "structure": "counting_with_indep_exp_intervals", "role": "type"},

    # Functional analysis
    "bounded_linear_operator":       {"about_topic": "bounded_operator", "domain": "functional_analysis", "structure": "T_in_BL_X_Y_finite_norm", "role": "type"},
    "compact_operator":              {"about_topic": "compact_operator", "domain": "functional_analysis", "structure": "T_bounded_sets_to_relatively_compact", "role": "type"},
    "dual_space":                    {"about_topic": "dual_space", "domain": "functional_analysis", "structure": "X_star_eq_bounded_linear_functionals", "role": "type"},
    "weak_topology":                 {"about_topic": "weak_topology", "domain": "functional_analysis", "structure": "coarsest_topology_continuous_dual", "role": "type"},
    "sobolev_space":                 {"about_topic": "sobolev_space", "domain": "functional_analysis", "structure": "W_kp_functions_with_Lp_weak_derivs", "role": "type"},
    "schwartz_space":                {"about_topic": "schwartz_space", "domain": "functional_analysis", "structure": "rapidly_decreasing_smooth", "role": "type"},
    "distribution_generalized_function":{"about_topic": "generalized_function", "domain": "functional_analysis", "structure": "linear_functional_on_test_functions", "role": "type"},
    "reflexive_space":               {"about_topic": "reflexive_space", "domain": "functional_analysis", "structure": "X_eq_X_double_dual", "role": "property"},
    "separable_space":               {"about_topic": "separable_space", "domain": "topology", "structure": "countable_dense_subset", "role": "property"},
    "hahn_banach_theorem":           {"about_topic": "hahn_banach", "domain": "functional_analysis", "structure": "extend_linear_functional_bounded", "role": "theorem"},

    # Graph theory
    "tree":                          {"about_topic": "tree", "domain": "graph_theory", "structure": "connected_acyclic_graph", "role": "type"},
    "bipartite_graph":               {"about_topic": "bipartite_graph", "domain": "graph_theory", "structure": "V_eq_AcupB_edges_cross", "role": "type"},
    "planar_graph":                  {"about_topic": "planar_graph", "domain": "graph_theory", "structure": "embeddable_in_R2_no_crossings", "role": "type"},
    "laplacian_matrix":              {"about_topic": "laplacian", "domain": "spectral_graph_theory", "structure": "D_minus_A_PSD", "role": "operation"},
    "spectral_graph_theory":         {"about_topic": "spectral_graph_theory", "domain": "graph_theory", "structure": "eigenvalues_of_laplacian_or_adjacency", "role": "type"},
    "chromatic_number":              {"about_topic": "chromatic_number", "domain": "graph_theory", "structure": "min_colors_proper_coloring", "role": "operation"},
    "cheeger_inequality":            {"about_topic": "cheeger", "domain": "spectral_graph_theory", "structure": "lambda_2_le_2_phi_eq_isoperimetric", "role": "inequality"},
    "fiedler_vector":                {"about_topic": "fiedler_vector", "domain": "spectral_graph_theory", "structure": "eigenvector_second_smallest_laplacian", "role": "type"},
    "graph_random_walk":             {"about_topic": "graph_random_walk", "domain": "graph_theory", "structure": "transition_P_via_degree", "role": "operation"},
    "shortest_path":                 {"about_topic": "shortest_path", "domain": "graph_theory", "structure": "min_total_weight_source_to_target", "role": "type"},
    "belief_propagation":            {"about_topic": "belief_propagation", "domain": "graphical_models", "structure": "message_passing_marginals_on_tree", "role": "operation"},

    # Analysis tools
    "generating_function":           {"about_topic": "generating_function", "domain": "combinatorics", "structure": "formal_power_series_encoding_sequence", "role": "type"},
    "finite_difference":             {"about_topic": "finite_difference", "domain": "numerical_analysis", "structure": "f_x_plus_h_minus_f_x_div_h", "role": "operation"},
    "monte_carlo":                   {"about_topic": "monte_carlo", "domain": "stochastic_simulation", "structure": "sample_avg_estimate_integral", "role": "operation"},
    "importance_sampling":           {"about_topic": "importance_sampling", "domain": "stochastic_simulation", "structure": "reweight_via_proposal_density", "role": "operation"},
    "viterbi_algorithm":             {"about_topic": "viterbi", "domain": "sequence_decoding", "structure": "DP_max_path_HMM_or_CRF", "role": "operation"},
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    pre_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"pre-backfill atoms-with-algebra: {pre_typed}")

    by_short = {}
    for a in atoms:
        if str(a.corpus).endswith("MATH") and str(a.tier).endswith("TIER_1_FOUNDATIONAL"):
            short = str(a.id).split("/")[-1].lower()
            by_short[short] = a

    backfilled = 0
    skipped_no_atom = 0
    skipped_already = 0
    failed = 0

    for short_id, alg in BACKFILL.items():
        a = by_short.get(short_id.lower())
        if a is None:
            print(f"  SKIP_NO_ATOM: {short_id}")
            skipped_no_atom += 1
            continue
        if a.algebra and len(a.algebra) >= 3:
            print(f"  SKIP_ALREADY: {short_id}")
            skipped_already += 1
            continue
        try:
            existing = dict(a.algebra) if a.algebra else {}
            merged = {**existing, **alg}
            meta = dict(a.metadata) if a.metadata else {}
            meta["typed_by"] = "backfill_T1_math_algebra_v3"
            meta["distillation_class"] = "B_structure_adding_hygiene"
            updated = Atom(
                id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                description=a.description, kind=a.kind, aliases=a.aliases,
                metadata=meta, serves_capability=a.serves_capability,
                algebra=merged,
            )
            ps.add_atom(updated, source="backfill_T1_math_algebra_v3",
                        note="deepen structured math core v3")
            print(f"  BACKFILLED: {short_id}")
            backfilled += 1
        except Exception as e:
            print(f"  FAIL {short_id}: {str(e)[:120]}")
            failed += 1

    atoms = ps.all_atoms()
    post_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"\n=== T1 MATH ALGEBRA BACKFILL v3 SUMMARY ===")
    print(f"pre:  {pre_typed}")
    print(f"post: {post_typed}  (+{post_typed - pre_typed})")
    print(f"  backfilled: {backfilled}")
    print(f"  skipped (no atom): {skipped_no_atom}")
    print(f"  skipped (already typed): {skipped_already}")
    print(f"  failed: {failed}")


if __name__ == "__main__":
    main()
