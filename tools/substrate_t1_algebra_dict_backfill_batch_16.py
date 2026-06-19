"""T1 batch 16 supplementary: 6 probability-foundation gap-fill atoms (L6-PROOF unblock)."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


SPECS = [
    ("T1/monotonicity", "Monotonicity", ("order_preserving",),
     "Property f(x) <= f(y) when x <= y (non-decreasing); foundation for measure + probability + analysis.",
     ("ordering_property", "measure_theory_foundation", "substrate_self_knowledge"),
     "analysis::ordering_properties", "order_preserving_map", "batch_16"),
    ("T1/chain_rule_probability", "Chain rule (probability)", ("probability_chain_rule",),
     "P(X_1, ..., X_n) = prod_i P(X_i | X_<i). Foundation for joint probability decomposition.",
     ("probability_decomposition", "bayesian_inference_foundation", "substrate_self_knowledge"),
     "probability_theory::decomposition_rules", "joint_via_conditionals", "batch_16"),
    ("T1/total_probability", "Total probability (law of)", ("law_of_total_probability", "LOTP"),
     "P(A) = sum_i P(A | B_i) P(B_i) for partition {B_i}. Foundation for marginalization.",
     ("probability_marginalization", "bayesian_inference_foundation", "substrate_self_knowledge"),
     "probability_theory::core_laws", "marginal_via_partition", "batch_16"),
    ("T1/marginal_distribution", "Marginal distribution", ("P_X_from_P_XY",),
     "P(X) = sum_Y P(X, Y) (or integral for continuous). Distribution of single variable from joint.",
     ("probability_foundation", "marginalization", "substrate_self_knowledge"),
     "probability_theory::distribution_classes", "sum_out_other_variables", "batch_16"),
    ("T1/joint_distribution", "Joint distribution", ("P_X_Y", "multivariate_distribution"),
     "P(X_1, ..., X_n) over multiple random variables. Foundation for multivariate probability + graphical models.",
     ("probability_foundation", "multivariate_modeling", "substrate_self_knowledge"),
     "probability_theory::distribution_classes", "multivariate_probability", "batch_16"),
    ("T1/conditional_independence", "Conditional independence", ("X_indep_Y_given_Z",),
     "X _||_ Y | Z iff P(X, Y | Z) = P(X | Z) P(Y | Z). Foundation for graphical models + d-separation.",
     ("probabilistic_modeling_foundation", "graphical_model_foundation", "substrate_self_knowledge"),
     "probability_theory::dependence_structure", "conditional_factorization", "batch_16"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-ingest: {len(ps.all_atoms())} atoms")
    for (aid, name, aliases, desc, serves, cat, sig, batch) in SPECS:
        qid = f"math::{aid}"
        if ps.has_atom(qid):
            print(f"SKIP: {qid}"); continue
        atom = Atom(id=aid, name=name, corpus=Corpus.MATH, tier=Tier.TIER_1_FOUNDATIONAL,
                    description=desc, kind=AtomKind.PRIMITIVE, aliases=aliases,
                    metadata={"science_algebra_category": cat, "signature_hint": sig, "batch_origin": batch},
                    serves_capability=serves)
        ps.add_atom(atom, source="t1_batch_16_supplementary", note=f"per {batch}")
        print(f"CREATED: {qid}")
    print(f"\npost-ingest: {len(ps.all_atoms())}")


if __name__ == "__main__":
    main()
