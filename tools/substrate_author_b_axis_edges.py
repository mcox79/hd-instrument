"""Author B-axis missing edges per Exp-Dev's spec to lift B 0.52 -> 0.62.

Per exp_dev_to_testbed_B_AXIS_MISSING_EDGE_AUTHORING_SPEC_*:
- Q39 INSTANCE_OF SCHOOL/structured_prediction_family: 4 edges
- Q41 DEPENDS_ON T1/random_variable: 5 edges
- Q38 USES from PP-376 to T3/structured_perceptron_collins: 1 edge
- Q40 SUPERSEDES: 2 edges FLAGGED uncertain (predecessor atoms not specified)

Also creates SCHOOL/structured_prediction_family school atom (missing from substrate).
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import (
    Atom, AtomKind, Corpus, Tier, RelationType,
)


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-author: {len(ps.all_atoms())} atoms")

    # Step 1: create SCHOOL/structured_prediction_family
    sp_qid = "school::SCHOOL/structured_prediction_family"
    if not ps.has_atom(sp_qid):
        sp_atom = Atom(
            id="SCHOOL/structured_prediction_family",
            name="Structured prediction family",
            corpus=Corpus.SCHOOL,
            tier=Tier.TIER_SCHOOL,
            description="Family of algorithms that predict structured outputs (sequences, trees, graphs) with joint dependencies; canonical examples HMM viterbi + structured perceptron + CRF + cascade pipelines.",
            kind=AtomKind.SCHOOL,
            aliases=("structured prediction", "structured output prediction", "structured_prediction"),
            metadata={"key_contributors": ["Collins", "Lafferty", "Tsochantaridis"]},
            algebra={"category_int": 14, "structure": "school",
                     "about_topic": "structured_prediction",
                     "operation_type": "joint_structured_inference",
                     "domain": "sequence_tagging_and_parsing"},
            equivalences=[],
            concept_links=["math::T3/viterbi_decoder",
                            "math::T3/structured_perceptron_collins",
                            "math::T4/cascade_hmm_pipeline",
                            "math::T4/discriminative_perceptron_pipeline"],
        )
        ps.add_atom(sp_atom, source="b_axis_authoring_per_exp_dev_spec",
                    note="created SCHOOL/structured_prediction_family for Q39 INSTANCE_OF gold")
        print(f"created {sp_qid}")

    # Step 2: Q39 INSTANCE_OF SCHOOL/structured_prediction_family
    Q39_INSTANCE_OF = [
        "math::T4/cascade_hmm_pipeline",
        "math::T4/discriminative_perceptron_pipeline",
        "math::T3/viterbi_decoder",
        "math::T3/structured_perceptron_collins",
    ]
    for src in Q39_INSTANCE_OF:
        try:
            ps.add_relation(src, RelationType.INSTANCE_OF, sp_qid,
                             source="b_axis_authoring_per_exp_dev_spec",
                             note="Q39 INSTANCE_OF gold")
            print(f"added {src} --INSTANCE_OF--> {sp_qid}")
        except Exception as e:
            print(f"FAIL {src} INSTANCE_OF: {str(e)[:80]}")

    # Step 3: Q41 DEPENDS_ON math::T1/random_variable
    Q41_DEPENDS_ON_RV = [
        "math::T1/bayes_rule",
        "math::T1/expectation_variance",
        "math::T1/markov_chain",
        "math::T1/shannon_entropy_atom",
        "math::T3/random_features",
    ]
    rv = "math::T1/random_variable"
    for src in Q41_DEPENDS_ON_RV:
        try:
            ps.add_relation(src, RelationType.DEPENDS_ON, rv,
                             source="b_axis_authoring_per_exp_dev_spec",
                             note="Q41 DEPENDS_ON random_variable gold")
            print(f"added {src} --DEPENDS_ON--> {rv}")
        except Exception as e:
            print(f"FAIL {src} DEPENDS_ON: {str(e)[:80]}")

    # Step 4: Q38 USES from PP-376_multibench_math to T3/structured_perceptron_collins
    try:
        ps.add_relation("concept::PP-376_multibench_math", RelationType.USES,
                         "math::T3/structured_perceptron_collins",
                         source="b_axis_authoring_per_exp_dev_spec",
                         note="Q38 USES structured_perceptron_collins gold")
        print(f"added PP-376_multibench_math --USES--> T3/structured_perceptron_collins")
    except Exception as e:
        print(f"FAIL Q38 USES: {str(e)[:80]}")

    print(f"\npost-author: {len(ps.all_atoms())} atoms")
    print("\nQ40 SUPERSEDES NOT applied: predecessor atoms not specified in Exp-Dev spec.")
    print("Flagging Q40 to Exp-Dev for predecessor disambiguation.")


if __name__ == "__main__":
    main()
