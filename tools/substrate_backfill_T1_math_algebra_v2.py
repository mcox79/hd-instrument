"""Backfill algebra metadata on 30+ untyped T1 math atoms (v2).

Continues v1 (c6e9f970). 106 T1 math atoms remain untyped.

This v2 covers 5 categorical clusters:
  Inequalities: cauchy_schwarz / triangle / holders / minkowski / jensen / gibbs
  Information theory: conditional_entropy / chain_rule_entropy / log_partition / sufficient_statistic / exponential_family
  Category theory: homomorphism / isomorphism / functor / natural_transformation / monoidal_category / equivalence_relation
  Matrix decompositions: SVD / eigendecomposition / QR / LU / cholesky / matrix_decomposition / pseudoinverse / condition_number
  Calculus / convexity: chain_rule_calculus / directional_derivative / total_derivative / mean_value_theorem / lipschitz_continuity / completeness / sequence_convergence / concave_function / log_concavity

Adopts standard 4-field algebra: about_topic / domain / structure / role.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


BACKFILL = {
    # Inequalities (named theorems)
    "cauchy_schwarz_inequality": {"about_topic": "cauchy_schwarz", "domain": "linear_algebra", "structure": "inner_prod_sq_le_norm_prod", "role": "inequality"},
    "triangle_inequality":       {"about_topic": "triangle_inequality", "domain": "metric_spaces", "structure": "norm_xy_le_norm_x_plus_norm_y", "role": "inequality"},
    "holders_inequality":        {"about_topic": "holders", "domain": "analysis", "structure": "Lp_Lq_product_bound", "role": "inequality"},
    "minkowski_inequality":      {"about_topic": "minkowski", "domain": "analysis", "structure": "Lp_triangle_inequality", "role": "inequality"},
    "jensen_inequality":         {"about_topic": "jensen", "domain": "convex_analysis", "structure": "convex_f_of_E_le_E_of_convex_f", "role": "inequality"},
    "gibbs_inequality":          {"about_topic": "gibbs", "domain": "information_theory", "structure": "KL_div_nonneg", "role": "inequality"},

    # Information theory
    "conditional_entropy":       {"about_topic": "conditional_entropy", "domain": "information_theory", "structure": "H_Y_given_X", "role": "operation"},
    "chain_rule_entropy":        {"about_topic": "chain_rule_entropy", "domain": "information_theory", "structure": "H_XY_eq_H_X_plus_H_Y_given_X", "role": "identity"},
    "log_partition_function":    {"about_topic": "log_partition", "domain": "exponential_family", "structure": "A_theta_eq_log_int_exp_inner_prod", "role": "operation"},
    "sufficient_statistic":      {"about_topic": "sufficient_statistic", "domain": "statistics", "structure": "T_X_captures_theta_dependence", "role": "type"},
    "exponential_family":        {"about_topic": "exponential_family", "domain": "statistics", "structure": "p_x_theta_eq_h_x_exp_eta_T_minus_A", "role": "type"},

    # Category theory
    "homomorphism":              {"about_topic": "homomorphism", "domain": "abstract_algebra", "structure": "structure_preserving_map", "role": "type"},
    "isomorphism":               {"about_topic": "isomorphism", "domain": "abstract_algebra", "structure": "bijective_homomorphism", "role": "type"},
    "functor":                   {"about_topic": "functor", "domain": "category_theory", "structure": "object_morphism_preserving_functor", "role": "type"},
    "natural_transformation":    {"about_topic": "natural_transformation", "domain": "category_theory", "structure": "morphism_between_functors", "role": "type"},
    "monoidal_category":         {"about_topic": "monoidal_category", "domain": "category_theory", "structure": "category_with_tensor_unit_assoc", "role": "type"},
    "equivalence_relation":      {"about_topic": "equivalence_relation", "domain": "set_theory", "structure": "reflexive_symmetric_transitive", "role": "type"},

    # Matrix decompositions
    "matrix_decomposition":      {"about_topic": "matrix_decomposition", "domain": "linear_algebra", "structure": "factorization_into_structured_factors", "role": "operation"},
    "SVD":                       {"about_topic": "SVD", "domain": "linear_algebra", "structure": "A_eq_U_Sigma_VT", "role": "operation"},
    "eigendecomposition":        {"about_topic": "eigendecomposition", "domain": "linear_algebra", "structure": "A_eq_Q_Lambda_Qinv", "role": "operation"},
    "QR_decomposition":          {"about_topic": "QR", "domain": "linear_algebra", "structure": "A_eq_QR_orth_upper_tri", "role": "operation"},
    "LU_decomposition":          {"about_topic": "LU", "domain": "linear_algebra", "structure": "A_eq_LU_lower_upper_tri", "role": "operation"},
    "cholesky_decomposition":    {"about_topic": "cholesky", "domain": "linear_algebra", "structure": "A_eq_LLT_PSD", "role": "operation"},
    "pseudoinverse":             {"about_topic": "pseudoinverse", "domain": "linear_algebra", "structure": "Moore_Penrose_A_plus", "role": "operation"},
    "condition_number":          {"about_topic": "condition_number", "domain": "numerical_linear_algebra", "structure": "sigma_max_div_sigma_min", "role": "property"},

    # Calculus / convexity
    "chain_rule_calculus":       {"about_topic": "chain_rule_calculus", "domain": "calculus", "structure": "d_f_g_eq_f_prime_g_prime", "role": "identity"},
    "directional_derivative":    {"about_topic": "directional_derivative", "domain": "multivariable_calculus", "structure": "lim_t0_f_x_plus_tv_minus_f_x_div_t", "role": "operation"},
    "total_derivative":          {"about_topic": "total_derivative", "domain": "multivariable_calculus", "structure": "df_eq_sum_partial_dx", "role": "operation"},
    "mean_value_theorem":        {"about_topic": "mean_value_theorem", "domain": "calculus", "structure": "exists_c_f_prime_c_eq_secant", "role": "theorem"},
    "lipschitz_continuity":      {"about_topic": "lipschitz", "domain": "analysis", "structure": "f_x_minus_f_y_le_L_norm_x_y", "role": "property"},
    "completeness":              {"about_topic": "completeness", "domain": "analysis", "structure": "cauchy_sequences_converge", "role": "property"},
    "sequence_convergence":      {"about_topic": "convergence", "domain": "analysis", "structure": "lim_n_xn_eq_L", "role": "operation"},
    "concave_function":          {"about_topic": "concave_function", "domain": "convex_analysis", "structure": "minus_f_convex", "role": "type"},
    "log_concavity":             {"about_topic": "log_concavity", "domain": "convex_analysis", "structure": "log_f_concave", "role": "property"},
    "non_negativity":            {"about_topic": "nonnegativity", "domain": "real_analysis", "structure": "x_ge_0", "role": "property"},
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
            meta["typed_by"] = "backfill_T1_math_algebra_v2"
            meta["distillation_class"] = "B_structure_adding_hygiene"
            updated = Atom(
                id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                description=a.description, kind=a.kind, aliases=a.aliases,
                metadata=meta, serves_capability=a.serves_capability,
                algebra=merged,
            )
            ps.add_atom(updated, source="backfill_T1_math_algebra_v2",
                        note="deepen structured math core v2")
            print(f"  BACKFILLED: {short_id}")
            backfilled += 1
        except Exception as e:
            print(f"  FAIL {short_id}: {str(e)[:120]}")
            failed += 1

    atoms = ps.all_atoms()
    post_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"\n=== T1 MATH ALGEBRA BACKFILL v2 SUMMARY ===")
    print(f"pre:  {pre_typed}")
    print(f"post: {post_typed}  (+{post_typed - pre_typed})")
    print(f"  backfilled: {backfilled}")
    print(f"  skipped (no atom by short_id): {skipped_no_atom}")
    print(f"  skipped (already typed): {skipped_already}")
    print(f"  failed: {failed}")


if __name__ == "__main__":
    main()
