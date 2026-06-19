"""Backfill algebra metadata on 23 substantive untyped T3 math atoms.

23 atoms include:
  Algorithm atoms: viterbi_decoding, jonker_volgenant, chu_liu_edmonds,
    prims_mst, map_estimation, cross_entropy_loss
  L6-PROOF chain lemmas/syntheses (mostly authored this session but
    didn't carry algebra metadata):
    dft_linearity_lemma, dft_convolution_to_pointwise_lemma,
    idft_inverse_property_lemma, convolution_theorem_synthesis,
    product_rule_probability_lemma, bayes_rule_synthesis,
    characteristic_function_iid_sum_lemma, characteristic_function_taylor_lemma,
    clt_synthesis, self_adjoint_operator_lemma,
    self_adjoint_real_eigenvalues_lemma, spectral_theorem_synthesis,
    inner_product_positive_semidefinite_lemma,
    quadratic_nonnegative_discriminant_lemma, cauchy_schwarz_synthesis,
    inner_product_bilinearity_lemma, pythagoras_inner_product_synthesis

After this, all substantive T3 math atoms (95 + 23 = 118) carry algebra.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


BACKFILL = {
    # Algorithm atoms
    "viterbi_decoding":          {"about_topic": "viterbi", "domain": "sequence_decoding", "structure": "DP_max_path_in_trellis", "role": "operation"},
    "jonker_volgenant":          {"about_topic": "jonker_volgenant", "domain": "combinatorial_optimization", "structure": "assignment_via_shortest_path", "role": "operation"},
    "chu_liu_edmonds":           {"about_topic": "chu_liu_edmonds", "domain": "graph_optimization", "structure": "max_arborescence_via_contraction", "role": "operation"},
    "prims_mst":                 {"about_topic": "prims_mst", "domain": "graph_optimization", "structure": "grow_tree_via_min_edge", "role": "operation"},
    "map_estimation":            {"about_topic": "map_estimation", "domain": "bayesian_inference", "structure": "argmax_p_theta_given_data", "role": "operation"},
    "cross_entropy_loss":        {"about_topic": "cross_entropy_loss", "domain": "supervised_learning", "structure": "minus_sum_y_log_p_hat", "role": "operation"},

    # L6-PROOF chain lemmas + syntheses (authored this session)
    "dft_linearity_lemma":                       {"about_topic": "dft_linearity", "domain": "signal_processing", "structure": "DFT_alpha_x_plus_beta_y_eq_alpha_DFT_x_plus_beta_DFT_y", "role": "lemma"},
    "dft_convolution_to_pointwise_lemma":        {"about_topic": "dft_convolution_pointwise", "domain": "signal_processing", "structure": "DFT_x_conv_y_eq_DFT_x_pointwise_DFT_y", "role": "lemma"},
    "idft_inverse_property_lemma":               {"about_topic": "idft_inverse", "domain": "signal_processing", "structure": "IDFT_DFT_x_eq_x", "role": "lemma"},
    "convolution_theorem_synthesis":             {"about_topic": "convolution_theorem", "domain": "signal_processing", "structure": "x_conv_y_eq_IDFT_DFT_x_pointwise_DFT_y", "role": "theorem"},
    "product_rule_probability_lemma":            {"about_topic": "product_rule_probability", "domain": "probability", "structure": "P_AB_eq_P_A_given_B_P_B", "role": "lemma"},
    "bayes_rule_synthesis":                      {"about_topic": "bayes_rule", "domain": "probability", "structure": "P_A_given_B_eq_P_B_given_A_P_A_div_P_B", "role": "theorem"},
    "characteristic_function_iid_sum_lemma":     {"about_topic": "char_fn_iid_sum", "domain": "probability", "structure": "phi_S_n_t_eq_phi_X_t_pow_n", "role": "lemma"},
    "characteristic_function_taylor_lemma":      {"about_topic": "char_fn_taylor", "domain": "probability", "structure": "phi_t_eq_1_plus_imu_t_minus_sigma2_t2_div_2_plus_O_t3", "role": "lemma"},
    "clt_synthesis":                             {"about_topic": "clt", "domain": "probability", "structure": "S_n_minus_n_mu_div_sigma_sqrt_n_to_N_0_1", "role": "theorem"},
    "self_adjoint_operator_lemma":               {"about_topic": "self_adjoint", "domain": "functional_analysis", "structure": "Tx_y_eq_x_Ty_for_all", "role": "lemma"},
    "self_adjoint_real_eigenvalues_lemma":       {"about_topic": "self_adjoint_real_eigenvalues", "domain": "functional_analysis", "structure": "T_self_adjoint_implies_eigenvalues_real", "role": "lemma"},
    "spectral_theorem_synthesis":                {"about_topic": "spectral_theorem", "domain": "functional_analysis", "structure": "T_self_adjoint_implies_orthonormal_eigenbasis", "role": "theorem"},
    "inner_product_positive_semidefinite_lemma": {"about_topic": "ip_psd", "domain": "linear_algebra", "structure": "x_x_ge_0", "role": "lemma"},
    "quadratic_nonnegative_discriminant_lemma":  {"about_topic": "quad_nonneg_disc", "domain": "algebra", "structure": "a_ge_0_q_t_ge_0_implies_b2_le_4ac", "role": "lemma"},
    "cauchy_schwarz_synthesis":                  {"about_topic": "cauchy_schwarz", "domain": "linear_algebra", "structure": "x_y_sq_le_x_x_y_y", "role": "theorem"},
    "inner_product_bilinearity_lemma":           {"about_topic": "ip_bilinearity", "domain": "linear_algebra", "structure": "ax_plus_bw_y_eq_a_x_y_plus_b_w_y", "role": "lemma"},
    "pythagoras_inner_product_synthesis":        {"about_topic": "pythagoras_ip", "domain": "linear_algebra", "structure": "x_y_eq_0_implies_norm_x_plus_y_sq_eq_norm_x_sq_plus_norm_y_sq", "role": "theorem"},
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    pre_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"pre-backfill atoms-with-algebra: {pre_typed}")

    by_short = {}
    for a in atoms:
        if str(a.corpus).endswith("MATH") and str(a.tier).endswith("TIER_3_ALGORITHM"):
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
                meta["typed_by"] = "backfill_T3_math_algebra_v1"
                meta["distillation_class"] = "B_structure_adding_hygiene"
                updated = Atom(
                    id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                    description=a.description, kind=a.kind, aliases=a.aliases,
                    metadata=meta, serves_capability=a.serves_capability,
                    algebra=merged,
                )
                ps.add_atom(updated, source="backfill_T3_math_algebra_v1",
                            note="T3 algorithm/lemma/synthesis algebra backfill")
                print(f"  BACKFILLED: {a.id}")
                backfilled += 1
            except Exception as e:
                print(f"  FAIL {a.id}: {str(e)[:120]}")
                failed += 1

    atoms = ps.all_atoms()
    post_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"\n=== T3 MATH ALGEBRA BACKFILL v1 SUMMARY ===")
    print(f"pre:  {pre_typed}")
    print(f"post: {post_typed}  (+{post_typed - pre_typed})")
    print(f"  backfilled: {backfilled}")
    print(f"  skipped no atom: {skipped_no_atom}")
    print(f"  skipped already: {skipped_already}")
    print(f"  failed: {failed}")


if __name__ == "__main__":
    main()
