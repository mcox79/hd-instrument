"""T1 algebra-dict backfill batches 04 (topology + analysis) + 05 (L6 PROOF inequality/convexity).

12 absent atoms (substrate already has metric_space, topology, continuity, compactness,
banach_space, hilbert_space, limit, convex_function).
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


ATOMS_TO_INGEST = [
    # BATCH 04 absent (topology + analysis)
    {
        "id": "T1/completeness",
        "name": "Completeness",
        "aliases": ("Cauchy_complete", "metric_completeness"),
        "description": "A metric space is complete iff every Cauchy sequence converges. Foundation for Banach + Hilbert spaces + functional analysis.",
        "serves_capability": ("metric_space_foundations", "functional_analysis", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::metric_space_properties",
                     "signature_hint": "cauchy_implies_convergent",
                     "related": "metric_space cauchy_sequence banach_space hilbert_space",
                     "batch_origin": "T1_dict_backfill_batch_04"},
    },
    {
        "id": "T1/sequence_convergence",
        "name": "Sequence convergence",
        "aliases": ("limit_of_sequence", "x_n_to_x"),
        "description": "Sequence x_n in metric space converges to x iff for all eps > 0 there exists N s.t. n >= N implies d(x_n, x) < eps.",
        "serves_capability": ("metric_space_foundations", "limit_theory", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::convergence",
                     "signature_hint": "eps_N_definition_of_limit",
                     "related": "metric_space cauchy_sequence completeness limit",
                     "batch_origin": "T1_dict_backfill_batch_04"},
    },
    {
        "id": "T1/lipschitz_continuity",
        "name": "Lipschitz continuity",
        "aliases": ("L_continuous", "bounded_slope_continuous"),
        "description": "f is L-Lipschitz iff |f(x) - f(y)| <= L * d(x,y) for all x,y. Stronger than uniform continuity; foundation for stable learning + optimization.",
        "serves_capability": ("optimization_theory", "stable_function_approximation", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::continuity_classes",
                     "signature_hint": "bounded_slope",
                     "related": "continuity uniform_continuity gradient_descent_convergence banach_fixed_point",
                     "batch_origin": "T1_dict_backfill_batch_04"},
    },
    # BATCH 05 absent (L6 PROOF inequality + convexity bridges)
    {
        "id": "T1/cauchy_schwarz_inequality",
        "name": "Cauchy-Schwarz inequality",
        "aliases": ("CS_inequality", "inner_product_inequality"),
        "description": "|<x, y>|^2 <= <x, x> * <y, y> in inner product spaces. Foundation for triangle inequality + norm + angle.",
        "serves_capability": ("inner_product_foundations", "vector_norm_construction", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::core_inequalities",
                     "signature_hint": "bound_on_inner_product_magnitude",
                     "related": "inner_product norm triangle_inequality hilbert_space",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
    {
        "id": "T1/log_concavity",
        "name": "Log concavity",
        "aliases": ("logconcave_distribution", "log_f_concave"),
        "description": "Function f is log-concave iff log f is concave. Common in exponential family + Gaussian-like distributions; enables efficient sampling + MAP.",
        "serves_capability": ("density_class_recognition", "efficient_sampling_foundation", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::convexity_classes",
                     "signature_hint": "log_transform_is_concave",
                     "related": "convexity concave_function exponential_family gaussian_distribution",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
    {
        "id": "T1/triangle_inequality",
        "name": "Triangle inequality",
        "aliases": ("subadditivity", "d_xz_leq_d_xy_plus_d_yz"),
        "description": "In metric space: d(x, z) <= d(x, y) + d(y, z). Foundation for metric space axioms + norm subadditivity.",
        "serves_capability": ("metric_space_foundations", "norm_construction", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::core_inequalities",
                     "signature_hint": "subadditive_distance",
                     "related": "metric_space norm cauchy_schwarz_inequality",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
    {
        "id": "T1/holders_inequality",
        "name": "Holder's inequality",
        "aliases": ("Holder_inequality", "Lp_Lq_duality"),
        "description": "|integral f * g| <= ||f||_p * ||g||_q where 1/p + 1/q = 1. Generalizes Cauchy-Schwarz (p=q=2). Foundation for Lp space duality.",
        "serves_capability": ("Lp_space_foundations", "duality_inequalities", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::core_inequalities",
                     "signature_hint": "conjugate_exponent_product_bound",
                     "related": "Lp_norm cauchy_schwarz_inequality minkowski_inequality",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
    {
        "id": "T1/minkowski_inequality",
        "name": "Minkowski inequality",
        "aliases": ("triangle_for_Lp", "subadditivity_Lp_norm"),
        "description": "||f + g||_p <= ||f||_p + ||g||_p for p >= 1. Triangle inequality in Lp spaces.",
        "serves_capability": ("Lp_space_foundations", "norm_subadditivity", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::core_inequalities",
                     "signature_hint": "Lp_norm_subadditivity",
                     "related": "Lp_norm triangle_inequality holders_inequality",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
    {
        "id": "T1/concave_function",
        "name": "Concave function",
        "aliases": ("concavity", "negative_convex"),
        "description": "f is concave iff -f is convex. phi(lambda x + (1-lambda) y) >= lambda phi(x) + (1-lambda) phi(y). Foundation for entropy + log-likelihood-concavity.",
        "serves_capability": ("entropy_foundations", "maximum_likelihood_foundation", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::convexity_classes",
                     "signature_hint": "negation_of_convex",
                     "related": "convex_function convexity jensen_inequality",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
    {
        "id": "T1/non_negativity",
        "name": "Non-negativity (axiom)",
        "aliases": ("non_negative_axiom", "x_geq_0"),
        "description": "Property/axiom: a quantity is >= 0. Foundation for probability axioms (P(A) >= 0) + KL >= 0 (Gibbs) + norms.",
        "serves_capability": ("probability_axiom_foundation", "metric_axiom_foundation", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::ordering_axioms",
                     "signature_hint": "non_negative_quantity",
                     "related": "probability_space metric_space kl_divergence gibbs_inequality",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
    {
        "id": "T1/conditional_entropy",
        "name": "Conditional entropy",
        "aliases": ("H_X_given_Y", "remaining_uncertainty"),
        "description": "H(X | Y) = E_Y[H(X | Y=y)] = H(X,Y) - H(Y). Average remaining uncertainty in X given Y.",
        "serves_capability": ("information_theory_foundations", "conditional_uncertainty_measure", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "information_theory::entropy_decomposition",
                     "signature_hint": "joint_minus_marginal_entropy",
                     "related": "shannon_entropy joint_entropy mutual_information chain_rule_entropy",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
    {
        "id": "T1/chain_rule_entropy",
        "name": "Chain rule (entropy)",
        "aliases": ("entropy_chain_rule", "H_X_Y_decomposition"),
        "description": "H(X, Y) = H(X) + H(Y | X) = H(Y) + H(X | Y). Generalizes to multi-variable: H(X_1, ..., X_n) = sum H(X_i | X_<i).",
        "serves_capability": ("information_theory_foundations", "joint_entropy_decomposition", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "information_theory::entropy_decomposition",
                     "signature_hint": "joint_entropy_decomposes_via_conditionals",
                     "related": "shannon_entropy conditional_entropy mutual_information",
                     "batch_origin": "T1_dict_backfill_batch_05"},
    },
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-ingest: {len(ps.all_atoms())} atoms\n")
    created = 0
    skipped = 0
    failed = 0
    for spec in ATOMS_TO_INGEST:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"SKIP: {qid}")
            skipped += 1
            continue
        try:
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
            ps.add_atom(atom, source="t1_algebra_dict_backfill_research_batches_04_05",
                        note=f"per {spec['metadata']['batch_origin']}; T1 math foundation")
            print(f"CREATED: {qid}")
            created += 1
        except Exception as e:
            print(f"FAIL: {qid}: {str(e)[:100]}")
            failed += 1
    print(f"\n=== SUMMARY ===\npost-ingest: {len(ps.all_atoms())} atoms")
    print(f"created: {created}; skipped: {skipped}; failed: {failed}")


if __name__ == "__main__":
    main()
