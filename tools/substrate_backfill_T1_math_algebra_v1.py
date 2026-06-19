"""Backfill algebra metadata on 30 untyped T1 math atoms.

Per Skunkworks direction note (2026-06-13 evening): item #5 "deepen the
structured math core (240 -> more)."

Substrate state: 127 of 217 T1 math atoms lack algebra metadata. This
batch types 30 of the most substrate-load-bearing foundational atoms.

Adopts Skunkworks's pattern from signature_type_atom records:
  about_topic / domain / structure / role

This contributes to the structured-core HYGIENE floor (12.4pct measured;
per COMPOUND optimization memo) by reducing unatomized signature
references.

NO LLM. NO bge. Pure algebra-dict backfill via atom upsert.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


# short_id -> algebra dict for backfill. Each gets >=4 fields so CHTV-1 can use them.
BACKFILL_SPECS = {
    # Algebraic structures
    "vector_space": {"about_topic": "vector_space", "domain": "linear_algebra", "structure": "V_over_F",  "role": "type"},
    "complex_field": {"about_topic": "complex_field", "domain": "abstract_algebra", "structure": "C",  "role": "type"},
    "real_field": {"about_topic": "real_field", "domain": "abstract_algebra", "structure": "R",  "role": "type"},
    "group_axioms": {"about_topic": "group", "domain": "abstract_algebra", "structure": "G_with_identity_inverse_assoc",  "role": "axiom_schema"},
    "ring_axioms": {"about_topic": "ring", "domain": "abstract_algebra", "structure": "R_with_add_mult_distrib",  "role": "axiom_schema"},
    "field_axioms": {"about_topic": "field", "domain": "abstract_algebra", "structure": "F_with_mult_inverse_nonzero",  "role": "axiom_schema"},
    "linear_independence": {"about_topic": "linear_independence", "domain": "linear_algebra", "structure": "subset_of_V",  "role": "property"},
    "basis": {"about_topic": "basis", "domain": "linear_algebra", "structure": "linearly_indep_span_V",  "role": "type"},
    "span": {"about_topic": "span", "domain": "linear_algebra", "structure": "subspace_generated_by_subset",  "role": "operation"},
    "unit_modulus": {"about_topic": "unit_modulus", "domain": "complex_analysis", "structure": "S1_unit_circle_in_C",  "role": "type"},

    # Probability / measure foundations
    "probability_distribution": {"about_topic": "probability_distribution", "domain": "probability", "structure": "measure_on_omega_summing_to_1",  "role": "type"},
    "sigma_algebra": {"about_topic": "sigma_algebra", "domain": "measure_theory", "structure": "subset_collection_complement_countable_union_closed",  "role": "type"},
    "conditional_probability": {"about_topic": "conditional_probability", "domain": "probability", "structure": "P_A_given_B_eq_P_AB_div_P_B",  "role": "operation"},
    "independence_probability": {"about_topic": "independence", "domain": "probability", "structure": "P_AB_eq_P_A_P_B",  "role": "property"},
    "maximum_likelihood": {"about_topic": "maximum_likelihood", "domain": "probability", "structure": "argmax_theta_likelihood",  "role": "operation"},

    # Information theory
    "shannon_entropy": {"about_topic": "shannon_entropy", "domain": "information_theory", "structure": "sum_p_log_inv_p",  "role": "operation"},
    "kl_divergence": {"about_topic": "kl_divergence", "domain": "information_theory", "structure": "sum_p_log_p_div_q",  "role": "operation"},
    "jensen_shannon_divergence": {"about_topic": "jensen_shannon_divergence", "domain": "information_theory", "structure": "half_KL_avg_symmetric",  "role": "operation"},

    # Optimization / graphs
    "discrete_optimization": {"about_topic": "discrete_optimization", "domain": "combinatorial_optimization", "structure": "argmin_over_discrete_set",  "role": "operation"},
    "graph_topology": {"about_topic": "graph_topology", "domain": "graph_theory", "structure": "vertices_edges_neighborhood",  "role": "type"},

    # Calculus / analysis
    "limit": {"about_topic": "limit", "domain": "analysis", "structure": "convergence_under_topology",  "role": "operation"},
    "derivative": {"about_topic": "derivative", "domain": "calculus", "structure": "f_prime_via_limit",  "role": "operation"},
    "partial_derivative": {"about_topic": "partial_derivative", "domain": "multivariable_calculus", "structure": "directional_partial",  "role": "operation"},
    "integral": {"about_topic": "integral", "domain": "calculus", "structure": "antiderivative_or_riemann_lebesgue",  "role": "operation"},
    "gradient_operator": {"about_topic": "gradient", "domain": "multivariable_calculus", "structure": "vector_of_partials",  "role": "operation"},

    # Geometric / inner-product extensions
    "orthonormal_basis": {"about_topic": "orthonormal_basis", "domain": "linear_algebra", "structure": "basis_with_orthogonal_unit_vectors",  "role": "type"},
    "projection": {"about_topic": "projection", "domain": "linear_algebra", "structure": "idempotent_linear_operator",  "role": "operation"},
    "eigenvalue": {"about_topic": "eigenvalue", "domain": "linear_algebra", "structure": "Tx_eq_lambda_x",  "role": "type"},
    "eigenvector": {"about_topic": "eigenvector", "domain": "linear_algebra", "structure": "Tx_eq_lambda_x_nonzero",  "role": "type"},
    "norm": {"about_topic": "norm", "domain": "linear_algebra", "structure": "vector_to_nonneg_real",  "role": "operation"},
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    pre_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"pre-backfill atoms-with-algebra: {pre_typed}")

    # Build short_id -> atom map for T1 math atoms
    t1_math_by_short = {}
    for a in atoms:
        if not (str(a.corpus).endswith("MATH") and str(a.tier).endswith("TIER_1_FOUNDATIONAL")):
            continue
        short = str(a.id).split("/")[-1].lower()
        t1_math_by_short[short] = a

    backfilled = 0
    skipped_no_atom = 0
    skipped_already = 0
    failed = 0

    for short_id, alg in BACKFILL_SPECS.items():
        a = t1_math_by_short.get(short_id)
        if a is None:
            print(f"  SKIP_NO_ATOM: {short_id}")
            skipped_no_atom += 1
            continue
        if a.algebra and len(a.algebra) >= 3:
            print(f"  SKIP_ALREADY_TYPED: {short_id}")
            skipped_already += 1
            continue
        try:
            existing = dict(a.algebra) if a.algebra else {}
            merged = {**existing, **alg}
            meta = dict(a.metadata) if a.metadata else {}
            meta["typed_by"] = "backfill_T1_math_algebra_v1"
            meta["distillation_class"] = "B_structure_adding_hygiene"
            updated = Atom(
                id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                description=a.description, kind=a.kind, aliases=a.aliases,
                metadata=meta, serves_capability=a.serves_capability,
                algebra=merged,
            )
            ps.add_atom(updated, source="backfill_T1_math_algebra_v1",
                        note=f"deepen structured math core; T1 foundational atom typed")
            print(f"  BACKFILLED: {short_id}")
            backfilled += 1
        except Exception as e:
            print(f"  FAIL {short_id}: {str(e)[:120]}")
            failed += 1

    atoms = ps.all_atoms()
    post_typed = sum(1 for a in atoms if a.algebra and len(a.algebra) >= 3)
    print(f"\n=== T1 MATH ALGEBRA BACKFILL v1 SUMMARY ===")
    print(f"pre-backfill atoms-with-algebra: {pre_typed}")
    print(f"post-backfill atoms-with-algebra: {post_typed} (+{post_typed - pre_typed})")
    print(f"  backfilled: {backfilled}")
    print(f"  skipped (no atom found by short_id): {skipped_no_atom}")
    print(f"  skipped (already typed): {skipped_already}")
    print(f"  failed: {failed}")
    print(f"\nStructured math core progression: {pre_typed} -> {post_typed}")
    print(f"Per Skunkworks direction note item #5 (deepen structured math core).")


if __name__ == "__main__":
    main()
