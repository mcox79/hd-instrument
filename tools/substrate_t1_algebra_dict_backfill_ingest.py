"""T1 algebra-dict backfill ingest for Research's 3 INGEST-READY batches (Cycle 51 day-3 close).

Per:
- research_to_testbed_T1_ALGEBRA_DICT_BACKFILL_BATCH_01_linear_algebra_information_theory_*
- research_to_testbed_T1_ALGEBRA_DICT_BACKFILL_BATCH_02_probability_foundations_*
- research_to_testbed_T1_ALGEBRA_DICT_BACKFILL_BATCH_03_info_theory_statistics_*

Ingest the 13 absent atoms (substrate already has 17 of 30 batched names). Each atom:
- math::T1/<canonical_name>
- aliases per YAML
- description summarizing algebra_dict
- metadata: science_algebra_category + signature_hint + algebra_dict-summary
- serves_capability per YAML

DEPENDS_ON edges per "related" field: deferred to batch 4 (Research may want consolidated edge authoring).
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


# 13 absent T1 atoms from research batches 1+2+3
ATOMS_TO_INGEST = [
    # BATCH 01 absent
    {
        "id": "T1/linear_independence",
        "name": "Linear independence",
        "aliases": ("LI", "linearly_independent_vectors"),
        "description": "Vectors v_1..v_n are linearly independent iff sum(c_i v_i) = 0 implies all c_i = 0. Foundation for basis + span + dimension theory.",
        "serves_capability": ("vector_space_foundations", "basis_construction", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "linear_algebra::vector_space_foundations",
                     "signature_hint": "uniqueness_of_trivial_combination",
                     "related": "vector_space basis span dimension",
                     "batch_origin": "T1_dict_backfill_batch_01"},
    },
    {
        "id": "T1/basis",
        "name": "Basis",
        "aliases": ("basis_set", "linearly_independent_spanning_set"),
        "description": "A linearly independent set that spans the vector space; every vector has unique coefficients. Cardinality = dimension.",
        "serves_capability": ("vector_space_foundations", "coordinate_systems", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "linear_algebra::vector_space_foundations",
                     "signature_hint": "linearly_independent_spanning_set",
                     "related": "vector_space linear_independence span dimension",
                     "batch_origin": "T1_dict_backfill_batch_01"},
    },
    {
        "id": "T1/span",
        "name": "Span",
        "aliases": ("linear_span", "linear_hull"),
        "description": "The set of all linear combinations of a vector set; the smallest subspace containing them.",
        "serves_capability": ("vector_space_foundations", "subspace_construction", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "linear_algebra::vector_space_foundations",
                     "signature_hint": "all_linear_combinations",
                     "related": "vector_space basis linear_independence",
                     "batch_origin": "T1_dict_backfill_batch_01"},
    },
    # BATCH 02 absent
    {
        "id": "T1/sigma_algebra",
        "name": "Sigma algebra",
        "aliases": ("Borel_field", "measurable_sets_collection"),
        "description": "Collection of subsets closed under complement + countable union + contains empty set. Foundation for measure theory + probability.",
        "serves_capability": ("measurability_reasoning", "integration_theory", "probability_foundations", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "probability_theory::measure_foundations",
                     "signature_hint": "closed_under_countable_set_operations",
                     "related": "measurable_function probability_space measure_theory",
                     "batch_origin": "T1_dict_backfill_batch_02"},
    },
    {
        "id": "T1/conditional_probability",
        "name": "Conditional probability",
        "aliases": ("P_A_given_B", "conditional"),
        "description": "P(A|B) = P(A intersect B) / P(B). Foundation for Bayesian inference + chain rule + law of total probability.",
        "serves_capability": ("bayesian_inference", "evidence_updating", "causal_reasoning", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "probability_theory::conditioning",
                     "signature_hint": "ratio_of_joint_to_marginal",
                     "related": "bayes_rule independence joint_probability conditional_expectation",
                     "batch_origin": "T1_dict_backfill_batch_02"},
    },
    {
        "id": "T1/independence_probability",
        "name": "Independence (probability)",
        "aliases": ("statistical_independence", "P_A_and_B_eq_P_A_P_B"),
        "description": "Events A,B independent iff P(A intersect B) = P(A)*P(B). Equivalently P(A|B) = P(A).",
        "serves_capability": ("factorization_assumptions", "naive_bayes_foundation", "independent_sampling_inference", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "probability_theory::dependence_structure",
                     "signature_hint": "joint_factors_to_marginals",
                     "related": "conditional_probability conditional_independence mutual_information covariance",
                     "batch_origin": "T1_dict_backfill_batch_02"},
    },
    # BATCH 03 absent
    {
        "id": "T1/jensen_shannon_divergence",
        "name": "Jensen-Shannon divergence",
        "aliases": ("JSD", "symmetric_KL", "smoothed_KL"),
        "description": "Symmetric divergence: JSD(P || Q) = 0.5*KL(P || M) + 0.5*KL(Q || M) where M = 0.5*(P+Q). Bounded, square-root is a metric.",
        "serves_capability": ("symmetric_divergence_measure", "distribution_comparison", "clustering", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "information_theory::divergences",
                     "signature_hint": "symmetrized_kl_via_mixture",
                     "related": "kl_divergence mutual_information cross_entropy",
                     "batch_origin": "T1_dict_backfill_batch_03"},
    },
    {
        "id": "T1/maximum_likelihood",
        "name": "Maximum likelihood estimation",
        "aliases": ("MLE", "maximum_likelihood_estimator"),
        "description": "theta_MLE = argmax_theta L(theta; X) = argmax sum log p(x_i ; theta). Consistent + asymptotically efficient under regularity.",
        "serves_capability": ("point_estimation", "model_fitting", "statistical_inference", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "statistics::estimation",
                     "signature_hint": "argmax_of_likelihood",
                     "related": "likelihood_function fisher_information sufficient_statistic exponential_family",
                     "batch_origin": "T1_dict_backfill_batch_03"},
    },
    {
        "id": "T1/sufficient_statistic",
        "name": "Sufficient statistic",
        "aliases": ("T_X", "data_summary_no_loss"),
        "description": "Statistic T(X) is sufficient for parameter theta iff P(X | T(X) = t, theta) does not depend on theta. Fisher-Neyman factorization theorem.",
        "serves_capability": ("data_reduction", "estimation_foundations", "exponential_family_recognition", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "statistics::data_reduction",
                     "signature_hint": "factorization_theorem",
                     "related": "exponential_family maximum_likelihood fisher_information",
                     "batch_origin": "T1_dict_backfill_batch_03"},
    },
    {
        "id": "T1/exponential_family",
        "name": "Exponential family",
        "aliases": ("expfam", "natural_parameter_family"),
        "description": "Distributions p(x | theta) = h(x) * exp(eta(theta) . T(x) - A(theta)). Includes Gaussian, Poisson, Bernoulli, Gamma, etc.",
        "serves_capability": ("conjugate_priors", "natural_parameterization", "generalized_linear_models", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "statistics::distribution_families",
                     "signature_hint": "log_partition_natural_parameter_sufficient_stat",
                     "related": "sufficient_statistic maximum_likelihood log_partition_function fisher_information",
                     "batch_origin": "T1_dict_backfill_batch_03"},
    },
    {
        "id": "T1/jensen_inequality",
        "name": "Jensen's inequality",
        "aliases": ("convex_inequality", "E_phi_X_geq_phi_E_X_for_convex"),
        "description": "For convex phi: phi(E[X]) <= E[phi(X)]; reverse for concave. Foundation for KL >= 0 + Gibbs inequality + EM algorithm.",
        "serves_capability": ("kl_divergence_proof", "gibbs_inequality_foundation", "EM_algorithm_foundation", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "analysis::convexity_inequalities",
                     "signature_hint": "convex_function_inequality_expectation",
                     "related": "convexity expectation kl_divergence gibbs_inequality",
                     "batch_origin": "T1_dict_backfill_batch_03"},
    },
    {
        "id": "T1/log_partition_function",
        "name": "Log partition function",
        "aliases": ("cumulant_generating_function", "A_theta", "free_energy"),
        "description": "A(theta) = log integral exp(eta . T(x)) h(x) dx in exponential families. Convex; derivatives give cumulants.",
        "serves_capability": ("exponential_family_normalization", "cumulant_generation", "variational_inference_foundation", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "statistics::exponential_family_machinery",
                     "signature_hint": "log_normalizer_of_exponential_family",
                     "related": "exponential_family sufficient_statistic fisher_information",
                     "batch_origin": "T1_dict_backfill_batch_03"},
    },
    {
        "id": "T1/gibbs_inequality",
        "name": "Gibbs inequality",
        "aliases": ("KL_non_negativity", "Gibbs_KL_geq_0"),
        "description": "KL(P || Q) >= 0 with equality iff P = Q (almost everywhere). Follows from Jensen for log. Foundation for cross-entropy minimization = KL minimization.",
        "serves_capability": ("kl_non_negativity_proof", "cross_entropy_minimization_foundation", "substrate_self_knowledge"),
        "metadata": {"science_algebra_category": "information_theory::core_inequalities",
                     "signature_hint": "non_negativity_of_kl",
                     "related": "kl_divergence cross_entropy jensen_inequality",
                     "batch_origin": "T1_dict_backfill_batch_03"},
    },
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-ingest: {len(ps.all_atoms())} atoms\n")

    created = 0
    skipped = 0
    failed = 0
    failures = []

    for spec in ATOMS_TO_INGEST:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"SKIP (already present): {qid}")
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
            ps.add_atom(atom, source="t1_algebra_dict_backfill_research_batches_01_02_03",
                        note=f"per {spec['metadata']['batch_origin']}; T1 math foundation")
            print(f"CREATED: {qid}")
            created += 1
        except Exception as e:
            print(f"FAIL: {qid}: {str(e)[:100]}")
            failed += 1
            failures.append((qid, str(e)[:100]))

    print(f"\n=== SUMMARY ===")
    print(f"post-ingest: {len(ps.all_atoms())} atoms")
    print(f"created: {created}")
    print(f"skipped: {skipped}")
    print(f"failed: {failed}")
    if failures:
        for q, e in failures:
            print(f"  {q}: {e}")


if __name__ == "__main__":
    main()
