"""Fix: backfill atom.algebra on 14 signature type atoms + 7 other T1 math.

Bug found in self-audit: signature_type_atoms_v1/v2/v3 scripts set
metadata.is_type_atom + metadata.science_algebra_category but did NOT
set top-level atom.algebra. So these 14 type atoms show as untyped to
the algebra-counting query (algebra is None).

Skunkworks's operator-type atom ingest correctly set atom.algebra (e.g.
T1/vector has algebra={"about_topic": "vector", "domain": "linear_algebra",
"structure": "V", "role": "type"}). Mirroring that pattern.

Plus 7 substantive T1 atoms from probability/calculus long tail.

After this, substantive T1 math typing coverage is 100% (only OEIS-like
leaves remain bare by design).

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


# 14 signature type atoms + 7 long-tail T1 math
BACKFILL = {
    # Signature type atoms (mathematical foundations) -- my v1/v2/v3
    "vector_space_over_field":   {"about_topic": "vector_space_over_field", "domain": "linear_algebra", "structure": "V_over_F_with_8_axioms", "role": "type"},
    "inner_product_space":       {"about_topic": "inner_product_space", "domain": "linear_algebra", "structure": "V_with_positive_def_hermitian_form", "role": "type"},
    "measurable_space":          {"about_topic": "measurable_space", "domain": "measure_theory", "structure": "set_X_with_sigma_algebra", "role": "type"},
    "linear_operator":           {"about_topic": "linear_operator", "domain": "linear_algebra", "structure": "T_V_to_W_T_ax_plus_by_eq_aTx_plus_bTy", "role": "type"},
    "bilinear_form":             {"about_topic": "bilinear_form", "domain": "linear_algebra", "structure": "B_V_x_V_to_F_linear_each_arg", "role": "type"},
    "continuous_map":            {"about_topic": "continuous_map", "domain": "topology", "structure": "preimage_open_is_open", "role": "type"},
    "self_adjoint_operator_type":{"about_topic": "self_adjoint", "domain": "functional_analysis", "structure": "Tx_y_eq_x_Ty", "role": "type"},
    "random_variable_type":      {"about_topic": "random_variable", "domain": "probability", "structure": "measurable_function_Omega_to_R", "role": "type"},
    "measure_preserving_map":    {"about_topic": "measure_preserving", "domain": "ergodic_theory", "structure": "mu_T_inv_A_eq_mu_A", "role": "type"},
    "group_action_type":         {"about_topic": "group_action", "domain": "abstract_algebra", "structure": "G_x_X_to_X_axioms", "role": "type"},
    "normed_vector_space":       {"about_topic": "normed_space", "domain": "linear_algebra", "structure": "V_with_norm_positive_homog_triangle", "role": "type"},
    "sigma_algebra_type":        {"about_topic": "sigma_algebra", "domain": "measure_theory", "structure": "subsets_complement_countable_union_closed", "role": "type"},
    "smooth_manifold_type":      {"about_topic": "smooth_manifold", "domain": "differential_geometry", "structure": "locally_Rn_smooth_transitions", "role": "type"},
    "lie_group_type":            {"about_topic": "lie_group", "domain": "differential_geometry", "structure": "smooth_manifold_with_group_smooth_ops", "role": "type"},
    "dynamical_system_type":     {"about_topic": "dynamical_system", "domain": "dynamical_systems", "structure": "X_T_phi_evolution_axioms", "role": "type"},

    # Long-tail T1 math
    "monotonicity":              {"about_topic": "monotonicity", "domain": "real_analysis", "structure": "x_le_y_implies_f_x_le_f_y_or_ge", "role": "property"},
    "chain_rule_probability":    {"about_topic": "chain_rule_probability", "domain": "probability", "structure": "P_X1_to_n_eq_prod_P_Xi_given_X1_to_iminus1", "role": "identity"},
    "total_probability":         {"about_topic": "total_probability", "domain": "probability", "structure": "P_A_eq_sum_P_A_given_Bi_P_Bi", "role": "identity"},
    "marginal_distribution":     {"about_topic": "marginal_distribution", "domain": "probability", "structure": "p_x_eq_sum_y_p_x_y", "role": "operation"},
    "joint_distribution":        {"about_topic": "joint_distribution", "domain": "probability", "structure": "p_x_y_over_two_or_more_RVs", "role": "type"},
    "conditional_independence":  {"about_topic": "conditional_independence", "domain": "probability", "structure": "X_perp_Y_given_Z_iff_p_X_Y_given_Z_factors", "role": "property"},
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
            meta["typed_by"] = "backfill_T1_math_algebra_v4_fix_type_atoms"
            meta["distillation_class"] = "B_structure_adding_hygiene"
            updated = Atom(
                id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                description=a.description, kind=a.kind, aliases=a.aliases,
                metadata=meta, serves_capability=a.serves_capability,
                algebra=merged,
            )
            ps.add_atom(updated, source="backfill_T1_math_algebra_v4_fix",
                        note="set top-level atom.algebra (bug: v1/v2/v3 only set metadata)")
            print(f"  BACKFILLED: {a.id}")
            backfilled += 1
        except Exception as e:
            print(f"  FAIL {a.id}: {str(e)[:120]}")
            failed += 1

    atoms = ps.all_atoms()
    post_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"\n=== T1 MATH ALGEBRA BACKFILL v4 SUMMARY ===")
    print(f"pre:  {pre_typed}")
    print(f"post: {post_typed}  (+{post_typed - pre_typed})")
    print(f"  backfilled: {backfilled}")
    print(f"  skipped no atom: {skipped_no_atom}")
    print(f"  skipped already: {skipped_already}")
    print(f"  failed: {failed}")


if __name__ == "__main__":
    main()
